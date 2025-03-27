# Team Stack Overseas Major Group Project

## Team Members

The members of the team are:

•⁠  ⁠Aishah Alharthi (k21171579)
•⁠  ⁠Chen Wang (k23008656)
•⁠  ⁠Hayeong Lee (k21189777)
•⁠  ⁠Isabella Landgrebe (k23001579)
•⁠  ⁠Nehir Bektas (k21153319)
•⁠  ⁠Saruta Kittipattananon (k23047468)

## Project Repositories

### Project Code Repository
The full source code for the project is available at:
•⁠  ⁠HTTPS: [https://github.com/Euniceverse/StackOverseas.git](https://github.com/Euniceverse/StackOverseas.git)
•⁠  ⁠SSH: ⁠ git@github.com:Euniceverse/StackOverseas.git ⁠

### Project Report Repository
The project report and related documentation can be accessed at:
•⁠  ⁠HTTPS: [https://github.com/Aisha-Bassam/Stack-Overseas-Report.git](https://github.com/Aisha-Bassam/Stack-Overseas-Report.git)
•⁠  ⁠SSH: ⁠ git@github.com:Aisha-Bassam/Stack-Overseas-Report.git ⁠

## Deployed Version of the Application
The deployed version of the application can be found at [stackoverseas.onrender.com](https://stackoverseas.onrender.com/).

## Developer Setup Instructions

### 1. Introduction
This document provides step-by-step instructions on how to install, set up, and run the application in a development environment. The guide includes environment setup, dependencies installation, database migrations, and running the application.

### 2. Prerequisites
Ensure you have the following installed on your system before proceeding:
•⁠  ⁠Python (version 3.x)
•⁠  ⁠Git (if cloning from a repository)
•⁠  ⁠A terminal or command line interface
•⁠  ⁠A code editor (e.g., VS Code, PyCharm, Sublime Text)

### 3. Installation
#### Option 1: Clone from GitHub
Windows / Mac / Linux:
⁠ sh
git clone https://github.com/Euniceverse/StackOverseas.git
# or
git clone git@github.com:Euniceverse/StackOverseas.git
cd StackOverseas
 ⁠

#### Option 2: Unzip the provided file
Download and extract the .zip file. Navigate to the extracted folder in your terminal.

### 4. Set Up Virtual Environment
#### Windows:
⁠ sh
python -m venv venv
venv\Scripts\activate
 ⁠

#### Mac/Linux:
⁠ sh
python3 -m venv venv
source venv/bin/activate
 ⁠

### 5. Install Dependencies
⁠ sh
pip install -r requirements.txt
# or
pip3 install -r requirements.txt
 ⁠

### 6. Apply Database Migrations
⁠ sh
python manage.py makemigrations
python manage.py migrate
# or
python3 manage.py makemigrations
python3 manage.py migrate
 ⁠

### 7. Seed the Database
⁠ sh
python config/seed.py
# or
python3 config/seed.py
 ⁠

### 8. Run the Server
Start the development server at http://127.0.0.1:8000/
⁠ sh
python manage.py runserver
# or
python3 manage.py runserver
 ⁠

If you face errors trying to run the server, try running the following command:
⁠ sh
python manage.py createcachetable activation_cache_table
 ⁠

### 9. Testing Instructions
#### Running All Tests
⁠ sh
python manage.py test
# or
python3 manage.py test
 ⁠

#### Running Specific Test Modules
⁠ sh
python manage.py test config.tests
 ⁠

To run tests for a specific file:
⁠ sh
python manage.py test config.tests.test_<specific_file>
 ⁠

To run tests for a specific app inside StackOverseas:
⁠ sh
python manage.py test apps.<app_name>
 ⁠

### 10. Deactivating the Virtual Environment
⁠ sh
deactivate
 ⁠

### 11. Retrieving User Credentials
#### Admin Credentials
•⁠  ⁠Email: admin@example.ac.uk
•⁠  ⁠Password: password123

#### User Credentials
The password for all populated users is ⁠ password123 ⁠.

##### Best Recommended Method
Query the ⁠ db.sqlite3 ⁠ file directly using:
•⁠  ⁠A terminal (⁠ sqlite3 db.sqlite3 ⁠ and relevant SQL queries)
•⁠  ⁠Online SQL file viewers such as SQLite Viewer

##### Alternative Method
Log in as an admin and navigate to ⁠ Societies → All Members ⁠ to retrieve any user's email address.

### Additional Notes
When facing migration or database errors, it is advised to:
1.⁠ ⁠Delete the migration files inside the ⁠ migrations ⁠ folder (except ⁠ __init__.py ⁠).
2.⁠ ⁠Delete the ⁠ db.sqlite3 ⁠ file.
3.⁠ ⁠Run:
⁠ sh
python manage.py flush
 ⁠
4.⁠ ⁠Redo the migration and seeding steps:
⁠ sh
python manage.py makemigrations
python manage.py migrate
python config/seed.py
 ⁠

## Sources
The packages used by this application are specified in ⁠ requirements.txt ⁠.

## Screencast
Two screencasts have been submitted:
•⁠  ⁠demonstrating the deployed version
•⁠  ⁠demonstrating the local version