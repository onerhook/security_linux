#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор всех типов безопасных симуляторов вирусов
12 типов угроз для тестирования системы RedSand Secure
"""

import os
from pathlib import Path

def generate_all_samples():
    """Генерация всех типов симуляторов"""
    
    output_dir = Path("test_samples")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    simulators = {
        "ransomware": generate_ransomware_sim,
        "stealer": generate_stealer_sim,
        "miner": generate_miner_sim,
        "rat": generate_rat_sim,
        "worm": generate_worm_sim,
        "botnet": generate_botnet_sim,
        "rootkit": generate_rootkit_sim,
        "spyware": generate_spyware_sim,
        "adware": generate_adware_sim,
        "trojan": generate_trojan_sim,
        "dropper": generate_dropper_sim,
        "keylogger": generate_keylogger_sim
    }
    
    print("🧪 Генерация тестовых симуляторов...")
    print("=" * 50)
    
    for threat_type, generator in simulators.items():
        try:
            filename = generator(output_dir)
            print(f"✅ {threat_type.upper()}: {filename}")
        except Exception as e:
            print(f"❌ {threat_type.upper()}: Ошибка - {e}")
    
    print("=" * 50)
    print(f"✅ Сгенерировано {len(simulators)} симуляторов в папке {output_dir}/")


def generate_ransomware_sim(output_dir: Path) -> str:
    """Симулятор Ransomware"""
    code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RANSOMWARE SIMULATOR (БЕЗОПАСНЫЙ)
Эмулирует поведение шифровальщика без реального шифрования
"""
import time
import os

def main():
    print("[RANSOM] Инициализация модуля шифрования...")
    time.sleep(1)
    
    # Эмуляция поиска целевых файлов
    target_extensions = ['.doc', '.docx', '.xls', '.xlsx', '.pdf', '.jpg', '.png', '.zip']
    print(f"[RANSOM] Поиск файлов с расширениями: {target_extensions}")
    time.sleep(1)
    
    # Эмуляция процесса шифрования
    fake_files = ['document.docx', 'report.pdf', 'photo.jpg', 'data.xlsx']
    for file in fake_files:
        print(f"[RANSOM] Шифрование: {file}")
        time.sleep(0.5)
    
    # Эмуляция создания ransom note
    print("[RANSOM] Создание ransom_note.txt...")
    print("[RANSOM] !!! ВАШИ ФАЙЛЫ ЗАШИФРОВАНЫ !!!")
    print("[RANSOM] Отправьте 1 BTC для расшифровки")
    
    # Эмуляция добавления в автозагрузку
    print("[RANSOM] Добавление в автозагрузку...")
    
    print("[RANSOM] Завершение работы")

if __name__ == "__main__":
    main()
'''
    filename = output_dir / "sim_ransomware.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    return str(filename)


def generate_stealer_sim(output_dir: Path) -> str:
    """Симулятор Stealer"""
    code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEALER SIMULATOR (БЕЗОПАСНЫЙ)
Эмулирует кражу данных без реального доступа
"""
import time

def main():
    print("[STEALER] Запуск модуля сбора данных...")
    time.sleep(0.5)
    
    # Цели для кражи
    targets = [
        "Browser passwords (Chrome, Firefox, Edge)",
        "Cookies and sessions",
        "Crypto wallets (Bitcoin, Ethereum)",
        "Discord tokens",
        "Telegram sessions",
        "System information",
        "Clipboard data",
        "Saved WiFi passwords"
    ]
    
    for target in targets:
        print(f"[STEALER] Сбор: {target}")
        time.sleep(0.3)
    
    # Эмуляция отправки на C&C
    print("[STEALER] Подключение к C&C серверу...")
    print("[STEALER] Отправка собранных данных...")
    print("[STEALER] Очистка следов...")
    
    print("[STEALER] Завершение работы")

if __name__ == "__main__":
    main()
'''
    filename = output_dir / "sim_stealer.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    return str(filename)


