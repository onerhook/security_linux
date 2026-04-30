import os
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class ExtendedVirusScanner:
    def __init__(self):
        # Расширенные сигнатуры вирусов (строки, которые ищем внутри файлов)
        self.virus_signatures = {
            # Ransomware сигнатуры
            "Ransomware": [
                b"encrypt", b"decrypt", b"bitcoin", b"wallet", b"ransom", b"payment",
                b".locked", b".crypto", b".encrypted", b"your files", b"pay bitcoin",
                b"private key", b"AES256", b"RSA4096", b"TOR", b"onion", b"recover files",
                b"FAKE_RANSOMWARE_SIGNATURE", b"AES256 encrypt function call", b"bitcoin_address"
            ],
            # Keylogger сигнатуры
            "Keylogger": [
                b"keylog", b"keystroke", b"GetAsyncKeyState", b"SetWindowsHookEx",
                b"keyboard", b"input", b"capture", b"SendDataToServer", b"log.txt",
                b"virtualkey", b"scan code", b"clipboard", b"password", b"credential",
                b"FAKE_KEYLOGGER_SIGNATURE", b"GetAsyncKeyState", b"SendDataToServer"
            ],
            # Miner сигнатуры
            "Miner": [
                b"mining", b"pool", b"stratum+tcp", b"cryptonight", b"monero", b"xmr",
                b"hashrate", b"coinhive", b"cpu miner", b"gpu miner", b"worker",
                b"submit share", b"difficulty", b"blockchain", b"coin", b"hash rate",
                b"FAKE_MINER_SIGNATURE", b"stratum+tcp://", b"coinhive"
            ],
            # Trojan сигнатуры
            "Trojan": [
                b"trojan", b"backdoor", b"reverse shell", b"cmd.exe /c", b"powershell",
                b"download", b"execute", b"payload", b"dropper", b"inject",
                b"remote access", b"c2", b"command and control", b"beacon",
                b"FAKE_TROJAN_SIGNATURE", b"cmd.exe /c del", b"reverse_shell"
            ],
            # Spyware сигнатуры
            "Spyware": [
                b"spy", b"monitor", b"screenshot", b"webcam", b"record", b"surveillance",
                b"clipboard", b"microphone", b"camera", b"screen capture", b"audio record",
                b"track", b"stealth", b"hidden", b"covert"
            ],
            # RAT (Remote Access Trojan) сигнатуры
            "RAT": [
                b"remote desktop", b"remote control", b"admin", b"shell", b"vnc",
                b"teamviewer", b"anydesk", b"remote admin", b"control panel", b"rat"
            ],
            # Stealer сигнатуры
            "Stealer": [
                b"password", b"cookie", b"credential", b"browser", b"steal", b"exfil",
                b"dump", b"wallet", b"autofill", b"history", b"bookmark", b"login data"
            ],
            # Rootkit сигнатуры
            "Rootkit": [
                b"rootkit", b"kernel", b"driver", b"hook", b"ssdt", b"idt", b"inline",
                b"stealth", b"hide process", b"hide file", b"system service", b"ntoskrnl"
            ],
            # Worm сигнатуры
            "Worm": [
                b"worm", b"spread", b"replicate", b"usb", b"network share", b"copy",
                b"propagate", b"autorun", b"removable", b"mass mailer"
            ],
            # Botnet сигнатуры
            "Botnet": [
                b"bot", b"ddos", b"flood", b"zombie", b"irc", b"syn flood", b"udp flood",
                b"http flood", b"botnet", b"c&c", b"master", b"slave", b"distributed"
            ],
            # Adware сигнатуры
            "Adware": [
                b"adware", b"popup", b"banner", b"redirect", b"promotion", b"sponsor",
                b"click here", b"advertisement", b"toolbar", b"browser helper"
            ],
            # Generic угрозы
            "GenericThreat": [
                b"MALICIOUS_PAYLOAD", b"DANGER_ZONE", b"EXPLOIT_CODE", b"SHELLCODE",
                b"buffer overflow", b"use after free", b"privilege escalation",
                b"bypass uac", b"disable antivirus", b"kill process", b"delete shadow copy"
            ],
            # Обфусцированный код
            "Obfuscated": [
                b"eval(", b"exec(", b"base64_decode", b"rot13", b"xor", b"unpack",
                b"deobfuscate", b"decode", b"decrypt", b"unpacker"
            ]
        }
        
        # Подозрительные API вызовы для PE файлов
        self.suspicious_apis = [
            b"VirtualAllocEx", b"WriteProcessMemory", b"CreateRemoteThread",
            b"NtUnmapViewOfSection", b"SetWindowsHookEx", b"GetAsyncKeyState",
            b"CryptEncrypt", b"CryptDecrypt", b"RegSetValueEx", b"CreateService",
            b"InternetOpen", b"URLDownloadToFile", b"WinExec", b"ShellExecute"
        ]
        
        # Белый список путей (Системные файлы никогда не сканируются агрессивно)
        self.safe_paths = [
            r"C:\Windows",
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            r"/usr/bin",
            r"/bin",
            r"/sbin",
            r"/Applications",
            r"/System",
            r"/Library"
        ]
        
        # Расширения безопасных файлов
        self.safe_extensions = ['.txt', '.jpg', '.jpeg', '.png', '.gif', '.bmp', 
                               '.mp3', '.mp4', '.avi', '.mkv', '.pdf', '.doc', 
                               '.docx', '.xls', '.xlsx', '.ppt', '.pptx']

    def is_safe_path(self, file_path: str) -> bool:
        """Проверяет, находится ли файл в безопасном системном каталоге."""
        file_path_lower = file_path.lower()
        for safe_path in self.safe_paths:
            if file_path_lower.startswith(safe_path.lower()):
                return True
        return False

    def calculate_hash(self, file_path: str) -> str:
        """Вычисляет SHA256 хэш файла."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(65536), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""

    def scan_file(self, file_path: str) -> Tuple[bool, str, float]:
        """
        Сканирует файл ПОЛНОСТЬЮ с умной оптимизацией.
        Возвращает: (is_malicious, threat_name, confidence)
        """
        try:
            # 1. Проверка существования
            if not os.path.exists(file_path):
                return False, "File not found", 0.0

            # 2. Проверка на системный файл (Белый список)
            if self.is_safe_path(file_path):
                logger.info(f"File {file_path} is in a safe system directory. Skipping deep scan.")
                return False, "Clean (System File)", 0.0

            # 3. Проверка размера
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return False, "Empty File", 0.0
            
            # 4. Проверка расширения (быстрая проверка для заведомо безопасных файлов)
            ext = os.path.splitext(file_path)[1].lower()
            if ext in self.safe_extensions and file_size < 10 * 1024 * 1024:  # < 10MB
                # Для безопасных расширений всё равно проводим быструю проверку
                pass

            # 5. ПОЛНОЕ ЧТЕНИЕ И СКАНИРОВАНИЕ ФАЙЛА
            signatures_found = []
            api_matches = []
            
            # Определяем размер чанка для чтения
            chunk_size = 1024 * 1024  # 1MB chunks для эффективного чтения
            
            with open(file_path, "rb") as f:
                # Читаем файл полностью по частям
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Поиск всех сигнатур в текущем чанке
                    for virus_name, signatures in self.virus_signatures.items():
                        for sig in signatures:
                            if sig in chunk:
                                if virus_name not in signatures_found:
                                    signatures_found.append(virus_name)
                                    logger.debug(f"Found signature '{virus_name}' in {file_path}")
                    
                    # Поиск подозрительных API (для бинарных файлов)
                    if ext in ['.exe', '.dll', '.sys', '.scr', '.com']:
                        for api in self.suspicious_apis:
                            if api in chunk:
                                if api.decode('utf-8', errors='ignore') not in api_matches:
                                    api_matches.append(api.decode('utf-8', errors='ignore'))

            # 6. Оценка результатов
            if signatures_found:
                threat_name = ", ".join(signatures_found)
                confidence = min(0.95 + (len(signatures_found) * 0.01), 1.0)
                logger.warning(f"THREAT DETECTED: {file_path} -> {threat_name} (confidence: {confidence:.2f})")
                return True, threat_name, confidence
            
            # Дополнительные проверки для API
            if len(api_matches) >= 3:
                threat_name = f"Suspicious APIs: {', '.join(api_matches[:5])}"
                confidence = 0.75 + (len(api_matches) * 0.02)
                confidence = min(confidence, 0.95)
                logger.warning(f"SUSPICIOUS FILE: {file_path} -> {threat_name}")
                return True, threat_name, confidence

            # 7. Если ничего не найдено - файл чист
            logger.info(f"File {file_path} is clean (fully scanned {file_size} bytes).")
            return False, "Clean", 0.0

        except PermissionError:
            logger.warning(f"Permission denied scanning {file_path}")
            return False, "Access Denied", 0.0
        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")
            return False, "Scan Error", 0.0

    def get_file_info(self, file_path: str) -> Dict:
        """Получает информацию о файле."""
        try:
            return {
                "path": file_path,
                "size": os.path.getsize(file_path),
                "hash": self.calculate_hash(file_path),
                "extension": os.path.splitext(file_path)[1].lower()
            }
        except Exception as e:
            return {"error": str(e)}
