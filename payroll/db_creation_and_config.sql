-- 1. Create a strong dedicated user for Django
CREATE USER coral_payroll WITH 
    PASSWORD 'Employer5-Pediatric9-Recapture4-Calamari1-Crunchy2'
    LOGIN 
    CREATEDB;   -- Allows Django to create test DBs if needed

-- 2. Create the database (if you haven't yet)
CREATE DATABASE db_coralaccounting 
    WITH OWNER = coral_payroll 
    ENCODING = 'UTF8' 
    LC_COLLATE = 'en_US.UTF-8' 
    LC_CTYPE = 'en_US.UTF-8' 
    TEMPLATE template0;

-- 3. Grant permissions
GRANT ALL PRIVILEGES ON DATABASE db_coralaccounting TO coral_payroll;

-- 4. Connect to the new DB and set schema permissions
\c db_coralaccounting

GRANT ALL ON SCHEMA public TO coral_payroll;
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT ALL ON TABLES TO coral_payroll;

ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT ALL ON SEQUENCES TO coral_payroll;

ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT ALL ON FUNCTIONS TO coral_payroll;