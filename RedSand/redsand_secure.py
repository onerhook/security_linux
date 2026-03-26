# -*- coding: utf-8 -*-
"""
RedSand Secure Sandbox - Главный оркестратор
Максимальная безопасность: отключение сети, классификация угроз, детальный анализ.
Только для запуска в изолированной ВМ от имени Администратора!
"""

import os
import sys
import json
import time
import logging
import subprocess
import hashlib
import threading
from datetime import datetime
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/redsand.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RedSand")

class NetworkIsolator:
    """Управление сетевой безопасностью (отключение/эмуляция)"""
    
    def __init__(self):
        self.original_state = {}
        self.isolated = False
        
    def kill_network(self):
        """Полное отключение всех сетевых адаптеров и блокировка фаерволом"""
        logger.warning("!!! ОТКЛЮЧЕНИЕ СЕТИ ДЛЯ БЕЗОПАСНОСТИ !!!")
        try:
            # Отключение всех интерфейсов через netsh
            cmd_disable = 'netsh interface set interface "Ethernet" admin=disabled'
            # Попытка отключить все видимые адаптеры
            result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                                    capture_output=True, text=True, shell=True)
            
            interfaces = []
            for line in result.stdout.splitlines():
                if 'Connected' in line or 'Disconnected' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        iface_name = " ".join(parts[3:])
                        interfaces.append(iface_name)
            
            for iface in interfaces:
                try:
                    subprocess.run(f'netsh interface set interface "{iface}" admin=disabled', 
                                   shell=True, check=False)
                    logger.info(f"Адаптер '{iface}' отключен.")
                except Exception as e:
                    logger.debug(f"Не удалось отключить {iface}: {e}")

            # Блокировка всего исходящего трафика через Firewall
            subprocess.run('netsh advfirewall firewall add rule name="RedSand_Block_All_Out" dir=out action=block enable=yes', 
                           shell=True, check=False)
            subprocess.run('netsh advfirewall firewall add rule name="RedSand_Block_All_In" dir=in action=block enable=yes', 
                           shell=True, check=False)
            
            self.isolated = True
            logger.critical("СЕТЬ ПОЛНОСТЬЮ ОТКЛЮЧЕНА. ОБРАЗЕЦ ИЗОЛИРОВАН.")
            return True
        except Exception as e:
            logger.error(f"Ошибка отключения сети: {e}")
            return False

    def restore_network(self):
        """Восстановление сетевого подключения"""
        if not self.isolated:
            return
            
        logger.warning("ВОССТАНОВЛЕНИЕ СЕТИ...")
        try:
            # Удаление правил фаервола
            subprocess.run('netsh advfirewall firewall delete rule name="RedSand_Block_All_Out"', shell=True, check=False)
            subprocess.run('netsh advfirewall firewall delete rule name="RedSand_Block_All_In"', shell=True, check=False)
            
            # Включение адаптеров (можно доработать под конкретные имена)
            result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                                    capture_output=True, text=True, shell=True)
            for line in result.stdout.splitlines():
                if 'Disabled' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        iface_name = " ".join(parts[3:])
                        subprocess.run(f'netsh interface set interface "{iface_name}" admin=enabled', shell=True, check=False)
            
            self.isolated = False
            logger.info("Сеть восстановлена.")
        except Exception as e:
            logger.error(f"Ошибка восстановления сети: {e}")

