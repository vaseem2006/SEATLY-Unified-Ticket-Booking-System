@echo off
echo Starting Ticket Booking App...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Stopping any existing server instances...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq FastAPI Server*" 2>nul
timeout /t 2 /nobreak >nul
echo.
echo Starting FastAPI server...
echo The browser will open automatically in a few seconds...
echo.
echo IMPORTANT: If you see the old design, press Ctrl+F5 in your browser to hard refresh!
echo.
start "FastAPI Server" python main.py
timeout /t 4 /nobreak >nul
start http://localhost:8000
echo.
echo Server is running in a separate window.
echo Browser has been opened to http://localhost:8000
echo.
echo To stop the server, close the "FastAPI Server" window.
echo.
echo TIP: Press Ctrl+F5 in your browser to see the latest changes!
echo.
pause

