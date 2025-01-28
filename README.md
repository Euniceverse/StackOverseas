# Team Stack Overseas Major Group project

## Team members
The members of the team are:
- Hayeong Lee (k21189777)
- Isabella Landgrebe (k)
- Chen Wang (k23008656)
- Saruta Kittipattananon (k)
- Nehir Bektas (k)
- Aishah Alharthi (k)

## Project structure
The project is called `uni_society`.  It consists of a single app `clubs`.

## Deployed version of the application
The deployed version of the application can be found at [*k2368571.pythonanywhere.com*](https://k2368571.pythonanywhere.com).

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Add or Install all required packages:

```
$ pip3 freeze > requirements.txt
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

## Sources
The packages used by this application are specified in `requirements.txt`
