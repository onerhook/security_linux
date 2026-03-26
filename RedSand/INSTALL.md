# RedSand - Инструкция по установке и использованию

## 📋 Описание

RedSand - локальная система анализа вредоносного ПО для Windows с минимальными требованиями к инфраструктуре. Использует ETW (Event Tracing for Windows) для мониторинга и перехвата системных вызовов.

**Важно:** Система работает только на Windows (для анализа образцов). Разработка возможна на Linux.

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    Host System (Linux/Windows)           │
│  ┌───────────────────────────────────────────────────┐  │
│  │           Python Orchestrator                      │  │
│  │  - Управление анализом                             │  │
│  │  - Сбор данных                                     │  │
│  │  - Генерация отчетов                               │  │
│  └───────────────────────────────────────────────────┘  │
│                          ↕                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │              C++ Monitoring Agent                  │  │
│  │  - Перехват API вызовов (MinHook)                 │  │
│  │  - Мониторинг через ETW                           │  │
│  │  - Отправка событий                                │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Требования

### Для запуска анализа (Windows):
- **ОС**: Windows 10/11 (64-bit)
- **Python**: 3.9 или выше
- **Компилятор** (для сборки агента): 
  - Visual Studio 2019+ с C++ workload, ИЛИ
  - MinGW-w64
- **Права администратора**: Требуются для перехвата системных вызовов

### Для разработки (Linux/Windows):
- Python 3.9+
- Git
- Текстовый редактор/IDE

---

## ⚙️ Установка

### Шаг 1: Клонирование репозитория

```bash
git clone <repository_url>
cd RedSand
```

### Шаг 2: Установка Python зависимостей

```bash
pip install psutil yara-python
```

### Шаг 3: Сборка C++ агента (только Windows)

#### Вариант A: Visual Studio

```bash
# Откройте Developer Command Prompt for VS
cd src

# Сборка DLL
cl /LD agent.cpp /Fe:..\bin\RedSandAgent.dll /link kernel32.lib advapi32.lib ws2_32.lib

# Или сборка EXE для тестирования
cl agent.cpp /Fe:..\bin\RedSandAgent.exe /link kernel32.lib advapi32.lib ws2_32.lib
```

#### Вариант B: MinGW-w64

```bash
cd src

# Сборка DLL
g++ -shared -o ../bin/RedSandAgent.dll agent.cpp -lkernel32 -ladvapi32 -lws2_32

# Или сборка EXE
g++ -o ../bin/RedSandAgent.exe agent.cpp -lkernel32 -ladvapi32 -lws2_32
```

### Шаг 4: Проверка установки

```bash
python src/orchestrator.py --help
```

---

## 🚀 Быстрый старт

### Базовый анализ файла

```bash
# Запуск анализа с настройками по умолчанию
python src/orchestrator.py --sample samples/suspicious.exe --output reports/report.json
```

### Анализ с дополнительными опциями

```bash
# Анализ с таймаутом 120 секунд и подробным выводом
python src/orchestrator.py --sample samples/suspicious.exe --timeout 120 --verbose
```

### Пост-обработка отчета

```bash
# Запуск анализатора для углубленного анализа
python src/analyzer.py reports/report.json reports/report_analyzed.json

# Генерация всех форматов отчетов (JSON, HTML, TXT)
python src/reporter.py reports/report_analyzed.json reports
```

---

## 📖 Использование

### Команды оркестратора

```bash
python src/orchestrator.py --sample <путь_к_файлу> [опции]

Опции:
  --sample PATH     Путь к файлу для анализа (обязательно)
  --output PATH     Путь для сохранения отчета (по умолчанию: reports/report.json)
  --timeout SEC     Таймаут анализа в секундах (по умолчанию: 60)
  --verbose         Включить подробный вывод
  --help            Показать справку
```

### Примеры использования

#### 1. Анализ подозрительного EXE файла

```bash
python src/orchestrator.py --sample samples/malware.exe --timeout 90
```

#### 2. Анализ скрипта

```bash
python src/orchestrator.py --sample samples/suspicious.bat --timeout 30
```

#### 3. Пакетный анализ нескольких файлов

```bash
for file in samples/*.exe; do
    python src/orchestrator.py --sample "$file" --output "reports/$(basename $file .exe).json"
done
```

