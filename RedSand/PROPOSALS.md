# 🔮 RedSand Secure - Предложения по Развитию и Улучшению

## 📋 Содержание
1. [Архитектурные Улучшения](#архитектурные-улучшения)
2. [Функциональные Расширения](#функциональные-расширения)
3. [Оптимизации Производительности](#оптимизации-производительности)
4. [Безопасность](#безопасность)
5. [UI/UX Улучшения](#uiux-улучшения)
6. [DevOps и Инфраструктура](#devops-и-инфраструктура)
7. [Приоритеты Реализации](#приоритеты-реализации)

---

## 🏗️ Архитектурные Улучшения

### 1.1 Микросервисная Архитектура
**Текущее состояние:** Монолитная архитектура с прямыми импортами модулей.

**Предложение:**
```python
# Разделение на независимые сервисы
services/
├── analyzer_service/      # Статический/динамический анализ
├── classifier_service/    # ML классификация угроз
├── report_service/        # Генерация отчетов
├── api_gateway/          # REST API шлюз
└── message_queue/        # RabbitMQ/Kafka для асинхронности
```

**Преимущества:**
- Масштабируемость каждого компонента
- Отказоустойчивость
- Возможность распределенного анализа
- Легкое обновление отдельных модулей

### 1.2 Контейнеризация (Docker)
```dockerfile
# Dockerfile для изолированного анализа
FROM python:3.10-slim

# Установка зависимостей для анализа
RUN apt-get update && apt-get install -y \
    libffi-dev \
    libssl-dev \
    pe-utils \
    yara \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запуск в изолированном режиме
CMD ["python", "redsand_secure.py"]
```

**Преимущества:**
- Полная изоляция от хост-системы
- Воспроизводимость окружения
- Быстрое развертывание
- Снапшоты состояния VM

### 1.3 Plugin System
**Предложение:** Система плагинов для расширяемости

```python
# plugins/base_plugin.py
class AnalysisPlugin(ABC):
    @abstractmethod
    def analyze(self, file_path: str) -> dict:
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        pass

# plugins/custom_yara.py
class CustomYaraPlugin(AnalysisPlugin):
    def __init__(self, rules_path: str):
        self.rules = self.load_rules(rules_path)
    
    def analyze(self, file_path: str) -> dict:
        # Кастомная логика YARA
        pass
    
    def get_priority(self) -> int:
        return 10
```

---

## 🚀 Функциональные Расширения

### 2.1 Машинное Обучение для Классификации
**Текущее состояние:** Эвристическая классификация на основе ключевых слов.

**Предложение:** ML-модель для точной классификации

```python
# modules/ml_classifier.py
from sklearn.ensemble import RandomForestClassifier
import joblib

class MLThreatClassifier:
    def __init__(self, model_path: str = None):
        if model_path:
            self.model = joblib.load(model_path)
        else:
            self.model = RandomForestClassifier(n_estimators=100)
    
    def extract_features(self, static_results: dict, dynamic_events: list) -> np.ndarray:
        """Извлечение признаков для модели"""
        features = []
        
        # Статические признаки
        features.append(len(static_results.get('strings', [])))
        features.append(len(static_results.get('pe_info', {}).get('imports', [])))
        features.append(static_results.get('pe_info', {}).get('sections', []))
        
        # Динамические признаки
        features.append(len(dynamic_events))
        features.append(self.count_critical_events(dynamic_events))
        
        return np.array(features).reshape(1, -1)
    
    def predict(self, features: np.ndarray) -> tuple:
        """Предсказание типа угрозы"""
        prediction = self.model.predict(features)[0]
        probability = self.model.predict_proba(features)[0]
        return prediction, max(probability)
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Обучение модели"""
        self.model.fit(X, y)
        joblib.dump(self.model, 'ml_model.pkl')
```

**Датасет для обучения:**
- VirusShare (百万 образцов)
- MalwareBazaar
- TheZoo GitHub repository
- Собственные собранные образцы

### 2.2 Behavioral Graph Visualization
**Предложение:** Визуализация поведения malware в виде графа

```python
# modules/behavior_graph.py
import networkx as nx
import matplotlib.pyplot as plt

class BehaviorGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def add_event(self, event: dict):
        """Добавление события в граф"""
        node_id = f"{event['type']}_{event['timestamp']}"
        self.graph.add_node(
            node_id,
            type=event['type'],
            message=event['message'],
            timestamp=event['timestamp']
        )
        
        # Добавление связей между событиями
        if len(self.graph.nodes) > 1:
            prev_node = list(self.graph.nodes)[-2]
            self.graph.add_edge(prev_node, node_id)
    
    def visualize(self, output_path: str = 'behavior_graph.png'):
        """Визуализация графа"""
        plt.figure(figsize=(20, 15))
        
        pos = nx.spring_layout(self.graph, k=2, iterations=50)
        
        # Цвета для разных типов событий
        color_map = {
            'PROCESS': '#ff6b6b',
            'FILE': '#4ecdc4',
            'REGISTRY': '#ffe66d',
            'NETWORK': '#95a5a6',
            'CRITICAL': '#e74c3c'
        }
        
        node_colors = [
            color_map.get(self.graph.nodes[n]['type'], '#95a5a6')
            for n in self.graph.nodes
        ]
        
        nx.draw(
            self.graph, pos,
            node_color=node_colors,
            with_labels=True,
            node_size=2000,
            font_size=8,
            edge_color='#34495e',
            arrows=True
        )
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
```

### 2.3 Sandbox Detection Evasion (Advanced)
**Предложение:** Продвинутые техники обхода детектирования песочниц

```python
# modules/advanced_evasion.py
import time
import random
import subprocess

class AdvancedEvasion:
    def __init__(self):
        self.user_activity_log = []
    
    def emulate_real_user(self):
        """Эмуляция реального пользователя"""
        # Движение мыши
        self.simulate_mouse_movement()
        
        # Нажатия клавиш
        self.simulate_keyboard_typing()
        
        # Открытие приложений
        self.open_common_applications()
        
        # Браузинг
        self.simulate_web_browsing()
    
    def detect_vm_artifacts(self) -> dict:
        """Детектирование артефактов VM"""
        artifacts = {
            'vm_processes': self.check_vm_processes(),
            'vm_drivers': self.check_vm_drivers(),
            'vm_registry': self.check_vm_registry(),
            'vm_mac_addresses': self.check_vm_mac(),
            'vm_screen_resolution': self.check_screen_resolution()
        }
        return artifacts
    
    def anti_debugging(self):
        """Анти-отладка"""
        # Проверка на отладчик
        if self.is_debugger_present():
            self.trigger_evasion()
        
        # Timing attacks detection
        self.check_timing_anomalies()
    
    def check_vm_processes(self) -> bool:
        """Проверка процессов песочницы"""
        vm_processes = [
            'vmsrvc', 'vmwaretray', 'vmtoolsd',
            'vboxservice', 'vboxtray',
            'prl_cc', 'prl_tools',
            'xenservice', 'qemu-ga'
        ]
        
        import psutil
        running_processes = [p.name().lower() for p in psutil.process_iter(['name'])]
        
        return any(vm_proc in running_processes for vm_proc in vm_processes)
```

### 2.4 Network Traffic Analysis
**Предложение:** Глубокий анализ сетевого трафика

```python
# modules/network_analyzer.py
from scapy.all import sniff, DNS, IP, TCP
import dpkt

class NetworkAnalyzer:
    def __init__(self, interface: str = None):
        self.interface = interface
        self.packets = []
        self.iocs = {
            'domains': set(),
            'ips': set(),
            'urls': set()
        }
    
    def start_capture(self, duration: int = 60):
        """Захват сетевого трафика"""
        self.packets = sniff(
            iface=self.interface,
            timeout=duration,
            filter="tcp or udp or dns"
        )
    
    def extract_iocs(self) -> dict:
        """Извлечение IOC из трафика"""
        for packet in self.packets:
            if packet.haslayer(DNS):
                self.extract_dns_iocs(packet)
            
            if packet.haslayer(IP):
                self.extract_ip_iocs(packet)
            
            if packet.haslayer(TCP):
                self.extract_http_iocs(packet)
        
        return self.iocs
    
    def extract_dns_iocs(self, packet):
        """Извлечение DNS запросов"""
        try:
            query_name = packet[DNS].qd.qname.decode()
            self.iocs['domains'].add(query_name)
            
            # Проверка на DGA (Domain Generation Algorithm)
            if self.is_dga_domain(query_name):
                print(f"[!] Возможный DGA домен: {query_name}")
        except:
            pass
    
    def is_dga_domain(self, domain: str) -> bool:
        """Детектирование DGA доменов"""
        # Простая эвристика
        name = domain.split('.')[0]
        
        # Высокая энтропия
        entropy = self.calculate_entropy(name)
        if entropy > 4.0:
            return True
        
        # Необычное соотношение согласных/гласных
        consonants = sum(1 for c in name.lower() if c in 'bcdfghjklmnpqrstvwxyz')
        vowels = sum(1 for c in name.lower() if c in 'aeiou')
        
        if vowels > 0 and consonants / vowels > 5:
            return True
        
        return False
    
    def calculate_entropy(self, s: str) -> float:
        """Вычисление энтропии Шеннона"""
        import math
        from collections import Counter
        
        prob = [float(cnt) / len(s) for cnt in Counter(s).values()]
        return -sum(p * math.log2(p) for p in prob if p > 0)
```

### 2.5 Memory Dump Analysis
**Предложение:** Анализ дампов памяти

```python
# modules/memory_analyzer.py
import volatility3.framework as volatility
from volatility3.framework import contexts

class MemoryAnalyzer:
    def __init__(self, dump_path: str):
        self.dump_path = dump_path
        self.context = contexts.Context()
    
    def analyze(self) -> dict:
        """Полный анализ памяти"""
        results = {
            'processes': self.list_processes(),
            'dlls': self.list_dlls(),
            'network_connections': self.list_connections(),
            'injected_code': self.detect_injection(),
            'credentials': self.extract_credentials()
        }
        return results
    
    def list_processes(self) -> list:
        """Список процессов в памяти"""
        # Использование volatility3
        pass
    
    def detect_injection(self) -> list:
        """Детектирование инъекций кода"""
        # Поиск аномалий в процессах
        injections = []
        
        # Hollow process detection
        # APC injection detection
        # DLL injection detection
        
        return injections
    
    def extract_credentials(self) -> dict:
        """Извлечение учетных данных из памяти"""
        credentials = {
            'browser_passwords': [],
            'windows_credentials': [],
            'ssh_keys': [],
            'crypto_wallets': []
        }
        
        # Парсинг памяти на наличие чувствительных данных
        pass
        
        return credentials
```

---

## ⚡ Оптимизации Производительности

### 3.1 Multiprocessing для Массового Анализа
```python
# modules/batch_analyzer.py
from multiprocessing import Pool, cpu_count
from concurrent.futures import ProcessPoolExecutor

class BatchAnalyzer:
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or cpu_count()
    
    def analyze_directory(self, dir_path: str) -> list:
        """Анализ всех файлов в директории"""
        files = self.collect_samples(dir_path)
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self.analyze_single, files))
        
        return results
    
    def analyze_single(self, file_path: str) -> dict:
        """Анализ одного файла (в отдельном процессе)"""
        # Изолированный процесс для безопасности
        sandbox = RedSandSecure(output_dir='reports_batch')
        return sandbox.analyze(file_path)
```

### 3.2 Кэширование Результатов
```python
# modules/cache_manager.py
import hashlib
import sqlite3
from datetime import datetime, timedelta

class AnalysisCache:
    def __init__(self, db_path: str = 'analysis_cache.db', ttl_days: int = 30):
        self.db_path = db_path
        self.ttl = timedelta(days=ttl_days)
        self.init_db()
    
    def init_db(self):
        """Инициализация БД кэша"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                hash_sha256 TEXT PRIMARY KEY,
                result BLOB,
                created_at TIMESTAMP,
                access_count INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get(self, file_hash: str) -> Optional[dict]:
        """Получение результата из кэша"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT result, created_at FROM cache
            WHERE hash_sha256 = ? AND created_at > ?
        ''', (file_hash, datetime.now() - self.ttl))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            import pickle
            result = pickle.loads(row[0])
            self.increment_access(file_hash)
            return result
        
        return None
    
    def set(self, file_hash: str, result: dict):
        """Сохранение результата в кэш"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        import pickle
        serialized = pickle.dumps(result)
        
        cursor.execute('''
            INSERT OR REPLACE INTO cache (hash_sha256, result, created_at)
            VALUES (?, ?, ?)
        ''', (file_hash, serialized, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def calculate_hash(self, file_path: str) -> str:
        """Вычисление SHA256 хеша файла"""
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        
        return sha256.hexdigest()
```

### 3.3 Lazy Loading для Больших Файлов
```python
# Оптимизация static_analyzer.py
class OptimizedStaticAnalyzer:
    def _extract_strings_lazy(self, file_path: str, min_length: int = 4):
        """Ленивое извлечение строк (генератор)"""
        with open(file_path, 'rb') as f:
            current_string = []
            
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                
                for byte in chunk:
                    if 32 <= byte <= 126:
                        current_string.append(chr(byte))
                    else:
                        if len(current_string) >= min_length:
                            yield ''.join(current_string)
                        current_string = []
            
            if len(current_string) >= min_length:
                yield ''.join(current_string)
```

---

## 🔒 Безопасность

### 4.1 Process Isolation
```python
# modules/isolated_runner.py
import subprocess
import tempfile
import os

class IsolatedRunner:
    def __init__(self, sandbox_tool: str = 'firejail'):
        self.sandbox_tool = sandbox_tool
    
    def run_isolated(self, file_path: str, timeout: int = 60) -> dict:
        """Запуск файла в изолированной среде"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Создание ограниченного окружения
            cmd = [
                self.sandbox_tool,
                '--private', tmpdir,
                '--net=none',
                '--blacklist=/etc',
                '--blacklist=/home',
                '--read-only=/',
                file_path
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return {
                    'returncode': process.returncode,
                    'stdout': stdout.decode(),
                    'stderr': stderr.decode()
                }
            except subprocess.TimeoutExpired:
                process.kill()
                return {'error': 'Timeout'}
```

### 4.2 Secure Configuration Management
```python
# modules/secure_config.py
from cryptography.fernet import Fernet
import json

class SecureConfig:
    def __init__(self, key_file: str = '.config.key'):
        self.key_file = key_file
        self.cipher = self.load_or_create_key()
    
    def load_or_create_key(self) -> Fernet:
        """Загрузка или создание ключа шифрования"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.key_file, 0o600)
        
        return Fernet(key)
    
    def save_config(self, config: dict, filepath: str):
        """Сохранение зашифрованной конфигурации"""
        encrypted = self.cipher.encrypt(json.dumps(config).encode())
        
        with open(filepath, 'wb') as f:
            f.write(encrypted)
    
    def load_config(self, filepath: str) -> dict:
        """Загрузка расшифрованной конфигурации"""
        with open(filepath, 'rb') as f:
            encrypted = f.read()
        
        decrypted = self.cipher.decrypt(encrypted)
        return json.loads(decrypted.decode())
```

---

## 🎨 UI/UX Улучшения

### 5.1 Dark Mode Toggle
```python
# Добавление переключения темы в GUI
class ThemeManager:
    LIGHT_THEME = """
    QMainWindow { background-color: #ffffff; color: #000000; }
    QPushButton { background-color: #0078d4; color: white; }
    """
    
    DARK_THEME = STYLESHEET  # Текущий темный стиль
    
    def toggle_theme(self, is_dark: bool):
        theme = self.DARK_THEME if is_dark else self.LIGHT_THEME
        QApplication.instance().setStyleSheet(theme)
```

### 5.2 Real-time Progress Visualization
```python
# modules/progress_visualizer.py
from PyQt5.QtCharts import QChart, QLineSeries, QValueAxis

class ProgressChart(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_chart()
    
    def setup_chart(self):
        """Настройка графика прогресса"""
        self.series = QLineSeries()
        self.chart = QChart()
        self.chart.addSeries(self.series)
        
        # Оси
        self.axis_x = QValueAxis()
        self.axis_y = QValueAxis()
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)
    
    def update_progress(self, stage: int, metrics: dict):
        """Обновление графика"""
        self.series.append(stage, metrics.get('score', 0))
```

### 5.3 Drag & Drop Support
```python
# Добавление drag & drop в GUI
class DropZone(QFrame):
    file_dropped = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            DropZone {
                border: 3px dashed #0f3460;
                border-radius: 10px;
                background-color: #16213e;
            }
            DropZone:hover {
                border-color: #e94560;
                background-color: #0f3460;
            }
        """)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.file_dropped.emit(file_path)
```

---

## 🛠️ DevOps и Инфраструктура

### 6.1 CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: RedSand CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest --cov=modules/ tests/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2

  build-docker:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker image
      run: docker build -t redsand:latest .
    
    - name: Push to registry
      run: docker push registry.example.com/redsand:latest
```

### 6.2 Automated Testing Framework
```python
# tests/test_analyzer.py
import pytest
from modules.static_analyzer import StaticAnalyzer

class TestStaticAnalyzer:
    @pytest.fixture
    def analyzer(self):
        return StaticAnalyzer()
    
    def test_calculate_hashes(self, analyzer, sample_file):
        hashes = analyzer._calculate_hashes(sample_file)
        
        assert 'md5' in hashes
        assert 'sha256' in hashes
        assert len(hashes['md5']) == 32
        assert len(hashes['sha256']) == 64
    
    def test_pe_analysis(self, analyzer, pe_file):
        pe_info = analyzer._analyze_pe(pe_file)
        
        assert 'machine' in pe_info
        assert 'sections' in pe_info
        assert len(pe_info['sections']) > 0
    
    @pytest.mark.parametrize("threat_type,expected_score", [
        ('RANSOMWARE', 95),
        ('STEALER', 90),
        ('ADWARE', 45)
    ])
    def test_threat_classification(self, threat_type, expected_score):
        classifier = ThreatClassifier()
        assert classifier.threat_types[threat_type]['risk_base'] == expected_score
```

### 6.3 Monitoring and Logging
```python
# modules/monitoring.py
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge

# Метрики
ANALYSIS_COUNT = Counter(
    'analysis_total',
    'Total number of analyses',
    ['threat_type', 'status']
)

ANALYSIS_DURATION = Histogram(
    'analysis_duration_seconds',
    'Analysis duration',
    buckets=[1, 5, 10, 30, 60, 120, 300, 600]
)

ACTIVE_ANALYSES = Gauge(
    'active_analyses',
    'Number of currently running analyses'
)

class MonitoredAnalyzer(RedSandSecure):
    def analyze(self, file_path: str, **kwargs):
        ACTIVE_ANALYSES.inc()
        start_time = time.time()
        
        try:
            result = super().analyze(file_path, **kwargs)
            
            threat_type = result.get('threat_classification', {}).get('type', 'UNKNOWN')
            ANALYSIS_COUNT.labels(threat_type=threat_type, status='success').inc()
            
            return result
        except Exception as e:
            ANALYSIS_COUNT.labels(threat_type='ERROR', status='failed').inc()
            raise
        finally:
            duration = time.time() - start_time
            ANALYSIS_DURATION.observe(duration)
            ACTIVE_ANALYSES.dec()
```

---

## 📊 Приоритеты Реализации

### 🔴 Критические (Неделя 1-2)
1. ✅ **GUI Interface** -已完成
2. 🔄 **Docker Containerization** - Изоляция среды
3. 🔄 **Configuration File** - Вынос настроек в config.yaml
4. 🔄 **Enhanced Logging** - Структурированные логи (JSON format)

### 🟡 Важные (Неделя 3-4)
5. ⏳ **ML Classifier** - Обучение модели на VirusShare
6. ⏳ **Caching System** - SQLite кэш результатов
7. ⏳ **Batch Analysis** - Multiprocessing поддержка
8. ⏳ **Unit Tests** - Покрытие тестами >80%

### 🟢 Желательные (Месяц 2)
9. ⬜ **Behavior Graph** - Визуализация поведения
10. ⬜ **Network Analysis** - Глубокий анализ трафика
11. ⬜ **REST API** - Веб-интерфейс + API
12. ⬜ **Plugin System** - Архитектура плагинов

### 🔵 Долгосрочные (Месяц 3+)
13. ⬜ **Memory Analysis** - Интеграция с Volatility
14. ⬜ **Distributed Analysis** - Кластерная обработка
15. ⬜ **Threat Intelligence Feed** - Интеграция с OTX, MISP
16. ⬜ **Automated Report Generation** - PDF/DOCX экспорты

---

## 📈 Метрики Успеха

| Метрика | Текущее | Цель | Срок |
|---------|---------|------|------|
| Время анализа | ~60 сек | <30 сек | 1 месяц |
| Точность классификации | ~70% | >90% | 2 месяца |
| Покрытие тестами | 0% | >80% | 1 месяц |
| Поддерживаемые форматы | PE, ELF | +PDF, Office, Scripts | 2 месяца |
| Производительность | 1 файл/мин | 10 файлов/мин | 1 месяц |

---

## 🤝 Contributing Guidelines

1. **Code Style**: PEP8, type hints обязательны
2. **Testing**: Все новые функции должны иметь тесты
3. **Documentation**: Docstrings для всех публичных методов
4. **Security**: Никаких хардкодов секретов, используйте env vars
5. **Performance**: Профилирование перед мерджем оптимизаций

---

## 📚 Ресурсы для Разработки

- [VirusShare](https://virusshare.com/) - Датасет malware
- [MITRE ATT&CK](https://attack.mitre.org/) - Тактики техник
- [MalwareBazaar](https://bazaar.abuse.ch/) - Образцы malware
- [Volatility Foundation](https://www.volatilityfoundation.org/) - Memory forensics
- [YARA Rules](https://github.com/Yara-Rules/rules) - Правила для детектирования

---

**RedSand Secure v2.0** - Развивается сообществом для сообщества 🔐
