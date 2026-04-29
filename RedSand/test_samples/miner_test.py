#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST MALWARE SAMPLE - MINER SIMULATION
Это тестовый образец криптомайнера для проверки антивируса
НЕ ЯВЛЯЕТСЯ РЕАЛЬНЫМ ВРЕДОНОСНЫМ ПО
"""

THREAT_TYPE: MINER
GENERATED: 2024-01-01
RANDOM_ID: TEST_MINER_001

[MALICIOUS_INDICATORS]
- Cryptocurrency mining
- Pool connection
- Resource hijacking

[SIGNATURE]
MINER_TEST_SIGNATURE_V1

def connect_to_pool():
    """Подключение к майнинг пулу"""
    print("Connecting to mining pool...")
    
    # Stratum протокол
    pool_url = "stratum+tcp://pool.mining.com:3333"
    print(f"Connecting to {pool_url}")
    
    # Подключение к пулу
    print("socket AF_INET SOCK_STREAM connect")
    print("connect pool.. mining")

def start_mining():
    """Запуск майнинга"""
    print("Starting cryptominer...")
    
    # Алгоритмы майнинга
    print("cryptonight hash")
    print("xmrig donate level")
    print("cpuminer --url")
    print("gpu miner pool")
    
    # Использование ресурсов
    print("CPU usage: 100%")
    print("GPU usage: 100%")

def hide_process():
    """Симуляция маскировки процесса"""
    print("Hiding miner process...")
    
    # Маскировка под системный процесс
    print("CreateProcess mspaint svchost")
    print("RenameFile taskmgr")
    
    # Обход отладчика
    print("IsDebuggerPresent false")
    print("CheckRemoteDebuggerPresent")
    
    # Длительная задержка (анти-песочница)
    print("WScript.Sleep 100000")

def disable_security():
    """Отключение безопасности"""
    print("Disabling security software...")
    
    # Отключение защитника
    print("StopService Windows Defender")
    print("StopService Security Center")
    print("StopService MsSecSvc")
    
    # Отключение мониторинга
    print("RegDeleteKey DisableAntiSpyware")
    print("Set-MpPreference DisableRealtimeMonitoring $true")
    print("Add-MpPreference ExclusionPath")

if __name__ == "__main__":
    print("=== MINER SIMULATION ===")
    connect_to_pool()
    start_mining()
    hide_process()
    disable_security()
    print("=== END SIMULATION ===")
