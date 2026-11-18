from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import json
from database import get_db_connection

# Create the Flask application
app = Flask(__name__)



# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Totals for each table
    cursor.execute("""
        SELECT
            (SELECT COUNT(*) FROM companies)    AS companies,
            (SELECT COUNT(*) FROM jobs)         AS jobs,
            (SELECT COUNT(*) FROM applications) AS applications,
            (SELECT COUNT(*) FROM contacts)     AS contacts
    """)
    totals = cursor.fetchone()

    # Applications grouped by status
    cursor.execute("""
        SELECT status, COUNT(*) AS total
        FROM applications
        WHERE status IS NOT NULL
        GROUP BY status
    """)
    status_counts = {status: 0 for status in APPLICATION_STATUSES}
    for row in cursor.fetchall():
        status_counts[row["status"]] = row["total"]

    # Five most recent applications
    cursor.execute("""
        SELECT applications.application_date, applications.status,
               jobs.job_title, companies.company_name
        FROM applications
        INNER JOIN jobs ON applications.job_id = jobs.job_id
        INNER JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY applications.application_date DESC
        LIMIT 5
    """)
    recent = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        totals=totals,
        status_counts=status_counts,
        recent=recent
    )


# =========================================================
# COMPANIES
# =========================================================

# Companies page
@app.route("/companies")
def companies():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM companies ORDER BY company_name")
    companies = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("companies.html", companies=companies)


# Add a new company
@app.route("/companies/add", methods=["POST"])
def add_company():
    company_name = request.form["company_name"]
    industry = request.form.get("industry")
    website = request.form.get("website")
    city = request.form.get("city")
    state = request.form.get("state")
    notes = request.form.get("notes")

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO companies
        (company_name, industry, website, city, state, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (company_name, industry, website, city, state, notes))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("companies"))


# Edit an existing company
@app.route("/companies/edit/<int:company_id>", methods=["POST"])
def edit_company(company_id):
    company_name = request.form["company_name"]
    industry = request.form.get("industry")
    website = request.form.get("website")
    city = request.form.get("city")
    state = request.form.get("state")
    notes = request.form.get("notes")

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE companies
        SET company_name = %s,
            industry = %s,
            website = %s,
            city = %s,
            state = %s,
            notes = %s
        WHERE company_id = %s
    """, (company_name, industry, website, city, state, notes, company_id))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("companies"))


# Delete an existing company
@app.route("/companies/delete/<int:company_id>", methods=["POST"])
def delete_company(company_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM companies WHERE company_id = %s",
            (company_id,)
        )
        connection.commit()
    except mysql.connector.Error:
        connection.rollback()
        return (
            "This company cannot be deleted because it still has jobs or "
            "contacts linked to it. Delete those first.",
            400
        )
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("companies"))


# =========================================================
# JOBS
# =========================================================

# Validate job requirements JSON
def get_requirements():
    requirements = request.form.get("requirements", "[]").strip() or "[]"

    try:
        parsed_requirements = json.loads(requirements)

        if not isinstance(parsed_requirements, list):
            return None, "Requirements must be a JSON list, such as [\"Python\", \"SQL\"]."

        return json.dumps(parsed_requirements), None

    except json.JSONDecodeError:
        return None, "Invalid JSON. Example: [\"Python\", \"SQL\", \"Flask\"]"


# Jobs page
@app.route("/jobs")
def jobs():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            jobs.job_id,
            jobs.company_id,
            jobs.job_title,
            jobs.job_type,
            jobs.salary_min,
            jobs.salary_max,
            jobs.job_url,
            jobs.date_posted,
            jobs.requirements,
            companies.company_name
        FROM jobs
        INNER JOIN companies
            ON jobs.company_id = companies.company_id
        ORDER BY jobs.job_title
    """)

    jobs = cursor.fetchall()

    cursor.execute("""
        SELECT company_id, company_name
        FROM companies
        ORDER BY company_name
    """)

    companies = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "jobs.html",
        jobs=jobs,
        companies=companies
    )


# Add a new job
@app.route("/jobs/add", methods=["POST"])
def add_job():
    company_id = request.form["company_id"]
    job_title = request.form["job_title"]
    job_type = request.form["job_type"]
    salary_min = request.form.get("salary_min") or None
    salary_max = request.form.get("salary_max") or None
    job_url = request.form.get("job_url") or None
    date_posted = request.form.get("date_posted") or None

    requirements, error = get_requirements()

    if error:
        return error, 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO jobs
        (company_id, job_title, job_type, salary_min, salary_max,
         job_url, date_posted, requirements)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        company_id, job_title, job_type, salary_min, salary_max,
        job_url, date_posted, requirements
    ))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("jobs"))


