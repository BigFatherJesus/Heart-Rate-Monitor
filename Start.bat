@echo off

REM Create a virtual environment
python -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate

REM Install the required libraries
pip install matplotlib scipy pyserial pyfirmata2 customtkinter

REM Run the python script
python "Final Assignment.py"

pause