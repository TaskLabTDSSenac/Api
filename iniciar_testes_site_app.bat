@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Ambiente virtual nao encontrado. Prepare a .venv conforme o README.
    pause
    exit /b 1
)

echo Iniciando a API para os testes do Site...
echo O banco tasklab_web_testes.db sera zerado nesta execucao.
echo O banco principal tasklab.db sera preservado.
".venv\Scripts\python.exe" scripts\iniciar_api_testes_site.py
set "API_EXIT_CODE=%ERRORLEVEL%"
if not "%API_EXIT_CODE%"=="0" (
    echo.
    echo Nao foi possivel iniciar. Confira a mensagem acima.
    pause
)
exit /b %API_EXIT_CODE%
