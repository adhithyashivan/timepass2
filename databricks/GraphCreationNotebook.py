# Databricks notebook source
# MAGIC %pip install gremlinpython

# COMMAND ----------

from pyspark.sql import SparkSession
import pandas as pd
from gremlin_python.driver import client, serializer

# Cosmos DB Config
cosmos_endpoint = "wss://hackathon-cosmosdb.gremlin.cosmos.azure.com:443/"
cosmos_key = "REMOVED_SECRET"
database = "graphrag"
container = "hackathongraph"

gremlin_client = client.Client(
    f"{cosmos_endpoint}",
    "g",
    username=f"/dbs/{database}/colls/{container}",
    password=cosmos_key,
    message_serializer=serializer.GraphSONSerializersV2d0()
)

print("Connected to Cosmos DB Graph!")

# COMMAND ----------

spark.conf.set(
    "fs.azure.sas.rawdata.barclayshackathontest.blob.core.windows.net",
    "sp=racwdl&st=2025-05-31T17:31:00Z&se=2025-06-07T01:31:00Z&spr=https&sv=2024-11-04&sr=c&sig=JKsY%2BTJgtgeCctNHwkqFgc0USNz8fV8YWa%2F3Y1FFCSk%3D"
)

# COMMAND ----------

jira_df = spark.read.option("header", True).csv(
    "wasbs://rawdata@barclayshackathontest.blob.core.windows.net/JIRA_Issues.csv")
confluence_df = spark.read.option("header", True) \
    .option("delimiter", ",") \
    .option("quote", '"') \
    .option("escape", '"') \
    .option("multiLine", True) \
    .csv("wasbs://rawdata@barclayshackathontest.blob.core.windows.net/Confluence_Enriched.csv")
cr_df = spark.read.option("header", True).csv(
    "wasbs://rawdata@barclayshackathontest.blob.core.windows.net/Change_Requests.csv")

# COMMAND ----------

confluence_df.show()

# COMMAND ----------

jira_pd = jira_df.toPandas()
conf_pd = confluence_df.toPandas()
cr_pd = cr_df.toPandas()

# COMMAND ----------

confluence_df_original = spark.read.option("header", True) \
    .option("delimiter", ",") \
    .option("quote", '"') \
    .option("escape", '"') \
    .option("multiLine", True) \
    .csv("wasbs://rawdata@barclayshackathontest.blob.core.windows.net/Confluence_Docs.csv")


# COMMAND ----------

confluence_df_original.show()

# COMMAND ----------

confluence_pd_original = confluence_df_original.toPandas()

# COMMAND ----------

# Merge original cr_id into enriched Confluence DataFrame
conf_pd = conf_pd.merge(
    confluence_pd_original[['confluence_doc_id', 'cr_id']],
    on='confluence_doc_id',
    how='left'
)

# COMMAND ----------

# Join Confluence with Jira on 'cr_id' to get 'jira_id'
conf_pd = conf_pd.merge(jira_pd[['jira_id', 'cr_id']], on='cr_id', how='left')

# Check result
conf_pd.head()

# COMMAND ----------

# Drop all vertices and edges in the graph
gremlin_client.submit("g.V().drop()").all().result()
gremlin_client.submit("g.E().drop()").all().result()

# COMMAND ----------


# Insert Jira vertices
for _, row in jira_pd.iterrows():
    jira_id = str(row['jira_id'])
    jira_summary = str(row['jira_summary']).replace(
        "'", "\\'").replace("\n", " ")
    cr_id = str(row['cr_id']) if pd.notna(row['cr_id']) else ""

    gremlin_client.submit(f"""
        g.addV('Jira')
        .property('id', '{jira_id}')
        .property('vertexType', 'Jira')
        .property('jira_summary', '{jira_summary}')
        .property('cr_id', '{cr_id}')
    """).all().result()

