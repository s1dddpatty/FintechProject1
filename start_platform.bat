@echo off
title Fintech Platform - Master Launcher
echo ========================================================
echo        FINTECH PLATFORM (BACKEND + FRONTEND)
echo ========================================================
echo.

echo Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Fintech FastAPI Backend" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo Starting Next.js Frontend on http://localhost:3000 ...
start "Fintech Next.js Frontend" cmd /k "cd /d %~dp0frontend && npm run dev -- -p 3000"

echo.
echo ========================================================
echo Both servers are launching in separate external windows!
echo Backend:  http://127.0.0.1:8000/docs
echo Frontend: http://localhost:3000/pipeline
echo ========================================================
echo You can keep this launcher or close it.
pause
