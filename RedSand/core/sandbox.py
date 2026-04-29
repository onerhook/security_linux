"""
RedSand Dynamic Sandbox (Cuckoo-like Implementation)
----------------------------------------------------
Реализует динамический анализ файлов в изолированной среде.
Основные принципы:
1. Изоляция выполнения (через ограниченный контекст и mock-объекты).
2. Мониторинг системных вызовов (API hooking).
3. Анализ поведения (сетевая активность, файловые операции, инъекции кода).
4. Генерация детального отчета о поведении.
"""

import os
import sys
import json
import time
import socket
import subprocess
import threading
import traceback
import hashlib
from datetime import datetime
from types import ModuleType
from io import StringIO
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

# --- Конфигурация песочницы ---
SANDBOX_TIMEOUT = 5  # Секунды на выполнение
MAX_MEMORY_USAGE = 100 * 1024 * 1024  # 100 MB лимит (эмуляция)


class ThreatCategory(Enum):
    NETWORK = "network_activity"
    FILE_SYSTEM = "file_system_access"
    CODE_INJECTION = "code_injection"
    SYSTEM_MODIFICATION = "system_modification"
    PERSISTENCE = "persistence_mechanism"
    CRYPTO = "crypto_operations"
    PROCESSES = "process_manipulation"


@dataclass
class Event:
    timestamp: float
    category: str
    severity: int  # 1-10
    action: str
    details: Dict[str, Any]
    stack_trace: str = ""


@dataclass
class SandboxReport:
    file_path: str
    file_hash: str
    start_time: str
    end_time: str
    duration: float
    verdict: str  # SAFE, SUSPICIOUS, MALICIOUS
    score: int  # 0-100
    events: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    behavior_summary: Dict[str, int] = field(default_factory=dict)


