#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Secure v2.0 - Главный оркестратор
Максимально безопасная система анализа вредоносного ПО
Запускать ТОЛЬКО в изолированной виртуальной машине!
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
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Добавляем модули в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from panic_button import PanicButton
from poly_engine import PolyEngine
from threat_classifier import ThreatClassifier
from report_generator import ReportGenerator
from static_analyzer import StaticAnalyzer
from network_emulator import NetworkEmulator
from anti_sandbox import AntiSandbox

class RedSandSecure:
    """Основной класс оркестратора анализа вредоносного ПО."""
    
    def __init__(self, output_dir: str = 'reports', log_level: int = logging.INFO):
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
        
        self.original_network_state: Dict[str, Any] = {}
        self.is_network_disabled = False
        self.analysis_start_time: Optional[datetime] = None
        self.processes_monitored: List[int] = []
        
        self.logger.info("RedSand Secure инициализирован")
    
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
            # Сохраняем текущее состояние
            result = subprocess.run(
                ['netsh', 'interface', 'show', 'interface'],
                capture_output=True, text=True, shell=True, check=False
            )
            self.original_network_state['output'] = result.stdout
            
            # Отключаем все адаптеры
            adapters = ['Wi-Fi', 'Ethernet', 'Беспроводная сеть', 'Подключение по локальной сети']
            for adapter in adapters:
                subprocess.run(
                    f'netsh interface set interface "{adapter}" admin=disabled',
                    shell=True, capture_output=True, check=False
                )
            
            # Блокируем весь трафик через фаервол
            subprocess.run(
                'netsh advfirewall firewall add rule name="RedSand_Block_All" dir=out action=block enable=yes',
                shell=True, capture_output=True, check=False
            )
            subprocess.run(
                'netsh advfirewall firewall add rule name="RedSand_Block_All_In" dir=in action=block enable=yes',
                shell=True, capture_output=True, check=False
            )
            
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
            # Включаем адаптеры
            adapters = ['Wi-Fi', 'Ethernet', 'Беспроводная сеть', 'Подключение по локальной сети']
            for adapter in adapters:
                subprocess.run(
                    f'netsh interface set interface "{adapter}" admin=enabled',
                    shell=True, capture_output=True, check=False
                )
            
            # Удаляем правила фаервола
            subprocess.run(
                'netsh advfirewall firewall delete rule name="RedSand_Block_All"',
                shell=True, capture_output=True, check=False
            )
            subprocess.run(
                'netsh advfirewall firewall delete rule name="RedSand_Block_All_In"',
                shell=True, capture_output=True, check=False
            )
            
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
        
        # Запускаем образец
        try:
            process = subprocess.Popen(
                [file_path],
                cwd=os.path.dirname(file_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
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
                process.terminate()
                process.wait(timeout=5)
            
            events_log = self.panic_button.get_events_log()
            
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
    
    def analyze(self, file_path: str, use_poly: bool = False, timeout: int = 60) -> Optional[Dict[str, Any]]:
        """Полный анализ файла с использованием контекстного менеджера."""
        if not os.path.exists(file_path):
            self.logger.error(f"Файл не найден: {file_path}")
            print(f"[-] Файл не найден: {file_path}")
            return None
        
        print("=" * 60)
        print("RedSand Secure v2.0 - Анализ вредоносного ПО")
        print("=" * 60)
        print(f"Файл: {file_path}")
        print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            # Шаг 1: Отключение сети
            self.disable_network()
            
            # Шаг 2: Применение анти-песочницы
            self.apply_anti_sandbox()
            
            # Шаг 3: Запуск эмуляции сети
            self.start_network_emulation()
            
            # Шаг 4: Статический анализ
            static_results = self.analyze_static(file_path)
            
            # Шаг 5: Полиморфная генерация (опционально)
            if use_poly:
                self.logger.info("Генерация полиморфных вариантов")
                print("[*] Генерация полиморфных вариантов...")
                poly_variants = self.poly_engine.generate_variants(file_path, count=3)
                static_results['poly_variants'] = poly_variants
            
            # Шаг 6: Динамический анализ
            dynamic_events = self.run_dynamic_analysis(file_path, timeout)
            
            # Шаг 7: Классификация угрозы
            threat_info = self.classify_threat(static_results, dynamic_events)
            
            # Шаг 8: Генерация отчетов
            report_data = self.generate_reports(file_path, static_results, dynamic_events, threat_info)
            
            # Вывод вердикта
            print("\n" + "=" * 60)
            print("ВЕРДИКТ")
            print("=" * 60)
            print(f"Тип угрозы: {threat_info.get('type', 'Неизвестно')}")
            print(f"Семейство: {threat_info.get('family', 'Неизвестно')}")
            print(f"Уровень риска: {threat_info.get('risk_score', 0)}/100")
            print(f"MITRE ATT&CK: {', '.join(threat_info.get('mitre_tactics', []))}")
            print("=" * 60)
            
            self.logger.info(f"Анализ завершен. Угроза: {threat_info.get('type', 'UNKNOWN')}, Риск: {threat_info.get('risk_score', 0)}")
            return report_data
            
        except Exception as e:
            self.logger.error(f"Критическая ошибка анализа: {e}", exc_info=True)
            print(f"[-] Критическая ошибка анализа: {e}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            # Всегда восстанавливаем сеть и останавливаем эмуляцию
            self.stop_network_emulation()
            self.restore_network()
            self.logger.info("Система возвращена в исходное состояние")
            print("[*] Система возвращена в исходное состояние")

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
        description='RedSand Secure v2.0 - Анализ вредоносного ПО',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python redsand_secure.py suspicious.exe
  python redsand_secure.py malware.dll --poly
  python redsand_secure.py --generate-test-samples
        """
    )
    parser.add_argument('file', nargs='?', help='Файл для анализа')
    parser.add_argument('--poly', action='store_true', help='Использовать полиморфный анализ')
    parser.add_argument('--timeout', type=int, default=60, help='Таймаут динамического анализа (сек)')
    parser.add_argument('--generate-test-samples', action='store_true', help='Сгенерировать тестовые образцы')
    parser.add_argument('--output', default='reports', help='Директория для отчетов')
    parser.add_argument('--verbose', '-v', action='store_true', help='Включить подробное логирование')
    
    args = parser.parse_args()
    
    if args.generate_test_samples:
        generate_test_samples()
        return
    
    if not args.file:
        parser.print_help()
        return
    
    log_level = logging.DEBUG if args.verbose else logging.INFO
    sandbox = RedSandSecure(output_dir=args.output, log_level=log_level)
    sandbox.analyze(args.file, use_poly=args.poly, timeout=args.timeout)

if __name__ == '__main__':
    # Проверка прав администратора
    if os.name == 'nt' and not ctypes.windll.shell32.IsUserAnAdmin():
        print("[!] Внимание: Рекомендуется запуск от имени администратора для полного функционала")
    
    main()
