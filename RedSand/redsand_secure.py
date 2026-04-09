#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Secure v3.0 - Главный оркестратор с Multiprocessing
Максимально безопасная система анализа вредоносного ПО
Запускать ТОЛЬКО в изолированной виртуальной машине или Docker контейнере!
"""

import os
import sys
import time
import json
import argparse
import subprocess
import shutil
import ctypes
import logging
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass, asdict
import hashlib
import signal

# Добавляем модули в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from panic_button import PanicButton
from poly_engine import PolyEngine
from threat_classifier import ThreatClassifier
from report_generator import ReportGenerator
from static_analyzer import StaticAnalyzer
from network_emulator import NetworkEmulator
from anti_sandbox import AntiSandbox


@dataclass
class AnalysisResult:
    """Результат анализа файла."""
    file_path: str
    file_hash: str
    file_size: int
    success: bool
    static_results: Optional[Dict[str, Any]] = None
    dynamic_events: Optional[List[Dict[str, Any]]] = None
    threat_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    analysis_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def calculate_file_hash(file_path: str) -> str:
    """Вычисление SHA256 хеша файла."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def analyze_single_file_worker(args: Tuple[str, str, int, bool]) -> Dict[str, Any]:
    """
    Worker функция для анализа одного файла в отдельном процессе.
    Используется для multiprocessing.
    """
    file_path, output_dir, timeout, use_poly = args
    
    # Создаем новый экземпляр анализатора для этого процесса
    local_analyzer = RedSandSecure(output_dir=output_dir, log_level=logging.WARNING)
    
    start_time = time.time()
    
    try:
        result = local_analyzer.analyze_single_file_internal(file_path, use_poly, timeout)
        result['analysis_time'] = time.time() - start_time
        result['success'] = True
        return result
    except Exception as e:
        return {
            'file_path': file_path,
            'file_hash': calculate_file_hash(file_path) if os.path.exists(file_path) else 'N/A',
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            'success': False,
            'error': str(e),
            'analysis_time': time.time() - start_time
        }

