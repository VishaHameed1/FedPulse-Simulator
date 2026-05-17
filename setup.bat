@echo off
REM Create directory structure for Federated Learning project
mkdir model
mkdir utils  
mkdir server
mkdir clients
mkdir dashboard

echo Directories created successfully!
echo.
echo Next steps:
echo 1. Run: pip install -r requirements.txt
echo 2. In terminal 1: python server/server.py
echo 3. In terminal 2: python clients/client.py 0
echo 4. In terminal 3: python clients/client.py 1
echo 5. In terminal 4: python clients/client.py 2
