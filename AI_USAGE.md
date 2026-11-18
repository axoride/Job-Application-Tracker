# AI Usage Documentation

## Tools Used
- **ChatGPT:** Initial Flask setup, HTML templates, CSS styling, and Git guidance.
- **Claude:** Job Match percentage calculation, Contacts CRUD, Dashboard statistics, SQL troubleshooting, and documentation.

## Key Prompts
1. "Write a Flask route to display all jobs with company names using a JOIN."
2. "Debug this error: MySQL Error 1452 – Cannot add or update a child row: a foreign key constraint fails."
3. "Create a Job Match function that calculates skill match percentage"
4. "Review my Flask code and help identify errors that prevent the application from working correctly."

## What Worked Well
- AI helped create Flask routes, and HTML templates for CRUD operations.
- AI explained errors and helped troubleshoot database issues.
- AI assisted in implementing the Job Match feature by helping with the calculation of skill match percentages and identifying missing skills.
- AI provided suggestions for improving the Dashboard and organizing the application.

## What I Modified
- Adjusted AI-generated SQL queries and variable names to match my database schema.
- Changed sample data to match the required ENUM values and table structure.
- Customized the CSS with a simple dark theme inspired by GTA VI.
- Rearranged the Dashboard layout and organized `app.py` with section comments.
- Tested generated code and corrected issues when necessary.

## Mistakes I Found
- Some AI suggestions were based on assumptions about my database that were not correct.
- One suggested code example used `flash()` without importing it.
- AI generated code needed more testing before it worked as expected.

## Lessons Learned
- Always test AI-generated code instead of assuming it will work.
- AI is useful for repetitive code and troubleshooting, but its output often needs adjustments.
- Understanding the code is important since Ai is prone to making mistakes that can affect applications.