"""
RedSand Reporter - Генератор отчетов

Функции:
- Генерация JSON отчета
- Создание человекочитаемого HTML отчета
- Формирование краткой сводки
- Экспорт IOC в различные форматы
"""

import json
from html import escape as html_escape
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class HTMLReportGenerator:
    """Генератор HTML отчетов"""
    
    CSS_STYLE = """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #d32f2f;
            border-bottom: 3px solid #d32f2f;
            padding-bottom: 10px;
        }
        h2 {
            color: #1976d2;
            margin-top: 30px;
        }
        h3 {
            color: #388e3c;
        }
        .verdict {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 18px;
            margin: 10px 0;
        }
        .verdict-safe {
            background: #c8e6c9;
            color: #2e7d32;
        }
        .verdict-suspicious {
            background: #fff9c4;
            color: #f57f17;
        }
        .verdict-malicious {
            background: #ffcdd2;
            color: #c62828;
        }
        .score-bar {
            width: 100%;
            height: 30px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }
        .score-fill {
            height: 100%;
            transition: width 0.5s;
        }
        .score-low { background: #4caf50; }
        .score-medium { background: #ff9800; }
        .score-high { background: #f44336; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #f5f5f5;
            font-weight: bold;
        }
        tr:hover {
            background: #f9f9f9;
        }
        .ioc-list {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 13px;
        }
        .timeline {
            border-left: 3px solid #1976d2;
            padding-left: 20px;
            margin-left: 10px;
        }
        .timeline-event {
            margin: 10px 0;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 4px;
        }
        .timestamp {
            color: #666;
            font-size: 12px;
        }
        .reason-item {
            padding: 5px 10px;
            background: #fff3e0;
            margin: 5px 0;
            border-radius: 4px;
            display: inline-block;
        }
        .metadata {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }
        .mitre-tag {
            display: inline-block;
            padding: 3px 8px;
            background: #9c27b0;
            color: white;
            border-radius: 3px;
            font-size: 12px;
            margin: 2px;
        }
    </style>
    """
    
    def generate(self, report: Dict, output_path: str) -> bool:
        """Генерация HTML отчета"""
        try:
            html_content = self._build_html(report)
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
        except Exception as e:
            print(f"Ошибка генерации HTML: {e}")
            return False
    
    def _build_html(self, report: Dict) -> str:
        """Построение HTML содержимого"""
        session = report.get('session', {})
        sample = session.get('sample', {})
        verdict = report.get('verdict', {})
        analysis = report.get('analysis', {})
        
        # Определение класса вердикта
        verdict_class = "verdict-safe"
        if verdict.get('verdict') == "SUSPICIOUS":
            verdict_class = "verdict-suspicious"
        elif verdict.get('verdict') == "MALICIOUS":
            verdict_class = "verdict-malicious"
        
        # Определение класса scores
        score_level = "score-low"
        if verdict.get('score', 0) >= 40:
            score_level = "score-medium"
        if verdict.get('score', 0) >= 70:
            score_level = "score-high"
        
        html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RedSand - Отчет анализа: {html_escape(sample.get('name', 'unknown'))}</title>
    {self.CSS_STYLE}
