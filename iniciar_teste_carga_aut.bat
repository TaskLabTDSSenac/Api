@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_CARGA=.venv\Scripts\python.exe"

if not exist "%PYTHON_CARGA%" (
    echo Ambiente Python nao encontrado. Prepare a .venv da API primeiro.
    pause
    exit /b 1
)

"%PYTHON_CARGA%" -c "import locust" >nul 2>&1
if errorlevel 1 (
    echo Instalando o Locust no ambiente da API...
    "%PYTHON_CARGA%" -m pip install locust==2.47.0
    if errorlevel 1 (
        echo Falha ao instalar o Locust.
        pause
        exit /b 1
    )
)

if not defined TASKLAB_TOKEN echo Cole o token quando solicitado e pressione Enter.
echo A API precisa estar rodando em outro terminal.
"%PYTHON_CARGA%" load_tests_automatizados\executar_carga.py %*
set "CARGA_EXIT_CODE=%ERRORLEVEL%"
echo.
echo Codigo de saida: %CARGA_EXIT_CODE%
pause
exit /b %CARGA_EXIT_CODE%
