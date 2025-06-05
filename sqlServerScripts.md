Okay, this is a classic data modeling and ETL (Extract, Transform, Load) task. The CSV data you've provided has some complexities, especially `JIRA_Issues_Detailed.csv` with its duplicated rows for links and watchers.

Here's how we can approach creating SQL Server `CREATE TABLE` scripts and `INSERT` scripts.

**Important Considerations for SQL Table Design from CSVs:**

1.  **Primary Keys:** Each table needs a primary key to uniquely identify rows.
2.  **Foreign Keys:** To maintain relationships between tables (e.g., `CR_ID` in `CR_CTasks` linking to `CR_Main`).
3.  **Data Types:** Choose appropriate SQL data types (e.g., `VARCHAR`, `INT`, `DECIMAL`, `DATE`, `DATETIME`).
4.  **Normalization (for `JIRA_Issues_Detailed.csv`):** The `JIRA_Issues_Detailed.csv` is denormalized because JIRA issue details are repeated for each link or watcher. For a relational database, it's generally better to normalize this:
    *   One table for core JIRA issue details (`JiraIssues`).
    *   A separate table for issue links (`JiraIssueLinks`).
    *   A separate table for watchers (`JiraIssueWatchers`).
    This avoids data redundancy and update anomalies. I will design the tables this way.
5.  **Semicolon-Delimited Fields:** Fields like `JIRA_Components`, `JIRA_Labels`, `Confluence_Linked_Jira_ID` are semicolon-delimited. In a relational database, these are often handled by:
    *   Storing them as `VARCHAR(MAX)` if you only need to store and retrieve the string.
    *   Creating separate link tables if you need to query individual items within the list (e.g., a `JiraIssueComponents` table). For simplicity in this `CREATE TABLE` script, I'll use `VARCHAR(MAX)` for these, but in a real-world scenario, further normalization might be needed based on query requirements.
6.  **Nullable Fields:** Determine which columns can accept `NULL` values.
7.  **Handling Duplicates in `CR_Main.csv`:** The `CR_Main.csv` has multiple rows for the same `CR_ID` representing status updates. We need a way to uniquely identify each *status record* while still linking it to the core Change Request. We can add an auto-incrementing primary key to this table.

---

**SQL `CREATE TABLE` Scripts**