# Edit an existing job
@app.route("/jobs/edit/<int:job_id>", methods=["POST"])
def edit_job(job_id):
    company_id = request.form["company_id"]
    job_title = request.form["job_title"]
    job_type = request.form["job_type"]
    salary_min = request.form.get("salary_min") or None
    salary_max = request.form.get("salary_max") or None
    job_url = request.form.get("job_url") or None
    date_posted = request.form.get("date_posted") or None

    requirements, error = get_requirements()

    if error:
        return error, 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE jobs
        SET company_id = %s,
            job_title = %s,
            job_type = %s,
            salary_min = %s,
            salary_max = %s,
            job_url = %s,
            date_posted = %s,
            requirements = %s
        WHERE job_id = %s
    """, (
        company_id, job_title, job_type, salary_min, salary_max,
        job_url, date_posted, requirements, job_id
    ))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("jobs"))


# Delete an existing job
@app.route("/jobs/delete/<int:job_id>", methods=["POST"])
def delete_job(job_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Check whether applications are linked to this job
    cursor.execute(
        "SELECT COUNT(*) FROM applications WHERE job_id = %s",
        (job_id,)
    )

    application_count = cursor.fetchone()[0]

    if application_count > 0:
        cursor.close()
        connection.close()

        return (
            "This job cannot be deleted because it has applications linked to it. "
            "Delete or update those applications first.",
            400
        )

    cursor.execute(
        "DELETE FROM jobs WHERE job_id = %s",
        (job_id,)
    )

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("jobs"))


# =========================================================
# APPLICATIONS
# =========================================================

APPLICATION_STATUSES = ["Applied", "Screening", "Interview", "Offer", "Rejected", "Withdrawn"]


# Validate optional interview data JSON
def get_interview_data():
    raw = request.form.get("interview_data", "").strip()

    if not raw:
        return None, None

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None, "Invalid JSON. Example: {\"round\": 1, \"interviewer\": \"Jane Smith\"}"

    if not isinstance(parsed, dict):
        return None, "Interview data must be a JSON object, such as {\"round\": 1}."

    return json.dumps(parsed), None


# Applications page
@app.route("/applications")
def applications():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            applications.application_id,
            applications.job_id,
            applications.application_date,
            applications.status,
            applications.resume_version,
            applications.cover_letter_sent,
            applications.interview_data,
            jobs.job_title,
            companies.company_name
        FROM applications
        INNER JOIN jobs ON applications.job_id = jobs.job_id
        INNER JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY applications.application_date DESC
    """)
    applications = cursor.fetchall()

    cursor.execute("""
        SELECT jobs.job_id, jobs.job_title, companies.company_name
        FROM jobs
        INNER JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY companies.company_name, jobs.job_title
    """)
    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "applications.html",
        applications=applications,
        jobs=jobs,
        statuses=APPLICATION_STATUSES
    )


# Add a new application
@app.route("/applications/add", methods=["POST"])
def add_application():
    job_id = request.form["job_id"]
    application_date = request.form["application_date"]
    status = request.form["status"]
    resume_version = request.form.get("resume_version", "").strip() or None
    cover_letter_sent = 1 if request.form.get("cover_letter_sent") == "1" else 0

    if status not in APPLICATION_STATUSES:
        return "Invalid status.", 400

    interview_data, error = get_interview_data()

    if error:
        return error, 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO applications
        (job_id, application_date, status, resume_version,
         cover_letter_sent, interview_data)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (job_id, application_date, status, resume_version,
          cover_letter_sent, interview_data))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("applications"))