def generate_miner_sim(output_dir: Path) -> str:
    """Симулятор Miner"""
    code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MINER SIMULATOR (БЕЗОПАСНЫЙ)
Эмулирует майнинг без нагрузки на систему
"""
import time
import random

def main():
    print("[MINER] Инициализация майнера...")
    time.sleep(0.5)
    
    # Подключение к пулу
    print("[MINER] Подключение к mining pool: pool.minexmr.com:4444")
    time.sleep(0.5)
    
    # Эмуляция майнинга
    print("[MINER] Начало майнинга Monero...")
    for i in range(10):
        hashrate = random.uniform(50.0, 150.0)
        shares = random.randint(1, 20)
        print(f"[MINER] Hashrate: {hashrate:.2f} H/s | Accepted shares: {shares}")
        time.sleep(0.5)
    
    # Эмуляция скрытия процесса
    print("[MINER] Маскировка под svchost.exe...")
    print("[MINER] Отключение при активности пользователя...")
    
    print("[MINER] Завершение работы")

if __name__ == "__main__":
    main()
'''
    filename = output_dir / "sim_miner.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    return str(filename)


def generate_rat_sim(output_dir: Path) -> str:
    """Симулятор RAT"""
    code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAT SIMULATOR (БЕЗОПАСНЫЙ)
Эмулирует удаленный доступ без реального контроля
"""
import time

def main():
    print("[RAT] Подключение к C&C серверу...")
    time.sleep(0.5)
    
    # Список команд
    commands = [
        "get_system_info",
        "list_processes",
        "list_files(C:\\\\Users)",
        "capture_screen",
        "start_keylogger",
        "webcam_capture",
        "microphone_record",
        "download_file(passwords.txt)",
        "execute_cmd(whoami)",
        "add_to_startup"
    ]
    
    print("[RAT] Ожидание команд...")
    time.sleep(0.5)
    
    for cmd in commands:
        print(f"[RAT] Получена команда: {cmd}")
        print(f"[RAT] Выполнение: {cmd}")
        time.sleep(0.3)
    
    print("[RAT] Режим ожидания...")
    print("[RAT] Завершение работы")

if __name__ == "__main__":
    main()
'''
    filename = output_dir / "sim_rat.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    return str(filename)


def generate_worm_sim(output_dir: Path) -> str:
    """Симулятор Worm"""
    code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WORM SIMULATOR (БЕЗОПАСНЫЙ)
Эмулирует распространение без реального заражения
"""
import time
import random

def main():
    print("[WORM] Инициализация модуля распространения...")
    time.sleep(0.5)
    
    # Сканирование сети
    print("[WORM] Сканирование локальной сети 192.168.1.0/24...")
    for i in range(5):
        ip = f"192.168.1.{random.randint(1, 254)}"
        print(f"[WORM] Найден узел: {ip}")
        time.sleep(0.3)
    
    # Эмуляция распространения через USB
    print("[WORM] Поиск USB устройств...")
    print("[WORM] Копирование на USB drive...")
    time.sleep(0.5)
    
    # Эмуляция распространения через сеть
    print("[WORM] Попытка заражения через сетевые шары...")
    for i in range(3):
        print(f"[WORM] Заражение узла {i+1}/3")
        time.sleep(0.3)
    
    print("[WORM] Завершение работы")

if __name__ == "__main__":
    main()
'''
    filename = output_dir / "sim_worm.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    return str(filename)


def generate_botnet_sim(output_dir: Path) -> str:
    """Симулятор Botnet"""
    code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOTNET SIMULATOR (БЕЗОПАСНЫЙ)