```sql
-- =======================================================================
-- Table: Users (Implicit from data, good for referential integrity)
-- =======================================================================
-- Although not explicitly a CSV, users are mentioned.
-- Creating a Users table is good practice if you want to enforce
-- foreign key constraints for user fields.
-- For this exercise, I'll make user fields VARCHARs in other tables,
-- but in a real system, you'd link to a Users table.
/*
CREATE TABLE Users (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    UserName VARCHAR(100) UNIQUE NOT NULL,
    Team VARCHAR(50) -- e.g., Team Phoenix, Team Griffin, Team Hydra, Marketing
    -- Add other user details if needed
);
GO
*/

-- =======================================================================
-- Table: JiraIssues (Normalized core JIRA issue details)
-- =======================================================================
CREATE TABLE JiraIssues (
    JiraIssueInternalID INT PRIMARY KEY IDENTITY(1,1), -- Surrogate key for the table
    JIRA_ID VARCHAR(50) NOT NULL UNIQUE, -- The business key like NOVA-1
    JIRA_Type VARCHAR(50),
    JIRA_Priority VARCHAR(50),
    JIRA_Components VARCHAR(MAX), -- Storing as text; consider normalization for querying
    JIRA_Labels VARCHAR(MAX),     -- Storing as text; consider normalization for querying
    JIRA_Sprint VARCHAR(100),
    JIRA_App_Name VARCHAR(100),
    JIRA_Reporter VARCHAR(100),   -- Consider FK to a Users table
    JIRA_Assignee VARCHAR(100),   -- Consider FK to a Users table
    JIRA_Start_Date DATE,
    JIRA_End_Date DATE,
    JIRA_Status VARCHAR(50),
    JIRA_Title VARCHAR(255),
    JIRA_Description VARCHAR(MAX),
    JIRA_Release_Fix_Version VARCHAR(100),
    JIRA_Team VARCHAR(50),
    JIRA_Confidence INT,
    JIRA_Created_Date DATE,
    JIRA_Updated_Date DATE,
    JIRA_Effort_Story_Points DECIMAL(5,1), -- e.g., 0.5, 1, 2, 3, 5, 8
    CR_ID_Link VARCHAR(50) -- Link to CR_Main.CR_ID (will be string for now)
);
GO

-- =======================================================================
-- Table: JiraIssueLinks (Normalized JIRA issue links)
-- =======================================================================
CREATE TABLE JiraIssueLinks (
    LinkID INT PRIMARY KEY IDENTITY(1,1),
    Source_JIRA_ID VARCHAR(50) NOT NULL, -- FK to JiraIssues.JIRA_ID (or JiraIssueInternalID)
    Target_JIRA_ID VARCHAR(50) NOT NULL, -- FK to JiraIssues.JIRA_ID (or JiraIssueInternalID)
    JIRA_Link_Type VARCHAR(50),
    CONSTRAINT FK_JiraIssueLinks_Source FOREIGN KEY (Source_JIRA_ID) REFERENCES JiraIssues(JIRA_ID),
    CONSTRAINT FK_JiraIssueLinks_Target FOREIGN KEY (Target_JIRA_ID) REFERENCES JiraIssues(JIRA_ID)
);
GO

-- =======================================================================
-- Table: JiraIssueWatchers (Normalized JIRA issue watchers)
-- =======================================================================
CREATE TABLE JiraIssueWatchers (
    WatcherID INT PRIMARY KEY IDENTITY(1,1),
    JIRA_ID VARCHAR(50) NOT NULL, -- FK to JiraIssues.JIRA_ID (or JiraIssueInternalID)
    JIRA_Watcher_User VARCHAR(100) NOT NULL, -- Consider FK to a Users table
    CONSTRAINT FK_JiraIssueWatchers_JiraIssue FOREIGN KEY (JIRA_ID) REFERENCES JiraIssues(JIRA_ID)
    -- Optional: Add a unique constraint on (JIRA_ID, JIRA_Watcher_User) if a user can only watch an issue once
    -- CONSTRAINT UQ_JiraIssueWatchers UNIQUE (JIRA_ID, JIRA_Watcher_User)
);
GO

-- =======================================================================
-- Table: ChangeRequests (CR_Main.csv)
-- CR_ID can have multiple status records, so we need a unique ID for each record.
-- =======================================================================
CREATE TABLE ChangeRequests (
    ChangeRequestRecordID INT PRIMARY KEY IDENTITY(1,1), -- Surrogate key for each status record
    CR_ID VARCHAR(50) NOT NULL, -- Business key for the Change Request
    CR_Title VARCHAR(255),
    Linked_Jira_ID VARCHAR(50), -- Consider FK to JiraIssues.JIRA_ID
    Linked_Confluence_ID VARCHAR(50), -- Consider FK to ConfluencePages.Confluence_ID
    CR_State VARCHAR(50),
    CR_Requested_By VARCHAR(100), -- Consider FK to a Users table
    CR_Team_Assignment_Group VARCHAR(50),
    CR_Assigned_To_User VARCHAR(100), -- Consider FK to a Users table
    CR_Impacted_Environment VARCHAR(50),
    CR_Impacted_Departments VARCHAR(MAX), -- Storing as text
    CR_Type VARCHAR(50),
    CR_Category VARCHAR(50),
    CR_Risk VARCHAR(50),
    CR_Risk_Percentage INT,
    CR_Lead_Time_Days INT,
    CR_Conflict_Status VARCHAR(50),
    CR_Description VARCHAR(MAX),
    CR_Start_Date DATE,
    CR_End_Date DATE,
    CR_Implementation_Plan_Summary VARCHAR(MAX),
    CR_Backout_Plan_Summary VARCHAR(MAX),
    CR_Updated_By_User VARCHAR(100), -- Renamed from CSV example for clarity
    CR_Record_Created_At DATE -- Renamed from CSV example for clarity (date of this status row)
    -- Optional: Add an index on CR_ID for faster lookups of all statuses for a CR
    -- CREATE INDEX IX_ChangeRequests_CR_ID ON ChangeRequests(CR_ID);
);
GO

-- =======================================================================
-- Table: ConfluencePages (Confluence_Pages_Detailed.csv)
-- =======================================================================
CREATE TABLE ConfluencePages (
    ConfluencePageInternalID INT PRIMARY KEY IDENTITY(1,1), -- Surrogate key
    Confluence_ID VARCHAR(50) NOT NULL UNIQUE, -- Business key
    Confluence_Title VARCHAR(255),
    Confluence_Owner_Member VARCHAR(100), -- Consider FK to Users table
    Confluence_Last_Edited_By VARCHAR(100), -- Consider FK to Users table
    Confluence_Space VARCHAR(100),
    Confluence_Team_Association VARCHAR(50),
    Confluence_Content_Summary VARCHAR(MAX),
    Confluence_Linked_Jira_ID VARCHAR(MAX), -- Storing as text; consider normalization
    Confluence_Linked_CR_ID VARCHAR(MAX),   -- Storing as text; consider normalization
    Confluence_Parent_Page_ID VARCHAR(50), -- Self-referencing FK (or link to Confluence_ID)
    Confluence_Created_Date DATE,
    Confluence_Last_Modified_Date DATE
    -- CONSTRAINT FK_ConfluencePages_ParentPage FOREIGN KEY (Confluence_Parent_Page_ID) REFERENCES ConfluencePages(Confluence_ID) -- if Confluence_ID is unique and used for FK
);
GO
-- If Confluence_Parent_Page_ID refers to ConfluencePageInternalID (surrogate key), the FK would be different.
-- For now, keeping it as VARCHAR referring to Confluence_ID based on CSV structure.

-- =======================================================================
-- Table: JiraActivities (JIRA_Activities.csv)
-- =======================================================================
CREATE TABLE JiraActivities (
    Activity_ID_PK INT PRIMARY KEY IDENTITY(1,1), -- Surrogate key, as Activity_ID might not be unique across systems
    Activity_ID_Source VARCHAR(50), -- The Activity_ID from the CSV
    JIRA_ID VARCHAR(50) NOT NULL, -- FK to JiraIssues.JIRA_ID
    Activity_Comment VARCHAR(MAX),
    Activity_Timestamp DATETIME, -- Changed to DATETIME to store time
    Activity_User VARCHAR(100), -- Consider FK to Users table
    CONSTRAINT FK_JiraActivities_JiraIssue FOREIGN KEY (JIRA_ID) REFERENCES JiraIssues(JIRA_ID)
);
GO

-- =======================================================================
-- Table: CR_CTasks (CR_CTasks.csv)
-- =======================================================================
CREATE TABLE CR_CTasks (
    CTASK_ID_PK INT PRIMARY KEY IDENTITY(1,1), -- Surrogate key
    CTASK_ID_Source VARCHAR(50), -- The CTASK_ID from the CSV
    CR_ID VARCHAR(50) NOT NULL, -- FK to ChangeRequests.CR_ID (identifies the CR, not specific status record)
    CTASK_Assigned_To_User VARCHAR(100), -- Consider FK to Users table
    CTASK_Start_Time DATETIME,
    CTASK_End_Time DATETIME,
    CTASK_Description VARCHAR(MAX)
    -- We can't directly FK to ChangeRequests.CR_ID if CR_ID is not unique there.
    -- A better approach might be to have a separate CR_Master table if CR_ID in ChangeRequests is just for grouping.
    -- For now, assuming CR_ID is the intended link for CTasks.
    -- If you create a CR_Master table with unique CR_ID, then FK to that.
);
GO
-- To properly link CR_CTasks.CR_ID to a unique Change Request, you would ideally have:
-- 1. A `ChangeRequestMaster` table: `CR_ID (PK), CR_Title, ... (core, non-status specific details)`
-- 2. `ChangeRequestStatusLog` table (what we called `ChangeRequests`): `ChangeRequestStatusID (PK), CR_ID (FK to Master), CR_State, CR_Record_Created_At ...`
-- Then `CR_CTasks.CR_ID` would FK to `ChangeRequestMaster.CR_ID`.
-- For simplicity based on the CSV, I've kept `ChangeRequests` as is.
```

