-- File: create_job_applications_table.sql

-- This script creates a table named job_applications
-- in the 'postgres' database. Make sure you're connected to the correct DB!

CREATE TABLE IF NOT EXISTS job_applications (
    id SERIAL PRIMARY KEY,
    position_name VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    link_to_job_ad TEXT,
    used_cv VARCHAR(255),
    used_cover_letter VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    date_of_application DATE NOT NULL,
    days_since_applied INT,
    last_modified_date DATE,
    notes TEXT,
    priority VARCHAR(50),
    reminder_date DATE
);

select * from job_applications;