# Insert Confluence vertices
for _, row in conf_pd.iterrows():
    conf_id = str(row['confluence_doc_id'])
    doc_topic = str(row['doc_topic']).replace("'", "\\'").replace("\n", " ")
    doc_content = str(row['doc_content']).replace(
        "'", "\\'").replace("\n", " ")
    jira_id = str(row['jira_id']) if pd.notna(row['jira_id']) else ""
    cr_id = str(row['cr_id']) if pd.notna(row['cr_id']) else ""

    gremlin_client.submit(f"""
        g.addV('Confluence')
        .property('id', '{conf_id}')
        .property('vertexType', 'Confluence')
        .property('doc_topic', '{doc_topic}')
        .property('doc_content', '{doc_content}')
        .property('jira_id', '{jira_id}')
        .property('cr_id', '{cr_id}')
    """).all().result()

# Insert CR vertices
for _, row in cr_pd.iterrows():
    cr_id = str(row['cr_id'])
    cr_title = str(row['cr_title']).replace("'", "\\'").replace("\n", " ")
    cr_status = str(row['cr_status'])
    created_at = str(row['created_at'])
    updated_by_user = str(row['updated_by_user'])
    team_name = str(row['team_name'])

    gremlin_client.submit(f"""
        g.addV('CR')
        .property('id', '{cr_id}')
        .property('vertexType', 'CR')
        .property('cr_title', '{cr_title}')
        .property('cr_status', '{cr_status}')
        .property('created_at', '{created_at}')
        .property('updated_by_user', '{updated_by_user}')
        .property('team_name', '{team_name}')
    """).all().result()

# COMMAND ----------

for _, row in conf_pd.iterrows():
    conf_id = row['confluence_doc_id']
    jira_id = row['jira_id']
    gremlin_client.submit(f"""
        g.V().has('id', '{conf_id}')
        .coalesce(
            outE('REFERS_TO').where(inV().has('id', '{jira_id}')),
            addE('REFERS_TO').to(g.V().has('id', '{jira_id}'))
        )
    """).all().result()

for _, row in jira_pd.iterrows():
    jira_id = row['jira_id']
    cr_id = row['cr_id']
    gremlin_client.submit(f"""
        g.V().has('id', '{jira_id}')
        .coalesce(
            outE('MENTIONS').where(inV().has('id', '{cr_id}')),
            addE('MENTIONS').to(g.V().has('id', '{cr_id}'))
        )
    """).all().result()

# COMMAND ----------

# # Insert a Jira vertex
# gremlin_client.submit("""
#     g.addV('Jira')
#     .property('id', 'JIRA-001')
#     .property('vertexType', 'Jira')
#     .property('jira_summary', 'Fix login bug')
# """).all().result()

# # Insert a Confluence vertex
# gremlin_client.submit("""
#     g.addV('Confluence')
#     .property('id', 'CONF-001')
#     .property('vertexType', 'Confluence')
#     .property('doc_topic', 'Login Bug Notes')
#     .property('doc_content', 'This document discusses login bug fixes.')
# """).all().result()

# # Insert a CR vertex
# gremlin_client.submit("""
#     g.addV('CR')
#     .property('id', 'CR-001')
#     .property('vertexType', 'CR')
#     .property('cr_title', 'Security Patch CR')
# """).all().result()


# COMMAND ----------

# # Confluence refers to Jira
# gremlin_client.submit("""
#     g.V().has('id', 'CONF-001').addE('REFERS_TO').to(g.V().has('id', 'JIRA-001'))
# """).all().result()

# # Jira mentions CR
# gremlin_client.submit("""
#     g.V().has('id', 'JIRA-001').addE('MENTIONS').to(g.V().has('id', 'CR-001'))
# """).all().result()

# COMMAND ----------

result = gremlin_client.submit("g.V().valueMap()").all().result()
for r in result:
    print(r)

# COMMAND ----------

jira_pd.head()

# COMMAND ----------

conf_pd.head()

# COMMAND ----------

