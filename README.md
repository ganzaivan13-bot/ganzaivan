# Ganza Ivan — Web Developer Portfolio

A Flask portfolio website with a customer booking form and a private admin dashboard.

## 1. Requirements
- Python 3.10 or newer
- VS Code (recommended)

## 2. Install and run on Windows PowerShell

Open this project folder in VS Code, then open the terminal:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation, use the virtual environment's Python directly:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:ADMIN_PASSWORD="Choose-A-Strong-Private-Password"
$env:SECRET_KEY="replace-this-with-a-long-random-secret"
.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000 in your browser.

## 3. Admin dashboard

Visit http://127.0.0.1:5000/admin/login and sign in with the `ADMIN_PASSWORD` you set in the terminal. Booking requests appear at `/admin`. Keep this password private.

## 4. Database

By default, SQLite stores submissions in `bookings.db` in the project folder. Each booking stores the customer's name, optional company, email, phone, selected service, preferred date/time, project description, status and submission timestamp.

## 5. Before publishing online

- Set a long random `SECRET_KEY`.
- Set a strong `ADMIN_PASSWORD` (or `ADMIN_PASSWORD_HASH`).
- Turn off Flask debug mode; do not run with `FLASK_DEBUG=1` in production.
- Use HTTPS and a trusted hosting provider.
- Configure persistent storage or PostgreSQL for production. Some hosting platforms erase local SQLite files when redeploying.
- Add a privacy notice and collect only information you need.
- Do not collect card numbers, CVV codes or passwords through this form. Use a trusted payment provider if you later accept payments.

## 6. Customise

Edit `templates/index.html` to update the biography, services or contact links. The current biography is intentionally general and does not claim qualifications or client results that have not been supplied.


## Languages
The public portfolio includes an English / Kinyarwanda switch (EN / RW) in the navigation. The selected language is saved in the visitor's browser. Booking field names and visible options are translated; submitted service values remain consistent in the database.
