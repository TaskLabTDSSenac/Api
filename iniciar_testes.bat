@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Ambiente virtual nao encontrado. Prepare a .venv conforme o README.
    pause
    exit /b 1
)

echo Conferindo e instalando dependencias de testes...
".venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
if errorlevel 1 (
    echo Nao foi possivel instalar as dependencias.
    pause
    exit /b 1
)

echo.
echo Executando testes com SQLite temporario, sem iniciar o Uvicorn...
".venv\Scripts\python.exe" -m pytest -v
set "TEST_EXIT_CODE=%ERRORLEVEL%"
echo.
echo Codigo de saida do pytest: %TEST_EXIT_CODE%
echo O CT-02 deve falhar enquanto o defeito de senha curta estiver ativo.
pause
exit /b %TEST_EXIT_CODE%
