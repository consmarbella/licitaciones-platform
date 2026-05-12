@echo off
echo Licitaciones Platform - Dropshipping al Estado
echo ==============================================
python -m pip install -r requirements.txt > nul 2>&1
echo Iniciando servidor...
echo Abri http://localhost:5000 en tu navegador
python app.py
pause
