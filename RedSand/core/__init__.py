"""
RedSand Core - Основные модули системы безопасности

Модули:
- virus_scanner: Базовый сканер вирусов с сигнатурным анализом
- extended_scanner: Расширенный сканер с эвристическим анализом
- threat_classifier: Классификатор типов угроз
- ml_classifier: ML-классификатор на основе ансамбля моделей
- sandbox: Базовая песочница для анализа
- docker_sandbox: Песочница на основе Docker
- behavioral_sandbox_v2: Behavioral Sandbox 2.0 с эмуляцией Windows API
- orchestrator: Оркестратор анализа
- realtime_antivirus: Антивирус реального времени
- quarantine_manager: Менеджер карантина
- report_generator: Генератор отчетов
- poly_engine: Полиморфный движок
- anti_sandbox: Детектор анти-песочниц
- network_emulator: Эмулятор сети
- thread_safe_scanner: Многопоточный сканер с кэшированием
- panic_button: Экстренная остановка
"""

from .virus_scanner import VirusScanner
from .extended_scanner import ExtendedVirusScanner
from .threat_classifier import ThreatClassifier
from .sandbox import SandboxAnalyzer
from .orchestrator import AnalysisOrchestrator
from .realtime_antivirus import RealTimeAntivirus
from .quarantine_manager import QuarantineManager
from .report_generator import ReportGenerator

__all__ = [
    'VirusScanner',
    'ExtendedVirusScanner',
    'ThreatClassifier',
    'SandboxAnalyzer',
    'AnalysisOrchestrator',
    'RealTimeAntivirus',
    'QuarantineManager',
    'ReportGenerator'
]
