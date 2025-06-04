Okay, I will now generate the five interconnected CSV datasets according to your specifications.

```python
import csv
import io
import random
import datetime

# --- Configuration & User Data ---
users_all = ["PM_Anna", "Sarah_P", "David_H", "Alex_P_Dev", "Ben_P_Dev", "Chloe_P_Dev", "Mark_G", "Liam_G_Dev", "Olivia_G_Dev", "Noah_G_Dev", "QA_Emma", "Ethan_H_Sec", "Ops_Jim", "Marketer_Sue", "User_Kate", "User_Leo", "User_Mia", "User_Omar", "User_Pia", "User_Raj"]
users_phoenix_devs = ["Alex_P_Dev", "Ben_P_Dev", "Chloe_P_Dev"]
users_griffin_devs = ["Liam_G_Dev", "Olivia_G_Dev", "Noah_G_Dev"]
users_team_phoenix = ["PM_Anna"] + users_phoenix_devs
users_team_griffin = ["Sarah_P"] + users_griffin_devs
users_team_hydra = ["David_H", "QA_Emma", "Ethan_H_Sec", "Ops_Jim"]
users_dev = users_phoenix_devs + users_griffin_devs
users_technical = users_team_phoenix + users_team_griffin + users_team_hydra
users_requesters = ["PM_Anna", "Sarah_P", "David_H", "Marketer_Sue"] + users_dev
users_non_dev_technical = ["PM_Anna", "Sarah_P", "David_H", "QA_Emma", "Ethan_H_Sec", "Ops_Jim"]

jira_teams = ["Team Phoenix", "Team Griffin", "Team Hydra"]
cr_teams = ["Team Phoenix", "Team Griffin", "Team Hydra", "Marketing"]
conf_teams = ["Team Phoenix", "Team Griffin", "Team Hydra", "Cross-functional", "Marketing"]

def get_user_for_team(team_name):
    if team_name == "Team Phoenix":
        return random.choice(users_team_phoenix)
    elif team_name == "Team Griffin":
        return random.choice(users_team_griffin)
    elif team_name == "Team Hydra":
        return random.choice(users_team_hydra)
    elif team_name == "Marketing":
        return "Marketer_Sue"
    return random.choice(users_all)

# --- Date Utilities ---
base_date = datetime.date(2023, 9, 1)
current_sim_date = datetime.date(2024, 1, 15)

def random_date(start, end):
    return start + datetime.timedelta(days=random.randint(0, (end - start).days))

def format_date(d):
    return d.strftime("%Y-%m-%d")

def format_datetime(dt):
    return dt.strftime("%Y-%MM-%DD %H:%M") # Corrected format

def format_datetime_correct(dt_obj): # Corrected function to use actual datetime object
    return dt_obj.strftime("%Y-%m-%d %H:%M")


# --- Entity ID Lists (to be populated) ---
jira_ids_unique = []
cr_ids_unique = []
conf_ids_unique = []

# --- Helper for CSV output ---
def create_csv_output(filename, headers, data):
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL) # Use QUOTE_MINIMAL for less quoting
    # For fields that might contain commas, newlines, or double quotes, use QUOTE_ALL or ensure data is pre-quoted
    # For this exercise, specific long text fields will be quoted manually if needed.
    # Forcing quotes on specific fields if they might contain delimiters.
    # The problem states "Enclose fields containing commas, newlines, or double quotes in double quotes"
    # And "primarily use simple text ... minimizing internal commas/newlines unless a field is explicitly for longer text"
    # So, I'll only quote if there's a comma in a description field.

    def quote_if_needed(field_value, header_name):
        # Explicitly quote longer text fields
        long_text_headers = ["CR_Description", "JIRA_Description", "Confluence_Content_Summary",
                             "CR_Implementation_Plan_Summary", "CR_Backout_Plan_Summary", "Activity_Comment", "CTASK_Description"]
        if header_name in long_text_headers and isinstance(field_value, str) and ',' in field_value:
             return f'"{field_value}"' # Manual quoting
        if isinstance(field_value, str) and (',' in field_value or '"' in field_value or '\n' in field_value):
            return f'"{field_value.replace("\"", "\"\"")}"' # Standard CSV quoting
        return field_value

    writer.writerow(headers)
    for row_dict in data:
        # Ensure row has all headers, defaulting to blank if missing
        ordered_row = []
        for header in headers:
            val = row_dict.get(header, "")
            # Apply specific quoting for long text fields if they contain commas
            if header in ["CR_Description", "JIRA_Description", "Confluence_Content_Summary", "CR_Implementation_Plan_Summary", "CR_Backout_Plan_Summary", "Activity_Comment", "CTASK_Description"]:
                 if isinstance(val, str) and ',' in val:
                     val = f'"{val}"' # manual quoting for simplicity as requested
            elif isinstance(val, str) and (',' in val or '"' in val or '\n' in val): # general quoting
                 val = f'"{val.replace("\"", "\"\"")}"'
            ordered_row.append(val)
        # writer.writerow(ordered_row) # This would re-apply csv.writer quoting
        # To adhere to "manual quoting for simplicity" let's join manually
        output.write(",".join(map(str, ordered_row)) + "\n")


    content = output.getvalue()
    output.close()
    return f"--- START OF FILE {filename} ---\n{content.strip()}\n--- END OF FILE {filename} ---"

# --- 1. JIRA_Issues_Detailed.csv (70-75 unique issues) ---
jira_data_final_rows = []
jira_headers = [
    "JIRA_ID", "JIRA_Type", "JIRA_Priority", "JIRA_Components", "JIRA_Labels",
    "JIRA_Sprint", "JIRA_App_Name", "JIRA_Reporter", "JIRA_Assignee",
    "JIRA_Start_Date", "JIRA_End_Date", "JIRA_Status", "JIRA_Title", "JIRA_Description",
    "JIRA_Release_Fix_Version", "JIRA_Team", "JIRA_Confidence", "JIRA_Created_Date",
    "JIRA_Updated_Date", "JIRA_Effort_Story_Points", "CR_ID_Link_From_CSV_Example",
    "JIRA_Linked_Issue_ID_Target", "JIRA_Link_Type", "JIRA_Watcher_User"
]

num_unique_jira_issues = 72
jira_issue_counter = 1
jira_sprint_names = [f"Sprint {i} (Nova Beta)" for i in range(1, 6)] + [f"Sprint {i+5} (Nova Hotfix)" for i in range(1,3)]
jira_types = ["Story", "Task", "Bug", "Feature", "Epic", "Project", "Business Outcome"]
jira_priorities = ["Minor", "Major", "Critical", "Low", "Medium", "High"]
jira_statuses = ["Pending", "Development", "Review", "Release", "Closed", "Blocked", "Open", "In Progress"]
jira_link_types = ["blocks", "relates to", "duplicates", "sub-task of", "cloned by", "caused by"]
app_names = ["Mobile Wallet Core", "Auth Service", "Payment Gateway API", "Notification Service", ""]

# Generate base JIRA issue "concepts"
base_jira_issues = []
for i in range(1, num_unique_jira_issues + 1):
    jira_id = f"NOVA-{i}"
    jira_ids_unique.append(jira_id)
    created_d = random_date(base_date, base_date + datetime.timedelta(days=90))
    start_d = random_date(created_d, created_d + datetime.timedelta(days=10)) if random.choice([True, False]) else ""
    end_d = random_date(start_d, start_d + datetime.timedelta(days=30)) if start_d else ""
    updated_d = random_date(created_d, current_sim_date)
    if start_d and updated_d < start_d : updated_d = start_d # ensure updated is not before start

    jira_team = random.choice(jira_teams)
    assignee = get_user_for_team(jira_team) if random.random() > 0.2 else ""
    reporter = random.choice(users_technical)
    
    issue_type = random.choice(jira_types)
    if i <= 5: issue_type = "Epic" # First 5 are Epics
    elif i <= 30: issue_type = random.choice(["Story", "Feature"])
    elif i <= 55: issue_type = "Task"
    else: issue_type = "Bug"

    title_suffix = f"{issue_type} {i}"
    title = ""
    if issue_type == "Epic":
        epic_themes = ["Mobile Wallet MVP Development", "Post-Launch Stability Hotfix", "Security Hardening Initiative", "Payment Gateway V2 Integration", "User Experience Overhaul Phase 1"]
        title = epic_themes[(i-1)%len(epic_themes)]
        assignee = random.choice(["PM_Anna", "Sarah_P", "David_H"])
    elif issue_type == "Story":
        title = f"Implement user story for {title_suffix}"
    elif issue_type == "Task":
        title = f"Complete task for {title_suffix}"
    elif issue_type == "Bug":
        title = f"Fix bug related to {title_suffix}"
        assignee = get_user_for_team(random.choice([team for team in jira_teams if team != "Team Hydra"])) # Bugs usually assigned to dev teams
    elif issue_type == "Feature":
        title = f"Develop feature: {title_suffix}"

    desc = f"Detailed description for {title}. This involves several steps and considerations, including integration with other modules."
    if random.random() < 0.1: desc += " Also, please check the attached design document." # Add a comma for testing quotes

    components = ";".join(random.sample(["Backend", "Frontend", "API", "Database", "UI-Mobile", "SecurityLayer"], k=random.randint(0, 2)))
    labels = ";".join(random.sample(["critical-path", "beta-feature", "mvp", "tech-debt", "ux-improvement", "performance", "hotfix-candidate"], k=random.randint(0, 3)))
    
    status = random.choice(jira_statuses)
    if end_d and end_d < current_sim_date and status not in ["Closed", "Release"]:
        status = random.choice(["Closed", "Release"])
    if status == "Closed" and not end_d:
        end_d = random_date(start_d if start_d else created_d, updated_d)


    base_issue_data = {
        "JIRA_ID": jira_id,
        "JIRA_Type": issue_type,
        "JIRA_Priority": random.choice(jira_priorities),
        "JIRA_Components": components,
        "JIRA_Labels": labels,
        "JIRA_Sprint": random.choice(jira_sprint_names) if random.random() > 0.3 else "",
        "JIRA_App_Name": random.choice(app_names) if issue_type not in ["Epic", "Project"] else "",
        "JIRA_Reporter": reporter,
        "JIRA_Assignee": assignee,
        "JIRA_Start_Date": format_date(start_d) if start_d else "",
        "JIRA_End_Date": format_date(end_d) if end_d else "",
        "JIRA_Status": status,
        "JIRA_Title": title,
        "JIRA_Description": desc,
        "JIRA_Release_Fix_Version": f"v1.{random.randint(0,2)}.{random.randint(0,5)}" if status in ["Release", "Closed"] and random.random() > 0.4 else (f"Nova Hotfix {random.randint(1,3)}" if "Hotfix" in title else ""),
        "JIRA_Team": jira_team,
        "JIRA_Confidence": str(random.randint(50, 100)) if random.random() > 0.5 else "",
        "JIRA_Created_Date": format_date(created_d),
        "JIRA_Updated_Date": format_date(updated_d),
        "JIRA_Effort_Story_Points": str(random.choice([1, 2, 3, 5, 8, 13, 0])) if issue_type in ["Story", "Feature"] else "",
        "CR_ID_Link_From_CSV_Example": "", # To be populated later
        "JIRA_Linked_Issue_ID_Target": "",
        "JIRA_Link_Type": "",
        "JIRA_Watcher_User": ""
    }
    base_jira_issues.append(base_issue_data)

# Populate JIRA_data_final_rows based on base_jira_issues and links/watchers
for issue_data in base_jira_issues:
    num_links = 0
    num_watchers = 0

    # ~30% of issues get links/watchers
    if random.random() < 0.4:
        num_links = random.randint(0, 2)
    if random.random() < 0.5:
        num_watchers = random.randint(0, 3)

    has_any_extra_info = False
    
    # Create rows for links
    linked_issue_targets_for_this_issue = []
    if num_links > 0:
        possible_targets = [jid for jid in jira_ids_unique if jid != issue_data["JIRA_ID"]]
        if possible_targets:
            for _ in range(num_links):
                link_target_id = random.choice(possible_targets)
                if link_target_id not in linked_issue_targets_for_this_issue : # avoid duplicate links to same target
                    link_row = issue_data.copy()
                    link_row["JIRA_Linked_Issue_ID_Target"] = link_target_id
                    link_row["JIRA_Link_Type"] = random.choice(jira_link_types)
                    link_row["JIRA_Watcher_User"] = ""
                    jira_data_final_rows.append(link_row)
                    has_any_extra_info = True
                    linked_issue_targets_for_this_issue.append(link_target_id)


    # Create rows for watchers
    if num_watchers > 0:
        watchers_for_this_issue = random.sample(users_all, k=min(num_watchers, len(users_all)))
        for watcher in watchers_for_this_issue:
            watcher_row = issue_data.copy()
            watcher_row["JIRA_Linked_Issue_ID_Target"] = ""
            watcher_row["JIRA_Link_Type"] = ""
            watcher_row["JIRA_Watcher_User"] = watcher
            jira_data_final_rows.append(watcher_row)
            has_any_extra_info = True
            
    # If an issue has no links and no watchers, it still needs one row
    if not has_any_extra_info:
        base_row = issue_data.copy()
        base_row["JIRA_Linked_Issue_ID_Target"] = ""
        base_row["JIRA_Link_Type"] = ""
        base_row["JIRA_Watcher_User"] = ""
        jira_data_final_rows.append(base_row)


# --- 2. CR_Main.csv (21-24 unique Change Requests) ---
cr_main_data = []
cr_headers = [
    "CR_ID", "CR_Title", "Linked_Jira_ID", "Linked_Confluence_ID", "CR_State",
    "CR_Requested_By", "CR_Team_Assignment_Group", "CR_Assigned_To_User",
    "CR_Impacted_Environment", "CR_Impacted_Departments", "CR_Type", "CR_Category",
    "CR_Risk", "CR_Risk_Percentage", "CR_Lead_Time_Days", "CR_Conflict_Status",
    "CR_Description", "CR_Start_Date", "CR_End_Date",
    "CR_Implementation_Plan_Summary", "CR_Backout_Plan_Summary",
    "CR_Updated_By_User_From_CSV_Example", "CR_Created_At_From_CSV_Example"
]

num_unique_crs = 23
cr_states_flow = ["New", "Assess", "Authorise", "Scheduled", "Implement", "Closed"]
cr_types = ["Standard", "Emergency", "Normal"]
cr_categories = ["Enhancement", "BugFix", "Security", "Infrastructure", "Deployment", "Audit", "Maintenance", "New Feature", "Communication"]
cr_risks = ["Low", "Medium", "High"]
cr_environments = ["Production", "Staging", "Development", "N/A"]
cr_conflict_statuses = ["No Conflict", "Conflict Detected", "Resolved"]
departments = ["Engineering", "Product", "QA", "Security", "Operations", "Marketing", "Compliance", "Finance"]


for i in range(1, num_unique_crs + 1):
    cr_id = f"CR{str(i).zfill(3)}"
    cr_ids_unique.append(cr_id)
    
    original_request_date = random_date(base_date + datetime.timedelta(days=10), base_date + datetime.timedelta(days=120))
    cr_team = random.choice(cr_teams)
    assigned_user = get_user_for_team(cr_team)
    requested_by = random.choice(users_requesters)
    updated_by = random.choice(users_technical)
    cr_category = random.choice(cr_categories)
    
    title = f"{cr_category} CR - {cr_id}"
    if cr_category == "Deployment": title = f"Deployment of Project Nova Feature Set {i} - {cr_id}"
    if cr_category == "Emergency" and i < 5: title = f"Emergency Fix for Production Issue - {cr_id}" # Make first few emergency
        
    description = f"This change request ({cr_id}) is for {title}. It requires careful planning and execution. This CR, if approved, will proceed as planned."
    if random.random() < 0.1: description += " Key stakeholders involved: Product team, Engineering lead."


    impl_plan = f"Implementation plan for {cr_id}: 1. Prepare environment. 2. Deploy changes. 3. Verify."
    backout_plan = f"Backout plan for {cr_id}: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders."

    linked_jira = ""
    if random.random() < 0.7 and jira_ids_unique:
        # Link to JIRA Features or Epics sometimes
        relevant_jiras = [j for j_data in base_jira_issues if j_data["JIRA_Type"] in ["Feature", "Epic"] for j in [j_data["JIRA_ID"]]]
        if not relevant_jiras: relevant_jiras = jira_ids_unique # fallback to any JIRA
        linked_jira = random.choice(relevant_jiras)
        # Also add this CR_ID to the JIRA issue's CR_ID_Link_From_CSV_Example field
        for jira_row in jira_data_final_rows:
            if jira_row["JIRA_ID"] == linked_jira and not jira_row["CR_ID_Link_From_CSV_Example"]: # Link only once
                 jira_row["CR_ID_Link_From_CSV_Example"] = cr_id
                 break # Assuming JIRA_ID is unique enough here for first match, or all duplicated rows get it.
                      # The spec for JIRA_Issues_Detailed.csv says CR_ID_Link "or blank", implying one link per JIRA entry.
                      # All rows for a given JIRA_ID should have the same CR_ID_Link if it links to a CR.
        for base_issue in base_jira_issues: # Ensure the base concept also reflects this
            if base_issue["JIRA_ID"] == linked_jira:
                base_issue["CR_ID_Link_From_CSV_Example"] = cr_id


    num_status_updates = random.choice([1, 1, 1, 1, 2, 3, len(cr_states_flow)]) # Some CRs go through more states
    current_cr_date = original_request_date

    for state_idx in range(num_status_updates):
        cr_state = cr_states_flow[state_idx]
        cr_record_date = current_cr_date + datetime.timedelta(days=random.randint(1,5) * state_idx)
        if cr_record_date > current_sim_date: cr_record_date = current_sim_date # cap at current date
        
        start_date_cr = ""
        end_date_cr = ""
        if cr_state in ["Scheduled", "Implement", "Closed"]:
            start_date_cr = cr_record_date + datetime.timedelta(days=random.randint(1,7))
            if cr_state in ["Implement", "Closed"]:
                 end_date_cr = start_date_cr + datetime.timedelta(days=random.randint(1,14))
            if end_date_cr and end_date_cr > current_sim_date + datetime.timedelta(days=30): # cap end date
                 end_date_cr = current_sim_date + datetime.timedelta(days=30)
            if start_date_cr > current_sim_date + datetime.timedelta(days=30):
                 start_date_cr = "" # If start date is too far in future, nullify
                 end_date_cr = ""


        cr_main_data.append({
            "CR_ID": cr_id,
            "CR_Title": title,
            "Linked_Jira_ID": linked_jira,
            "Linked_Confluence_ID": "", # To be populated after Confluence
            "CR_State": cr_state,
            "CR_Requested_By": requested_by,
            "CR_Team_Assignment_Group": cr_team,
            "CR_Assigned_To_User": assigned_user if cr_state not in ["New", "Assess"] else "",
            "CR_Impacted_Environment": random.choice(cr_environments) if cr_category not in ["Communication", "Audit"] else "N/A",
            "CR_Impacted_Departments": ";".join(random.sample(departments, k=random.randint(1,3))),
            "CR_Type": random.choice(cr_types) if cr_category != "Emergency" else "Emergency",
            "CR_Category": cr_category,
            "CR_Risk": random.choice(cr_risks) if cr_category != "Emergency" else "High",
            "CR_Risk_Percentage": str(random.randint(0,100)) if random.random() > 0.3 else "",
            "CR_Lead_Time_Days": str(random.randint(1,30)),
            "CR_Conflict_Status": random.choice(cr_conflict_statuses) if cr_state not in ["New"] else "No Conflict",
            "CR_Description": description,
            "CR_Start_Date": format_date(start_date_cr) if start_date_cr else "",
            "CR_End_Date": format_date(end_date_cr) if end_date_cr else "",
            "CR_Implementation_Plan_Summary": impl_plan if cr_state in ["Authorise", "Scheduled", "Implement", "Closed"] else "Pending assessment",
            "CR_Backout_Plan_Summary": backout_plan if cr_state in ["Authorise", "Scheduled", "Implement", "Closed"] else "Pending assessment",
            "CR_Updated_By_User_From_CSV_Example": updated_by if state_idx > 0 else requested_by,
            "CR_Created_At_From_CSV_Example": format_date(cr_record_date)
        })
        if state_idx < num_status_updates -1 : # avoid date increment if last state
            current_cr_date = cr_record_date + datetime.timedelta(days=random.randint(1,3)) # next status update some days later


# --- 3. Confluence_Pages_Detailed.csv (20-25 unique pages) ---
confluence_data = []
confluence_headers = [
    "Confluence_ID", "Confluence_Title", "Confluence_Owner_Member",
    "Confluence_Last_Edited_By", "Confluence_Space", "Confluence_Team_Association",
    "Confluence_Content_Summary", "Confluence_Linked_Jira_ID",
    "Confluence_Linked_CR_ID", "Confluence_Parent_Page_ID",
    "Confluence_Created_Date", "Confluence_Last_Modified_Date"
]

num_conf_pages = 22
conf_spaces = ["Project Nova", "Engineering Docs", "QA Central", "Release Management", "Marketing Hub"]
conf_page_themes = [
    ("Project Nova Overview", "Project Nova"), ("Mobile Wallet Beta - Requirements", "Project Nova"),
    ("Backend API Specification v1", "Engineering Docs"), ("QA Test Plan - Sprint X", "QA Central"),
    ("Deployment Checklist - Beta Launch", "Release Management"), ("Hotfix NOVA-XXX - RCA", "Project Nova"),
    ("Release Notes - v1.0 Beta", "Release Management"), ("User Authentication Flow Design", "Engineering Docs"),
    ("Security Review Findings - Q4 2023", "QA Central"), ("Marketing Campaign Plan - Wallet Launch", "Marketing Hub"),
    ("Sprint Retrospective Notes - Sprint Y", "Project Nova"), ("Competitor Analysis - Mobile Wallets", "Marketing Hub")
]

for i in range(1, num_conf_pages + 1):
    conf_id = f"CONF-{str(i).zfill(3)}"
    conf_ids_unique.append(conf_id)
    
    created_d = random_date(base_date, base_date + datetime.timedelta(days=100))
    last_modified_d = random_date(created_d, current_sim_date)
    
    theme_title, default_space = random.choice(conf_page_themes)
    title = f"{theme_title} ({conf_id})"
    if "Sprint X" in title: title = title.replace("Sprint X", f"Sprint {random.randint(1,7)}")
    if "Sprint Y" in title: title = title.replace("Sprint Y", f"Sprint {random.randint(1,7)}")
    if "NOVA-XXX" in title and jira_ids_unique: title = title.replace("NOVA-XXX", random.choice(jira_ids_unique))
        
    owner = random.choice(users_technical)
    last_editor = random.choice(users_technical)
    space = default_space
    team_assoc = random.choice(conf_teams)
    
    summary = f"This document ({conf_id}: {title}) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context."
    if random.random() < 0.1: summary += " This page is currently under review, feedback is welcome."

    linked_jiras_list = []
    if random.random() < 0.7 and jira_ids_unique:
        linked_jiras_list = random.sample(jira_ids_unique, k=min(random.randint(1,3), len(jira_ids_unique)))
    linked_jiras_str = ";".join(linked_jiras_list)
    
    linked_crs_list = []
    if random.random() < 0.5 and cr_ids_unique:
        linked_crs_list = random.sample(cr_ids_unique, k=min(random.randint(1,2), len(cr_ids_unique)))
    linked_crs_str = ";".join(linked_crs_list)

    # Link this confluence page back to some CRs
    for cr_id_to_link in linked_crs_list:
        for cr_row in cr_main_data:
            if cr_row["CR_ID"] == cr_id_to_link and not cr_row["Linked_Confluence_ID"]: # Link only if not already linked
                cr_row["Linked_Confluence_ID"] = conf_id
                # Since CRs can have multiple rows for status, link to all of them or just the latest?
                # For simplicity, let's assume the CR object links to one Confluence page.
                # So, if a CR is linked, all its status rows will show the same Confluence ID.
                # This assignment may overwrite if multiple Confluence pages link to the same CR, but that's okay for sample data.

    parent_page_id = ""
    if i > 5 and random.random() < 0.4 and conf_ids_unique: # First 5 are top-level
        parent_page_id = random.choice(conf_ids_unique[:i-1]) # Link to an already created page

    confluence_data.append({
        "Confluence_ID": conf_id,
        "Confluence_Title": title,
        "Confluence_Owner_Member": owner,
        "Confluence_Last_Edited_By": last_editor,
        "Confluence_Space": space,
        "Confluence_Team_Association": team_assoc,
        "Confluence_Content_Summary": summary,
        "Confluence_Linked_Jira_ID": linked_jiras_str,
        "Confluence_Linked_CR_ID": linked_crs_str,
        "Confluence_Parent_Page_ID": parent_page_id,
        "Confluence_Created_Date": format_date(created_d),
        "Confluence_Last_Modified_Date": format_date(last_modified_d)
    })

# --- 4. JIRA_Activities.csv (15-20 entries) ---
jira_activities_data = []
jira_activities_headers = [
    "Activity_ID", "JIRA_ID", "Activity_Comment", "Activity_Timestamp", "Activity_User"
]
num_jira_activities = 18
activity_comments_templates = [
    "Status changed to {status}.", "Comment: Blocked by upstream dependency.", "Assigned to {user}.",
    "Effort estimated at {points} points.", "Ready for QA.", "Fix verified and closed.", "Reopened due to issue persistence.",
    "Deployment to Staging complete.", "New attachment: design_mockup_v2.png", "Priority set to {priority}."
]

# Select JIRA issues that are not Epics for activities
candidate_jira_ids_for_activity = [row["JIRA_ID"] for row in jira_data_final_rows if row["JIRA_Type"] != "Epic"]
# Use unique JIRA IDs for selection to avoid too many activities on one multi-row issue.
candidate_jira_ids_for_activity = list(set(candidate_jira_ids_for_activity))


if candidate_jira_ids_for_activity:
    for i in range(1, num_jira_activities + 1):
        activity_id = f"ACT-{str(i).zfill(3)}"
        jira_id_for_activity = random.choice(candidate_jira_ids_for_activity)
        
        # Find corresponding JIRA issue to get context (created date, status)
        # Taking the first row for a JIRA_ID, assuming core details are consistent
        jira_issue_details_list = [iss for iss in base_jira_issues if iss["JIRA_ID"] == jira_id_for_activity]
        if not jira_issue_details_list: continue # Should not happen if candidate_jira_ids come from base_jira_issues
        
        jira_issue_details = jira_issue_details_list[0]


        activity_user = random.choice(users_technical)
        comment_template = random.choice(activity_comments_templates)
        comment = comment_template.format(
            status=random.choice(jira_statuses), 
            user=random.choice(users_technical), 
            points=random.choice([1,2,3,5,8]),
            priority=random.choice(jira_priorities)
        )
        
        # Ensure activity timestamp is logical
        jira_created_dt = datetime.datetime.strptime(jira_issue_details["JIRA_Created_Date"], "%Y-%m-%d")
        jira_updated_dt = datetime.datetime.strptime(jira_issue_details["JIRA_Updated_Date"], "%Y-%m-%d")
        
        # Ensure activity timestamp is within the JIRA's lifecycle
        min_ts_dt = jira_created_dt
        max_ts_dt = jira_updated_dt if jira_updated_dt > jira_created_dt else jira_created_dt + datetime.timedelta(days=1)
        if max_ts_dt > datetime.datetime.combine(current_sim_date, datetime.datetime.min.time()):
            max_ts_dt = datetime.datetime.combine(current_sim_date, datetime.datetime.min.time())

        if min_ts_dt >= max_ts_dt : # if created and updated are same day, or created is after updated
            activity_ts_dt = min_ts_dt + datetime.timedelta(hours=random.randint(1,5))
        else:
            activity_ts_dt = min_ts_dt + datetime.timedelta(
                seconds=random.randint(0, int((max_ts_dt - min_ts_dt).total_seconds()))
            )
        
        activity_ts_dt = activity_ts_dt.replace(hour=random.randint(9,17), minute=random.randint(0,59))


        jira_activities_data.append({
            "Activity_ID": activity_id,
            "JIRA_ID": jira_id_for_activity,
            "Activity_Comment": comment,
            "Activity_Timestamp": format_datetime_correct(activity_ts_dt),
            "Activity_User": activity_user
        })

# --- 5. CR_CTasks.csv (10-15 CTask entries) ---
cr_ctasks_data = []
cr_ctasks_headers = [
    "CTASK_ID", "CR_ID", "CTASK_Assigned_To_User", "CTASK_Start_Time",
    "CTASK_End_Time", "CTASK_Description"
]
num_cr_ctasks = 12
ctask_description_templates = [
    "Perform technical assessment for CR.", "Develop and unit test changes for CR.",
    "Deploy CR to Staging environment.", "Execute UAT for CR.", "Schedule CR for production deployment.",
    "Communicate CR implementation to stakeholders.", "Monitor system post-CR implementation.",
    "Rollback CR due to unforeseen issues.", "Document CR closure."
]

# Select CRs that are in appropriate states for CTasks (e.g., Authorise, Scheduled, Implement)
candidate_cr_ids_for_ctask = [
    row["CR_ID"] for row in cr_main_data 
    if row["CR_State"] in ["Authorise", "Scheduled", "Implement"]
]
candidate_cr_ids_for_ctask = list(set(candidate_cr_ids_for_ctask)) # Unique CR_IDs

if candidate_cr_ids_for_ctask:
    for i in range(1, num_cr_ctasks + 1):
        ctask_id = f"CTASK{str(i).zfill(3)}"
        cr_id_for_ctask = random.choice(candidate_cr_ids_for_ctask)
        
        # Find corresponding CR to get dates and team
        cr_details_list = [cr for cr in cr_main_data if cr["CR_ID"] == cr_id_for_ctask and cr["CR_Start_Date"]]
        if not cr_details_list: continue # Skip if no suitable CR record found (e.g. no start date)
        
        cr_detail = random.choice(cr_details_list) # Pick one record of the CR
        
        assigned_user = cr_detail.get("CR_Assigned_To_User") or get_user_for_team(cr_detail["CR_Team_Assignment_Group"])
        description = random.choice(ctask_description_templates)
        
        cr_start_dt_str = cr_detail["CR_Start_Date"]
        cr_end_dt_str = cr_detail["CR_End_Date"]

        try:
            cr_start_datetime = datetime.datetime.strptime(cr_start_dt_str, "%Y-%m-%d")
            
            ctask_start_offset_days = random.randint(0, 3)
            ctask_start_time = cr_start_datetime + datetime.timedelta(days=ctask_start_offset_days)
            ctask_start_time = ctask_start_time.replace(hour=random.randint(9, 16), minute=random.choice([0, 15, 30, 45]))

            ctask_duration_hours = random.randint(1, 8)
            ctask_end_time = ctask_start_time + datetime.timedelta(hours=ctask_duration_hours)
            
            if cr_end_dt_str:
                cr_end_datetime = datetime.datetime.strptime(cr_end_dt_str, "%Y-%m-%d").replace(hour=23, minute=59)
                if ctask_end_time > cr_end_datetime:
                    ctask_end_time = cr_end_datetime
                if ctask_start_time > cr_end_datetime: # if somehow start is after CR end, adjust
                    ctask_start_time = cr_start_datetime 
                    ctask_end_time = ctask_start_time + datetime.timedelta(hours=1)


            cr_ctasks_data.append({
                "CTASK_ID": ctask_id,
                "CR_ID": cr_id_for_ctask,
                "CTASK_Assigned_To_User": assigned_user,
                "CTASK_Start_Time": format_datetime_correct(ctask_start_time),
                "CTASK_End_Time": format_datetime_correct(ctask_end_time),
                "CTASK_Description": description
            })
        except ValueError:
            # If CR_Start_Date is empty or invalid, skip this CTask or log error
            # For this generation, we just skip.
            continue


# --- Generate Final CSV Content ---
jira_csv_content = create_csv_output("JIRA_Issues_Detailed.csv", jira_headers, jira_data_final_rows)
cr_main_csv_content = create_csv_output("CR_Main.csv", cr_headers, cr_main_data)
confluence_csv_content = create_csv_output("Confluence_Pages_Detailed.csv", confluence_headers, confluence_data)
jira_activities_csv_content = create_csv_output("JIRA_Activities.csv", jira_activities_headers, jira_activities_data)
cr_ctasks_csv_content = create_csv_output("CR_CTasks.csv", cr_ctasks_headers, cr_ctasks_data)

# --- Print all CSV blocks ---
print(jira_csv_content)
print("\n")
print(cr_main_csv_content)
print("\n")
print(confluence_csv_content)
print("\n")
print(jira_activities_csv_content)
print("\n")
print(cr_ctasks_csv_content)

```