print("Vertices:")
for v in gremlin_client.submit("g.V().valueMap(true)").all().result():
    print(v)

print("\nEdges:")
for e in gremlin_client.submit("g.E().valueMap(true)").all().result():
    print(e)

# COMMAND ----------

gremlin_client.submit("g.V().drop()").all().result()

# COMMAND ----------


spark = SparkSession.builder.appName("GraphRAGIngestion").getOrCreate()

blob_container = "rawdata"
blob_account = "barclayshackathontest"
# Replace with actual SAS token
sas_token = "sp=racwdl&st=2025-05-31T17:31:00Z&se=2025-06-07T01:31:00Z&spr=https&sv=2024-11-04&sr=c&sig=JKsY%2BTJgtgeCctNHwkqFgc0USNz8fV8YWa%2F3Y1FFCSk%3D"

# Configure access
spark.conf.set(
    f"fs.azure.sas.{blob_container}.{blob_account}.blob.core.windows.net", sas_token)

# Load CSVs
cr_main_df = spark.read.option("header", True).csv(
    f"wasbs://{blob_container}@{blob_account}.blob.core.windows.net/CR_Main_csv.csv").toPandas()
ctask_df = spark.read.option("header", True).csv(
    f"wasbs://{blob_container}@{blob_account}.blob.core.windows.net/CR_CTasks_csv.csv").toPandas()
jira_df = spark.read.option("header", True).csv(
    f"wasbs://{blob_container}@{blob_account}.blob.core.windows.net/JIRA_Issues_Detailed_csv.csv").toPandas()
activity_df = spark.read.option("header", True).csv(
    f"wasbs://{blob_container}@{blob_account}.blob.core.windows.net/JIRA_Activities_csv.csv").toPandas()
confluence_df = spark.read.option("header", True).csv(
    f"wasbs://{blob_container}@{blob_account}.blob.core.windows.net/Confluence_Pages_Detailed_csv.csv").toPandas()

print("Data loaded from Blob Storage!")

# Cosmos DB Config
cosmos_endpoint = "wss://hackathon-cosmosdb.gremlin.cosmos.azure.com:443/"
cosmos_key = "REMOVED_SECRET"
database = "graphrag"
container = "hackathongraph"

gremlin_client = client.Client(
    f"{cosmos_endpoint}",
    "g",
    username=f"/dbs/{database}/colls/{container}",
    password=cosmos_key,
    message_serializer=serializer.GraphSONSerializersV2d0()
)

print("Connected to Cosmos DB Graph!")

# Helper Function to Format Properties


def safe_props(row, columns):
    prop_list = []
    for col in columns:
        value = str(row[col]).replace('"', '\\"')
        prop_list.append(f'.property("{col}", "{value}")')
    return ''.join(prop_list)

# Helper Function to Check if Vertex Exists


def vertex_exists(vertex_id):
    result = gremlin_client.submit(
        f"g.V().has('id', '{vertex_id}').count()").all().result()
    return result[0] > 0


# Create Team Nodes
unique_teams = set(cr_main_df['CR_Team_Assignment_Group']).union(set(
    jira_df['JIRA_Team'])).union(set(confluence_df['Confluence_Team_Association']))
for team in unique_teams:
    team_id = f"TEAM-{team.replace(' ', '_')}"
    if not vertex_exists(team_id):
        gremlin_client.submit(f"""
            g.addV('Team').property('id', '{team_id}').property('team_name', '{team}').property('vertexType', 'Team')
        """).all().result()

# Create CR Nodes + BELONGS_TO
for _, row in cr_main_df.iterrows():
    cr_id = row['CR_ID']
    team_id = f"TEAM-{row['CR_Team_Assignment_Group'].replace(' ', '_')}"
    props = safe_props(row, cr_main_df.columns)
    if not vertex_exists(cr_id):
        gremlin_client.submit(
            f"""g.addV('CR').property('id', '{cr_id}').property('vertexType', 'CR'){props}""").all().result()
    gremlin_client.submit(
        f"""g.V().has('id', '{cr_id}').addE('BELONGS_TO').to(g.V().has('id', '{team_id}'))""").all().result()

