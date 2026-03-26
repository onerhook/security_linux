# 📖 RedSand - Примеры использования

## Быстрый старт

### Базовый анализ файла

```bash
python redsand.py suspicious.exe
```

Вывод:
```
🛡️ RedSand - Начало анализа
📁 Файл: suspicious.exe

[1/5] 🔬 Статический анализ...
    ✓ Хеш SHA256: a3f2b8c9d1e4f5...

[2/5] 🎭 Применение техник обхода песочницы...
    ✓ Эмулировано процессов: 5

[3/5] 🌐 Запуск сетевой эмуляции...
    ✓ DNS сервер: запущен
    ✓ HTTP сервер: запущен

[4/5] ⚡ Выполнение образца...

[5/5] 💾 Анализ памяти...

📊 Вердикт: MALICIOUS
⚠️ Оценка риска: 85/100
```

## Сценарии использования

### Сценарий 1: Анализ подозрительного email вложения

```python
from redsand import RedSandOrchestrator

# Конфигурация для быстрого анализа
config = {
    "analysis_timeout": 120,  # 2 минуты
    "memory_dump_enabled": False,
    "network_emulation": True,
    "anti_sandbox_evasion": True,
    "output_dir": "email_analysis"
}

analyzer = RedSandOrchestrator(config)
results = analyzer.analyze("C:\\Users\\Admin\\Downloads\\invoice.exe")

# Проверка вердикта
if results["verdict"]["risk_score"] >= 70:
    print("⚠️ УГРОЗА ОБНАРУЖЕНА - заблокировать отправителя")
    # Добавить IOC в черный список
    for ioc in results["verdict"]["indicators"]:
        print(f"  - {ioc}")
```

### Сценарий 2: Пакетный анализ образцов

```python
import os
from pathlib import Path
from redsand import RedSandOrchestrator

samples_dir = "C:\\quarantine"
reports_dir = "batch_reports"

config = {
    "analysis_timeout": 180,
    "output_dir": reports_dir
}

analyzer = RedSandOrchestrator(config)

# Анализ всех exe файлов
for file in Path(samples_dir).glob("*.exe"):
    print(f"\n{'='*60}")
    print(f"Анализ: {file.name}")
    print('='*60)
    
    results = analyzer.analyze(str(file))
    
    # Краткий отчет
    print(f"Вердикт: {results['verdict']['label']}")
    print(f"Риск: {results['verdict']['risk_score']}/100")
```

### Сценарий 3: Мониторинг в реальном времени

```python
import time
import threading
from redsand import RedSandOrchestrator

class RealTimeMonitor:
    def __init__(self, watch_folder):
        self.watch_folder = watch_folder
        self.analyzer = RedSandOrchestrator()
        self.processed_files = set()
        
    def start(self):
        print(f"[*] Мониторинг папки: {self.watch_folder}")
        while True:
            for file in Path(self.watch_folder).glob("*.exe"):
                if file not in self.processed_files:
                    self.processed_files.add(file)
                    threading.Thread(
                        target=self.analyze_file,
                        args=(file,)
                    ).start()
            time.sleep(5)
    
    def analyze_file(self, file_path):
        try:
            results = self.analyzer.analyze(str(file_path))
            
            if results["verdict"]["risk_score"] >= 70:
                print(f"\n🚨 ТРЕВОГА! Обнаружено вредоносное ПО: {file_path}")
                # Автоматическое действие: переместить в карантин
                # quarantine.move(file_path)
        except Exception as e:
            print(f"[!] Ошибка анализа {file_path}: {e}")

# Запуск монитора
monitor = RealTimeMonitor("C:\\Downloads")
monitor.start()
```

## Работа с модулями

### Статический анализ

```python
from modules.static_analyzer import StaticAnalyzer

analyzer = StaticAnalyzer(yara_rules_path="rules")

# Полный анализ
result = analyzer.analyze("malware.exe")

# Доступ к результатам
print(f"MD5: {result['hashes']['md5']}")
print(f"SHA256: {result['hashes']['sha256']}")
print(f"PE файл: {result['pe_info']['is_pe']}")

# Подозрительные флаги
for flag in result['pe_info'].get('suspicious_flags', []):
    print(f"⚠️ {flag}")

# YARA совпадения
for match in result['yara_matches']:
    print(f"🎯 YARA правило: {match['rule_name']}")
```

### Сетевая эмуляция

```python
from modules.network_emulator import NetworkEmulator

emulator = NetworkEmulator()

# Запуск эмуляции
results = emulator.start_emulation()
print("DNS сервер:", results['dns_server']['started'])
print("HTTP сервер:", results['http_server']['started'])

# Ждем выполнения образца...
import time
time.sleep(10)

# Анализ поведения
behavior = emulator.analyze_network_behavior()
print(f"Всего подключений: {behavior['total_connections']}")
print(f"DNS запросов: {len(behavior['dns_queries'])}")
print(f"Подозрительных доменов: {len(behavior['suspicious_domains'])}")
print(f"Оценка риска: {behavior['risk_score']}")

# Остановка
emulator.stop_emulation()
```

