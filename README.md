# :bookmark_tabs: LitReview :bookmark_tabs:

Django Web App for book reviews on demand.

***
## Table of Contents
1. [General Info](#general-info)
2. [Technologies](#technologies)
3. [Installation](#installation)

### :newspaper: General Info :newspaper:
***
This is an OpenClassrooms student Django project. 
The objective is to allow users to make requests for book reviews or to publish them. 
They can also follow users and see their reviews or requests.
Here is required a functional application with a simple front according to wireframes.

### :briefcase: Technologies :briefcase:
*** 
- [Django](https://pypi.org/project/Django/4.2/): Version 4.2
- [Python](https://www.python.org/): Version 3.10.7
- [Pip](https://pypi.org/project/pip/): Version 23.0
- [Flake8](https://pypi.org/project/flake8/): Version 6.0.0
- [Flake8-html](https://pypi.org/project/flake8-html/): Version 0.4.3
- [Pillow](https://pypi.org/project/Pillow/): Version 9.5.0
- HTML5 + CSS3

### :wrench: Installation :wrench:
***
In your directory for the project:

Clone repository from:
- https://github.com/SpiritF0rest/OC_Python_P9_LitReview

### :wrench: Virtual environment creation and use :wrench:

```
In terminal from cloned folder :
$ python3 -m venv env

To active the virtual environment:
$ source env/bin/activate

To install modules: 
$ pip install -r requirements.txt

To run server:
$ python3 manage.py runserver

To deactive the virtual environment: 
$ deactivate
```

Warning, for the prerequisites of the evaluation of the student project, db.sqlite3 and media directory are not in .gitignore file.

### :wrench: Migrations :wrench:

```
To create a migration after modifying the models
$ python3 manage.py makemigrations

To apply migrations
$ python3 manage.py migrate
```

### :mag_right: Generate a new flake8 html :mag_right:

```
From cloned folder after activate the virtual environment:
$ flake8
```

### :red_haired_man: Test user :red_haired_man:

There are 3 test users whose usernames are:
- yohan
- daniel
- gael
***
The password for these accounts is : 1234Aze!

***

:snake: Enjoy :snake:
