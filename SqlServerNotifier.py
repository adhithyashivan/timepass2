# __init__.py for Azure Function (HTTP Trigger: FormatQuestionnaireEmail)
import logging
import azure.functions as func
import json
import datetime  # For better timestamp formatting if needed

# This is the formatting logic


def format_email_body_from_dict(audit_entry: dict) -> str:
    action = audit_entry.get("ActionTaken", "N/A")
    q_id = audit_entry.get("QuestionaireID", "N/A")

    timestamp_str = audit_entry.get("ActionTimestamp", "N/A")
    try:
        # SQL Server datetime might come in a specific format. Adjust if needed.
        # Example: '2023-10-27T10:30:00' (if no Z, assume local or needs timezone info)
        # If it includes timezone, fromisoformat might work directly if it's ISO 8601.
        if 'Z' in timestamp_str:  # Indicates UTC
            dt_obj = datetime.datetime.fromisoformat(
                timestamp_str.replace('Z', '+00:00'))
        elif '.' in timestamp_str:  # Handle milliseconds if present
            dt_obj = datetime.datetime.strptime(
                timestamp_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        else:
            dt_obj = datetime.datetime.strptime(
                timestamp_str, '%Y-%m-%dT%H:%M:%S')
        # Assuming original was UTC or converted
        timestamp = dt_obj.strftime('%Y-%m-%d %H:%M:%S UTC')
    except Exception as e:
        logging.warning(f"Could not parse timestamp '{timestamp_str}': {e}")
        timestamp = timestamp_str  # Fallback to original string if parsing fails

    user = audit_entry.get("ActionUser", "N/A")

    body = f"""
    <html><head><style>
        table {{ font-family: Arial, sans-serif; border-collapse: collapse; width: 100%; }}
        td, th {{ border: 1px solid #dddddd; text-align: left; padding: 8px; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        h2, h3, h4 {{ color: #333366; }}
    </style></head><body>
    <h2>Agent Questionnaire Change Notification</h2>
    <p>An action occurred on the Agent Questionnaire table:</p>
    <table>
        <tr><td><strong>Action:</strong></td><td>{action}</td></tr>
        <tr><td><strong>Questionnaire ID:</strong></td><td>{q_id}</td></tr>
        <tr><td><strong>Timestamp:</strong></td><td>{timestamp}</td></tr>
        <tr><td><strong>User:</strong></td><td>{user}</td></tr>
    </table>
    """

    if action == "INSERT":
        body += "<h3>New Entry Details:</h3><table>"
        body += f"<tr><td><strong>Question:</strong></td><td>{audit_entry.get('NewQuestion', 'N/A')}</td></tr>"
        body += f"<tr><td><strong>Answer:</strong></td><td>{audit_entry.get('NewAnswer', 'N/A')}</td></tr></table>"
    elif action == "DELETE":
        body += "<h3>Deleted Entry Details:</h3><table>"
        body += f"<tr><td><strong>Question:</strong></td><td>{audit_entry.get('OldQuestion', 'N/A')}</td></tr>"
        body += f"<tr><td><strong>Answer:</strong></td><td>{audit_entry.get('OldAnswer', 'N/A')}</td></tr></table>"
    elif action == "UPDATE":
        body += "<h3>Updated Entry Details:</h3>"
        body += "<h4>Before Change:</h4><table>"
        body += f"<tr><td><strong>Old Question:</strong></td><td>{audit_entry.get('OldQuestion', 'N/A')}</td></tr>"
        body += f"<tr><td><strong>Old Answer:</strong></td><td>{audit_entry.get('OldAnswer', 'N/A')}</td></tr></table>"
        body += "<h4>After Change:</h4><table>"
        body += f"<tr><td><strong>New Question:</strong></td><td>{audit_entry.get('NewQuestion', 'N/A')}</td></tr>"
        body += f"<tr><td><strong>New Answer:</strong></td><td>{audit_entry.get('NewAnswer', 'N/A')}</td></tr></table>"
    else:
        body += "<p>Unknown action type or details not fully available.</p>"

    body += "<hr><p><em>This is an automated notification.</em></p>"
    body += "</body></html>"
    return body

# Main function for the HTTP Trigger


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(
        'Python HTTP trigger function (FormatQuestionnaireEmail) processed a request.')

    try:
        # Power Automate will send the audit log row data as JSON in the request body
        audit_data_dict = req.get_json()
    except ValueError:
        logging.error("Request body is not valid JSON or is empty.")
        return func.HttpResponse(
            "ERROR: Please pass a valid JSON object in the request body representing the audit log entry.",
            status_code=400
        )

    if audit_data_dict:
        try:
            html_email_body = format_email_body_from_dict(audit_data_dict)

            # Return the HTML as the response body
            return func.HttpResponse(
                body=html_email_body,
                mimetype="text/html",
                status_code=200
            )
        except Exception as e:
            logging.error(f"Error formatting email content: {e}")
            return func.HttpResponse(
                f"ERROR: Internal server error during email formatting: {str(e)}",
                status_code=500
            )
    else:  # Should be caught by get_json() if body is empty, but as a fallback
        return func.HttpResponse(
            "ERROR: Please pass data in the request body.",
            status_code=400
        )
