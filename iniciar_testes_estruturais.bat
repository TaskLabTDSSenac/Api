@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Ambiente virtual nao encontrado. Prepare a .venv conforme o README.
    exit /b 1
)

set "TEST_FILE="
set "COVERAGE_SERVICE="
:parse_args
if "%~1"=="" goto args_done
for /f "tokens=1,* delims==" %%K in ("%~1") do (
    if /i "%%K"=="test_file" set "TEST_FILE=%%L"
    if /i "%%K"=="coverage_service" set "COVERAGE_SERVICE=%%L"
)
shift
goto parse_args
:args_done
if not defined TEST_FILE set "TEST_FILE=test_task_service_kennedy.py"
if not defined COVERAGE_SERVICE set "COVERAGE_SERVICE=task_service"

if not exist "tests\estruturais\%TEST_FILE%" (
    echo Teste nao encontrado: tests\estruturais\%TEST_FILE%
    exit /b 2
)

if /i not "%COVERAGE_SERVICE%"=="task_service" if /i not "%COVERAGE_SERVICE%"=="auth_service" if /i not "%COVERAGE_SERVICE%"=="user_service" (
    echo Service de cobertura invalido. Use task_service, auth_service ou user_service.
    exit /b 2
)

echo Conferindo dependencias de testes...
".venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
if errorlevel 1 exit /b 1

echo.
echo Executando tests\estruturais\%TEST_FILE% com cobertura de app.services.%COVERAGE_SERVICE%...
".venv\Scripts\python.exe" -m pytest "tests\estruturais\%TEST_FILE%" -v --cov="app.services.%COVERAGE_SERVICE%" --cov-branch --cov-report=term-missing --cov-report=html:htmlcov_estruturais
set "TEST_EXIT_CODE=%ERRORLEVEL%"
echo.
echo Codigo de saida do pytest: %TEST_EXIT_CODE%
exit /b %TEST_EXIT_CODE%


