#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Real-Time Antivirus - Антивирус реального времени
Мониторит систему на наличие новых скачанных файлов и автоматически сканирует их
"""

import os
import sys
import time
import json
import threading
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, asdict
import logging

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
except ImportError:
    # Для старых версий watchdog
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    from watchdog.events import FileCreatedEvent, FileModifiedEvent

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from core.virus_scanner import VirusScanner
from core.report_generator import ReportGenerator


@dataclass
class ScanResult:
    """Результат сканирования файла"""
    file_path: str
    file_name: str
    file_size: int
    file_hash: str
    scan_time: str
    threat_level: str  # CLEAN, SUSPICIOUS, MALICIOUS
    risk_score: int
    is_malicious: bool
    detected_threats: List[str]
    action_taken: str  # NONE, QUARANTINE, DELETE, ALERT
    message: str


class QuarantineManager:
    """Управление карантином для подозрительных файлов"""
    
    def __init__(self, quarantine_dir: str = "quarantine"):
        self.quarantine_dir = Path(quarantine_dir)
        self.quarantine_dir.mkdir(exist_ok=True)
        self.quarantine_log = self.quarantine_dir / "quarantine_log.json"
        self.quarantined_files: Dict[str, Dict[str, Any]] = {}
        self._load_quarantine_log()
    
    def _load_quarantine_log(self):
        """Загрузка журнала карантина"""
        if self.quarantine_log.exists():
            try:
                with open(self.quarantine_log, 'r', encoding='utf-8') as f:
                    self.quarantined_files = json.load(f)
            except Exception:
                self.quarantined_files = {}
    
    def _save_quarantine_log(self):
        """Сохранение журнала карантина"""
        try:
            with open(self.quarantine_log, 'w', encoding='utf-8') as f:
                json.dump(self.quarantined_files, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения журнала карантина: {e}")
    
    def move_to_quarantine(self, file_path: str, reason: str) -> bool:
        """Перемещение файла в карантин"""
        try:
            if not os.path.exists(file_path):
                return False
            
            file_name = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            quarantine_name = f"{timestamp}_{file_name}"
            quarantine_path = self.quarantine_dir / quarantine_name
            
            # Перемещаем файл
            os.rename(file_path, quarantine_path)
            
            # Записываем в журнал
            self.quarantined_files[str(quarantine_path)] = {
                'original_path': file_path,
                'original_name': file_name,
                'quarantine_time': datetime.now().isoformat(),
                'reason': reason,
                'can_restore': True
            }
            self._save_quarantine_log()
            
            print(f"[+] Файл перемещен в карантин: {quarantine_path}")
            return True
            
        except Exception as e:
            print(f"[-] Ошибка перемещения в карантин: {e}")
            return False
    
    def restore_from_quarantine(self, quarantine_path: str) -> bool:
        """Восстановление файла из карантина"""
        try:
            if quarantine_path not in self.quarantined_files:
                print("Файл не найден в журнале карантина")
                return False
            
            info = self.quarantined_files[quarantine_path]
            original_path = info['original_path']
            
            # Восстанавливаем файл
            os.rename(quarantine_path, original_path)
            
            # Удаляем из журнала
            del self.quarantined_files[quarantine_path]
            self._save_quarantine_log()
            
            print(f"[+] Файл восстановлен: {original_path}")
            return True
            
        except Exception as e:
            print(f"[-] Ошибка восстановления: {e}")
            return False
    
    def list_quarantined(self) -> List[Dict[str, Any]]:
        """Список файлов в карантине"""
        return list(self.quarantined_files.values())


class FileMonitorHandler(FileSystemEventHandler):
    """Обработчик событий файловой системы"""
    
    def __init__(self, scanner_callback: Callable[[str], ScanResult], 
                 monitored_extensions: List[str] = None,
                 logger_callback: Callable[[str], None] = None):
        super().__init__()
        self.scanner_callback = scanner_callback
        self.logger_callback = logger_callback or print
        self.monitored_extensions = monitored_extensions or [
            '.exe', '.bat', '.cmd', '.ps1', '.vbs', '.js',
            '.msi', '.dll', '.scr', '.pif', '.com',
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.pdf', '.zip', '.rar', '.7z', '.tar', '.gz'
        ]
        self.scan_queue = []
        self.is_scanning = False
        self.lock = threading.Lock()
    
    def _should_scan(self, file_path: str) -> bool:
        """Проверка, нужно ли сканировать файл"""
        ext = os.path.splitext(file_path)[1].lower()
        
        # Проверяем расширение
        if ext not in self.monitored_extensions:
            return False
        
        # Игнорируем временные файлы
        file_name = os.path.basename(file_path)
        if file_name.startswith('~$') or file_name.startswith('.'):
            return False
        
        # Игнорируем системные директории
        ignore_dirs = ['Windows', 'Program Files', 'ProgramData', '$Recycle.Bin']
        for ignore_dir in ignore_dirs:
            if ignore_dir in file_path:
                return False
        
        return True
    
    def on_created(self, event):
        """Событие создания файла - сканируем только новые файлы"""
        if isinstance(event, FileCreatedEvent) and not event.is_directory:
            file_path = event.src_path
            
            # Ждем пока файл полностью запишется
            time.sleep(0.3)
            
            if self._should_scan(file_path):
                self.logger_callback(f"\n[!] Обнаружен НОВЫЙ файл: {file_path}")
                self._queue_for_scanning(file_path)
    
    def on_modified(self, event):
        """Событие изменения файла - НЕ сканируем, чтобы избежать повторных срабатываний"""
        # Игнорируем изменения, сканируем только при создании
        pass
    
    def _queue_for_scanning(self, file_path: str):
        """Добавление файла в очередь на сканирование"""
        with self.lock:
            if file_path not in self.scan_queue:
                self.scan_queue.append(file_path)
                self.logger_callback(f"[+] Добавлен в очередь: {file_path}")
                
                # Запускаем сканирование если еще не запущено
                if not self.is_scanning:
                    threading.Thread(target=self._process_queue, daemon=True).start()
    
    def _process_queue(self):
        """Обработка очереди сканирования"""
        while True:
            with self.lock:
                if not self.scan_queue:
                    self.is_scanning = False
                    break
                
                file_path = self.scan_queue.pop(0)
                self.is_scanning = True
            
            # Небольшая задержка чтобы файл полностью записался
            time.sleep(0.5)
            
            # Сканируем файл
            try:
                result = self.scanner_callback(file_path)
                self._handle_scan_result(result)
            except Exception as e:
                self.logger_callback(f"[-] Ошибка сканирования {file_path}: {e}")
    
    def _handle_scan_result(self, result: ScanResult):
        """Обработка результата сканирования"""
        if result.is_malicious:
            self.logger_callback(f"\n🚨 ОБНАРУЖЕНА УГРОЗА! 🚨")
            self.logger_callback(f"Файл: {result.file_name}")
            self.logger_callback(f"Уровень угрозы: {result.threat_level}")
            self.logger_callback(f"Риск: {result.risk_score}/100")
            if result.detected_threats:
                self.logger_callback(f"Угрозы: {', '.join(result.detected_threats)}")
            self.logger_callback(f"Действие: {result.action_taken}")
            self.logger_callback(f"Сообщение: {result.message}\n")
        elif result.threat_level == 'SUSPICIOUS':
            self.logger_callback(f"\n⚠️ ПОДОЗРИТЕЛЬНЫЙ ФАЙЛ ⚠️")
            self.logger_callback(f"Файл: {result.file_name}")
            self.logger_callback(f"Рекомендация: Будьте осторожны с этим файлом\n")


class RealTimeAntivirus:
    """Основной класс антивируса реального времени"""
    
    def __init__(self, 
                 monitored_folders: List[str] = None,
                 auto_quarantine: bool = True,
                 scan_on_access: bool = True,
                 reports_dir: str = "reports"):
        
        self.monitored_folders = monitored_folders or self._get_default_monitored_folders()
        self.auto_quarantine = auto_quarantine
        self.scan_on_access = scan_on_access
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Компоненты
        self.virus_scanner = VirusScanner()
        self.quarantine_manager = QuarantineManager()
        self.report_generator = ReportGenerator(str(self.reports_dir))
        
        # Мониторинг
        self.observer: Optional[Observer] = None
        self.is_running = False
        self.scan_results: List[ScanResult] = []
        
        # Настройки
        self.enabled = False  # По умолчанию выключен
        self.notification_callback: Optional[Callable[[ScanResult], None]] = None
        
        # Логирование
        self._setup_logging()
    
    def _setup_logging(self):
        """Настройка логирования"""
        log_file = self.reports_dir / f"antivirus_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('RealTimeAntivirus')
    
    def _get_default_monitored_folders(self) -> List[str]:
        """Получение папок для мониторинга по умолчанию"""
        home = Path.home()
        
        default_folders = [
            str(home / "Downloads"),
            str(home / "Desktop"),
            str(home / "Documents"),
        ]
        
        # Добавляем Windows специфичные папки
        if sys.platform == 'win32':
            default_folders.extend([
                str(Path(os.environ.get('TEMP', 'C:\\Temp'))),
                str(Path(os.environ.get('USERPROFILE', 'C:\\Users\\Default')) / "Downloads"),
            ])
        
        # Фильтруем несуществующие папки
        return [f for f in default_folders if os.path.exists(f)]
    
    def scan_file(self, file_path: str) -> ScanResult:
        """Сканирование одного файла через ExtendedVirusScanner"""
        self.logger.info(f"Сканирование файла: {file_path}")
        
        start_time = time.time()
        
        # Используем ExtendedVirusScanner для более точного анализа
        from core.extended_scanner import ExtendedVirusScanner
        scanner = ExtendedVirusScanner()
        scan_result = scanner.scan_file(file_path)
        
        # Определяем действие
        action_taken = "NONE"
        message = "Файл безопасен"
        
        threat_level_str = scan_result.threat_level.value if hasattr(scan_result.threat_level, 'value') else str(scan_result.threat_level)
        is_malicious = threat_level_str == 'MALICIOUS'
        
        if is_malicious:
            if self.auto_quarantine:
                if self.quarantine_manager.move_to_quarantine(file_path, threat_level_str):
                    action_taken = "QUARANTINE"
                    message = "Файл перемещен в карантин"
                else:
                    action_taken = "ALERT"
                    message = "Обнаружена угроза! Требуется ручное вмешательство"
            else:
                action_taken = "ALERT"
                message = "Обнаружена угроза! Требуется ручное вмешательство"
        
        elif threat_level_str == 'SUSPICIOUS':
            action_taken = "ALERT"
            message = "Подозрительный файл. Рекомендуется проверка."
        
        # Создаем результат
        result = ScanResult(
            file_path=file_path,
            file_name=os.path.basename(file_path),
            file_size=scan_result.score,  # используем score как размер для совместимости
            file_hash=scan_result.sha256,
            scan_time=datetime.now().isoformat(),
            threat_level=threat_level_str,
            risk_score=scan_result.score,
            is_malicious=is_malicious,
            detected_threats=scan_result.threats_found,
            action_taken=action_taken,
            message=message
        )
        
        # Сохраняем в историю
        self.scan_results.append(result)
        
        # Генерируем отчет для угроз
        if is_malicious or threat_level_str == 'SUSPICIOUS':
            self._generate_scan_report(result)
        
        # Уведомляем callback
        if self.notification_callback:
            self.notification_callback(result)
        
        elapsed = time.time() - start_time
        self.logger.info(f"Сканирование завершено за {elapsed:.2f}с: {threat_level_str}")
        
        return result
    
    def _generate_scan_report(self, result: ScanResult):
        """Генерация отчета о сканировании"""
        report_data = {
            'scan_type': 'realtime',
            'file': {
                'path': result.file_path,
                'name': result.file_name,
                'size': result.file_size,
                'hash': result.file_hash
            },
            'result': {
                'threat_level': result.threat_level,
                'risk_score': result.risk_score,
                'is_malicious': result.is_malicious,
                'detected_threats': result.detected_threats,
                'action_taken': result.action_taken,
                'message': result.message
            },
            'scan_time': result.scan_time,
            'action': result.action_taken
        }
        
        # Генерируем JSON отчет
        report_path = self.report_generator.generate_json(report_data)
        self.logger.info(f"Отчет сохранен: {report_path}")
    
    def start(self):
        """Запуск антивируса реального времени"""
        if self.is_running:
            self.logger.warning("Антивирус уже запущен")
            return
        
        if not self.enabled:
            self.logger.warning("Антивирус выключен. Включите перед запуском.")
            return
        
        self.logger.info("Запуск антивируса реального времени...")
        self.logger.info(f"Мониторинг папок: {', '.join(self.monitored_folders)}")
        
        # Создаем обработчик
        handler = FileMonitorHandler(
            scanner_callback=self.scan_file,
            logger_callback=self.logger.info
        )
        
        # Создаем наблюдатель
        self.observer = Observer()
        
        # Добавляем папки для мониторинга
        for folder in self.monitored_folders:
            if os.path.exists(folder):
                self.observer.schedule(handler, folder, recursive=False)
                self.logger.info(f"Добавлена папка: {folder}")
            else:
                self.logger.warning(f"Папка не существует: {folder}")
        
        # Запускаем наблюдатель
        self.observer.start()
        self.is_running = True
        self.logger.info("✅ Антивирус реального времени запущен")
        
        # Бесконечный цикл (можно прервать через stop())
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def start_background(self):
        """Запуск антивируса в фоновом режиме"""
        if not self.enabled:
            self.logger.warning("Антивирус выключен. Включите перед запуском.")
            return False
        
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        time.sleep(1)  # Ждем пока запустится
        return self.is_running
    
    def stop(self):
        """Остановка антивируса"""
        if not self.is_running:
            return
        
        self.logger.info("Остановка антивируса...")
        self.is_running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5)
        
        self.logger.info("❌ Антивирус остановлен")
    
    def enable(self):
        """Включение антивируса"""
        self.enabled = True
        self.logger.info("✅ Антивирус включен")
    
    def disable(self):
        """Выключение антивируса"""
        self.enabled = False
        if self.is_running:
            self.stop()
        self.logger.info("❌ Антивирус выключен")
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса антивируса"""
        return {
            'enabled': self.enabled,
            'is_running': self.is_running,
            'monitored_folders': self.monitored_folders,
            'auto_quarantine': self.auto_quarantine,
            'scanned_files_count': len(self.scan_results),
            'quarantined_files_count': len(self.quarantine_manager.list_quarantined()),
            'last_scans': [asdict(r) for r in self.scan_results[-10:]]  # Последние 10 сканирований
        }
    
    def manual_scan(self, folder_path: str) -> List[ScanResult]:
        """Ручное сканирование папки"""
        self.logger.info(f"Ручное сканирование папки: {folder_path}")
        
        results = []
        scanned_count = 0
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    result = self.scan_file(file_path)
                    results.append(result)
                    scanned_count += 1
                    
                    if scanned_count % 10 == 0:
                        self.logger.info(f"Просканировано файлов: {scanned_count}")
                        
                except Exception as e:
                    self.logger.error(f"Ошибка сканирования {file_path}: {e}")
        
        self.logger.info(f"Ручное сканирование завершено. Просканировано: {scanned_count} файлов")
        return results