# Edit an existing application
@app.route("/applications/edit/<int:application_id>", methods=["POST"])
def edit_application(application_id):
    job_id = request.form["job_id"]
    application_date = request.form["application_date"]
    status = request.form["status"]
    resume_version = request.form.get("resume_version", "").strip() or None
    cover_letter_sent = 1 if request.form.get("cover_letter_sent") == "1" else 0

    if status not in APPLICATION_STATUSES:
        return "Invalid status.", 400

    interview_data, error = get_interview_data()

    if error:
        return error, 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE applications
        SET job_id = %s,
            application_date = %s,
            status = %s,
            resume_version = %s,
            cover_letter_sent = %s,
            interview_data = %s
        WHERE application_id = %s
    """, (job_id, application_date, status, resume_version,
          cover_letter_sent, interview_data, application_id))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("applications"))


# Delete an existing application
@app.route("/applications/delete/<int:application_id>", methods=["POST"])
def delete_application(application_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM applications WHERE application_id = %s",
        (application_id,)
    )

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("applications"))


# =========================================================
# CONTACTS
# =========================================================

# Contacts page
@app.route("/contacts")
def contacts():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            contacts.contact_id,
            contacts.company_id,
            contacts.contact_name,
            contacts.title,
            contacts.email,
            contacts.phone,
            contacts.linkedin_url,
            contacts.notes,
            companies.company_name
        FROM contacts
        INNER JOIN companies ON contacts.company_id = companies.company_id
        ORDER BY contacts.contact_name
    """)
    contacts = cursor.fetchall()

    cursor.execute("""
        SELECT company_id, company_name
        FROM companies
        ORDER BY company_name
    """)
    companies = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("contacts.html", contacts=contacts, companies=companies)


# Add a new contact
@app.route("/contacts/add", methods=["POST"])
def add_contact():
    company_id = request.form["company_id"]
    contact_name = request.form["contact_name"].strip()
    title = request.form.get("title", "").strip() or None
    email = request.form.get("email", "").strip() or None
    phone = request.form.get("phone", "").strip() or None
    linkedin_url = request.form.get("linkedin_url", "").strip() or None
    notes = request.form.get("notes", "").strip() or None

    if not contact_name:
        return "Contact name is required.", 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO contacts
        (company_id, contact_name, title, email, phone, linkedin_url, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (company_id, contact_name, title, email, phone, linkedin_url, notes))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("contacts"))


# Edit an existing contact
@app.route("/contacts/edit/<int:contact_id>", methods=["POST"])
def edit_contact(contact_id):
    company_id = request.form["company_id"]
    contact_name = request.form["contact_name"].strip()
    title = request.form.get("title", "").strip() or None
    email = request.form.get("email", "").strip() or None
    phone = request.form.get("phone", "").strip() or None
    linkedin_url = request.form.get("linkedin_url", "").strip() or None
    notes = request.form.get("notes", "").strip() or None

    if not contact_name:
        return "Contact name is required.", 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE contacts
        SET company_id = %s,
            contact_name = %s,
            title = %s,
            email = %s,
            phone = %s,
            linkedin_url = %s,
            notes = %s
        WHERE contact_id = %s
    """, (company_id, contact_name, title, email, phone,
          linkedin_url, notes, contact_id))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("contacts"))


# Delete an existing contact
@app.route("/contacts/delete/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM contacts WHERE contact_id = %s",
        (contact_id,)
    )

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("contacts"))


# =========================================================
# JOB MATCH
# =========================================================

@app.route("/job-match")
def job_match():
    raw_skills = request.args.get("skills", "").strip()
    user_skills = [s.strip() for s in raw_skills.split(",") if s.strip()]
    user_lower = {s.lower() for s in user_skills}

    results = []

    if user_skills:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT jobs.job_id, jobs.job_title, jobs.requirements,
                   companies.company_name
            FROM jobs
            INNER JOIN companies ON jobs.company_id = companies.company_id
        """)
        jobs = cursor.fetchall()

        cursor.close()
        connection.close()

        for job in jobs:
            requirements = job["requirements"]

            # MySQL returns JSON columns as text
            try:
                if isinstance(requirements, (str, bytes)):
                    requirements = json.loads(requirements)
            except json.JSONDecodeError:
                continue

            # Also accept the object format from Assignment 7
            if isinstance(requirements, dict):
                requirements = requirements.get("required_skills", [])

            if not requirements:
                continue

            requirements = [str(r) for r in requirements]
            matched = [r for r in requirements if r.lower() in user_lower]
            missing = [r for r in requirements if r.lower() not in user_lower]

            if not matched:
                continue

            results.append({
                "job_title": job["job_title"],
                "company_name": job["company_name"],
                "matched": matched,
                "missing": missing,
                "total": len(requirements),
                "percent": round(len(matched) / len(requirements) * 100)
            })

        # Best match first; ties go to more matched skills, then title
        results.sort(key=lambda r: (-r["percent"], -len(r["matched"]), r["job_title"]))

    return render_template(
        "job_match.html",
        skills=raw_skills,
        user_skills=user_skills,
        results=results
    )


# =========================================================
# START THE APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)