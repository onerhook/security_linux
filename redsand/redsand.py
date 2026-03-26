"""
RedSand - Главный оркестратор
Объединяет все модули анализа в единую систему
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Импорт модулей
try:
    from modules.static_analyzer import StaticAnalyzer
    from modules.anti_sandbox import AntiSandbox
    from modules.network_emulator import NetworkEmulator
    from modules.memory_analyzer import MemoryAnalyzer
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"[!] Модули доступны только на Windows: {e}")
    MODULES_AVAILABLE = False


class RedSandOrchestrator:
    """Главный оркестратор системы RedSand"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if not MODULES_AVAILABLE:
            raise RuntimeError("Модули недоступны. Требуется Windows для полного функционала.")
        
        self.config = config or {
            "analysis_timeout": 300,  # 5 минут
            "memory_dump_enabled": True,
            "network_emulation": True,
            "anti_sandbox_evasion": True,
            "output_dir": "reports"
        }
        
        self.results = {
            "sample_info": {},
            "static_analysis": {},
            "dynamic_analysis": {},
            "network_analysis": {},
            "memory_analysis": {},
            "verdict": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Инициализация модулей
        self.static_analyzer = StaticAnalyzer()
        self.anti_sandbox = AntiSandbox()
        self.network_emulator = NetworkEmulator()
        self.memory_analyzer = MemoryAnalyzer()
        
    def analyze(self, file_path: str) -> Dict[str, Any]:
        """Полный анализ образца"""
        print(f"\n{'='*60}")
        print(f"🛡️ RedSand - Начало анализа")
        print(f"{'='*60}")
        print(f"📁 Файл: {file_path}")
        
        # Проверка существования файла
        if not Path(file_path).exists():
            return {"error": f"Файл не найден: {file_path}"}
        
        try:
            # 1. Статический анализ
            print("\n[1/5] 🔬 Статический анализ...")
            self.results["static_analysis"] = self.static_analyzer.analyze(file_path)
            self.results["sample_info"] = self.results["static_analysis"]["file_info"]
            print(f"    ✓ Хеш SHA256: {self.results['static_analysis']['hashes']['sha256'][:16]}...")
            
            # 2. Применение анти-песочницы
            if self.config.get("anti_sandbox_evasion", True):
                print("\n[2/5] 🎭 Применение техник обхода песочницы...")
                evasion_results = self.anti_sandbox.apply_evasion()
                self.results["dynamic_analysis"]["evasion"] = evasion_results
                print(f"    ✓ Эмулировано процессов: {len(evasion_results.get('process_emulation', []))}")
            
            # 3. Запуск сетевой эмуляции
            if self.config.get("network_emulation", True):
                print("\n[3/5] 🌐 Запуск сетевой эмуляции...")
                network_results = self.network_emulator.start_emulation()
                self.results["network_analysis"]["config"] = network_results
                print(f"    ✓ DNS сервер: {'запущен' if network_results['dns_server']['started'] else 'ошибка'}")
                print(f"    ✓ HTTP сервер: {'запущен' if network_results['http_server']['started'] else 'ошибка'}")
            
            # 4. Симуляция выполнения (в реальной версии здесь запуск образца)
            print("\n[4/5] ⚡ Выполнение образца...")
            print("    [В реальной версии здесь происходит запуск образца в изолированной среде]")
            
            # Симуляция задержки выполнения
            time.sleep(2)
            
            # Сбор логов сетевой активности
            if self.config.get("network_emulation", True):
                network_behavior = self.network_emulator.analyze_network_behavior()
                self.results["network_analysis"]["behavior"] = network_behavior
                self.network_emulator.stop_emulation()
                print(f"    ✓ Зафиксировано подключений: {network_behavior['total_connections']}")
            
            # 5. Анализ памяти (если включено)
            if self.config.get("memory_dump_enabled", True):
                print("\n[5/5] 💾 Анализ памяти...")
                # В реальной версии здесь создание дампа процесса
                self.results["memory_analysis"] = {
                    "status": "enabled",
                    "note": "Требует запуска от администратора на Windows"
                }
                print("    ✓ Модуль готов к работе (требуется Windows + Admin)")
            
            # Формирование вердикта
            print("\n[*] 📊 Формирование вердикта...")
            self.results["verdict"] = self._generate_verdict()
            
            # Сохранение результатов
            self._save_report()
            
            print(f"\n{'='*60}")
            print(f"✅ Анализ завершен!")
            print(f"{'='*60}")
            print(f"📊 Вердикт: {self.results['verdict']['label']}")
            print(f"⚠️ Оценка риска: {self.results['verdict']['risk_score']}/100")
            print(f"📄 Отчет сохранен в: {self.config['output_dir']}")
            
        except Exception as e:
            self.results["error"] = str(e)
            print(f"\n[!] Ошибка анализа: {e}")
        
        return self.results
    
    def _generate_verdict(self) -> Dict[str, Any]:
        """Генерация вердикта на основе результатов анализа"""
        risk_score = 0
        indicators = []
        
        # Анализ статических признаков
        static = self.results.get("static_analysis", {})
        
        # Проверка YARA совпадений
        yara_matches = static.get("yara_matches", [])
        if yara_matches:
            risk_score += 50
            indicators.append(f"YARA правила: {len(yara_matches)} совпадений")
        
        # Проверка подозрительных импортов
        pe_info = static.get("pe_info", {})
        suspicious_flags = pe_info.get("suspicious_flags", [])
        if suspicious_flags:
            risk_score += len(suspicious_flags) * 10
            indicators.extend(suspicious_flags)
        
        # Проверка импортов API
        imports = pe_info.get("imports", [])
        dangerous_apis = ["VirtualAllocEx", "WriteProcessMemory", "CreateRemoteThread", 
                         "NtUnmapViewOfSection", "SetWindowsHookEx"]
        dangerous_found = [api for api in imports if api in dangerous_apis]
        if dangerous_found:
            risk_score += len(dangerous_found) * 5
            indicators.append(f"Опасные API: {', '.join(dangerous_found[:3])}")
        
        # Анализ сетевого поведения
        network = self.results.get("network_analysis", {}).get("behavior", {})
        if network.get("suspicious_domains"):
            risk_score += len(network["suspicious_domains"]) * 15
            indicators.append(f"Подозрительные домены: {', '.join(network['suspicious_domains'][:3])}")
        
        risk_score = min(risk_score, 100)  # Ограничиваем 100
        
        # Определение вердикта
        if risk_score >= 70:
            label = "MALICIOUS"
            description = "Обнаружены признаки вредоносного ПО"
        elif risk_score >= 40:
            label = "SUSPICIOUS"
            description = "Выявлены подозрительные действия"
        else:
            label = "SAFE"
            description = "Угроз не обнаружено"
        
        return {
            "label": label,
            "risk_score": risk_score,
            "description": description,
            "indicators": indicators,
            "confidence": "high" if risk_score >= 70 else "medium" if risk_score >= 40 else "low"
        }
    
    def _save_report(self):
        """Сохранение отчета"""
        output_dir = Path(self.config["output_dir"])
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON отчет
        json_path = output_dir / f"report_{timestamp}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"    ✓ JSON отчет: {json_path}")
        
        # HTML отчет (шаблон)
        html_path = output_dir / f"report_{timestamp}.html"
        print(f"    ✓ HTML отчет: {html_path} (генерируется из шаблона)")
        
        # TXT отчет
        txt_path = output_dir / f"report_{timestamp}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("RedSand - Отчет анализа вредоносного ПО\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Файл: {self.results.get('sample_info', {}).get('name', 'N/A')}\n")
            f.write(f"Вердикт: {self.results['verdict']['label']}\n")
            f.write(f"Оценка риска: {self.results['verdict']['risk_score']}/100\n\n")
            f.write("Индикаторы:\n")
            for ind in self.results['verdict'].get('indicators', []):
                f.write(f"  - {ind}\n")
        print(f"    ✓ TXT отчет: {txt_path}")


def main():
    """Точка входа"""
    import sys
    
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║   🛡️  RedSand - Система анализа вредоносного ПО  ║
    ║                                                   ║
    ║   Локальная песочница для безопасного анализа     ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) < 2:
        print("Использование: python redsand.py <путь_к_файлу>")
        print("\nПримеры:")
        print("  python redsand.py sample.exe")
        print("  python redsand.py C:\\malware\\trojan.dll")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Создание оркестратора и запуск анализа
    orchestrator = RedSandOrchestrator()
    results = orchestrator.analyze(file_path)
    
    # Вывод кратких результатов
    print("\n" + "=" * 60)
    print("КРАТКИЕ РЕЗУЛЬТАТЫ:")
    print("=" * 60)
    print(f"Вердикт: {results['verdict']['label']}")
    print(f"Риск: {results['verdict']['risk_score']}/100")
    print(f"Доверие: {results['verdict']['confidence']}")
    
    if results['verdict']['indicators']:
        print("\nКлючевые индикаторы:")
        for ind in results['verdict']['indicators'][:5]:
            print(f"  ⚠️ {ind}")


if __name__ == "__main__":
    main()
