# Sky Engineering Teams Portal
5COSC021W Software Development Group Project | CWK2 | University of Westminster

## What is this

This is a Django web app built for Sky's Global Apps Engineering department. The idea is to replace a spreadsheet that the team was using to track engineering teams, managers, departments, dependencies and repositories. Everything is now in one place and anyone with a portal account can find what they need without having to ask someone or dig through a shared Excel file.

## What it does

- Browse and search all engineering teams, filter by name or department
- View full team details including members, roles, skills, repositories and dependencies
- Send messages to other users through a built-in inbox system
- Schedule meetings with a monthly and weekly calendar view
- See the org chart showing how departments and teams fit together
- Generate reports on team data and download them as PDF or Excel
- Register an account, log in, update your profile and change your password
- Admin panel for managing all the data

## Who built what

| Student | Module |
|---|---|
| Marc Fernandes (W2081572) | Team Management |
| Ehsaan Zakriya (W2115831) | Organisation and Department |
| Amran Mohammed (W2066724) | Messages |
| Ibrahim Chowdhury (W1905510) | Schedule |
| Sadana Suresh (W21162895) | Reports |

## Tech stack

- Python 3, Django 4.2.10
- SQLite
- Bootstrap 5, Bootstrap Icons, Roboto font
- Git and GitHub for version control
- ReportLab and openpyxl for PDF and Excel exports

## How to run it

**1. Clone the repo**
```bash
git clone https://github.com/Amran1700/Software_Development_GP_CWK2.git
cd Software_Development_GP_CWK2
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run migrations**
```bash
python manage.py migrate
```

**5. Load sample data**
```bash
python manage.py loaddata superadmins.json
python manage.py loaddata organisation_feature/fixtures/organisation_data.json
python manage.py loaddata organisation_feature/fixtures/teams_data.json
python manage.py loaddata messages_feature/fixtures/fixtures.json
```

**6. Start the server**
```bash
python manage.py runserver
```

**7. Open the app**

Go to http://127.0.0.1:8000

## Login credentials

**Superuser (admin access)**
- Username: admin
- Password: admin123

**Regular test user**
- Username: testuser
- Password: testpass123

The admin panel is at http://127.0.0.1:8000/admin

## Notes

- The database file db.sqlite3 is included in the submission with sample data already loaded. If you want to start fresh, delete it and run the migrations and loaddata commands above.
- If you see W042 warnings when running tests that is expected, it is just other modules not setting default_auto_field and does not affect anything.
- All 24 automated tests for the Reports module pass. Run them with: `python manage.py test reports_feature`
