@echo off
cd /d "%~dp0"
python serve.py stop
if errorlevel 1 pause
