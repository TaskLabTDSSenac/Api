@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Criando o ambiente virtual...
    py -3.12 -m venv .venv
    if errorlevel 1 goto erro
)

echo Conferindo e instalando dependencias...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto erro

echo.
echo Swagger: http://127.0.0.1:8000/docs
echo Para encerrar, pressione Ctrl+C.
echo.

".venv\Scripts\python.exe" -m uvicorn app.main:app --reload
if errorlevel 1 goto erro
exit /b 0

:erro
echo.
echo Nao foi possivel iniciar a API.
echo Confira a mensagem acima e se o Python 3.12 esta instalado.
pause
exit /b 1