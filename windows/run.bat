@ECHO ON

@echo [[setting path]]
@set my_path=%0%
@set my_path=%my_path:\windows\run.bat=%

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

@echo [[starting python venv]]
set python=%my_path%\venv\Scripts\python.exe
set pip=%my_path%\venv\Scripts\pip.exe
@if not exist %python% (
  @echo python venv not found.  Please fix that
  @pause
  @exit
)

@echo [[starting server]]
cd reel_logger

%python% manage.py runserver 0.0.0.0:8000

@echo server is set up
@pause