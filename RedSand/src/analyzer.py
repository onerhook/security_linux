"""
RedSand Analyzer - Движок анализа поведения

Функции:
- Построение графа поведения
- Расчет риска на основе эвристик
- Сопоставление с паттернами MITRE ATT&CK
- Извлечение IOC (Indicators of Compromise)
- Интеграция с YARA правилами
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict


class BehaviorGraph:
    """Граф поведения для визуализации действий образца"""
    
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Dict] = []
        self.timeline: List[Dict] = []
    
    def add_node(self, node_id: str, node_type: str, data: Dict):
        """Добавление узла в граф"""
        self.nodes[node_id] = {
            'type': node_type,
            'data': data,
            'timestamp': data.get('timestamp', 0)
        }
    
    def add_edge(self, source: str, target: str, action: str):
        """Добавление связи между узлами"""
        self.edges.append({
            'source': source,
            'target': target,
            'action': action
        })
    
    def add_event(self, event: Dict):
        """Добавление события во временную шкалу"""
        self.timeline.append(event)
    
    def sort_timeline(self):
        """Сортировка временной шкалы"""
        self.timeline.sort(key=lambda x: x.get('timestamp', 0))
    
    def to_dict(self) -> Dict:
        return {
            'nodes': self.nodes,
            'edges': self.edges,
            'timeline': self.timeline
        }


class MITREMapper:
    """Сопоставление действий с тактиками MITRE ATT&CK"""
    
    # Упрощенная карта соответствий
    TECHNIQUE_MAP = {
        'file_create': ['T1005', 'T1039'],  # Data from Local System
        'file_write': ['T1005', 'T1105'],   # Ingress Tool Transfer
        'file_delete': ['T1070'],           # Indicator Removal
        'registry_set': ['T1547'],          # Boot or Logon Autostart Execution
        'process_create': ['T1059'],        # Command and Scripting Interpreter
        'network_connect': ['T1071', 'T1095'],  # Application Layer Protocol
        'dll_load': ['T1055'],              # Process Injection
        'injection': ['T1055']              # Process Injection
    }
    
    TACTIC_MAP = {
        'T1005': 'Collection',
        'T1039': 'Collection',
        'T1105': 'Command and Control',
        'T1070': 'Defense Evasion',
        'T1547': 'Persistence',
        'T1059': 'Execution',
        'T1071': 'Command and Control',
        'T1095': 'Command and Control',
        'T1055': 'Defense Evasion'
    }
    
    @classmethod
    def map_event(cls, event_type: str) -> List[Dict]:
        """Сопоставление события с техниками MITRE"""
        techniques = cls.TECHNIQUE_MAP.get(event_type, [])
        result = []
        
        for tech_id in techniques:
            result.append({
                'technique_id': tech_id,
                'technique_name': tech_id,
                'tactic': cls.TACTIC_MAP.get(tech_id, 'Unknown')
            })
        
        return result


class RiskCalculator:
    """Калькулятор риска на основе поведения"""
    
    # Веса для различных типов событий
    EVENT_WEIGHTS = {
        'file': 5,
        'registry': 8,
        'network': 10,
        'process': 6,
        'injection': 15,
        'error': 3
    }
    
    # Пороговые значения
    THRESHOLDS = {
        'file_changes': 10,
        'registry_changes': 5,
        'network_connections': 3,
        'process_spawn': 5
    }
    
    # Подозрительные паттерны
    SUSPICIOUS_PATTERNS = [
        r'.*\.exe$',  # Запуск исполняемых файлов
        r'.*\\AppData\\.*',  # Доступ к AppData
        r'.*\\Temp\\.*',  # Доступ к Temp
        r'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run',  # Автозагрузка
        r'cmd\.exe',  # Использование cmd
        r'powershell',  # Использование PowerShell
        r'wscript|cscript',  # Использование скриптов
    ]
    
    def __init__(self):
        self.score = 0
        self.reasons: List[str] = []
    
    def calculate(self, events: List[Dict]) -> Tuple[int, str, List[str]]:
        """
        Расчет общего риска
        
        Returns:
            (score, risk_level, reasons)
        """
        self.score = 0
        self.reasons = []
        
        # Подсчет событий по типам
        event_counts = defaultdict(int)
        for event in events:
            event_type = event.get('type', 'unknown')
            event_counts[event_type] += 1
            
            # Проверка на подозрительные паттерны
            self._check_patterns(event)
        
        # Расчет базового scores
        for event_type, count in event_counts.items():
            weight = self.EVENT_WEIGHTS.get(event_type, 1)
            self.score += count * weight
        
        # Бонусы за превышение порогов
        if event_counts.get('file', 0) > self.THRESHOLDS['file_changes']:
            self.score += 20
            self.reasons.append("Множественные изменения файлов")
        
        if event_counts.get('registry', 0) > self.THRESHOLDS['registry_changes']:
            self.score += 25
            self.reasons.append("Активные изменения реестра")
        
        if event_counts.get('network', 0) > self.THRESHOLDS['network_connections']:
            self.score += 30
            self.reasons.append("Интенсивная сетевая активность")
        
        if event_counts.get('process', 0) > self.THRESHOLDS['process_spawn']:
            self.score += 20
            self.reasons.append("Создание множества процессов")
        
        if event_counts.get('injection', 0) > 0:
            self.score += 50
            self.reasons.append("Попытки инъекции кода")
        
        # Нормализация scores (0-100)
        self.score = min(100, self.score)
        
        # Определение уровня риска
        if self.score >= 70:
            risk_level = "HIGH"
        elif self.score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return self.score, risk_level, self.reasons
    
    def _check_patterns(self, event: Dict):
        """Проверка события на подозрительные паттерны"""
        data = event.get('data', {})
        text_to_check = ""
        
        # Сбор текста для проверки
        if 'path' in data:
            text_to_check += data['path']
        if 'key' in data:
            text_to_check += data['key']
        if 'name' in data:
            text_to_check += data['name']
        if 'cmdline' in data:
            text_to_check += ' '.join(data['cmdline'])
        
        # Проверка паттернов
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                self.score += 5
                reason = f"Подозрительный паттерн: {pattern}"
                if reason not in self.reasons:
                    self.reasons.append(reason)
                break


class IOCExtractor:
    """Извлечение индикаторов компрометации"""
    
    # Регулярные выражения для извлечения
    PATTERNS = {
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'domain': r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+(?:com|net|org|ru|info|biz|xyz|top)\b',
        'url': r'https?://[^\s<>"{}|\\^`\[\]]+',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'mutex': r'\\BaseNamedObjects\\[^\s]+'
    }
    
    def extract(self, events: List[Dict]) -> Dict[str, List[str]]:
        """Извлечение всех IOC из событий"""
        iocs = {
            'files': set(),
            'registry_keys': set(),
            'ip_addresses': set(),
            'domains': set(),
            'urls': set(),
            'mutexes': set(),
            'emails': set()
        }
        
        for event in events:
            data = event.get('data', {})
            
            # Извлечение файловых путей
            if 'path' in data:
                iocs['files'].add(data['path'])
            
            # Извлечение ключей реестра
            if 'key' in data:
                iocs['registry_keys'].add(data['key'])
            
            # Извлечение текстовых данных для regex
            text_data = self._extract_text(data)
            self._extract_with_regex(text_data, iocs)
        
        # Преобразование множеств в списки
        return {k: list(v) for k, v in iocs.items()}
    
    def _extract_text(self, data: Dict) -> str:
        """Извлечение всего текста из данных"""
        texts = []
        for value in data.values():
            if isinstance(value, str):
                texts.append(value)
            elif isinstance(value, list):
                texts.extend([str(v) for v in value if isinstance(v, str)])
        return ' '.join(texts)
    
    def _extract_with_regex(self, text: str, iocs: Dict):
        """Извлечение IOC с помощью регулярных выражений"""
        for ioc_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                key = ioc_type.replace('_', '_')
                if key in iocs:
                    iocs[key].update(matches)


class YARAScanner:
    """Сканер YARA правил (заглушка для демонстрации)"""
    
    def __init__(self, rules_path: Optional[str] = None):
        self.rules_path = rules_path
        self.rules = []
        self._load_rules()
    
    def _load_rules(self):
        """Загрузка YARA правил"""
        if not self.rules_path or not Path(self.rules_path).exists():
            return
        
        # В реальной реализации:
        # import yara
        # self.rules = yara.compile(filepath=self.rules_path)
        pass
    
    def scan(self, file_path: str) -> List[Dict]:
        """Сканирование файла правилами YARA"""
        results = []
        
        # В реальной реализации:
        # if self.rules:
        #     matches = self.rules.match(file_path)
        #     for match in matches:
        #         results.append({
        #             'rule': match.rule,
        #             'namespace': match.namespace,
        #             'strings': match.strings
        #         })
        
        return results


class Analyzer:
    """Главный класс анализатора"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.graph = BehaviorGraph()
        self.risk_calculator = RiskCalculator()
        self.ioc_extractor = IOCExtractor()
        self.yara_scanner = YARAScanner(self.config.get('yara_rules_path'))
    
    def analyze(self, report_data: Dict) -> Dict:
        """
        Полный анализ отчета
        
        Args:
            report_data: Данные отчета оркестратора
        
        Returns:
            Расширенный отчет с анализом
        """
        events = report_data.get('session', {}).get('events', [])
        
        # Построение графа поведения
        self._build_behavior_graph(events)
        
        # Расчет риска
        score, risk_level, reasons = self.risk_calculator.calculate(events)
        
        # Извлечение IOC
        iocs = self.ioc_extractor.extract(events)
        
        # Сопоставление с MITRE ATT&CK
        mitre_mappings = self._map_to_mitre(events)
        
        # Сканирование YARA
        sample_path = report_data.get('session', {}).get('sample', {}).get('path', '')
        yara_results = []
        if sample_path:
            yara_results = self.yara_scanner.scan(sample_path)
        
        # Формирование расширенного отчета
        analysis_report = {
            'behavior_graph': self.graph.to_dict(),
            'risk_assessment': {
                'score': score,
                'level': risk_level,
                'reasons': reasons
            },
            'iocs': iocs,
            'mitre_attack': mitre_mappings,
            'yara_matches': yara_results,
            'statistics': self._calculate_statistics(events)
        }
        
        return analysis_report
    
    def _build_behavior_graph(self, events: List[Dict]):
        """Построение графа поведения"""
        for event in events:
            event_type = event.get('type', 'unknown')
            timestamp = event.get('timestamp', 0)
            data = event.get('data', {})
            
            # Добавление события во временную шкалу
            self.graph.add_event(event)
            
            # Создание узлов на основе типа события
            node_id = f"{event_type}_{timestamp}"
            
            if event_type == 'process':
                self.graph.add_node(node_id, 'process', data)
                if 'ppid' in data:
                    parent_id = f"process_{data['ppid']}"
                    self.graph.add_edge(parent_id, node_id, 'spawned')
            
            elif event_type == 'file':
                self.graph.add_node(node_id, 'file', data)
            
            elif event_type == 'network':
                self.graph.add_node(node_id, 'network', data)
            
            elif event_type == 'registry':
                self.graph.add_node(node_id, 'registry', data)
        
        self.graph.sort_timeline()
    
    def _map_to_mitre(self, events: List[Dict]) -> Dict:
        """Сопоставление событий с MITRE ATT&CK"""
        mappings = defaultdict(list)
        
        for event in events:
            event_type = event.get('type', 'unknown')
            technique_list = MITREMapper.map_event(event_type)
            
            for tech in technique_list:
                mappings[tech['tactic']].append(tech['technique_id'])
        
        # Удаление дубликатов
        return {k: list(set(v)) for k, v in mappings.items()}
    
    def _calculate_statistics(self, events: List[Dict]) -> Dict:
        """Расчет статистики по событиям"""
        stats = {
            'total_events': len(events),
            'events_by_type': defaultdict(int),
            'unique_processes': set(),
            'unique_files': set(),
            'time_span': 0
        }
        
        if events:
            timestamps = [e.get('timestamp', 0) for e in events]
            stats['time_span'] = max(timestamps) - min(timestamps)
        
        for event in events:
            event_type = event.get('type', 'unknown')
            stats['events_by_type'][event_type] += 1
            
            data = event.get('data', {})
            if 'pid' in data:
                stats['unique_processes'].add(data['pid'])
            if 'path' in data:
                stats['unique_files'].add(data['path'])
        
        # Преобразование для JSON сериализации
        stats['events_by_type'] = dict(stats['events_by_type'])
        stats['unique_processes'] = len(stats['unique_processes'])
        stats['unique_files'] = len(stats['unique_files'])
        
        return stats


