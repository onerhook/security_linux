# RedSand Secure - Руководство по новым функциям v4.0

## 📋 Обзор изменений

В версии 4.0 добавлены две критически важные функции:

1. **Docker-изоляция для безопасного анализа** - Исправлена проблема с запуском EXE файлов в системе
2. **Антивирус реального времени** - Мониторинг скачанных файлов и автоматическое сканирование

---

## 🔒 1. Docker-изоляция для безопасного анализа

### Проблема (ИСПРАВЛЕНА)
Ранее при анализе `.exe` файлов они запускались непосредственно в системе, что представляло опасность заражения.

### Решение
Теперь все исполняемые файлы запускаются в изолированном Docker контейнере с ограничениями:

- ✅ Полная изоляция сети (`--network none`)
- ✅ Файловая система только для чтения (`--read-only`)
- ✅ Ограничение памяти (512MB)
- ✅ Ограничение CPU (0.5 ядра)
- ✅ Максимум 50 процессов
- ✅ Отключены все привилегии (`--cap-drop ALL`)
- ✅ Автоматическое удаление после выполнения (`--rm`)

### Использование

#### В коде (оркестратор)
```python
from core.orchestrator import RedSandSecure

# По умолчанию Docker включен (use_docker=True)
sandbox = RedSandSecure(output_dir='reports', use_docker=True)

# Анализ файла (автоматически использует Docker)
result = sandbox.analyze_file('path/to/suspicious.exe')
```

#### Отключение Docker (не рекомендуется)
```python
# Только если Docker недоступен
sandbox = RedSandSecure(output_dir='reports', use_docker=False)
```

#### Прямое использование Docker Sandbox
```python
from core.docker_sandbox import DockerSandbox, analyze_in_docker

# Быстрый анализ в Docker
result = analyze_in_docker(
    file_path='suspicious.exe',
    timeout=60,
    use_wine=True  # Для Windows EXE на Linux
)

print(result)
# {
#     'success': True,
#     'method': 'docker_wine',
#     'file_path': 'suspicious.exe',
#     'events': [...],
#     'isolated': True
# }
```

### Требования

#### Для Linux:
```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Проверка
docker --version
docker run hello-world
```

