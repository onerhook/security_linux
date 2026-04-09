#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Panic Button - Модуль экстренной остановки
Мгновенное реагирование на критические действия вредоносного ПО
"""

import psutil
import subprocess
import time
from datetime import datetime
from threading import Thread, Event

class PanicButton:
    def __init__(self):
        self.events_log = []
        self.critical_actions = [
            'format', 'del /q', 'rmdir /s', 'cipher /w',
            'reg delete', 'schtasks /create', 'net user',
            'wmic process', 'powershell -enc', 'certutil -decode'
        ]
        self.suspicious_processes = []
        self.stop_event = Event()
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Запуск мониторинга в отдельном потоке"""
        self.monitor_thread = Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def _monitor_loop(self):
        """Цикл мониторинга процессов"""
        while not self.stop_event.is_set():
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                        name = proc.info['name']
                        
                        # Проверка на критические команды
                        for action in self.critical_actions:
                            if action in cmdline.lower():
                                self.log_event('CRITICAL', f'Process {name} executed: {action}')
                                self.suspicious_processes.append(proc.info['pid'])
                                
                        # Подозрительные имена процессов
                        suspicious_names = ['mimikatz', 'procdump', 'psexec', 'lazagne']
                        if any(s in name.lower() for s in suspicious_names):
                            self.log_event('SUSPICIOUS', f'Suspicious process detected: {name}')
                            self.suspicious_processes.append(proc.info['pid'])
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
                time.sleep(0.5)
            except Exception as e:
                self.log_event('ERROR', f'Monitoring error: {str(e)}')
                
    def check_critical_actions(self):
        """Проверка на критические действия"""
        return len(self.suspicious_processes) > 0
        
    def trigger(self):
        """Экстренная остановка всех подозрительных процессов"""
        print("[!] PANIC BUTTON ACTIVATED!")
        self.log_event('PANIC', 'Emergency stop triggered')
        
        killed_count = 0
        for pid in self.suspicious_processes[:]:
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                proc.wait(timeout=3)
                self.log_event('KILLED', f'Process {pid} ({proc.name()}) terminated')
                killed_count += 1
            except Exception as e:
                try:
                    proc.kill()
                    self.log_event('KILLED_FORCE', f'Process {pid} force killed')
                    killed_count += 1
                except:
                    self.log_event('FAILED', f'Failed to kill process {pid}: {str(e)}')
                    
        print(f"[+] Убито процессов: {killed_count}")
        return killed_count
        
    def log_event(self, event_type, message):
        """Логирование события"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'message': message
        }
        self.events_log.append(event)
        print(f"[{event_type}] {message}")
        
    def get_events_log(self):
        """Получение лога событий"""
        return self.events_log
        
    def stop(self):
        """Остановка мониторинга"""
        self.stop_event.set()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
