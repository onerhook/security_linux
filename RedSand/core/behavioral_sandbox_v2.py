"""
Behavioral Sandbox 2.0 - Полная эмуляция Windows API
Модуль для глубокого анализа поведения вредоносного ПО через эмуляцию системных вызовов Windows
"""

import os
import sys
import json
import time
import hashlib
import logging
import threading
import subprocess
import tempfile
import shutil
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import defaultdict
import ctypes
from ctypes import wintypes

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class APIHook:
    """Представление перехваченного API вызова"""
    function_name: str
    parameters: Dict[str, Any]
    return_value: Any
    timestamp: float
    thread_id: int
    process_id: int
    stack_trace: List[str] = field(default_factory=list)
    memory_changes: Dict[str, Any] = field(default_factory=dict)
    file_operations: List[Dict[str, Any]] = field(default_factory=list)
    registry_operations: List[Dict[str, Any]] = field(default_factory=list)
    network_operations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class BehaviorReport:
    """Отчет о поведенческом анализе"""
    file_hash: str
    file_path: str
    analysis_start: float
    analysis_end: float
    total_duration: float
    api_calls: List[APIHook] = field(default_factory=list)
    suspicious_behaviors: List[Dict[str, Any]] = field(default_factory=list)
    threat_indicators: Dict[str, int] = field(default_factory=dict)
    risk_score: float = 0.0
    threat_classification: str = "UNKNOWN"
    mitigation_recommendations: List[str] = field(default_factory=list)
    ioc_extracted: Dict[str, List[str]] = field(default_factory=lambda: {
        'ip_addresses': [],
        'domains': [],
        'urls': [],
        'file_paths': [],
        'registry_keys': [],
        'mutexes': [],
        'dropped_files': []
    })