class SandboxEnvironment:
    """
    Эмулирует безопасное окружение для выполнения кода.
    Подменяет опасные модули на безопасные заглушки, которые логируют действия.
    """

    def __init__(self, logger_callback: Callable[[Event], None]):
        self.logger = logger_callback
        self.safe_modules = self._build_safe_environment()

    def _log_event(self, category: str, severity: int, action: str, details: Dict):
        event = Event(
            timestamp=time.time(),
            category=category,
            severity=severity,
            action=action,
            details=details,
            stack_trace="".join(traceback.format_stack()[:-2])
        )
        self.logger(event)

    def _build_safe_environment(self) -> Dict[str, Any]:
        """Создает словарь безопасных глобальных переменных и модулей."""

        # --- Безопасный OS ---
        class SafeOS:
            def __init__(self, logger):
                self.logger = logger
                self.name = "sandboxed_os"
                self.environ = {"USER": "sandbox_user", "HOME": "/tmp/sandbox"}

            def system(self, cmd):
                self.logger("SYSTEM_MODIFICATION", 9, "os.system call", {"command": cmd})
                raise PermissionError("Доступ к системным командам запрещен в песочнице")

            def popen(self, *args, **kwargs):
                self.logger("PROCESSES", 8, "os.popen call", {"args": args})
                raise PermissionError("Запуск процессов запрещен")

            def execv(self, *args):
                self.logger("PROCESSES", 9, "os.execv call", {"args": args})
                raise PermissionError("Выполнение внешних программ запрещено")

            def remove(self, path):
                self.logger("FILE_SYSTEM", 7, "File deletion attempt", {"path": path})
                # В песочнице можно удалять только во временной папке
                if "/tmp/sandbox" not in str(path):
                    raise PermissionError("Удаление файлов вне песочницы запрещено")

            def mkdir(self, path):
                self.logger("FILE_SYSTEM", 5, "Directory creation", {"path": path})

            def getenv(self, key, default=None):
                return self.environ.get(key, default)

            def __getattr__(self, item):
                # Разрешаем безопасные атрибуты
                if item in ['path', 'sep', 'curdir', 'pardir']:
                    return getattr(os.path, item, None)
                self.logger("SYSTEM_MODIFICATION", 6, f"Access to os.{item}", {})
                return lambda *args, **kwargs: None # Возвращаем заглушку для безопасности

        # --- Безопасная Сеть ---
        class SafeSocket:
            def __init__(self, logger):
                self.logger = logger

            def socket(self, *args, **kwargs):
                self.logger("NETWORK", 8, "Socket creation attempt", {"args": args})
                # Возвращаем фейковый сокет
                return FakeSocket(self.logger)

        class FakeSocket:
            def __init__(self, logger):
                self.logger = logger
            def connect(self, addr):
                self.logger("NETWORK", 9, "Connection attempt", {"address": addr})
                raise ConnectionRefusedError("Сетевое соединение заблокировано песочницей")
            def send(self, data):
                self.logger("NETWORK", 9, "Data sending attempt", {"size": len(data)})
                return 0
            def recv(self, bufsize):
                return b""
            def close(self):
                pass

        # --- Безопасный Subprocess ---
        class SafeSubprocess:
            def __init__(self, logger):
                self.logger = logger
            def call(self, *args, **kwargs):
                self.logger("PROCESSES", 9, "subprocess.call", {"args": args})
                raise PermissionError("Запуск процессов запрещен")
            def check_output(self, *args, **kwargs):
                self.logger("PROCESSES", 9, "subprocess.check_output", {"args": args})
                raise PermissionError("Запуск процессов запрещен")
            def Popen(self, *args, **kwargs):
                self.logger("PROCESSES", 9, "subprocess.Popen", {"args": args})
                raise PermissionError("Запуск процессов запрещен")

        # --- Безопасный Builtins ---
        def safe_open(file, mode='r', *args, **kwargs):
            # Логирование доступа к файлам
            severity = 5
            if 'w' in mode or 'a' in mode or 'x' in mode:
                severity = 7
            if '/etc/' in str(file) or '/windows/' in str(file):
                severity = 9

            # Ограничиваем доступ только к папке песочницы
            sandbox_path = "/tmp/sandbox"
            if sandbox_path not in str(file) and severity > 5:
                 # Для чтения разрешаем многие файлы, для записи - строго нет
                 if 'w' in mode or 'a' in mode:
                     raise PermissionError(f"Запись в {file} запрещена")

            self.logger("FILE_SYSTEM", severity, "File open", {"file": str(file), "mode": mode})

            # Если файл не существует и режим запись, создаем фиктивный
            if 'w' in mode or 'a' in mode or 'x' in mode:
                return StringIO()
            try:
                return open(file, mode, *args, **kwargs)
            except Exception:
                return StringIO() # Возвращаем пустой поток вместо реального файла для безопасности

        def safe_import(name, *args, **kwargs):
            # Блокируем опасные модули
            dangerous_modules = ['ctypes', 'cffi', 'multiprocessing', 'socketserver']
            if any(dm in name for dm in dangerous_modules):
                self.logger("CODE_INJECTION", 8, "Blocked module import", {"module": name})
                raise ImportError(f"Импорт модуля {name} запрещен в песочнице")

            # Разрешаем стандартные безопасные модули
            try:
                return __import__(name, *args, **kwargs)
            except Exception:
                self.logger("CODE_INJECTION", 4, "Failed import", {"module": name})
                return ModuleType(name) # Возвращаем пустой модуль

        env = {
            '__builtins__': {
                'open': safe_open,
                'input': lambda x="": "", # Блокируем ввод
                'print': lambda *args: None, # Блокируем вывод в консоль (логируем внутри)
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'pow': pow,
                'True': True,
                'False': False,
                'None': None,
                'Exception': Exception,
                'ImportError': ImportError,
                'PermissionError': PermissionError,
                'ConnectionRefusedError': ConnectionRefusedError,
            },
            'os': SafeOS(self._log_event),
            'sys': ModuleType('sys'), # Пустой sys для безопасности
            'socket': SafeSocket(self._log_event),
            'subprocess': SafeSubprocess(self._log_event),
            'time': time,
            'json': json,
            'hashlib': hashlib,
            'math': __import__('math'),
            'random': __import__('random'),
            're': __import__('re'),
            'datetime': datetime,
            'Path': Path,
        }

        # Добавляем алиасы для популярных паттернов импорта
        env['__builtins__']['__import__'] = safe_import

        return env