def analyze_report(report_path: str, output_path: Optional[str] = None) -> Dict:
    """
    Удобная функция для анализа отчета
    
    Args:
        report_path: Путь к JSON отчету оркестратора
        output_path: Путь для сохранения расширенного отчета
    
    Returns:
        Расширенный отчет
    """
    # Загрузка отчета
    with open(report_path, 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    # Анализ
    analyzer = Analyzer()
    analysis = analyzer.analyze(report_data)
    
    # Объединение отчетов
    full_report = {
        **report_data,
        'analysis': analysis
    }
    
    # Сохранение
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)
    
    return full_report


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python analyzer.py <report.json> [output.json]")
        sys.exit(1)
    
    report_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = analyze_report(report_path, output_path)
    
    print("\n" + "="*50)
    print("РЕЗУЛЬТАТЫ АНАЛИЗА")
    print("="*50)
    print(f"Оценка риска: {result['analysis']['risk_assessment']['score']}/100")
    print(f"Уровень: {result['analysis']['risk_assessment']['level']}")
    print(f"Причины: {', '.join(result['analysis']['risk_assessment']['reasons'])}")
    print(f"\nIOC найдено:")
    for ioc_type, ioc_list in result['analysis']['iocs'].items():
        if ioc_list:
            print(f"  {ioc_type}: {len(ioc_list)}")
    print(f"\nMITRE ATT&CK тактики:")
    for tactic, techniques in result['analysis']['mitre_attack'].items():
        print(f"  {tactic}: {', '.join(techniques)}")
    print("="*50)
