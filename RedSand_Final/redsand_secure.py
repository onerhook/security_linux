#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Secure v2.0 - Локальная система анализа вредоносного ПО
Максимальная безопасность, классификация угроз, подробные отчеты
"""

import os
import sys
import json
import time
import hashlib
import logging
import subprocess
import threading
from datetime import datetime
from pathlib import Path

# Импорт модулей
try:
    from modules.panic_button import PanicButton
    from modules.poly_engine import PolyEngine
    from modules.static_analyzer import StaticAnalyzer
    from modules.threat_classifier import ThreatClassifier
    from modules.report_generator import ReportGenerator
    from modules.network_emulator import NetworkEmulator
    from modules.anti_sandbox import AntiSandbox
except ImportError as e:
    print(f"⚠️  Ошибка импорта модулей: {e}")
    print("Убедитесь, что все модули находятся в папке modules/")
    sys.exit(1)

class RedSandSecure:
    def __init__(self, config_path="config.json"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.panic_button = PanicButton(self)
        self.poly_engine = PolyEngine()
        self.static_analyzer = StaticAnalyzer()
        self.classifier = ThreatClassifier()
        self.report_gen = ReportGenerator()
        self.network_emulator = None
        self.anti_sandbox = AntiSandbox()
        self.isolation_active = False
        self.sample_path = None
        self.analysis_results = {}
        
    def _load_config(self, config_path):
        """Загрузка конфигурации"""
        default_config = {
            "isolation": {
                "disable_network": True,
                "block_firewall": True,
                "emulate_network": True
            },
            "analysis": {
                "timeout": 60,
                "memory_dump_interval": 5,
                "enable_poly_variants": True
            },
            "reporting": {
                "formats": ["json", "html", "txt"],
                "output_dir": "reports"
            }
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"Ошибка загрузки конфига: {e}, используем настройки по умолчанию")
        
        return default_config
    
    def _setup_logging(self):
        """Настройка логирования"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"redsand_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        return logging.getLogger(__name__)
    
    def secure_isolation_start(self):
        """Включение максимальной изоляции"""
        self.logger.info("🔒 Активация режима максимальной изоляции...")
        
        try:
            # Отключение сетевых адаптеров
            if self.config["isolation"]["disable_network"]:
                self.logger.info("🌐 Отключение всех сетевых адаптеров...")
                self._disable_network_adapters()
            
            # Блокировка фаерволом
            if self.config["isolation"]["block_firewall"]:
                self.logger.info("🛡️  Настройка правил брандмауэра...")
                self._configure_firewall()
            
            # Эмуляция сети для образца
            if self.config["isolation"]["emulate_network"]:
                self.logger.info("🎭 Запуск эмулятора сети...")
                self.network_emulator = NetworkEmulator()
                self.network_emulator.start()
            
            self.isolation_active = True
            self.logger.info("✅ Изоляция активирована успешно")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка активации изоляции: {e}")
            raise
    
    def secure_isolation_stop(self):
        """Отключение изоляции и восстановление системы"""
        self.logger.info("🔓 Деактивация изоляции и восстановление системы...")
        
        try:
            # Остановка эмулятора сети
            if self.network_emulator:
                self.network_emulator.stop()
                self.network_emulator = None
            
            # Восстановление сетевых адаптеров
            if self.config["isolation"]["disable_network"]:
                self.logger.info("🌐 Восстановление сетевых адаптеров...")
                self._restore_network_adapters()
            
            # Удаление правил фаервола
            if self.config["isolation"]["block_firewall"]:
                self.logger.info("🛡️  Удаление правил брандмауэра...")
                self._restore_firewall()
            
            self.isolation_active = False
            self.logger.info("✅ Система восстановлена")
            
        except Exception as e:
            self.logger.error(f"⚠️  Ошибка восстановления: {e}")
            # Критическая ошибка - пробуем восстановить любыми способами
            self._emergency_restore()
    
    def _disable_network_adapters(self):
        """Отключение сетевых адаптеров (Windows)"""
        if sys.platform == "win32":
            commands = [
                'netsh interface set interface "Wi-Fi" admin=disabled',
                'netsh interface set interface "Ethernet" admin=disabled',
                'netsh interface set interface "Беспроводная сеть" admin=disabled',
                'netsh interface set interface "Подключение по локальной сети" admin=disabled'
            ]
            
            for cmd in commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
                except Exception:
                    pass  # Игнорируем ошибки, если интерфейс не найден
        else:
            # Linux аналог
            try:
                subprocess.run(['ip', 'link', 'set', 'dev', 'wlan0', 'down'], 
                             capture_output=True, timeout=5)
                subprocess.run(['ip', 'link', 'set', 'dev', 'eth0', 'down'], 
                             capture_output=True, timeout=5)
            except Exception:
                pass
    
    def _restore_network_adapters(self):
        """Восстановление сетевых адаптеров"""
        if sys.platform == "win32":
            commands = [
                'netsh interface set interface "Wi-Fi" admin=enabled',
                'netsh interface set interface "Ethernet" admin=enabled',
                'netsh interface set interface "Беспроводная сеть" admin=enabled',
                'netsh interface set interface "Подключение по локальной сети" admin=enabled'
            ]
            
            for cmd in commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
                except Exception:
                    pass
        else:
            try:
                subprocess.run(['ip', 'link', 'set', 'dev', 'wlan0', 'up'], 
                             capture_output=True, timeout=5)
                subprocess.run(['ip', 'link', 'set', 'dev', 'eth0', 'up'], 
                             capture_output=True, timeout=5)
            except Exception:
                pass
    
    def _configure_firewall(self):
        """Настройка правил брандмауэра для блокировки всего трафика"""
        if sys.platform == "win32":
            rules = [
                'netsh advfirewall firewall add rule name="RedSand_Block_All_Out" dir=out action=block enable=yes',
                'netsh advfirewall firewall add rule name="RedSand_Block_All_In" dir=in action=block enable=yes'
            ]
            
            for rule in rules:
                try:
                    subprocess.run(rule, shell=True, capture_output=True, timeout=5)
                except Exception:
                    pass
    
    def _restore_firewall(self):
        """Удаление правил брандмауэра"""
        if sys.platform == "win32":
            rules = [
                'netsh advfirewall firewall delete rule name="RedSand_Block_All_Out"',
                'netsh advfirewall firewall delete rule name="RedSand_Block_All_In"'
            ]
            
            for rule in rules:
                try:
                    subprocess.run(rule, shell=True, capture_output=True, timeout=5)
                except Exception:
                    pass
    
    def _emergency_restore(self):
        """Экстренное восстановление системы"""
        self.logger.critical("🚨 ЭКСТРЕННОЕ ВОССТАНОВЛЕНИЕ СИСТЕМЫ!")
        
        # Принудительное восстановление сети
        self._restore_network_adapters()
        self._restore_firewall()
        
        # Убийство всех подозрительных процессов
        self.panic_button.emergency_kill_all()
        
        self.logger.critical("✅ Экстренное восстановление завершено")
    
    def analyze_sample(self, sample_path, generate_poly_variants=False):
        """Основной метод анализа образца"""
        self.sample_path = sample_path
        self.logger.info(f"🔍 Начало анализа: {sample_path}")
        
        analysis_start = datetime.now()
        
        try:
            # 1. Активация изоляции
            self.secure_isolation_start()
            
            # 2. Статический анализ
            self.logger.info("📊 Выполнение статического анализа...")
            static_results = self.static_analyzer.analyze(sample_path)
            
            # 3. Генерация полиморфных вариантов (опционально)
            poly_results = []
            if generate_poly_variants and self.config["analysis"]["enable_poly_variants"]:
                self.logger.info("🔄 Генерация полиморфных вариантов...")
                poly_results = self.poly_engine.generate_variants(sample_path, count=3)
            
            # 4. Подготовка анти-песочницы
            self.logger.info("🎭 Активация анти-песочницы...")
            self.anti_sandbox.activate()
            
            # 5. Динамический анализ (упрощенный)
            self.logger.info("⚡ Запуск динамического анализа...")
            dynamic_results = self._run_dynamic_analysis(sample_path)
            
            # 6. Классификация угрозы
            self.logger.info("🏷️  Классификация угрозы...")
            threat_info = self.classifier.classify(static_results, dynamic_results)
            
            # 7. Формирование результатов
            self.analysis_results = {
                "timestamp": analysis_start.isoformat(),
                "sample": {
                    "path": str(sample_path),
                    "hash": static_results.get("hashes", {}),
                    "size": static_results.get("file_info", {}).get("size", 0)
                },
                "static_analysis": static_results,
                "poly_variants": poly_results,
                "dynamic_analysis": dynamic_results,
                "threat_classification": threat_info,
                "verdict": self._calculate_verdict(threat_info),
                "risk_score": threat_info.get("risk_score", 0)
            }
            
            # 8. Генерация отчетов
            self.logger.info("📝 Генерация отчетов...")
            reports = self.report_gen.generate_reports(self.analysis_results)
            
            self.logger.info("✅ Анализ завершен успешно!")
            return self.analysis_results, reports
            
        except Exception as e:
            self.logger.error(f"❌ Критическая ошибка анализа: {e}")
            self.panic_button.trigger()
            raise
        finally:
            # Всегда восстанавливаем систему
            self.secure_isolation_stop()
    
    def _run_dynamic_analysis(self, sample_path):
        """Запуск динамического анализа"""
        results = {
            "process_tree": [],
            "file_operations": [],
            "registry_operations": [],
            "network_operations": [],
            "behavior_flags": []
        }
        
        # Здесь должна быть интеграция с C++ агентом
        # Для демонстрации - симуляция
        
        timeout = self.config["analysis"]["timeout"]
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Мониторинг процессов
            time.sleep(1)
            
            # Проверка на критические действия через PanicButton
            if self.panic_button.check_critical_actions():
                self.logger.warning("⚠️  Обнаружены критические действия!")
                results["behavior_flags"].append("CRITICAL_ACTIONS_DETECTED")
                break
        
        return results
    
    def _calculate_verdict(self, threat_info):
        """Расчет вердикта на основе риска"""
        risk_score = threat_info.get("risk_score", 0)
        
        if risk_score >= 70:
            return "MALICIOUS"
        elif risk_score >= 40:
            return "SUSPICIOUS"
        else:
            return "SAFE"
    
    def get_analysis_summary(self):
        """Получение краткой сводки анализа"""
        if not self.analysis_results:
            return "Анализ еще не проводился"
        
        verdict = self.analysis_results["verdict"]
        risk_score = self.analysis_results["risk_score"]
        threat_type = self.analysis_results["threat_classification"].get("type", "Неизвестно")
        
        summary = f"""
╔══════════════════════════════════════════════════╗
║           REDSAND SECURE v2.0 - ОТЧЕТ            ║
╠══════════════════════════════════════════════════╣
║ Вердикт:         {verdict:<20} ║
║ Уровень риска:   {risk_score}/100{'':12} ║
║ Тип угрозы:      {threat_type:<20} ║
╚══════════════════════════════════════════════════╝
        """
        
        return summary