class WindowsAPIEmulator:
    """
    Эмулятор Windows API для перехвата и анализа системных вызовов
    """
    
    # Категории опасных API функций
    DANGEROUS_APIS = {
        'process_injection': [
            'VirtualAllocEx', 'WriteProcessMemory', 'CreateRemoteThread',
            'NtCreateThreadEx', 'RtlCreateUserThread', 'SetThreadContext',
            'NtUnmapViewOfSection', 'NtMapViewOfSection', 'ZwMapViewOfSection'
        ],
        'persistence': [
            'RegSetValueExA', 'RegSetValueExW', 'RegCreateKeyExA', 'RegCreateKeyExW',
            'CreateServiceA', 'CreateServiceW', 'ChangeServiceConfigA', 'ChangeServiceConfigW',
            'SetWindowsHookExA', 'SetWindowsHookExW'
        ],
        'file_operations': [
            'DeleteFileA', 'DeleteFileW', 'MoveFileA', 'MoveFileW',
            'CopyFileA', 'CopyFileW', 'CreateFileA', 'CreateFileW',
            'WriteFile', 'SetFilePointer', 'FlushFileBuffers'
        ],
        'crypto': [
            'CryptEncrypt', 'CryptDecrypt', 'CryptGenKey', 'CryptDeriveKey',
            'CryptAcquireContextA', 'CryptAcquireContextW', 'BCryptEncrypt', 'BCryptDecrypt'
        ],
        'network': [
            'socket', 'connect', 'send', 'recv', 'WSAStartup', 'InternetOpenA',
            'InternetOpenW', 'InternetConnectA', 'InternetConnectW', 'HttpOpenRequestA',
            'HttpOpenRequestW', 'URLDownloadToFileA', 'URLDownloadToFileW',
            'WinHttpOpen', 'WinHttpConnect', 'WinHttpOpenRequest'
        ],
        'evasion': [
            'IsDebuggerPresent', 'CheckRemoteDebuggerPresent', 'NtQueryInformationProcess',
            'GetTickCount', 'QueryPerformanceCounter', 'Sleep', 'NtDelayExecution',
            'GetSystemTime', 'GetLocalTime'
        ],
        'keylogging': [
            'GetAsyncKeyState', 'GetKeyState', 'SetWindowsHookExA', 'SetWindowsHookExW',
            'GetKeyboardState', 'ToUnicode', 'ToUnicodeEx'
        ],
        'screenshot': [
            'BitBlt', 'StretchBlt', 'GetDC', 'GetWindowDC', 'CreateCompatibleDC',
            'SelectObject', 'GetDIBits'
        ],
        'clipboard': [
            'OpenClipboard', 'GetClipboardData', 'SetClipboardData', 'EmptyClipboard'
        ]
    }
    
    # Паттерны подозрительного поведения
    SUSPICIOUS_PATTERNS = {
        'ransomware': [
            r'encrypt.*file', r'decrypt.*key', r'\.locked', r'\.encrypted',
            r'bitcoin', r'ransom', r'decrypt.*instruction', r'restore.*files'
        ],
        'stealer': [
            r'password', r'credential', r'cookie', r'browser.*data',
            r'wallet', r'cryptocurrency', r'login.*data'
        ],
        'rat': [
            r'remote.*desktop', r'backdoor', r'c2.*server', r'command.*control',
            r'shell.*command', r'reverse.*shell'
        ],
        'miner': [
            r'stratum.*tcp', r'mining.*pool', r'cryptonight', r'monero',
            r'bitcoin.*miner', r'hash.*rate'
        ]
    }
    
    def __init__(self, sandbox_dir: Optional[str] = None):
        """
        Инициализация эмулятора
        
        Args:
            sandbox_dir: Директория песочницы (создается временная если не указана)
        """
        self.sandbox_dir = sandbox_dir or tempfile.mkdtemp(prefix='redsand_sandbox_')
        self.emulated_registry: Dict[str, Any] = {}
        self.emulated_processes: Dict[int, Dict[str, Any]] = {}
        self.emulated_files: Dict[str, bytes] = {}
        self.emulated_network: Dict[str, Any] = {'connections': [], 'dns_cache': {}}
        self.hooked_apis: Dict[str, callable] = {}
        self.api_call_log: List[APIHook] = []
        self.behavior_flags: Dict[str, int] = defaultdict(int)
        self.lock = threading.Lock()
        
        # Инициализация эмулированного реестра
        self._init_emulated_registry()
        
        logger.info(f"Windows API Emulator initialized in {self.sandbox_dir}")
    
    def _init_emulated_registry(self):
        """Инициализация базовой структуры эмулированного реестра"""
        self.emulated_registry = {
            'HKEY_LOCAL_MACHINE': {
                'SOFTWARE': {
                    'Microsoft': {
                        'Windows': {
                            'CurrentVersion': {
                                'Run': {},
                                'RunOnce': {}
                            }
                        }
                    }
                },
                'SYSTEM': {
                    'CurrentControlSet': {
                        'Services': {}
                    }
                }
            },
            'HKEY_CURRENT_USER': {
                'SOFTWARE': {
                    'Microsoft': {
                        'Windows': {
                            'CurrentVersion': {
                                'Run': {},
                                'RunOnce': {}
                            }
                        }
                    }
                }
            }
        }
    
    def hook_api(self, func_name: str, handler: callable):
        """
        Установка хука на API функцию
        
        Args:
            func_name: Имя функции для перехвата
            handler: Функция-обработчик
        """
        with self.lock:
            self.hooked_apis[func_name] = handler
            logger.debug(f"Hooked API: {func_name}")
    
    def emulate_api_call(self, func_name: str, params: Dict[str, Any], 
                         thread_id: int = 0, process_id: int = 0) -> Any:
        """
        Эмуляция вызова API функции
        
        Args:
            func_name: Имя функции
            params: Параметры вызова
            thread_id: ID потока
            process_id: ID процесса
            
        Returns:
            Результат эмуляции
        """
        timestamp = time.time()
        
        # Создаем запись о вызове
        api_hook = APIHook(
            function_name=func_name,
            parameters=params,
            return_value=None,
            timestamp=timestamp,
            thread_id=thread_id,
            process_id=process_id
        )
        
        # Проверяем категорию опасности
        for category, apis in self.DANGEROUS_APIS.items():
            if func_name in apis:
                self.behavior_flags[category] += 1
                api_hook.stack_trace.append(f"DANGEROUS_API:{category}")
                break
        
        # Вызываем хук если установлен
        return_value = None
        if func_name in self.hooked_apis:
            try:
                return_value = self.hooked_apis[func_name](params, api_hook)
            except Exception as e:
                logger.error(f"Error in hook {func_name}: {e}")
                return_value = {"error": str(e)}
        else:
            # Эмуляция по умолчанию
            return_value = self._default_emulation(func_name, params, api_hook)
        
        api_hook.return_value = return_value
        
        # Логируем вызов
        with self.lock:
            self.api_call_log.append(api_hook)
        
        return return_value
    
    def _default_emulation(self, func_name: str, params: Dict[str, Any], 
                          api_hook: APIHook) -> Any:
        """
        Эмуляция поведения API по умолчанию
        
        Args:
            func_name: Имя функции
            params: Параметры
            api_hook: Объект хука
            
        Returns:
            Эмулированный результат
        """
        # Эмуляция работы с реестром
        if func_name in ['RegSetValueExA', 'RegSetValueExW']:
            key_path = params.get('key', '')
            value_name = params.get('value_name', '')
            value_data = params.get('data', '')
            
            # Разбираем путь ключа
            parts = key_path.split('\\')
            current = self.emulated_registry
            
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            if isinstance(current, dict):
                current[value_name] = value_data
            
            api_hook.registry_operations.append({
                'operation': 'SET_VALUE',
                'key': key_path,
                'value_name': value_name,
                'data': value_data
            })
            
            return {'success': True}
        
        # Эмуляция создания файлов
        elif func_name in ['CreateFileA', 'CreateFileW', 'WriteFile']:
            file_path = params.get('filename', '')
            content = params.get('content', b'')
            
            # Сохраняем в эмулированную файловую систему
            self.emulated_files[file_path] = content
            
            api_hook.file_operations.append({
                'operation': 'CREATE_WRITE',
                'path': file_path,
                'size': len(content) if isinstance(content, bytes) else 0
            })
            
            return {'handle': hash(file_path), 'success': True}
        
        # Эмуляция сетевых подключений
        elif func_name in ['socket', 'connect', 'InternetConnectA', 'InternetConnectW']:
            host = params.get('host', '')
            port = params.get('port', 0)
            
            self.emulated_network['connections'].append({
                'host': host,
                'port': port,
                'timestamp': time.time(),
                'protocol': params.get('protocol', 'TCP')
            })
            
            api_hook.network_operations.append({
                'operation': 'CONNECT',
                'host': host,
                'port': port
            })
            
            return {'connected': True, 'socket_id': hash(f"{host}:{port}")}
        
        # Эмуляция выделения памяти
        elif func_name in ['VirtualAllocEx', 'VirtualAlloc']:
            size = params.get('size', 0)
            protection = params.get('protection', '')
            
            is_executable = 'EXECUTE' in protection.upper() if protection else False
            
            api_hook.memory_changes.append({
                'operation': 'ALLOCATE',
                'size': size,
                'protection': protection,
                'executable': is_executable
            })
            
            if is_executable:
                self.behavior_flags['memory_injection'] += 1
            
            return {'address': 0x10000000, 'success': True}
        
        # Эмуляция создания процессов/потоков
        elif func_name in ['CreateRemoteThread', 'CreateProcessA', 'CreateProcessW']:
            target = params.get('target', '')
            command_line = params.get('command_line', '')
            
            process_id = len(self.emulated_processes) + 1
            
            self.emulated_processes[process_id] = {
                'target': target,
                'command_line': command_line,
                'start_time': time.time(),
                'parent_pid': params.get('parent_pid', 0)
            }
            
            api_hook.file_operations.append({
                'operation': 'CREATE_PROCESS',
                'target': target,
                'command_line': command_line
            })
            
            return {'process_id': process_id, 'success': True}
        
        # Эмуляция криптографических операций
        elif func_name in ['CryptEncrypt', 'CryptDecrypt']:
            api_hook.file_operations.append({
                'operation': 'CRYPTO',
                'function': func_name,
                'data_size': params.get('data_size', 0)
            })
            
            self.behavior_flags['crypto_operations'] += 1
            
            return {'success': True, 'encrypted': func_name == 'CryptEncrypt'}
        
        # Эмуляция получения состояния клавиш
        elif func_name in ['GetAsyncKeyState', 'GetKeyState']:
            api_hook.file_operations.append({
                'operation': 'KEYLOG',
                'function': func_name,
                'key_code': params.get('key_code', 0)
            })
            
            self.behavior_flags['keylogging'] += 1
            
            return {'state': 0}
        
        # По умолчанию возвращаем успех
        return {'success': True, 'emulated': True}
    
    def analyze_behavior(self) -> BehaviorReport:
        """
        Анализ собранного поведения
        
        Returns:
            Отчет о поведении
        """
        report = BehaviorReport(
            file_hash='',
            file_path='',
            analysis_start=min([h.timestamp for h in self.api_call_log]) if self.api_call_log else 0,
            analysis_end=max([h.timestamp for h in self.api_call_log]) if self.api_call_log else 0,
            total_duration=0
        )
        
        report.total_duration = report.analysis_end - report.analysis_start
        report.api_calls = self.api_call_log.copy()
        
        # Анализируем поведение
        risk_factors = []
        
        # Проверка на инъекцию кода
        if self.behavior_flags.get('process_injection', 0) > 0:
            risk_factors.append(('CODE_INJECTION', 40))
            report.suspicious_behaviors.append({
                'type': 'CODE_INJECTION',
                'severity': 'HIGH',
                'description': 'Обнаружены попытки инъекции кода в другие процессы',
                'count': self.behavior_flags['process_injection']
            })
        
        # Проверка на персистентность
        if self.behavior_flags.get('persistence', 0) > 0:
            risk_factors.append(('PERSISTENCE', 30))
            report.suspicious_behaviors.append({
                'type': 'PERSISTENCE',
                'severity': 'MEDIUM',
                'description': 'Попытки закрепления в системе (автозагрузка)',
                'count': self.behavior_flags['persistence']
            })
        
        # Проверка на шифрование
        if self.behavior_flags.get('crypto_operations', 0) > 5:
            risk_factors.append(('RANSOMWARE_BEHAVIOR', 50))
            report.suspicious_behaviors.append({
                'type': 'RANSOMWARE_BEHAVIOR',
                'severity': 'CRITICAL',
                'description': 'Массовые криптографические операции (возможно шифровальщик)',
                'count': self.behavior_flags['crypto_operations']
            })
        
        # Проверка на кейлоггинг
        if self.behavior_flags.get('keylogging', 0) > 0:
            risk_factors.append(('KEYLOGGING', 35))
            report.suspicious_behaviors.append({
                'type': 'KEYLOGGING',
                'severity': 'HIGH',
                'description': 'Обнаружен перехват нажатий клавиш',
                'count': self.behavior_flags['keylogging']
            })
        
        # Проверка сетевой активности
        if len(self.emulated_network['connections']) > 0:
            # Извлекаем IOC
            for conn in self.emulated_network['connections']:
                host = conn.get('host', '')
                if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', host):
                    report.ioc_extracted['ip_addresses'].append(host)
                elif '.' in host:
                    report.ioc_extracted['domains'].append(host)
            
            risk_factors.append(('NETWORK_ACTIVITY', 20))
            report.suspicious_behaviors.append({
                'type': 'NETWORK_ACTIVITY',
                'severity': 'MEDIUM',
                'description': f'Обнаружено {len(self.emulated_network["connections"])} сетевых подключений',
                'count': len(self.emulated_network['connections'])
            })
        
        # Анализ паттернов в параметрах вызовов
        for api_call in self.api_call_log:
            all_params = str(api_call.parameters).lower()
            
            for threat_type, patterns in self.SUSPICIOUS_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, all_params, re.IGNORECASE):
                        if threat_type not in report.threat_indicators:
                            report.threat_indicators[threat_type] = 0
                        report.threat_indicators[threat_type] += 1
        
        # Расчет общего риска
        total_risk = sum([factor[1] for factor in risk_factors])
        
        # Дополнительные баллы за множественные индикаторы
        for threat_type, count in report.threat_indicators.items():
            if count > 3:
                total_risk += 15
            elif count > 1:
                total_risk += 8
        
        report.risk_score = min(100.0, float(total_risk))
        
        # Классификация угрозы
        if report.risk_score >= 70:
            report.threat_classification = 'MALICIOUS'
        elif report.risk_score >= 40:
            report.threat_classification = 'SUSPICIOUS'
        else:
            report.threat_classification = 'CLEAN'
        
        # Генерация рекомендаций
        if 'CODE_INJECTION' in [b['type'] for b in report.suspicious_behaviors]:
            report.mitigation_recommendations.append("Немедленно изолировать файл")
            report.mitigation_recommendations.append("Проверить память на наличие инжектированного кода")
        
        if 'RANSOMWARE_BEHAVIOR' in [b['type'] for b in report.suspicious_behaviors]:
            report.mitigation_recommendations.append("Создать резервную копию важных данных")
            report.mitigation_recommendations.append("Отключить сеть для предотвращения распространения")
        
        if report.ioc_extracted['ip_addresses'] or report.ioc_extracted['domains']:
            report.mitigation_recommendations.append("Заблокировать выявленные IP/домены в фаерволе")
        
        return report
    
    def cleanup(self):
        """Очистка ресурсов песочницы"""
        try:
            if os.path.exists(self.sandbox_dir):
                shutil.rmtree(self.sandbox_dir)
            logger.info(f"Sandbox cleaned up: {self.sandbox_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up sandbox: {e}")


