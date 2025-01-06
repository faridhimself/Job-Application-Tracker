# Job Application Tracker

The **Job Application Tracker** is a Python-based application designed to help users manage and track their job applications efficiently. It integrates with a SQL Server database to ensure all job applications added, updated, or deleted are automatically reflected in the database, providing real-time data persistence and synchronization.

## Features

- **Application Management:** Add, edit, and delete job applications with details such as position name, company, application status, and more.
- **Status Tracking:** Monitor the progress of each application through various stages (e.g., Applied, Interview, Offer, Rejected).
- **Priority Setting:** Assign priority levels to applications to focus on the most important opportunities.
- **Reminder System:** Set reminder dates for follow-ups and important deadlines.
- **Data Persistence:** All data is stored in a SQL Server database for reliability and scalability, with automatic synchronization of changes.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/faridhimself/Job-Application-Tracker.git
   cd Job-Application-Tracker
   ```

2. **Set up the SQL Server database:**

   - Ensure SQL Server is installed and running on your system.
   - Create a database named `JobApplicationsDB`.
   - Update the database connection settings in `app.py`:

     ```python
     DB_SERVER = 'localhost'  # Update with your SQL Server host
     DB_PORT = '1433'        # Default SQL Server port
     DB_NAME = 'JobApplicationsDB'
     DB_USER = 'your_username'
     DB_PASSWORD = 'your_password'
     ```

   - Execute the SQL script to create the necessary table:

     ```bash
     sqlcmd -S localhost -d JobApplicationsDB -U your_username -P your_password -i create_job_applications_table.sql
     ```

3. **Install the required Python packages:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**

   - For the Flask web application:

     ```bash
     python app.py
     ```

   - For the desktop application:

     ```bash
     python desktop_app.py
     ```

## Usage

1. **Add Applications:** Use the interface to input job application details such as:
   - Company name
   - Job title
   - Date applied
   - Current status
   - Notes

2. **Track Status:** View all applications in the tracker, filter by status, and monitor their progress.

3. **Data Synchronization:** All changes (additions, updates, deletions) are automatically reflected in the SQL Server database in real-time.

4. **Export Data:** Export job application data from the database for reporting or backup purposes.

## File Structure

- `app.py`: Main Flask application for the web interface.
- `desktop_app.py`: Desktop application interface.
- `create_job_applications_table.sql`: SQL script to create the `job_applications` table in SQL Server.
- `requirements.txt`: List of required Python packages.
- `start_job_tracker.bat`: Batch file to start the application on Windows systems.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch:

   ```bash
   git checkout -b feature-name
   ```

3. Commit your changes:

   ```bash
   git commit -m "Add new feature"
   ```

4. Push to your branch:

   ```bash
   git push origin feature-name
   ```

5. Open a pull request.

## License

This project is licensed under the MIT License.

---

Feel free to reach out with any questions or suggestions to improve the tracker. Your contributions and feedback are highly appreciated!
