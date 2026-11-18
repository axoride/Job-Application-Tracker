# Job Application Tracker

A full-stack web application for tracking job applications, built for COP4751.
It uses Python/Flask, MySQL, and HTML/CSS, and includes a skills-based Job Match feature.

## Features
- **Dashboard** with totals, applications by status, and recent applications
- **Companies, Jobs, Applications, and Contacts** with full Create, Read, Update, and Delete (delete asks for confirmation)
- **JSON columns** for job requirements (`jobs.requirements`) and interview details (`applications.interview_data`)
- **Job Match:** enter your skills and see jobs ranked by match percentage, with missing skills listed

## Requirements
- Python 3
- MySQL 8.0 or newer
- MySQL Workbench (optional, but makes running the SQL file easier)

## Setup

1. **Clone the repository and open the project folder.**

2. **Install the dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Create the database.** Run `schema.sql` in MySQL Workbench (File > Open SQL Script, then run it), or from the command line:
   ```
   mysql -u root -p < schema.sql
   ```
   This creates the `job_tracker` database and its 4 tables.

4. **Create your `.env` file** in the project folder with your MySQL settings:
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=job_tracker
   DB_PORT=3306
   ```
   Replace `your_mysql_password` with your own password.

5. **Start the app:**
   ```
   python app.py
   ```

6. **Open** http://127.0.0.1:5000 in your browser.

## Using the App

The database starts empty. Add records with the forms in this order:

1. **Companies:** add a company first
2. **Jobs:** add a job linked to a company, with requirements as a JSON list such as `["Python", "SQL", "Flask"]`
3. **Applications:** add an application linked to a job
4. **Contacts:** add a contact linked to a company

Job Match needs jobs that have requirements in order to produce results.

## Important Notes

- **Run `schema.sql` only on a new database.** If the tables already exist it will fail with "table already exists." To start over, drop the database first, then run `schema.sql` again:
  ```sql
  DROP DATABASE job_tracker;
  ```
- **Never commit your `.env` file.** It contains your database password and is listed in `.gitignore`. Each person creates their own.
- Jobs cannot be deleted while applications are linked to them. Delete or update those applications first.

## Job Match

Enter skills separated by commas, such as `Python, SQL, Flask`. Each job's
requirements (stored as a JSON list) are compared to your skills, case-insensitively.
Jobs are ranked by the percentage of requirements you meet, and any skills you
are missing are listed.

For example, if a job requires Python, SQL, and Flask and you enter all three,
it shows as 100% (3/3 skills). A job requiring Python, SQL, and Excel shows as
67% (2/3 skills) with Excel listed as missing.

## Project Structure

```
Job-Application-Tracker/
├── app.py            # Flask application and routes
├── schema.sql        # Database creation script
├── requirements.txt  # Python dependencies
├── AI_USAGE.md       # Documentation of AI tool usage
├── README.md         # This file
├── static/
│   └── style.css     # Styling
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── companies.html
    ├── jobs.html
    ├── applications.html
    ├── contacts.html
    └── job_match.html
```

## Technologies
Python 3, Flask, MySQL, mysql-connector-python, python-dotenv, HTML, CSS

## AI Usage
AI tools were used during development. See [AI_USAGE.md]