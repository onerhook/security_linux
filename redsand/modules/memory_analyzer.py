"""
RedSand - Модуль анализа памяти
Создает дампы памяти процессов, обнаруживает инъекции кода и скрытые угрозы
"""

import ctypes
from ctypes import wintypes
from typing import Dict, List, Any, Optional
import json


class MemoryAnalyzer:
    """Анализ дампов памяти процессов"""
    
    def __init__(self):
        self.process_handle = None
        self.dump_path = "dumps"
        
        # Windows API константы
        self.PROCESS_VM_READ = 0x0010
        self.PROCESS_QUERY_INFORMATION = 0x0400
        self.TH32CS_SNAPPROCESS = 0x00000002
        
    def create_process_dump(self, pid: int, output_path: str) -> Dict[str, Any]:
        """Создание полного дампа процесса"""
        result = {
            "pid": pid,
            "success": False,
            "dump_path": output_path,
            "size": 0,
            "error": None
        }
        
        try:
            # Открытие процесса
            h_process = ctypes.windll.kernel32.OpenProcess(
                self.PROCESS_VM_READ | self.PROCESS_QUERY_INFORMATION,
                False,
                pid
            )
            
            if not h_process:
                result["error"] = f"Не удалось открыть процесс {pid}"
                return result
            
            # Получение информации о процессе
            process_info = self._get_process_info(pid)
            
            # Чтение памяти процесса
            memory_regions = self._read_memory_regions(h_process, pid)
            
            # Сохранение дампа
            dump_size = self._save_dump(memory_regions, output_path)
            
            result["success"] = True
            result["size"] = dump_size
            result["process_info"] = process_info
            result["regions_count"] = len(memory_regions)
            
            ctypes.windll.kernel32.CloseHandle(h_process)
            
        except Exception as e:
            result["error"] = str(e)
            
        return result
    
    def _get_process_info(self, pid: int) -> Dict[str, Any]:
        """Получение информации о процессе"""
        info = {"pid": pid, "name": "", "path": ""}
        
        try:
            # Использование WMI для получения информации
            import subprocess
            ps_command = f'powershell "Get-Process -Id {pid} | Select-Object Name, Path | ConvertTo-Json"'
            result = subprocess.run(ps_command, shell=True, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                info["name"] = data.get("Name", "")
                info["path"] = data.get("Path", "")
                
        except Exception as e:
            info["error"] = str(e)
            
        return info
    
    def _read_memory_regions(self, h_process: int, pid: int) -> List[Dict[str, Any]]:
        """Чтение регионов памяти процесса"""
        regions = []
        
        try:
            # Структура MEMORY_BASIC_INFORMATION
            class MEMORY_BASIC_INFORMATION(ctypes.Structure):
                _fields_ = [
                    ("BaseAddress", ctypes.c_void_p),
                    ("AllocationBase", ctypes.c_void_p),
                    ("AllocationProtect", wintypes.DWORD),
                    ("RegionSize", ctypes.c_size_t),
                    ("State", wintypes.DWORD),
                    ("Protect", wintypes.DWORD),
                    ("Type", wintypes.DWORD)
                ]
            
            mbi = MEMORY_BASIC_INFORMATION()
            address = 0
            
            while True:
                # QueryVirtualMemory
                result = ctypes.windll.kernel32.VirtualQueryEx(
                    h_process,
                    ctypes.c_void_p(address),
                    ctypes.byref(mbi),
                    ctypes.sizeof(mbi)
                )
                
                if result == 0:
                    break
                
                # Читаем только коммитированную память
                if mbi.State == 0x1000:  # MEM_COMMIT
                    region_data = {
                        "base_address": hex(mbi.BaseAddress),
                        "size": mbi.RegionSize,
                        "protect": mbi.Protect,
                        "type": mbi.Type,
                        "data": None
                    }
                    
                    # Чтение данных из региона (ограниченный размер для производительности)
                    if mbi.RegionSize < 10 * 1024 * 1024:  # Максимум 10MB на регион
                        buffer = ctypes.create_string_buffer(mbi.RegionSize)
                        bytes_read = ctypes.c_size_t()
                        
                        if ctypes.windll.kernel32.ReadProcessMemory(
                            h_process,
                            ctypes.c_void_p(mbi.BaseAddress),
                            buffer,
                            mbi.RegionSize,
                            ctypes.byref(bytes_read)
                        ):
                            region_data["data"] = buffer.raw[:bytes_read.value]
                    
                    regions.append(region_data)
                
                address += mbi.RegionSize
                
        except Exception as e:
            pass
            
        return regions
    
    def _save_dump(self, regions: List[Dict[str, Any]], output_path: str) -> int:
        """Сохранение дампа в файл"""
        total_size = 0
        
        try:
            with open(output_path, 'wb') as f:
                for region in regions:
                    if region.get("data"):
                        f.write(region["data"])
                        total_size += len(region["data"])
                        
        except Exception as e:
            pass
            
        return total_size
    
    def detect_injections(self, pid: int) -> Dict[str, Any]:
        """Обнаружение инъекций кода в процессе"""
        detection = {
            "pid": pid,
            "suspicious_regions": [],
            "hooks_detected": [],
            "risk_score": 0
        }
        
        try:
            h_process = ctypes.windll.kernel32.OpenProcess(
                self.PROCESS_VM_READ | self.PROCESS_QUERY_INFORMATION,
                False,
                pid
            )
            
            if not h_process:
                detection["error"] = f"Не удалось открыть процесс {pid}"
                return detection
            
            # Анализ регионов памяти на подозрительные признаки
            regions = self._read_memory_regions(h_process, pid)
            
            for region in regions:
                # Проверка на исполняемую память с записью (RWX) - подозрительно
                if region["protect"] == 0x40:  # PAGE_EXECUTE_READWRITE
                    detection["suspicious_regions"].append({
                        "address": region["base_address"],
                        "size": region["size"],
                        "reason": "Исполняемая память с правами записи (RWX)"
                    })
                    detection["risk_score"] += 20
                
                # Проверка на наличие shellcode паттернов
                if region.get("data"):
                    shellcode_patterns = [
                        b"\x90\x90\x90",  # NOP sled
                        b"\xcc\xcc\xcc",  # INT3 breakpoints
                        b"\x6a\x00\x68",  # Push 0, Push ...
                    ]
                    
                    for pattern in shellcode_patterns:
                        if pattern in region["data"]:
                            detection["suspicious_regions"].append({
                                "address": region["base_address"],
                                "pattern": pattern.hex(),
                                "reason": "Обнаружен shellcode паттерн"
                            })
                            detection["risk_score"] += 30
            
            ctypes.windll.kernel32.CloseHandle(h_process)
            
        except Exception as e:
            detection["error"] = str(e)
            
        return detection
    
    def scan_for_strings(self, dump_path: str, min_length: int = 4) -> Dict[str, List[str]]:
        """Поиск строк в дампе памяти"""
        strings = {
            "ascii": [],
            "unicode": [],
            "urls": [],
            "ips": [],
            "paths": []
        }
        
        try:
            import re
            
            with open(dump_path, 'rb') as f:
                data = f.read()
            
            # ASCII строки
            ascii_pattern = rb'[\x20-\x7e]{' + str(min_length).encode() + rb',}'
            strings["ascii"] = [s.decode('ascii', errors='ignore') for s in re.findall(ascii_pattern, data)][:200]
            
            # Unicode строки
            unicode_pattern = rb'(?:[\x20-\x7e]\x00){' + str(min_length).encode() + rb',}'
            unicode_matches = re.findall(unicode_pattern, data)
            strings["unicode"] = [s.decode('utf-16-le', errors='ignore')[:100] for s in unicode_matches][:200]
            
            # URL адреса
            url_pattern = rb'https?://[^\s\x00]{4,}'
            strings["urls"] = list(set([s.decode('ascii', errors='ignore') for s in re.findall(url_pattern, data)]))[:50]
            
            # IP адреса
            ip_pattern = rb'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            strings["ips"] = list(set([s.decode('ascii') for s in re.findall(ip_pattern, data)]))[:50]
            
            # Пути к файлам
            path_pattern = rb'[A-Za-z]:\\[^\x00\s]{3,}'
            strings["paths"] = list(set([s.decode('ascii', errors='ignore') for s in re.findall(path_pattern, data)]))[:50]
            
        except Exception as e:
            strings["error"] = str(e)
            
        return strings
    
    def analyze_memory_dump(self, dump_path: str) -> Dict[str, Any]:
        """Комплексный анализ дампа памяти"""
        analysis = {
            "dump_path": dump_path,
            "file_size": 0,
            "strings_analysis": {},
            "suspicious_indicators": [],
            "iocs": {}
        }
        
        try:
            import os
            analysis["file_size"] = os.path.getsize(dump_path)
            
            # Анализ строк
            analysis["strings_analysis"] = self.scan_for_strings(dump_path)
            
            # Извлечение IOC
            iocs = {
                "urls": analysis["strings_analysis"].get("urls", []),
                "ips": analysis["strings_analysis"].get("ips", []),
                "paths": analysis["strings_analysis"].get("paths", []),
                "suspicious_strings": []
            }
            
            # Поиск подозрительных строк
            suspicious_keywords = [
                "password", "admin", "login", "shell", "cmd", "powershell",
                "registry", "inject", "hook", "payload", "c2", "beacon"
            ]
            
            all_strings = analysis["strings_analysis"].get("ascii", []) + \
                         analysis["strings_analysis"].get("unicode", [])
            
            for s in all_strings:
                s_lower = s.lower()
                if any(keyword in s_lower for keyword in suspicious_keywords):
                    iocs["suspicious_strings"].append(s)
            
            analysis["iocs"] = iocs
            
            # Подозрительные индикаторы
            if len(iocs["urls"]) > 0:
                analysis["suspicious_indicators"].append("Обнаружены URL адреса в памяти")
            if len(iocs["ips"]) > 10:
                analysis["suspicious_indicators"].append("Большое количество IP адресов в памяти")
            if len(iocs["suspicious_strings"]) > 5:
                analysis["suspicious_indicators"].append("Найдены подозрительные строки")
                
        except Exception as e:
            analysis["error"] = str(e)
            
        return analysis


if __name__ == "__main__":
    # Тестирование модуля (только на Windows)
    print("[*] Модуль анализа памяти")
    print("Примечание: Требуется запуск от имени администратора на Windows")
    
    # Пример использования (раскомментировать на Windows)
    # analyzer = MemoryAnalyzer()
    # result = analyzer.create_process_dump(1234, "dumps/process_1234.dmp")
    # print(json.dumps(result, indent=2))
