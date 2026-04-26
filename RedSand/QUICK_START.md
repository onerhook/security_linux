# 🚀 RedSand Secure v4.0 - Быстрый старт

## ✅ Что исправлено и добавлено

### 🔒 1. Исправлена критическая проблема безопасности
**ПРОБЛЕМА:** EXE файлы открывались в системе, а не в изолированной среде  
**РЕШЕНИЕ:** Теперь все executables запускаются в Docker контейнере с полной изоляцией

### 🛡️ 2. Добавлен антивирус реального времени
- Мониторит папки (Downloads, Desktop, Documents)
- Автоматически сканирует новые файлы
- Помещает угрозы в карантин

---

## ⚡ Быстрое использование

### 1. Анализ файла с Docker изоляцией
```bash
cd /workspace/RedSand
python3 -c "
from core.orchestrator import RedSandSecure
sandbox = RedSandSecure(use_docker=True)  # Docker включен по умолчанию
result = sandbox.analyze_file('samples/fake_trojan_BXW7OP.exe')
print(f'Вердикт: {result.threat_info.get(\"verdict\", \"UNKNOWN\")}')
"
```

### 2. Запуск антивируса реального времени
```bash
python3 -c "
from core.realtime_antivirus import create_antivirus_service
av = create_antivirus_service(auto_start=True)
print('✅ Антивирус запущен! Мониторит Downloads/Desktop/Documents')
import time
time.sleep(60)  # Работает 60 секунд для примера
av.stop()
print('❌ Антивирус остановлен')
"
```

### 3. Запуск GUI
```bash
python3 run.py
```
GUI автоматически использует Docker изоляцию!

---

## 📁 Новые файлы

| Файл | Описание |
|------|----------|
| `core/docker_sandbox.py` | Docker изоляция для безопасного запуска |
| `core/realtime_antivirus.py` | Антивирус реального времени |
| `NEW_FEATURES_GUIDE.md` | Полная документация новых функций |
| `requirements.txt` | Обновлен (добавлен watchdog) |

---

## 🔧 Требования

### Для Docker изоляции:
```bash
# Linux
sudo apt install docker.io
sudo usermod -aG docker $USER

# Проверка
docker --version
```

### Для антивиуса реального времени:
```bash
pip install watchdog
```

---

## 🎯 Примеры использования

### Сценарий 1: Проверить скачанный файл
```python
from core.orchestrator import RedSandSecure

sandbox = RedSandSecure()  # Docker включен по умолчанию
result = sandbox.analyze_file('~/Downloads/suspicious.exe')

if result.threat_info.get('verdict') == 'MALICIOUS':
    print("🚨 УГРОЗА! Удалите файл!")
else:
    print("✅ Файл безопасен")
```

### Сценарий 2: Постоянная защита
```python
from core.realtime_antivirus import RealTimeAntivirus

av = RealTimeAntivirus(auto_quarantine=True)
av.enable()
av.start_background()

print("🛡️ Защита активирована!")
# Работает в фоне, сканирует новые файлы
```

### Сценарий 3: Ручное сканирование папки
```python
from core.realtime_antivirus import RealTimeAntivirus

av = RealTimeAntivirus()
av.enable()

results = av.manual_scan('/home/user/Downloads')
threats = [r for r in results if r.is_malicious]

print(f"Найдено угроз: {len(threats)}")
for t in threats:
    print(f"  - {t.file_name}: {t.threat_level}")
```

---

## ⚠️ Важно

1. **Docker должен быть запущен** перед анализом EXE файлов
2. **Антивирус выключен по умолчанию** - нужно явно включить через `av.enable()`
3. **GUI автоматически использует Docker** - ничего дополнительно настраивать не нужно

---

## 📊 Структура проекта

```
RedSand/
├── core/
│   ├── docker_sandbox.py       # НОВЫЙ: Docker изоляция
│   ├── realtime_antivirus.py   # НОВЫЙ: Антивирус реального времени
│   ├── orchestrator.py         # Обновлен: интеграция Docker
│   ├── virus_scanner.py        # Сканирование сигнатур
│   ├── sandbox.py              # Python песочница
│   └── ...
├── gui/
│   └── main_gui.py             # GUI с Docker поддержкой
├── samples/                    # Тестовые образцы
├── reports/                    # Отчеты анализа
├── quarantine/                 # Карантин (создается автоматически)
├── requirements.txt            # Зависимости
├── run.py                      # Точка входа
├── NEW_FEATURES_GUIDE.md      # Полная документация
└── QUICK_START.md             # Этот файл
```

---

## 🆘 Troubleshooting

### Docker не работает
```bash
# Проверка
docker ps

# Если ошибка - запустите службу
sudo systemctl start docker

# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER
# Перезайдите в систему
```

### Антивирус не видит файлы
- Проверьте что папки существуют
- Проверьте права доступа
- Смотрите логи в `antivirus_reports/`

---

## 📞 Поддержка

- Полная документация: `NEW_FEATURES_GUIDE.md`
- Оригинальная документация: `README.md`
- Примеры файлов: `samples/`

**Безопасного анализа! 🛡️**