class BehavioralSandbox2:
    """
    Behavioral Sandbox 2.0 - Система поведенческого анализа с эмуляцией Windows API
    """
    
    def __init__(self, enable_gui_logging: bool = False):
        """
        Инициализация песочницы
        
        Args:
            enable_gui_logging: Включить логирование для GUI
        """
        self.emulator = WindowsAPIEmulator()
        self.enable_gui_logging = enable_gui_logging
        self.analysis_thread: Optional[threading.Thread] = None
        self.is_running = False
        
        # Настраиваем хуки для критических API
        self._setup_default_hooks()
        
        logger.info("Behavioral Sandbox 2.0 initialized")
    
    def _setup_default_hooks(self):
        """Настройка хуков по умолчанию для критических API"""
        
        # Хук для CreateRemoteThread (инъекция кода)
        def handle_create_remote_thread(params, api_hook):
            target_process = params.get('process_handle', '')
            start_address = params.get('start_address', 0)
            
            api_hook.stack_trace.append(f"INJECTION_TARGET: {target_process}")
            api_hook.stack_trace.append(f"INJECTION_ADDRESS: {hex(start_address)}")
            
            return self.emulator._default_emulation('CreateRemoteThread', params, api_hook)
        
        self.emulator.hook_api('CreateRemoteThread', handle_create_remote_thread)
        
        # Хук для RegSetValueEx (персистентность)
        def handle_reg_set_value(params, api_hook):
            key_path = params.get('key', '')
            value_data = params.get('data', '')
            
            # Проверяем на автозагрузку
            if 'CurrentVersion\\Run' in key_path or 'CurrentVersion\\RunOnce' in key_path:
                api_hook.stack_trace.append("PERSISTENCE_MECHANISM: AUTORUN")
            
            # Проверяем на подозрительные данные
            if any(x in str(value_data).lower() for x in ['cmd', 'powershell', 'temp', 'appdata']):
                api_hook.stack_trace.append("SUSPICIOUS_AUTORUN_DATA")
            
            return self.emulator._default_emulation('RegSetValueExA', params, api_hook)
        
        self.emulator.hook_api('RegSetValueExA', handle_reg_set_value)
        self.emulator.hook_api('RegSetValueExW', handle_reg_set_value)
        
        # Хук для URLDownloadToFile (скачивание вредоносов)
        def handle_url_download(params, api_hook):
            url = params.get('url', '')
            filename = params.get('filename', '')
            
            api_hook.network_operations.append({
                'operation': 'DOWNLOAD',
                'url': url,
                'destination': filename
            })
            
            # Извлекаем IOC
            if re.match(r'https?://', url):
                self.emulator.emulated_network['connections'].append({
                    'type': 'HTTP_DOWNLOAD',
                    'url': url,
                    'timestamp': time.time()
                })
            
            return self.emulator._default_emulation('URLDownloadToFileA', params, api_hook)
        
        self.emulator.hook_api('URLDownloadToFileA', handle_url_download)
        self.emulator.hook_api('URLDownloadToFileW', handle_url_download)
        
        # Хук для socket/connect (сетевая активность)
        def handle_network_connect(params, api_hook):
            host = params.get('host', '')
            port = params.get('port', 0)
            
            # Проверяем на известные плохие порты
            suspicious_ports = [4444, 5555, 6666, 31337, 12345]
            if port in suspicious_ports:
                api_hook.stack_trace.append(f"SUSPICIOUS_PORT: {port}")
            
            # Проверяем на C2 паттерны
            if any(x in str(host).lower() for x in ['no-ip', 'dyndns', 'ngrok', 'duckdns']):
                api_hook.stack_trace.append("POSSIBLE_C2_DOMAIN")
            
            return self.emulator._default_emulation('connect', params, api_hook)
        
        self.emulator.hook_api('connect', handle_network_connect)
    
    def analyze_file(self, file_path: str, simulation_script: Optional[List[Dict]] = None) -> BehaviorReport:
        """
        Анализ файла в песочнице
        
        Args:
            file_path: Путь к анализируемому файлу
            simulation_script: Скрипт симуляции поведения (опционально)
            
        Returns:
            Отчет о поведенческом анализе
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Вычисляем хеш файла
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        self.emulator.api_call_log.clear()
        self.emulator.behavior_flags.clear()
        self.emulator.emulated_network['connections'].clear()
        
        logger.info(f"Starting behavioral analysis of {file_path} (SHA256: {file_hash})")
        
        # Устанавливаем метаданные в отчет эмулятора
        self.emulator.api_call_log  # Access to ensure initialization
        
        # Если есть скрипт симуляции, выполняем его
        if simulation_script:
            logger.info("Executing simulation script...")
            for api_call in simulation_script:
                func_name = api_call.get('function')
                params = api_call.get('parameters', {})
                
                if func_name:
                    self.emulator.emulate_api_call(func_name, params, thread_id=1, process_id=1234)
                    time.sleep(0.01)  # Небольшая задержка между вызовами
        else:
            # Базовая симуляция - пытаемся извлечь и проанализировать строки
            self._simulate_basic_execution(file_path)
        
        # Получаем отчет
        report = self.emulator.analyze_behavior()
        report.file_hash = file_hash
        report.file_path = file_path
        
        logger.info(f"Analysis complete. Risk score: {report.risk_score}, Classification: {report.threat_classification}")
        
        return report
    
    def _simulate_basic_execution(self, file_path: str):
        """
        Базовая симуляция выполнения файла через анализ содержимого
        
        Args:
            file_path: Путь к файлу
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Пытаемся прочитать как текст (для скриптов)
            try:
                text_content = content.decode('utf-8', errors='ignore')
            except:
                text_content = ""
            
            # Анализируем на наличие подозрительных строк
            suspicious_strings = []
            
            # Поиск URL
            urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text_content)
            for url in urls[:10]:  # Ограничиваем количество
                self.emulator.emulate_api_call(
                    'URLDownloadToFileA',
                    {'url': url, 'filename': f'temp_{len(suspicious_strings)}.tmp'},
                    thread_id=1,
                    process_id=1234
                )
                suspicious_strings.append(url)
            
            # Поиск путей к файлам
            paths = re.findall(r'[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*', text_content)
            for path in paths[:10]:
                self.emulator.emulate_api_call(
                    'CreateFileA',
                    {'filename': path, 'content': b''},
                    thread_id=1,
                    process_id=1234
                )
            
            # Поиск команд PowerShell/CMD
            if 'powershell' in text_content.lower() or 'cmd.exe' in text_content.lower():
                self.emulator.emulate_api_call(
                    'CreateProcessA',
                    {'target': 'cmd.exe', 'command_line': text_content[:200]},
                    thread_id=1,
                    process_id=1234
                )
            
            # Поиск регистрных ключей
            reg_keys = re.findall(r'HKEY_[A-Z_]+\\[^\s"\']+', text_content)
            for key in reg_keys[:5]:
                self.emulator.emulate_api_call(
                    'RegSetValueExA',
                    {'key': key, 'value_name': 'malware', 'data': 'payload.exe'},
                    thread_id=1,
                    process_id=1234
                )
            
            # Для бинарных файлов эмулируем базовое поведение
            if len(content) > 0 and text_content.strip() == "":
                # Эмуляция загрузки PE файла
                self.emulator.emulate_api_call(
                    'CreateFileA',
                    {'filename': file_path, 'content': content[:1000]},
                    thread_id=1,
                    process_id=1234
                )
                
                # Эмуляция выделения памяти
                self.emulator.emulate_api_call(
                    'VirtualAlloc',
                    {'size': len(content), 'protection': 'PAGE_EXECUTE_READWRITE'},
                    thread_id=1,
                    process_id=1234
                )
        
        except Exception as e:
            logger.error(f"Error in basic simulation: {e}")
    
    def analyze_dynamic(self, file_path: str, timeout: int = 30) -> BehaviorReport:
        """
        Динамический анализ с реальным запуском в изолированной среде
        
        Args:
            file_path: Путь к файлу
            timeout: Таймаут анализа в секундах
            
        Returns:
            Отчет о поведенческом анализе
        """
        logger.warning("Dynamic analysis requires Docker/VM isolation. Using enhanced simulation.")
        
        # В реальной реализации здесь был бы запуск в Docker контейнере
        # Для пока используем расширенную симуляцию
        return self.analyze_file(file_path)
    
    def get_analysis_summary(self, report: BehaviorReport) -> Dict[str, Any]:
        """
        Получение краткой сводки анализа
        
        Args:
            report: Отчет о поведении
            
        Returns:
            Словарь с краткой информацией
        """
        return {
            'file_hash': report.file_hash,
            'risk_score': report.risk_score,
            'classification': report.threat_classification,
            'total_api_calls': len(report.api_calls),
            'suspicious_behaviors_count': len(report.suspicious_behaviors),
            'top_threat_indicators': dict(sorted(
                report.threat_indicators.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
            'ioc_summary': {
                'ip_count': len(report.ioc_extracted['ip_addresses']),
                'domain_count': len(report.ioc_extracted['domains']),
                'url_count': len(report.ioc_extracted['urls']),
                'dropped_files_count': len(report.ioc_extracted['dropped_files'])
            },
            'recommendations': report.mitigation_recommendations[:3]
        }
    
    def export_report(self, report: BehaviorReport, output_path: str, format: str = 'json'):
        """
        Экспорт отчета в файл
        
        Args:
            report: Отчет
            output_path: Путь вывода
            format: Формат ('json' или 'text')
        """
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(report), f, indent=2, default=str)
        elif format == 'text':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("BEHAVIORAL SANDBOX 2.0 - ANALYSIS REPORT\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"File: {report.file_path}\n")
                f.write(f"SHA256: {report.file_hash}\n")
                f.write(f"Analysis Duration: {report.total_duration:.2f}s\n")
                f.write(f"Risk Score: {report.risk_score}/100\n")
                f.write(f"Classification: {report.threat_classification}\n\n")
                
                f.write("-" * 40 + "\n")
                f.write("SUSPICIOUS BEHAVIORS:\n")
                f.write("-" * 40 + "\n")
                for behavior in report.suspicious_behaviors:
                    f.write(f"  [{behavior['severity']}] {behavior['type']}\n")
                    f.write(f"    {behavior['description']}\n")
                    f.write(f"    Count: {behavior['count']}\n\n")
                
                f.write("-" * 40 + "\n")
                f.write("THREAT INDICATORS:\n")
                f.write("-" * 40 + "\n")
                for indicator, count in sorted(report.threat_indicators.items(), 
                                               key=lambda x: x[1], reverse=True):
                    f.write(f"  {indicator}: {count}\n")
                
                f.write("\n" + "-" * 40 + "\n")
                f.write("EXTRACTED IOCs:\n")
                f.write("-" * 40 + "\n")
                for ioc_type, values in report.ioc_extracted.items():
                    if values:
                        f.write(f"  {ioc_type}:\n")
                        for value in values[:10]:
                            f.write(f"    - {value}\n")
                
                f.write("\n" + "-" * 40 + "\n")
                f.write("RECOMMENDATIONS:\n")
                f.write("-" * 40 + "\n")
                for rec in report.mitigation_recommendations:
                    f.write(f"  • {rec}\n")
        
        logger.info(f"Report exported to {output_path}")
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.emulator.cleanup()
        self.is_running = False


# Пример использования
if __name__ == "__main__":
    # Создание песочницы
    sandbox = BehavioralSandbox2()
    
    # Пример анализа с симуляцией
    simulation = [
        {
            'function': 'CreateRemoteThread',
            'parameters': {
                'process_handle': 'explorer.exe',
                'start_address': 0x12345678
            }
        },
        {
            'function': 'RegSetValueExA',
            'parameters': {
                'key': 'HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run',
                'value_name': 'Malware',
                'data': 'C:\\Temp\\malware.exe'
            }
        },
        {
            'function': 'URLDownloadToFileA',
            'parameters': {
                'url': 'http://malicious-domain.com/payload.exe',
                'filename': 'C:\\Temp\\payload.exe'
            }
        },
        {
            'function': 'connect',
            'parameters': {
                'host': '192.168.1.100',
                'port': 4444
            }
        },
        {
            'function': 'CryptEncrypt',
            'parameters': {
                'data_size': 1024000
            }
        }
    ]
    
    # Создаем тестовый файл
    test_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    test_file.write("Test malware simulation")
    test_file.close()
    
    try:
        # Выполняем анализ
        report = sandbox.analyze_file(test_file.name, simulation_script=simulation)
        
        # Выводим результаты
        summary = sandbox.get_analysis_summary(report)
        print("\n" + "="*60)
        print("BEHAVIORAL ANALYSIS SUMMARY")
        print("="*60)
        print(f"Risk Score: {summary['risk_score']}/100")
        print(f"Classification: {summary['classification']}")
        print(f"Total API Calls: {summary['total_api_calls']}")
        print(f"Suspicious Behaviors: {summary['suspicious_behaviors_count']}")
        
        if summary['top_threat_indicators']:
            print("\nTop Threat Indicators:")
            for indicator, count in summary['top_threat_indicators'].items():
                print(f"  - {indicator}: {count}")
        
        if summary['ioc_summary']['ip_count'] > 0 or summary['ioc_summary']['domain_count'] > 0:
            print("\nExtracted IOCs:")
            print(f"  IP Addresses: {summary['ioc_summary']['ip_count']}")
            print(f"  Domains: {summary['ioc_summary']['domain_count']}")
        
        if summary['recommendations']:
            print("\nRecommendations:")
            for rec in summary['recommendations']:
                print(f"  • {rec}")
        
        # Экспортируем полный отчет
        sandbox.export_report(report, 'behavioral_report.json', format='json')
        sandbox.export_report(report, 'behavioral_report.txt', format='text')
        
        print("\n✓ Reports exported successfully!")
        
    finally:
        # Очистка
        os.unlink(test_file.name)
        sandbox.cleanup()