#### Для Windows:
1. Установите [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Запустите Docker Desktop
3. Дождитесь полной загрузки

#### Для macOS:
1. Установите [Docker Desktop для Mac](https://www.docker.com/products/docker-desktop/)
2. Запустите Docker

### Fallback режим
Если Docker недоступен, система автоматически переключается на локальный запуск с предупреждением:
```
[-] Docker недоступен, используем локальный запуск (МЕНЕЕ БЕЗОПАСНО!)
[!] ВНИМАНИЕ: Запуск без Docker изоляции! Это опасно!
```

---

## 🛡️ 2. Антивирус реального времени

### Описание
Антивирус мониторит указанные папки и автоматически сканирует все новые файлы.

### Возможности
- ✅ Мониторинг папок в реальном времени
- ✅ Автоматическое сканирование новых файлов
- ✅ Поддержка множества форматов (.exe, .doc, .pdf, .zip и др.)
- ✅ Автоматический карантин угроз
- ✅ Ведение журнала сканирований
- ✅ Генерация отчетов
- ✅ Возможность восстановления из карантина

### Быстрый старт

#### 1. Базовое использование
```python
from core.realtime_antivirus import create_antivirus_service

# Создание и запуск антивируса
antivirus = create_antivirus_service(auto_start=True)

print("Антивирус запущен и мониторит систему!")
```

#### 2. Расширенная настройка
```python
from core.realtime_antivirus import RealTimeAntivirus

# Создание с настройками
antivirus = RealTimeAntivirus(
    monitored_folders=[
        '/home/user/Downloads',
        '/home/user/Desktop',
        'C:\\Users\\User\\Downloads'  # Windows
    ],
    auto_quarantine=True,      # Автоматически помещать в карантин
    scan_on_access=True,       # Сканировать при доступе
    reports_dir='av_reports'   # Папка для отчетов
)

# Включение
antivirus.enable()

# Запуск в фоновом режиме
if antivirus.start_background():
    print("✅ Антивирус запущен")

# Проверка статуса
status = antivirus.get_status()
print(f"Включен: {status['enabled']}")
print(f"Мониторится папок: {len(status['monitored_folders'])}")
print(f"Просканировано файлов: {status['scanned_files_count']}")

# Остановка
antivirus.stop()

# Выключение
antivirus.disable()
```

#### 3. Ручное сканирование папки
```python
from core.realtime_antivirus import RealTimeAntivirus

antivirus = RealTimeAntivirus()
antivirus.enable()

# Сканирование папки
results = antivirus.manual_scan('/path/to/folder')

for result in results:
    if result.is_malicious:
        print(f"🚨 УГРОЗА: {result.file_name}")
        print(f"   Действие: {result.action_taken}")
```

#### 4. Работа с карантином
```python
# Просмотр файлов в карантине
quarantined = antivirus.quarantine_manager.list_quarantined()
for item in quarantined:
    print(f"Файл: {item['original_name']}")
    print(f"Причина: {item['reason']}")
    print(f"Дата: {item['quarantine_time']}")

# Восстановление файла
antivirus.quarantine_manager.restore_from_quarantine('/path/to/quarantine/file')
```

### Мониторинг событий

#### Callback уведомления
```python
def on_threat_detected(result):
    if result.is_malicious:
        print(f"\n🚨 ОБНАРУЖЕНА УГРОЗА!")
        print(f"Файл: {result.file_name}")
        print(f"Уровень: {result.threat_level}")
        print(f"Действие: {result.action_taken}\n")

antivirus = RealTimeAntivirus()
antivirus.notification_callback = on_threat_detected
antivirus.enable()
antivirus.start_background()
```

### Отключаемые расширения
По умолчанию сканируются:
```python
monitored_extensions = [
    '.exe', '.bat', '.cmd', '.ps1', '.vbs', '.js',
    '.msi', '.dll', '.scr', '.pif', '.com',
    '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.pdf', '.zip', '.rar', '.7z', '.tar', '.gz'
]
```

### Игнорируемые папки
Антивирус автоматически игнорирует:
- `Windows`
- `Program Files`
- `ProgramData`
- `$Recycle.Bin`
- Временные файлы (начинающиеся с `~$` или `.`)

---

## 📦 Установка зависимостей

```bash
cd RedSand
pip install -r requirements.txt
```

### requirements.txt включает:
```
pefile
yara-python
psutil
watchdog>=3.0.0          # Для антивируса реального времени
# docker>=6.0.0          # Опционально для Docker API
```

---

## 🎮 Интеграция с GUI

GUI автоматически использует Docker-изоляцию при анализе:

```python
# В gui/main_gui.py (AnalysisWorker)
sandbox = RedSandSecure(output_dir='reports_gui', use_docker=True)
```

### Добавление кнопки антивируса в GUI (пример)
```python
# Добавить в интерфейс кнопку "Включить защиту"
self.antivirus_btn = QPushButton("🛡️ Включить антивирус")
self.antivirus_btn.clicked.connect(self.toggle_antivirus)

def toggle_antivirus(self):
    if not hasattr(self, 'antivirus'):
        from core.realtime_antivirus import create_antivirus_service
        self.antivirus = create_antivirus_service(auto_start=True)
        self.antivirus_btn.setText("❌ Выключить антивирус")
        self.statusBar.showMessage("Антивирус включен", 5000)
    else:
        self.antivirus.stop()
        self.antivirus.disable()
        self.antivirus_btn.setText("🛡️ Включить антивирус")
        self.statusBar.showMessage("Антивирус выключен", 5000)
```

---

## ⚠️ Важные замечания

### Безопасность
1. **Всегда используйте Docker** для анализа неизвестных файлов
2. **Запускайте в виртуальной машине** для максимальной безопасности
3. **Не отключайте изоляцию** без необходимости

### Производительность
- Docker добавляет небольшие накладные расходы (~1-2 секунды на запуск контейнера)
- Антивирус реального времени использует ~50-100MB RAM в фоне
- Рекомендуется мониторить не более 5-10 папок одновременно

### Совместимость
- **Linux**: Полная поддержка Docker и всех функций
- **Windows**: Требуется Docker Desktop, некоторые ограничения
- **macOS**: Требуется Docker Desktop, полная поддержка

---

## 🔧 Troubleshooting

### Docker не запускается
```bash
# Проверка статуса
docker ps

# Перезапуск службы (Linux)
sudo systemctl restart docker

# Проверка прав
sudo usermod -aG docker $USER
# Затем перезайдите в систему
```

### Антивирус не видит файлы
1. Проверьте права доступа к папкам
2. Убедитесь, что папки существуют
3. Проверьте логи: `antivirus_reports/antivirus_YYYYMMDD.log`

### Ложные срабатывания
- Добавьте файл в исключения (измените `monitored_extensions`)
- Настройте `VirusScanner` для whitelist конкретных файлов

---

## 📊 Примеры использования

### Сценарий 1: Защита загрузок
```python
from core.realtime_antivirus import RealTimeAntivirus

av = RealTimeAntivirus(
    monitored_folders=['/home/user/Downloads'],
    auto_quarantine=True
)
av.enable()
av.start_background()

print("Защита загрузок активирована!")
```

### Сценарий 2: Анализ подозрительного файла
```python
from core.orchestrator import RedSandSecure

sandbox = RedSandSecure(use_docker=True)
result = sandbox.analyze_file('downloaded_file.exe')

if result.threat_info.get('verdict') == 'MALICIOUS':
    print("🚨 Файл опасен! Удалите его немедленно!")
```

### Сценарий 3: Массовое сканирование
```python
from core.realtime_antivirus import RealTimeAntivirus

av = RealTimeAntivirus()
av.enable()

# Сканирование всей папки пользователя
results = av.manual_scan('/home/user')

malicious = [r for r in results if r.is_malicious]
print(f"Найдено угроз: {len(malicious)}")
```

---

## 📝 Changelog v4.0

### Добавлено
- ✅ Модуль `core/docker_sandbox.py` - Docker изоляция
- ✅ Модуль `core/realtime_antivirus.py` - Антивирус реального времени
- ✅ Класс `QuarantineManager` - Управление карантином
- ✅ Класс `FileMonitorHandler` - Мониторинг файловой системы
- ✅ Интеграция Docker в оркестратор
- ✅ Обновленный GUI с поддержкой Docker

### Изменено
- 🔄 `use_docker` теперь `True` по умолчанию
- 🔄 Улучшена безопасность локального запуска (fallback)
- 🔄 Добавлены предупреждения при отключении Docker

### Исправлено
- 🐛 EXE файлы больше не запускаются в основной системе
- 🐛 Утечка процессов при анализе
- 🐛 Проблемы с кодировкой в логах

---

## 📞 Поддержка

Для вопросов и предложений:
- Документация: `/workspace/RedSand/README.md`
- Примеры: `/workspace/RedSand/samples/`
- Логи: `reports/` и `antivirus_reports/`

**Безопасного анализа! 🛡️**