---

**SQL `INSERT` Scripts**

Generating `INSERT` scripts from CSVs manually can be tedious and error-prone, especially with quoting and data type conversions. **For larger datasets, you'd typically use SQL Server Import and Export Wizard, SSIS, `BULK INSERT`, or scripting languages (like Python with `pyodbc` or `pandas`) to load the data.**

However, I'll provide a few sample `INSERT` statements based on the data you provided to illustrate the structure.

**Important Notes for these `INSERT` Scripts:**

*   **Dates:** SQL Server expects dates in 'YYYY-MM-DD' format. Ensure your CSV dates are compatible or use `CONVERT` if needed.
*   **NULLs:** If a CSV field is empty and the corresponding SQL column is nullable, use `NULL`. If it's a numeric or date field and empty, you MUST insert `NULL` (not an empty string).
*   **Quotes:** Single quotes in your data (like in descriptions) need to be escaped by doubling them (e.g., `O'Malley` becomes `O''Malley`).
*   **Order of Inserts:** You need to insert into tables with primary keys before tables with foreign keys referencing them (e.g., `JiraIssues` before `JiraIssueLinks`).
*   **Normalization of JIRA Data:** The inserts for JIRA will be split. First, the unique JIRA issues, then their links, then their watchers.

**Sample `INSERT` Scripts (Illustrative - adapt for full data):**

