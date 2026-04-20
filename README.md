# Sky Engineering Teams Portal
### 5COSC021W – Software Development Group Project | CWK2

A Django web application built for Sky's Engineering Department to replace a manual Excel spreadsheet with a centralised, database-driven portal for discovering and managing engineering teams.

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