def create_antivirus_service(auto_start: bool = False) -> RealTimeAntivirus:
    """
    Создание и настройка сервиса антивируса.
    
    Args:
        auto_start: Автоматически запускать при создании
    
    Returns:
        Настроенный экземпляр RealTimeAntivirus
    """
    antivirus = RealTimeAntivirus(
        monitored_folders=None,  # Использовать папки по умолчанию
        auto_quarantine=True,    # Автоматически помещать угрозы в карантин
        scan_on_access=True,     # Сканировать при доступе
        reports_dir="antivirus_reports"
    )
    
    # Включаем антивирус
    antivirus.enable()
    
    if auto_start:
        antivirus.start_background()
    
    return antivirus


if __name__ == '__main__':
    print("=" * 60)
    print("RedSand Real-Time Antivirus v1.0")
    print("=" * 60)
    
    # Создаем антивирус
    antivirus = create_antivirus_service(auto_start=False)
    
    print("\nСтатус антивируса:")
    status = antivirus.get_status()
    print(f"  Включен: {status['enabled']}")
    print(f"  Запущен: {status['is_running']}")
    print(f"  Папок под наблюдением: {len(status['monitored_folders'])}")
    print(f"  Авто-карантин: {status['auto_quarantine']}")
    
    print("\nПапки для мониторинга:")
    for folder in status['monitored_folders']:
        print(f"  - {folder}")
    
    print("\n" + "=" * 60)
    print("Для запуска мониторинга выполните: antivirus.start()")
    print("Или в фоновом режиме: antivirus.start_background()")
    print("Для остановки: antivirus.stop()")
    print("Для выключения: antivirus.disable()")
    print("=" * 60)
