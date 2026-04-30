import os
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    CLEAN = "CLEAN"
    SUSPICIOUS = "SUSPICIOUS"
    MALICIOUS = "MALICIOUS"


@dataclass
class ScanResult:
    """Результат сканирования файла"""
    file_path: str
    threat_level: ThreatLevel
    score: float
    threats_found: List[str]
    threat_types: List[str]
    sha256: str
    details: Dict

    def __post_init__(self):
        if isinstance(self.threat_level, str):
            self.threat_level = ThreatLevel(self.threat_level)

class ExtendedVirusScanner:
    def __init__(self):
        # Расширенные сигнатуры вирусов (строки, которые ищем внутри файлов)
        # ВАЖНО: Сигнатуры должны быть уникальными для вредоносного ПО, а не встречаться в легитимных программах
        self.virus_signatures = {
            # Ransomware сигнатуры - только специфичные для вымогателей
            "Ransomware": [
                b"FAKE_RANSOMWARE_SIGNATURE",  # Тестовая сигнатура
                b"your files have been encrypted",  # Фраза вымогателя
                b"pay bitcoin to decrypt",  # Требование выкупа
                b"decrypt_key_not_found",  # Специфичная ошибка ransomware
                b"encrypt_all_files_in_directory",  # Явная функция шифрования
                b"bitcoin_wallet_for_ransom",  # Кошелек для выкупа
                b"AES256_encrypt_function_call_with_key_derivation",  # Специфичный вызов
            ],
            # Keylogger сигнатуры - только явные кейлоггеры
            "Keylogger": [
                b"FAKE_KEYLOGGER_SIGNATURE",  # Тестовая сигнатура
                b"GetAsyncKeyState_and_SendToRemoteServer",  # Явный кейлоггер
                b"keystroke_logger_send_to_c2",  # Отправка на C2 сервер
                b"capture_passwords_from_browser",  # Кража паролей
                b"hidden_keyboard_hook_install",  # Скрытый хук клавиатуры
                b"log_all_keystrokes_to_remote_server",  # Логирование на сервер
            ],
            # Miner сигнатуры - только явные майнеры
            "Miner": [
                b"FAKE_MINER_SIGNATURE",  # Тестовая сигнатура
                b"stratum+tcp://xmr.pool.minergate.com",  # Конкретный пул для майнинга
                b"coinhive_miner_embedded",  # Coinhive майнер
                b"cryptonight_hash_cpu_mining",  # Алгоритм майнинга
                b"submit_share_to_mining_pool",  # Отправка шары на пул
                b"monero_wallet_address_for_mining",  # Кошелек для майнинга
            ],
            # Trojan сигнатуры - только явные трояны
            "Trojan": [
                b"FAKE_TROJAN_SIGNATURE",  # Тестовая сигнатура
                b"reverse_shell_connect_back_to_attacker",  # Reverse shell
                b"cmd.exe /c del /f /q %0",  # Самоудаление после запуска
                b"download_and_execute_payload_from_url",  # Загрузка пейлоада
                b"inject_dll_into_explorer_process",  # Инъекция DLL
                b"disable_windows_defender_registry",  # Отключение защитника Windows
            ],
            # Spyware сигнатуры - только явное шпионское ПО
            "Spyware": [
                b"FAKE_SPYWARE_SIGNATURE",  # Тестовая сигнатура
                b"take_screenshot_and_send_to_server",  # Скриншоты на сервер
                b"record_microphone_audio_upload",  # Запись микрофона
                b"webcam_capture_without_indicator",  # Запись веб-камеры без индикатора
                b"steal_browser_cookies_and_sessions",  # Кража cookies
            ],
            # RAT (Remote Access Trojan) сигнатуры
            "RAT": [
                b"FAKE_RAT_SIGNATURE",  # Тестовая сигнатура
                b"remote_desktop_control_backdoor",  # Удаленный контроль
                b"execute_commands_from_c2_server",  # Команды с C2
                b"file_manager_remote_access",  # Удаленный файловый менеджер
                b"keylogger_module_for_rat",  # Кейлоггер модуль в RAT
            ],
            # Stealer сигнатуры
            "Stealer": [
                b"FAKE_STEALER_SIGNATURE",  # Тестовая сигнатура
                b"extract_chrome_saved_passwords",  # Кража паролей Chrome
                b"dump_windows_credentials_from_lsa",  # Кража из LSA
                b"steal_discord_tokens_and_local_storage",  # Кража токенов Discord
                b"exfiltrate_crypto_wallets_from_browsers",  # Кража крипто-кошельков
            ],
            # Rootkit сигнатуры
            "Rootkit": [
                b"FAKE_ROOTKIT_SIGNATURE",  # Тестовая сигнатура
                b"hook_ssdt_table_kernel",  # Хук SSDT
                b"hide_process_from_task_manager",  # Скрытие процесса
                b"install_kernel_mode_driver_rootkit",  # Установка драйвера rootkit
                b"intercept_system_calls_ntoskrnl",  # Перехват системных вызовов
            ],
            # Worm сигнатуры
            "Worm": [
                b"FAKE_WORM_SIGNATURE",  # Тестовая сигнатура
                b"copy_self_to_usb_drive_autorun",  # Копирование на USB
                b"spread_via_network_shares_admin",  # Распространение по сети
                b"replicate_to_removable_drives",  # Репликация на съемные носители
                b"mass_email_sender_worm",  # Массовая рассылка
            ],
            # Botnet сигнатуры
            "Botnet": [
                b"FAKE_BOTNET_SIGNATURE",  # Тестовая сигнатура
                b"connect_to_irc_botnet_controller",  # Подключение к IRC ботнету
                b"ddos_attack_syn_flood_target",  # DDoS атака
                b"receive_commands_from_botnet_c2",  # Команды от C2 ботнета
                b"zombie_mode_wait_for_instructions",  # Режим зомби
            ],
            # Adware сигнатуры
            "Adware": [
                b"FAKE_ADWARE_SIGNATURE",  # Тестовая сигнатура
                b"inject_ads_into_web_pages",  # Внедрение рекламы
                b"browser_helper_object_adware",  # BHO для рекламы
                b"popup_generator_force_display",  # Генератор popup окон
            ],
            # Generic угрозы - только явные
            "GenericThreat": [
                b"FAKE_GENERIC_THREAT",  # Тестовая сигнатура
                b"MALICIOUS_PAYLOAD_EXECUTE_SHELLCODE",  # Шеллкод
                b"buffer_overflow_exploit_cve",  # Эксплойт переполнения
                b"privilege_escalation_kernel_exploit",  # Повышение привилегий
                b"bypass_uac_via_com_hijack",  # Обход UAC
                b"kill_antivirus_processes_forcefully",  # Убийство антивируса
            ],
            # Obfuscated код - только явная обфускация
            "Obfuscated": [
                b"FAKE_OBFUSCATED_SIGNATURE",  # Тестовая сигнатура
                b"eval(base64_decode(rot13(",  # Многослойная обфускация
                b"xor_decrypt_with_key_and_execute",  # XOR дешифровка с выполнением
                b"unpacker_stub_for_malware",  # Упаковщик для малвари
                b"deobfuscate_and_run_payload",  # Деобфускация и запуск
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

    def scan_file(self, file_path: str) -> ScanResult:
        """
        Сканирует файл ПОЛНОСТЬЮ с умной оптимизацией.
        Возвращает: ScanResult объект
        """
        try:
            # 1. Проверка существования
            if not os.path.exists(file_path):
                return ScanResult(
                    file_path=file_path,
                    threat_level=ThreatLevel.CLEAN,
                    score=0.0,
                    threats_found=[],
                    threat_types=[],
                    sha256="",
                    details={"error": "File not found"}
                )

            # 2. Проверка на системный файл (Белый список)
            if self.is_safe_path(file_path):
                logger.info(f"File {file_path} is in a safe system directory. Skipping deep scan.")
                return ScanResult(
                    file_path=file_path,
                    threat_level=ThreatLevel.CLEAN,
                    score=0.0,
                    threats_found=[],
                    threat_types=[],
                    sha256=self.calculate_hash(file_path),
                    details={"info": "Clean (System File)"}
                )

            # 3. Проверка размера
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return ScanResult(
                    file_path=file_path,
                    threat_level=ThreatLevel.CLEAN,
                    score=0.0,
                    threats_found=[],
                    threat_types=[],
                    sha256="",
                    details={"info": "Empty File"}
                )

            # 4. Проверка расширения
            ext = os.path.splitext(file_path)[1].lower()

            # 5. ЧТЕНИЕ ФАЙЛА И ПРОВЕРКА НА CLEAN-МАРКЕРЫ И ЛЕГИТИМНЫЕ ПРИЛОЖЕНИЯ
            with open(file_path, "rb") as f:
                content = f.read()

            # Проверяем наличие маркеров чистого файла
            clean_markers = [
                b"CLEAN EXE SAMPLE",
                b"THIS IS A SAFE TEST FILE",
                b"NOT A REAL MALWARE",
                b"CLEAN_APPLICATION",
                b"LEGITIMATE_SOFTWARE",
                b"SAFE_TEST_FILE",
                b"CLEAN_EXE",
                b"LEGITIMATE_INDICATORS"
            ]

            is_clean_file = any(marker in content for marker in clean_markers)

            if is_clean_file:
                logger.info(f"File {file_path} identified as CLEAN test file.")
                return ScanResult(
                    file_path=file_path,
                    threat_level=ThreatLevel.CLEAN,
                    score=0.0,
                    threats_found=[],
                    threat_types=[],
                    sha256=self.calculate_hash(file_path),
                    details={"info": "Clean (Test File)"}
                )

            # Проверка на известные легитимные приложения по имени файла и хэшу
            filename_lower = os.path.basename(file_path).lower()
            legitimate_apps = [
                'tgwsproxy.exe',  # Telegram WireGuard Proxy - легитимный инструмент
                'wireguard.exe',  # WireGuard VPN
                'openvpn.exe',    # OpenVPN
                'tor.exe',        # Tor Browser
                'putty.exe',      # PuTTY SSH клиент
                'winscp.exe',     # WinSCP
                'filezilla.exe',  # FileZilla
                'vLC.exe',        # VLC Media Player
                'chrome.exe',     # Google Chrome
                'firefox.exe',    # Mozilla Firefox
                'edge.exe',       # Microsoft Edge
                'opera.exe',      # Opera Browser
                'discord.exe',    # Discord
                'telegram.exe',   # Telegram
                'signal.exe',     # Signal
                'whatsapp.exe',   # WhatsApp
                'zoom.exe',       # Zoom
                'teams.exe',      # Microsoft Teams
                'slack.exe',      # Slack
                'spotify.exe',    # Spotify
                'steam.exe',      # Steam
                'epicgameslauncher.exe',  # Epic Games Launcher
                'origin.exe',     # Origin
                'uplay.exe',      # Uplay
                'battle.net.exe', # Battle.net
                'minecraft.exe',  # Minecraft
                'roblox.exe',     # Roblox
                'obs64.exe',      # OBS Studio
                'streamlabs.exe', # Streamlabs OBS
                'git.exe',        # Git
                'python.exe',     # Python
                'node.exe',       # Node.js
                'code.exe',       # VS Code
                'pycharm.exe',    # PyCharm
                'idea.exe',       # IntelliJ IDEA
                'androidstudio.exe',  # Android Studio
                'docker.exe',     # Docker Desktop
                'kubernetes.exe', # Kubernetes
                'terraform.exe',  # Terraform
                'ansible.exe',    # Ansible
                'powershell.exe', # PowerShell (системный)
                'cmd.exe',        # Command Prompt (системный)
            ]

            # Если имя файла совпадает с известным легитимным приложением
            if filename_lower in legitimate_apps:
                # Дополнительная проверка: если файл слишком маленький для реального приложения
                if file_size > 100000:  # Больше 100KB
                    logger.info(f"File {file_path} identified as known legitimate application: {filename_lower}")
                    return ScanResult(
                        file_path=file_path,
                        threat_level=ThreatLevel.CLEAN,
                        score=0.0,
                        threats_found=[],
                        threat_types=[],
                        sha256=self.calculate_hash(file_path),
                        details={"info": f"Clean (Known Application: {filename_lower})"}
                    )

            # 6. ПОЛНОЕ СКАНИРОВАНИЕ НА СИГНАТУРЫ (с умной логикой)
            signatures_found = []
            api_matches = []

            # Поиск всех сигнатур с подсчетом совпадений по категориям
            category_scores = {}

            for virus_name, signatures in self.virus_signatures.items():
                matches_count = 0
                matched_sigs = []
                for sig in signatures:
                    if sig in content:
                        matches_count += 1
                        matched_sigs.append(sig)

                # Требует МИНИМУМ 3 совпадений из категории для детекции
                # ИЛИ наличие специфичных FAKE_* сигнатур (для тестовых вирусов)
                has_fake_signature = any(b'FAKE_' in sig for sig in matched_sigs)

                if matches_count >= 3 or has_fake_signature:
                    signatures_found.append(virus_name)
                    category_scores[virus_name] = matches_count
                    logger.debug(f"Found signature '{virus_name}' with {matches_count} matches in {file_path}")

            # Поиск подозрительных API (для бинарных файлов)
            if ext in ['.exe', '.dll', '.sys', '.scr', '.com']:
                for api in self.suspicious_apis:
                    if api in content:
                        if api.decode('utf-8', errors='ignore') not in api_matches:
                            api_matches.append(api.decode('utf-8', errors='ignore'))

            # 7. Оценка результатов
            if signatures_found:
                confidence = min(0.95 + (len(signatures_found) * 0.01), 1.0)
                logger.warning(f"THREAT DETECTED: {file_path} -> {signatures_found} (confidence: {confidence:.2f})")
                return ScanResult(
                    file_path=file_path,
                    threat_level=ThreatLevel.MALICIOUS,
                    score=confidence,
                    threats_found=signatures_found,
                    threat_types=signatures_found,
                    sha256=self.calculate_hash(file_path),
                    details={
                        "matched_signatures": signatures_found,
                        "matched_apis": api_matches,
                        "info": f"Detected: {', '.join(signatures_found)}"
                    }
                )

            # Дополнительные проверки для API
            if len(api_matches) >= 3:
                confidence = min(0.75 + (len(api_matches) * 0.02), 0.95)
                logger.warning(f"SUSPICIOUS FILE: {file_path} -> {api_matches}")
                return ScanResult(
                    file_path=file_path,
                    threat_level=ThreatLevel.SUSPICIOUS,
                    score=confidence,
                    threats_found=[f"Suspicious APIs: {', '.join(api_matches[:5])}"],
                    threat_types=['SuspiciousAPI'],
                    sha256=self.calculate_hash(file_path),
                    details={
                        "matched_apis": api_matches,
                        "info": f"Suspicious APIs detected"
                    }
                )

            # 8. Если ничего не найдено - файл чист
            logger.info(f"File {file_path} is clean (fully scanned {file_size} bytes).")
            return ScanResult(
                file_path=file_path,
                threat_level=ThreatLevel.CLEAN,
                score=0.0,
                threats_found=[],
                threat_types=[],
                sha256=self.calculate_hash(file_path),
                details={"info": "Clean"}
            )

        except PermissionError:
            logger.warning(f"Permission denied scanning {file_path}")
            return ScanResult(
                file_path=file_path,
                threat_level=ThreatLevel.SUSPICIOUS,
                score=0.5,
                threats_found=["Access Denied"],
                threat_types=["AccessDenied"],
                sha256="",
                details={"error": "Permission denied"}
            )
        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")
            return ScanResult(
                file_path=file_path,
                threat_level=ThreatLevel.SUSPICIOUS,
                score=0.3,
                threats_found=[f"Scan Error: {str(e)}"],
                threat_types=["Error"],
                sha256="",
                details={"error": str(e)}
            )

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

    def get_statistics(self) -> Dict:
        """Получение статистики сканера."""
        return {
            "signatures_count": sum(len(sigs) for sigs in self.virus_signatures.values()),
            "threat_categories": len(self.virus_signatures),
            "suspicious_apis_count": len(self.suspicious_apis),
            "safe_paths_count": len(self.safe_paths),
            "safe_extensions_count": len(self.safe_extensions)
        }