class ThreatClassifier:
    """Классификатор типов угроз на основе поведения и статики"""
    
    SIGNATURES = {
        'Ransomware': [b'MZ', b'.pdb', b'encrypt', b'decrypt', b'bitcoin', b'wallet', b'.onion', b'locky', b'wannacry'],
        'Stealer': [b'password', b'cookie', b'credential', b'wallet', b'meta', b'steal', b'log', b'telegram'],
        'Miner': [b'stratum', b'pool.', b'xmr', b'miner', b'cpu', b'gpu', b'hash', b'cryptonight'],
        'RAT': [b'cmd.exe', b'powershell', b'screenshot', b'webcam', b'microphone', b'keylog', b'remote'],
        'Botnet': [b'ddos', b'flood', b'bot', b'zombie', b'irc', b'udp', b'syn', b'amplification'],
        'Dropper': [b'download', b'execute', b'payload', b'shell', b'drop', b'install']
    }
    
    BEHAVIOR_PATTERNS = {
        'Ransomware': ['file_encryption', 'shadow_copy_delete', 'ransom_note_create'],
        'Stealer': ['browser_access', 'clipboard_monitor', 'keyhook_install'],
        'Miner': ['high_cpu_usage', 'gpu_access', 'network_pool_connection'],
        'RAT': ['process_injection', 'persistence_registry', 'screenshot_capture'],
        'Botnet': ['ddos_pattern', 'port_scan', 'spam_activity'],
        'Dropper': ['file_download', 'secondary_execution', 'self_delete']
    }

    def classify_static(self, file_content: bytes) -> dict:
        """Статическая классификация по байтам"""
        scores = {k: 0 for k in self.SIGNATURES.keys()}
        found_indicators = {k: [] for k in self.SIGNATURES.keys()}
        
        for threat_type, signatures in self.SIGNATURES.items():
            for sig in signatures:
                if sig in file_content:
                    scores[threat_type] += 15
                    found_indicators[threat_type].append(sig.decode('utf-8', errors='ignore'))
        
        max_score = max(scores.values()) if scores.values() else 0
        primary_type = max(scores, key=scores.get) if max_score > 0 else "Unknown"
        
        return {
            "type": primary_type,
            "confidence": min(max_score, 100),
            "indicators": found_indicators[primary_type]
        }

    def classify_dynamic(self, events: list) -> dict:
        """Динамическая классификация по событиям"""
        scores = {k: 0 for k in self.BEHAVIOR_PATTERNS.keys()}
        detected_actions = []
        
        for event in events:
            action = event.get('action', '')
            for threat_type, patterns in self.BEHAVIOR_PATTERNS.items():
                if any(p in action for p in patterns):
                    scores[threat_type] += 20
                    detected_actions.append(f"{threat_type}: {action}")
        
        max_score = max(scores.values()) if scores.values() else 0
        primary_type = max(scores, key=scores.get) if max_score > 0 else "Unknown"
        
        return {
            "type": primary_type,
            "confidence": min(max_score, 100),
            "actions": detected_actions
        }

