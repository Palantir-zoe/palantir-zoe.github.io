@echo off
cd /d "%~dp0"
python serve.py start --open
if errorlevel 1 pause
