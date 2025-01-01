import os
import psycopg2
from flask import Flask, render_template_string, request, redirect, url_for, flash
from datetime import date, datetime
from psycopg2.extras import RealDictCursor

#######################################
# CONFIGURATION
#######################################
# If you prefer environment variables, you can use:
# from dotenv import load_dotenv
# load_dotenv()

# For now, let's hardcode your credentials to keep it simple:
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = 'Qafqaz1995Arzu'  # <-- CHANGE TO YOUR PASSWORD

#######################################
# FLASK APP
#######################################
app = Flask(__name__)

#######################################
# HELPER FUNCTIONS
#######################################
def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def calculate_days_since_applied(application_date):
    """Calculates the number of days since the given application_date."""
    reference_date = datetime(2025, 1, 1, 16, 21, 42)  # Using the provided timestamp
    today = reference_date.date()
    delta = today - application_date
    return delta.days

def update_days_since_applied_and_last_modified(record):
    """
    Updates 'days_since_applied' and 'last_modified_date' 
    based on the status and date_of_application.
    """
    record['days_since_applied'] = calculate_days_since_applied(record['date_of_application'])
    
    # Update last_modified_date if status is not "Rejected"
    if record['status'].lower() != "rejected":
        record['last_modified_date'] = date.today()
    else:
        # If it's rejected, we do not change last_modified_date
        pass
    return record

def get_weekly_stats():
    """Get statistics for the current week's job applications."""
    print("Calculating weekly stats...")
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Get the start of the current week (Monday)
        cur.execute("""
            SELECT COUNT(*) as weekly_count 
            FROM job_applications 
            WHERE date_trunc('week', date_of_application) = date_trunc('week', CURRENT_DATE);
        """)
        result = cur.fetchone()
        print(f"Weekly count query result: {result}")
    conn.close()
    
    weekly_count = result['weekly_count'] if result and result['weekly_count'] else 0
    goal = 100
    progress = (weekly_count / goal) * 100
    
    # Calculate days remaining in the week
    today = datetime(2025, 1, 1, 17, 4, 30).date()  # Using provided timestamp
    days_until_sunday = 7 - today.isoweekday()
    
    stats = {
        'weekly_count': weekly_count,
        'goal': goal,
        'progress': min(progress, 100),
        'days_remaining': days_until_sunday
    }
    print(f"Calculated stats: {stats}")
    return stats