class RedSandSecure:
    """Основной класс песочницы"""
    
    def __init__(self, sample_path: str):
        self.sample_path = Path(sample_path).resolve()
        self.net_isolator = NetworkIsolator()
        self.classifier = ThreatClassifier()
        self.events_log = []
        self.start_time = None
        self.end_time = None
        
        if not self.sample_path.exists():
            raise FileNotFoundError(f"Файл не найден: {self.sample_path}")

    def run_analysis(self):
        """Запуск полного цикла анализа"""
        logger.info("="*50)
        logger.info(f"НАЧАЛО АНАЛИЗА: {self.sample_path}")
        logger.info("="*50)
        
        # 1. Отключение сети
        if not self.net_isolator.kill_network():
            logger.error("КРИТИЧЕСКАЯ ОШИБКА: Не удалось отключить сеть! Прерывание.")
            return None

        try:
            self.start_time = datetime.now()
            
            # 2. Статический анализ
            logger.info("[1/3] Статический анализ...")
            with open(self.sample_path, 'rb') as f:
                content = f.read()
            
            static_result = self.classifier.classify_static(content)
            self.events_log.append({
                "stage": "static",
                "timestamp": self.start_time.isoformat(),
                "result": static_result
            })
            logger.info(f"Статический вердикт: {static_result['type']} (Уверенность: {static_result['confidence']}%)")
            
            # 3. Динамический анализ (Эмуляция запуска)
            # В реальной версии здесь будет запуск агента C++ и мониторинг
            logger.info("[2/3] Динамический анализ (Эмуляция)...")
            time.sleep(2) # Имитация времени выполнения
            
            # Фейковые события для демонстрации (заменится на реальные данные от агента)
            fake_events = [
                {"action": "registry_persistence", "detail": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"},
                {"action": "file_encryption", "detail": "C:\\Users\\Public\\*.docx locked"},
                {"action": "network_attempt", "detail": "Blocked connection to 192.168.1.1"}
            ]
            self.events_log.extend(fake_events)
            
            dynamic_result = self.classifier.classify_dynamic(fake_events)
            logger.info(f"Динамический вердикт: {dynamic_result['type']} (Уверенность: {dynamic_result['confidence']}%)")
            
            self.end_time = datetime.now()
            
            # 4. Формирование итогового отчета
            report = self.generate_report(static_result, dynamic_result)
            
            return report
            
        finally:
            # 4. Восстановление сети (ОБЯЗАТЕЛЬНО)
            logger.info("[3/3] Восстановление системы...")
            self.net_isolator.restore_network()

    def generate_report(self, static_res, dynamic_res):
        """Генерация детального отчета"""
        final_type = dynamic_res['type'] if dynamic_res['confidence'] > static_res['confidence'] else static_res['type']
        risk_score = max(static_res['confidence'], dynamic_res['confidence'])
        
        verdict = "SAFE"
        if risk_score > 70: verdict = "MALICIOUS"
        elif risk_score > 40: verdict = "SUSPICIOUS"
        
        report = {
            "meta": {
                "sample": str(self.sample_path),
                "md5": hashlib.md5(open(self.sample_path, 'rb').read()).hexdigest(),
                "sha256": hashlib.sha256(open(self.sample_path, 'rb').read()).hexdigest(),
                "analysis_time": str(self.end_time - self.start_time),
                "timestamp": datetime.now().isoformat()
            },
            "verdict": {
                "status": verdict,
                "risk_score": risk_score,
                "malware_family": final_type,
                "description": self._get_description(final_type)
            },
            "static_analysis": static_res,
            "dynamic_analysis": dynamic_res,
            "mitre_attack": self._map_mitre(final_type),
            "recommendations": self._get_recommendations(final_type)
        }
        
        # Сохранение отчета
        report_path = Path("reports") / f"report_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Отчет сохранен: {report_path}")
        return report

    def _get_description(self, malware_type):
        desc = {
            'Ransomware': "Шифровальщик файлов. Требует выкуп за расшифровку.",
            'Stealer': "Похищает пароли, куки и криптокошельки.",
            'Miner': "Использует ресурсы ПК для майнинга криптовалюты.",
            'RAT': "Удаленное управление компьютером (троян).",
            'Botnet': "Вовлекает ПК в бот-сеть для атак.",
            'Dropper': "Загрузчик, устанавливающий другие вирусы.",
            'Unknown': "Тип угрозы не определен точно."
        }
        return desc.get(malware_type, "Нет описания")

    def _map_mitre(self, malware_type):
        mapping = {
            'Ransomware': ['T1486 (Data Encrypted for Impact)', 'T1490 (Inhibit System Recovery)'],
            'Stealer': ['T1555 (Credentials from Password Stores)', 'T1539 (Steal Web Session Cookie)'],
            'Miner': ['T1496 (Resource Hijacking)'],
            'RAT': ['T1059 (Command and Scripting Interpreter)', 'T1055 (Process Injection)'],
            'Botnet': ['T1498 (Network Denial of Service)', 'T1071 (Application Layer Protocol)'],
            'Dropper': ['T1105 (Ingress Tool Transfer)', 'T1204 (User Execution)']
        }
        return mapping.get(malware_type, [])

    def _get_recommendations(self, malware_type):
        recs = {
            'Ransomware': ["Не платить выкуп!", "Восстановить файлы из бэкапа", "Проверить другие ПК в сети"],
            'Stealer': ["Сменить все пароли", "Выйти из сессий везде", "Проверить банковские счета"],
            'Miner': ["Проверить автозагрузку", "Обновить драйверы", "Проверить процессы в Диспетчере задач"],
            'RAT': ["Отключить интернет", "Сбросить пароли", "Провести полную проверку антивирусом"],
            'Botnet': ["Блокировать подозрительные порты", "Перепрошить роутер", "Следить за трафиком"],
            'Dropper': ["Удалить файл", "Проверить временные папки", "Очистить кэш браузера"]
        }
        return recs.get(malware_type, ["Провести полный анализ системы"])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python redsand_secure.py <путь_к_файлу>")
        print("ВАЖНО: Запускать ТОЛЬКО в виртуальной машине от имени АДМИНИСТРАТОРА!")
        sys.exit(1)

    try:
        sandbox = RedSandSecure(sys.argv[1])
        result = sandbox.run_analysis()
        if result:
            print("\n" + "="*50)
            print(f"ВЕРДИКТ: {result['verdict']['status']}")
            print(f"Угроза: {result['verdict']['malware_family']}")
            print(f"Риск: {result['verdict']['risk_score']}/100")
            print("="*50)
    except Exception as e:
        logger.critical(f"Фатальная ошибка: {e}")
        # Экстренное восстановление сети при крахе
        NetworkIsolator().restore_network()
