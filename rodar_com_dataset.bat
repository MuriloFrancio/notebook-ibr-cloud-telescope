@echo off
setlocal

cd /d "%~dp0"

echo ============================================
echo Cloud Telescope Lab - Dataset 3
echo ============================================
echo.

set /p DATASET_DIR=Digite o caminho da pasta onde esta o Dataset 3: 
set /p DATASET_ZIP_PASSWORD=Digite a senha do Dataset 3: 

if not exist "%DATASET_DIR%\cloud_telescope_raw_dataset_3.zip" (
    echo.
    echo ERRO: O arquivo cloud_telescope_raw_dataset_3.zip nao foi encontrado em:
    echo %DATASET_DIR%
    echo.
    echo Informe a PASTA onde o arquivo ZIP esta localizado.
    pause
    exit /b 1
)

if not exist "%CD%\resultados" (
    mkdir "%CD%\resultados"
)

echo.
echo Atualizando imagem Docker...
docker pull murilofrancio770/ibr-notebook:latest

if errorlevel 1 (
    echo.
    echo ERRO: Nao foi possivel obter a imagem Docker.
    pause
    exit /b 1
)

echo.
echo Iniciando Cloud Telescope Lab...
echo.

docker run --rm -it ^
    --name ibr-notebook ^
    -p 8888:8888 ^
    --cap-add NET_RAW ^
    --cap-add NET_ADMIN ^
    -v "%CD%\resultados:/home/jovyan/ibr-notebook/resultados" ^
    -v "%DATASET_DIR%:/home/jovyan/dataset:ro" ^
    -e "DATASET_ZIP_PASSWORD=%DATASET_ZIP_PASSWORD%" ^
    -e "DATASET_ZIP_PATH=/home/jovyan/dataset/cloud_telescope_raw_dataset_3.zip" ^
    murilofrancio770/ibr-notebook:latest

pause
