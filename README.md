# 🎯 Attendance Management System

![Django](https://img.shields.io/badge/Django-5.2-green) ![License](https://img.shields.io/badge/License-MIT-blue) ![Python](https://img.shields.io/badge/Python-3.13-blue)

---

## 📑 Project Overview

**Attendance Management System** is a Django-based web application that allows employees to **mark attendance with live location**, while enabling admins to **manage, correct, and export** attendance data.
It supports **working hours management**, **CSV export**, **late marking detection**, and much more.

---

## ✨ Features

* 🔐 Secure Employee and Admin Login
* 🕘 Mark Attendance with Check-in and Check-out Times
* 📍 Location Capture (Latitude/Longitude)
* 🏢 Admin Dashboard for Monitoring
* 🛠️ Attendance Correction (Admin Rights)
* 📥 Export Attendance Data as CSV
* 📊 View Employees Present on Selected Date
* 🏢 Set Office Location & Working Hours
* 📄 Attendance History Per Employee
* ⚙️ Admin Manage Employees (Add/Edit/Delete)

---

## 🛠️ Tech Stack

* **Backend:** Django 5.2, Python 3.13
* **Frontend:** HTML, CSS, Bootstrap 5
* **Database:** SQLite3 (default)
* **Deployment Ready:** Render, PythonAnywhere, Railway

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/saurabhrmaurya/attandance_management_system.git
cd attandance_management_system
```

### 2. Create Virtual Environment

```bash
python -m venv env
```

Activate it:

* **Windows:**

  ```bash
  env\Scripts\activate
  ```
* **Mac/Linux:**

  ```bash
  source env/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Migrate Database

```bash
python manage.py migrate
```

### 5. Create Admin User

```bash
python manage.py createsuperuser
```

(Provide username, email, password.)

### 6. Run Server

```bash
python manage.py runserver
```

Access: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🔗 Important Routes

| URL Path                    | Description             |
| :-------------------------- | :---------------------- |
| `/`                         | Employee Login          |
| `/register/`                | Admin Register Employee |
| `/employee/dashboard/`      | Employee Dashboard      |
| `/masterdashboard/`         | Admin Dashboard         |
| `/mark/`                    | Mark Attendance         |
| `/employees_present/`       | View Attendance on Date |
| `/attendance/correct/<id>/` | Correct Attendance      |
| `/export-csv/`              | Export CSV Attendance   |

---

## 📷 Screenshots

> (Insert screenshots here if you want! I can help create a sample if you want.)

---

## ⚙️ Deployment Guide

You can deploy it easily on:

* [Render](https://render.com/)
* [PythonAnywhere](https://www.pythonanywhere.com/)
* [Railway](https://railway.app/)
* [Vercel](https://vercel.com/) (Serverless)

✅ Remember to update:

* `DEBUG = False`
* Proper `ALLOWED_HOSTS`
* Use `.env` file for secret keys

---

## 🛡️ Security & Best Practices

* Passwords are hashed securely (Django built-in).
* User permissions separated (Employee / Admin).
* CSRF Protection enabled.
* Server validation for all forms.

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute.

---

## ✨ Author

**Saurabh R. Maurya**
GitHub: [@saurabhrmaurya](https://github.com/saurabhrmaurya)

---

## 🙋‍♂️ Support

Found a bug or have an idea? Open an [Issue](https://github.com/saurabhrmaurya/attandance_management_system/issues).

---

# 🎉 Thank you for using Attendance Management System!

---

---

