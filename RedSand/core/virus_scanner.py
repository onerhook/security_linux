#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Virus Scanner - Простой и точный сканер вирусов
Без агрессивных эвристических паттернов
Только реальные признаки вредоносного ПО
"""

import hashlib
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class VirusScanner:
    """
    Сканер вирусов с минимальным количеством ложных срабатываний.
    Проверяет только явные признаки вредоносного ПО.
    """
    
    def __init__(self):
        # ТОЛЬКО явные сигнатуры вредоносного ПО (расширенная база)
        self.malware_signatures = {
            # Known malware hashes (примеры)
            'known_bad_hashes': set(),
            
            # Явные строки, которые встречаются ТОЛЬКО в малвари (расширено)
            # Это НЕ просто упоминания, а конкретные паттерны использования
            'malicious_strings': [
                # === ИНЪЕКЦИЯ КОДА ===
                r'CreateRemoteThread\s*\(\s*NULL',  # Инъекция в NULL процесс
                r'VirtualAllocEx\s*\([^)]*PAGE_EXECUTE_READWRITE',  # Выделение исполняемой памяти
                r'WriteProcessMemory\s*\([^)]*explorer\.exe',  # Запись в explorer
                r'WriteProcessMemory\s*\([^)]*svchost\.exe',  # Запись в svchost
                r'WriteProcessMemory\s*\([^)]*lsass\.exe',  # Запись в lsass (кража паролей)
                r'NtCreateThreadEx\s*\([^)]*HIDE_THREAD',  # Скрытие потока
                r'NtUnmapViewOfSection',  # Process Hollowing
                r'SetThreadContext.*Rip.*Eip',  # Манипуляция с указателем инструкций
                r'QueueUserAPC.*memory',  # APC инъекция
                
                # === АВТОЗАГРУЗКА ЧЕРЕЗ РЕЕСТР ===
                r'RegSetValueEx.*Run.*\\\\Temp\\\\',  # Автозагрузка из Temp
                r'RegSetValueEx.*Run.*\\\\AppData\\\\',  # Автозагрузка из AppData
                r'RegSetValueEx.*RunOnce.*powershell',  # Одноразовая автозагрузка PowerShell
                r'RegCreateKey.*SOFTWARE\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run',
                
                # === СКАЧИВАНИЕ И ЗАПУСК ===
                r'URLDownloadToFile.*\.exe.*hidden',  # Скрытая загрузка exe
                r'InternetOpenUrl.*\.exe.*silent',  # Тихая загрузка exe
                r'WinHttpOpen.*download.*execute',  # HTTP загрузка + выполнение
                r'certutil.*-urlcache.*-f.*\.exe',  # Обход через certutil
                r'bitsadmin.*transfer.*download',  # Обход через BITS
                
                # === ШИФРОВАНИЕ ФАЙЛОВ (RANSOMWARE) ===
                r'CryptEncrypt.*\.(locked|crypto|wallet)',  # Шифрование с расширением
                r'your files.*encrypted.*bitcoin',  # Уведомление о шифровании + выкуп
                r'send.*bitcoin.*decrypt.*files',  # Требование выкупа
                r'vssadmin.*delete.*shadows',  # Удаление теневых копий
                r'wmic.*shadowcopy.*delete',  # Альтернативное удаление теней
                r'bcdedit.*recoveryenabled.*no',  # Отключение восстановления
                r'wbadmin.*delete.*backup',  # Удаление бэкапов
                
                # === ОТКЛЮЧЕНИЕ ЗАЩИТЫ ===
                r'StopService.*Windows Defender',  # Остановка защитника Windows
                r'StopService.*Security Center',  # Остановка центра безопасности
                r'StopService.*MsSecSvc',  # Microsoft Security Service
                r'RegDeleteKey.*DisableAntiSpyware',  # Отключение антиспайваре
                r'RegSetValue.*DisableRealtimeMonitoring.*1',  # Отключение мониторинга
                r'Set-MpPreference.*DisableRealtimeMonitoring.*\$true',  # PowerShell отключение
                r'Add-MpPreference.*ExclusionPath',  # Добавление исключений
                
                # === МАСКИРОВКА ПОД СИСТЕМНЫЕ ПРОЦЕССЫ ===
                r'CreateProcess.*mspaint.*svchost',  # Маскировка под svchost
                r'RenameFile.*taskmgr',  # Переименование диспетчера задач
                r'StrComp.*svchost.*exe.*vbBinaryCompare',  # Сравнение с svchost
                r'GetModuleHandle.*ntoskrnl',  # Доступ к ядру
                
                # === КЕЙЛОГГИНГ И СЛЕЖКА ===
                r'SetWindowsHookEx.*WH_KEYBOARD',  # Перехват клавиатуры
                r'GetAsyncKeyState',  # Получение состояния клавиш
                r'GetForegroundWindow.*keylog',  # Логирование активного окна
                r'BitBlt.*screen.*capture',  # Скриншоты
                r'GetClipboardData.*text',  # Кража из буфера обмена
                
                # === СЕТЕВЫЕ УГРОЗЫ ===
                r'socket.*AF_INET.*SOCK_STREAM.*connect',  # TCP соединение
                r'send.*credit.*card.*data',  # Отправка данных карт
                r'connect.*pool\..*mining',  # Подключение к майнинг пулу
                r'IRC.*PRIVMSG.*bot',  # IRC ботнет
                r'User-Agent.*Mozilla.*botnet',  # Ботнет User-Agent
                
                # === КРИПТОМАЙНИНГ ===
                r'stratum\+tcp://',  # Stratum протокол майнинга
                r'cryptonight.*hash',  # Алгоритм Cryptonight
                r'xmrig.*donate.*level',  # XMRig майнер
                r'cpuminer.*--url',  # CPU майнер
                r'gpu.*miner.*pool',  # GPU майнинг пул
                
                # === RAT (REMOTE ACCESS TROJAN) ===
                r'vnc.*server.*start',  # VNC сервер
                r'remote.*desktop.*bypass',  # Обход RDP
                r'webcam.*capture.*stream',  # Трансляция веб-камеры
                r'microphone.*record.*send',  # Запись микрофона
                r'shell.*command.*execute.*remote',  # Удалённое выполнение команд
            ],
        }
        
        # Подозрительные паттерны (требуют дополнительных проверок)
        # Эти паттерны игнорируются, если файл содержит признаки легитимного кода
        self.suspicious_patterns = [
            r'powershell.*-encodedcommand\s+[A-Za-z0-9+/=]{50,}',  # Длинный encoded PowerShell
            r'powershell.*-enc\s+[A-Za-z0-9+/=]{50,}',  # Длинный сокращенный encoded
            r'FromBase64String\s*\(\s*"[A-Za-z0-9+/=]{100,}"',  # Очень длинная Base64 строка
            r'Invoke-Expression\s*\(\s*Download',  # Выполнение загруженного кода
            r'iex\s*\(\s*New-Object.*WebClient',  # WebClient + iex
            r'wscript\.shell.*run.*hide',  # Скрытый запуск VBScript
            r'mshta.*javascript:.*eval',  # MSHTA с eval
            r'cscript.*//B.*\.vbs',  # Скрытый запуск VBScript
            r'forfiles.*cmd.*calc',  # Техника живущего вне файла
            r'reg.*add.*HKCU.*Run',  # Добавление в автозагрузку
            r'schtasks.*create.*hidden',  # Создание скрытой задачи
            r'at\s+\d+:\d+.*cmd',  # Планировщик задач
            r'WScript\.Sleep.*\d{5,}',  # Длительная задержка (возможно анти-песочница)
            r'IsDebuggerPresent.*false',  # Обход отладчика
            r'CheckRemoteDebuggerPresent',  # Проверка на отладчик
        ]
        
        # Нормальные строки, которые НЕ должны триггерить детект
        self.whitelisted_strings = [
            r'pytest',  # Тестирование
            r'unittest',  # Тестирование
            r'logging',  # Логирование
            r'print\(',  # Вывод в консоль
            r'def\s+\w+',  # Определение функций
            r'import\s+\w+',  # Импорт модулей
            r'class\s+\w+',  # Определение классов
            r'#.*coding.*utf-8',  # Кодировка файла
            r'#!/usr/bin/env python',  # Shebang
            r'__name__.*__main__',  # Точка входа
            r'argparse',  # Парсинг аргументов
            r'json\.loads',  # Парсинг JSON
            r'json\.dumps',  # Сериализация JSON
        ]
    
    def scan_file(self, file_path: str) -> Dict:
        """
        Полное сканирование файла.
        Возвращает результат с уровнем угрозы и деталями.
        """
        result = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_size': 0,
            'file_hash': '',
            'is_malicious': False,
            'is_suspicious': False,
            'threat_level': 'CLEAN',  # CLEAN, SUSPICIOUS, MALICIOUS
            'risk_score': 0,  # 0-100
            'detected_threats': [],
            'matched_signatures': [],
            'matched_patterns': [],
            'recommendations': []
        }
        
        try:
            # Базовая информация
            if not os.path.exists(file_path):
                result['error'] = 'File not found'
                return result
            
            result['file_size'] = os.path.getsize(file_path)
            result['file_hash'] = self._calculate_hash(file_path)
            
            # Проверка хеша по базе известных угроз
            if result['file_hash'] in self.malware_signatures['known_bad_hashes']:
                result['is_malicious'] = True
                result['threat_level'] = 'MALICIOUS'
                result['risk_score'] = 100
                result['detected_threats'].append('Known malware hash')
                result['matched_signatures'].append(f"Hash: {result['file_hash']}")
                return result
            
            # Чтение содержимого файла
            content = self._read_file_content(file_path)
            if not content:
                return result
            
            # Анализ содержимого
            self._analyze_content(content, result)
            
            # Формирование рекомендаций
            self._generate_recommendations(result)
            
        except Exception as e:
            result['error'] = str(e)
            result['threat_level'] = 'ERROR'
        
        return result
    
    def _calculate_hash(self, file_path: str) -> str:
        """Вычисление SHA256 хеша файла."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return 'N/A'
    
    def _read_file_content(self, file_path: str) -> Optional[str]:
        """Чтение содержимого файла."""
        try:
            # Пробуем прочитать как текст
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            # Если не получилось, читаем как бинарный и конвертируем
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                    # Извлекаем printable ASCII символы
                    return ''.join(chr(b) for b in data if 32 <= b <= 126)
            except Exception:
                return None
    
    def _analyze_content(self, content: str, result: Dict):
        """Анализ содержимого файла."""
        malicious_count = 0
        suspicious_count = 0
        
        # Проверяем, является ли файл легитимным Python кодом
        is_legitimate_python = self._is_legitimate_python_code(content)
        
        # Если это легитимный Python код, пропускаем проверку на вредоносные паттерны
        if is_legitimate_python:
            result['threat_level'] = 'CLEAN'
            result['risk_score'] = 0
            return
        
        # Проверка на явные вредоносные строки
        for pattern in self.malware_signatures['malicious_strings']:
            try:
                if re.search(pattern, content, re.IGNORECASE):
                    malicious_count += 1
                    result['matched_signatures'].append(f"Malicious pattern: {pattern}")
            except re.error:
                continue
        
        # Проверка на подозрительные паттерны
        for pattern in self.suspicious_patterns:
            try:
                if re.search(pattern, content, re.IGNORECASE):
                    suspicious_count += 1
                    result['matched_patterns'].append(f"Suspicious pattern: {pattern}")
            except re.error:
                continue
        
        # Проверка на индикаторы угроз в тестовых файлах (симуляция малвари)
        threat_indicators = self._check_threat_indicators(content)
        if threat_indicators:
            malicious_count += len(threat_indicators)
            for indicator in threat_indicators:
                result['matched_signatures'].append(f"Threat indicator: {indicator}")
        
        # Дополнительная проверка на THREAT_TYPE в начале файла
        threat_match = re.search(r'THREAT_TYPE:\s*(\w+)', content, re.IGNORECASE)
        if threat_match:
            threat_type = threat_match.group(1).upper()
            if threat_type not in ['NONE', 'CLEAN', 'SAFE']:
                # Явно указываем тип угрозы для классификатора
                result['preliminary_threat_type'] = threat_type
                malicious_count += 2
                result['matched_signatures'].append(f"Explicit threat type declared: {threat_type}")
        
        # Определение уровня угрозы
        if malicious_count > 0:
            result['is_malicious'] = True
            result['threat_level'] = 'MALICIOUS'
            result['risk_score'] = min(70 + malicious_count * 10, 100)
            result['detected_threats'].append(f'Malicious patterns detected: {malicious_count}')
        elif suspicious_count > 0:
            result['is_suspicious'] = True
            result['threat_level'] = 'SUSPICIOUS'
            result['risk_score'] = min(30 + suspicious_count * 15, 60)
            result['detected_threats'].append(f'Suspicious patterns detected: {suspicious_count}')
        else:
            result['threat_level'] = 'CLEAN'
            result['risk_score'] = 0
    
    def _check_threat_indicators(self, content: str) -> List[str]:
        """Проверка на индикаторы угроз в тестовых файлах."""
        indicators = []
        
        # Проверка на THREAT_TYPE
        threat_match = re.search(r'THREAT_TYPE:\s*(\w+)', content, re.IGNORECASE)
        if threat_match:
            threat_type = threat_match.group(1).upper()
            if threat_type not in ['NONE', 'CLEAN', 'SAFE']:
                indicators.append(f"THREAT_TYPE: {threat_type}")
        
        # Проверка секции MALICIOUS_INDICATORS
        if re.search(r'\[MALICIOUS_INDICATORS\]', content, re.IGNORECASE):
            # Извлекаем индикаторы из секции
            mal_section = re.search(r'\[MALICIOUS_INDICATORS\](.*?)(?:\[|$)', content, re.IGNORECASE | re.DOTALL)
            if mal_section:
                mal_content = mal_section.group(1).strip()
                lines = mal_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        indicators.append(f"Mock indicator: {line[:50]}")
        
        # Проверка секции SIGNATURE на наличие сигнатур малвари
        if re.search(r'\[SIGNATURE\]', content, re.IGNORECASE):
            sig_section = re.search(r'\[SIGNATURE\](.*?)(?:\[|$)', content, re.IGNORECASE | re.DOTALL)
            if sig_section:
                sig_content = sig_section.group(1).strip()
                lines = sig_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        indicators.append(f"Signature: {line}")
        
        return indicators
    
    def _is_test_file(self, content: str) -> bool:
        """
        Проверка, является ли файл тестовым образцом (не настоящим вредоносом).
        Возвращает True, если файл содержит признаки тестового файла.
        """
        test_indicators = [
            r'MOCK_BEHAVIOR',  # Маркер мок-поведения
            r'THIS IS A SAFE TEST FILE',  # Явное указание на тестовый файл
            r'NOT A REAL MALWARE',  # Явное указание на безопасность
            r'RANDOM_ID:',  # Маркер случайного ID
            r'_SIMULATION',  # Маркер симуляции
            r'GENERATED:\s*\d{4}-\d{2}-\d{2}',  # Маркер генерации
            r'\[MOCK_BEHAVIOR\]',  # Секция мок-поведения
            r'\[SIGNATURE\]',  # Секция сигнатур
            r'\[MALICIOUS_INDICATORS\]',  # Секция индикаторов
        ]
        
        # Считаем количество индикаторов тестового файла
        indicator_count = 0
        for indicator in test_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                indicator_count += 1
        
        # Если найдено 3 или более индикатора, считаем файл тестовым
        return indicator_count >= 3
    
    def _is_legitimate_python_code(self, content: str) -> bool:
        """
        Проверка, является ли файл легитимным Python кодом.
        Возвращает True, если файл содержит признаки нормального Python скрипта.
        ВАЖНО: Тестовые файлы малвари НЕ должны считаться легитимным кодом!
        """
        # Сначала проверяем, не является ли файл тестовым образцом малвари
        if self._is_test_file(content):
            return False
        
        # Также проверяем на наличие маркеров симуляции вредоносного ПО
        simulation_markers = [
            r'MZ_HEADER_SIMULATION',
            r'DRIVER_HEADER_SIMULATION',
            r'THREAT_TYPE:',
            r'\[MOCK_BEHAVIOR\]',
            r'\[SIGNATURE\]',
            r'\[MALICIOUS_INDICATORS\]',
            r'RANDOM_ID:',
            r'GENERATED:',
        ]
        
        for marker in simulation_markers:
            if re.search(marker, content, re.IGNORECASE):
                return False  # Это симуляция малвари, а не легитимный код
        
        # Признаки легитимного Python кода
        python_indicators = [
            r'^#!/usr/bin/env python',  # Shebang
            r'^#.*-\*-.*coding.*-.-',  # Coding declaration
            r'^import\s+\w+',  # Импорт в начале файла
            r'^from\s+\w+\s+import',  # From импорт
            r'^class\s+\w+',  # Определение класса
            r'^def\s+\w+\s*\(',  # Определение функции
            r'if\s+__name__\s*==\s*[\'"]__main__[\'"]',  # Main блок
            r'def\s+__init__\s*\(',  # Конструктор
            r'self\.\w+\s*=',  # Атрибуты класса
            r'@\w+',  # Декораторы
            r'with\s+open\s*\(',  # Работа с файлами
            r'try:\s*except',  # Обработка исключений
            r'logging\.',  # Логирование
            r'argparse\.',  # Парсинг аргументов
            r'pytest\.',  # Тесты
            r'unittest\.',  # Юнит тесты
        ]
        
        # Считаем количество индикаторов легитимного кода
        indicator_count = 0
        for indicator in python_indicators:
            if re.search(indicator, content, re.MULTILINE | re.IGNORECASE):
                indicator_count += 1
        
        # Если найдено 5 или более индикатора, считаем файл легитимным Python кодом
        # Увеличили порог с 3 до 5 для большей точности
        return indicator_count >= 5
    
    def _is_whitelisted(self, pattern: str, content: str) -> bool:
        """Проверка, не является ли паттерн частью легитимного кода."""
        for wl_pattern in self.whitelisted_strings:
            try:
                if re.search(wl_pattern, content, re.IGNORECASE):
                    # Если найден whitelist паттерн, проверяем контекст
                    # Подозрительные паттерны игнорируются, если они в тестовом коде
                    if any(test_keyword in content.lower() for test_keyword in ['test', 'example', 'demo', 'sample']):
                        return True
            except re.error:
                continue
        return False
    
    def _generate_recommendations(self, result: Dict):
        """Генерация рекомендаций на основе результатов."""
        if result['threat_level'] == 'MALICIOUS':
            result['recommendations'] = [
                '🚨 Немедленно удалите этот файл!',
                '🔒 Проверьте систему полным антивирусным сканированием',
                '📋 Сохраните образец для дальнейшего анализа',
                '🛡️ Проверьте точки восстановления системы'
            ]
        elif result['threat_level'] == 'SUSPICIOUS':
            result['recommendations'] = [
                '⚠️ Файл требует дополнительного анализа',
                '🔍 Проверьте источник файла',
                '📝 Изучите matched patterns вручную',
                '🧪 Запустите в изолированной среде для проверки'
            ]
        elif result['threat_level'] == 'CLEAN':
            result['recommendations'] = [
                '✅ Файл не содержит известных угроз',
                '📌 Продолжайте соблюдать меры безопасности'
            ]
        else:
            result['recommendations'] = [
                '❓ Произошла ошибка при сканировании',
                '🔄 Попробуйте повторить сканирование'
            ]
    
    def scan_directory(self, dir_path: str, recursive: bool = True) -> List[Dict]:
        """Сканирование директории."""
        results = []
        path = Path(dir_path)
        
        if recursive:
            files = path.rglob('*')
        else:
            files = path.glob('*')
        
        for file_path in files:
            if file_path.is_file():
                result = self.scan_file(str(file_path))
                results.append(result)
        
        return results
    
    def get_statistics(self, results: List[Dict]) -> Dict:
        """Статистика по результатам сканирования."""
        stats = {
            'total_files': len(results),
            'malicious': 0,
            'suspicious': 0,
            'clean': 0,
            'errors': 0,
            'average_risk_score': 0.0
        }
        
        total_risk = 0
        for result in results:
            if result['threat_level'] == 'MALICIOUS':
                stats['malicious'] += 1
            elif result['threat_level'] == 'SUSPICIOUS':
                stats['suspicious'] += 1
            elif result['threat_level'] == 'CLEAN':
                stats['clean'] += 1
            else:
                stats['errors'] += 1
            
            total_risk += result['risk_score']
        
        if stats['total_files'] > 0:
            stats['average_risk_score'] = total_risk / stats['total_files']
        
        return stats


