@echo off
title Senac Tech - Microservices Manager
echo ==========================================
echo    INICIANDO MICROSSERVICOS Senac Tech
echo ==========================================

:: Inicia o Auth Service na porta 5000
start "Auth Service (5000)" cmd /k "cd services/auth_service && python run.py"
start "Auth Service (5001)" cmd /k "cd services/catalog_service && python run.py"
start "Auth Service (5002)" cmd /k "cd services/inventory_service && python run.py"
start "Auth Service (5003)" cmd /k "cd services/user_service && python run.py"