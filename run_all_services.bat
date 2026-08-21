@echo off
title Senac Tech - Microservices Manager
echo ==========================================
echo    INICIANDO MICROSSERVICOS Senac Tech
echo ==========================================

:: Inicia o Auth Service na porta 5000
start "Auth Service (5000)" cmd /k "cd services/auth_service && C:\Python312\python.exe run.py"
:: Inicia o User Service na porta 5003
start "User Service (5003)" cmd /k "cd services/user_service && C:\Python312\python.exe run.py"