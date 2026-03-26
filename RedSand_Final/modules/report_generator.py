#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Generator - Генератор отчетов
Создание подробных отчетов в форматах JSON, HTML, TXT
Интерактивный HTML с визуализацией данных
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class ReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_reports(self, analysis_results: Dict) -> Dict[str, str]:
        """Генерация всех форматов отчетов"""
        reports = {}
        
        # JSON отчет
        json_path = self._generate_json_report(analysis_results)
        reports["json"] = json_path
        
        # HTML отчет
        html_path = self._generate_html_report(analysis_results)
        reports["html"] = html_path
        
        # TXT отчет
        txt_path = self._generate_txt_report(analysis_results)
        reports["txt"] = txt_path
        
        return reports
    
    def _generate_json_report(self, results: Dict) -> str:
        """Генерация JSON отчета"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def _generate_html_report(self, results: Dict) -> str:
        """Генерация интерактивного HTML отчета"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.html"
        filepath = self.output_dir / filename
        
        verdict = results.get("verdict", "UNKNOWN")
        risk_score = results.get("risk_score", 0)
        threat_type = results.get("threat_classification", {}).get("type", "Неизвестно")
        threat_details = results.get("threat_classification", {}).get("details", {})
        mitre_techniques = threat_details.get("mitre_techniques", [])
        recommendation = results.get("threat_classification", {}).get("recommendation", "")
        
        # Определение цвета вердикта
        verdict_colors = {
            "MALICIOUS": "#dc3545",
            "SUSPICIOUS": "#ffc107",
            "SAFE": "#28a745"
        }
        verdict_color = verdict_colors.get(verdict, "#6c757d")
        
        html_content = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RedSand Secure - Отчет об анализе</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .verdict-badge {{ display: inline-block; padding: 10px 30px; border-radius: 25px; font-size: 1.5em; font-weight: bold; color: white; background: {verdict_color}; }}
        .card {{ background: white; border-radius: 10px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .card h2 {{ color: #667eea; margin-bottom: 15px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }}
        .info-item {{ background: #f8f9fa; padding: 15px; border-radius: 8px; }}
        .info-item label {{ font-weight: bold; color: #495057; display: block; margin-bottom: 5px; }}
        .info-item value {{ color: #212529; font-family: monospace; }}
        .risk-meter {{ width: 100%; height: 30px; background: #e9ecef; border-radius: 15px; overflow: hidden; margin: 10px 0; }}
        .risk-fill {{ height: 100%; background: linear-gradient(90deg, #28a745, #ffc107, #dc3545); transition: width 0.5s; }}
        .tag {{ display: inline-block; padding: 5px 12px; margin: 3px; background: #667eea; color: white; border-radius: 15px; font-size: 0.9em; }}
        .recommendation {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; }}
        .mitre-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        .mitre-table th, .mitre-table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        .mitre-table th {{ background: #667eea; color: white; }}
        .copy-btn {{ background: #667eea; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; margin-left: 10px; }}
        .copy-btn:hover {{ background: #5568d3; }}
        .hash-section {{ background: #f8f9fa; padding: 15px; border-radius: 8px; font-family: monospace; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ RedSand Secure v2.0</h1>
            <p>Отчет об анализе вредоносного ПО</p>
            <div style="margin-top: 20px;">
                <span class="verdict-badge">{verdict}</span>
            </div>
        </div>
        
        <div class="card">
            <h2>📊 Общая информация</h2>
            <div class="info-grid">
                <div class="info-item">
                    <label>Дата анализа:</label>
                    <value>{results.get('timestamp', 'N/A')}</value>
                </div>
                <div class="info-item">
                    <label>Тип угрозы:</label>
                    <value>{threat_type}</value>
                </div>
                <div class="info-item">
                    <label>Уровень риска:</label>
                    <value>{risk_score}/100</value>
                </div>
                <div class="info-item">
                    <label>Уверенность:</label>
                    <value>{results.get('threat_classification', {}).get('confidence', 'N/A')}</value>
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <label><strong>Индикатор риска:</strong></label>
                <div class="risk-meter">
                    <div class="risk-fill" style="width: {risk_score}%;"></div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🔐 Хэши файла</h2>
            <div class="hash-section">
                <p><strong>MD5:</strong> {results.get('sample', {}).get('hash', {}).get('md5', 'N/A')} <button class="copy-btn" onclick="copyToClipboard('{results.get('sample', {}).get('hash', {}).get('md5', '')}')">Копировать</button></p>
                <p><strong>SHA1:</strong> {results.get('sample', {}).get('hash', {}).get('sha1', 'N/A')} <button class="copy-btn" onclick="copyToClipboard('{results.get('sample', {}).get('hash', {}).get('sha1', '')}')">Копировать</button></p>
                <p><strong>SHA256:</strong> {results.get('sample', {}).get('hash', {}).get('sha256', 'N/A')} <button class="copy-btn" onclick="copyToClipboard('{results.get('sample', {}).get('hash', {}).get('sha256', '')}')">Копировать</button></p>
            </div>
        </div>
        
        <div class="card">
            <h2>🎯 MITRE ATT&CK Mapping</h2>
            {self._generate_mitre_table(mitre_techniques)}
        </div>
        
        <div class="card">
            <h2>⚠️ Рекомендации</h2>
            <div class="recommendation">
                <strong>Что делать:</strong>
                <p>{recommendation}</p>
            </div>
        </div>
        
        <div class="card">
            <h2>📁 Информация об образце</h2>
            <div class="info-grid">
                <div class="info-item">
                    <label>Путь к файлу:</label>
                    <value>{results.get('sample', {}).get('path', 'N/A')}</value>
                </div>
                <div class="info-item">
                    <label>Размер:</label>
                    <value>{results.get('sample', {}).get('size', 'N/A')} байт</value>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🔍 Детали обнаружения</h2>
            {self._generate_detection_details(threat_details)}
        </div>
    </div>
    
    <script>
        function copyToClipboard(text) {{
            navigator.clipboard.writeText(text).then(function() {{
                alert('Скопировано в буфер обмена!');
            }}, function(err) {{
                console.error('Ошибка копирования: ', err);
            }});
        }}
    </script>
</body>
</html>'''
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def _generate_mitre_table(self, techniques: List[str]) -> str:
        """Генерация таблицы MITRE ATT&CK"""
        if not techniques:
            return "<p>Техники MITRE ATT&CK не определены</p>"
        
        technique_names = {
            "T1486": "Data Encrypted for Impact",
            "T1490": "Inhibit System Recovery",
            "T1489": "Service Stop",
            "T1555": "Credentials from Password Stores",
            "T1503": "Credentials from Web Browsers",
            "T1539": "Steal or Forge Authentication Certificates",
            "T1496": "Resource Hijacking",
            "T1219": "Remote Access Software",
            "T1125": "Video Capture",
            "T1113": "Screen Capture",
            "T1083": "File and Directory Discovery",
            "T1091": "Replication Through Removable Media",
            "T1071": "Application Layer Protocol",
            "T1498": "Network Denial of Service",
            "T1095": "Non-Application Layer Protocol",
            "T1014": "Rootkit",
            "T1562.006": "Impair Defenses: Indicator Blocking",
            "T1056": "Input Capture",
            "T1123": "Audio Capture",
            "T1564.003": "Hide Artifacts: Hide Window",
            "T1059": "Command and Scripting Interpreter",
            "T1204": "User Execution",
            "T1204.002": "Malicious File",
            "T1056.001": "Keylogging",
            "T1571": "Non-Standard Port"
        }
        
        rows = ""
        for tech in techniques:
            name = technique_names.get(tech, "Unknown Technique")
            rows += f"<tr><td>{tech}</td><td>{name}</td></tr>"
        
        return f'''
        <table class="mitre-table">
            <thead>
                <tr>
                    <th>ID техники</th>
                    <th>Название</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        '''
    
    def _generate_detection_details(self, details: Dict) -> str:
        """Генерация деталей обнаружения"""
        if not details:
            return "<p>Детали обнаружения недоступны</p>"
        
        indicators = details.get("indicators", [])
        description = details.get("description", "")
        
        indicator_tags = "".join([f'<span class="tag">{ind}</span>' for ind in indicators])
        
        return f'''
        <div>
            <p><strong>Описание:</strong></p>
            <p>{description}</p>
            <p style="margin-top: 15px;"><strong>Индикаторы:</strong></p>
            <div>{indicator_tags}</div>
        </div>
        '''
    
    def _generate_txt_report(self, results: Dict) -> str:
        """Генерация текстового отчета"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.txt"
        filepath = self.output_dir / filename
        
        verdict = results.get("verdict", "UNKNOWN")
        risk_score = results.get("risk_score", 0)
        threat_type = results.get("threat_classification", {}).get("type", "Неизвестно")
        threat_details = results.get("threat_classification", {}).get("details", {})
        recommendation = results.get("threat_classification", {}).get("recommendation", "")
        
        report_text = f'''
================================================================================
                    REDSAND SECURE v2.0 - ОТЧЕТ ОБ АНАЛИЗЕ
================================================================================

ДАТА АНАЛИЗА: {results.get('timestamp', 'N/A')}
ВЕРДИКТ: {verdict}
УРОВЕНЬ РИСКА: {risk_score}/100
ТИП УГРОЗЫ: {threat_type}
УВЕРЕННОСТЬ: {results.get('threat_classification', {}).get('confidence', 'N/A')}

--------------------------------------------------------------------------------
                              ИНФОРМАЦИЯ ОБ ОБРАЗЦЕ
--------------------------------------------------------------------------------
Путь: {results.get('sample', {}).get('path', 'N/A')}
Размер: {results.get('sample', {}).get('size', 'N/A')} байт
MD5: {results.get('sample', {}).get('hash', {}).get('md5', 'N/A')}
SHA1: {results.get('sample', {}).get('hash', {}).get('sha1', 'N/A')}
SHA256: {results.get('sample', {}).get('hash', {}).get('sha256', 'N/A')}

--------------------------------------------------------------------------------
                              MITRE ATT&CK TECHNIQUES
--------------------------------------------------------------------------------
{chr(10).join(results.get('threat_classification', {}).get('details', {}).get('mitre_techniques', ['Не определены']))}

--------------------------------------------------------------------------------
                              РЕКОМЕНДАЦИИ
--------------------------------------------------------------------------------
{recommendation}

--------------------------------------------------------------------------------
                              ДЕТАЛИ ОБНАРУЖЕНИЯ
--------------------------------------------------------------------------------
Описание: {threat_details.get('description', 'N/A')}
Индикаторы: {', '.join(threat_details.get('indicators', []))}

================================================================================
                              КОНЕЦ ОТЧЕТА
================================================================================
'''
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        return str(filepath)
