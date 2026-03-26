# 📦 RedSand - Руководство по установке

## Требования

### Минимальные требования
- **ОС**: Windows 10/11 (для полного функционала)
- **Python**: 3.9 или выше
- **Права**: Администратор (рекомендуется)
- **RAM**: 4 GB минимум, 8 GB рекомендуется
- **Диск**: 1 GB свободного места

### Для изолированного анализа
- Виртуальная машина с Windows (VirtualBox/VMware)
- Снапшот чистой системы
- Отключенная сеть или NAT

## Установка на Windows

### Шаг 1: Установка Python

1. Скачайте Python 3.9+ с https://www.python.org/downloads/
2. При установке отметьте "Add Python to PATH"
3. Проверьте установку:
   ```cmd
   python --version
   ```

### Шаг 2: Клонирование репозитория

```cmd
git clone <repository-url> redsand
cd redsand
```

Или скачайте ZIP архив и распакуйте.

### Шаг 3: Установка зависимостей

```cmd
pip install -r requirements.txt
```

Или вручную:
```cmd
pip install pefile yara-python
```

### Шаг 4: Проверка установки

```cmd
python redsand.py --help
```

Вы должны увидеть приветственное сообщение.

## Установка компонентов для расширенного анализа

### Frida (для динамического анализа)

```cmd
pip install frida-tools
```

Проверка:
```cmd
frida --version
```

### YARA правила

1. Скачайте правила с https://github.com/Yara-Rules/rules
2. Поместите `.yar` файлы в папку `rules/`

### Visual C++ Redistributable (для C++ агента)

Скачайте с https://aka.ms/vs/17/release/vc_redist.x64.exe

## Компиляция C++ агента (опционально)

Для глубокого перехвата API требуется компиляция native агента:

### Требования
- Visual Studio 2019+ с C++ workload
- Windows SDK
- MinHook библиотека

### Шаги компиляции

1. Установите MinHook:
   ```cmd
   git clone https://github.com/TsudaKageyu/minhook.git
   cd minhook
   nmake /f Makefile.vc
   ```

2. Скомпилируйте агент:
   ```cmd
   cl /EHsc /I minhook\include agent.cpp minhook\lib\MinHook.x64.lib /link /OUT:agent.exe
   ```

## Настройка виртуальной машины (рекомендуется)

### VirtualBox настройка

1. Создайте VM с Windows 10
2. Выделите минимум 2 CPU, 4 GB RAM
3. Включите Nested VT-x/AMD-V
4. Установите Guest Additions
5. Создайте снапшот "Clean State"

### Настройка гостевой ОС

1. Отключите Windows Defender:
   ```powershell
   Set-MpPreference -DisableRealtimeMonitoring $true
   ```

2. Включите PowerShell скрипты:
   ```powershell
   Set-ExecutionPolicy Unrestricted -Force
   ```

3. Отключите автоматические обновления
4. Установите Python и зависимости
5. Скопируйте RedSand в VM
6. Создайте снапшот "Ready for Analysis"

## Проверка работоспособности

### Тест статического анализатора

```cmd
python -m modules.static_analyzer tests\sample.exe
```

### Тест сетевого эмулятора

```cmd
python -m modules.network_emulator
```

В другом терминале:
```cmd
curl http://localhost:8080/test
```

### Полный тест

```cmd
python redsand.py tests\sample.exe
```

## Устранение проблем

### Ошибка "No module named 'winreg'"
Это нормально на Linux. Модули работают только на Windows.

### Ошибка доступа к памяти
Запустите от имени администратора.

### Файл не анализируется
Проверьте путь к файлу и права доступа.

### Сетевой эмулятор не запускается
Порт 5353 или 8080 может быть занят. Измените порты в коде.

## Безопасность

⚠️ **ВАЖНО**: Всегда анализируйте образцы в изолированной среде!

1. Используйте VM с снапшотами
2. Отключайте сеть или используйте NAT
3. Не анализируйте на основной системе
4. Сохраняйте образцы для отчетности
5. Очищайте VM после анализа

## Обновление

```cmd
git pull origin main
pip install -U pefile yara-python
```

## Следующие шаги

После установки:
1. Прочитайте [USAGE_EXAMPLE.md](USAGE_EXAMPLE.md)
2. Настройте VM для анализа
3. Добавьте YARA правила
4. Запустите первый анализ

---

**Готово!** RedSand установлен и готов к работе 🛡️
