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
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from core.panic_button import PanicButton
from core.poly_engine import PolyEngine
from core.threat_classifier import ThreatClassifier
from core.report_generator import ReportGenerator
from core.virus_scanner import VirusScanner
from core.network_emulator import NetworkEmulator
from core.anti_sandbox import AntiSandbox
from core.docker_sandbox import DockerSandbox, analyze_in_docker


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
    analysis_time: Dict[str, Any] = None  # {'start': str, 'duration': float}

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

    def __init__(self, output_dir: str = 'reports', log_level: int = logging.INFO, max_workers: Optional[int] = None, use_docker: bool = True):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.use_docker = use_docker  # Флаг использования Docker для изоляции (по умолчанию True)

        # Настройка логирования
        self._setup_logging(log_level)

        self.panic_button = PanicButton()
        self.poly_engine = PolyEngine()
        self.classifier = ThreatClassifier()
        self.report_gen = ReportGenerator(str(self.output_dir))
        self.virus_scanner = VirusScanner()
        self.net_emulator: Optional[NetworkEmulator] = None
        self.anti_sandbox = AntiSandbox()
        self.docker_sandbox: Optional[DockerSandbox] = None  # Docker песочница для безопасного запуска

        # Multiprocessing настройки
        self.max_workers = max_workers or mp.cpu_count()
        docker_msg = " с Docker-изоляцией" if use_docker else ""
        self.logger.info(f"RedSand Secure v3.0 инициализирован (максимум потоков: {self.max_workers}){docker_msg}")

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
            # Сохраняем текущее состояние - используем Popen вместо shell=True с read()
            proc = subprocess.Popen(
                ['netsh', 'interface', 'show', 'interface'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            stdout, stderr = proc.communicate(timeout=5)
            self.original_network_state['output'] = stdout.decode('utf-8', errors='replace')

            # Отключаем все адаптеры
            adapters = ['Wi-Fi', 'Ethernet', 'Беспроводная сеть', 'Подключение по локальной сети']
            for adapter in adapters:
                proc = subprocess.Popen(
                    f'netsh interface set interface "{adapter}" admin=disabled',
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                proc.communicate(timeout=5)

            # Блокируем весь трафик через фаервол
            proc = subprocess.Popen(
                'netsh advfirewall firewall add rule name="RedSand_Block_All" dir=out action=block enable=yes',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            proc.communicate(timeout=5)
            
            proc = subprocess.Popen(
                'netsh advfirewall firewall add rule name="RedSand_Block_All_In" dir=in action=block enable=yes',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            proc.communicate(timeout=5)

            self.is_network_disabled = True
            self.logger.info("Сеть успешно отключена")
            print("[+] Сеть успешно отключена")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка отключения сети: {e}")
            print(f"[-] Ошибка отключения сети: {e}")
            return False

    def restore_network(self) -> None:
        """Восстановление сетевого подключения."""
        if not self.is_network_disabled:
            return

        self.logger.info("Восстановление сетевого подключения")
        print("[*] Восстановление сетевого подключения...")
        try:
            # Включаем адаптеры - используем Popen для избежания проблем с кодировкой
            adapters = ['Wi-Fi', 'Ethernet', 'Беспроводная сеть', 'Подключение по локальной сети']
            for adapter in adapters:
                proc = subprocess.Popen(
                    f'netsh interface set interface "{adapter}" admin=enabled',
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                proc.communicate(timeout=5)

            # Удаляем правила фаервола
            proc = subprocess.Popen(
                'netsh advfirewall firewall delete rule name="RedSand_Block_All"',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            proc.communicate(timeout=5)
            
            proc = subprocess.Popen(
                'netsh advfirewall firewall delete rule name="RedSand_Block_All_In"',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            proc.communicate(timeout=5)

            self.is_network_disabled = False
            self.logger.info("Сеть восстановлена")
            print("[+] Сеть восстановлена")
        except Exception as e:
            self.logger.error(f"Ошибка восстановления сети: {e}")
            print(f"[-] Ошибка восстановления сети: {e}")

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
        """Статический анализ файла с помощью VirusScanner"""
        print(f"[*] Статический анализ: {file_path}")
        results = self.virus_scanner.scan_file(file_path)

        # Добавляем хеш в результаты для GUI
        if 'file_hash' in results and 'hashes' not in results:
            results['hashes'] = {'sha256': results['file_hash']}

        # Предварительная классификация на основе результатов сканера
        if results['threat_level'] == 'MALICIOUS':
            threat_type = 'MALWARE'
        elif results['threat_level'] == 'SUSPICIOUS':
            threat_type = 'SUSPICIOUS'
        else:
            threat_type = 'CLEAN'

        results['preliminary_threat_type'] = threat_type

        return results

    def run_dynamic_analysis(self, file_path, timeout=60):
        """Динамический анализ с мониторингом"""
        print(f"[*] Запуск динамического анализа (таймаут: {timeout}с)...")

        self.analysis_start_time = datetime.now()
        events_log = []

        # Проверка типа файла - не запускаем текстовые файлы и другие не-executable
        if not (file_path.endswith('.exe') or file_path.endswith('.bat') or 
                file_path.endswith('.cmd') or file_path.endswith('.sh') or
                file_path.endswith('.py')):
            print(f"[!] Пропуск динамического анализа для не-executable файла: {file_path}")
            return [{'info': 'Dynamic analysis skipped for non-executable file'}]

        # Проверяем, является ли файл тестовым образцом (текстовый файл с метаданными)
        # Такие файлы не нужно запускать как executables
        try:
            with open(file_path, 'rb') as f:
                header = f.read(1024)
                # Если файл начинается с текста MZ_HEADER_SIMULATION или THREAT_TYPE, это тестовый файл
                if b'MZ_HEADER_SIMULATION' in header or b'THREAT_TYPE:' in header:
                    print(f"[!] Тестовый образец обнаружен, запуск не требуется: {file_path}")
                    return [{'info': 'Test sample detected, execution skipped', 'mock_analysis': True}]
        except Exception:
            pass  # Игнорируем ошибки чтения

        # БЕЗОПАСНЫЙ ЗАПУСК: Используем Docker для изоляции
        if self.use_docker:
            print("[*] Запуск в Docker контейнере для максимальной безопасности...")
            try:
                docker_result = analyze_in_docker(file_path, timeout=timeout, use_wine=file_path.lower().endswith('.exe'))
                
                if docker_result['success']:
                    print("[+] Анализ в Docker завершен успешно")
                    events_log = docker_result.get('events', [])
                    events_log.append({'docker_isolated': True, 'method': docker_result['method']})
                else:
                    print("[-] Docker недоступен, используем локальный запуск (МЕНЕЕ БЕЗОПАСНО!)")
                    events_log.append({'warning': 'Docker failed, fallback to local execution'})
                    # Fallback на локальный запуск если Docker не доступен
                    events_log.extend(self._run_local_analysis(file_path, timeout))
            except Exception as e:
                print(f"[-] Ошибка Docker: {e}, используем локальный запуск")
                events_log.extend(self._run_local_analysis(file_path, timeout))
        else:
            # Локальный запуск (не рекомендуется для реального вредоносного ПО)
            print("[!] ВНИМАНИЕ: Запуск без Docker изоляции! Это опасно!")
            events_log.extend(self._run_local_analysis(file_path, timeout))

        return events_log

    def _run_local_analysis(self, file_path, timeout=60):
        """Локальный запуск анализа (только если Docker недоступен)"""
        events_log = []
        
        # Запускаем образец с дополнительными ограничениями
        try:
            # Определяем тип файла и выбираем метод запуска
            if sys.platform == 'win32' and file_path.lower().endswith('.exe'):
                # На Windows используем CREATE_NO_WINDOW и ограниченные права
                process = subprocess.Popen(
                    [file_path],
                    cwd=os.path.dirname(file_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='replace',
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
                )
            else:
                # На Linux/Unix используем setsid для изоляции
                process = subprocess.Popen(
                    [file_path],
                    cwd=os.path.dirname(file_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid if hasattr(os, 'setsid') else None,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='replace'
                )
            
            self.processes_monitored.append(process.pid)
            events_log.append({'process_started': process.pid, 'isolated': False})

            # Мониторинг процессов
            start_time = time.time()
            while time.time() - start_time < timeout:
                if process.poll() is not None:
                    break

                # Проверка на критические действия
                if self.panic_button.check_critical_actions():
                    print("[!] Обнаружены критические действия! Экстренная остановка!")
                    self.panic_button.trigger()
                    events_log.append({'panic_triggered': True})
                    break

                time.sleep(1)

            # Завершаем процесс если еще работает
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    events_log.append({'process_killed': True, 'reason': 'timeout'})

            events_log.extend(self.panic_button.get_events_log())

        except Exception as e:
            print(f"[-] Ошибка выполнения: {e}")
            events_log.append({'error': str(e)})
        
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
        analysis_start = time.time()

        try:
            # Отключение сети
            self.disable_network()

            # Применение анти-песочницы
            self.apply_anti_sandbox()

            # Запуск эмуляции сети
            self.start_network_emulation()

            # Статический анализ
            static_results = self.analyze_static(file_path)

            # Полиморфная генерация удалена - функция больше не используется

            # Динамический анализ
            dynamic_events = self.run_dynamic_analysis(file_path, timeout)

            # Классификация угрозы
            threat_info = self.classify_threat(static_results, dynamic_events)

            # Генерация отчетов
            report_data = self.generate_reports(file_path, static_results, dynamic_events, threat_info)

            analysis_duration = time.time() - analysis_start

            return {
                'file_path': file_path,
                'file_hash': file_hash,
                'file_size': file_size,
                'static_results': static_results,
                'dynamic_events': dynamic_events,
                'threat_info': threat_info if threat_info else {},
                'report_data': report_data,
                'analysis_time': {'start': self.analysis_start_time.isoformat() if self.analysis_start_time else None, 'duration': analysis_duration},
                'success': True
            }

        except Exception as e:
            analysis_duration = time.time() - analysis_start
            return {
                'file_path': file_path,
                'file_hash': file_hash,
                'file_size': file_size,
                'success': False,
                'error': str(e),
                'threat_info': {},
                'analysis_time': {'start': None, 'duration': analysis_duration}
            }
        finally:
            self.stop_network_emulation()
            self.restore_network()

    def analyze_file(self, file_path: str, use_poly: bool = False, timeout: int = 60) -> AnalysisResult:
        """
        Публичный метод анализа одного файла.
        Возвращает объект AnalysisResult.
        """
        if not os.path.exists(file_path):
            return AnalysisResult(
                file_path=file_path,
                file_hash='N/A',
                file_size=0,
                success=False,
                error='File not found',
                analysis_time={'start': None, 'duration': 0.0}
            )
        
        try:
            # Вызываем внутренний метод анализа
            result_dict = self.analyze_single_file_internal(file_path, use_poly, timeout)
            
            # Преобразуем словарь в объект AnalysisResult
            return AnalysisResult(
                file_path=result_dict.get('file_path', file_path),
                file_hash=result_dict.get('file_hash', 'N/A'),
                file_size=result_dict.get('file_size', 0),
                success=result_dict.get('success', False),
                static_results=result_dict.get('static_results'),
                dynamic_events=result_dict.get('dynamic_events'),
                threat_info=result_dict.get('threat_info'),
                error=result_dict.get('error'),
                analysis_time=result_dict.get('analysis_time', {'start': None, 'duration': 0.0})
            )
        except Exception as e:
            return AnalysisResult(
                file_path=file_path,
                file_hash='N/A',
                file_size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                success=False,
                error=str(e),
                analysis_time={'start': None, 'duration': 0.0}
            )

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