Эмулирует бот-сеть без реальных атак
"""
import time

def main():
    print("[BOTNET] Подключение к C&C серверу...")
    time.sleep(0.5)
    
    print("[BOTNET] Регистрация в бот-сети...")
    print("[BOTNET] Ваш ID: BOT_7X9K2M")
    time.sleep(0.5)
    
    # Команды от бот-мастера
    commands = [
        "DDoS target: example.com",
        "Send spam: 1000 emails",
        "Scan ports: 192.168.0.0/16",
        "Update bot client",
        "Spread to other hosts"
    ]
    
    for cmd in commands:
        print(f"[BOTNET] Команда от мастера: {cmd}")
        print(f"[BOTNET] Выполнение...")
        time.sleep(0.3)
    
    print("[BOTNET] Режим ожидания...")
    print("[BOTNET] Завершение работы")

if __name__ == "__main__":
    main()
'''
    filename = output_dir / "sim_botnet.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    return str(filename)


def generate_rootkit_sim(output_dir: Path) -> str:
    """Симулятор Rootkit"""
    code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROOTKIT SIMULATOR (БЕЗОПАСНЫЙ)
Эмулирует скрытие без реального внедрения в ядро
"""
import time

def main():
    print("[ROOTKIT] Инициализация драйвера...")
    time.sleep(0.5)
    
    # Эмуляция установки драйвера
    print("[ROOTKIT] Установка драйвера: rtcore.sys")
    print("[ROOTKIT] Внедрение в ядро...")
    time.sleep(0.5)
    
    # Эмуляция скрытия процессов
    hidden_processes = ["malware.exe", "backdoor.dll", "keylog.sys"]
    print("[ROOTKIT] Скрытие процессов:")
    for proc in hidden_processes:
        print(f"[ROOTKIT]   - {proc}")
        time.sleep(0.2)
    
    # Эмуляция скрытия файлов
    print("[ROOTKIT] Скрытие файлов и записей реестра...")
    time.sleep(0.3)
    
    # Hooking системных вызовов
    print("[ROOTKIT] Перехват системных вызовов...")
    print("[ROOTKIT] SSDT hooks installed")
    
    print("[ROOTKIT] Завершение работы")

if __name__ == "__main__":
    main()
'''
    filename = output_dir / "sim_rootkit.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    return str(filename)


def generate_spyware_sim(output_dir: Path) -> str:
    """Симулятор Spyware"""
    code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPYWARE SIMULATOR (БЕЗОПАСНЫЙ)
Эмулирует слежку без реального сбора данных
"""
import time

def main():
    print("[SPYWARE] Запуск модуля наблюдения...")
    time.sleep(0.5)
    
    # Мониторинг активности
    activities = [
        "Отслеживание посещенных сайтов",
        "Перехват скриншотов каждые 5 сек",
        "Запись нажатий клавиш",
        "Мониторинг активных приложений",
        "Запись аудио с микрофона"
    ]
    
    for activity in activities:
        print(f"[SPYWARE] {activity}")
        time.sleep(0.3)
    
    # Отправка данных
    print("[SPYWARE] Сжатие собранных данных...")
    print("[SPYWARE] Отправка на сервер анализа...")
    
    print("[SPYWARE] Продолжение мониторинга...")
    print("[SPYWARE] Завершение работы")

if __name__ == "__main__":
    main()
'''
    filename = output_dir / "sim_spyware.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    return str(filename)


def generate_adware_sim(output_dir: Path) -> str:
    """Симулятор Adware"""
    code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADWARE SIMULATOR (БЕЗОПАСНЫЙ)
Эмулирует рекламу без реальных popup
"""
import time

def main():
    print("[ADWARE] Инициализация рекламного модуля...")
    time.sleep(0.5)
    
    # Изменение настроек браузера
    print("[ADWARE] Изменение домашней страницы...")
    print("[ADWARE] Установка поисковика по умолчанию...")
    time.sleep(0.3)
    
    # Эмуляция показа рекламы
    ads = [
        "ПОКУПАЙТЕ BITCOIN СЕЙЧАС!",
        "ВЫИГРАЙ IPHONE 15!",
        "ГОРЯЧИЕ СКИДКИ 90%!",
        "Заработок $5000 в день!"
    ]
    
    for ad in ads:
        print(f"[ADWARE] Popup: {ad}")
        time.sleep(0.3)
    
    # Перенаправление трафика
    print("[ADWARE] Перенаправление поисковых запросов...")
    
    print("[ADWARE] Завершение работы")

if __name__ == "__main__":
    main()
'''
    filename = output_dir / "sim_adware.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    return str(filename)


def generate_trojan_sim(output_dir: Path) -> str:
    """Симулятор Trojan"""
    code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TROJAN SIMULATOR (БЕЗОПАСНЫЙ)
Эмулирует троян без реальной вредоносной нагрузки
"""
import time