def main():
    """Точка входа"""
    if len(sys.argv) < 2:
        print("RedSand Secure v2.0 - Система анализа вредоносного ПО")
        print("Использование:")
        print("  python redsand_secure.py <путь_к_файлу> [--poly]")
        print("  python redsand_secure.py --generate-test-samples")
        print("\nПримеры:")
        print("  python redsand_secure.py suspicious.exe")
        print("  python redsand_secure.py malware.dll --poly")
        sys.exit(1)
    
    # Создание экземпляра системы
    sandbox = RedSandSecure()
    
    try:
        if sys.argv[1] == "--generate-test-samples":
            print("🧪 Генерация тестовых образцов...")
            from test_samples.generate_all import generate_all_samples
            generate_all_samples()
            print("✅ Тестовые образцы созданы в папке test_samples/")
        else:
            sample_path = sys.argv[1]
            poly_mode = "--poly" in sys.argv
            
            if not os.path.exists(sample_path):
                print(f"❌ Файл не найден: {sample_path}")
                sys.exit(1)
            
            # Запуск анализа
            results, reports = sandbox.analyze_sample(sample_path, generate_poly_variants=poly_mode)
            
            # Вывод сводки
            print(sandbox.get_analysis_summary())
            
            # Вывод путей к отчетам
            print("\n📁 Отчеты сохранены:")
            for report_type, report_path in reports.items():
                print(f"  {report_type}: {report_path}")
    
    except KeyboardInterrupt:
        print("\n⚠️  Анализ прерван пользователем")
        sandbox.panic_button.trigger()
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
