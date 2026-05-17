@echo off
REM Federated Learning - Dependency Installation Script
REM Run this to install all required Python packages

echo ========================================================
echo Installing Federated Learning Dependencies
echo ========================================================
echo.

echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing packages from requirements.txt...
python -m pip install -r requirements.txt

echo.
echo ========================================================
echo Installation Complete!
echo ========================================================
echo.
echo Next steps:
echo.
echo Open 4 terminals and run:
echo   Terminal 1: python server/server.py
echo   Terminal 2: python clients/client.py 0
echo   Terminal 3: python clients/client.py 1
echo   Terminal 4: python clients/client.py 2
echo.
pause
