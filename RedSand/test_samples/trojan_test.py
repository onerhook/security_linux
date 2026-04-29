#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST MALWARE SAMPLE - TROJAN SIMULATION
Это тестовый образец трояна для проверки антивируса
НЕ ЯВЛЯЕТСЯ РЕАЛЬНЫМ ВРЕДОНОСНЫМ ПО
"""

THREAT_TYPE: TROJAN
GENERATED: 2024-01-01
RANDOM_ID: TEST_TROJAN_001

[MALICIOUS_INDICATORS]
- Remote access capability
- Keylogging behavior
- Data exfiltration

[SIGNATURE]
TROJAN_TEST_SIGNATURE_V1

def inject_code():
    """Симуляция инъекции кода в процесс"""
    # CreateRemoteThread - инъекция в другой процесс
    print("Injecting code into explorer.exe...")
    
    # Симуляция выделения исполняемой памяти
    addr = "VirtualAllocEx(NULL, PAGE_EXECUTE_READWRITE)"
    print(f"Allocated memory at {addr}")
    
    # Запись в память процесса
    print("WriteProcessMemory to explorer.exe")
    print("WriteProcessMemory to svchost.exe")
    print("WriteProcessMemory to lsass.exe")
    
    # Создание удаленного потока
    print("CreateRemoteThread(NULL, ...)")
    
    # Process Hollowing
    print("NtUnmapViewOfSection called")

def keylogger():
    """Симуляция кейлоггера"""
    print("Starting keylogger...")
    
    # Перехват клавиатуры
    print("SetWindowsHookEx WH_KEYBOARD")
    print("GetAsyncKeyState called")
    
    # Логирование нажатий
    with open("keylog.txt", "w") as f:
        f.write("Captured keystrokes...")

def steal_data():
    """Симуляция кражи данных"""
    print("Stealing data...")
    
    # Кража из буфера обмена
    print("GetClipboardData text")
    
    # Отправка данных на сервер
    import socket
    print("socket AF_INET SOCK_STREAM connect")
    print("send credit card data")
    
    # HTTP запросы
    print("InternetOpenUrl download execute")
    print("URLDownloadToFile .exe hidden")

def persistence():
    """Симуляция закрепления в системе"""
    print("Establishing persistence...")
    
    # Автозагрузка через реестр
    print("RegSetValueEx Run \\\\Temp\\\\malware.exe")
    print("RegSetValueEx Run \\\\AppData\\\\malware.exe")
    print("RegCreateKey SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run")
    
    # Планировщик задач
    print("schtasks create hidden")
    print("at 12:00 cmd /c malware.exe")

if __name__ == "__main__":
    print("=== TROJAN SIMULATION ===")
    inject_code()
    keylogger()
    steal_data()
    persistence()
    print("=== END SIMULATION ===")
