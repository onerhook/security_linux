#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anti Sandbox - Модуль обхода анти-песочничных техник
Эмуляция активности пользователя, подмена системных параметров
"""

import random
import time
import logging
import subprocess
import sys
from typing import List, Dict

logger = logging.getLogger(__name__)

class AntiSandbox:
    def __init__(self):
        self.active = False
        self.emulation_threads = []
        
        # Параметры для эмуляции
        self.fake_usernames = ["Admin", "User", "John", "Alex", "Dmitry"]
        self.fake_computernames = ["WORKSTATION", "OFFICE-PC", "HOME-PC", "DEV-MACHINE"]
        self.fake_processes = ["chrome.exe", "explorer.exe", "notepad.exe", "outlook.exe"]
    
    def activate(self):
        """Активация анти-песочницы"""
        logger.info("🎭 Активация анти-песочницы...")
        self.active = True
        
        try:
            # Подмена системных параметров
            self._spoof_system_info()
            
            # Эмуляция активности пользователя
            self._emulate_user_activity()
            
            # Создание фейковых артефактов
            self._create_fake_artifacts()
            
            logger.info("✅ Анти-песочница активирована")
        except Exception as e:
            logger.error(f"⚠️  Ошибка активации анти-песочницы: {e}")
    
    def deactivate(self):
        """Деактивация анти-песочницы"""
        logger.info("🔓 Деактивация анти-песочницы...")
        self.active = False
        
        # Остановка всех эмуляций
        for thread in self.emulation_threads:
            try:
                thread.join(timeout=2)
            except:
                pass
        
        self.emulation_threads = []
        logger.info("✅ Анти-песочница деактивирована")
    
    def _spoof_system_info(self):
        """Подмена системной информации"""
        if sys.platform == "win32":
            # Подмена имени компьютера (требует прав админа)
            fake_hostname = random.choice(self.fake_computernames) + str(random.randint(100, 999))
            
            try:
                # Попытка подмены через реестр (может потребовать перезагрузки)
                subprocess.run(
                    f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\ComputerName\\ComputerName" /v ComputerName /t REG_SZ /d {fake_hostname} /f',
                    shell=True, capture_output=True, timeout=5
                )
                logger.info(f"🎭 Имя компьютера изменено на: {fake_hostname}")
            except Exception as e:
                logger.warning(f"Не удалось изменить имя компьютера: {e}")
            
            # Подмена имени пользователя
            fake_username = random.choice(self.fake_usernames)
            try:
                subprocess.run(f'wmic useraccount where name="%username%" set FullName="{fake_username}"',
                             shell=True, capture_output=True, timeout=5)
                logger.info(f"🎭 Полное имя пользователя изменено на: {fake_username}")
            except Exception as e:
                logger.warning(f"Не удалось изменить имя пользователя: {e}")
    
    def _emulate_user_activity(self):
        """Эмуляция активности пользователя"""
        logger.info("🖱️  Эмуляция активности пользователя...")
        
        # Эмуляция движения мыши (если есть доступ)
        try:
            if sys.platform == "win32":
                import ctypes
                
                # Симуляция движения мыши
                for _ in range(3):
                    ctypes.windll.user32.mouse_event(0x0001, random.randint(-10, 10), random.randint(-10, 10), 0, 0)
                    time.sleep(0.5)
                
                logger.info("🖱️  Движение мыши эмулировано")
        except Exception as e:
            logger.warning(f"Не удалось эмулировать движение мыши: {e}")
        
        # Эмуляция нажатий клавиш (безопасная)
        try:
            if sys.platform == "win32":
                import ctypes
                
                # Фейковые нажатия (не отправляем реальные символы)
                ctypes.windll.user32.keybd_event(0x10, 0, 0, 0)  # Shift down
                time.sleep(0.1)
                ctypes.windll.user32.keybd_event(0x10, 0, 2, 0)  # Shift up
                
                logger.info("⌨️  Нажатия клавиш эмулированы")
        except Exception as e:
            logger.warning(f"Не удалось эмулировать нажатия: {e}")
    
    def _create_fake_artifacts(self):
        """Создание фейковых артефактов системы"""
        logger.info("📁 Создание фейковых артефактов...")
        
        if sys.platform == "win32":
            try:
                # Создание фейковых файлов в Temp
                import tempfile
                temp_dir = tempfile.gettempdir()
                
                fake_files = [
                    ("recent_docs.txt", "Document1.docx\nReport.pdf\nPhoto.jpg"),
                    ("browser_history.txt", "https://google.com\nhttps://youtube.com\nhttps://github.com"),
                    ("cache.dat", random.randbytes(1024).hex())
                ]
                
                for filename, content in fake_files:
                    filepath = f"{temp_dir}\\{filename}"
                    try:
                        with open(filepath, 'w') as f:
                            f.write(content)
                        logger.info(f"Создан фейковый файл: {filepath}")
                    except:
                        pass
                
            except Exception as e:
                logger.warning(f"Ошибка создания артефактов: {e}")
    
    def _check_vm_indicators(self) -> List[str]:
        """Проверка индикаторов виртуальной машины"""
        indicators = []
        
        # Проверка процессов ВМ
        vm_processes = ["vmtoolsd", "vboxservice", "vboxtray", "vmwaretray"]
        
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() in [p.lower() for p in vm_processes]:
                    indicators.append(f"VM_PROCESS:{proc.info['name']}")
        except:
            pass
        
        # Проверка драйверов ВМ
        if sys.platform == "win32":
            vm_drivers = ["vmmouse", "vmhgfs", "vboxmouse", "vboxsf"]
            try:
                result = subprocess.run('driverquery /fo csv', shell=True, capture_output=True, text=True, timeout=10)
                for driver in vm_drivers:
                    if driver.lower() in result.stdout.lower():
                        indicators.append(f"VM_DRIVER:{driver}")
            except:
                pass
        
        return indicators
    
    def get_status(self) -> Dict:
        """Получение статуса модуля"""
        return {
            "active": self.active,
            "emulation_threads": len(self.emulation_threads),
            "vm_indicators": self._check_vm_indicators()
        }