class RedSandSecure:
    """Основной класс оркестратора анализа вредоносного ПО."""
    
    def __init__(self, output_dir: str = 'reports', log_level: int = logging.INFO, max_workers: Optional[int] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Настройка логирования
        self._setup_logging(log_level)
        
        self.panic_button = PanicButton()
        self.poly_engine = PolyEngine()
        self.classifier = ThreatClassifier()
        self.report_gen = ReportGenerator(str(self.output_dir))
        self.static_analyzer = StaticAnalyzer()
        self.net_emulator: Optional[NetworkEmulator] = None
        self.anti_sandbox = AntiSandbox()
        
        # Multiprocessing настройки
        self.max_workers = max_workers or mp.cpu_count()
        self.logger.info(f"RedSand Secure v3.0 инициализирован (максимум потоков: {self.max_workers})")
        
        self.original_network_state: Dict[str, Any] = {}
        self.is_network_disabled = False
        self.analysis_start_time: Optional[datetime] = None
        self.processes_monitored: List[int] = []
    
    def _setup_logging(self, log_level: int) -> None:
        """Настройка системы логирования."""
        log_file = self.output_dir / f'redsand_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('RedSandSecure')
        
    def disable_network(self) -> bool:
        """Полное отключение сети для максимальной безопасности."""
        self.logger.info("Отключение всех сетевых адаптеров")
        print("[*] Отключение всех сетевых адаптеров...")
        try:
            import sys
            if sys.platform == 'win32':
                # Windows методы
                result = subprocess.run(
                    ['netsh', 'interface', 'show', 'interface'],
                    capture_output=True, text=True, shell=True, check=False
                )
                self.original_network_state['output'] = result.stdout
                
                adapters = ['Wi-Fi', 'Ethernet', 'Беспроводная сеть', 'Подключение по локальной сети']
                for adapter in adapters:
                    subprocess.run(
                        f'netsh interface set interface "{adapter}" admin=disabled',
                        shell=True, capture_output=True, check=False
                    )
                
                subprocess.run(
                    'netsh advfirewall firewall add rule name="RedSand_Block_All" dir=out action=block enable=yes',
                    shell=True, capture_output=True, check=False
                )
                subprocess.run(
                    'netsh advfirewall firewall add rule name="RedSand_Block_All_In" dir=in action=block enable=yes',
                    shell=True, capture_output=True, check=False
                )
            else:
                # Linux методы
                self.original_network_state['interfaces'] = []
                
                # Пробуем разные команды для получения списка интерфейсов
                result = subprocess.run(
                    ['ip', '-o', 'link', 'show'],
                    capture_output=True, text=True, check=False
                )
                self.original_network_state['output'] = result.stdout
                
                interfaces = []
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            parts = line.split(':')
                            if len(parts) >= 2:
                                iface = parts[1].strip()
                                if iface != 'lo':
                                    interfaces.append(iface)
                                    self.original_network_state['interfaces'].append(iface)
                else:
                    # Если ip команда не доступна, пробуем ifconfig
                    result = subprocess.run(
                        ['ifconfig', '-a'],
                        capture_output=True, text=True, check=False
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if line and not line.startswith(' ') and ':' in line:
                                iface = line.split(':')[0].strip()
                                if iface != 'lo' and iface:
                                    interfaces.append(iface)
                                    self.original_network_state['interfaces'].append(iface)
                
                # Отключаем интерфейсы
                for iface in interfaces:
                    try:
                        subprocess.run(
                            ['ip', 'link', 'set', iface, 'down'],
                            capture_output=True, check=False
                        )
                    except:
                        pass
                
                # Блокируем трафик через iptables если доступно
                try:
                    subprocess.run(
                        ['iptables', '-A', 'OUTPUT', '-j', 'DROP'],
                        capture_output=True, check=False
                    )
                    subprocess.run(
                        ['iptables', '-A', 'INPUT', '-j', 'DROP'],
                        capture_output=True, check=False
                    )
                except:
                    pass
            
            self.is_network_disabled = True
            self.logger.info("Сеть успешно отключена")
            print("[+] Сеть успешно отключена")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка отключения сети: {e}")
            print(f"[-] Ошибка отключения сети: {e}")
            # Даже если ошибка - считаем что сеть отключена для безопасности
            self.is_network_disabled = True
            return False
    
    def restore_network(self) -> None:
        """Восстановление сетевого подключения."""
        if not self.is_network_disabled:
            return
            
        self.logger.info("Восстановление сетевого подключения")
        print("[*] Восстановление сетевого подключения...")
        try:
            import sys
            if sys.platform == 'win32':
                # Windows методы
                adapters = ['Wi-Fi', 'Ethernet', 'Беспроводная сеть', 'Подключение по локальной сети']
                for adapter in adapters:
                    subprocess.run(
                        f'netsh interface set interface "{adapter}" admin=enabled',
                        shell=True, capture_output=True, check=False
                    )
                
                subprocess.run(
                    'netsh advfirewall firewall delete rule name="RedSand_Block_All"',
                    shell=True, capture_output=True, check=False
                )
                subprocess.run(
                    'netsh advfirewall firewall delete rule name="RedSand_Block_All_In"',
                    shell=True, capture_output=True, check=False
                )
            else:
                # Linux методы
                interfaces = self.original_network_state.get('interfaces', [])
                for iface in interfaces:
                    try:
                        subprocess.run(
                            ['ip', 'link', 'set', iface, 'up'],
                            capture_output=True, check=False
                        )
                    except:
                        pass
                
                try:
                    subprocess.run(
                        ['iptables', '-F'],
                        capture_output=True, check=False
                    )
                except:
                    pass
            
            self.is_network_disabled = False
            self.logger.info("Сеть восстановлена")
            print("[+] Сеть восстановлена")
        except Exception as e:
            self.logger.error(f"Ошибка восстановления сети: {e}")
            print(f"[-] Ошибка восстановления сети: {e}")
            # Сбрасываем флаг в любом случае
            self.is_network_disabled = False
    
    def start_network_emulation(self):
        """Запуск эмуляции сети для образца"""
        print("[*] Запуск эмуляции сети...")
        self.net_emulator = NetworkEmulator()
        self.net_emulator.start()
        print("[+] Эмуляция сети запущена (локальные DNS/HTTP)")
    
    def stop_network_emulation(self):
        """Остановка эмуляции сети"""
        if self.net_emulator:
            self.net_emulator.stop()
            self.net_emulator = None
    
    def apply_anti_sandbox(self):
        """Применение техник обхода анти-песочницы"""
        print("[*] Применение анти-песочничных техник...")
        self.anti_sandbox.emulate_user_activity()
        self.anti_sandbox.fake_registry_entries()
        self.anti_sandbox.spawn_fake_processes()
        print("[+] Анти-песочница активирована")
    
    def analyze_static(self, file_path):
        """Статический анализ файла"""
        print(f"[*] Статический анализ: {file_path}")
        results = self.static_analyzer.analyze(file_path)
        
        # Предварительная классификация
        threat_type = self.classifier.classify_static(results)
        results['preliminary_threat_type'] = threat_type
        
        return results
    
    def run_dynamic_analysis(self, file_path, timeout=60):
        """Динамический анализ с мониторингом"""
        print(f"[*] Запуск динамического анализа (таймаут: {timeout}с)...")
        
        self.analysis_start_time = datetime.now()
        events_log = []
        
        # Проверяем существование файла и его тип
        if not os.path.exists(file_path):
            print(f"[-] Файл не найден: {file_path}")
            return [{'error': f'File not found: {file_path}'}]
        
        # Определяем интерпретатор для запуска в зависимости от типа файла
        import sys
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.bat' or file_ext == '.cmd':
                if sys.platform == 'win32':
                    cmd = [file_path]
                else:
                    # На Linux используем wine или просто читаем файл
                    print(f"[*] BAT файл на Linux - только статический анализ")
                    return [{'info': 'BAT file on Linux - static analysis only'}]
            elif file_ext == '.ps1':
                if sys.platform == 'win32':
                    cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', file_path]
                else:
                    print(f"[*] PowerShell файл на Linux - только статический анализ")
                    return [{'info': 'PowerShell file on Linux - static analysis only'}]
            elif file_ext in ['.exe', '.dll']:
                if sys.platform == 'win32':
                    cmd = [file_path]
                else:
                    # Пробуем wine для запуска Windows исполняемых файлов
                    wine_path = shutil.which('wine')
                    if wine_path:
                        cmd = [wine_path, file_path]
                        print(f"[*] Запуск через Wine: {file_path}")
                    else:
                        print(f"[*] Wine не найден - только статический анализ")
                        return [{'info': 'Wine not available - static analysis only'}]
            elif file_ext == '.py':
                cmd = [sys.executable, file_path]
            elif file_ext == '.sh':
                cmd = ['/bin/bash', file_path]
            else:
                # Пытаемся запустить как скрипт или бинарник
                if os.access(file_path, os.X_OK):
                    cmd = [file_path]
                else:
                    print(f"[*] Неизвестный тип файла - только статический анализ")
                    return [{'info': f'Unknown file type: {file_ext}'}]
            
            # Запускаем образец
            process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(file_path) or '.',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=None if sys.platform == 'win32' else os.setsid
            )
            self.processes_monitored.append(process.pid)
            
            # Мониторинг процессов
            start_time = time.time()
            while time.time() - start_time < timeout:
                if process.poll() is not None:
                    break
                
                # Проверка на критические действия
                if self.panic_button.check_critical_actions():
                    print("[!] Обнаружены критические действия! Экстренная остановка!")
                    self.panic_button.trigger()
                    break
                
                time.sleep(1)
            
            # Завершаем процесс если еще работает
            if process.poll() is None:
                if sys.platform == 'win32':
                    process.terminate()
                else:
                    import signal
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                process.wait(timeout=5)
            
            events_log = self.panic_button.get_events_log()
            
            # Добавляем информацию о завершении
            if process.returncode is not None:
                events_log.append({'process_exit_code': process.returncode})
            
        except Exception as e:
            print(f"[-] Ошибка выполнения: {e}")
            events_log = [{'error': str(e)}]
        
        return events_log
    
    def classify_threat(self, static_results, dynamic_events):
        """Классификация угрозы"""
        print("[*] Классификация угрозы...")
        threat_info = self.classifier.classify(static_results, dynamic_events)
        return threat_info
    
    def generate_reports(self, file_path, static_results, dynamic_events, threat_info):
        """Генерация отчетов"""
        print("[*] Генерация отчетов...")
        
        report_data = {
            'file': {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            },
            'static_analysis': static_results,
            'dynamic_analysis': dynamic_events,
            'threat_classification': threat_info,
            'analysis_time': {
                'start': self.analysis_start_time.isoformat() if self.analysis_start_time else None,
                'end': datetime.now().isoformat(),
                'duration': (datetime.now() - self.analysis_start_time).total_seconds() if self.analysis_start_time else 0
            },
            'system_info': {
                'network_disabled': self.is_network_disabled,
                'emulation_used': self.net_emulator is not None,
                'anti_sandbox_applied': True
            }
        }
        
        # Генерируем все форматы отчетов
        json_report = self.report_gen.generate_json(report_data)
        html_report = self.report_gen.generate_html(report_data)
        txt_report = self.report_gen.generate_txt(report_data)
        
        print(f"[+] Отчеты сохранены:")
        print(f"    JSON: {json_report}")
        print(f"    HTML: {html_report}")
        print(f"    TXT:  {txt_report}")
        
        return report_data
    
    def analyze_single_file_internal(self, file_path: str, use_poly: bool = False, timeout: int = 60) -> Dict[str, Any]:
        """
        Внутренний метод анализа одного файла (для использования в worker процессах).
        Возвращает словарь с результатами.
        """
        if not os.path.exists(file_path):
            return {
                'file_path': file_path,
                'file_hash': 'N/A',
                'file_size': 0,
                'success': False,
                'error': 'File not found'
            }
        
        file_hash = calculate_file_hash(file_path)
        file_size = os.path.getsize(file_path)
        
        try:
            # Отключение сети
            self.disable_network()
            
            # Применение анти-песочницы
            self.apply_anti_sandbox()
            
            # Запуск эмуляции сети
            self.start_network_emulation()
            
            # Статический анализ
            static_results = self.analyze_static(file_path)
            
            # Полиморфная генерация (опционально)
            if use_poly:
                poly_variants = self.poly_engine.generate_variants(file_path, count=3)
                static_results['poly_variants'] = poly_variants
            
            # Динамический анализ
            dynamic_events = self.run_dynamic_analysis(file_path, timeout)
            
            # Классификация угрозы
            threat_info = self.classify_threat(static_results, dynamic_events)
            
            # Генерация отчетов
            report_data = self.generate_reports(file_path, static_results, dynamic_events, threat_info)
            
            return {
                'file_path': file_path,
                'file_hash': file_hash,
                'file_size': file_size,
                'static_results': static_results,
                'dynamic_events': dynamic_events,
                'threat_info': threat_info,
                'report_data': report_data
            }
            
        except Exception as e:
            return {
                'file_path': file_path,
                'file_hash': file_hash,
                'file_size': file_size,
                'success': False,
                'error': str(e)
            }
        finally:
            self.stop_network_emulation()
            self.restore_network()
    
    def analyze_batch_multiprocessing(self, file_paths: List[str], use_poly: bool = False, 
                                       timeout: int = 60, show_progress: bool = True) -> List[Dict[str, Any]]:
        """
        Параллельный анализ нескольких файлов с использованием multiprocessing.
        
        Args:
            file_paths: Список путей к файлам для анализа
            use_poly: Использовать ли полиморфный анализ
            timeout: Таймаут динамического анализа для каждого файла
            show_progress: Показывать ли прогресс бар
            
        Returns:
            Список результатов анализа
        """
        if not file_paths:
            self.logger.warning("Список файлов пуст")
            return []
        
        total_files = len(file_paths)
        self.logger.info(f"Запуск параллельного анализа {total_files} файлов ({self.max_workers} рабочих процессов)")
        
        print("\n" + "=" * 70)
        print(f"RedSand Secure v3.0 - Параллельный анализ {total_files} файлов")
        print(f"Максимум потоков: {self.max_workers}")
        print("=" * 70)
        
        results = []
        start_time = time.time()
        
        # Подготовка аргументов для workers
        worker_args = [(fp, str(self.output_dir), timeout, use_poly) for fp in file_paths]
        
        try:
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                # Отправляем задачи
                future_to_file = {executor.submit(analyze_single_file_worker, arg): arg[0] 
                                  for arg in worker_args}
                
                # Обрабатываем результаты по мере завершения
                completed = 0
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    completed += 1
                    
                    if show_progress:
                        progress = (completed / total_files) * 100
                        elapsed = time.time() - start_time
                        avg_time = elapsed / completed if completed > 0 else 0
                        eta = avg_time * (total_files - completed)
                        
                        print(f"\r[{completed}/{total_files}] {progress:.1f}% | "
                              f"Время: {elapsed:.1f}с | ETA: {eta:.1f}с", end='', flush=True)
                    
                    try:
                        result = future.result(timeout=timeout + 10)
                        results.append(result)
                        
                        if result.get('success'):
                            threat_type = result.get('threat_info', {}).get('type', 'UNKNOWN')
                            risk_score = result.get('threat_info', {}).get('risk_score', 0)
                            print(f" ✓ {os.path.basename(file_path)} - {threat_type} (Risk: {risk_score})")
                        else:
                            print(f" ✗ {os.path.basename(file_path)} - Ошибка: {result.get('error', 'Unknown')}")
                    
                    except Exception as e:
                        error_result = {
                            'file_path': file_path,
                            'file_hash': 'N/A',
                            'file_size': 0,
                            'success': False,
                            'error': f'Worker exception: {str(e)}',
                            'analysis_time': 0.0
                        }
                        results.append(error_result)
                        print(f" ✗ {os.path.basename(file_path)} - Exception: {e}")
        
        except KeyboardInterrupt:
            print("\n\n[!] Анализ прерван пользователем")
            self.logger.warning("Анализ прерван пользователем")
        
        total_time = time.time() - start_time
        successful = sum(1 for r in results if r.get('success'))
        failed = total_files - successful
        
        print("\n" + "=" * 70)
        print("РЕЗУЛЬТАТЫ ПАРАЛЛЕЛЬНОГО АНАЛИЗА")
        print("=" * 70)
        print(f"Всего файлов: {total_files}")
        print(f"Успешно: {successful} ({successful/total_files*100:.1f}%)")
        print(f"Ошибки: {failed} ({failed/total_files*100:.1f}%)")
        print(f"Общее время: {total_time:.2f}с")
        print(f"Среднее время на файл: {total_time/total_files:.2f}с")
        print(f"Производительность: {total_files/total_time:.2f} файлов/сек")
        print("=" * 70)
        
        self.logger.info(f"Параллельный анализ завершен: {successful}/{total_files} успешно за {total_time:.2f}с")
        
        return results
    
    def analyze_directory(self, directory_path: str, recursive: bool = True, 
                         extensions: Optional[List[str]] = None, use_poly: bool = False,
                         timeout: int = 60) -> List[Dict[str, Any]]:
        """
        Анализ всех файлов в директории с использованием multiprocessing.
        
        Args:
            directory_path: Путь к директории
            recursive: Рекурсивно искать файлы в поддиректориях
            extensions: Список расширений для анализа (None = все файлы)
            use_poly: Использовать ли полиморфный анализ
            timeout: Таймаут динамического анализа
            
        Returns:
            Список результатов анализа
        """
        dir_path = Path(directory_path)
        
        if not dir_path.exists():
            self.logger.error(f"Директория не найдена: {directory_path}")
            print(f"[-] Директория не найдена: {directory_path}")
            return []
        
        if not dir_path.is_dir():
            self.logger.error(f"Не является директорией: {directory_path}")
            print(f"[-] Не является директорией: {directory_path}")
            return []
        
        print(f"[*] Поиск файлов в {directory_path}...")
        
        # Сбор файлов
        if recursive:
            if extensions:
                files = [f for ext in extensions for f in dir_path.rglob(f'*.{ext}')]
            else:
                files = list(dir_path.rglob('*'))
        else:
            if extensions:
                files = [f for ext in extensions for f in dir_path.glob(f'*.{ext}')]
            else:
                files = list(dir_path.glob('*'))
        
        # Фильтруем только файлы
        file_paths = [str(f) for f in files if f.is_file()]
        
        if not file_paths:
            print(f"[!] Файлы не найдены в {directory_path}")
            return []
        
        print(f"[+] Найдено {len(file_paths)} файлов")
        
        # Запускаем параллельный анализ
        return self.analyze_batch_multiprocessing(file_paths, use_poly=use_poly, timeout=timeout)
    
    def generate_summary_report(self, results: List[Dict[str, Any]]) -> str:
        """
        Генерация сводного отчета по результатам пакетного анализа.
        
        Args:
            results: Список результатов анализа файлов
            
        Returns:
            Путь к сохраненному отчету
        """
        if not results:
            return ""
        
        summary = {
            'summary': {
                'total_files': len(results),
                'successful': sum(1 for r in results if r.get('success')),
                'failed': sum(1 for r in results if not r.get('success')),
                'analysis_date': datetime.now().isoformat(),
                'max_workers_used': self.max_workers
            },
            'threats_detected': [],
            'files_analyzed': []
        }
        
        # Агрегация угроз
        threat_types = {}
        families = {}
        risk_scores = []
        
        for result in results:
            if result.get('success') and result.get('threat_info'):
                threat_info = result['threat_info']
                threat_type = threat_info.get('type', 'UNKNOWN')
                family = threat_info.get('family', 'Unknown')
                risk_score = threat_info.get('risk_score', 0)
                
                threat_types[threat_type] = threat_types.get(threat_type, 0) + 1
                families[family] = families.get(family, 0) + 1
                risk_scores.append(risk_score)
                
                if risk_score >= 50:  # Только значительные угрозы
                    summary['threats_detected'].append({
                        'file': os.path.basename(result['file_path']),
                        'hash': result['file_hash'],
                        'type': threat_type,
                        'family': family,
                        'risk_score': risk_score
                    })
            
            summary['files_analyzed'].append({
                'path': result['file_path'],
                'hash': result['file_hash'],
                'size': result['file_size'],
                'success': result.get('success', False),
                'error': result.get('error'),
                'analysis_time': result.get('analysis_time', 0.0)
            })
        
        # Статистика
        if risk_scores:
            summary['summary']['risk_statistics'] = {
                'average': sum(risk_scores) / len(risk_scores),
                'max': max(risk_scores),
                'min': min(risk_scores)
            }
        
        summary['threat_statistics'] = {
            'by_type': threat_types,
            'by_family': families
        }
        
        # Сохранение отчета
        summary_file = self.output_dir / f'summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n[+] Сводный отчет сохранен: {summary_file}")
        self.logger.info(f"Сводный отчет сохранен: {summary_file}")
        
        return str(summary_file)

def generate_test_samples():
    """Генерация тестовых симуляторов"""
    print("[*] Генерация тестовых симуляторов вирусов...")
    from test_samples.generate_all import generate_all_samples
    samples_dir = Path('test_samples/generated')
    samples_dir.mkdir(exist_ok=True)
    generated = generate_all_samples(str(samples_dir))
    print(f"[+] Сгенерировано {len(generated)} тестовых образцов в {samples_dir}")
    return generated

def main():
    parser = argparse.ArgumentParser(
        description='RedSand Secure v3.0 - Анализ вредоносного ПО с Multiprocessing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python redsand_secure.py suspicious.exe                    # Анализ одного файла
  python redsand_secure.py --dir ./samples                   # Анализ директории (multiprocessing)
  python redsand_secure.py --dir ./malware --workers 8       # 8 потоков
  python redsand_secure.py malware.dll --poly                # С полиморфным анализом
  python redsand_secure.py --generate-test-samples           # Генерация тестовых образцов
        """
    )
    parser.add_argument('file', nargs='?', help='Файл для анализа')
    parser.add_argument('--dir', type=str, help='Директория для пакетного анализа')
    parser.add_argument('--recursive', action='store_true', default=True, help='Рекурсивный поиск в директории')
    parser.add_argument('--extensions', type=str, nargs='+', help='Фильтр по расширениям (exe, dll, bat и т.д.)')
    parser.add_argument('--workers', type=int, default=None, help='Количество рабочих процессов (по умолчанию = CPU count)')
    parser.add_argument('--poly', action='store_true', help='Использовать полиморфный анализ')
    parser.add_argument('--timeout', type=int, default=60, help='Таймаут динамического анализа (сек)')
    parser.add_argument('--generate-test-samples', action='store_true', help='Сгенерировать тестовые образцы')
    parser.add_argument('--output', default='reports', help='Директория для отчетов')
    parser.add_argument('--verbose', '-v', action='store_true', help='Включить подробное логирование')
    parser.add_argument('--no-summary', action='store_true', help='Не генерировать сводный отчет')
    
    args = parser.parse_args()
    
    if args.generate_test_samples:
        generate_test_samples()
        return
    
    log_level = logging.DEBUG if args.verbose else logging.INFO
    
    # Определяем режим работы
    if args.dir:
        # Пакетный анализ директории
        sandbox = RedSandSecure(output_dir=args.output, log_level=log_level, max_workers=args.workers)
        results = sandbox.analyze_directory(
            directory_path=args.dir,
            recursive=args.recursive,
            extensions=args.extensions,
            use_poly=args.poly,
            timeout=args.timeout
        )
        
        # Генерируем сводный отчет если не отключено
        if results and not args.no_summary:
            sandbox.generate_summary_report(results)
    
    elif args.file:
        # Анализ одного файла
        sandbox = RedSandSecure(output_dir=args.output, log_level=log_level, max_workers=args.workers)
        result = sandbox.analyze_single_file_internal(args.file, use_poly=args.poly, timeout=args.timeout)
        
        # Вывод вердикта
        if result.get('success') and result.get('threat_info'):
            print("\n" + "=" * 70)
            print("ВЕРДИКТ")
            print("=" * 70)
            print(f"Файл: {os.path.basename(args.file)}")
            print(f"Хеш SHA256: {result['file_hash']}")
            print(f"Тип угрозы: {result['threat_info'].get('type', 'Неизвестно')}")
            print(f"Семейство: {result['threat_info'].get('family', 'Неизвестно')}")
            print(f"Уровень риска: {result['threat_info'].get('risk_score', 0)}/100")
            print(f"MITRE ATT&CK: {', '.join(result['threat_info'].get('mitre_tactics', []))}")
            print("=" * 70)
        else:
            print(f"\n[!] Ошибка анализа: {result.get('error', 'Неизвестная ошибка')}")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    # Проверка прав администратора
    if os.name == 'nt' and not ctypes.windll.shell32.IsUserAnAdmin():
        print("[!] Внимание: Рекомендуется запуск от имени администратора для полного функционала")
        print("    Для Docker: контейнер уже настроен с необходимыми правами\n")
    
    # Поддержка multiprocessing на Windows
    if os.name == 'nt':
        mp.set_start_method('spawn', force=True)
    
    main()
