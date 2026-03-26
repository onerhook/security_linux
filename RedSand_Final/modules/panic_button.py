#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Panic Button - Модуль экстренной остановки
Мгновенная блокировка подозрительных процессов при обнаружении критических действий
"""

import psutil
import subprocess
import logging
from datetime import datetime
from typing import List, Set

logger = logging.getLogger(__name__)

class PanicButton:
    def __init__(self, sandbox_instance=None):
        self.sandbox = sandbox_instance
        self.critical_actions = set()
        self.killed_processes: Set[int] = set()
        self.emergency_mode = False
        
        # Критические действия для мониторинга
        self.CRITICAL_PATTERNS = [
            'encrypt', 'decrypt', 'ransom',
            'delete', 'format', 'wipe',
            'inject', 'hook', 'patch',
            'keylog', 'screenshot', 'clipboard',
            'password', 'credential', 'token',
            'miner', 'coin', 'bitcoin',
            'connect', 'socket', 'beacon'
        ]
        
        # Подозрительные процессы
        self.SUSPICIOUS_PROCESS_NAMES = [
            'powershell', 'cmd', 'wscript', 'cscript',
            'mshta', 'regsvr32', 'rundll32',
            'certutil', 'bitsadmin', 'wmic'
        ]
    
    def check_critical_actions(self) -> bool:
        """Проверка на наличие критических действий"""
        try:
            # Проверка активных процессов
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    pid = proc.info['pid']
                    name = proc.info['name'].lower()
                    cmdline = ' '.join(proc.info['cmdline'] or []).lower()
                    
                    # Проверка на критические паттерны
                    for pattern in self.CRITICAL_PATTERNS:
                        if pattern in name or pattern in cmdline:
                            self.critical_actions.add(f"{pattern}:{pid}")
                            logger.warning(f"⚠️  Обнаружено критическое действие: {pattern} в процессе {pid}")
                            return True
                    
                    # Проверка на подозрительные процессы
                    if name in self.SUSPICIOUS_PROCESS_NAMES:
                        logger.info(f"ℹ️  Подозрительный процесс: {name} (PID: {pid})")
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка проверки критических действий: {e}")
            return False
    
    def trigger(self):
        """Экстренная активация защиты"""
        logger.critical("🚨 АКТИВАЦИЯ PANIC BUTTON!")
        self.emergency_mode = True
        
        try:
            # Убийство всех подозрительных процессов
            self.emergency_kill_all()
            
            # Блокировка сети (дополнительная)
            self._emergency_block_network()
            
            logger.critical("✅ PANIC BUTTON активирован успешно")
            
        except Exception as e:
            logger.error(f"❌ Ошибка активации PANIC BUTTON: {e}")
    
    def emergency_kill_all(self):
        """Убийство всех подозрительных процессов"""
        logger.info("💀 Убийство подозрительных процессов...")
        
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pid = proc.info['pid']
                name = proc.info['name'].lower()
                
                # Не убиваем системные процессы
                if pid in [0, 4] or name in ['system', 'idle']:
                    continue
                
                # Убиваем если процесс уже был замечен или подозрительный
                if pid in self.killed_processes or name in self.SUSPICIOUS_PROCESS_NAMES:
                    continue
                
                # Проверяем на критические паттерны
                is_suspicious = any(pattern in name for pattern in self.CRITICAL_PATTERNS)
                
                if is_suspicious or pid in self.killed_processes:
                    proc.kill()
                    self.killed_processes.add(pid)
                    killed_count += 1
                    logger.warning(f"💀 Убит процесс: {name} (PID: {pid})")
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        logger.info(f"✅ Убито процессов: {killed_count}")
    
    def _emergency_block_network(self):
        """Экстренная блокировка сети"""
        logger.info("🔒 Экстренная блокировка сети...")
        
        try:
            if psutil.WINDOWS:
                # Windows - блокируем через netsh
                subprocess.run(
                    'netsh advfirewall firewall add rule name="PanicBlock" dir=out action=block enable=yes',
                    shell=True, capture_output=True, timeout=5
                )
            else:
                # Linux - блокируем через iptables
                subprocess.run(
                    ['iptables', '-A', 'OUTPUT', '-j', 'DROP'],
                    capture_output=True, timeout=5
                )
            
            logger.info("✅ Сеть заблокирована")
            
        except Exception as e:
            logger.error(f"⚠️  Не удалось заблокировать сеть: {e}")
    
    def add_critical_action(self, action: str, pid: int):
        """Добавление критического действия в список"""
        self.critical_actions.add(f"{action}:{pid}")
        logger.warning(f"Добавлено критическое действие: {action} (PID: {pid})")
    
    def get_status(self) -> dict:
        """Получение статуса модуля"""
        return {
            "emergency_mode": self.emergency_mode,
            "critical_actions_count": len(self.critical_actions),
            "killed_processes_count": len(self.killed_processes),
            "critical_actions": list(self.critical_actions)
        }
