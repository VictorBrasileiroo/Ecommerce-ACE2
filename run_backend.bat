@echo off
cd /d "c:\Users\victo\Desktop\ACE2"
echo Iniciando servidor FastAPI...
"C:/Users/victo/Desktop/ACE2/.venv/Scripts/python.exe" -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8001
