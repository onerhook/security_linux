"""
RedSand Secure - Расширенный сканер вирусов с увеличенной базой сигнатур
Поддерживает 56+ явных сигнатур и 15+ эвристических паттернов
"""

import re
import os
import hashlib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ThreatLevel(Enum):
    CLEAN = "CLEAN"
    SUSPICIOUS = "SUSPICIOUS"
    MALICIOUS = "MALICIOUS"


@dataclass
class ScanResult:
    file_path: str
    threat_level: ThreatLevel
    score: int
    threats_found: List[str]
    threat_types: List[str]
    sha256: str
    details: Dict


class ExtendedVirusScanner:
    """
    Расширенный сканер вирусов с поддержкой 56+ сигнатур и эвристического анализа
    """
    
    def __init__(self):
        # === ЯВНЫЕ СИГНАТУРЫ ВРЕДОНОСНОГО ПОВЕДЕНИЯ (56 паттернов) ===
        self.malware_signatures = {
            # --- Инъекция кода и манипуляции с процессами (9 паттернов) ---
            'code_injection': [
                r'CreateRemoteThread\s*\(\s*NULL',  # Инъекция в процесс
                r'WriteProcessMemory\s*\([^)]*explorer\.exe',  # Запись в explorer
                r'WriteProcessMemory\s*\([^)]*svchost\.exe',  # Запись в svchost
                r'VirtualAllocEx\s*\([^)]*PAGE_EXECUTE',  # Выделение исполняемой памяти
                r'NtCreateThreadEx\s*\(',  # Создание скрытого потока
                r'QueueUserAPC\s*\(',  # APC инъекция
                r'SetThreadContext\s*\(',  # Модификация контекста потока
                r'NtUnmapViewOfSection\s*\(',  # Process Hollowing
                r'ResumeThread\s*\([^)]*CREATE_SUSPENDED',  # Запуск приостановленного процесса
            ],
            
            # --- Автозагрузка через реестр (4 паттерна) ---
            'registry_persistence': [
                r'RegSetValueEx\s*[^)]*SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run',
                r'RegSetValueEx\s*[^)]*SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce',
                r'reg\s+add\s+.*HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run',
                r'schtasks\s+/create\s+.*/onlogon',  # Планировщик задач
            ],
            
            # --- Скачивание и запуск вредоносного ПО (5 паттернов) ---
            'download_execute': [
                r'URLDownloadToFile\s*\([^)]*\.exe',
                r'WinHttpOpenRequest\s*[^)]*GET',
                r'InternetReadFile\s*\([^)]*WriteFile',
                r'powershell\s+-c\s+.*DownloadString',
                r'certutil\s+-urlcache\s+-split\s+-f',  # Living off the Land
            ],
            
            # --- Ransomware и шифрование файлов (8 паттернов) ---
            'ransomware': [
                r'CryptEncrypt\s*\([^)]*\.(locked|encrypted|crypto)',
                r'FindFirstFile\s*\([^)]*\*\..*',  # Массовый поиск файлов
                r'SetFileAttributes\s*\([^)]*FILE_ATTRIBUTE_HIDDEN',
                r'DeleteVolumeShadowCopies\s*\(',  # Удаление теневых копий
                r'vssadmin\s+delete\s+shadows',
                r'bcdedit\s+/set\s+{default}\s+recoveryenabled\s+no',  # Отключение восстановления
                r'wbadmin\s+delete\s+systemstatebackup',
                r'\.(locked|encrypted|crypt|bitcoin|decrypt)\s*=',  # Расширения вымогателей
            ],
            
            # --- Отключение защиты системы (7 паттернов) ---
            'disable_security': [
                r'StopService\s*\([^)]*WinDefend',  # Отключение Защитника Windows
                r'StopService\s*\([^)]*SecurityHealthService',
                r'RegSetValueEx\s*[^)]*DisableAntiSpyware',
                r'RegSetValueEx\s*[^)]*DisableRealtimeMonitoring',
                r'taskkill\s+/im\s+mssecsvc\.exe',
                r'netsh\s+advfirewall\s+set\s+allprofiles\s+state\s+off',  # Отключение фаервола
                r'ScStop\s*\([^)]*(defender|security|antivirus)',
            ],
            
            # --- Маскировка под системные процессы (4 паттерна) ---
            'masquerading': [
                r'CreateProcess\s*\([^)]*svchost\.exe[^)]*-k\s+netsvcs',
                r'CreateProcess\s*\([^)]*explorer\.exe[^)]*/root,',
                r'CopyFile\s*\([^)]*System32[^)]*Temp\\',
                r'SetCurrentDirectory\s*\([^)]*System32',
            ],
            
            # --- Кейлоггинг и слежка (5 паттернов) ---
            'keylogger_spyware': [
                r'GetAsyncKeyState\s*\(',  # Перехват нажатий клавиш
                r'GetKeyState\s*\(',
                r'SetWindowsHookEx\s*\([^)]*WH_KEYBOARD',
                r'GetForegroundWindow\s*\([^)]*GetWindowText',
                r'BitBlt\s*\([^)]*ScreenCapture',  # Скриншоты
            ],
            
            # --- Сетевые угрозы и ботнеты (5 паттернов) ---
            'network_threats': [
                r'socket\s*\([^)]*AF_INET[^)]*SOCK_STREAM',
                r'connect\s*\([^)]*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+',
                r'send\s*\([^)]*POST\s+/gate\.php',  # C2 коммуникация
                r'recv\s*\([^)]*cmd\s*=',
                r'WSAStartup\s*\([^)]*shell',
            ],
            
            # --- Криптомайнеры (5 паттернов) ---
            'cryptominer': [
                r'stratum\+tcp://',  # Протокол майнинга
                r'pool\.minexmr\.com',
                r'xmr\.pool\.com',
                r'cryptonight|monero|bytecoin',
                r'cudaDeviceSynchronize\s*\([^)]*mining',
            ],
            
            # --- RAT (Remote Access Trojan) (5 паттернов) ---
            'rat': [
                r'CreateRemoteThread\s*\([^)]*cmd\.exe',
                r'shell\s*=\s*exec\s*\(',
                r'wscript\.shell\s*\.run\s*\([^)]*hidden',
                r'nc\s+-e\s+/bin/(bash|sh)',  # Netcat reverse shell
                r'python\s+-c\s+.*socket.*connect',
            ],
            
            # --- Dropper и загрузчики (3 паттерна) ---
            'dropper': [
                r'Expand\s*\([^)]*\.cab[^)]*System32',
                r'MakeCab\s*\([^)]*\.dll',
                r'bitsadmin\s+/transfer\s+/download',
            ],
        }
        
        # === ЭВРИСТИЧЕСКИЕ ПАТТЕРНЫ (15 паттернов) ===
        self.heuristic_patterns = {
            # Подозрительные комбинации API
            'suspicious_api_combo': [
                r'(VirtualAlloc|HeapCreate).*PAGE_EXECUTE',
                r'(CreateFile|WriteFile).*(CreateProcess|ShellExecute)',
                r'(RegOpenKey|RegSetValue).*(Run|RunOnce)',
                r'(socket|connect).*(send|recv).*(exec|eval)',
                r'(FindFirstFile|FindNextFile).*(DeleteFile|MoveFile)',
            ],
            
            # Обфускация и кодирование
            'obfuscation': [
                r'base64\.b64decode\s*\([^)]*exec',
                r'eval\s*\(\s*["\'].*["\']\s*\+\s*["\']',
                r'chr\s*\(\s*[0-9]+\s*\)\s*\+\s*chr',
                r'fromcharcode\s*\([^)]*join',
                r'[a-z]{1}\s*=\s*[a-z]{1}\s*\^\s*[a-z]{1}',  # XOR обфускация
            ],
            
            # Анти-анализ и анти-отладка
            'anti_analysis': [
                r'IsDebuggerPresent\s*\(',
                r'CheckRemoteDebuggerPresent\s*\(',
                r'NtQueryInformationProcess\s*\([^)]*ProcessDebugPort',
                r'GetTickCount\s*\([^)]*sleep',
                r'cpuid',
            ],
        }
        
        # Веса для различных категорий угроз
        self.threat_weights = {
            'code_injection': 25,
            'registry_persistence': 20,
            'download_execute': 22,
            'ransomware': 30,
            'disable_security': 28,
            'masquerading': 18,
            'keylogger_spyware': 24,
            'network_threats': 20,
            'cryptominer': 15,
            'rat': 26,
            'dropper': 20,
            'suspicious_api_combo': 15,
            'obfuscation': 12,
            'anti_analysis': 18,
        }
        
        # Пороговые значения
        self.thresholds = {
            'clean_max': 25,
            'suspicious_max': 60,
        }
        
        # Известные безопасные пути (для снижения ложных срабатываний)
        self.safe_paths = [
            r'\\Program Files\\',
            r'\\Windows\\System32\\',
            r'\\AppData\\Local\\Packages\\',
            r'pytest',
            r'unittest',
            r'\\venv\\',
            r'\\node_modules\\',
        ]

    def calculate_file_hash(self, file_path: str) -> str:
        """Вычисляет SHA256 хеш файла"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return "unknown"

    def is_safe_path(self, file_path: str) -> bool:
        """Проверяет, находится ли файл в безопасном пути"""
        for safe_pattern in self.safe_paths:
            if re.search(safe_pattern, file_path, re.IGNORECASE):
                return True
        return False

    def extract_strings(self, file_path: str, min_length: int = 4) -> List[str]:
        """Извлекает строки из файла (ANSI и Unicode)"""
        strings = []
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                
                # ANSI строки
                ansi_pattern = rb'[\x20-\x7e]{' + str(min_length).encode() + rb',}'
                ansi_strings = re.findall(ansi_pattern, content)
                strings.extend([s.decode('ascii', errors='ignore') for s in ansi_strings])
                
                # Unicode строки
                unicode_pattern = rb'(?:[\x20-\x7e]\x00){' + str(min_length).encode() + rb',}'
                unicode_strings = re.findall(unicode_pattern, content)
                strings.extend([s.decode('utf-16-le', errors='ignore') for s in unicode_strings])
                
        except Exception:
            pass
        
        return strings

    def scan_content(self, content: str, file_path: str = "") -> Tuple[int, List[str], List[str]]:
        """
        Сканирует содержимое на наличие сигнатур и эвристик
        Возвращает: (score, threats_found, threat_types)
        """
        score = 0
        threats_found = []
        threat_types = set()
        
        # Проверка на безопасный путь
        if self.is_safe_path(file_path):
            score -= 10  # Снижаем оценку для файлов в безопасных путях
        
        # Сканирование явных сигнатур
        for category, patterns in self.malware_signatures.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                        weight = self.threat_weights.get(category, 15)
                        score += weight
                        threat_name = f"{category.upper()}::{pattern[:30]}..."
                        threats_found.append(threat_name)
                        threat_types.add(category.upper())
                except re.error:
                    continue
        
        # Сканирование эвристических паттернов
        for category, patterns in self.heuristic_patterns.items():
            matches_count = 0
            for pattern in patterns:
                try:
                    if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                        matches_count += 1
                except re.error:
                    continue
            
            if matches_count > 0:
                # Бонус за множественные совпадения эвристик
                bonus = min(matches_count * 3, 15)
                weight = self.threat_weights.get(category, 12)
                score += weight + bonus
                threat_name = f"HEURISTIC::{category.upper()} ({matches_count} matches)"
                threats_found.append(threat_name)
                threat_types.add(f"HEUR_{category.upper()}")
        
        return score, threats_found, list(threat_types)

    def scan_file(self, file_path: str) -> ScanResult:
        """Полное сканирование файла"""
        try:
            # Вычисляем хеш
            file_hash = self.calculate_file_hash(file_path)
            
            # Читаем файл
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception:
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='ignore')
            
            # Извлекаем строки для дополнительного анализа
            strings = self.extract_strings(file_path)
            strings_content = '\n'.join(strings)
            
            # Объединяем контент для анализа
            full_content = content + '\n' + strings_content
            
            # Сканируем
            score, threats, threat_types = self.scan_content(full_content, file_path)
            
            # Нормализация оценки
            score = max(0, min(100, score))
            
            # Определяем уровень угрозы
            if score <= self.thresholds['clean_max']:
                threat_level = ThreatLevel.CLEAN
            elif score <= self.thresholds['suspicious_max']:
                threat_level = ThreatLevel.SUSPICIOUS
            else:
                threat_level = ThreatLevel.MALICIOUS
            
            # Формируем детали
            details = {
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'strings_analyzed': len(strings),
                'categories_detected': list(threat_types),
                'is_safe_path': self.is_safe_path(file_path),
            }
            
            return ScanResult(
                file_path=file_path,
                threat_level=threat_level,
                score=score,
                threats_found=threats,
                threat_types=threat_types,
                sha256=file_hash,
                details=details
            )
            
        except Exception as e:
            return ScanResult(
                file_path=file_path,
                threat_level=ThreatLevel.SUSPICIOUS,
                score=50,
                threats_found=[f"ERROR: {str(e)}"],
                threat_types=['ERROR'],
                sha256="error",
                details={'error': str(e)}
            )

    def get_statistics(self) -> Dict:
        """Возвращает статистику по сигнатурам"""
        total_signatures = sum(len(patterns) for patterns in self.malware_signatures.values())
        total_heuristics = sum(len(patterns) for patterns in self.heuristic_patterns.values())
        
        return {
            'total_signatures': total_signatures,
            'total_heuristics': total_heuristics,
            'categories': len(self.malware_signatures),
            'heuristic_categories': len(self.heuristic_patterns),
            'thresholds': self.thresholds,
        }