def main():
    print("[TROJAN] Маскировка под легитимное ПО...")
    print("[TROJAN] Имя: Adobe_Flash_Update.exe")
    time.sleep(0.5)
    
    # Эмуляция установки
    print("[TROJAN] Запуск установщика...")
    print("[TROJAN] Копирование файлов...")
    print("[TROJAN] Создание записей реестра...")
    time.sleep(0.5)
    
    # Полезная нагрузка
    print("[TROJAN] Активация полезной нагрузки...")
    print("[TROJAN] Загрузка дополнительного модуля...")
    print("[TROJAN] Установка соединения с C&C...")
    
    # Персистентность
    print("[TROJAN] Добавление в автозагрузку...")
    print("[TROJAN] Создание службы...")
    
    print("[TROJAN] Завершение работы")

if __name__ == "__main__":
    main()
'''
    filename = output_dir / "sim_trojan.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    return str(filename)


def generate_dropper_sim(output_dir: Path) -> str:
    """Симулятор Dropper"""
    code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DROPPER SIMULATOR (БЕЗОПАСНЫЙ)
Эмулирует загрузчик без реальной доставки
"""
import time

def main():
    print("[DROPPER] Запуск загрузчика...")
    time.sleep(0.5)
    
    # Извлечение полезной нагрузки
    print("[DROPPER] Расшифровка встроенной полезной нагрузки...")
    print("[DROPPER] Извлечение: payload.dll")
    time.sleep(0.5)
    
    # Загрузка из интернета
    print("[DROPPER] Загрузка дополнительных модулей...")
    print("[DROPPER] URL: hxxp://malicious-server[.]com/stage2.exe")
    time.sleep(0.3)
    
    # Установка
    print("[DROPPER] Установка полезной нагрузки...")
    print("[DROPPER] Запуск установленного компонента...")
    
    # Самоудаление
    print("[DROPPER] Очистка следов...")
    print("[DROPPER] Самоудаление загрузчика...")
    
    print("[DROPPER] Завершение работы")

if __name__ == "__main__":
    main()
'''
    filename = output_dir / "sim_dropper.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    return str(filename)


def generate_keylogger_sim(output_dir: Path) -> str:
    """Симулятор Keylogger"""
    code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KEYLOGGER SIMULATOR (БЕЗОПАСНЫЙ)
Эмулирует кейлоггер без реального перехвата
"""
import time

def main():
    print("[KEYLOGGER] Установка хука клавиатуры...")
    time.sleep(0.5)
    
    # Эмуляция перехвата
    print("[KEYLOGGER] Мониторинг нажатий клавиш...")
    
    fake_keystrokes = [
        "user: admin",
        "password: ********",
        "https://bank.com/login",
        "card: 4*** **** **** 1234"
    ]
    
    for stroke in fake_keystrokes:
        print(f"[KEYLOGGER] Перехвачено: {stroke}")
        time.sleep(0.3)
    
    # Сохранение логов
    print("[KEYLOGGER] Сохранение в log.txt...")
    print("[KEYLOGGER] Отправка логов на сервер...")
    
    # Скрытие
    print("[KEYLOGGER] Маскировка процесса...")
    print("[KEYLOGGER] Добавление в автозагрузку...")
    
    print("[KEYLOGGER] Завершение работы")

if __name__ == "__main__":
    main()
'''
    filename = output_dir / "sim_keylogger.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    return str(filename)


if __name__ == "__main__":
    generate_all_samples()
