#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate All Test Samples - Генератор безопасных симуляторов вирусов
12 типов угроз для тестирования системы RedSand Secure
"""

import os
import random
import string
from pathlib import Path

def generate_ransomware_simulator(output_dir):
    """Симулятор ransomware поведения"""
    filename = os.path.join(output_dir, 'sim_ransomware.bat')
    content = '''@echo off
REM Симулятор ransomware поведения (БЕЗОПАСНЫЙ)
echo [RANSOMWARE_SIM] Starting file encryption simulation...
echo [RANSOMWARE_SIM] Scanning for documents...
echo [RANSOMWARE_SIM] Would encrypt: *.docx, *.xlsx, *.pdf
echo [RANSOMWARE_SIM] Creating ransom note: READ_ME.txt
echo RANSOMWARE SIMULATION - Your files would be encrypted! > "%TEMP%\\READ_ME.txt"
echo [RANSOMWARE_SIM] Requesting bitcoin payment...
echo [RANSOMWARE_SIM] Simulation complete
'''
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def generate_stealer_simulator(output_dir):
    """Симулятор stealers поведения"""
    filename = os.path.join(output_dir, 'sim_stealer.bat')
    content = '''@echo off
REM Симулятор stealer поведения (БЕЗОПАСНЫЙ)
echo [STEALER_SIM] Starting credential theft simulation...
echo [STEALER_SIM] Would access browser data...
echo [STEALER_SIM] Would steal cookies from Chrome/Firefox
echo [STEALER_SIM] Would extract saved passwords
echo [STEALER_SIM] Would collect crypto wallets
echo [STEALER_SIM] Sending data to C2 server (simulated)...
echo [STEALER_SIM] Simulation complete
'''
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def generate_miner_simulator(output_dir):
    """Симулятор майнера поведения"""
    filename = os.path.join(output_dir, 'sim_miner.bat')
    content = '''@echo off
REM Симулятор miner поведения (БЕЗОПАСНЫЙ)
echo [MINER_SIM] Starting cryptocurrency mining simulation...
echo [MINER_SIM] Connecting to pool: stratum+tcp://pool.example.com:3333
echo [MINER_SIM] Algorithm: cryptonight
echo [MINER_SIM] CPU usage would be 90%%
echo [MINER_SIM] Mining started...
echo [MINER_SIM] Hashrate: 1234 H/s
echo [MINER_SIM] Simulation complete
'''
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def generate_rat_simulator(output_dir):
    """Симулятор RAT поведения"""
    filename = os.path.join(output_dir, 'sim_rat.bat')
    content = '''@echo off
REM Симулятор RAT поведения (БЕЗОПАСНЫЙ)
echo [RAT_SIM] Starting remote access trojan simulation...
echo [RAT_SIM] Opening backdoor port 4444...
echo [RAT_SIM] Waiting for C2 commands...
echo [RAT_SIM] Would capture screenshots
echo [RAT_SIM] Would log keystrokes
echo [RAT_SIM] Would access webcam
echo [RAT_SIM] Simulation complete
'''
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def generate_worm_simulator(output_dir):
    """Симулятор worm поведения"""
    filename = os.path.join(output_dir, 'sim_worm.bat')
    content = '''@echo off
REM Симулятор worm поведения (БЕЗОПАСНЫЙ)
echo [WORM_SIM] Starting worm propagation simulation...
echo [WORM_SIM] Scanning for USB drives...
echo [WORM_SIM] Would copy to removable media
echo [WORM_SIM] Creating autorun.inf...
echo [WORM_SIM] Scanning network shares...
echo [WORM_SIM] Would spread via SMB
echo [WORM_SIM] Simulation complete
'''
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def generate_botnet_simulator(output_dir):
    """Симулятор botnet поведения"""
    filename = os.path.join(output_dir, 'sim_botnet.bat')
    content = '''@echo off
REM Симулятор botnet поведения (БЕЗОПАСНЫЙ)
echo [BOTNET_SIM] Starting botnet client simulation...
echo [BOTNET_SIM] Connecting to IRC C2 server...
echo [BOTNET_SIM] Bot ID: BOT_12345 registered
echo [BOTNET_SIM] Waiting for DDoS commands...
echo [BOTNET_SIM] Would participate in flood attacks
echo [BOTNET_SIM] Simulation complete
'''
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def generate_rootkit_simulator(output_dir):
    """Симулятор rootkit поведения"""
    filename = os.path.join(output_dir, 'sim_rootkit.bat')
    content = '''@echo off
REM Симулятор rootkit поведения (БЕЗОПАСНЫЙ)
echo [ROOTKIT_SIM] Starting rootkit installation simulation...
echo [ROOTKIT_SIM] Would load kernel driver...
echo [ROOTKIT_SIM] Would hook SSDT functions...
echo [ROOTKIT_SIM] Would hide processes and files...
echo [ROOTKIT_SIM] Would disable antivirus...
echo [ROOTKIT_SIM] Rootkit active (simulated)
echo [ROOTKIT_SIM] Simulation complete
'''
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def generate_spyware_simulator(output_dir):
    """Симулятор spyware поведения"""
    filename = os.path.join(output_dir, 'sim_spyware.bat')
    content = '''@echo off
REM Симулятор spyware поведения (БЕЗОПАСНЫЙ)
echo [SPYWARE_SIM] Starting spyware simulation...
echo [SPYWARE_SIM] Would monitor user activity...
echo [SPYWARE_SIM] Would capture screenshots every 10 seconds
echo [SPYWARE_SIM] Would track clipboard contents
echo [SPYWARE_SIM] Would record browsing history
echo [SPYWARE_SIM] Sending data to remote server...
echo [SPYWARE_SIM] Simulation complete
'''
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def generate_adware_simulator(output_dir):
    """Симулятор adware поведения"""
    filename = os.path.join(output_dir, 'sim_adware.bat')
    content = '''@echo off
REM Симулятор adware поведения (БЕЗОПАСНЫЙ)
echo [ADWARE_SIM] Starting adware simulation...
echo [ADWARE_SIM] Would modify browser homepage...
echo [ADWARE_SIM] Would inject ads into web pages
echo [ADWARE_SIM] Would show popup advertisements
echo [ADWARE_SIM] Would redirect search queries
echo [ADWARE_SIM] Adware active (simulated)
echo [ADWARE_SIM] Simulation complete
'''
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def generate_trojan_simulator(output_dir):
    """Симулятор trojan поведения"""
    filename = os.path.join(output_dir, 'sim_trojan.bat')
    content = '''@echo off
REM Симулятор trojan поведения (БЕЗОПАСНЫЙ)
echo [TROJAN_SIM] Starting trojan simulation...
echo [TROJAN_SIM] Disguised as legitimate software...
echo [TROJAN_SIM] Would download additional payload...
echo [TROJAN_SIM] Would inject into system processes
echo [TROJAN_SIM] Would establish persistence
echo [TROJAN_SIM] Trojan active (simulated)
echo [TROJAN_SIM] Simulation complete
'''
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def generate_dropper_simulator(output_dir):
    """Симулятор dropper поведения"""
    filename = os.path.join(output_dir, 'sim_dropper.bat')
    content = '''@echo off
REM Симулятор dropper поведения (БЕЗОПАСНЫЙ)
echo [DROPPER_SIM] Starting dropper simulation...
echo [DROPPER_SIM] Extracting embedded payload...
echo [DROPPER_SIM] Would write malware.exe to %TEMP%
echo [DROPPER_SIM] Would execute downloaded payload
echo [DROPPER_SIM] Would delete itself after execution
echo [DROPPER_SIM] Dropper active (simulated)
echo [DROPPER_SIM] Simulation complete
'''
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def generate_keylogger_simulator(output_dir):
    """Симулятор keylogger поведения"""
    filename = os.path.join(output_dir, 'sim_keylogger.bat')
    content = '''@echo off
REM Симулятор keylogger поведения (БЕЗОПАСНЫЙ)
echo [KEYLOGGER_SIM] Starting keylogger simulation...
echo [KEYLOGGER_SIM] Installing keyboard hook...
echo [KEYLOGGER_SIM] Would capture all keystrokes
echo [KEYLOGGER_SIM] Logging to: %TEMP%\\keys.log
echo [KEYLOGGER_SIM] Would send logs to remote server
echo [KEYLOGGER_SIM] Keylogger active (simulated)
echo [KEYLOGGER_SIM] Simulation complete
'''
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def generate_all_samples(output_dir):
    """Генерация всех 12 симуляторов"""
    generators = [
        ('RANSOMWARE', generate_ransomware_simulator),
        ('STEALER', generate_stealer_simulator),
        ('MINER', generate_miner_simulator),
        ('RAT', generate_rat_simulator),
        ('WORM', generate_worm_simulator),
        ('BOTNET', generate_botnet_simulator),
        ('ROOTKIT', generate_rootkit_simulator),
        ('SPYWARE', generate_spyware_simulator),
        ('ADWARE', generate_adware_simulator),
        ('TROJAN', generate_trojan_simulator),
        ('DROPPER', generate_dropper_simulator),
        ('KEYLOGGER', generate_keylogger_simulator),
    ]
    
    generated_files = []
    
    print(f"[*] Генерация 12 симуляторов вирусов в {output_dir}")
    
    for threat_type, generator_func in generators:
        try:
            filepath = generator_func(output_dir)
            generated_files.append({
                'type': threat_type,
                'path': filepath
            })
            print(f"[+] Сгенерирован: {threat_type} -> {filepath}")
        except Exception as e:
            print(f"[-] Ошибка генерации {threat_type}: {e}")
    
    print(f"\n[+] Всего сгенерировано: {len(generated_files)} симуляторов")
    return generated_files

if __name__ == '__main__':
    output_directory = 'test_samples/generated'
    os.makedirs(output_directory, exist_ok=True)
    generate_all_samples(output_directory)