# Create JIRA Nodes + BELONGS_TO
for _, row in jira_df.iterrows():
    jira_id = row['JIRA_ID']
    team_id = f"TEAM-{row['JIRA_Team'].replace(' ', '_')}"
    props = safe_props(row, jira_df.columns)
    if not vertex_exists(jira_id):
        gremlin_client.submit(
            f"""g.addV('JIRA').property('id', '{jira_id}').property('vertexType', 'JIRA'){props}""").all().result()
    gremlin_client.submit(
        f"""g.V().has('id', '{jira_id}').addE('BELONGS_TO').to(g.V().has('id', '{team_id}'))""").all().result()

# Create Confluence Nodes + BELONGS_TO
for _, row in confluence_df.iterrows():
    conf_id = row['Confluence_ID']
    team_id = f"TEAM-{row['Confluence_Team_Association'].replace(' ', '_')}"
    props = safe_props(row, confluence_df.columns)
    if not vertex_exists(conf_id):
        gremlin_client.submit(
            f"""g.addV('Confluence').property('id', '{conf_id}').property('vertexType', 'Confluence'){props}""").all().result()
    gremlin_client.submit(
        f"""g.V().has('id', '{conf_id}').addE('BELONGS_TO').to(g.V().has('id', '{team_id}'))""").all().result()

# Create REFERS_TO, MENTIONS, and other edges
for _, row in cr_main_df.iterrows():
    if pd.notna(row['Linked_Jira_ID']):
        gremlin_client.submit(
            f"""g.V().has('id', '{row['CR_ID']}').addE('REFERS_TO').to(g.V().has('id', '{row['Linked_Jira_ID']}'))""").all().result()
    if pd.notna(row['Linked_Confluence_ID']):
        gremlin_client.submit(
            f"""g.V().has('id', '{row['CR_ID']}').addE('REFERS_TO').to(g.V().has('id', '{row['Linked_Confluence_ID']}'))""").all().result()

for _, row in jira_df.iterrows():
    if pd.notna(row['CR_ID_Link_From_CSV_Example']):
        gremlin_client.submit(
            f"""g.V().has('id', '{row['JIRA_ID']}').addE('MENTIONS').to(g.V().has('id', '{row['CR_ID_Link_From_CSV_Example']}'))""").all().result()
    if pd.notna(row['JIRA_Linked_Issue_ID_Target']) and pd.notna(row['JIRA_Link_Type']):
        gremlin_client.submit(
            f"""g.V().has('id', '{row['JIRA_ID']}').addE('{row['JIRA_Link_Type']}').to(g.V().has('id', '{row['JIRA_Linked_Issue_ID_Target']}'))""").all().result()

for _, row in confluence_df.iterrows():
    if pd.notna(row['Confluence_Linked_Jira_ID']):
        for j in str(row['Confluence_Linked_Jira_ID']).split(';'):
            if j:
                gremlin_client.submit(
                    f"""g.V().has('id', '{row['Confluence_ID']}').addE('REFERS_TO').to(g.V().has('id', '{j}'))""").all().result()
    if pd.notna(row['Confluence_Linked_CR_ID']):
        for c in str(row['Confluence_Linked_CR_ID']).split(';'):
            if c:
                gremlin_client.submit(
                    f"""g.V().has('id', '{row['Confluence_ID']}').addE('REFERS_TO').to(g.V().has('id', '{c}'))""").all().result()

print("Data loaded and hierarchical ingestion complete! 🚀")

# COMMAND ----------

print("Vertices:")
for v in gremlin_client.submit("g.V().valueMap(true)").all().result():
    print(v)

print("\nEdges:")
for e in gremlin_client.submit("g.E().valueMap(true)").all().result():
    print(e)

# COMMAND ----------