---

## 📊 Формат отчета

### JSON отчет содержит:

```json
{
  "metadata": {
    "tool": "RedSand",
    "version": "1.0.0",
    "analysis_time": "2024-01-15T10:30:00",
    "host": "SANDBOX-PC"
  },
  "session": {
    "sample": {
      "name": "malware.exe",
      "size": 12345,
      "hash_md5": "...",
      "hash_sha256": "..."
    },
    "duration_seconds": 45.2,
    "events": [...]
  },
  "verdict": {
    "score": 75,
    "risk_level": "HIGH",
    "verdict": "MALICIOUS",
    "reasons": ["Множественные изменения файлов", "Сетевая активность"]
  },
  "iocs": {
    "files": [...],
    "ip_addresses": [...],
    "domains": [...]
  },
  "analysis": {
    "behavior_graph": {...},
    "mitre_attack": {...},
    "statistics": {...}
  }
}
```

---

## 🔧 Настройка

### Конфигурационный файл (опционально)

Создайте `config.json` в корневой директории:

```json
{
  "analysis_timeout": 60,
  "monitoring_interval": 0.1,
  "enable_network_monitor": true,
  "enable_file_monitor": true,
  "enable_registry_monitor": true,
  "enable_process_monitor": true,
  "yara_rules_path": "rules/",
  "log_level": "INFO"
}
```

---

## 🛡️ Меры безопасности

⚠️ **КРИТИЧЕСКИ ВАЖНО:**

1. **Запускайте только в изолированной среде!**
   - Используйте виртуальную машину (VirtualBox, VMware)
   - Отключите общий доступ к файлам
   - Ограничьте сетевой доступ

2. **Настройте снапшоты ВМ**
   - Создайте чистый снапшот перед анализом
   - Восстанавливайте после каждого анализа

3. **Не анализируйте на основной системе**
   - Выделите отдельную машину для анализа
   - Не храните важные данные на машине для анализа

4. **Ограничьте права**
   - Запускайте от имени администратора только когда необходимо
   - Используйте ограниченные учетные записи для повседневной работы

---

## 📁 Структура проекта

```
RedSand/
├── src/
│   ├── orchestrator.py      # Главный контроллер
│   ├── agent.cpp            # C++ агент мониторинга
│   ├── analyzer.py          # Движок анализа
│   └── reporter.py          # Генератор отчетов
├── bin/
│   └── RedSandAgent.dll     # Скомпилированный агент
├── logs/                    # Логи работы системы
├── samples/                 # Образцы для анализа
├── reports/                 # Сгенерированные отчеты
├── rules/                   # YARA правила (опционально)
└── README.md               # Документация
```

---

## 🔍 Интерпретация результатов

### Уровни риска:

- **LOW (0-39)**: Минимальная подозрительная активность
- **MEDIUM (40-69)**: Подозрительное поведение, требует внимания
- **HIGH (70-100)**: Высокая вероятность вредоносного ПО

### Вердикты:

- **SAFE**: Файл безопасен
- **SUSPICIOUS**: Подозрительная активность, требуется дополнительный анализ
- **MALICIOUS**: Обнаружены признаки вредоносного ПО

---

## 🐛 Решение проблем

### Агент не запускается

**Проблема**: Ошибка при загрузке DLL

**Решение**:
1. Убедитесь, что агент собран для правильной архитектуры (x64/x86)
2. Проверьте наличие зависимостей (Visual C++ Redistributable)
3. Запустите от имени администратора

### Нет событий в отчете

**Проблема**: Пустой список событий

**Решение**:
1. Увеличьте таймаут анализа
2. Проверьте права доступа
3. Убедитесь, что образец действительно выполняется

### Ошибки компиляции агента

**Проблема**: Ошибки при сборке agent.cpp

**Решение**:
1. Установите актуальный Visual Studio или MinGW
2. Проверьте пути к заголовочным файлам Windows SDK
3. Убедитесь, что все библиотеки доступны

---

## 📝 Лицензия

MIT License

---

## 👥 Авторы

RedSand Team - Альтернатива зарубежным sandbox системам

---

## 📞 Поддержка

Для вопросов и предложений создавайте Issues в репозитории.
