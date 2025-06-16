@ECHO ON

@echo [[setting path]]
@set my_path=%0%
@set my_path=%my_path:\windows\install.bat=%

@echo path = %my_path%
cd %my_path%

@echo [[doing checks]]
@if not exist reel_logger\ (
  @echo reel_logger directory is missing
  @pause
  @exit
)

where python >nul 2>nul
@IF NOT ERRORLEVEL 0 (
  @echo python not found in path. Please install it
  @pause
  @exit
)

where ffmpeg >nul 2>nul
@IF NOT ERRORLEVEL 0 (
  @echo ffmpeg not found in path. Please install it
  @pause
  @exit
)

net session >nul 2>&1
@if not %errorLevel% == 0 (
  @echo please run as admin
  @pause
  @exit
)

@echo [[starting python venv]]
set python=%my_path%\venv\Scripts\python.exe
set pip=%my_path%\venv\Scripts\pip.exe
@if not exist %python% (
  pause
  @echo making venv
  python -m venv venv
)
%pip% install -r requirements.txt

@echo [[creating settings]]
set secret=reel_logger/secret.toml
::cp reel_logger\template_secret.toml %secret%

@echo # mandatory settings for django >  %secret%
@echo [django] >>  %secret%
@echo debug = true >>  %secret%
@echo secret_key = 'django-insecure' >>  %secret%
@echo media_path = '%my_path%\media' >>  %secret%
@echo allowed_hosts = ['*', '.localhost', '127.0.0.1', '[::1]'] >>  %secret%
@echo # defines database settings >>  %secret%
@echo # optional : sqlite3 is used by default >>  %secret%
@echo [database] >>  %secret%
@echo user = "myuser" >>  %secret%
@echo password = "mypassword" >>  %secret%

@echo change the settings NOW in secret.toml, then continue
@pause

@echo [[create database]]
cd reel_logger

%python% manage.py migrate

@echo [[collect static files]]

%python% manage.py collectstatic

@echo [[configure firewall]]

set PORT=8000
set RULE_NAME="Open Port %PORT%"

netsh advfirewall firewall show rule name=%RULE_NAME% >nul
if not ERRORLEVEL 1 (
    rem Rule %RULE_NAME% already exists.
    echo Hey, you already got a out rule by that name, you cannot put another one in!
) else (
    echo Rule %RULE_NAME% does not exist. Creating...
    pause
    netsh advfirewall firewall add rule name=%RULE_NAME% dir=in action=allow protocol=TCP localport=%PORT%
)

@echo server is set up
@pause