import os
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class ExtendedVirusScanner:
    def __init__(self):
        # Сигнатуры вирусов (строки, которые ищем внутри файлов)
        self.virus_signatures = {
            "FakeRansomware": [b"FAKE_RANSOMWARE_SIGNATURE", b"AES256 encrypt function call", b"bitcoin_address"],
            "FakeKeylogger": [b"FAKE_KEYLOGGER_SIGNATURE", b"GetAsyncKeyState", b"SendDataToServer"],
            "FakeMiner": [b"FAKE_MINER_SIGNATURE", b"stratum+tcp://", b"coinhive"],
            "FakeTrojan": [b"FAKE_TROJAN_SIGNATURE", b"cmd.exe /c del", b"reverse_shell"],
            "GenericThreat": [b"MALICIOUS_PAYLOAD", b"DANGER_ZONE", b"EXPLOIT_CODE"]
        }
        
        # Белый список путей (Системные файлы никогда не сканируются агрессивно)
        self.safe_paths = [
            r"C:\Windows",
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            r"/usr/bin",
            r"/bin",
            r"/sbin",
            r"/Applications"
        ]

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
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""

    def scan_file(self, file_path: str) -> Tuple[bool, str, float]:
        """
        Сканирует файл.
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

            # 3. Проверка размера (слишком большие файлы пропускаем или сканируем частично)
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return False, "Empty File", 0.0
            
            # 4. Чтение содержимого для поиска сигнатур
            # Читаем первые 1MB + последний блок (чтобы найти сигнатуры в конце)
            signatures_found = []
            
            with open(file_path, "rb") as f:
                # Читаем начало файла
                head_data = f.read(1024 * 1024) 
                
                # Читаем конец файла, если он большой
                tail_data = b""
                if file_size > 1024 * 1024:
                    f.seek(-1024 * 1024, 2)
                    tail_data = f.read(1024 * 1024)
                
                scan_data = head_data + tail_data

                # Поиск сигнатур
                for virus_name, signatures in self.virus_signatures.items():
                    for sig in signatures:
                        if sig in scan_data:
                            signatures_found.append(virus_name)
                            break # Найден один признак вируса - уже плохо

            if signatures_found:
                threat_name = ", ".join(list(set(signatures_found)))
                logger.warning(f"THREAT DETECTED: {file_path} -> {threat_name}")
                return True, threat_name, 0.95

            # 5. Если ничего не найдено - файл чист
            logger.info(f"File {file_path} is clean.")
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