```
--- START OF FILE JIRA_Issues_Detailed.csv ---
JIRA_ID,JIRA_Type,JIRA_Priority,JIRA_Components,JIRA_Labels,JIRA_Sprint,JIRA_App_Name,JIRA_Reporter,JIRA_Assignee,JIRA_Start_Date,JIRA_End_Date,JIRA_Status,JIRA_Title,JIRA_Description,JIRA_Release_Fix_Version,JIRA_Team,JIRA_Confidence,JIRA_Created_Date,JIRA_Updated_Date,JIRA_Effort_Story_Points,CR_ID_Link_From_CSV_Example,JIRA_Linked_Issue_ID_Target,JIRA_Link_Type,JIRA_Watcher_User
NOVA-1,Epic,Critical,SecurityLayer;Database,ux-improvement;beta-feature;tech-debt,Sprint 3 (Nova Beta),,PM_Anna,PM_Anna,2023-10-04,2023-10-09,Pending,Mobile Wallet MVP Development,"Detailed description for Mobile Wallet MVP Development. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,77,2023-09-29,2023-12-27,,,NOVA-29,sub-task of,
NOVA-1,Epic,Critical,SecurityLayer;Database,ux-improvement;beta-feature;tech-debt,Sprint 3 (Nova Beta),,PM_Anna,PM_Anna,2023-10-04,2023-10-09,Pending,Mobile Wallet MVP Development,"Detailed description for Mobile Wallet MVP Development. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,77,2023-09-29,2023-12-27,,,NOVA-40,relates to,
NOVA-1,Epic,Critical,SecurityLayer;Database,ux-improvement;beta-feature;tech-debt,Sprint 3 (Nova Beta),,PM_Anna,PM_Anna,2023-10-04,2023-10-09,Pending,Mobile Wallet MVP Development,"Detailed description for Mobile Wallet MVP Development. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,77,2023-09-29,2023-12-27,,,,User_Omar
NOVA-1,Epic,Critical,SecurityLayer;Database,ux-improvement;beta-feature;tech-debt,Sprint 3 (Nova Beta),,PM_Anna,PM_Anna,2023-10-04,2023-10-09,Pending,Mobile Wallet MVP Development,"Detailed description for Mobile Wallet MVP Development. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,77,2023-09-29,2023-12-27,,,,User_Raj
NOVA-2,Epic,Critical,Database;API,tech-debt;performance;critical-path,Sprint 2 (Nova Beta),,David_H,David_H,2023-11-21,2023-12-02,Release,Post-Launch Stability Hotfix,"Detailed description for Post-Launch Stability Hotfix. This involves several steps and considerations, including integration with other modules.",v1.0.3,Team Hydra,82,2023-11-20,2024-01-06,,,NOVA-58,blocks,
NOVA-2,Epic,Critical,Database;API,tech-debt;performance;critical-path,Sprint 2 (Nova Beta),,David_H,David_H,2023-11-21,2023-12-02,Release,Post-Launch Stability Hotfix,"Detailed description for Post-Launch Stability Hotfix. This involves several steps and considerations, including integration with other modules.",v1.0.3,Team Hydra,82,2023-11-20,2024-01-06,,,,Ops_Jim
NOVA-3,Epic,Major,SecurityLayer;Backend,ux-improvement;critical-path;beta-feature,,PM_Anna,David_H,2023-09-05,2023-09-18,Release,Security Hardening Initiative,"Detailed description for Security Hardening Initiative. This involves several steps and considerations, including integration with other modules.",v1.1.1,Team Phoenix,69,2023-09-02,2023-11-06,,,NOVA-17,blocks,
NOVA-3,Epic,Major,SecurityLayer;Backend,ux-improvement;critical-path;beta-feature,,PM_Anna,David_H,2023-09-05,2023-09-18,Release,Security Hardening Initiative,"Detailed description for Security Hardening Initiative. This involves several steps and considerations, including integration with other modules.",v1.1.1,Team Phoenix,69,2023-09-02,2023-11-06,,,,User_Raj
NOVA-3,Epic,Major,SecurityLayer;Backend,ux-improvement;critical-path;beta-feature,,PM_Anna,David_H,2023-09-05,2023-09-18,Release,Security Hardening Initiative,"Detailed description for Security Hardening Initiative. This involves several steps and considerations, including integration with other modules.",v1.1.1,Team Phoenix,69,2023-09-02,2023-11-06,,,,Noah_G_Dev
NOVA-4,Epic,High,UI-Mobile;Frontend,tech-debt;performance;beta-feature,,PM_Anna,Sarah_P,2023-09-04,2023-10-02,Open,Payment Gateway V2 Integration,"Detailed description for Payment Gateway V2 Integration. This involves several steps and considerations, including integration with other modules.",,Team Griffin,59,2023-09-03,2023-12-09,,,,
NOVA-5,Epic,Critical,API,ux-improvement;critical-path,Sprint 7 (Nova Hotfix),,PM_Anna,Sarah_P,2023-11-05,2023-11-07,Closed,User Experience Overhaul Phase 1,"Detailed description for User Experience Overhaul Phase 1. This involves several steps and considerations, including integration with other modules. Also, please check the attached design document.",v1.2.0,Team Griffin,96,2023-10-24,2023-11-07,,,NOVA-46,relates to,
NOVA-5,Epic,Critical,API,ux-improvement;critical-path,Sprint 7 (Nova Hotfix),,PM_Anna,Sarah_P,2023-11-05,2023-11-07,Closed,User Experience Overhaul Phase 1,"Detailed description for User Experience Overhaul Phase 1. This involves several steps and considerations, including integration with other modules. Also, please check the attached design document.",v1.2.0,Team Griffin,96,2023-10-24,2023-11-07,,,,David_H
NOVA-6,Story,Low,UI-Mobile;SecurityLayer,mvp;performance,Sprint 4 (Nova Beta),Notification Service,User_Pia,Olivia_G_Dev,2023-11-28,2023-12-19,Closed,Implement user story for Story 6,"Detailed description for Implement user story for Story 6. This involves several steps and considerations, including integration with other modules.",v1.0.3,Team Griffin,,2023-11-02,2023-12-19,8,CR008,,NOVA-32,relates to,
NOVA-6,Story,Low,UI-Mobile;SecurityLayer,mvp;performance,Sprint 4 (Nova Beta),Notification Service,User_Pia,Olivia_G_Dev,2023-11-28,2023-12-19,Closed,Implement user story for Story 6,"Detailed description for Implement user story for Story 6. This involves several steps and considerations, including integration with other modules.",v1.0.3,Team Griffin,,2023-11-02,2023-12-19,8,CR008,NOVA-37,blocks,
NOVA-6,Story,Low,UI-Mobile;SecurityLayer,mvp;performance,Sprint 4 (Nova Beta),Notification Service,User_Pia,Olivia_G_Dev,2023-11-28,2023-12-19,Closed,Implement user story for Story 6,"Detailed description for Implement user story for Story 6. This involves several steps and considerations, including integration with other modules.",v1.0.3,Team Griffin,,2023-11-02,2023-12-19,8,CR008,,User_Pia
NOVA-6,Story,Low,UI-Mobile;SecurityLayer,mvp;performance,Sprint 4 (Nova Beta),Notification Service,User_Pia,Olivia_G_Dev,2023-11-28,2023-12-19,Closed,Implement user story for Story 6,"Detailed description for Implement user story for Story 6. This involves several steps and considerations, including integration with other modules.",v1.0.3,Team Griffin,,2023-11-02,2023-12-19,8,CR008,,User_Raj
NOVA-6,Story,Low,UI-Mobile;SecurityLayer,mvp;performance,Sprint 4 (Nova Beta),Notification Service,User_Pia,Olivia_G_Dev,2023-11-28,2023-12-19,Closed,Implement user story for Story 6,"Detailed description for Implement user story for Story 6. This involves several steps and considerations, including integration with other modules.",v1.0.3,Team Griffin,,2023-11-02,2023-12-19,8,CR008,,Marketer_Sue
NOVA-7,Feature,Minor,SecurityLayer;UI-Mobile,mvp;tech-debt,Sprint 7 (Nova Hotfix),Auth Service,User_Mia,Chloe_P_Dev,2023-11-19,2023-12-03,Closed,Develop feature: Feature 7,"Detailed description for Develop feature: Feature 7. This involves several steps and considerations, including integration with other modules.",v1.2.5,Team Phoenix,93,2023-11-19,2023-12-03,13,CR003,,NOVA-43,cloned by,
NOVA-7,Feature,Minor,SecurityLayer;UI-Mobile,mvp;tech-debt,Sprint 7 (Nova Hotfix),Auth Service,User_Mia,Chloe_P_Dev,2023-11-19,2023-12-03,Closed,Develop feature: Feature 7,"Detailed description for Develop feature: Feature 7. This involves several steps and considerations, including integration with other modules.",v1.2.5,Team Phoenix,93,2023-11-19,2023-12-03,13,CR003,,User_Leo
NOVA-7,Feature,Minor,SecurityLayer;UI-Mobile,mvp;tech-debt,Sprint 7 (Nova Hotfix),Auth Service,User_Mia,Chloe_P_Dev,2023-11-19,2023-12-03,Closed,Develop feature: Feature 7,"Detailed description for Develop feature: Feature 7. This involves several steps and considerations, including integration with other modules.",v1.2.5,Team Phoenix,93,2023-11-19,2023-12-03,13,CR003,,User_Pia
NOVA-8,Story,Minor,Database;API,critical-path;performance,Sprint 7 (Nova Hotfix),Auth Service,Ops_Jim,Noah_G_Dev,2023-10-17,2023-11-05,Closed,Implement user story for Story 8,"Detailed description for Implement user story for Story 8. This involves several steps and considerations, including integration with other modules.",v1.1.5,Team Griffin,51,2023-10-04,2023-11-05,2,,,,
NOVA-9,Story,Critical,Database;UI-Mobile,,Sprint 1 (Nova Beta),Auth Service,Mark_G,Alex_P_Dev,2023-11-23,2023-12-09,Closed,Implement user story for Story 9,"Detailed description for Implement user story for Story 9. This involves several steps and considerations, including integration with other modules.",v1.1.3,Team Phoenix,,2023-11-05,2023-12-09,2,,,,
NOVA-10,Story,Minor,SecurityLayer;UI-Mobile,performance;beta-feature,Sprint 3 (Nova Beta),Auth Service,Ethan_H_Sec,Ben_P_Dev,2023-10-08,2023-10-11,Open,Implement user story for Story 10,"Detailed description for Implement user story for Story 10. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,86,2023-09-17,2023-12-27,3,,,,
NOVA-11,Story,High,SecurityLayer;Frontend,ux-improvement;mvp;tech-debt,Sprint 2 (Nova Beta),Payment Gateway API,PM_Anna,Ben_P_Dev,2023-12-18,2024-01-01,In Progress,Implement user story for Story 11,"Detailed description for Implement user story for Story 11. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,59,2023-11-22,2024-01-03,13,,,,
NOVA-12,Story,Major,UI-Mobile;API,mvp;performance,Sprint 5 (Nova Beta),Auth Service,David_H,Alex_P_Dev,2023-10-14,2023-10-17,Closed,Implement user story for Story 12,"Detailed description for Implement user story for Story 12. This involves several steps and considerations, including integration with other modules.",v1.2.3,Team Phoenix,88,2023-09-26,2023-10-17,13,CR015,,NOVA-49,relates to,
NOVA-12,Story,Major,UI-Mobile;API,mvp;performance,Sprint 5 (Nova Beta),Auth Service,David_H,Alex_P_Dev,2023-10-14,2023-10-17,Closed,Implement user story for Story 12,"Detailed description for Implement user story for Story 12. This involves several steps and considerations, including integration with other modules.",v1.2.3,Team Phoenix,88,2023-09-26,2023-10-17,13,CR015,,Ops_Jim
NOVA-12,Story,Major,UI-Mobile;API,mvp;performance,Sprint 5 (Nova Beta),Auth Service,David_H,Alex_P_Dev,2023-10-14,2023-10-17,Closed,Implement user story for Story 12,"Detailed description for Implement user story for Story 12. This involves several steps and considerations, including integration with other modules.",v1.2.3,Team Phoenix,88,2023-09-26,2023-10-17,13,CR015,,Ben_P_Dev
NOVA-13,Feature,High,Database;SecurityLayer,beta-feature;critical-path;performance,Sprint 2 (Nova Beta),Mobile Wallet Core,User_Omar,Noah_G_Dev,2023-10-29,2023-11-06,Closed,Develop feature: Feature 13,"Detailed description for Develop feature: Feature 13. This involves several steps and considerations, including integration with other modules.",v1.0.2,Team Griffin,53,2023-09-27,2023-11-06,3,,,,
NOVA-14,Story,High,API;SecurityLayer,critical-path;mvp;tech-debt,Sprint 1 (Nova Beta),Auth Service,QA_Emma,Mark_G,2023-10-26,2023-11-12,Development,Implement user story for Story 14,"Detailed description for Implement user story for Story 14. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-10-24,2023-11-20,8,,,NOVA-41,blocks,
NOVA-14,Story,High,API;SecurityLayer,critical-path;mvp;tech-debt,Sprint 1 (Nova Beta),Auth Service,QA_Emma,Mark_G,2023-10-26,2023-11-12,Development,Implement user story for Story 14,"Detailed description for Implement user story for Story 14. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-10-24,2023-11-20,8,,,Sarah_P
NOVA-14,Story,High,API;SecurityLayer,critical-path;mvp;tech-debt,Sprint 1 (Nova Beta),Auth Service,QA_Emma,Mark_G,2023-10-26,2023-11-12,Development,Implement user story for Story 14,"Detailed description for Implement user story for Story 14. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-10-24,2023-11-20,8,,,David_H
NOVA-15,Feature,Low,Database;Backend,ux-improvement;performance;tech-debt,Sprint 7 (Nova Hotfix),Auth Service,User_Pia,Sarah_P,2023-09-20,2023-09-23,Open,Develop feature: Feature 15,"Detailed description for Develop feature: Feature 15. This involves several steps and considerations, including integration with other modules.",,Team Griffin,64,2023-09-19,2023-10-12,0,,,NOVA-64,blocks,
NOVA-15,Feature,Low,Database;Backend,ux-improvement;performance;tech-debt,Sprint 7 (Nova Hotfix),Auth Service,User_Pia,Sarah_P,2023-09-20,2023-09-23,Open,Develop feature: Feature 15,"Detailed description for Develop feature: Feature 15. This involves several steps and considerations, including integration with other modules.",,Team Griffin,64,2023-09-19,2023-10-12,0,,,User_Leo
NOVA-15,Feature,Low,Database;Backend,ux-improvement;performance;tech-debt,Sprint 7 (Nova Hotfix),Auth Service,User_Pia,Sarah_P,2023-09-20,2023-09-23,Open,Develop feature: Feature 15,"Detailed description for Develop feature: Feature 15. This involves several steps and considerations, including integration with other modules.",,Team Griffin,64,2023-09-19,2023-10-12,0,,,Ops_Jim
NOVA-16,Feature,Medium,Database,critical-path;performance;mvp,,Mobile Wallet Core,Ops_Jim,,2023-11-01,,Review,Develop feature: Feature 16,"Detailed description for Develop feature: Feature 16. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-09-06,2023-10-27,13,,,,
NOVA-17,Feature,Low,UI-Mobile;API,beta-feature;mvp,Sprint 5 (Nova Beta),,Noah_G_Dev,Olivia_G_Dev,2023-11-03,2023-11-14,Release,Develop feature: Feature 17,"Detailed description for Develop feature: Feature 17. This involves several steps and considerations, including integration with other modules. Also, please check the attached design document.",v1.0.0,Team Griffin,,2023-10-21,2023-11-14,13,CR001,,NOVA-57,sub-task of,
NOVA-17,Feature,Low,UI-Mobile;API,beta-feature;mvp,Sprint 5 (Nova Beta),,Noah_G_Dev,Olivia_G_Dev,2023-11-03,2023-11-14,Release,Develop feature: Feature 17,"Detailed description for Develop feature: Feature 17. This involves several steps and considerations, including integration with other modules. Also, please check the attached design document.",v1.0.0,Team Griffin,,2023-10-21,2023-11-14,13,CR001,,User_Kate
NOVA-17,Feature,Low,UI-Mobile;API,beta-feature;mvp,Sprint 5 (Nova Beta),,Noah_G_Dev,Olivia_G_Dev,2023-11-03,2023-11-14,Release,Develop feature: Feature 17,"Detailed description for Develop feature: Feature 17. This involves several steps and considerations, including integration with other modules. Also, please check the attached design document.",v1.0.0,Team Griffin,,2023-10-21,2023-11-14,13,CR001,,David_H
NOVA-18,Story,High,SecurityLayer;API,performance;tech-debt;critical-path,Sprint 5 (Nova Beta),Auth Service,User_Leo,Liam_G_Dev,2023-11-12,2023-11-24,Closed,Implement user story for Story 18,"Detailed description for Implement user story for Story 18. This involves several steps and considerations, including integration with other modules.",v1.0.2,Team Griffin,,2023-10-05,2023-11-24,8,,,,
NOVA-19,Story,High,UI-Mobile,beta-feature;performance,Sprint 6 (Nova Hotfix),Mobile Wallet Core,David_H,Noah_G_Dev,2023-12-05,2023-12-17,Development,Implement user story for Story 19,"Detailed description for Implement user story for Story 19. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-11-26,2023-12-17,2,,,NOVA-31,relates to,
NOVA-19,Story,High,UI-Mobile,beta-feature;performance,Sprint 6 (Nova Hotfix),Mobile Wallet Core,David_H,Noah_G_Dev,2023-12-05,2023-12-17,Development,Implement user story for Story 19,"Detailed description for Implement user story for Story 19. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-11-26,2023-12-17,2,,,Ben_P_Dev
NOVA-19,Story,High,UI-Mobile,beta-feature;performance,Sprint 6 (Nova Hotfix),Mobile Wallet Core,David_H,Noah_G_Dev,2023-12-05,2023-12-17,Development,Implement user story for Story 19,"Detailed description for Implement user story for Story 19. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-11-26,2023-12-17,2,,,Marketer_Sue
NOVA-20,Feature,Major,Database,beta-feature;tech-debt;ux-improvement,Sprint 5 (Nova Beta),Payment Gateway API,Ben_P_Dev,Alex_P_Dev,2023-10-05,2023-11-04,Release,Develop feature: Feature 20,"Detailed description for Develop feature: Feature 20. This involves several steps and considerations, including integration with other modules.",v1.0.2,Team Phoenix,,2023-09-07,2023-11-04,13,CR018,,NOVA-51,relates to,
NOVA-20,Feature,Major,Database,beta-feature;tech-debt;ux-improvement,Sprint 5 (Nova Beta),Payment Gateway API,Ben_P_Dev,Alex_P_Dev,2023-10-05,2023-11-04,Release,Develop feature: Feature 20,"Detailed description for Develop feature: Feature 20. This involves several steps and considerations, including integration with other modules.",v1.0.2,Team Phoenix,,2023-09-07,2023-11-04,13,CR018,,User_Raj
NOVA-21,Story,Medium,SecurityLayer;Frontend,performance;beta-feature,Sprint 3 (Nova Beta),Payment Gateway API,Chloe_P_Dev,Ben_P_Dev,2023-10-07,2023-10-17,Closed,Implement user story for Story 21,"Detailed description for Implement user story for Story 21. This involves several steps and considerations, including integration with other modules. Also, please check the attached design document.",v1.2.4,Team Phoenix,70,2023-10-02,2023-10-17,8,,,,
NOVA-22,Feature,Minor,Database;Frontend,tech-debt,Sprint 3 (Nova Beta),Mobile Wallet Core,Liam_G_Dev,Liam_G_Dev,2023-09-04,2023-09-29,Release,Develop feature: Feature 22,"Detailed description for Develop feature: Feature 22. This involves several steps and considerations, including integration with other modules.",v1.2.2,Team Griffin,94,2023-09-03,2023-10-15,1,,,,
NOVA-23,Feature,Low,UI-Mobile,critical-path;beta-feature;tech-debt,Sprint 2 (Nova Beta),Notification Service,User_Leo,Mark_G,2023-11-24,2023-12-23,In Progress,Develop feature: Feature 23,"Detailed description for Develop feature: Feature 23. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-11-15,2023-12-23,8,,,,
NOVA-24,Story,Medium,API;UI-Mobile,ux-improvement;critical-path,Sprint 7 (Nova Hotfix),Mobile Wallet Core,Mark_G,Noah_G_Dev,2023-09-23,2023-10-21,Pending,Implement user story for Story 24,"Detailed description for Implement user story for Story 24. This involves several steps and considerations, including integration with other modules.",,Team Griffin,93,2023-09-16,2023-11-23,0,CR016,,NOVA-50,relates to,
NOVA-24,Story,Medium,API;UI-Mobile,ux-improvement;critical-path,Sprint 7 (Nova Hotfix),Mobile Wallet Core,Mark_G,Noah_G_Dev,2023-09-23,2023-10-21,Pending,Implement user story for Story 24,"Detailed description for Implement user story for Story 24. This involves several steps and considerations, including integration with other modules.",,Team Griffin,93,2023-09-16,2023-11-23,0,CR016,,User_Kate
NOVA-24,Story,Medium,API;UI-Mobile,ux-improvement;critical-path,Sprint 7 (Nova Hotfix),Mobile Wallet Core,Mark_G,Noah_G_Dev,2023-09-23,2023-10-21,Pending,Implement user story for Story 24,"Detailed description for Implement user story for Story 24. This involves several steps and considerations, including integration with other modules.",,Team Griffin,93,2023-09-16,2023-11-23,0,CR016,,Ops_Jim
NOVA-25,Story,Medium,Database;Backend,beta-feature;ux-improvement,Sprint 4 (Nova Beta),Auth Service,Ethan_H_Sec,Alex_P_Dev,2023-10-29,2023-11-02,Review,Implement user story for Story 25,"Detailed description for Implement user story for Story 25. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,57,2023-10-19,2023-12-21,3,,,,
NOVA-26,Story,Minor,UI-Mobile;SecurityLayer,ux-improvement;mvp,Sprint 7 (Nova Hotfix),,Ben_P_Dev,Liam_G_Dev,2023-10-08,2023-10-21,Pending,Implement user story for Story 26,"Detailed description for Implement user story for Story 26. This involves several steps and considerations, including integration with other modules.",,Team Griffin,96,2023-09-15,2023-11-09,8,,,,
NOVA-27,Feature,Low,SecurityLayer,tech-debt;critical-path;performance,Sprint 4 (Nova Beta),Payment Gateway API,Mark_G,Sarah_P,2023-11-22,2023-12-03,Closed,Develop feature: Feature 27,"Detailed description for Develop feature: Feature 27. This involves several steps and considerations, including integration with other modules.",v1.1.5,Team Griffin,86,2023-11-09,2023-12-03,5,,,NOVA-49,blocks,
NOVA-27,Feature,Low,SecurityLayer,tech-debt;critical-path;performance,Sprint 4 (Nova Beta),Payment Gateway API,Mark_G,Sarah_P,2023-11-22,2023-12-03,Closed,Develop feature: Feature 27,"Detailed description for Develop feature: Feature 27. This involves several steps and considerations, including integration with other modules.",v1.1.5,Team Griffin,86,2023-11-09,2023-12-03,5,,,User_Mia
NOVA-27,Feature,Low,SecurityLayer,tech-debt;critical-path;performance,Sprint 4 (Nova Beta),Payment Gateway API,Mark_G,Sarah_P,2023-11-22,2023-12-03,Closed,Develop feature: Feature 27,"Detailed description for Develop feature: Feature 27. This involves several steps and considerations, including integration with other modules.",v1.1.5,Team Griffin,86,2023-11-09,2023-12-03,5,,,Noah_G_Dev
NOVA-28,Story,Minor,API;SecurityLayer,critical-path;performance,Sprint 3 (Nova Beta),Auth Service,Ops_Jim,Chloe_P_Dev,2023-09-26,2023-10-01,Release,Implement user story for Story 28,"Detailed description for Implement user story for Story 28. This involves several steps and considerations, including integration with other modules.",v1.1.3,Team Phoenix,,2023-09-16,2023-10-01,3,CR020,,NOVA-41,sub-task of,
NOVA-28,Story,Minor,API;SecurityLayer,critical-path;performance,Sprint 3 (Nova Beta),Auth Service,Ops_Jim,Chloe_P_Dev,2023-09-26,2023-10-01,Release,Implement user story for Story 28,"Detailed description for Implement user story for Story 28. This involves several steps and considerations, including integration with other modules.",v1.1.3,Team Phoenix,,2023-09-16,2023-10-01,3,CR020,,Ben_P_Dev
NOVA-28,Story,Minor,API;SecurityLayer,critical-path;performance,Sprint 3 (Nova Beta),Auth Service,Ops_Jim,Chloe_P_Dev,2023-09-26,2023-10-01,Release,Implement user story for Story 28,"Detailed description for Implement user story for Story 28. This involves several steps and considerations, including integration with other modules.",v1.1.3,Team Phoenix,,2023-09-16,2023-10-01,3,CR020,,Mark_G
NOVA-29,Story,Medium,API;SecurityLayer,ux-improvement;performance,Sprint 2 (Nova Beta),Notification Service,User_Omar,Mark_G,2023-11-05,2023-11-22,Review,Implement user story for Story 29,"Detailed description for Implement user story for Story 29. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-10-28,2023-11-27,3,,,,
NOVA-30,Feature,Minor,UI-Mobile,tech-debt;critical-path,Sprint 7 (Nova Hotfix),Payment Gateway API,Mark_G,Olivia_G_Dev,2023-10-27,2023-11-15,Closed,Develop feature: Feature 30,"Detailed description for Develop feature: Feature 30. This involves several steps and considerations, including integration with other modules.",v1.1.1,Team Griffin,,2023-10-13,2023-11-15,3,CR022,,NOVA-69,cloned by,
NOVA-30,Feature,Minor,UI-Mobile,tech-debt;critical-path,Sprint 7 (Nova Hotfix),Payment Gateway API,Mark_G,Olivia_G_Dev,2023-10-27,2023-11-15,Closed,Develop feature: Feature 30,"Detailed description for Develop feature: Feature 30. This involves several steps and considerations, including integration with other modules.",v1.1.1,Team Griffin,,2023-10-13,2023-11-15,3,CR022,,Alex_P_Dev
NOVA-31,Task,High,API,critical-path;beta-feature;mvp,Sprint 3 (Nova Beta),Auth Service,User_Pia,Ben_P_Dev,2023-11-07,2023-11-11,Pending,Complete task for Task 31,"Detailed description for Complete task for Task 31. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,68,2023-10-28,2023-12-18,,,,NOVA-65,relates to,
NOVA-31,Task,High,API,critical-path;beta-feature;mvp,Sprint 3 (Nova Beta),Auth Service,User_Pia,Ben_P_Dev,2023-11-07,2023-11-11,Pending,Complete task for Task 31,"Detailed description for Complete task for Task 31. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,68,2023-10-28,2023-12-18,,,,David_H
NOVA-32,Task,Low,Backend,mvp;ux-improvement;tech-debt,Sprint 2 (Nova Beta),Notification Service,Alex_P_Dev,Chloe_P_Dev,2023-10-04,2023-10-11,Development,Complete task for Task 32,"Detailed description for Complete task for Task 32. This involves several steps and considerations, including integration with other modules. Also, please check the attached design document.",,Team Phoenix,88,2023-09-12,2023-10-25,,,,
NOVA-33,Task,Low,Database;Frontend,performance;ux-improvement;critical-path,Sprint 6 (Nova Hotfix),Payment Gateway API,User_Omar,Ben_P_Dev,2023-11-29,2023-12-09,Closed,Complete task for Task 33,"Detailed description for Complete task for Task 33. This involves several steps and considerations, including integration with other modules.",v1.2.0,Team Phoenix,69,2023-11-28,2023-12-09,,,,
NOVA-34,Task,Medium,SecurityLayer;Backend,mvp;tech-debt,Sprint 2 (Nova Beta),Notification Service,User_Mia,David_H,2023-11-09,2023-11-25,Release,Complete task for Task 34,"Detailed description for Complete task for Task 34. This involves several steps and considerations, including integration with other modules.",v1.2.5,Team Hydra,82,2023-10-18,2023-11-25,,,,
NOVA-35,Task,Major,Database;UI-Mobile,beta-feature;performance;ux-improvement,Sprint 4 (Nova Beta),Notification Service,User_Pia,Olivia_G_Dev,2023-11-06,2023-11-26,Pending,Complete task for Task 35,"Detailed description for Complete task for Task 35. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-10-12,2023-12-14,,,,
NOVA-36,Task,Major,UI-Mobile;API,ux-improvement;critical-path;beta-feature,,Mobile Wallet Core,User_Kate,Mark_G,2023-10-03,2023-10-14,Closed,Complete task for Task 36,"Detailed description for Complete task for Task 36. This involves several steps and considerations, including integration with other modules.",v1.1.1,Team Griffin,,2023-09-26,2023-10-14,,,NOVA-42,blocks,
NOVA-36,Task,Major,UI-Mobile;API,ux-improvement;critical-path;beta-feature,,Mobile Wallet Core,User_Kate,Mark_G,2023-10-03,2023-10-14,Closed,Complete task for Task 36,"Detailed description for Complete task for Task 36. This involves several steps and considerations, including integration with other modules.",v1.1.1,Team Griffin,,2023-09-26,2023-10-14,,,Mark_G
NOVA-37,Task,High,UI-Mobile;API,mvp;performance;ux-improvement,Sprint 6 (Nova Hotfix),Auth Service,PM_Anna,Ben_P_Dev,2023-10-21,2023-11-01,Review,Complete task for Task 37,"Detailed description for Complete task for Task 37. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,,2023-09-21,2023-11-01,,,,
NOVA-38,Task,Major,UI-Mobile;API,critical-path;mvp,Sprint 3 (Nova Beta),Auth Service,User_Leo,QA_Emma,2023-09-19,2023-09-26,Blocked,Complete task for Task 38,"Detailed description for Complete task for Task 38. This involves several steps and considerations, including integration with other modules.",,Team Hydra,,2023-09-12,2023-09-26,,,,
NOVA-39,Task,High,Frontend;Database,critical-path;tech-debt;beta-feature,Sprint 5 (Nova Beta),Mobile Wallet Core,PM_Anna,Sarah_P,2023-11-06,2023-11-25,Closed,Complete task for Task 39,"Detailed description for Complete task for Task 39. This involves several steps and considerations, including integration with other modules.",v1.0.1,Team Griffin,73,2023-10-22,2023-11-25,,,,
NOVA-40,Task,Minor,SecurityLayer;API,ux-improvement;performance;critical-path,Sprint 7 (Nova Hotfix),Mobile Wallet Core,Ethan_H_Sec,Liam_G_Dev,2023-10-17,2023-10-24,In Progress,Complete task for Task 40,"Detailed description for Complete task for Task 40. This involves several steps and considerations, including integration with other modules.",,Team Griffin,79,2023-10-11,2023-10-24,,,,
NOVA-41,Task,Low,SecurityLayer;API,critical-path;ux-improvement;mvp,Sprint 3 (Nova Beta),Notification Service,User_Mia,Noah_G_Dev,2023-09-10,2023-09-29,Release,Complete task for Task 41,"Detailed description for Complete task for Task 41. This involves several steps and considerations, including integration with other modules.",v1.2.0,Team Griffin,68,2023-09-08,2023-11-05,,,NOVA-53,blocks,
NOVA-41,Task,Low,SecurityLayer;API,critical-path;ux-improvement;mvp,Sprint 3 (Nova Beta),Notification Service,User_Mia,Noah_G_Dev,2023-09-10,2023-09-29,Release,Complete task for Task 41,"Detailed description for Complete task for Task 41. This involves several steps and considerations, including integration with other modules.",v1.2.0,Team Griffin,68,2023-09-08,2023-11-05,,,User_Kate
NOVA-41,Task,Low,SecurityLayer;API,critical-path;ux-improvement;mvp,Sprint 3 (Nova Beta),Notification Service,User_Mia,Noah_G_Dev,2023-09-10,2023-09-29,Release,Complete task for Task 41,"Detailed description for Complete task for Task 41. This involves several steps and considerations, including integration with other modules.",v1.2.0,Team Griffin,68,2023-09-08,2023-11-05,,,User_Omar
NOVA-42,Task,Critical,UI-Mobile;SecurityLayer,critical-path;performance;mvp,Sprint 5 (Nova Beta),Mobile Wallet Core,Noah_G_Dev,Ops_Jim,2023-09-27,2023-10-08,Pending,Complete task for Task 42,"Detailed description for Complete task for Task 42. This involves several steps and considerations, including integration with other modules. Also, please check the attached design document.",,Team Hydra,82,2023-09-21,2023-11-08,,,,
NOVA-43,Task,High,UI-Mobile;API,mvp;critical-path,Sprint 1 (Nova Beta),Mobile Wallet Core,PM_Anna,Chloe_P_Dev,2023-10-02,2023-10-23,Closed,Complete task for Task 43,"Detailed description for Complete task for Task 43. This involves several steps and considerations, including integration with other modules.",v1.1.2,Team Phoenix,,2023-09-12,2023-10-23,,,,
NOVA-44,Task,Low,SecurityLayer,tech-debt;performance,Sprint 4 (Nova Beta),,Ops_Jim,Mark_G,2023-10-03,2023-10-21,Closed,Complete task for Task 44,"Detailed description for Complete task for Task 44. This involves several steps and considerations, including integration with other modules. Also, please check the attached design document.",v1.0.2,Team Griffin,,2023-09-03,2023-10-21,,,,
NOVA-45,Task,Major,Frontend;UI-Mobile,critical-path;performance;mvp,Sprint 6 (Nova Hotfix),Notification Service,User_Pia,Ben_P_Dev,2023-09-17,2023-09-26,Closed,Complete task for Task 45,"Detailed description for Complete task for Task 45. This involves several steps and considerations, including integration with other modules.",v1.1.0,Team Phoenix,,2023-09-12,2023-09-26,,,NOVA-52,relates to,
NOVA-45,Task,Major,Frontend;UI-Mobile,critical-path;performance;mvp,Sprint 6 (Nova Hotfix),Notification Service,User_Pia,Ben_P_Dev,2023-09-17,2023-09-26,Closed,Complete task for Task 45,"Detailed description for Complete task for Task 45. This involves several steps and considerations, including integration with other modules.",v1.1.0,Team Phoenix,,2023-09-12,2023-09-26,,,Ethan_H_Sec
NOVA-46,Task,Minor,Backend,critical-path;mvp,,Mobile Wallet Core,User_Pia,Ben_P_Dev,2023-09-27,2023-10-23,Blocked,Complete task for Task 46,"Detailed description for Complete task for Task 46. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,82,2023-09-23,2023-10-23,,,NOVA-72,relates to,
NOVA-46,Task,Minor,Backend,critical-path;mvp,,Mobile Wallet Core,User_Pia,Ben_P_Dev,2023-09-27,2023-10-23,Blocked,Complete task for Task 46,"Detailed description for Complete task for Task 46. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,82,2023-09-23,2023-10-23,,,Ops_Jim
NOVA-46,Task,Minor,Backend,critical-path;mvp,,Mobile Wallet Core,User_Pia,Ben_P_Dev,2023-09-27,2023-10-23,Blocked,Complete task for Task 46,"Detailed description for Complete task for Task 46. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,82,2023-09-23,2023-10-23,,,User_Kate
NOVA-47,Task,Critical,API,beta-feature;ux-improvement;performance,Sprint 5 (Nova Beta),Auth Service,Ops_Jim,Chloe_P_Dev,2023-11-06,2023-11-25,Closed,Complete task for Task 47,"Detailed description for Complete task for Task 47. This involves several steps and considerations, including integration with other modules. Also, please check the attached design document.",v1.1.3,Team Phoenix,,2023-10-14,2023-11-25,,,,
NOVA-48,Task,High,UI-Mobile;API,tech-debt;mvp;critical-path,Sprint 6 (Nova Hotfix),Notification Service,User_Mia,Liam_G_Dev,2023-11-09,2023-11-21,Review,Complete task for Task 48,"Detailed description for Complete task for Task 48. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-10-10,2023-11-21,,,NOVA-53,relates to,
NOVA-48,Task,High,UI-Mobile;API,tech-debt;mvp;critical-path,Sprint 6 (Nova Hotfix),Notification Service,User_Mia,Liam_G_Dev,2023-11-09,2023-11-21,Review,Complete task for Task 48,"Detailed description for Complete task for Task 48. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-10-10,2023-11-21,,,User_Kate
NOVA-49,Task,Minor,Frontend;Database,ux-improvement;critical-path;performance,Sprint 2 (Nova Beta),Payment Gateway API,User_Pia,Alex_P_Dev,2023-09-22,2023-10-09,Release,Complete task for Task 49,"Detailed description for Complete task for Task 49. This involves several steps and considerations, including integration with other modules.",v1.1.2,Team Phoenix,,2023-09-20,2023-10-25,,,,
NOVA-50,Task,Minor,Database,tech-debt;critical-path;mvp,Sprint 2 (Nova Beta),Mobile Wallet Core,PM_Anna,Olivia_G_Dev,2023-10-02,2023-10-24,Closed,Complete task for Task 50,"Detailed description for Complete task for Task 50. This involves several steps and considerations, including integration with other modules.",v1.2.4,Team Griffin,77,2023-09-26,2023-10-24,,,,
NOVA-51,Task,Critical,Database,ux-improvement,Sprint 7 (Nova Hotfix),,Ops_Jim,Chloe_P_Dev,2023-10-08,2023-10-16,Review,Complete task for Task 51,"Detailed description for Complete task for Task 51. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,,2023-10-01,2023-11-05,,,,
NOVA-52,Task,Medium,API;UI-Mobile,beta-feature;critical-path,Sprint 2 (Nova Beta),Auth Service,Ops_Jim,Alex_P_Dev,2023-10-06,2023-10-25,Development,Complete task for Task 52,"Detailed description for Complete task for Task 52. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,,2023-09-24,2023-12-12,,,NOVA-57,blocks,
NOVA-52,Task,Medium,API;UI-Mobile,beta-feature;critical-path,Sprint 2 (Nova Beta),Auth Service,Ops_Jim,Alex_P_Dev,2023-10-06,2023-10-25,Development,Complete task for Task 52,"Detailed description for Complete task for Task 52. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,,2023-09-24,2023-12-12,,,User_Leo
NOVA-53,Task,Low,Database;SecurityLayer,critical-path;beta-feature,Sprint 3 (Nova Beta),Auth Service,User_Kate,Chloe_P_Dev,2023-11-06,2023-11-23,Closed,Complete task for Task 53,"Detailed description for Complete task for Task 53. This involves several steps and considerations, including integration with other modules.",v1.2.3,Team Phoenix,,2023-10-11,2023-11-23,,,,
NOVA-54,Task,Minor,SecurityLayer;UI-Mobile,tech-debt;beta-feature;performance,Sprint 2 (Nova Beta),Mobile Wallet Core,Ben_P_Dev,QA_Emma,2023-10-23,2023-11-06,Open,Complete task for Task 54,"Detailed description for Complete task for Task 54. This involves several steps and considerations, including integration with other modules.",,Team Hydra,67,2023-10-08,2023-11-18,,,,
NOVA-55,Task,High,API;Backend,ux-improvement;critical-path;beta-feature,Sprint 7 (Nova Hotfix),Auth Service,User_Raj,Ethan_H_Sec,2023-10-24,2023-11-07,Development,Complete task for Task 55,"Detailed description for Complete task for Task 55. This involves several steps and considerations, including integration with other modules.",,Team Hydra,,2023-10-19,2023-11-17,,,NOVA-66,duplicates,
NOVA-55,Task,High,API;Backend,ux-improvement;critical-path;beta-feature,Sprint 7 (Nova Hotfix),Auth Service,User_Raj,Ethan_H_Sec,2023-10-24,2023-11-07,Development,Complete task for Task 55,"Detailed description for Complete task for Task 55. This involves several steps and considerations, including integration with other modules.",,Team Hydra,,2023-10-19,2023-11-17,,,Ben_P_Dev
NOVA-55,Task,High,API;Backend,ux-improvement;critical-path;beta-feature,Sprint 7 (Nova Hotfix),Auth Service,User_Raj,Ethan_H_Sec,2023-10-24,2023-11-07,Development,Complete task for Task 55,"Detailed description for Complete task for Task 55. This involves several steps and considerations, including integration with other modules.",,Team Hydra,,2023-10-19,2023-11-17,,,Mark_G
NOVA-56,Bug,Minor,API;SecurityLayer,ux-improvement;beta-feature,Sprint 5 (Nova Beta),Notification Service,QA_Emma,Alex_P_Dev,2023-10-18,2023-11-14,In Progress,Fix bug related to Bug 56,"Detailed description for Fix bug related to Bug 56. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,54,2023-10-15,2023-11-14,,,,
NOVA-57,Bug,Critical,Database,critical-path,Sprint 1 (Nova Beta),Payment Gateway API,User_Omar,Mark_G,2023-10-11,2023-10-15,Release,Fix bug related to Bug 57,"Detailed description for Fix bug related to Bug 57. This involves several steps and considerations, including integration with other modules.",v1.0.1,Team Griffin,99,2023-09-13,2023-10-15,,,NOVA-71,blocks,
NOVA-57,Bug,Critical,Database,critical-path,Sprint 1 (Nova Beta),Payment Gateway API,User_Omar,Mark_G,2023-10-11,2023-10-15,Release,Fix bug related to Bug 57,"Detailed description for Fix bug related to Bug 57. This involves several steps and considerations, including integration with other modules.",v1.0.1,Team Griffin,99,2023-09-13,2023-10-15,,,User_Omar
NOVA-58,Bug,Major,Backend,beta-feature;mvp,Sprint 5 (Nova Beta),Notification Service,Noah_G_Dev,Chloe_P_Dev,2023-11-17,2023-12-08,Open,Fix bug related to Bug 58,"Detailed description for Fix bug related to Bug 58. This involves several steps and considerations, including integration with other modules. Also, please check the attached design document.",,Team Phoenix,,2023-10-30,2023-12-19,,,,
NOVA-59,Bug,Low,UI-Mobile;API,performance;tech-debt;mvp,Sprint 3 (Nova Beta),Mobile Wallet Core,Ben_P_Dev,Alex_P_Dev,2023-11-24,2023-12-08,Blocked,Fix bug related to Bug 59,"Detailed description for Fix bug related to Bug 59. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,,2023-11-21,2023-12-11,,,,
NOVA-60,Bug,Critical,Database;Backend,beta-feature;critical-path;ux-improvement,Sprint 6 (Nova Hotfix),Mobile Wallet Core,Chloe_P_Dev,Ben_P_Dev,2023-10-01,2023-10-16,Closed,Fix bug related to Bug 60,"Detailed description for Fix bug related to Bug 60. This involves several steps and considerations, including integration with other modules.",v1.0.1,Team Phoenix,72,2023-09-03,2023-10-16,,,NOVA-64,caused by,
NOVA-60,Bug,Critical,Database;Backend,beta-feature;critical-path;ux-improvement,Sprint 6 (Nova Hotfix),Mobile Wallet Core,Chloe_P_Dev,Ben_P_Dev,2023-10-01,2023-10-16,Closed,Fix bug related to Bug 60,"Detailed description for Fix bug related to Bug 60. This involves several steps and considerations, including integration with other modules.",v1.0.1,Team Phoenix,72,2023-09-03,2023-10-16,,,User_Mia
NOVA-60,Bug,Critical,Database;Backend,beta-feature;critical-path;ux-improvement,Sprint 6 (Nova Hotfix),Mobile Wallet Core,Chloe_P_Dev,Ben_P_Dev,2023-10-01,2023-10-16,Closed,Fix bug related to Bug 60,"Detailed description for Fix bug related to Bug 60. This involves several steps and considerations, including integration with other modules.",v1.0.1,Team Phoenix,72,2023-09-03,2023-10-16,,,Mark_G
NOVA-61,Bug,Low,API;Backend,ux-improvement;performance;mvp,Sprint 1 (Nova Beta),Payment Gateway API,Ops_Jim,Chloe_P_Dev,2023-11-24,2023-12-17,Pending,Fix bug related to Bug 61,"Detailed description for Fix bug related to Bug 61. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,,2023-10-28,2023-12-26,,,NOVA-67,duplicates,
NOVA-61,Bug,Low,API;Backend,ux-improvement;performance;mvp,Sprint 1 (Nova Beta),Payment Gateway API,Ops_Jim,Chloe_P_Dev,2023-11-24,2023-12-17,Pending,Fix bug related to Bug 61,"Detailed description for Fix bug related to Bug 61. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,,2023-10-28,2023-12-26,,,User_Mia
NOVA-62,Bug,Critical,Frontend;API,critical-path;mvp;performance,Sprint 4 (Nova Beta),Notification Service,Sarah_P,Noah_G_Dev,2023-10-24,2023-11-09,In Progress,Fix bug related to Bug 62,"Detailed description for Fix bug related to Bug 62. This involves several steps and considerations, including integration with other modules. Also, please check the attached design document.",,Team Griffin,,2023-10-22,2023-11-09,,,,
NOVA-63,Bug,High,Frontend,ux-improvement;beta-feature,Sprint 1 (Nova Beta),Notification Service,Ethan_H_Sec,Noah_G_Dev,2023-09-03,2023-09-09,Closed,Fix bug related to Bug 63,"Detailed description for Fix bug related to Bug 63. This involves several steps and considerations, including integration with other modules.",v1.0.3,Team Griffin,59,2023-09-02,2023-09-09,,,,
NOVA-64,Bug,Major,UI-Mobile;Frontend,tech-debt,Sprint 7 (Nova Hotfix),Auth Service,User_Raj,Noah_G_Dev,2023-11-02,2023-11-27,Release,Fix bug related to Bug 64,"Detailed description for Fix bug related to Bug 64. This involves several steps and considerations, including integration with other modules.",v1.0.1,Team Griffin,88,2023-10-17,2023-11-27,,,,
NOVA-65,Bug,High,Database;Backend,performance;ux-improvement;critical-path,Sprint 1 (Nova Beta),Payment Gateway API,Noah_G_Dev,Alex_P_Dev,2023-10-01,2023-10-10,Closed,Fix bug related to Bug 65,"Detailed description for Fix bug related to Bug 65. This involves several steps and considerations, including integration with other modules.",v1.0.0,Team Phoenix,,2023-09-28,2023-10-10,,,,
NOVA-66,Bug,Minor,SecurityLayer;UI-Mobile,ux-improvement;beta-feature,Sprint 1 (Nova Beta),Notification Service,Ben_P_Dev,Noah_G_Dev,2023-09-24,2023-09-29,Review,Fix bug related to Bug 66,"Detailed description for Fix bug related to Bug 66. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-09-09,2023-10-14,,,NOVA-71,sub-task of,
NOVA-66,Bug,Minor,SecurityLayer;UI-Mobile,ux-improvement;beta-feature,Sprint 1 (Nova Beta),Notification Service,Ben_P_Dev,Noah_G_Dev,2023-09-24,2023-09-29,Review,Fix bug related to Bug 66,"Detailed description for Fix bug related to Bug 66. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-09-09,2023-10-14,,,Ethan_H_Sec
NOVA-66,Bug,Minor,SecurityLayer;UI-Mobile,ux-improvement;beta-feature,Sprint 1 (Nova Beta),Notification Service,Ben_P_Dev,Noah_G_Dev,2023-09-24,2023-09-29,Review,Fix bug related to Bug 66,"Detailed description for Fix bug related to Bug 66. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-09-09,2023-10-14,,,Chloe_P_Dev
NOVA-67,Bug,Minor,Backend;Database,ux-improvement;critical-path;tech-debt,Sprint 1 (Nova Beta),Notification Service,David_H,Olivia_G_Dev,2023-09-27,2023-10-18,Blocked,Fix bug related to Bug 67,"Detailed description for Fix bug related to Bug 67. This involves several steps and considerations, including integration with other modules.",,Team Griffin,60,2023-09-12,2023-11-27,,,NOVA-68,cloned by,
NOVA-67,Bug,Minor,Backend;Database,ux-improvement;critical-path;tech-debt,Sprint 1 (Nova Beta),Notification Service,David_H,Olivia_G_Dev,2023-09-27,2023-10-18,Blocked,Fix bug related to Bug 67,"Detailed description for Fix bug related to Bug 67. This involves several steps and considerations, including integration with other modules.",,Team Griffin,60,2023-09-12,2023-11-27,,,User_Raj
NOVA-68,Bug,High,SecurityLayer,ux-improvement;tech-debt;critical-path,Sprint 3 (Nova Beta),Payment Gateway API,User_Raj,Alex_P_Dev,2023-10-23,2023-11-09,Review,Fix bug related to Bug 68,"Detailed description for Fix bug related to Bug 68. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,,2023-09-26,2023-11-09,,,,
NOVA-69,Bug,High,UI-Mobile;API,beta-feature;ux-improvement,Sprint 6 (Nova Hotfix),Auth Service,Alex_P_Dev,Noah_G_Dev,2023-10-18,2023-10-30,Open,Fix bug related to Bug 69,"Detailed description for Fix bug related to Bug 69. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-09-24,2023-11-28,,,NOVA-70,blocks,
NOVA-69,Bug,High,UI-Mobile;API,beta-feature;ux-improvement,Sprint 6 (Nova Hotfix),Auth Service,Alex_P_Dev,Noah_G_Dev,2023-10-18,2023-10-30,Open,Fix bug related to Bug 69,"Detailed description for Fix bug related to Bug 69. This involves several steps and considerations, including integration with other modules.",,Team Griffin,,2023-09-24,2023-11-28,,,User_Pia
NOVA-70,Bug,Minor,Frontend,ux-improvement;mvp,Sprint 2 (Nova Beta),Mobile Wallet Core,Ethan_H_Sec,Liam_G_Dev,2023-11-28,2023-12-06,Closed,Fix bug related to Bug 70,"Detailed description for Fix bug related to Bug 70. This involves several steps and considerations, including integration with other modules.",v1.1.1,Team Griffin,,2023-11-26,2023-12-06,,,,
NOVA-71,Bug,Minor,Frontend,ux-improvement;performance;beta-feature,Sprint 1 (Nova Beta),Payment Gateway API,User_Leo,Olivia_G_Dev,2023-10-07,2023-10-12,Release,Fix bug related to Bug 71,"Detailed description for Fix bug related to Bug 71. This involves several steps and considerations, including integration with other modules.",v1.1.5,Team Griffin,87,2023-09-25,2023-11-28,,,,
NOVA-72,Bug,Minor,API;SecurityLayer,critical-path;beta-feature;performance,Sprint 5 (Nova Beta),Auth Service,User_Kate,Alex_P_Dev,2023-10-02,2023-10-15,Open,Fix bug related to Bug 72,"Detailed description for Fix bug related to Bug 72. This involves several steps and considerations, including integration with other modules.",,Team Phoenix,91,2023-09-10,2023-11-17,,,,
--- END OF FILE JIRA_Issues_Detailed.csv ---


--- START OF FILE CR_Main.csv ---
CR_ID,CR_Title,Linked_Jira_ID,Linked_Confluence_ID,CR_State,CR_Requested_By,CR_Team_Assignment_Group,CR_Assigned_To_User,CR_Impacted_Environment,CR_Impacted_Departments,CR_Type,CR_Category,CR_Risk,CR_Risk_Percentage,CR_Lead_Time_Days,CR_Conflict_Status,CR_Description,CR_Start_Date,CR_End_Date,CR_Implementation_Plan_Summary,CR_Backout_Plan_Summary,CR_Updated_By_User_From_CSV_Example,CR_Created_At_From_CSV_Example
CR001,Emergency Fix for Production Issue - CR001,NOVA-17,CONF-005,New,User_Pia,Team Griffin,Sarah_P,Production,"Marketing;Compliance;Engineering",Emergency,Emergency,High,32,24,No Conflict,"This change request (CR001) is for Emergency Fix for Production Issue - CR001. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,User_Pia,2023-11-14
CR001,Emergency Fix for Production Issue - CR001,NOVA-17,CONF-005,Assess,User_Pia,Team Griffin,Sarah_P,Production,"Marketing;Compliance;Engineering",Emergency,Emergency,High,32,24,No Conflict,"This change request (CR001) is for Emergency Fix for Production Issue - CR001. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,User_Raj,2023-11-15
CR001,Emergency Fix for Production Issue - CR001,NOVA-17,CONF-005,Authorise,User_Pia,Team Griffin,Sarah_P,Production,"Marketing;Compliance;Engineering",Emergency,Emergency,High,32,24,Resolved,"This change request (CR001) is for Emergency Fix for Production Issue - CR001. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2023-11-21,2023-12-02,"Implementation plan for CR001: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR001: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",User_Raj,2023-11-18
CR001,Emergency Fix for Production Issue - CR001,NOVA-17,CONF-005,Scheduled,User_Pia,Team Griffin,Sarah_P,Production,"Marketing;Compliance;Engineering",Emergency,Emergency,High,32,24,No Conflict,"This change request (CR001) is for Emergency Fix for Production Issue - CR001. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2023-11-23,2023-12-07,"Implementation plan for CR001: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR001: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",User_Raj,2023-11-23
CR001,Emergency Fix for Production Issue - CR001,NOVA-17,CONF-005,Implement,User_Pia,Team Griffin,Sarah_P,Production,"Marketing;Compliance;Engineering",Emergency,Emergency,High,32,24,Conflict Detected,"This change request (CR001) is for Emergency Fix for Production Issue - CR001. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2023-12-02,2023-12-03,"Implementation plan for CR001: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR001: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",User_Raj,2023-11-28
CR001,Emergency Fix for Production Issue - CR001,NOVA-17,CONF-005,Closed,User_Pia,Team Griffin,Sarah_P,Production,"Marketing;Compliance;Engineering",Emergency,Emergency,High,32,24,Resolved,"This change request (CR001) is for Emergency Fix for Production Issue - CR001. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2023-12-01,2023-12-06,"Implementation plan for CR001: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR001: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",User_Raj,2023-11-29
CR002,Security CR - CR002,NOVA-3,CONF-019,New,Ops_Jim,Team Hydra,Ops_Jim,Staging,"QA;Product;Compliance",Normal,Security,Medium,16,13,No Conflict,"This change request (CR002) is for Security CR - CR002. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Ops_Jim,2023-09-13
CR003,New Feature CR - CR003,NOVA-7,,New,Alex_P_Dev,Team Phoenix,Alex_P_Dev,Development,"Engineering;Product",Standard,New Feature,Low,,29,No Conflict,"This change request (CR003) is for New Feature CR - CR003. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Alex_P_Dev,2023-12-16
CR003,New Feature CR - CR003,NOVA-7,,Assess,Alex_P_Dev,Team Phoenix,Alex_P_Dev,Development,"Engineering;Product",Standard,New Feature,Low,,29,No Conflict,"This change request (CR003) is for New Feature CR - CR003. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Ben_P_Dev,2023-12-17
CR003,New Feature CR - CR003,NOVA-7,,Authorise,Alex_P_Dev,Team Phoenix,Alex_P_Dev,Development,"Engineering;Product",Standard,New Feature,Low,,29,Resolved,"This change request (CR003) is for New Feature CR - CR003. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2023-12-26,2024-01-02,"Implementation plan for CR003: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR003: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",Ben_P_Dev,2023-12-20
CR004,Deployment of Project Nova Feature Set 4 - CR004,NOVA-4,CONF-022,New,PM_Anna,Team Phoenix,PM_Anna,Production,"Marketing;Product;Operations",Standard,Deployment,Medium,55,20,Resolved,"This change request (CR004) is for Deployment of Project Nova Feature Set 4 - CR004. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,PM_Anna,2023-12-09
CR004,Deployment of Project Nova Feature Set 4 - CR004,NOVA-4,CONF-022,Assess,PM_Anna,Team Phoenix,PM_Anna,Production,"Marketing;Product;Operations",Standard,Deployment,Medium,55,20,Resolved,"This change request (CR004) is for Deployment of Project Nova Feature Set 4 - CR004. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Mark_G,2023-12-10
CR004,Deployment of Project Nova Feature Set 4 - CR004,NOVA-4,CONF-022,Authorise,PM_Anna,Team Phoenix,PM_Anna,Production,"Marketing;Product;Operations",Standard,Deployment,Medium,55,20,No Conflict,"This change request (CR004) is for Deployment of Project Nova Feature Set 4 - CR004. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2023-12-15,2023-12-20,"Implementation plan for CR004: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR004: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",Mark_G,2023-12-11
CR005,Emergency Fix for Production Issue - CR005,NOVA-5,,New,Sarah_P,Team Hydra,David_H,Production,"Engineering;Compliance;QA",Emergency,Emergency,High,53,18,No Conflict,"This change request (CR005) is for Emergency Fix for Production Issue - CR005. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Sarah_P,2023-11-06
CR005,Emergency Fix for Production Issue - CR005,NOVA-5,,Assess,Sarah_P,Team Hydra,David_H,Production,"Engineering;Compliance;QA",Emergency,Emergency,High,53,18,No Conflict,"This change request (CR005) is for Emergency Fix for Production Issue - CR005. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,PM_Anna,2023-11-08
CR005,Emergency Fix for Production Issue - CR005,NOVA-5,,Authorise,Sarah_P,Team Hydra,David_H,Production,"Engineering;Compliance;QA",Emergency,Emergency,High,53,18,No Conflict,"This change request (CR005) is for Emergency Fix for Production Issue - CR005. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2023-11-15,2023-11-21,"Implementation plan for CR005: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR005: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",PM_Anna,2023-11-09
CR006,Deployment of Project Nova Feature Set 6 - CR006,NOVA-2,,New,PM_Anna,Team Griffin,Sarah_P,Staging,"Compliance;QA;Product",Normal,Deployment,Medium,33,29,No Conflict,"This change request (CR006) is for Deployment of Project Nova Feature Set 6 - CR006. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,PM_Anna,2023-09-21
CR006,Deployment of Project Nova Feature Set 6 - CR006,NOVA-2,,Assess,PM_Anna,Team Griffin,Sarah_P,Staging,"Compliance;QA;Product",Normal,Deployment,Medium,33,29,Resolved,"This change request (CR006) is for Deployment of Project Nova Feature Set 6 - CR006. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,User_Pia,2023-09-23
CR006,Deployment of Project Nova Feature Set 6 - CR006,NOVA-2,,Authorise,PM_Anna,Team Griffin,Sarah_P,Staging,"Compliance;QA;Product",Normal,Deployment,Medium,33,29,No Conflict,"This change request (CR006) is for Deployment of Project Nova Feature Set 6 - CR006. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2023-10-02,2023-10-08,"Implementation plan for CR006: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR006: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",User_Pia,2023-09-24
CR007,Emergency Fix for Production Issue - CR007,NOVA-2,,New,Ops_Jim,Team Hydra,Ops_Jim,Production,"Operations;Engineering;Compliance",Emergency,Emergency,High,40,27,Resolved,"This change request (CR007) is for Emergency Fix for Production Issue - CR007. It requires careful planning and execution. This CR, if approved, will proceed as planned. Key stakeholders involved: Product team, Engineering lead.",,,,Pending assessment,Pending assessment,Ops_Jim,2023-10-22
CR008,Maintenance CR - CR008,NOVA-6,CONF-013,New,David_H,Team Phoenix,PM_Anna,Development,"Product;Engineering;Marketing",Emergency,Maintenance,Low,84,15,Resolved,"This change request (CR008) is for Maintenance CR - CR008. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,David_H,2023-12-29
CR009,Emergency Fix for Production Issue - CR009,NOVA-2,,New,User_Pia,Team Hydra,Ethan_H_Sec,Production,"Marketing;Compliance;Security",Emergency,Emergency,High,50,22,No Conflict,"This change request (CR009) is for Emergency Fix for Production Issue - CR009. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,User_Pia,2023-10-06
CR010,Communication CR - CR010,,,New,Marketer_Sue,Marketing,Marketer_Sue,N/A,"Product;Marketing",Normal,Communication,Low,,14,No Conflict,"This change request (CR010) is for Communication CR - CR010. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Marketer_Sue,2023-10-07
CR011,Deployment of Project Nova Feature Set 11 - CR011,NOVA-4,,New,Ops_Jim,Team Hydra,David_H,Production,"Engineering;QA;Security",Standard,Deployment,High,,17,Conflict Detected,"This change request (CR011) is for Deployment of Project Nova Feature Set 11 - CR011. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Ops_Jim,2023-12-16
CR012,Audit CR - CR012,NOVA-3,CONF-016,New,QA_Emma,Team Hydra,David_H,N/A,"Compliance;Security;QA",Normal,Audit,Medium,91,22,No Conflict,"This change request (CR012) is for Audit CR - CR012. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,QA_Emma,2023-10-12
CR012,Audit CR - CR012,NOVA-3,CONF-016,Assess,QA_Emma,Team Hydra,David_H,N/A,"Compliance;Security;QA",Normal,Audit,Medium,91,22,No Conflict,"This change request (CR012) is for Audit CR - CR012. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Marketer_Sue,2023-10-13
CR012,Audit CR - CR012,NOVA-3,CONF-016,Authorise,QA_Emma,Team Hydra,David_H,N/A,"Compliance;Security;QA",Normal,Audit,Medium,91,22,Resolved,"This change request (CR012) is for Audit CR - CR012. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2023-10-20,2023-11-03,"Implementation plan for CR012: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR012: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",Marketer_Sue,2023-10-16
CR013,Deployment of Project Nova Feature Set 13 - CR013,NOVA-4,,New,David_H,Team Phoenix,PM_Anna,Staging,"QA;Product;Operations",Emergency,Deployment,Medium,32,28,No Conflict,"This change request (CR013) is for Deployment of Project Nova Feature Set 13 - CR013. It requires careful planning and execution. This CR, if approved, will proceed as planned. Key stakeholders involved: Product team, Engineering lead.",,,,Pending assessment,Pending assessment,David_H,2023-11-01
CR014,Enhancement CR - CR014,NOVA-5,,New,User_Mia,Team Griffin,Noah_G_Dev,Development,"Product;Engineering",Standard,Enhancement,Low,18,28,Resolved,"This change request (CR014) is for Enhancement CR - CR014. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,User_Mia,2023-12-10
CR015,BugFix CR - CR015,NOVA-12,CONF-010,New,Chloe_P_Dev,Team Hydra,Ops_Jim,Development,"QA;Product;Engineering",Normal,BugFix,Medium,,26,No Conflict,"This change request (CR015) is for BugFix CR - CR015. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Chloe_P_Dev,2023-12-23
CR015,BugFix CR - CR015,NOVA-12,CONF-010,Assess,Chloe_P_Dev,Team Hydra,Ops_Jim,Development,"QA;Product;Engineering",Normal,BugFix,Medium,,26,No Conflict,"This change request (CR015) is for BugFix CR - CR015. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Ops_Jim,2023-12-24
CR015,BugFix CR - CR015,NOVA-12,CONF-010,Authorise,Chloe_P_Dev,Team Hydra,Ops_Jim,Development,"QA;Product;Engineering",Normal,BugFix,Medium,,26,No Conflict,"This change request (CR015) is for BugFix CR - CR015. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2024-01-02,2024-01-07,"Implementation plan for CR015: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR015: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",Ops_Jim,2023-12-27
CR016,Infrastructure CR - CR016,NOVA-24,,New,Alex_P_Dev,Team Phoenix,Chloe_P_Dev,Staging,"Engineering;Security;Operations",Emergency,Infrastructure,High,97,29,Conflict Detected,"This change request (CR016) is for Infrastructure CR - CR016. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Alex_P_Dev,2023-12-27
CR017,Enhancement CR - CR017,NOVA-1,,New,Mark_G,Team Phoenix,Alex_P_Dev,Development,"Operations;Product;Engineering",Standard,Enhancement,Medium,60,1,No Conflict,"This change request (CR017) is for Enhancement CR - CR017. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Mark_G,2023-12-26
CR017,Enhancement CR - CR017,NOVA-1,,Assess,Mark_G,Team Phoenix,Alex_P_Dev,Development,"Operations;Product;Engineering",Standard,Enhancement,Medium,60,1,Resolved,"This change request (CR017) is for Enhancement CR - CR017. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,User_Kate,2023-12-27
CR017,Enhancement CR - CR017,NOVA-1,,Authorise,Mark_G,Team Phoenix,Alex_P_Dev,Development,"Operations;Product;Engineering",Standard,Enhancement,Medium,60,1,Resolved,"This change request (CR017) is for Enhancement CR - CR017. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2024-01-04,2024-01-11,"Implementation plan for CR017: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR017: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",User_Kate,2023-12-28
CR018,New Feature CR - CR018,NOVA-20,CONF-001,New,User_Raj,Team Phoenix,Ben_P_Dev,Development,"QA;Product;Engineering",Standard,New Feature,Low,78,22,Resolved,"This change request (CR018) is for New Feature CR - CR018. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,User_Raj,2023-10-07
CR019,Maintenance CR - CR019,,CONF-007,New,Ethan_H_Sec,Team Hydra,Ethan_H_Sec,Staging,"Security;Engineering;Operations",Normal,Maintenance,Medium,69,14,No Conflict,"This change request (CR019) is for Maintenance CR - CR019. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Ethan_H_Sec,2023-10-11
CR020,Deployment of Project Nova Feature Set 20 - CR020,NOVA-28,,New,Marketer_Sue,Marketing,Marketer_Sue,Production,"Compliance;Marketing;Product",Normal,Deployment,Low,69,12,No Conflict,"This change request (CR020) is for Deployment of Project Nova Feature Set 20 - CR020. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Marketer_Sue,2023-12-21
CR021,Audit CR - CR021,NOVA-3,,New,User_Leo,Team Hydra,Ethan_H_Sec,N/A,"Operations;Security;QA",Normal,Audit,Medium,19,8,No Conflict,"This change request (CR021) is for Audit CR - CR021. It requires careful planning and execution. This CR, if approved, will proceed as planned. Key stakeholders involved: Product team, Engineering lead.",,,,Pending assessment,Pending assessment,User_Leo,2023-09-19
CR021,Audit CR - CR021,NOVA-3,,Assess,User_Leo,Team Hydra,Ethan_H_Sec,N/A,"Operations;Security;QA",Normal,Audit,Medium,19,8,No Conflict,"This change request (CR021) is for Audit CR - CR021. It requires careful planning and execution. This CR, if approved, will proceed as planned. Key stakeholders involved: Product team, Engineering lead.",,,,Pending assessment,Pending assessment,Noah_G_Dev,2023-09-20
CR021,Audit CR - CR021,NOVA-3,,Authorise,User_Leo,Team Hydra,Ethan_H_Sec,N/A,"Operations;Security;QA",Normal,Audit,Medium,19,8,Resolved,"This change request (CR021) is for Audit CR - CR021. It requires careful planning and execution. This CR, if approved, will proceed as planned. Key stakeholders involved: Product team, Engineering lead.",2023-09-23,2023-10-02,"Implementation plan for CR021: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR021: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",Noah_G_Dev,2023-09-21
CR022,BugFix CR - CR022,NOVA-30,,New,Ben_P_Dev,Team Griffin,Mark_G,Production,"QA;Product;Engineering",Standard,BugFix,Medium,51,29,Resolved,"This change request (CR022) is for BugFix CR - CR022. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Ben_P_Dev,2023-11-26
CR022,BugFix CR - CR022,NOVA-30,,Assess,Ben_P_Dev,Team Griffin,Mark_G,Production,"QA;Product;Engineering",Standard,BugFix,Medium,51,29,No Conflict,"This change request (CR022) is for BugFix CR - CR022. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Ops_Jim,2023-11-27
CR022,BugFix CR - CR022,NOVA-30,,Authorise,Ben_P_Dev,Team Griffin,Mark_G,Production,"QA;Product;Engineering",Standard,BugFix,Medium,51,29,Conflict Detected,"This change request (CR022) is for BugFix CR - CR022. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2023-12-05,2023-12-14,"Implementation plan for CR022: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR022: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",Ops_Jim,2023-11-29
CR023,Infrastructure CR - CR023,,CONF-003,New,Ethan_H_Sec,Team Hydra,Ethan_H_Sec,Staging,"QA;Security;Operations",Normal,Infrastructure,High,,1,No Conflict,"This change request (CR023) is for Infrastructure CR - CR023. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,Ethan_H_Sec,2023-09-24
CR023,Infrastructure CR - CR023,,CONF-003,Assess,Ethan_H_Sec,Team Hydra,Ethan_H_Sec,Staging,"QA;Security;Operations",Normal,Infrastructure,High,,1,Conflict Detected,"This change request (CR023) is for Infrastructure CR - CR023. It requires careful planning and execution. This CR, if approved, will proceed as planned.",,,,Pending assessment,Pending assessment,QA_Emma,2023-09-25
CR023,Infrastructure CR - CR023,,CONF-003,Authorise,Ethan_H_Sec,Team Hydra,Ethan_H_Sec,Staging,"QA;Security;Operations",Normal,Infrastructure,High,,1,No Conflict,"This change request (CR023) is for Infrastructure CR - CR023. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2023-10-01,2023-10-10,"Implementation plan for CR023: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR023: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",QA_Emma,2023-09-28
CR023,Infrastructure CR - CR023,,CONF-003,Scheduled,Ethan_H_Sec,Team Hydra,Ethan_H_Sec,Staging,"QA;Security;Operations",Normal,Infrastructure,High,,1,No Conflict,"This change request (CR023) is for Infrastructure CR - CR023. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2023-10-01,2023-10-08,"Implementation plan for CR023: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR023: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",QA_Emma,2023-10-01
CR023,Infrastructure CR - CR023,,CONF-003,Implement,Ethan_H_Sec,Team Hydra,Ethan_H_Sec,Staging,"QA;Security;Operations",Normal,Infrastructure,High,,1,Resolved,"This change request (CR023) is for Infrastructure CR - CR023. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2023-10-02,2023-10-09,"Implementation plan for CR023: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR023: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",QA_Emma,2023-10-01
CR023,Infrastructure CR - CR023,,CONF-003,Closed,Ethan_H_Sec,Team Hydra,Ethan_H_Sec,Staging,"QA;Security;Operations",Normal,Infrastructure,High,,1,No Conflict,"This change request (CR023) is for Infrastructure CR - CR023. It requires careful planning and execution. This CR, if approved, will proceed as planned.",2023-10-02,2023-10-04,"Implementation plan for CR023: 1. Prepare environment. 2. Deploy changes. 3. Verify.","Backout plan for CR023: 1. Revert deployment. 2. Restore previous state. 3. Notify stakeholders.",QA_Emma,2023-10-02
--- END OF FILE CR_Main.csv ---


--- START OF FILE Confluence_Pages_Detailed.csv ---
Confluence_ID,Confluence_Title,Confluence_Owner_Member,Confluence_Last_Edited_By,Confluence_Space,Confluence_Team_Association,Confluence_Content_Summary,Confluence_Linked_Jira_ID,Confluence_Linked_CR_ID,Confluence_Parent_Page_ID,Confluence_Created_Date,Confluence_Last_Modified_Date
CONF-001,Project Nova Overview (CONF-001),Ops_Jim,Chloe_P_Dev,Project Nova,Cross-functional,"This document (CONF-001: Project Nova Overview (CONF-001)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.",NOVA-24;NOVA-4;NOVA-31,CR018,2023-11-02,2023-12-23
CONF-002,Marketing Campaign Plan - Wallet Launch (CONF-002),Noah_G_Dev,QA_Emma,Marketing Hub,Marketing,"This document (CONF-002: Marketing Campaign Plan - Wallet Launch (CONF-002)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context. This page is currently under review, feedback is welcome.",NOVA-48;NOVA-26,CR004;CR020,,2023-09-09,2023-12-11
CONF-003,Security Review Findings - Q4 2023 (CONF-003),User_Pia,Liam_G_Dev,QA Central,Team Hydra,"This document (CONF-003: Security Review Findings - Q4 2023 (CONF-003)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.",NOVA-36;NOVA-14;NOVA-5,CR023,2023-10-17,2023-10-24
CONF-004,Sprint Retrospective Notes - Sprint 4 (CONF-004),Ops_Jim,Ops_Jim,Project Nova,Team Hydra,"This document (CONF-004: Sprint Retrospective Notes - Sprint 4 (CONF-004)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context. This page is currently under review, feedback is welcome.",NOVA-24;NOVA-45;NOVA-31,CR013,2023-10-22,2024-01-12
CONF-005,Deployment Checklist - Beta Launch (CONF-005),Alex_P_Dev,User_Leo,Release Management,Team Hydra,"This document (CONF-005: Deployment Checklist - Beta Launch (CONF-005)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.",NOVA-15;NOVA-11;NOVA-52,CR001,2023-11-24,2023-12-20
CONF-006,Mobile Wallet Beta - Requirements (CONF-006),Alex_P_Dev,Mark_G,Project Nova,Team Phoenix,"This document (CONF-006: Mobile Wallet Beta - Requirements (CONF-006)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.",NOVA-51;NOVA-62,,CONF-001,2023-09-28,2023-11-14
CONF-007,Marketing Campaign Plan - Wallet Launch (CONF-007),User_Raj,Ops_Jim,Marketing Hub,Marketing,"This document (CONF-007: Marketing Campaign Plan - Wallet Launch (CONF-007)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.",NOVA-44;NOVA-37,CR019,CONF-002,2023-11-26,2023-12-15
CONF-008,Backend API Specification v1 (CONF-008),David_H,Ops_Jim,Engineering Docs,Team Hydra,"This document (CONF-008: Backend API Specification v1 (CONF-008)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.",NOVA-35;NOVA-41;NOVA-66,CR017;CR006,,2023-10-21,2023-12-28
CONF-009,Competitor Analysis - Mobile Wallets (CONF-009),User_Kate,User_Raj,Marketing Hub,Marketing,"This document (CONF-009: Competitor Analysis - Mobile Wallets (CONF-009)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.",NOVA-14;NOVA-47;NOVA-11,,CONF-002,2023-11-23,2023-12-05
CONF-010,Security Review Findings - Q4 2023 (CONF-010),User_Raj,User_Leo,QA Central,Team Hydra,"This document (CONF-010: Security Review Findings - Q4 2023 (CONF-010)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.",NOVA-68;NOVA-47;NOVA-6,CR015,CONF-003,2023-09-02,2023-12-24
CONF-011,Hotfix NOVA-40 - RCA (CONF-011),Chloe_P_Dev,Alex_P_Dev,Project Nova,Cross-functional,"This document (CONF-011: Hotfix NOVA-40 - RCA (CONF-011)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.",NOVA-40;NOVA-50;NOVA-66,CR007,CONF-001,2023-09-02,2023-11-02
CONF-012,User Authentication Flow Design (CONF-012),Ethan_H_Sec,Ops_Jim,Engineering Docs,Team Phoenix,"This document (CONF-012: User Authentication Flow Design (CONF-012)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.",NOVA-14;NOVA-1;NOVA-49,CR011,2023-10-03,2023-11-06
CONF-013,QA Test Plan - Sprint 3 (CONF-013),User_Leo,Alex_P_Dev,QA Central,Team Hydra,"This document (CONF-013: QA Test Plan - Sprint 3 (CONF-013)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.",NOVA-14;NOVA-51;NOVA-66,CR008;CR021,CONF-010,2023-12-02,2023-12-29
CONF-014,Sprint Retrospective Notes - Sprint 2 (CONF-014),Mark_G,User_Mia,Project Nova,Team Griffin,"This document (CONF-014: Sprint Retrospective Notes - Sprint 2 (CONF-014)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.",NOVA-24;NOVA-38;NOVA-58,,CONF-004,2023-10-28,2023-12-12
CONF-015,Sprint Retrospective Notes - Sprint 7 (CONF-015),Liam_G_Dev,User_Raj,Project Nova,Team Phoenix,"This document (CONF-015: Sprint Retrospective Notes - Sprint 7 (CONF-015)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context. This page is currently under review, feedback is welcome.",NOVA-29;NOVA-69;NOVA-33,CR009,,2023-12-06,2023-12-20
CONF-016,User Authentication Flow Design (CONF-016),Ben_P_Dev,QA_Emma,Engineering Docs,Team Phoenix,"This document (CONF-016: User Authentication Flow Design (CONF-016)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context. This page is currently under review, feedback is welcome.",NOVA-48;NOVA-21;NOVA-17,CR012,CONF-012,2023-11-29,2023-12-14
CONF-017,Project Nova Overview (CONF-017),User_Leo,Ben_P_Dev,Project Nova,Team Phoenix,"This document (CONF-017: Project Nova Overview (CONF-017)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.",NOVA-23;NOVA-63;NOVA-61,,CONF-001,2023-11-02,2023-12-13
CONF-018,Release Notes - v1.0 Beta (CONF-018),PM_Anna,User_Raj,Release Management,Cross-functional,"This document (CONF-018: Release Notes - v1.0 Beta (CONF-018)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.",NOVA-50;NOVA-31;NOVA-2,,CONF-005,2023-10-28,2023-12-03
CONF-019,Deployment Checklist - Beta Launch (CONF-019),User_Raj,Ops_Jim,Release Management,Team Hydra,"This document (CONF-019: Deployment Checklist - Beta Launch (CONF-019)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.",NOVA-69,CR002;CR007,,2023-11-24,2023-12-14
CONF-020,Security Review Findings - Q4 2023 (CONF-020),Ethan_H_Sec,User_Raj,QA Central,Cross-functional,"This document (CONF-020: Security Review Findings - Q4 2023 (CONF-020)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to
linked items for more context.",NOVA-2;NOVA-42;NOVA-66,,CONF-003,2023-11-14,2023-12-05
CONF-021,Competitor Analysis - Mobile Wallets (CONF-021),Marketer_Sue,User_Raj,Marketing Hub,Marketing,"This document (CONF-021: Competitor Analysis - Mobile Wallets (CONF-021)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context. This page is currently under review, feedback is welcome.",NOVA-55;NOVA-46;NOVA-69,CR010,CONF-009,2023-11-29,2023-12-21
CONF-022,QA Test Plan - Sprint 6 (CONF-022),Ben_P_Dev,Ops_Jim,QA Central,Team Hydra,"This document (CONF-022: QA Test Plan - Sprint 6 (CONF-022)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context. This page is currently under review, feedback is welcome.",NOVA-17;NOVA-44;NOVA-27,CR004,CONF-013,2023-10-29,2023-11-23
--- END OF FILE Confluence_Pages_Detailed.csv ---


--- START OF FILE JIRA_Activities.csv ---
Activity_ID,JIRA_ID,Activity_Comment,Activity_Timestamp,Activity_User
ACT-001,NOVA-20,"Status changed to Development.",2023-09-23 12:38,Ops_Jim
ACT-002,NOVA-30,"Status changed to Review.",2023-10-14 17:18,User_Kate
ACT-003,NOVA-51,"Status changed to Pending.",2023-10-05 15:46,User_Omar
ACT-004,NOVA-13,"Deployment to Staging complete.",2023-10-05 11:53,PM_Anna
ACT-005,NOVA-32,"New attachment: design_mockup_v2.png",2023-10-15 11:52,User_Kate
ACT-006,NOVA-38,"Priority set to Minor.",2023-09-13 17:43,Ethan_H_Sec
ACT-007,NOVA-13,"Priority set to High.",2023-10-10 13:58,Ben_P_Dev
ACT-008,NOVA-46,"Reopened due to issue persistence.",2023-10-15 13:02,User_Raj
ACT-009,NOVA-45,"Effort estimated at 2 points.",2023-09-12 10:54,Ben_P_Dev
ACT-010,NOVA-38,"Comment: Blocked by upstream dependency.",2023-09-24 11:37,User_Omar
ACT-011,NOVA-37,"Assigned to PM_Anna.",2023-10-15 12:17,QA_Emma
ACT-012,NOVA-61,"Status changed to Release.",2023-11-01 17:42,User_Kate
ACT-013,NOVA-57,"Effort estimated at 1 points.",2023-09-19 10:48,Marketer_Sue
ACT-014,NOVA-22,"Fix verified and closed.",2023-10-07 11:18,Ethan_H_Sec
ACT-015,NOVA-48,"Assigned to User_Pia.",2023-10-18 13:31,Sarah_P
ACT-016,NOVA-38,"Ready for QA.",2023-09-17 17:24,Sarah_P
ACT-017,NOVA-42,"Fix verified and closed.",2023-10-11 14:53,User_Raj
ACT-018,NOVA-46,"Deployment to Staging complete.",2023-10-08 16:01,David_H
--- END OF FILE JIRA_Activities.csv ---


--- START OF FILE CR_CTasks.csv ---
CTASK_ID,CR_ID,CTASK_Assigned_To_User,CTASK_Start_Time,CTASK_End_Time,CTASK_Description
CTASK001,CR005,David_H,2023-11-15 12:00,2023-11-15 15:00,Communicate CR implementation to stakeholders.
CTASK002,CR001,Sarah_P,2023-11-23 11:15,2023-11-23 14:15,Document CR closure.
CTASK003,CR023,Ethan_H_Sec,2023-10-02 14:00,2023-10-02 22:00,Monitor system post-CR implementation.
CTASK004,CR001,Sarah_P,2023-12-02 09:15,2023-12-02 17:15,Schedule CR for production deployment.
CTASK005,CR015,Ops_Jim,2024-01-03 14:15,2024-01-03 22:15,Rollback CR due to unforeseen issues.
CTASK006,CR003,Alex_P_Dev,2023-12-26 15:45,2023-12-26 19:45,Execute UAT for CR.
CTASK007,CR001,Sarah_P,2023-12-01 10:45,2023-12-01 14:45,Develop and unit test changes for CR.
CTASK008,CR001,Sarah_P,2023-12-02 12:45,2023-12-02 15:45,Develop and unit test changes for CR.
CTASK009,CR021,Ethan_H_Sec,2023-09-23 14:00,2023-09-23 19:00,Perform technical assessment for CR.
CTASK010,CR022,Mark_G,2023-12-08 10:30,2023-12-08 12:30,Monitor system post-CR implementation.
CTASK011,CR006,Sarah_P,2023-10-03 16:30,2023-10-03 22:30,Deploy CR to Staging environment.
CTASK012,CR006,Sarah_P,2023-10-04 12:30,2023-10-04 14:30,Perform technical assessment for CR.
--- END OF FILE CR_CTasks.csv ---
```
