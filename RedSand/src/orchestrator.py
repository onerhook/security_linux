"""
RedSand Orchestrator - Главный контроллер системы анализа

Управляет жизненным циклом анализа вредоносных файлов:
- Запуск и остановка мониторинга
- Управление образцом
- Сбор и агрегация данных
- Генерация отчета
"""

import os
import sys
import json
import time
import logging
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import psutil
except ImportError:
    print("Требуется установить: pip install psutil")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('RedSand.Orchestrator')


class SampleInfo:
    """Информация об образце для анализа"""
    
    def __init__(self, file_path: str):
        self.path = Path(file_path)
        self.name = self.path.name
        self.size = self.path.stat().st_size if self.path.exists() else 0
        self.hash_md5 = self._calculate_hash('md5')
        self.hash_sha256 = self._calculate_hash('sha256')
        self.submission_time = datetime.now().isoformat()
    
    def _calculate_hash(self, algorithm: str) -> str:
        """Вычисление хэша файла"""
        if not self.path.exists():
            return ""
        
        hash_func = hashlib.new(algorithm)
        with open(self.path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'path': str(self.path),
            'size': self.size,
            'hash_md5': self.hash_md5,
            'hash_sha256': self.hash_sha256,
            'submission_time': self.submission_time
        }


class MonitoringSession:
    """Сессия мониторинга поведения образца"""
    
    def __init__(self, sample: SampleInfo):
        self.sample = sample
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.events: List[Dict[str, Any]] = []
        self.process_tree: Dict[int, Dict] = {}
        self.network_connections: List[Dict] = []
        self.file_changes: List[Dict] = []
        self.registry_changes: List[Dict] = []
        self.errors: List[str] = []
    
    def start(self):
        """Начало сессии мониторинга"""
        self.start_time = time.time()
        logger.info(f"Начало анализа образца: {self.sample.name}")
    
    def stop(self):
        """Завершение сессии мониторинга"""
        self.end_time = time.time()
        logger.info(f"Завершение анализа образца: {self.sample.name}")
    
    def add_event(self, event_type: str, data: Dict[str, Any]):
        """Добавление события в лог"""
        event = {
            'timestamp': time.time(),
            'type': event_type,
            'data': data
        }
        self.events.append(event)
        
        # Категоризация событий
        if event_type == 'file':
            self.file_changes.append(event)
        elif event_type == 'registry':
            self.registry_changes.append(event)
        elif event_type == 'network':
            self.network_connections.append(event)
        elif event_type == 'process':
            self._update_process_tree(data)
    
    def _update_process_tree(self, process_data: Dict):
        """Обновление дерева процессов"""
        pid = process_data.get('pid')
        if pid:
            self.process_tree[pid] = process_data
    
    def get_duration(self) -> float:
        """Получение длительности анализа в секундах"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sample': self.sample.to_dict(),
            'duration_seconds': self.get_duration(),
            'events_count': len(self.events),
            'file_changes_count': len(self.file_changes),
            'registry_changes_count': len(self.registry_changes),
            'network_connections_count': len(self.network_connections),
            'processes_count': len(self.process_tree),
            'errors': self.errors,
            'events': self.events
        }


class Orchestrator:
    """Главный оркестратор системы RedSand"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.session: Optional[MonitoringSession] = None
        self.agent_process: Optional[subprocess.Popen] = None
        
        # Создание необходимых директорий
        for dir_name in ['logs', 'samples', 'reports']:
            Path(dir_name).mkdir(exist_ok=True)
    
    def _default_config(self) -> Dict:
        """Конфигурация по умолчанию"""
        return {
            'analysis_timeout': 60,  # секунд
            'monitoring_interval': 0.1,  # секунд
            'enable_network_monitor': True,
            'enable_file_monitor': True,
            'enable_registry_monitor': True,
            'enable_process_monitor': True,
            'agent_path': 'bin/RedSandAgent.dll',
            'yara_rules_path': 'rules/'
        }
    
    def analyze(self, sample_path: str, output_path: Optional[str] = None) -> Dict:
        """
        Основной метод анализа образца
        
        Args:
            sample_path: Путь к файлу для анализа
            output_path: Путь для сохранения отчета (опционально)
        
        Returns:
            Словарь с результатами анализа
        """
        logger.info(f"Начало анализа файла: {sample_path}")
        
        # Проверка существования файла
        if not os.path.exists(sample_path):
            error_msg = f"Файл не найден: {sample_path}"
            logger.error(error_msg)
            return {'error': error_msg}
        
        # Инициализация сессии
        sample_info = SampleInfo(sample_path)
        self.session = MonitoringSession(sample_info)
        
        try:
            # Запуск мониторинга
            self._start_monitoring()
            
            # Запуск образца
            self._execute_sample(sample_path)
            
            # Ожидание завершения анализа
            self._wait_for_completion()
            
        except Exception as e:
            logger.error(f"Ошибка во время анализа: {str(e)}")
            self.session.errors.append(str(e))
        finally:
            # Остановка мониторинга
            self._stop_monitoring()
        
        # Формирование отчета
        report = self._generate_report()
        
        # Сохранение отчета
        if output_path:
            self._save_report(report, output_path)
        
        return report
    
    def _start_monitoring(self):
        """Запуск подсистем мониторинга"""
        logger.info("Запуск мониторинга...")
        self.session.start()
        
        # Здесь будет запуск C++ агента через DLL injection или отдельный процесс
        # Для демонстрации используем заглушку
        if self.config.get('enable_process_monitor'):
            self._monitor_processes()
    
    def _stop_monitoring(self):
        """Остановка подсистем мониторинга"""
        logger.info("Остановка мониторинга...")
        if self.session:
            self.session.stop()
        
        if self.agent_process:
            self.agent_process.terminate()
            self.agent_process = None
    
    def _execute_sample(self, sample_path: str):
        """Запуск образца на выполнение"""
        logger.info(f"Запуск образца: {sample_path}")
        
        # В реальной реализации здесь будет запуск через C++ агент
        # Для демонстрации используем subprocess с ограничениями
        try:
            # ЗАМЕТКА: В продакшене использовать только в изолированной среде!
            process = subprocess.Popen(
                [sample_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Ожидание завершения или таймаут
            try:
                process.wait(timeout=self.config['analysis_timeout'])
            except subprocess.TimeoutExpired:
                logger.warning("Таймаут выполнения образца, принудительная остановка")
                process.kill()
                self.session.add_event('timeout', {'message': 'Превышено время выполнения'})
                
        except Exception as e:
            logger.error(f"Ошибка запуска образца: {str(e)}")
            self.session.add_event('error', {'message': str(e)})
    
    def _monitor_processes(self):
        """Мониторинг процессов (базовая реализация)"""
        initial_processes = set(psutil.pids())
        
        # Периодическая проверка новых процессов
        check_interval = 0.5
        elapsed = 0
        
        while elapsed < self.config['analysis_timeout']:
            current_processes = set(psutil.pids())
            new_pids = current_processes - initial_processes
            
            for pid in new_pids:
                try:
                    proc = psutil.Process(pid)
                    process_info = {
                        'pid': pid,
                        'name': proc.name(),
                        'cmdline': proc.cmdline(),
                        'ppid': proc.ppid(),
                        'status': proc.status(),
                        'username': proc.username()
                    }
                    self.session.add_event('process', process_info)
                    logger.info(f"Обнаружен новый процесс: {proc.name()} (PID: {pid})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            time.sleep(check_interval)
            elapsed += check_interval
    
    def _wait_for_completion(self):
        """Ожидание завершения анализа"""
        logger.info("Ожидание завершения анализа...")
        # Реализация зависит от метода мониторинга
    
    def _generate_report(self) -> Dict:
        """Генерация отчета о анализе"""
        if not self.session:
            return {'error': 'Нет активной сессии анализа'}
        
        report = {
            'metadata': {
                'tool': 'RedSand',
                'version': '1.0.0',
                'analysis_time': datetime.now().isoformat(),
                'host': os.getenv('COMPUTERNAME', 'unknown')
            },
            'session': self.session.to_dict(),
            'verdict': self._calculate_verdict(),
            'iocs': self._extract_iocs()
        }
        
        return report
    
    def _calculate_verdict(self) -> Dict:
        """Расчет вердикта на основе поведения"""
        score = 0
        reasons = []
        
        # Простая эвристика для демонстрации
        if len(self.session.file_changes) > 10:
            score += 30
            reasons.append("Множественные изменения файлов")
        
        if len(self.session.registry_changes) > 5:
            score += 25
            reasons.append("Изменения в реестре")
        
        if len(self.session.network_connections) > 0:
            score += 20
            reasons.append("Сетевая активность")
        
        if len(self.session.process_tree) > 3:
            score += 15
            reasons.append("Создание дочерних процессов")
        
        if self.session.errors:
            score += 10
            reasons.append("Ошибки при выполнении")
        
        # Определение уровня риска
        if score >= 70:
            risk_level = "HIGH"
            verdict = "MALICIOUS"
        elif score >= 40:
            risk_level = "MEDIUM"
            verdict = "SUSPICIOUS"
        else:
            risk_level = "LOW"
            verdict = "SAFE"
        
        return {
            'score': min(score, 100),
            'risk_level': risk_level,
            'verdict': verdict,
            'reasons': reasons
        }
    
    def _extract_iocs(self) -> Dict:
        """Извлечение индикаторов компрометации (IOCs)"""
        iocs = {
            'files': [],
            'registry_keys': [],
            'ip_addresses': [],
            'domains': [],
            'urls': [],
            'mutexes': []
        }
        
        # Извлечение из событий файлов
        for event in self.session.file_changes:
            if 'path' in event.get('data', {}):
                iocs['files'].append(event['data']['path'])
        
        # Извлечение из событий реестра
        for event in self.session.registry_changes:
            if 'key' in event.get('data', {}):
                iocs['registry_keys'].append(event['data']['key'])
        
        # Удаление дубликатов
        for key in iocs:
            iocs[key] = list(set(iocs[key]))
        
        return iocs
    
    def _save_report(self, report: Dict, output_path: str):
        """Сохранение отчета в файл"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Отчет сохранен: {output_path}")
        except Exception as e:
            logger.error(f"Ошибка сохранения отчета: {str(e)}")


def main():
    """Точка входа для запуска из командной строки"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RedSand - Анализ вредоносных файлов')
    parser.add_argument('--sample', required=True, help='Путь к файлу для анализа')
    parser.add_argument('--output', default='reports/report.json', help='Путь для отчета')
    parser.add_argument('--timeout', type=int, default=60, help='Таймаут анализа в секундах')
    parser.add_argument('--verbose', action='store_true', help='Подробный вывод')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Создание оркестратора
    config = {'analysis_timeout': args.timeout}
    orchestrator = Orchestrator(config)
    
    # Запуск анализа
    report = orchestrator.analyze(args.sample, args.output)
    
    # Вывод краткого результата
    print("\n" + "="*50)
    print("РЕЗУЛЬТАТЫ АНАЛИЗА")
    print("="*50)
    print(f"Файл: {report['session']['sample']['name']}")
    print(f"Вердикт: {report['verdict']['verdict']}")
    print(f"Уровень риска: {report['verdict']['risk_level']}")
    print(f"Оценка: {report['verdict']['score']}/100")
    print(f"Причины: {', '.join(report['verdict']['reasons'])}")
    print(f"Отчет сохранен: {args.output}")
    print("="*50)


if __name__ == '__main__':
    main()
