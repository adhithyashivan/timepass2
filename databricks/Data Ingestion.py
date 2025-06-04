# Databricks notebook source
# MAGIC %pip install openai

# COMMAND ----------

import openai

openai.api_type = "azure"
openai.api_base = "https://hackathongraphragopenai.openai.azure.com/"
#openai.api_version = "2023-12-01-preview"
openai.REMOVED_SECRET

# COMMAND ----------

from pyspark.sql.functions import pandas_udf
import pandas as pd

@pandas_udf("string")
def generate_doc_content(doc_topic: pd.Series, jira_summary: pd.Series, cr_title: pd.Series) -> pd.Series:
    summaries = []
    for topic, jira, cr in zip(doc_topic, jira_summary, cr_title):
        prompt = f"""
        Write a concise summary (2-3 paragraphs) for a Confluence document titled {topic}.
        Focus mainly on the Confluence document topic.
        """
        try:
            response = client.chat.completions.create(
            model="gpt-4-completion",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
            )
            
            summaries.append(response['choices'][0]['message']['content'].strip())
        except Exception as e:
            summaries.append(f"AI error: {e}")
    return pd.Series(summaries)

# COMMAND ----------

import openai

client = openai.AzureOpenAI(
    REMOVED_SECRET,
    api_version="2023-12-01-preview",
    azure_endpoint="https://hackathongraphragopenai.openai.azure.com/"
)

prompt = """
Write a concise summary ( 3 paragraphs) for a Confluence document titled 'Login Bug Notes'.
Focus mainly on the Confluence document topic"""

response = client.chat.completions.create(
    model="gpt-4-completion",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=1000
)

print(response.choices[0].message.content.strip())

# COMMAND ----------

spark.conf.set(
    "fs.azure.sas.rawdata.barclayshackathontest.blob.core.windows.net",
    "sp=racwdl&st=2025-05-31T01:24:56Z&se=2025-06-06T09:24:56Z&spr=https&sv=2024-11-04&sr=c&sig=g3Zsdf01Tr4a5jA7WJXsLtsZUieV6PZQFdC3J28Msxo%3D"
)

# COMMAND ----------

#SAS_URL="https://barclayshackathontest.blob.core.windows.net/rawdata?sp=racw&st=2025-05-29T02:01:28Z&se=2025-06-06T10:01:28Z&sv=2024-11-04&sr=c&sig=jql4VXUIYQaGgZ6mdsUmN1M9CnyghWK9ff9G0sx3K6U%3D"
#SAS_TOKEN="sp=racw&st=2025-05-29T02:01:28Z&se=2025-06-06T10:01:28Z&sv=2024-11-04&sr=c&sig=jql4VXUIYQaGgZ6mdsUmN1M9CnyghWK9ff9G0sx3K6U%3D"


# COMMAND ----------

# Load CSVs from Blob Storage
jira_df = spark.read.option("header", True).csv("wasbs://rawdata@barclayshackathontest.blob.core.windows.net/JIRA_Issues.csv")
cr_df = spark.read.option("header", True).csv("wasbs://rawdata@barclayshackathontest.blob.core.windows.net/Change_Requests.csv")
conf_df = spark.read.option("header", True).csv("wasbs://rawdata@barclayshackathontest.blob.core.windows.net/Confluence_Docs.csv")

# Preview data
jira_df.show()
cr_df.show()
conf_df.show()

# COMMAND ----------

from pyspark.sql.functions import col, when, concat, lit

# Join CR and JIRA on cr_id
cr_jira_df = cr_df.join(jira_df, on="cr_id", how="left").select("cr_id", "jira_id", "jira_summary", "cr_title")

cr_jira_df.show()


# COMMAND ----------

# Join Confluence with CR-JIRA mapping
conf_joined = conf_df.join(cr_jira_df, on="cr_id", how="left").drop("cr_id")
conf_joined.show()

# COMMAND ----------

conf_joined.count()

# COMMAND ----------

conf_pandas = conf_joined.select("confluence_doc_id", "doc_topic", "jira_summary", "cr_title").toPandas()

import openai

client = openai.AzureOpenAI(
    REMOVED_SECRET,
    api_version="2023-12-01-preview",
    azure_endpoint="https://hackathongraphragopenai.openai.azure.com/"
)

def generate_summary(row):
    prompt = f"""
    Write a concise summary (2-3 paragraphs) for a Confluence document titled {row['doc_topic']}.
    Focus mainly on the Confluence document topic.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4-completion",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI error: {e}"

# Apply AI function to each row
conf_pandas["doc_content"] = conf_pandas.apply(generate_summary, axis=1)

conf_final_ai = spark.createDataFrame(conf_pandas)
conf_final_ai.show(truncate=False)

# COMMAND ----------

print(conf_final_ai.count())

display(conf_final_ai) #Download the CSV file from here

# COMMAND ----------

# MAGIC %md
# MAGIC