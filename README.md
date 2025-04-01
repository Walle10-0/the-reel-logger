# the-reel-logger
A tool for logging and storing video and audio footage.

# How to run the thing

## Step 1:  

Start a virtual environment for python  

`python -m venv venv`

## Step 2

Activate the virtual environment  

Windows:  
```
# In cmd.exe
venv\Scripts\activate.bat
# In PowerShell
venv\Scripts\Activate.ps1
```

Linux:  
`source venv/bin/activate`

## Step 3:  

Install requirements  

`pip install -r requirements.txt`

## Step 4:

copy `/reel_logger/template_secret.toml` as `/reel_logger/secret.toml`  

## Step 5:  

Enter appropriate `secret_key` and `media_path` into `secret.toml`  

## Step 6 (option 1):

Enter mySQL credentials into `secret.toml` under `database`  

## Step 6 (option 2):

In `/reel_logger/reel_logger/settings.py` in the `DATABASES` dictionary, swap the keys `default` and `alternative`  
(You may delete the old `default` settings)

## Step 7:  

Move into `reel_logger` directory

`cd reel_logger`

## Step 7:  

create database

`python manage.py migrate`

## Step 8 (optional):  

create admin user

`python manage.py createsuperuser`

## Step 9:  

run server

`python manage.py runserver`