### Анти-песочница

```python
from modules.anti_sandbox import AntiSandbox

evasion = AntiSandbox()

# Применение всех техник
results = evasion.apply_evasion()

print("Эмулировано процессов:", len(results['process_emulation']))
print("Изменений реестра:", len(results['registry_changes']))
print("Длительность задержки:", results['time_manipulation']['sleep_duration'])
```

### Анализ памяти

```python
from modules.memory_analyzer import MemoryAnalyzer

analyzer = MemoryAnalyzer()

# Создание дампа процесса (требуется PID и права админа)
dump_result = analyzer.create_process_dump(
    pid=1234,
    output_path="dumps/process_1234.dmp"
)

if dump_result['success']:
    print(f"Дамп создан: {dump_result['size']} байт")
    
    # Анализ дампа
    analysis = analyzer.analyze_memory_dump("dumps/process_1234.dmp")
    
    print("Найдено URL:", len(analysis['iocs']['urls']))
    print("Найдено IP:", len(analysis['iocs']['ips']))
    print("Подозрительные строки:", len(analysis['iocs']['suspicious_strings']))

# Обнаружение инъекций
injection_result = analyzer.detect_injections(pid=1234)
print(f"Подозрительных регионов: {len(injection_result['suspicious_regions'])}")
print(f"Оценка риска: {injection_result['risk_score']}")
```

## Интерпретация результатов

### Вердикты

| Вердикт | Описание | Действия |
|---------|----------|----------|
| **MALICIOUS** (70-100) | Обнаружены явные признаки вредоносного ПО | Изолировать, удалить, проверить другие системы |
| **SUSPICIOUS** (40-69) | Выявлены подозрительные действия | Дополнительный анализ, мониторинг |
| **SAFE** (0-39) | Угроз не обнаружено | Разрешить, добавить в белый список |

### Индикаторы компрометации (IOC)

Пример извлечения IOC:

```python
results = analyzer.analyze("sample.exe")

# Сетевые IOC
for domain in results.get('network_analysis', {}).get('behavior', {}).get('suspicious_domains', []):
    print(f"Заблокировать домен: {domain}")

# Файловые IOC
static = results.get('static_analysis', {})
if static.get('pe_info', {}).get('is_pe'):
    print(f"Хеш для блокировки: {static['hashes']['sha256']}")

# MITRE ATT&CK тактики
print("\nОбнаруженные тактики:")
for tactic in results.get('mitre_attack', []):
    print(f"  - {tactic['id']}: {tactic['name']}")
```

## Интеграция с другими системами

### Экспорт в STIX/TAXII

```python
import json
from datetime import datetime

def export_to_stix(results):
    """Конвертация результатов в формат STIX"""
    stix_package = {
        "type": "bundle",
        "id": f"bundle--{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "objects": [
            {
                "type": "indicator",
                "spec_version": "2.1",
                "id": f"indicator--{results['sample_info']['name']}",
                "pattern": f"[file:hashes.MD5 = '{results['static_analysis']['hashes']['md5']}']",
                "pattern_type": "stix",
                "valid_from": datetime.now().isoformat()
            }
        ]
    }
    return json.dumps(stix_package, indent=2)

# Использование
stix_output = export_to_stix(results)
with open("report.stix", "w") as f:
    f.write(stix_output)
```

### Отправка в SIEM

```python
import requests

def send_to_siem(results, siem_url):
    """Отправка результатов в SIEM систему"""
    payload = {
        "source": "RedSand",
        "event_type": "malware_analysis",
        "timestamp": results["timestamp"],
        "file_name": results["sample_info"]["name"],
        "verdict": results["verdict"]["label"],
        "risk_score": results["verdict"]["risk_score"],
        "indicators": results["verdict"]["indicators"]
    }
    
    response = requests.post(siem_url, json=payload)
    return response.status_code == 200

# Использование
send_to_siem(results, "https://siem.company.com/api/events")
```

## Советы и лучшие практики

1. **Всегда используйте VM** - Никогда не анализируйте на основной системе
2. **Делайте снапшоты** - Восстанавливайте чистое состояние после каждого анализа
3. **Обновляйте YARA правила** - Регулярно скачивайте новые сигнатуры
4. **Логируйте всё** - Сохраняйте все отчеты для истории
5. **Автоматизируйте** - Используйте пакетный анализ для больших объемов
6. **Проверяйте ложные срабатывания** - Высокий риск не всегда означает malware

---

**RedSand** - Эффективный анализ угроз 🛡️
