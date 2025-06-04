import logging
import azure.functions as func
import json
import os
import requests  # For Teams Webhook
from sendgrid import SendGridAPIClient  # For SendGrid (Email)
from sendgrid.helpers.mail import Mail  # For SendGrid (Email)

# --- Configuration - Retrieve from Environment Variables (Function App Settings) ---
TEAMS_WEBHOOK_URL = os.environ.get('TEAMS_WEBHOOK_URL')
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDGRID_FROM_EMAIL = os.environ.get(
    'SENDGRID_FROM_EMAIL', 'noreply@example.com')  # Default if not set
NOTIFICATION_TO_EMAIL = os.environ.get('NOTIFICATION_TO_EMAIL')


def send_to_teams(message: str, log: logging.Logger):
    if not TEAMS_WEBHOOK_URL:
        log.warning("TEAMS_WEBHOOK_URL not set. Skipping Teams notification.")
        return

    payload = {"text": message}
    try:
        response = requests.post(TEAMS_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()  # Raises an exception for HTTP errors
        log.info(
            f"Message sent to Teams successfully. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        log.error(f"Error sending message to Teams: {e}")
    except Exception as e:
        log.error(f"An unexpected error occurred while sending to Teams: {e}")


def send_email_notification(subject: str, body: str, log: logging.Logger):
    if not SENDGRID_API_KEY or not NOTIFICATION_TO_EMAIL:
        log.warning(
            "SENDGRID_API_KEY or NOTIFICATION_TO_EMAIL not set. Skipping email notification.")
        return

    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=NOTIFICATION_TO_EMAIL,
        subject=subject,
        # Include raw doc for debug
        html_content=f"<strong>{body}</strong><p>Raw Document: <pre>{json.dumps(body, indent=2)}</pre></p>"
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        log.info(
            f"Email sent successfully. Status Code: {response.status_code}")
    except Exception as e:
        log.error(f"Error sending email: {e}")


def main(documents: func.DocumentList) -> None:
    if documents:
        logging.info(f"Received {len(documents)} document changes.")
        for doc in documents:
            try:
                # The 'doc' object is an azure.functions.Document, which acts like a dictionary.
                # You might need to convert to a standard dict if preferred for deep processing.
                # Get a standard dictionary representation
                doc_dict = json.loads(doc.to_json())

                element_id = doc_dict.get("id", "Unknown ID")
                label = doc_dict.get("label", "Unknown Label")
                notification_message = ""
                email_subject = ""

                # Heuristic to differentiate vertex from edge:
                # Edges in Cosmos DB Gremlin often have properties like '_isEdge: true',
                # or specific properties like 'inV', 'outV', '_sink', '_vertexId'.
                # Inspect your actual document structure in Cosmos DB to confirm.
                is_edge = doc_dict.get("_isEdge", False)
                if not is_edge:  # Fallback check for common Gremlin edge properties
                    is_edge = all(k in doc_dict for k in ("inV", "outV")) or \
                        all(k in doc_dict for k in ("_sink", "_vertexId"))

                if is_edge:
                    # if your edges store these
                    source_v_label = doc_dict.get(
                        "outVLabel", "UnknownSourceLabel")
                    # if your edges store these
                    target_v_label = doc_dict.get(
                        "inVLabel", "UnknownTargetLabel")
                    source_v_id = doc_dict.get(
                        "outV", doc_dict.get("_vertexId", "UnknownSourceID"))
                    target_v_id = doc_dict.get(
                        "inV", doc_dict.get("_sink", "UnknownTargetID"))

                    notification_message = (
                        f"Gremlin Edge Updated/Created: \n"
                        f"  Label: '{label}' (ID: {element_id})\n"
                        f"  From: Vertex '{source_v_label}' (ID: {source_v_id})\n"
                        f"  To:   Vertex '{target_v_label}' (ID: {target_v_id})"
                    )
                    email_subject = f"Gremlin Edge Update: {label} ({element_id})"
                else:  # Assume it's a vertex
                    notification_message = (
                        f"Gremlin Vertex Updated/Created: \n"
                        f"  Label: '{label}' (ID: {element_id})"
                    )
                    # You could add more details about changed properties here if needed
                    # e.g., by comparing with a previous state if you store snapshots (more complex)
                    email_subject = f"Gremlin Vertex Update: {label} ({element_id})"

                logging.info(
                    f"Processing change for document ID: {element_id}. Message: {notification_message}")

                # Send Notifications
                send_to_teams(notification_message, logging)
                send_email_notification(
                    email_subject, notification_message, logging)

            except Exception as e:
                logging.error(
                    f"Error processing document {doc.id if hasattr(doc, 'id') else 'Unknown ID'}: {e}")
                logging.error(
                    f"Problematic document content: {doc.to_json() if hasattr(doc, 'to_json') else str(doc)}")
