@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo Ambiente Python nao encontrado. Execute iniciar.bat primeiro.
    exit /b 1
)

"%PYTHON%" -c "import locust" >nul 2>&1
if errorlevel 1 (
    echo Instalando o Locust no ambiente da API...
    "%PYTHON%" -m pip install locust
    if errorlevel 1 exit /b 1
)

if not defined TASKLAB_TOKEN (
    set /p "TASKLAB_TOKEN=Cole o access_token da conta de teste: "
)
if not defined TASKLAB_TOKEN (
    echo O token e necessario para testar GET /tasks.
    exit /b 1
)

"%PYTHON%" -m locust -f load_tests/locustfile.py --host http://127.0.0.1:8000 %*
exit /b %errorlevel%