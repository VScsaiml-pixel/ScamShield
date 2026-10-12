@echo off
title ScamShield AI - Single Localhost Server
echo ================================================================
echo   ScamShield AI - Starting Unified Localhost Application
echo ================================================================
echo.
cd /d "%~dp0"
backend\venv\Scripts\python.exe run_app.py
pause
