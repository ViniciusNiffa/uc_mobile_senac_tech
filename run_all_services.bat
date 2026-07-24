@echo off
title Senac Tech - Microservices Manager
echo ==========================================
echo    INICIANDO MICROSSERVICOS Senac Tech
echo ==========================================

:: Inicia o Auth Service na porta 5000
start "Auth Service (5000)" cmd /k "cd services/auth_service && python run.py"