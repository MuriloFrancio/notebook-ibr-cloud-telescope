@echo off
echo ============================================
echo IBR Notebook - Execucao com Dataset 3
echo ============================================
echo.

set /p DATASET_DIR=Digite o caminho da pasta onde esta o Dataset 3: 
set /p DATASET_ZIP_PASSWORD=Digite a senha do Dataset 3: 

if not exist "%DATASET_DIR%\cloud_telescope_raw_dataset_3.zip" (
  echo.
  echo ERRO: O arquivo cloud_telescope_raw_dataset_3.zip nao foi encontrado em:
  echo %DATASET_DIR%
  echo.
  echo Verifique se voce informou a PASTA correta, nao o arquivo ZIP.
  pause
  exit /b 1
)

docker run --rm -it -p 8888:8888 ^
  --cap-add NET_RAW ^
  --cap-add NET_ADMIN ^
  -v "%DATASET_DIR%:/home/jovyan/ibr-notebook/dataset:ro" ^
  -e "DATASET_ZIP_PASSWORD=%DATASET_ZIP_PASSWORD%" ^
  -e "DATASET_ZIP_PATH=/home/jovyan/ibr-notebook/dataset/cloud_telescope_raw_dataset_3.zip" ^
  murilofrancio770/ibr-notebook:latest

pause