```sql
-- =======================================================================
-- Inserts for JiraIssues (Core Details - ONE row per unique JIRA_ID)
-- This requires processing your JIRA_Issues_Detailed.csv to extract unique issues first.
-- =======================================================================
-- For NOVA-1 (only one entry needed in JiraIssues for its core details)
INSERT INTO JiraIssues (
    JIRA_ID, JIRA_Type, JIRA_Priority, JIRA_Components, JIRA_Labels, JIRA_Sprint, JIRA_App_Name,
    JIRA_Reporter, JIRA_Assignee, JIRA_Start_Date, JIRA_End_Date, JIRA_Status, JIRA_Title, JIRA_Description,
    JIRA_Release_Fix_Version, JIRA_Team, JIRA_Confidence, JIRA_Created_Date, JIRA_Updated_Date,
    JIRA_Effort_Story_Points, CR_ID_Link
) VALUES (
    'NOVA-1', 'Epic', 'Critical', 'SecurityLayer;Database', 'ux-improvement;beta-feature;tech-debt', 'Sprint 3 (Nova Beta)', NULL,
    'PM_Anna', 'PM_Anna', '2023-10-04', '2023-10-09', 'Pending', 'Mobile Wallet MVP Development', 'Detailed description for Mobile Wallet MVP Development. This involves several steps and considerations, including integration with other modules.',
    NULL, 'Team Phoenix', 77, '2023-09-29', '2023-12-27',
    NULL, NULL -- Assuming CR_ID_Link is not present on these specific example rows for the core NOVA-1
);
GO
-- ... (You would add more unique JIRA issues here, e.g., NOVA-17, NOVA-20, NOVA-29, NOVA-30, NOVA-40 if they appear as unique issues)
-- Example for NOVA-17 (assuming it's a unique issue mentioned in CR_Main)
INSERT INTO JiraIssues (JIRA_ID, JIRA_Title, JIRA_Created_Date, JIRA_Updated_Date)
VALUES ('NOVA-17', 'Placeholder for NOVA-17 details', GETDATE(), GETDATE());
GO
INSERT INTO JiraIssues (JIRA_ID, JIRA_Title, JIRA_Created_Date, JIRA_Updated_Date)
VALUES ('NOVA-29', 'Placeholder for NOVA-29 details', GETDATE(), GETDATE());
GO
INSERT INTO JiraIssues (JIRA_ID, JIRA_Title, JIRA_Created_Date, JIRA_Updated_Date)
VALUES ('NOVA-40', 'Placeholder for NOVA-40 details', GETDATE(), GETDATE());
GO
-- Add NOVA-20, NOVA-24, NOVA-4, NOVA-31, NOVA-48, NOVA-26 based on other CSVs
INSERT INTO JiraIssues (JIRA_ID, JIRA_Title, JIRA_Created_Date, JIRA_Updated_Date) VALUES ('NOVA-20', 'Placeholder for NOVA-20', GETDATE(), GETDATE());
INSERT INTO JiraIssues (JIRA_ID, JIRA_Title, JIRA_Created_Date, JIRA_Updated_Date) VALUES ('NOVA-24', 'Placeholder for NOVA-24', GETDATE(), GETDATE());
INSERT INTO JiraIssues (JIRA_ID, JIRA_Title, JIRA_Created_Date, JIRA_Updated_Date) VALUES ('NOVA-4', 'Placeholder for NOVA-4', GETDATE(), GETDATE());
INSERT INTO JiraIssues (JIRA_ID, JIRA_Title, JIRA_Created_Date, JIRA_Updated_Date) VALUES ('NOVA-31', 'Placeholder for NOVA-31', GETDATE(), GETDATE());
INSERT INTO JiraIssues (JIRA_ID, JIRA_Title, JIRA_Created_Date, JIRA_Updated_Date) VALUES ('NOVA-48', 'Placeholder for NOVA-48', GETDATE(), GETDATE());
INSERT INTO JiraIssues (JIRA_ID, JIRA_Title, JIRA_Created_Date, JIRA_Updated_Date) VALUES ('NOVA-26', 'Placeholder for NOVA-26', GETDATE(), GETDATE());
INSERT INTO JiraIssues (JIRA_ID, JIRA_Title, JIRA_Created_Date, JIRA_Updated_Date) VALUES ('NOVA-30', 'Placeholder for NOVA-30', GETDATE(), GETDATE());
GO


-- =======================================================================
-- Inserts for JiraIssueLinks (from JIRA_Issues_Detailed.csv where link fields are populated)
-- =======================================================================
-- From: NOVA-1 ... JIRA_Linked_Issue_ID_Target=NOVA-29, JIRA_Link_Type=sub-task of
INSERT INTO JiraIssueLinks (Source_JIRA_ID, Target_JIRA_ID, JIRA_Link_Type)
VALUES ('NOVA-1', 'NOVA-29', 'sub-task of');
GO

-- From: NOVA-1 ... JIRA_Linked_Issue_ID_Target=NOVA-40, JIRA_Link_Type=relates to
INSERT INTO JiraIssueLinks (Source_JIRA_ID, Target_JIRA_ID, JIRA_Link_Type)
VALUES ('NOVA-1', 'NOVA-40', 'relates to');
GO

-- =======================================================================
-- Inserts for JiraIssueWatchers (from JIRA_Issues_Detailed.csv where watcher field is populated)
-- =======================================================================
-- The provided JIRA_Issues_Detailed.csv sample rows don't have watchers for NOVA-1.
-- If a row was: NOVA-1, ..., JIRA_Watcher_User=UserA
-- It would be:
-- INSERT INTO JiraIssueWatchers (JIRA_ID, JIRA_Watcher_User) VALUES ('NOVA-1', 'UserA');
-- GO


-- =======================================================================
-- Inserts for ChangeRequests (CR_Main.csv)
-- =======================================================================
INSERT INTO ChangeRequests (
    CR_ID, CR_Title, Linked_Jira_ID, Linked_Confluence_ID, CR_State, CR_Requested_By,
    CR_Team_Assignment_Group, CR_Assigned_To_User, CR_Impacted_Environment, CR_Impacted_Departments,
    CR_Type, CR_Category, CR_Risk, CR_Risk_Percentage, CR_Lead_Time_Days, CR_Conflict_Status,
    CR_Description, CR_Start_Date, CR_End_Date, CR_Implementation_Plan_Summary, CR_Backout_Plan_Summary,
    CR_Updated_By_User, CR_Record_Created_At
) VALUES (
    'CR001', 'Emergency Fix for Production Issue - CR001', 'NOVA-17', 'CONF-005', 'New', 'User_Pia',
    'Team Griffin', 'Sarah_P', 'Production', 'Marketing;Compliance;Engineering',
    'Emergency', 'Emergency', 'High', 32, 24, 'No Conflict',
    'This change request (CR001) is for Emergency Fix for Production Issue - CR001. It requires careful planning and execution. This CR, if approved, will proceed as planned.',
    NULL, NULL, 'Pending assessment', 'Pending assessment',
    'User_Pia', '2023-11-14'
);
GO

INSERT INTO ChangeRequests (
    CR_ID, CR_Title, Linked_Jira_ID, Linked_Confluence_ID, CR_State, CR_Requested_By,
    CR_Team_Assignment_Group, CR_Assigned_To_User, CR_Impacted_Environment, CR_Impacted_Departments,
    CR_Type, CR_Category, CR_Risk, CR_Risk_Percentage, CR_Lead_Time_Days, CR_Conflict_Status,
    CR_Description, CR_Start_Date, CR_End_Date, CR_Implementation_Plan_Summary, CR_Backout_Plan_Summary,
    CR_Updated_By_User, CR_Record_Created_At
) VALUES (
    'CR001', 'Emergency Fix for Production Issue - CR001', 'NOVA-17', 'CONF-005', 'Assess', 'User_Pia',
    'Team Griffin', 'Sarah_P', 'Production', 'Marketing;Compliance;Engineering',
    'Emergency', 'Emergency', 'High', 32, 24, 'No Conflict',
    'This change request (CR001) is for Emergency Fix for Production Issue - CR001. It requires careful planning and execution. This CR, if approved, will proceed as planned.',
    NULL, NULL, 'Pending assessment', 'Pending assessment',
    'User_Raj', '2023-11-15'
);
GO
-- Insert other CRs (CR018, CR004, CR020) placeholders if not fully detailed
INSERT INTO ChangeRequests (CR_ID, CR_Title, CR_Record_Created_At) VALUES ('CR018', 'Placeholder CR018', GETDATE());
INSERT INTO ChangeRequests (CR_ID, CR_Title, CR_Record_Created_At) VALUES ('CR004', 'Placeholder CR004', GETDATE());
INSERT INTO ChangeRequests (CR_ID, CR_Title, CR_Record_Created_At) VALUES ('CR020', 'Placeholder CR020', GETDATE());
INSERT INTO ChangeRequests (CR_ID, CR_Title, CR_Record_Created_At) VALUES ('CR005', 'Placeholder CR005', GETDATE());
GO

-- =======================================================================
-- Inserts for ConfluencePages (Confluence_Pages_Detailed.csv)
-- =======================================================================
INSERT INTO ConfluencePages (
    Confluence_ID, Confluence_Title, Confluence_Owner_Member, Confluence_Last_Edited_By, Confluence_Space,
    Confluence_Team_Association, Confluence_Content_Summary, Confluence_Linked_Jira_ID, Confluence_Linked_CR_ID,
    Confluence_Parent_Page_ID, Confluence_Created_Date, Confluence_Last_Modified_Date
) VALUES (
    'CONF-001', 'Project Nova Overview (CONF-001)', 'Ops_Jim', 'Chloe_P_Dev', 'Project Nova',
    'Cross-functional', 'This document (CONF-001: Project Nova Overview (CONF-001)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context.',
    'NOVA-24;NOVA-4;NOVA-31', 'CR018',
    NULL, '2023-11-02', '2023-12-23' -- Assuming Parent_Page_ID is blank for this row
);
GO
INSERT INTO ConfluencePages (
    Confluence_ID, Confluence_Title, Confluence_Owner_Member, Confluence_Last_Edited_By, Confluence_Space,
    Confluence_Team_Association, Confluence_Content_Summary, Confluence_Linked_Jira_ID, Confluence_Linked_CR_ID,
    Confluence_Parent_Page_ID, Confluence_Created_Date, Confluence_Last_Modified_Date
) VALUES (
    'CONF-002', 'Marketing Campaign Plan - Wallet Launch (CONF-002)', 'Noah_G_Dev', 'QA_Emma', 'Marketing Hub',
    'Marketing', 'This document (CONF-002: Marketing Campaign Plan - Wallet Launch (CONF-002)) provides a summary of key information. It includes details about objectives, scope, and relevant findings. Please refer to linked items for more context. This page is currently under review, feedback is welcome.',
    'NOVA-48;NOVA-26', 'CR004;CR020',
    NULL, '2023-09-09', '2023-12-11'
);
GO
-- Insert CONF-005 for CR linking
INSERT INTO ConfluencePages (Confluence_ID, Confluence_Title, Confluence_Created_Date, Confluence_Last_Modified_Date)
VALUES ('CONF-005', 'Placeholder CONF-005', GETDATE(), GETDATE());
GO


-- =======================================================================
-- Inserts for JiraActivities (JIRA_Activities.csv)
-- =======================================================================
INSERT INTO JiraActivities (
    Activity_ID_Source, JIRA_ID, Activity_Comment, Activity_Timestamp, Activity_User
) VALUES (
    'ACT-001', 'NOVA-20', 'Status changed to Development.', '2023-09-23 12:38:00', 'Ops_Jim'
);
GO

INSERT INTO JiraActivities (
    Activity_ID_Source, JIRA_ID, Activity_Comment, Activity_Timestamp, Activity_User
) VALUES (
    'ACT-002', 'NOVA-30', 'Status changed to Review.', '2023-10-14 17:18:00', 'User_Kate'
);
GO

-- =======================================================================
-- Inserts for CR_CTasks (CR_CTasks.csv)
-- =======================================================================
INSERT INTO CR_CTasks (
    CTASK_ID_Source, CR_ID, CTASK_Assigned_To_User, CTASK_Start_Time, CTASK_End_Time, CTASK_Description
) VALUES (
    'CTASK001', 'CR005', 'David_H', '2023-11-15 12:00:00', '2023-11-15 15:00:00', 'Communicate CR implementation to stakeholders.'
);
GO

INSERT INTO CR_CTasks (
    CTASK_ID_Source, CR_ID, CTASK_Assigned_To_User, CTASK_Start_Time, CTASK_End_Time, CTASK_Description
) VALUES (
    'CTASK002', 'CR001', 'Sarah_P', '2023-11-23 11:15:00', '2023-11-23 14:15:00', 'Document CR closure.'
);
GO
```

**Recommendations for Real-World Scenarios:**

*   **Data Loading Tools:** For loading entire CSV files, use:
    *   **SQL Server Import and Export Wizard:** Right-click your database in SSMS > Tasks > Import Data.
    *   **`BULK INSERT` T-SQL command:** Very efficient for large files.
        ```sql
        BULK INSERT JiraIssues_Temp -- Load to a staging table first
        FROM 'C:\path\to\your\JIRA_Issues_Detailed.csv'
        WITH (
            FORMAT = 'CSV',
            FIRSTROW = 2, -- Skip header row
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '\n', -- Or '\r\n'
            KEEPNULLS,
            TABLOCK
        );
        -- Then process from JiraIssues_Temp to your normalized tables
        ```
    *   **SSIS (SQL Server Integration Services):** For complex ETL workflows.
    *   **Python with `pandas` and `pyodbc`/`sqlalchemy`:** Read CSV into a DataFrame, transform as needed, then write to SQL tables. This gives you great control over normalization logic.

This set of scripts should give you a good starting point for creating the schema and understanding how to insert the sample data. Remember to adapt data types and constraints based on the full range and rules of your actual data.