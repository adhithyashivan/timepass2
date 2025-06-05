import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import requests
import json
import os
import time
import asyncio

# --- Configuration ---
COSMOS_ENDPOINT = os.environ.get("COSMOS_ENDPOINT", "YOUR_COSMOS_DB_ENDPOINT")
COSMOS_KEY = os.environ.get("COSMOS_KEY", "YOUR_COSMOS_DB_PRIMARY_KEY")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "YourDatabaseName")
MONITORED_CONTAINER_NAME = os.environ.get(
    "MONITORED_CONTAINER_NAME", "YourMonitoredContainerName")
# Stores change feed processor state
LEASE_CONTAINER_NAME = os.environ.get("LEASE_CONTAINER_NAME", "leases")
POWER_AUTOMATE_URL = os.environ.get(
    "POWER_AUTOMATE_URL", "YOUR_POWER_AUTOMATE_HTTP_POST_URL")

# A unique name for this instance of the processor
HOST_NAME = "my-python-processor-host"

# --- Initialize Cosmos DB Client ---
client = cosmos_client.CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
monitored_container = database.get_container_client(MONITORED_CONTAINER_NAME)

# --- Ensure Lease Container Exists ---
try:
    lease_container = database.create_container_if_not_exists(
        id=LEASE_CONTAINER_NAME,
        # Lease container needs a partition key
        partition_key=PartitionKey(path="/id")
    )
    print(
        f"Lease container '{LEASE_CONTAINER_NAME}' created or already exists.")
except exceptions.CosmosResourceExistsError:
    lease_container = database.get_container_client(LEASE_CONTAINER_NAME)
    print(f"Lease container '{LEASE_CONTAINER_NAME}' already exists.")
except Exception as e:
    print(f"Error creating/accessing lease container: {e}")
    exit()

# --- Change Feed Processor Callback ---


async def process_changes(docs):
    print(f"Received {len(docs)} document(s) from Change Feed.")
    for doc in docs:
        print(f"Processing document ID: {doc.get('id')}")
        try:
            # Prepare data for Power Automate
            # You might want to transform or select specific fields from 'doc'
            payload = doc  # Send the whole document, or customize

            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                POWER_AUTOMATE_URL, data=json.dumps(payload), headers=headers)

            if response.status_code >= 200 and response.status_code < 300:
                print(
                    f"Successfully sent document {doc.get('id')} to Power Automate. Status: {response.status_code}")
            else:
                print(
                    f"Failed to send document {doc.get('id')} to Power Automate. Status: {response.status_code}, Response: {response.text}")

        except Exception as e:
            print(
                f"Error sending document {doc.get('id')} to Power Automate: {e}")
        # Add a small delay if sending many requests rapidly to avoid overwhelming Power Automate
        await asyncio.sleep(0.1)


# --- Build and Run the Change Feed Processor ---
async def main():
    print("Starting Change Feed Processor...")
    try:
        change_feed_processor = (
            monitored_container.get_change_feed_processor_builder(
                change_feed_processor_name="my-py-processor",  # A name for this processor
                callback=process_changes,
                lease_container_client=lease_container
            )
            .with_host_name(HOST_NAME)
            .with_feed_poll_delay(5)  # Poll every 5 seconds
            .build()
        )

        await change_feed_processor.start()
        print("Change Feed Processor started. Press Ctrl+C to stop.")

        # Keep the processor running
        while True:
            # Check status or do other things periodically
            await asyncio.sleep(60)

    except exceptions.CosmosHttpResponseError as e:
        print(f"Cosmos DB HTTP Error: {e.message}")
    except KeyboardInterrupt:
        print("Stopping Change Feed Processor...")
        if 'change_feed_processor' in locals() and change_feed_processor:
            await change_feed_processor.stop()
        print("Change Feed Processor stopped.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if 'change_feed_processor' in locals() and change_feed_processor:
            await change_feed_processor.stop()

if __name__ == "__main__":
    # Set environment variables or replace placeholders directly in the script
    # For example:
    # COSMOS_ENDPOINT = "https://your-cosmos-account.documents.azure.com:443/"
    # COSMOS_KEY = "YOUR_PRIMARY_KEY"
    # DATABASE_NAME = "ToDoList"
    # MONITORED_CONTAINER_NAME = "Items"
    # POWER_AUTOMATE_URL = "YOUR_FLOW_HTTP_URL"

    if not all([COSMOS_ENDPOINT, COSMOS_KEY, DATABASE_NAME, MONITORED_CONTAINER_NAME, POWER_AUTOMATE_URL]):
        print("Error: Ensure COSMOS_ENDPOINT, COSMOS_KEY, DATABASE_NAME, MONITORED_CONTAINER_NAME, and POWER_AUTOMATE_URL are set.")
    else:
        asyncio.run(main())
