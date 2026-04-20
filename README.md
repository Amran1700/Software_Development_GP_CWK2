# Sky Engineering Teams Portal
### 5COSC021W – Software Development Group Project | CWK2
## Project Overview

The Sky Engineering Teams Portal is a full-stack web application developed as part of the 5COSC021W Software Development Group Project module at the University of Westminster. The application was built for Sky's Global Apps Engineering department to replace a manually maintained Excel spreadsheet that listed all engineering teams, their managers, departments, upstream and downstream dependencies, code repositories and contact details.

The portal provides a centralised, database-driven interface where authenticated users can search for engineering teams, view detailed team information, send messages, schedule meetings, visualise the organisational structure, and generate reports. The system supports team lifecycle management — including new teams being created, teams being restructured, and teams being disbanded — and ensures all information is up to date and accessible across the organisation.

## What the Application Does

- **Browse and search** all engineering teams across departments with real-time filtering by team name and department
- **View full team details** including team purpose, description, manager, all team members with roles and contact details, linked code repositories, skills with proficiency levels, and upstream and downstream team dependencies
- **Send internal messages** to teams and individuals through a built-in messaging system with inbox, sent, drafts and compose functionality
- **Schedule and manage meetings** with a calendar view showing monthly and weekly schedules, platform selection and attendee management
- **Visualise organisational structure** through an interactive org chart showing how departments and teams relate to each other
- **Generate reports** on team data including total teams by department, teams without managers, and summary statistics — exportable as PDF or Excel
- **Self-register and manage accounts** with local user registration, login, profile update and password change functionality
- **Django Admin panel** for full data management including adding teams, managing members, assigning skills and setting dependencies

## What Was Developed

The application was built using Django 6.0 with a SQLite database and Bootstrap 5 frontend. Development followed an Agile approach with weekly sprints tracked on Trello. Each of the five group members was responsible for implementing one module of the application individually, with shared responsibility for the database design, user authentication, admin panel and global navigation. All five modules were integrated into a single application through a shared base template and connected database.
---

## Group Members

| Student | Module |
|---|---|
| Student 1 (W2081572) | Team Management |
| Student 2 | Organisation & Department |
| Student 3 | Messages |
| Student 4 | Schedule |
| Student 5 | Reports |

---

## Tech Stack

- **Backend:** Python 3, Django 6.0
- **Database:** SQLite
- **Frontend:** Bootstrap 5, Bootstrap Icons, Roboto font
- **Version Control:** Git / GitHub

---

## Features

- **Team Management** — Browse all engineering teams, search by name or department, view full team details including members, skills, repositories and dependencies
- **Organisation & Department** — Org chart visualisation, department list and detail pages
- **Messages** — Internal messaging with inbox, sent, drafts and compose
- **Schedule** — Create and manage meetings with monthly and weekly calendar views
- **Reports** — Generate PDF and Excel reports on team data

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

**1 — Clone the repository:**
```bash
git clone https://github.com/Amran1700/Software_Development_GP_CWK2.git
cd Software_Development_GP_CWK2
```

**2 — Create and activate a virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3 — Install dependencies:**
```bash
pip install -r requirements.txt
```

**4 — Run migrations:**
```bash
python manage.py migrate
```

**5 — Load sample data:**
```bash
python manage.py loaddata superadmins.json
python manage.py loaddata organisation_feature/fixtures/organisation_data.json
python manage.py loaddata organisation_feature/fixtures/teams_data.json
```

**6 — Run the server:**
```bash
python manage.py runserver
```

**7 — Visit the app:**
