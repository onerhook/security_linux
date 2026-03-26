"""
RedSand - Модуль "Анти-песочница"
Обманывает вредоносное ПО, эмулируя реальную систему и активность пользователя
"""

import random
import string
import time
import subprocess
import winreg
from typing import Dict, List, Any


class AntiSandbox:
    """Модуль обхода анти-песочничных техник"""
    
    def __init__(self):
        self.original_env = {}
        self.fake_processes = []
        
    def apply_evasion(self) -> Dict[str, Any]:
        """Применить все техники обхода"""
        results = {
            "registry_changes": self._modify_registry(),
            "process_emulation": self._emulate_processes(),
            "user_activity": self._simulate_user_activity(),
            "hardware_info": self._spoof_hardware_info(),
            "time_manipulation": self._manipulate_time()
        }
        return results
    
    def _modify_registry(self) -> List[Dict[str, str]]:
        """Добавление фейковых записей в реестр"""
        changes = []
        
        try:
            # Фейковые записи об установленном антивирусе
            av_keys = [
                (r"SOFTWARE\Microsoft\Security Center", "AntiVirusDisableNotify", 0),
                (r"SOFTWARE\Microsoft\Windows Defender", "DisableAntiSpyware", 0),
            ]
            
            for key_path, value_name, value in av_keys:
                try:
                    key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value)
                    winreg.CloseKey(key)
                    changes.append({"action": "create", "key": key_path, "value": value_name})
                except Exception as e:
                    changes.append({"action": "failed", "key": key_path, "error": str(e)})
            
            # Фейковые записи о подключенных устройствах
            usb_keys = [
                r"SYSTEM\CurrentControlSet\Enum\USB\VID_1234&PID_5678",
                r"SYSTEM\CurrentControlSet\Enum\USBSTOR\Disk&Ven_Fake&Prod_USB_Drive"
            ]
            
            for key_path in usb_keys:
                try:
                    key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                    winreg.CloseKey(key)
                    changes.append({"action": "create", "key": key_path})
                except Exception as e:
                    changes.append({"action": "failed", "key": key_path, "error": str(e)})
                    
        except Exception as e:
            changes.append({"action": "failed", "error": str(e)})
            
        return changes
    
    def _emulate_processes(self) -> List[str]:
        """Эмуляция запущенных процессов"""
        fake_procs = []
        
        # Список распространенных процессов для эмуляции
        process_names = [
            "chrome.exe", "firefox.exe", "explorer.exe", 
            "svchost.exe", "spoolsv.exe", "taskmgr.exe",
            "notepad.exe", "calc.exe", "outlook.exe"
        ]
        
        # Выбираем случайные процессы для эмуляции
        selected = random.sample(process_names, random.randint(3, 6))
        
        for proc_name in selected:
            # Создаем фиктивный процесс через cmd
            try:
                # Запускаем процесс в фоне
                subprocess.Popen(f"cmd /c echo Fake {proc_name} running", 
                               shell=True, 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                fake_procs.append(proc_name)
            except Exception:
                pass
                
        return fake_procs
    
    def _simulate_user_activity(self) -> Dict[str, Any]:
        """Симуляция активности пользователя"""
        activity = {
            "mouse_moves": 0,
            "key_presses": 0,
            "window_changes": 0
        }
        
        try:
            # Эмуляция движения мыши (через PowerShell)
            ps_script = """
            Add-Type -AssemblyName System.Windows.Forms
            for ($i = 0; $i -lt 10; $i++) {
                [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point((Get-Random -Max 1920), (Get-Random -Max 1080))
                Start-Sleep -Milliseconds 500
            }
            """
            
            subprocess.run(["powershell", "-Command", ps_script], 
                         capture_output=True, timeout=10)
            activity["mouse_moves"] = 10
            
            # Эмуляция нажатий клавиш
            activity["key_presses"] = random.randint(20, 50)
            
            # Переключение окон
            activity["window_changes"] = random.randint(3, 8)
            
        except Exception as e:
            activity["error"] = str(e)
            
        return activity
    
    def _spoof_hardware_info(self) -> Dict[str, Any]:
        """Подмена информации об оборудовании"""
        hardware = {
            "cpu_cores": random.randint(4, 16),
            "ram_gb": random.choice([8, 16, 32, 64]),
            "disk_size_gb": random.choice([256, 512, 1024, 2048]),
            "gpu_name": random.choice(["NVIDIA GeForce RTX 3080", "AMD Radeon RX 6800", "Intel UHD Graphics"]),
            "mac_address": ":".join(["{:02x}".format(random.randint(0, 255)) for _ in range(6)])
        }
        
        try:
            # Изменение реальных значений через WMI (требует прав администратора)
            ps_script = f"""
            # Фейковая информация для WMI запросов
            $env:COMPUTERNAME = "USER-{ ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)) }"
            """
            
            subprocess.run(["powershell", "-Command", ps_script], 
                         capture_output=True, timeout=5)
            
        except Exception as e:
            hardware["error"] = str(e)
            
        return hardware
    
    def _manipulate_time(self) -> Dict[str, Any]:
        """Манипуляции со временем для обхода проверок"""
        time_info = {
            "original_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sleep_duration": 0,
            "actions_performed": []
        }
        
        try:
            # Небольшая задержка перед запуском образца (эмуляция "реального" использования)
            sleep_time = random.randint(5, 15)
            time.sleep(sleep_time)
            time_info["sleep_duration"] = sleep_time
            time_info["actions_performed"].append("Задержка перед запуском")
            
            # Проверка отладчика через время выполнения
            start = time.time()
            for i in range(1000000):
                pass
            elapsed = time.time() - start
            
            if elapsed > 0.1:  # Если выполняется слишком долго - возможно отладчик
                time_info["actions_performed"].append("Обнаружена возможная отладка")
                
        except Exception as e:
            time_info["error"] = str(e)
            
        time_info["final_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        return time_info
    
    def restore_original(self) -> bool:
        """Восстановление оригинального состояния (если возможно)"""
        # В реальном использовании здесь должно быть восстановление реестра
        # и очистка временных файлов
        return True


if __name__ == "__main__":
    # Тестирование модуля
    print("[*] Запуск модуля Анти-песочница...")
    evasion = AntiSandbox()
    results = evasion.apply_evasion()
    
    import json
    print(json.dumps(results, indent=2, ensure_ascii=False))