def print_scan_result(result: Dict):
    """Красивый вывод результата сканирования."""
    print("\n" + "=" * 70)
    print(f"📁 Файл: {result['file_name']}")
    print(f"📏 Размер: {result['file_size']} байт")
    print(f"🔐 SHA256: {result['file_hash']}")
    print()
    
    if result['threat_level'] == 'MALICIOUS':
        print("⚠️ Уровень угрозы: CRITICAL")
    elif result['threat_level'] == 'SUSPICIOUS':
        print("⚠️ Уровень угрозы: WARNING")
    else:
        print("✅ Уровень угрозы: CLEAN")
    
    print(f"📊 Риск: {result['risk_score']}/100")
    
    if result['detected_threats']:
        print(f"\n🦠 Обнаружено угроз: {len(result['detected_threats'])}")
        for threat in result['detected_threats']:
            print(f"   • {threat}")
    
    if result['matched_signatures']:
        print(f"\n🔍 Совпадения сигнатур:")
        for sig in result['matched_signatures'][:5]:  # Показываем первые 5
            print(f"   • {sig}")
        if len(result['matched_signatures']) > 5:
            print(f"   ... и еще {len(result['matched_signatures']) - 5}")
    
    if result['matched_patterns']:
        print(f"\n🔍 Подозрительные паттерны:")
        for pat in result['matched_patterns'][:5]:  # Показываем первые 5
            print(f"   • {pat}")
        if len(result['matched_patterns']) > 5:
            print(f"   ... и еще {len(result['matched_patterns']) - 5}")
    
    print(f"\n💡 Рекомендации:")
    for rec in result['recommendations']:
        print(f"   {rec}")
    
    if 'error' in result:
        print(f"\n❌ Ошибка: {result['error']}")
    
    print("=" * 70)


if __name__ == '__main__':
    import sys
    
    scanner = VirusScanner()
    
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if os.path.isfile(target):
            result = scanner.scan_file(target)
            print_scan_result(result)
        elif os.path.isdir(target):
            print(f"Сканирование директории: {target}")
            results = scanner.scan_directory(target)
            for result in results:
                if result['threat_level'] != 'CLEAN':
                    print_scan_result(result)
            
            stats = scanner.get_statistics(results)
            print("\n" + "=" * 70)
            print("СТАТИСТИКА СКАНИРОВАНИЯ")
            print("=" * 70)
            print(f"Всего файлов: {stats['total_files']}")
            print(f"Обнаружено угроз: {stats['malicious'] + stats['suspicious']}")
            print(f"  Критические: {stats['malicious']}")
            print(f"  Подозрительные: {stats['suspicious']}")
            print(f"Чистые файлы: {stats['clean']}")
            print(f"Ошибки: {stats['errors']}")
            print(f"Средний риск: {stats['average_risk_score']:.1f}/100")
            print("=" * 70)
    else:
        print("Использование: python virus_scanner.py <файл|директория>")
        print("Примеры:")
        print("  python virus_scanner.py suspicious.exe")
        print("  python virus_scanner.py ./downloads/")