class DynamicSandbox:
    """
    Основной класс песочницы. Управляет выполнением, таймаутами и сбором отчетов.
    """

    def __init__(self):
        self.events: List[Event] = []
        self.errors: List[str] = []
        self.report: Optional[SandboxReport] = None

    def _event_logger(self, event: Event):
        self.events.append(event)

    def _calculate_score(self) -> int:
        """Вычисляет оценку угрозы на основе событий."""
        if not self.events:
            return 0

        score = 0
        weights = {
            "NETWORK": 15,
            "CODE_INJECTION": 20,
            "SYSTEM_MODIFICATION": 15,
            "PERSISTENCE": 25,
            "FILE_SYSTEM": 5,
            "PROCESSES": 15,
            "CRYPTO": 10
        }

        category_counts = {}

        for event in self.events:
            cat = event.category
            category_counts[cat] = category_counts.get(cat, 0) + 1
            # Базовый штраф за событие
            score += (event.severity / 10) * weights.get(cat, 5)

        # Дополнительные баллы за частоту опасных действий
        for cat, count in category_counts.items():
            if count > 5:
                score += 10
            if count > 20:
                score += 20

        return min(100, int(score))

    def _determine_verdict(self, score: int) -> str:
        if score >= 70:
            return "MALICIOUS"
        elif score >= 30:
            return "SUSPICIOUS"
        else:
            return "SAFE"

    def analyze_file(self, file_path: str) -> SandboxReport:
        """Запускает полный цикл анализа файла."""
        self.events = []
        self.errors = []

        start_time = time.time()
        file_hash = hashlib.sha256(open(file_path, 'rb').read()).hexdigest()

        # Чтение содержимого
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except UnicodeDecodeError:
            # Бинарный файл не может быть выполнен как скрипт в этой песочнице
            self.errors.append("Binary file detected. Static analysis only.")
            end_time = time.time()
            return SandboxReport(
                file_path=file_path,
                file_hash=file_hash,
                start_time=datetime.fromtimestamp(start_time).isoformat(),
                end_time=datetime.fromtimestamp(end_time).isoformat(),
                duration=end_time - start_time,
                verdict="UNKNOWN",
                score=0,
                events=[],
                errors=self.errors
            )

        # Подготовка окружения
        sandbox_env = SandboxEnvironment(self._event_logger)
        global_scope = sandbox_env.safe_modules.copy()

        # Добавляем переменную __file__
        global_scope['__file__'] = file_path

        execution_thread = None
        execution_error = None

        def target():
            nonlocal execution_error
            try:
                # Компиляция и выполнение
                compiled_code = compile(code, file_path, 'exec')
                exec(compiled_code, global_scope)
            except Exception as e:
                execution_error = str(e)
                # Логируем ошибку как событие, если это не явный запрет песочницы
                if "запрещен" not in str(e):
                    self.errors.append(f"Runtime error: {execution_error}")

        # Запуск в потоке с таймаутом
        execution_thread = threading.Thread(target=target)
        execution_thread.daemon = True
        execution_thread.start()
        execution_thread.join(timeout=SANDBOX_TIMEOUT)

        if execution_thread.is_alive():
            self.errors.append("Execution timeout exceeded. Possible infinite loop or hang.")
            # В реальном продакшене здесь нужно убивать поток, но в Python это сложно сделать безопасно.
            # Мы просто прерываем отчет.

        end_time = time.time()
        duration = end_time - start_time

        # Обработка результатов
        score = self._calculate_score()
        verdict = self._determine_verdict(score)

        # Группировка событий для отчета
        behavior_summary = {}
        for event in self.events:
            behavior_summary[event.category] = behavior_summary.get(event.category, 0) + 1

        serializable_events = [asdict(e) for e in self.events]
        # Очищаем стек трейса для краткости в основном отчете, оставляем только верхний уровень
        for e in serializable_events:
            e['stack_trace'] = e['stack_trace'].split('\n')[0]

        self.report = SandboxReport(
            file_path=file_path,
            file_hash=file_hash,
            start_time=datetime.fromtimestamp(start_time).isoformat(),
            end_time=datetime.fromtimestamp(end_time).isoformat(),
            duration=duration,
            verdict=verdict,
            score=score,
            events=serializable_events,
            errors=self.errors,
            behavior_summary=behavior_summary
        )

        return self.report

    def export_report(self, output_path: str):
        """Экспортирует отчет в JSON."""
        if not self.report:
            raise ValueError("No report available. Run analyze_file first.")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.report), f, indent=2, ensure_ascii=False)

        return output_path

# Алиас для совместимости
SandboxAnalyzer = DynamicSandbox

if __name__ == "__main__":
    print("RedSand Sandbox Module Initialized.")
    print("Для анализа используйте: DynamicSandbox().analyze_file('path/to/script.py')")
    
    # Пример создания тестового вредоносного скрипта
    test_script = """
import os
import socket

# Попытка сетевого соединения
try:
    s = socket.socket()
    s.connect(('evil.com', 8080))
except:
    pass

# Попытка выполнения команды
try:
    os.system('rm -rf /')
except:
    pass

# Легитимная операция
x = 10 + 20
print(x)
"""

    test_path = "/tmp/sandbox_test_malware.py"
    os.makedirs("/tmp/sandbox", exist_ok=True)

    with open(test_path, "w") as f:
        f.write(test_script)

    print(f"\nЗапуск анализа тестового файла: {test_path}")
    sandbox = DynamicSandbox()
    report = sandbox.analyze_file(test_path)

    print("\n--- ОТЧЕТ ПЕСОЧНИЦЫ ---")
    print(f"Вердикт: {report.verdict}")
    print(f"Оценка риска: {report.score}/100")
    print(f"Событий обнаружено: {len(report.events)}")
    print(f"Категории поведения: {report.behavior_summary}")

    if report.events:
        print("\nПервые 3 события:")
        for ev in report.events[:3]:
            print(f" - [{ev.category}] {ev.action}: {ev.details}")

    # Очистка
    if os.path.exists(test_path):
        os.remove(test_path)

    print("\nАнализ завершен.")