</head>
<body>
    <div class="container">
        <h1>🛡️ RedSand - Отчет анализа вредоносного ПО</h1>
        
        <div class="metadata">
            <strong>Файл:</strong> {html_escape(sample.get('name', 'unknown'))}<br>
            <strong>Размер:</strong> {sample.get('size', 0)} байт<br>
            <strong>MD5:</strong> <code>{html_escape(sample.get('hash_md5', ''))}</code><br>
            <strong>SHA256:</strong> <code>{html_escape(sample.get('hash_sha256', ''))}</code><br>
            <strong>Время анализа:</strong> {report.get('metadata', {}).get('analysis_time', '')}<br>
            <strong>Длительность:</strong> {session.get('duration_seconds', 0):.2f} сек
        </div>
        
        <h2>📊 Вердикт</h2>
        <div class="verdict {verdict_class}">
            {html_escape(verdict.get('verdict', 'UNKNOWN'))}
        </div>
        
        <div style="margin: 20px 0;">
            <strong>Оценка риска: {verdict.get('score', 0)}/100</strong>
            <div class="score-bar">
                <div class="score-fill {score_level}" style="width: {verdict.get('score', 0)}%"></div>
            </div>
            <strong>Уровень:</strong> {html_escape(verdict.get('risk_level', 'UNKNOWN'))}
        </div>
        
        <h3>Причины:</h3>
        <div>
            {''.join(f'<div class="reason-item">{html_escape(r)}</div>' for r in verdict.get('reasons', []))}
        </div>
        
        <h2>🔍 Индикаторы компрометации (IOC)</h2>
        {self._generate_ioc_section(analysis.get('iocs', {}))}
        
        <h2>🎯 MITRE ATT&CK</h2>
        {self._generate_mitre_section(analysis.get('mitre_attack', {}))}
        
        <h2>📈 Статистика</h2>
        {self._generate_statistics(analysis.get('statistics', {}))}
        
        <h2>⏱️ Временная шкала событий</h2>
        {self._generate_timeline(session.get('events', []))}
        
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
            Сгенерировано RedSand v1.0.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_ioc_section(self, iocs: Dict) -> str:
        """Генерация секции IOC"""
        if not any(iocs.values()):
            return "<p>IOC не обнаружены</p>"
        
        html_parts = []
        for ioc_type, items in iocs.items():
            if items:
                html_parts.append(f"<h4>{ioc_type.replace('_', ' ').title()}</h4>")
                html_parts.append('<div class="ioc-list">')
                for item in items[:20]:  # Ограничение на 20 элементов
                    html_parts.append(f"<div>{html_escape(str(item))}</div>")
                if len(items) > 20:
                    html_parts.append(f"<div>... и ещё {len(items) - 20}</div>")
                html_parts.append('</div>')
        
        return ''.join(html_parts)
    
    def _generate_mitre_section(self, mitre: Dict) -> str:
        """Генерация секции MITRE ATT&CK"""
        if not mitre:
            return "<p>Сопоставлений с MITRE ATT&CK не найдено</p>"
        
        html_parts = []
        for tactic, techniques in mitre.items():
            html_parts.append(f"<h4>{html_escape(tactic)}</h4>")
            tech_html = ''.join(f'<span class="mitre-tag">{html_escape(t)}</span>' for t in techniques)
            html_parts.append(f"<div>{tech_html}</div>")
        
        return ''.join(html_parts)
    
    def _generate_statistics(self, stats: Dict) -> str:
        """Генерация секции статистики"""
        if not stats:
            return "<p>Статистика недоступна</p>"
        
        return f"""
        <table>
            <tr>
                <th>Метрика</th>
                <th>Значение</th>
            </tr>
            <tr>
                <td>Всего событий</td>
                <td>{stats.get('total_events', 0)}</td>
            </tr>
            <tr>
                <td>Уникальных процессов</td>
                <td>{stats.get('unique_processes', 0)}</td>
            </tr>
            <tr>
                <td>Уникальных файлов</td>
                <td>{stats.get('unique_files', 0)}</td>
            </tr>
            <tr>
                <td>Временной интервал</td>
                <td>{stats.get('time_span', 0):.2f} сек</td>
            </tr>
        </table>
        """
    
    def _generate_timeline(self, events: List[Dict]) -> str:
        """Генерация временной шкалы"""
        if not events:
            return "<p>События не зафиксированы</p>"
        
        html_parts = ['<div class="timeline">']
        
        for event in events[:50]:  # Ограничение на 50 событий
            event_type = event.get('type', 'unknown')
            timestamp = event.get('timestamp', 0)
            data = event.get('data', {})
            
            # Форматирование данных
            data_str = ', '.join(f"{k}={html_escape(str(v))}" for k, v in list(data.items())[:3])
            
            html_parts.append(f"""
            <div class="timeline-event">
                <div class="timestamp">[{timestamp:.3f}] <strong>{html_escape(event_type.upper())}</strong></div>
                <div>{data_str}</div>
            </div>
            """)
        
        if len(events) > 50:
            html_parts.append(f"<div>... и ещё {len(events) - 50} событий</div>")
        
        html_parts.append('</div>')
        
        return ''.join(html_parts)


