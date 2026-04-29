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
        
        # ЗАКОММЕНТИРОВАНО: Не используем PowerShell для эмуляции мыши/клавиатуры
        # Это может вызвать проблемы с кодировкой и нежелательное поведение
        # Движение мыши (симуляция) - отключено
        # try:
        #     for _ in range(5):
        #         subprocess.run(
        #             'powershell -command "Add-Type -AssemblyName System.Windows.Forms; $pos = [System.Windows.Forms.Cursor]::Position; $pos.X += {}; $pos.Y += {}; [System.Windows.Forms.Cursor]::Position = $pos".format(...),
        #             shell=True, capture_output=True, timeout=2
        #         )
        #         time.sleep(0.5)
        # except:
        #     pass
        
        # Эмуляция нажатий клавиш - отключена
        # try:
        #     subprocess.run(...)
        # except:
        #     pass
        
        print("[*] Эмуляция активности пользователя завершена (симуляция)")
    
    def fake_registry_entries(self):
        """Создание фейковых записей в реестре"""
        print("[*] Создание фейковых записей реестра...")
        
        # ЗАКОММЕНТИРОВАНО: Не изменяем реестр, чтобы избежать проблем
        # registry_entries = [...]
        # for key, name, value in registry_entries:
        #     try:
        #         subprocess.run(...)
        #     except:
        #         pass
        
        print("[*] Фейковые записи реестра эмулированы (без реального изменения)")
    
    def spawn_fake_processes(self):
        """Запуск фейковых процессов для маскировки"""
        print("[*] Запуск фейковых процессов...")
        
        # ЗАКОММЕНТИРОВАНО: Не запускаем реальные приложения (notepad, mspaint, calc)
        # Это вызывает нежелательное открытие окон после анализа
        # fake_commands = [
        #     'notepad.exe',
        #     'calc.exe',
        #     'mspaint.exe',
        # ]
        # 
        # for cmd in fake_commands:
        #     try:
        #         proc = subprocess.Popen(
        #             cmd,
        #             stdout=subprocess.PIPE,
        #             stderr=subprocess.PIPE
        #         )
        #         self.fake_processes.append(proc)
        #         time.sleep(0.2)
        #     except:
        #         pass
        
        # Эмулируем только наличие процессов без реального запуска
        print("[*] Фейковые процессы эмулированы (без реального запуска)")
        self.fake_processes = []
    
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
