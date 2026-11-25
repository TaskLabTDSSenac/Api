@echo off
setlocal
cd /d "%~dp0"
set "TEST_FILE="
set "COVERAGE_SERVICE="

rem Parametros opcionais: test_file=arquivo.py coverage_service=auth_service
:parametros
if "%~1"=="" goto preparar
rem O CMD pode separar nome=valor em dois argumentos quando nao ha aspas.
if /i "%~1"=="test_file" goto arquivo_parametro
if /i "%~1"=="coverage_service" goto service_parametro
for /f "tokens=1,* delims==" %%A in ("%~1") do (
    if /i "%%A"=="test_file" (
        set "TEST_FILE=%%B"
    ) else if /i "%%A"=="coverage_service" (
        set "COVERAGE_SERVICE=%%B"
    ) else (
        echo Parametro desconhecido: %%A
        goto uso
    )
    if "%%B"=="" goto uso
)
shift
goto parametros

:arquivo_parametro
if "%~2"=="" goto uso
set "TEST_FILE=%~2"
shift
shift
goto parametros

:service_parametro
if "%~2"=="" goto uso
set "COVERAGE_SERVICE=%~2"
shift
shift
goto parametros

:preparar

if not exist ".venv\Scripts\python.exe" (
    echo Ambiente virtual nao encontrado. Prepare a .venv conforme o README.
    echo Use: py -3.12 -m venv .venv
    pause
    exit /b 1
)

rem Valida caminhos antes de instalar dependencias ou iniciar os testes.
".venv\Scripts\python.exe" -c "import os, pathlib, sys; root=pathlib.Path('tests/estruturais').resolve(); name=os.environ.get('TEST_FILE', ''); target=(root/name).resolve(); service=os.environ.get('COVERAGE_SERVICE', ''); valid_file=not name or (target.is_relative_to(root) and target.is_file() and target.suffix=='.py'); valid_service=not service or (service.isidentifier() and pathlib.Path('app/services', service+'.py').is_file()); sys.exit(0 if valid_file and valid_service else 1)"
if errorlevel 1 (
    echo Arquivo de teste ou service invalido.
    goto uso
)
set "TEST_TARGET=tests/estruturais/"
if defined TEST_FILE set "TEST_TARGET=tests/estruturais/%TEST_FILE%"
set "COVERAGE_TARGET=app.services"
if defined COVERAGE_SERVICE set "COVERAGE_TARGET=app.services.%COVERAGE_SERVICE%"

echo Conferindo e instalando dependencias de testes...
".venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
if errorlevel 1 (
    echo Nao foi possivel instalar as dependencias.
    pause
    exit /b 1
)

echo Testes: %TEST_TARGET%
echo Cobertura: %COVERAGE_TARGET%
".venv\Scripts\python.exe" -m pytest "%TEST_TARGET%" -v "--cov=%COVERAGE_TARGET%" --cov-branch --cov-report=term-missing --cov-report=html:htmlcov_estruturais
set "TEST_EXIT_CODE=%ERRORLEVEL%"
echo.
echo Codigo de saida do pytest: %TEST_EXIT_CODE%
echo Relatorio HTML: %~dp0htmlcov_estruturais\index.html
pause
exit /b %TEST_EXIT_CODE%

:uso
echo Uso: iniciar_testes_estruturais.bat [test_file=arquivo.py] [coverage_service=auth_service]
echo test_file: caminho relativo a tests/estruturais.
echo coverage_service: nome do arquivo em app/services, sem .py.
echo Sem parametros: todos os testes estruturais e cobertura de todos os services.
pause
exit /b 1