class JSONReporter:
    """Генератор JSON отчетов"""
    
    @staticmethod
    def save(report: Dict, output_path: str) -> bool:
        """Сохранение отчета в JSON"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Ошибка сохранения JSON: {e}")
            return False


class SummaryReporter:
    """Генератор краткой сводки"""
    
    @staticmethod
    def generate(report: Dict) -> str:
        """Генерация текстовой сводки"""
        session = report.get('session', {})
        sample = session.get('sample', {})
        verdict = report.get('verdict', {})
        analysis = report.get('analysis', {})
        
        summary = []
        summary.append("=" * 60)
        summary.append("RED SAND - КРАТКИЙ ОТЧЕТ АНАЛИЗА")
        summary.append("=" * 60)
        summary.append(f"Файл: {sample.get('name', 'unknown')}")
        summary.append(f"Размер: {sample.get('size', 0)} байт")
        summary.append(f"MD5: {sample.get('hash_md5', '')}")
        summary.append(f"SHA256: {sample.get('hash_sha256', '')}")
        summary.append("")
        summary.append("-" * 60)
        summary.append("ВЕРДИКТ")
        summary.append("-" * 60)
        summary.append(f"Статус: {verdict.get('verdict', 'UNKNOWN')}")
        summary.append(f"Оценка риска: {verdict.get('score', 0)}/100")
        summary.append(f"Уровень: {verdict.get('risk_level', 'UNKNOWN')}")
        summary.append("")
        summary.append("Причины:")
        for reason in verdict.get('reasons', []):
            summary.append(f"  • {reason}")
        summary.append("")
        summary.append("-" * 60)
        summary.append("ИНДИКАТОРЫ (IOC)")
        summary.append("-" * 60)
        
        iocs = analysis.get('iocs', {})
        for ioc_type, items in iocs.items():
            if items:
                summary.append(f"{ioc_type.replace('_', ' ').title()}: {len(items)}")
                for item in items[:5]:
                    summary.append(f"  - {item}")
                if len(items) > 5:
                    summary.append(f"  ... и ещё {len(items) - 5}")
        
        summary.append("")
        summary.append("-" * 60)
        summary.append("MITRE ATT&CK")
        summary.append("-" * 60)
        
        mitre = analysis.get('mitre_attack', {})
        for tactic, techniques in mitre.items():
            summary.append(f"{tactic}: {', '.join(techniques)}")
        
        summary.append("")
        summary.append("=" * 60)
        
        return '\n'.join(summary)


def generate_report(report: Dict, output_dir: str = 'reports') -> Dict[str, str]:
    """
    Генерация всех форматов отчетов
    
    Args:
        report: Данные отчета
        output_dir: Директория для сохранения
    
    Returns:
        Словарь с путями к созданным файлам
    """
    output_paths = {}
    
    # JSON отчет
    json_path = f"{output_dir}/report_full.json"
    if JSONReporter.save(report, json_path):
        output_paths['json'] = json_path
    
    # HTML отчет
    html_path = f"{output_dir}/report.html"
    generator = HTMLReportGenerator()
    if generator.generate(report, html_path):
        output_paths['html'] = html_path
    
    # Текстовая сводка
    txt_path = f"{output_dir}/report_summary.txt"
    try:
        summary = SummaryReporter.generate(report)
        Path(txt_path).write_text(summary, encoding='utf-8')
        output_paths['txt'] = txt_path
    except Exception as e:
        print(f"Ошибка генерации текстового отчета: {e}")
    
    return output_paths


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python reporter.py <report.json> [output_dir]")
        sys.exit(1)
    
    report_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'reports'
    
    # Загрузка отчета
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # Генерация отчетов
    paths = generate_report(report, output_dir)
    
    print("\nОтчеты сгенерированы:")
    for format_name, path in paths.items():
        print(f"  {format_name.upper()}: {path}")
    
    # Вывод сводки
    print("\n" + SummaryReporter.generate(report))
