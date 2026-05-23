@echo off
cd /d "E:\class\ComputerNetworkDesign"
echo CWD: %cd%
echo Python: %~dp0
echo.
echo === Testing imports ===
python -c "from scanner import TCPScanner, ScanConfig; print('Imports OK')"
echo.
echo === Launching GUI ===
python -c "import gui; gui.PortScannerGUI().run()"
echo.
echo GUI exited. Exit code: %ERRORLEVEL%
pause