#######################################
# FLASK ROUTES
#######################################
# 1) Home page: list all job applications
@app.route('/')
def index():
    """Home page: list all job applications"""
    print("Loading index page...")
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM job_applications ORDER BY id;")
        applications = cur.fetchall()
        print(f"Found {len(applications)} applications")
    conn.close()

    weekly_stats = get_weekly_stats()
    print("Rendering template...")

    # Simple HTML template
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Job Application Tracker</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            .status-applied { background-color: #fff3cd; }
            .status-interview { background-color: #cfe2ff; }
            .status-rejected { background-color: #f8d7da; }
            .status-accepted { background-color: #d1e7dd; }
            .priority-high { border-left: 4px solid #dc3545; }
            .priority-medium { border-left: 4px solid #ffc107; }
            .priority-low { border-left: 4px solid #198754; }
            .table-responsive { margin-top: 20px; }
            .btn-add { margin: 20px 0; }
            .search-box { margin: 20px 0; }
            .goal-tracker {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .progress {
                height: 25px;
                background-color: #e9ecef;
                border-radius: 15px;
            }
            .progress-bar {
                transition: width 0.5s ease-in-out;
                border-radius: 15px;
            }
            .progress-bar.good { background-color: #198754; }
            .progress-bar.warning { background-color: #ffc107; }
            .progress-bar.danger { background-color: #dc3545; }
            .stats-card {
                background-color: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                height: 100%;
            }
            .stats-number {
                font-size: 24px;
                font-weight: bold;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="container-fluid py-4">
            <!-- Goal Tracker Section -->
            <div class="goal-tracker">
                <h3 class="mb-3">Weekly Application Goal Tracker</h3>
                <div class="progress mb-4">
                    <div class="progress-bar progress-bar-striped progress-bar-animated {{ 'good' if weekly_stats['progress'] >= 80 else 'warning' if weekly_stats['progress'] >= 50 else 'danger' }}" 
                         role="progressbar" 
                         style="width: {{ weekly_stats['progress'] }}%"
                         aria-valuenow="{{ weekly_stats['weekly_count'] }}" 
                         aria-valuemin="0" 
                         aria-valuemax="100">
                        {{ weekly_stats['weekly_count'] }}/{{ weekly_stats['goal'] }} Applications
                    </div>
                </div>
                <div class="row g-3">
                    <div class="col-md-4">
                        <div class="stats-card">
                            <h5 class="text-muted mb-0">Weekly Progress</h5>
                            <div class="stats-number">{{ weekly_stats['weekly_count'] }} / {{ weekly_stats['goal'] }}</div>
                            <small class="text-muted">Applications submitted this week</small>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stats-card">
                            <h5 class="text-muted mb-0">Time Remaining</h5>
                            <div class="stats-number">{{ weekly_stats['days_remaining'] }}</div>
                            <small class="text-muted">Days left this week</small>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stats-card">
                            <h5 class="text-muted mb-0">Daily Target</h5>
                            <div class="stats-number">
                                {% if weekly_stats['days_remaining'] > 0 %}
                                    {{ ((weekly_stats['goal'] - weekly_stats['weekly_count']) / weekly_stats['days_remaining']) | round(1) }}
                                {% else %}
                                    0
                                {% endif %}
                            </div>
                            <small class="text-muted">Applications needed per day</small>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mb-3">
                <div class="col">
                    <h1 class="display-4">Job Applications</h1>
                </div>
            </div>

            <div class="row mb-3">
                <div class="col-md-4">
                    <a href="{{ url_for('add_application') }}" class="btn btn-primary btn-add">
                        <i class="bi bi-plus-circle"></i> Add New Application
                    </a>
                </div>
                <div class="col-md-8">
                    <div class="search-box">
                        <input type="text" id="searchInput" class="form-control" placeholder="Search applications...">
                    </div>
                </div>
            </div>

            <div class="table-responsive">
                <table class="table table-hover" id="applicationsTable">
                    <thead class="table-light">
                        <tr>
                            <th onclick="sortTable(0)">ID <i class="bi bi-arrow-down-up"></i></th>
                            <th onclick="sortTable(1)">Position Name <i class="bi bi-arrow-down-up"></i></th>
                            <th onclick="sortTable(2)">Company <i class="bi bi-arrow-down-up"></i></th>
                            <th>Link</th>
                            <th>CV Used</th>
                            <th>Cover Letter</th>
                            <th onclick="sortTable(6)">Status <i class="bi bi-arrow-down-up"></i></th>
                            <th onclick="sortTable(7)">Date Applied <i class="bi bi-arrow-down-up"></i></th>
                            <th onclick="sortTable(8)">Days Since Applied <i class="bi bi-arrow-down-up"></i></th>
                            <th>Last Modified</th>
                            <th>Notes</th>
                            <th onclick="sortTable(11)">Priority <i class="bi bi-arrow-down-up"></i></th>
                            <th>Reminder Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for app in applications %}
                        <tr class="status-{{ app.status.lower() }} priority-{{ app.priority.lower() }}">
                            <td>{{ app.id }}</td>
                            <td>{{ app.position_name }}</td>
                            <td>{{ app.company }}</td>
                            <td>
                                {% if app.link_to_job_ad %}
                                    <a href="{{ app.link_to_job_ad }}" class="btn btn-sm btn-outline-primary" target="_blank">
                                        <i class="bi bi-link-45deg"></i> View
                                    </a>
                                {% endif %}
                            </td>
                            <td>{{ app.used_cv }}</td>
                            <td>{{ app.used_cover_letter }}</td>
                            <td><span class="badge bg-secondary">{{ app.status }}</span></td>
                            <td>{{ app.date_of_application }}</td>
                            <td>{{ app.days_since_applied }}</td>
                            <td>{{ app.last_modified_date }}</td>
                            <td>
                                {% if app.notes %}
                                    <button type="button" class="btn btn-sm btn-outline-info" data-bs-toggle="tooltip" title="{{ app.notes }}">
                                        <i class="bi bi-info-circle"></i>
                                    </button>
                                {% endif %}
                            </td>
                            <td><span class="badge bg-{{ 'danger' if app.priority == 'High' else 'warning' if app.priority == 'Medium' else 'success' }}">{{ app.priority }}</span></td>
                            <td>{{ app.reminder_date }}</td>
                            <td>
                                <div class="btn-group">
                                    <a href="{{ url_for('edit_application', app_id=app.id) }}" class="btn btn-sm btn-outline-primary">
                                        <i class="bi bi-pencil"></i>
                                    </a>
                                    <a href="{{ url_for('delete_application', app_id=app.id) }}" class="btn btn-sm btn-outline-danger" 
                                       onclick="return confirm('Are you sure you want to delete this application?')">
                                        <i class="bi bi-trash"></i>
                                    </a>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Initialize tooltips
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl)
            })

            // Search functionality
            document.getElementById('searchInput').addEventListener('keyup', function() {
                var input = this.value.toLowerCase();
                var table = document.getElementById('applicationsTable');
                var rows = table.getElementsByTagName('tr');

                for (var i = 1; i < rows.length; i++) {
                    var show = false;
                    var cells = rows[i].getElementsByTagName('td');
                    for (var j = 0; j < cells.length; j++) {
                        if (cells[j].textContent.toLowerCase().indexOf(input) > -1) {
                            show = true;
                            break;
                        }
                    }
                    rows[i].style.display = show ? '' : 'none';
                }
            });

            // Sorting functionality
            function sortTable(n) {
                var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
                table = document.getElementById("applicationsTable");
                switching = true;
                dir = "asc";
                
                while (switching) {
                    switching = false;
                    rows = table.rows;
                    
                    for (i = 1; i < (rows.length - 1); i++) {
                        shouldSwitch = false;
                        x = rows[i].getElementsByTagName("TD")[n];
                        y = rows[i + 1].getElementsByTagName("TD")[n];
                        
                        if (dir == "asc") {
                            if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                                shouldSwitch = true;
                                break;
                            }
                        } else if (dir == "desc") {
                            if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                                shouldSwitch = true;
                                break;
                            }
                        }
                    }
                    
                    if (shouldSwitch) {
                        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                        switching = true;
                        switchcount++;
                    } else {
                        if (switchcount == 0 && dir == "asc") {
                            dir = "desc";
                            switching = true;
                        }
                    }
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, applications=applications, weekly_stats=weekly_stats)

# 2) Add a new application
@app.route('/add', methods=['GET', 'POST'])
def add_application():
    if request.method == 'POST':
        # Collect form data
        position_name = request.form['position_name']
        company = request.form['company']
        link_to_job_ad = request.form['link_to_job_ad']
        used_cv = request.form['used_cv']
        used_cover_letter = request.form['used_cover_letter']
        status = request.form['status']
        date_of_application = request.form['date_of_application']
        notes = request.form['notes']
        priority = request.form['priority']
        reminder_date = request.form['reminder_date'] or None

        record = {
            'position_name': position_name,
            'company': company,
            'link_to_job_ad': link_to_job_ad,
            'used_cv': used_cv,
            'used_cover_letter': used_cover_letter,
            'status': status,
            'date_of_application': date.fromisoformat(date_of_application),
            'days_since_applied': 0,
            'last_modified_date': None,
            'notes': notes,
            'priority': priority,
            'reminder_date': date.fromisoformat(reminder_date) if reminder_date else None
        }

        # Update days_since_applied & last_modified_date
        record = update_days_since_applied_and_last_modified(record)

        # Insert into DB
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO job_applications 
                    (position_name, company, link_to_job_ad, used_cv, used_cover_letter, status, 
                     date_of_application, days_since_applied, last_modified_date, notes, priority, reminder_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                record['position_name'], record['company'], record['link_to_job_ad'],
                record['used_cv'], record['used_cover_letter'], record['status'],
                record['date_of_application'], record['days_since_applied'],
                record['last_modified_date'], record['notes'], record['priority'],
                record['reminder_date']
            ))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    else:
        # Display form
        html_template = """
        <html>
        <head><title>Add Application</title></head>
        <body>
            <h1>Add a New Application</h1>
            <form method="POST">
                <label>Position Name:</label><br/>
                <input type="text" name="position_name" required><br/><br/>

                <label>Company:</label><br/>
                <input type="text" name="company" required><br/><br/>

                <label>Link to Job Ad:</label><br/>
                <input type="text" name="link_to_job_ad"><br/><br/>

                <label>Used CV (filename):</label><br/>
                <input type="text" name="used_cv"><br/><br/>

                <label>Used Cover Letter (filename/path):</label><br/>
                <input type="text" name="used_cover_letter"><br/><br/>

                <label>Status:</label><br/>
                <select name="status">
                    <option value="Applied">Applied</option>
                    <option value="Interview">Interview</option>
                    <option value="Offer">Offer</option>
                    <option value="Rejected">Rejected</option>
                </select><br/><br/>

                <label>Date of Application:</label><br/>
                <input type="date" name="date_of_application" required><br/><br/>

                <label>Notes:</label><br/>
                <textarea name="notes"></textarea><br/><br/>

                <label>Priority:</label><br/>
                <select name="priority">
                    <option value="Low">Low</option>
                    <option value="Medium" selected>Medium</option>
                    <option value="High">High</option>
                </select><br/><br/>

                <label>Reminder Date:</label><br/>
                <input type="date" name="reminder_date"><br/><br/>

                <input type="submit" value="Add Application">
            </form>
            <br>
            <a href="{{ url_for('index') }}">Back to Home</a>
        </body>
        </html>
        """
        return render_template_string(html_template)

# 3) Edit an existing application
@app.route('/edit/<int:app_id>', methods=['GET', 'POST'])
def edit_application(app_id):
    conn = get_db_connection()
    if request.method == 'POST':
        position_name = request.form['position_name']
        company = request.form['company']
        link_to_job_ad = request.form['link_to_job_ad']
        used_cv = request.form['used_cv']
        used_cover_letter = request.form['used_cover_letter']
        status = request.form['status']
        date_of_application = request.form['date_of_application']
        notes = request.form['notes']
        priority = request.form['priority']
        reminder_date = request.form['reminder_date'] or None

        # Get the current record for days_since_applied, last_modified_date
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM job_applications WHERE id = %s;", (app_id,))
            current_record = cur.fetchone()

        record = {
            'id': app_id,
            'position_name': position_name,
            'company': company,
            'link_to_job_ad': link_to_job_ad,
            'used_cv': used_cv,
            'used_cover_letter': used_cover_letter,
            'status': status,
            'date_of_application': date.fromisoformat(date_of_application),
            'days_since_applied': current_record['days_since_applied'],
            'last_modified_date': current_record['last_modified_date'],
            'notes': notes,
            'priority': priority,
            'reminder_date': date.fromisoformat(reminder_date) if reminder_date else None
        }

        # Update days_since_applied & last_modified_date
        record = update_days_since_applied_and_last_modified(record)

        # Update in DB
        with conn.cursor() as cur:
            sql = """
                UPDATE job_applications
                SET position_name = %s,
                    company = %s,
                    link_to_job_ad = %s,
                    used_cv = %s,
                    used_cover_letter = %s,
                    status = %s,
                    date_of_application = %s,
                    days_since_applied = %s,
                    last_modified_date = %s,
                    notes = %s,
                    priority = %s,
                    reminder_date = %s
                WHERE id = %s
            """
            cur.execute(sql, (
                record['position_name'], record['company'], record['link_to_job_ad'],
                record['used_cv'], record['used_cover_letter'], record['status'],
                record['date_of_application'], record['days_since_applied'],
                record['last_modified_date'], record['notes'], record['priority'],
                record['reminder_date'], record['id']
            ))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    else:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM job_applications WHERE id = %s;", (app_id,))
            application = cur.fetchone()
        conn.close()

        html_template = """
        <html>
        <head><title>Edit Application</title></head>
        <body>
            <h1>Edit Application (ID: {{ application.id }})</h1>
            <form method="POST">
                <label>Position Name:</label><br/>
                <input type="text" name="position_name" value="{{ application.position_name }}" required><br/><br/>

                <label>Company:</label><br/>
                <input type="text" name="company" value="{{ application.company }}" required><br/><br/>

                <label>Link to Job Ad:</label><br/>
                <input type="text" name="link_to_job_ad" value="{{ application.link_to_job_ad }}"><br/><br/>

                <label>Used CV (filename):</label><br/>
                <input type="text" name="used_cv" value="{{ application.used_cv }}"><br/><br/>

                <label>Used Cover Letter (filename/path):</label><br/>
                <input type="text" name="used_cover_letter" value="{{ application.used_cover_letter }}"><br/><br/>

                <label>Status:</label><br/>
                <select name="status">
                    <option value="Applied" {% if application.status == 'Applied' %}selected{% endif %}>Applied</option>
                    <option value="Interview" {% if application.status == 'Interview' %}selected{% endif %}>Interview</option>
                    <option value="Offer" {% if application.status == 'Offer' %}selected{% endif %}>Offer</option>
                    <option value="Rejected" {% if application.status == 'Rejected' %}selected{% endif %}>Rejected</option>
                </select><br/><br/>

                <label>Date of Application:</label><br/>
                <input type="date" name="date_of_application" value="{{ application.date_of_application }}" required><br/><br/>

                <label>Notes:</label><br/>
                <textarea name="notes">{{ application.notes }}</textarea><br/><br/>

                <label>Priority:</label><br/>
                <select name="priority">
                    <option value="Low" {% if application.priority == 'Low' %}selected{% endif %}>Low</option>
                    <option value="Medium" {% if application.priority == 'Medium' %}selected{% endif %}>Medium</option>
                    <option value="High" {% if application.priority == 'High' %}selected{% endif %}>High</option>
                </select><br/><br/>

                <label>Reminder Date:</label><br/>
                <input type="date" name="reminder_date" value="{{ application.reminder_date }}"><br/><br/>

                <input type="submit" value="Update Application">
            </form>
            <br>
            <a href="{{ url_for('index') }}">Back to Home</a>
        </body>
        </html>
        """
        return render_template_string(html_template, application=application)

# 4) Delete an application
@app.route('/delete/<int:app_id>')
def delete_application(app_id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM job_applications WHERE id = %s;", (app_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

#######################################
# MAIN ENTRY POINT
#######################################
if __name__ == '__main__':
    app.run(debug=True)
