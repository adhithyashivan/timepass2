CREATE TABLE AGENT_QUESTIONAIRE_AuditLog (
    AuditLogID INT PRIMARY KEY IDENTITY(1,1),
    QuestionaireID INT,             -- Foreign key to AGENT_QUESTIONAIRE.ID
    OldQuestion VARCHAR(MAX),
    NewQuestion VARCHAR(MAX),
    OldAnswer VARCHAR(MAX),
    NewAnswer VARCHAR(MAX),
    ActionTaken VARCHAR(10) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    ActionTimestamp DATETIME DEFAULT GETDATE(),
    ActionUser VARCHAR(128) DEFAULT SUSER_SNAME()
);
GO




CREATE TRIGGER TR_AGENT_QUESTIONAIRE_Audit
ON AGENT_QUESTIONAIRE
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    -- Ensure the trigger doesn't run if no rows were actually affected
    IF @@ROWCOUNT = 0
        RETURN;

    SET NOCOUNT ON;

    -- Check for INSERT operation
    IF EXISTS (SELECT 1 FROM inserted) AND NOT EXISTS (SELECT 1 FROM deleted)
    BEGIN
        INSERT INTO AGENT_QUESTIONAIRE_AuditLog (
            QuestionaireID,
            NewQuestion,
            NewAnswer,
            ActionTaken,
            ActionTimestamp,
            ActionUser
        )
        SELECT
            i.ID,
            i.Question,
            i.Answer,
            'INSERT',
            GETDATE(),
            SUSER_SNAME()
        FROM inserted i;
    END

    -- Check for DELETE operation
    IF EXISTS (SELECT 1 FROM deleted) AND NOT EXISTS (SELECT 1 FROM inserted)
    BEGIN
        INSERT INTO AGENT_QUESTIONAIRE_AuditLog (
            QuestionaireID,
            OldQuestion,
            OldAnswer,
            ActionTaken,
            ActionTimestamp,
            ActionUser
        )
        SELECT
            d.ID,
            d.Question,
            d.Answer,
            'DELETE',
            GETDATE(),
            SUSER_SNAME()
        FROM deleted d;
    END

    -- Check for UPDATE operation
    IF EXISTS (SELECT 1 FROM inserted) AND EXISTS (SELECT 1 FROM deleted)
    BEGIN
        INSERT INTO AGENT_QUESTIONAIRE_AuditLog (
            QuestionaireID,
            OldQuestion,
            NewQuestion,
            OldAnswer,
            NewAnswer,
            ActionTaken,
            ActionTimestamp,
            ActionUser
        )
        SELECT
            i.ID,
            d.Question,  -- Old Question from 'deleted' table
            i.Question,  -- New Question from 'inserted' table
            d.Answer,    -- Old Answer from 'deleted' table
            i.Answer,    -- New Answer from 'inserted' table
            'UPDATE',
            GETDATE(),
            SUSER_SNAME()
        FROM inserted i
        INNER JOIN deleted d ON i.ID = d.ID; -- Join on the primary key 'ID'
    END
END;
GO