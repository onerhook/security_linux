#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Generator - Генератор отчетов
Создание отчетов в форматах JSON, HTML, TXT
"""

import json
import os
from datetime import datetime
from pathlib import Path

class ReportGenerator:
    def __init__(self, output_dir='reports'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_json(self, report_data):
        """Генерация JSON отчета"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def generate_html(self, report_data):
        """Генерация интерактивного HTML отчета"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{timestamp}.html"
        filepath = self.output_dir / filename
        
        threat_info = report_data.get('threat_classification', {})
        risk_score = threat_info.get('risk_score', 0)
        
        # Определение цвета риска
        if risk_score >= 70:
            risk_color = '#dc3545'
            risk_label = 'MALICIOUS'
        elif risk_score >= 40:
            risk_color = '#ffc107'
            risk_label = 'SUSPICIOUS'
        else:
            risk_color = '#28a745'
            risk_label = 'SAFE'
        
        # Обработка analysis_time - может быть dict или float
        analysis_time = report_data.get('analysis_time', {})
        if isinstance(analysis_time, dict):
            start_time = analysis_time.get('start', 'N/A')
            end_time = analysis_time.get('end', 'N/A')
            duration = analysis_time.get('duration', 0)
        else:
            # Если это float, используем текущее время
            now = datetime.now()
            start_time = now.isoformat()
            end_time = now.isoformat()
            duration = float(analysis_time) if isinstance(analysis_time, (int, float)) else 0
        
        html_content = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RedSand Secure - Отчет об анализе</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; }}
        h2 {{ color: #2c3e50; margin-top: 30px; }}
        .verdict {{ display: inline-block; padding: 15px 30px; border-radius: 5px; color: white; font-weight: bold; font-size: 18px; background: {risk_color}; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }}
        .info-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #e74c3c; }}
        .info-card h3 {{ margin-top: 0; color: #2c3e50; }}
        .tag {{ display: inline-block; background: #e9ecef; padding: 5px 10px; margin: 3px; border-radius: 3px; font-size: 12px; }}
        .ioc-item {{ background: #fff3cd; padding: 8px; margin: 5px 0; border-radius: 4px; cursor: pointer; transition: background 0.2s; }}
        .ioc-item:hover {{ background: #ffe69c; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background: #f8f9fa; font-weight: 600; }}
        .copy-btn {{ background: #007bff; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; float: right; }}
        .copy-btn:hover {{ background: #0056b3; }}
        .timeline {{ position: relative; padding-left: 30px; }}
        .timeline-item {{ position: relative; padding: 10px 0; }}
        .timeline-item::before {{ content: "•"; position: absolute; left: -20px; color: #e74c3c; font-size: 20px; }}
        .mitre-tag {{ background: #6f42c1; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ RedSand Secure - Отчет об анализе вредоносного ПО</h1>
        
        <div style="text-align: center; margin: 30px 0;">
            <div class="verdict">{risk_label}</div>
            <p style="margin-top: 10px; color: #666;">Уровень риска: <strong>{risk_score}/100</strong></p>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <h3>📁 Информация о файле</h3>
                <p><strong>Имя:</strong> {report_data.get('file', {}).get('name', 'N/A')}</p>
                <p><strong>Путь:</strong> {report_data.get('file', {}).get('path', 'N/A')}</p>
                <p><strong>Размер:</strong> {report_data.get('file', {}).get('size', 0)} байт</p>
            </div>
            
            <div class="info-card">
                <h3>🦠 Классификация угрозы</h3>
                <p><strong>Тип:</strong> {threat_info.get('type', 'Неизвестно')}</p>
                <p><strong>Семейство:</strong> {threat_info.get('family', 'Неизвестно')}</p>
                <p><strong>Доверие:</strong> {threat_info.get('confidence', 'Низкое')}</p>
            </div>
            
            <div class="info-card">
                <h3>⏱️ Время анализа</h3>
                <p><strong>Начало:</strong> {start_time}</p>
                <p><strong>Окончание:</strong> {end_time}</p>
                <p><strong>Длительность:</strong> {duration:.2f} сек</p>
            </div>
        </div>
        
        <h2>🎯 MITRE ATT&CK Тактики</h2>
        <div>
            {self._generate_mitre_tags(threat_info.get('mitre_tactics', []))}
        </div>
        
        <h2>🔍 Статический анализ</h2>
        {self._generate_static_section(report_data.get('static_analysis', {}))}
        
        <h2>🎬 Динамический анализ</h2>
        {self._generate_dynamic_section(report_data.get('dynamic_analysis', []))}
        
        <h2>📊 Поведение</h2>
        <div>
            {self._generate_behavior_tags(threat_info.get('behaviors_detected', []))}
        </div>
        
        <h2>💾 Извлеченные IOC</h2>
        {self._generate_ioc_section(report_data)}
        
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #666; font-size: 12px;">
            <p>Отчет сгенерирован RedSand Secure v2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>⚠️ Запускайте анализ только в изолированной виртуальной машине!</p>
        </div>
    </div>
    
    <script>
        document.querySelectorAll('.ioc-item').forEach(item => {{
            item.addEventListener('click', function() {{
                const text = this.textContent.trim();
                navigator.clipboard.writeText(text);
                alert('IOC скопирован: ' + text);
            }});
        }});
    </script>
</body>
</html>'''
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def generate_txt(self, report_data):
        """Генерация текстового отчета"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{timestamp}.txt"
        filepath = self.output_dir / filename
        
        threat_info = report_data.get('threat_classification', {})
        
        lines = [
            "=" * 70,
            "RedSand Secure v2.0 - Отчет об анализе вредоносного ПО",
            "=" * 70,
            "",
            f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "ИНФОРМАЦИЯ О ФАЙЛЕ",
            "-" * 40,
            f"Имя: {report_data.get('file', {}).get('name', 'N/A')}",
            f"Путь: {report_data.get('file', {}).get('path', 'N/A')}",
            f"Размер: {report_data.get('file', {}).get('size', 0)} байт",
            "",
            "ВЕРДИКТ",
            "-" * 40,
            f"Тип угрозы: {threat_info.get('type', 'Неизвестно')}",
            f"Семейство: {threat_info.get('family', 'Неизвестно')}",
            f"Уровень риска: {threat_info.get('risk_score', 0)}/100",
            f"Доверие: {threat_info.get('confidence', 'Низкое')}",
            "",
            "MITRE ATT&CK:",
            ", ".join(threat_info.get('mitre_tactics', ['N/A'])),
            "",
            "СТАТИЧЕСКИЙ АНАЛИЗ",
            "-" * 40,
            self._format_static_txt(report_data.get('static_analysis', {})),
            "",
            "ДИНАМИЧЕСКИЙ АНАЛИЗ",
            "-" * 40,
            self._format_dynamic_txt(report_data.get('dynamic_analysis', [])),
            "",
            "ПОВЕДЕНИЕ",
            "-" * 40,
            ", ".join(threat_info.get('behaviors_detected', ['Не обнаружено'])),
            "",
            "=" * 70,
            "Конец отчета",
            "=" * 70
        ]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return str(filepath)
    
    def _generate_mitre_tags(self, tactics):
        if not tactics:
            return '<span class="tag">Нет данных</span>'
        return ''.join(f'<span class="tag mitre-tag">{t}</span>' for t in tactics)
    
    def _generate_behavior_tags(self, behaviors):
        if not behaviors:
            return '<span class="tag">Нет данных</span>'
        return ''.join(f'<span class="tag">{b}</span>' for b in behaviors)
    
    def _generate_static_section(self, static_data):
        if not static_data:
            return '<p>Нет данных</p>'
        
        html = '<table><tr><th>Параметр</th><th>Значение</th></tr>'
        for key, value in static_data.items():
            if isinstance(value, (dict, list)):
                value = str(value)[:100] + '...' if len(str(value)) > 100 else str(value)
            html += f'<tr><td>{key}</td><td>{value}</td></tr>'
        html += '</table>'
        return html
    
    def _generate_dynamic_section(self, dynamic_data):
        if not dynamic_data:
            return '<p>Нет данных</p>'
        
        html = '<div class="timeline">'
        for event in dynamic_data[:20]:  # Первые 20 событий
            html += f'<div class="timeline-item"><strong>{event.get("type", "INFO")}</strong>: {event.get("message", "N/A")}</div>'
        html += '</div>'
        return html
    
    def _generate_ioc_section(self, report_data):
        iocs = []
        
        # Извлекаем хеши
        static = report_data.get('static_analysis', {})
        if 'hashes' in static:
            for hash_type, hash_value in static['hashes'].items():
                iocs.append(f"<div class='ioc-item'><strong>{hash_type}:</strong> {hash_value}</div>")
        
        if not iocs:
            return '<p>IOC не извлечены</p>'
        
        return '\n'.join(iocs)
    
    def _format_static_txt(self, static_data):
        if not static_data:
            return "Нет данных"
        
        lines = []
        for key, value in static_data.items():
            lines.append(f"{key}: {value}")
        return '\n'.join(lines)
    
    def _format_dynamic_txt(self, dynamic_data):
        if not dynamic_data:
            return "Нет данных"
        
        lines = []
        for event in dynamic_data[:20]:
            lines.append(f"[{event.get('type', 'INFO')}] {event.get('message', 'N/A')}")
        return '\n'.join(lines)
