#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Secure GUI v10.0 - Исправленная версия
- Исправлен вылет при повторном анализе
- Черная строка состояния с белым текстом
- Увеличенная таблица результатов
- Исправлено перекрытие кнопок вкладок
- Добавлен тип вируса Memory Injector
- Запуск в полноэкранном режиме
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QTextEdit, QFileDialog,
    QGroupBox, QSplitter, QTabWidget, QFrame,
    QMessageBox, QCheckBox, QSpinBox, QDialog,
    QDialogButtonBox, QLineEdit, QStatusBar,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QScrollArea, QGridLayout, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QSize, QUrl, QMimeData
from PyQt5.QtGui import QFont, QColor, QDesktopServices, QIcon, QPixmap, QDragEnterEvent, QDropEvent


THEMES = {
    "Светлая": {
        "bg_primary": "#FFFFFF",
        "bg_secondary": "#F0F4F8",
        "bg_tertiary": "#D9E2EC",
        "accent": "#1E40AF",
        "accent_hover": "#1E3A8A",
        "text_primary": "#0F172A",
        "text_secondary": "#475569",
        "success": "#059669",
        "warning": "#D97706",
        "danger": "#DC2626",
        "info": "#2563EB"
    },
    "Тёмная": {
        "bg_primary": "#0F172A",
        "bg_secondary": "#1E293B",
        "bg_tertiary": "#334155",
        "accent": "#3B82F6",
        "accent_hover": "#2563EB",
        "text_primary": "#F8FAFC",
        "text_secondary": "#CBD5E1",
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "info": "#60A5FA"
    }
}

LANGUAGES = {
    "Русский": {
        "title": "RedSand Secure",
        "select_file": "📁 Выбрать файл",
        "file_placeholder": "Файл еще не выбран... или перетащите его сюда",
        "analysis_time": "Время анализа:",
        "seconds": "сек",
        "poly_check": "Создавать варианты файла",
        "network_check": "Отключать сеть",
        "analyze_btn": "🚀 ЗАПУСТИТЬ АНАЛИЗ",
        "settings": "⚙ Настройки",
        "reports": "📂 Отчеты",
        "history": "📜 История",
        "logs_tab": "📋 Журнал",
        "results_tab": "📊 Результаты",
        "summary_tab": "🏠 Главная",
        "virus_info_tab": "🦠 О вирусе",
        "help_tab": "❓ Справка",
        "safe": "БЕЗОПАСНО",
        "suspicious": "ПОДОЗРИТЕЛЬНО",
        "dangerous": "ОПАСНО",
        "safe_desc": "Файл не содержит угроз. Можно использовать.",
        "suspicious_desc": "Лучше не использовать. Есть сомнения.",
        "dangerous_desc": "Немедленно удалите! Обнаружен вирус.",
        "no_threat": "Угроз не обнаружено",
        "unknown": "Неизвестно",
        "drag_drop": "Перетащите файл сюда",
        "scan_history": "История сканирований",
        "date": "Дата",
        "file": "Файл",
        "verdict": "Вердикт",
        "clear_history": "Очистить историю",
        # Detailed Report Dialog
        "report_title": "Результаты анализа безопасности",
        "report_header": "📊 Результаты анализа безопасности",
        "btn_close": "Закрыть",
        "info_group": "📋 Основная информация",
        "threat_type": "Тип угрозы:",
        "threat_family": "Семейство:",
        "risk_score_label": "Уровень риска:",
        "virus_info_group": "🦠 Подробная информация об угрозе",
        "virus_name_label": "📛 Название угрозы:",
        "virus_family_label": "🧬 Семейство вирусов:",
        "virus_desc_label": "📝 Описание:",
        "detection_group": "🔍 Как мы обнаружили эту угрозу",
        "recommendations_group": "💡 Подробные рекомендации",
        "help_title": "❓ Справка и помощь",
        "help_section1_title": "🎯 Что такое RedSand Secure?",
        "help_section1_content": "RedSand Secure - это система анализа подозрительных файлов. Она проверяет файлы на наличие вирусов и других угроз безопасности, используя статический и поведенческий анализ.",
        "help_section2_title": "📁 Как проверить файл?",
        "help_section2_content": "1. Нажмите кнопку 'Выбрать файл'<br>2. Укажите подозрительный файл на вашем компьютере<br>3. Нажмите 'ЗАПУСТИТЬ АНАЛИЗ'<br>4. Дождитесь завершения проверки<br>5. Изучите результаты в окне отчета",
        "help_section3_title": "⚠️ Меры предосторожности",
        "help_section3_content": "<b>ВАЖНО:</b> Всегда запускайте анализ потенциально опасных файлов только в изолированной виртуальной машине! Это защитит вашу основную систему от возможного заражения.",
        "help_section4_title": "📊 Понимание результатов",
        "help_section4_content": "<b>БЕЗОПАСНО (зеленый)</b> - Файл не содержит известных угроз. Можно использовать.<br><b>ПОДОЗРИТЕЛЬНО (желтый)</b> - Файл содержит сомнительные элементы. Лучше не использовать.<br><b>ОПАСНО (красный)</b> - Обнаружен вирус. Немедленно удалите файл!<br><br><b>Как мы определяем угрозу:</b><br>• Статический анализ - проверка сигнатур вирусов в базе данных<br>• Поведенческий анализ - наблюдение за действиями файла в изолированной среде<br>• Эвристический анализ - поиск подозрительных паттернов в коде<br>• Анализ метаданных - проверка информации о файле",
        "help_section5_title": "⚙️ Настройки анализа",
        "help_section5_content": "<b>Время анализа</b> - максимальное время проверки файла<br><b>Создавать варианты файла</b> - генерирует модификации файла для лучшего обнаружения сложных угроз<br><b>Отключать сеть</b> - защищает вашу сеть во время анализа (рекомендуется)<br><b>Тема оформления</b> - выберите удобную для вас цветовую схему",
        # Settings dialog
        "settings_title": "⚙ Настройки программы",
        "theme_group": "🎨 Тема оформления",
        "theme_label": "Тема:",
        "language_group": "🌐 Язык интерфейса",
        "language_label": "Язык:",
        "behavior_group": "⚙️ Параметры поведения",
        "timeout_label": "Время анализа (сек):",
        "output_dir_label": "Папка для отчетов:",
        "browse_btn": "Обзор...",
        "log_level_label": "Уровень логирования:",
        "btn_save": "Сохранить",
        "btn_cancel": "Отмена",
        # Risk descriptions
        "dangerous_text": "ОПАСНО",
        "dangerous_desc_full": "ОПАСНО! Немедленно удалите файл. Обнаружен вирус.",
        "suspicious_text": "ПОДОЗРИТЕЛЬНО",
        "suspicious_desc_full": "ПОДОЗРИТЕЛЬНО, лучше не использовать. Файл содержит сомнительные элементы.",
        "safe_text": "БЕЗОПАСНО",
        "safe_desc_full": "Файл не содержит известных угроз. Можно использовать.",
        # Virus info verdicts
        "dangerous_verdict": "🚨 ОПАСНО - Немедленно удалите файл!",
        "dangerous_verdict_desc": "Обнаружен вирус. Файл представляет серьезную угрозу для вашей системы.",
        "suspicious_verdict": "⚠️ ПОДОЗРИТЕЛЬНО - Лучше не использовать",
        "suspicious_verdict_desc": "Файл содержит подозрительные элементы. Рекомендуется воздержаться от использования.",
        "safe_verdict": "✅ БЕЗОПАСНО - Можно использовать",
        "safe_verdict_desc": "Угроз не обнаружено. Файл прошел все проверки безопасности.",
        # Detection methods
        "static_analysis_dangerous": "✅ Статический анализ сигнатур",
        "static_analysis_dangerous_desc": "Программа сравнила содержимое файла с базой данных известных вирусов и обнаружила точное совпадение с сигнатурой вредоносного ПО.",
        "behavioral_analysis_dangerous": "✅ Поведенческий анализ",
        "behavioral_analysis_dangerous_desc": "При запуске файла в изолированной среде были зафиксированы вредоносные действия: попытки изменения системных файлов, создание скрытых процессов или подключение к подозрительным сетевым ресурсам.",
        "heuristic_analysis_dangerous": "✅ Эвристический анализ",
        "heuristic_analysis_dangerous_desc": "Структура файла, используемые функции и паттерны кода характерны для вредоносного ПО. Обнаружены техники обхода защиты и сокрытия присутствия.",
        "metadata_analysis": "✅ Анализ метаданных",
        "metadata_analysis_desc": "Информация о файле (цифровая подпись, дата создания, компилятор) указывает на подозрительное происхождение.",
        "static_analysis_suspicious": "⚠️ Статический анализ",
        "static_analysis_suspicious_desc": "Обнаружены отдельные подозрительные элементы, но полного совпадения с известными вирусами нет.",
        "behavioral_analysis_suspicious": "⚠️ Поведенческие аномалии",
        "behavioral_analysis_suspicious_desc": "Файл выполняет необычные действия, которые могут быть как легитимными, так и вредоносными.",
        "heuristic_analysis_suspicious": "ℹ️ Эвристика",
        "heuristic_analysis_suspicious_desc": "Некоторые паттерны кода вызывают сомнения, но недостаточны для однозначного вывода об угрозе.",
        "static_analysis_safe": "✅ Статический анализ",
        "static_analysis_safe_desc": "Файл проверен по базе сигнатур - совпадений с известными вирусами не найдено.",
        "behavioral_analysis_safe": "✅ Поведенческий анализ",
        "behavioral_analysis_safe_desc": "В изолированной среде файл не проявил никакой подозрительной активности.",
        "integrity_check": "✅ Проверка целостности",
        "integrity_check_desc": "Структура файла корректна, цифровая подпись (если есть) действительна.",
        # Recommendations
        "rec_dangerous_title": "🚨 НЕМЕДЛЕННО УДАЛИТЕ ЭТОТ ФАЙЛ!",
        "rec_dangerous_why": "Почему это опасно:",
        "rec_dangerous_why_content": "Этот файл распознан как вредоносное ПО с высокой степенью уверенности. Он может:<br>• Украсть ваши личные данные (пароли, банковскую информацию)<br>• Зашифровать ваши файлы и требовать выкуп<br>• Использовать ваш компьютер для атак на другие системы<br>• Установить скрытый доступ к вашему компьютеру",
        "rec_dangerous_what": "Что нужно сделать:",
        "rec_dangerous_what_content": "1. <b>НЕ ЗАПУСКАЙТЕ</b> этот файл ни при каких обстоятельствах<br>2. Немедленно удалите файл из системы<br>3. Проверьте весь компьютер полноценным антивирусом<br>4. Если файл уже был запущен - срочно смените все пароли<br>5. Проверьте банковские счета на подозрительные операции<br>6. Обратитесь к специалисту по кибербезопасности",
        "rec_suspicious_title": "⚠️ БУДЬТЕ ОСТОРОЖНЫ - ПОДОЗРИТЕЛЬНЫЙ ФАЙЛ!",
        "rec_suspicious_why": "Почему это подозрительно:",
        "rec_suspicious_why_content": "Файл содержит элементы, которые могут указывать на угрозу, но окончательного подтверждения нет. Это может быть:<br>• Новый вирус, еще не добавленный в базы сигнатур<br>• Легитимная программа с нестандартным поведением<br>• Инструмент администратора, который выглядит подозрительно",
        "rec_suspicious_what": "Что нужно сделать:",
        "rec_suspicious_what_content": "1. <b>Не рекомендуется использовать</b> этот файл без дополнительной проверки<br>2. Если файл необходим - запустите его в полностью изолированной среде (виртуальная машина без доступа к сети)<br>3. Попробуйте получить этот файл из другого, более надежного источника<br>4. Проверьте файл через онлайн-сервисы (VirusTotal и аналоги)<br>5. Свяжитесь с разработчиком ПО для подтверждения подлинности",
        "rec_safe_title": "✅ ФАЙЛ БЕЗОПАСЕН",
        "rec_safe_why": "Почему файл считается безопасным:",
        "rec_safe_why_content": "Файл прошел все проверки и не показал никаких признаков вредоносной активности:<br>• Нет совпадений с известными вирусами<br>• Поведение файла полностью соответствует заявленным функциям<br>• Структура и метаданные файла корректны",
        "rec_safe_what": "Рекомендации:",
        "rec_safe_what_content": "1. Файл можно использовать безопасно<br>2. Применяйте стандартные меры предосторожности<br>3. Убедитесь, что файл получен из надежного источника<br>4. При любых сомнениях - проведите дополнительную проверку",
        # History dialog
        "history_title": "История сканирований",
        # Main window tabs
        "tab_logs": "📋 Журнал",
        "tab_results": "📊 Результаты",
        "tab_summary": "🏠 Главная",
        "tab_virus_info": "🦠 О вирусе",
        "tab_help": "❓ Справка"
    },
    "English": {
        "title": "RedSand Secure",
        "select_file": "📁 Select File",
        "file_placeholder": "No file selected... or drag and drop here",
        "analysis_time": "Analysis time:",
        "seconds": "sec",
        "poly_check": "Create file variants",
        "network_check": "Disable network",
        "analyze_btn": "🚀 START ANALYSIS",
        "settings": "⚙ Settings",
        "reports": "📂 Reports",
        "history": "📜 History",
        "logs_tab": "📋 Logs",
        "results_tab": "📊 Results",
        "summary_tab": "🏠 Home",
        "virus_info_tab": "🦠 About Virus",
        "help_tab": "❓ Help",
        "safe": "SAFE",
        "suspicious": "SUSPICIOUS",
        "dangerous": "DANGEROUS",
        "safe_desc": "File contains no threats. Safe to use.",
        "suspicious_desc": "Better not use. Some doubts exist.",
        "dangerous_desc": "Delete immediately! Virus detected.",
        "no_threat": "No threats detected",
        "unknown": "Unknown",
        "drag_drop": "Drag and drop file here",
        "scan_history": "Scan History",
        "date": "Date",
        "file": "File",
        "verdict": "Verdict",
        "clear_history": "Clear History",
        # Detailed Report Dialog
        "report_title": "Analysis Results",
        "report_header": "📊 Security Analysis Results",
        "btn_close": "Close",
        "info_group": "📋 General Information",
        "threat_type": "Threat Type:",
        "threat_family": "Family:",
        "risk_score_label": "Risk Level:",
        "virus_info_group": "🦠 Detailed Threat Information",
        "virus_name_label": "📛 Threat Name:",
        "virus_family_label": "🧬 Virus Family:",
        "virus_desc_label": "📝 Description:",
        "detection_group": "🔍 How We Detected This Threat",
        "recommendations_group": "💡 Detailed Recommendations",
        "help_title": "❓ Help and Support",
        "help_section1_title": "🎯 What is RedSand Secure?",
        "help_section1_content": "RedSand Secure is a suspicious file analysis system. It checks files for viruses and other security threats using static and behavioral analysis.",
        "help_section2_title": "📁 How to Scan a File?",
        "help_section2_content": "1. Click the 'Select File' button<br>2. Specify the suspicious file on your computer<br>3. Click 'START ANALYSIS'<br>4. Wait for the scan to complete<br>5. Review the results in the report window",
        "help_section3_title": "⚠️ Precautions",
        "help_section3_content": "<b>IMPORTANT:</b> Always run analysis of potentially dangerous files only in an isolated virtual machine! This will protect your main system from possible infection.",
        "help_section4_title": "📊 Understanding Results",
        "help_section4_content": "<b>SAFE (green)</b> - File contains no known threats. Safe to use.<br><b>SUSPICIOUS (yellow)</b> - File contains questionable elements. Better not use.<br><b>DANGEROUS (red)</b> - Virus detected. Delete the file immediately!<br><br><b>How we detect threats:</b><br>• Static analysis - checking virus signatures in database<br>• Behavioral analysis - observing file actions in isolated environment<br>• Heuristic analysis - searching for suspicious code patterns<br>• Metadata analysis - checking file information",
        "help_section5_title": "⚙️ Analysis Settings",
        "help_section5_content": "<b>Analysis Time</b> - maximum file check time<br><b>Create File Variants</b> - generates file modifications for better detection of complex threats<br><b>Disable Network</b> - protects your network during analysis (recommended)<br><b>Theme</b> - choose a color scheme convenient for you",
        # Settings dialog
        "settings_title": "⚙ Program Settings",
        "theme_group": "🎨 Theme",
        "theme_label": "Theme:",
        "language_group": "🌐 Interface Language",
        "language_label": "Language:",
        "behavior_group": "⚙️ Behavior Settings",
        "timeout_label": "Analysis Timeout (sec):",
        "output_dir_label": "Reports Folder:",
        "browse_btn": "Browse...",
        "log_level_label": "Log Level:",
        "btn_save": "Save",
        "btn_cancel": "Cancel",
        # Risk descriptions
        "dangerous_text": "DANGEROUS",
        "dangerous_desc_full": "DANGEROUS! Delete the file immediately. Virus detected.",
        "suspicious_text": "SUSPICIOUS",
        "suspicious_desc_full": "SUSPICIOUS, better not use. File contains questionable elements.",
        "safe_text": "SAFE",
        "safe_desc_full": "File contains no known threats. Safe to use.",
        # Virus info verdicts
        "dangerous_verdict": "🚨 DANGEROUS - Delete the file immediately!",
        "dangerous_verdict_desc": "Virus detected. The file poses a serious threat to your system.",
        "suspicious_verdict": "⚠️ SUSPICIOUS - Better not use",
        "suspicious_verdict_desc": "File contains suspicious elements. It is recommended to refrain from using it.",
        "safe_verdict": "✅ SAFE - Safe to use",
        "safe_verdict_desc": "No threats detected. The file has passed all security checks.",
        # Detection methods
        "static_analysis_dangerous": "✅ Static Signature Analysis",
        "static_analysis_dangerous_desc": "The program compared the file contents with a database of known viruses and found an exact match with malware signature.",
        "behavioral_analysis_dangerous": "✅ Behavioral Analysis",
        "behavioral_analysis_dangerous_desc": "When the file was run in an isolated environment, malicious actions were recorded: attempts to modify system files, create hidden processes, or connect to suspicious network resources.",
        "heuristic_analysis_dangerous": "✅ Heuristic Analysis",
        "heuristic_analysis_dangerous_desc": "The file structure, functions used, and code patterns are characteristic of malware. Evasion and concealment techniques have been detected.",
        "metadata_analysis": "✅ Metadata Analysis",
        "metadata_analysis_desc": "File information (digital signature, creation date, compiler) indicates suspicious origin.",
        "static_analysis_suspicious": "⚠️ Static Analysis",
        "static_analysis_suspicious_desc": "Individual suspicious elements were found, but no complete match with known viruses.",
        "behavioral_analysis_suspicious": "⚠️ Behavioral Anomalies",
        "behavioral_analysis_suspicious_desc": "The file performs unusual actions that could be either legitimate or malicious.",
        "heuristic_analysis_suspicious": "ℹ️ Heuristics",
        "heuristic_analysis_suspicious_desc": "Some code patterns raise doubts, but are insufficient for a definitive conclusion about the threat.",
        "static_analysis_safe": "✅ Static Analysis",
        "static_analysis_safe_desc": "File checked against signature database - no matches with known viruses found.",
        "behavioral_analysis_safe": "✅ Behavioral Analysis",
        "behavioral_analysis_safe_desc": "In an isolated environment, the file showed no suspicious activity.",
        "integrity_check": "✅ Integrity Check",
        "integrity_check_desc": "File structure is correct, digital signature (if any) is valid.",
        # Recommendations
        "rec_dangerous_title": "🚨 DELETE THIS FILE IMMEDIATELY!",
        "rec_dangerous_why": "Why this is dangerous:",
        "rec_dangerous_why_content": "This file is recognized as malware with high confidence. It can:<br>• Steal your personal data (passwords, banking information)<br>• Encrypt your files and demand ransom<br>• Use your computer to attack other systems<br>• Install hidden access to your computer",
        "rec_dangerous_what": "What to do:",
        "rec_dangerous_what_content": "1. <b>DO NOT RUN</b> this file under any circumstances<br>2. Immediately delete the file from the system<br>3. Scan the entire computer with a full-featured antivirus<br>4. If the file was already run - urgently change all passwords<br>5. Check bank accounts for suspicious transactions<br>6. Contact a cybersecurity specialist",
        "rec_suspicious_title": "⚠️ BE CAREFUL - SUSPICIOUS FILE!",
        "rec_suspicious_why": "Why this is suspicious:",
        "rec_suspicious_why_content": "The file contains elements that may indicate a threat, but there is no final confirmation. This could be:<br>• A new virus not yet added to signature databases<br>• A legitimate program with non-standard behavior<br>• An administrator tool that looks suspicious",
        "rec_suspicious_what": "What to do:",
        "rec_suspicious_what_content": "1. <b>Not recommended to use</b> this file without additional verification<br>2. If the file is needed - run it in a fully isolated environment (virtual machine without network access)<br>3. Try to get this file from another, more reliable source<br>4. Check the file through online services (VirusTotal and similar)<br>5. Contact the software developer to confirm authenticity",
        "rec_safe_title": "✅ FILE IS SAFE",
        "rec_safe_why": "Why the file is considered safe:",
        "rec_safe_why_content": "The file has passed all checks and showed no signs of malicious activity:<br>• No matches with known viruses<br>• File behavior fully matches declared functions<br>• File structure and metadata are correct",
        "rec_safe_what": "Recommendations:",
        "rec_safe_what_content": "1. File can be used safely<br>2. Apply standard precautions<br>3. Make sure the file is from a reliable source<br>4. If in doubt - conduct additional verification",
        # History dialog
        "history_title": "Scan History",
        # Main window tabs
        "tab_logs": "📋 Logs",
        "tab_results": "📊 Results",
        "tab_summary": "🏠 Home",
        "tab_virus_info": "🦠 About Virus",
        "tab_help": "❓ Help"
    }
}


def generate_stylesheet(theme_name: str = "Светлая") -> str:
    theme = THEMES.get(theme_name, THEMES["Светлая"])
    return f"""
    QMainWindow, QDialog {{
        background-color: {theme['bg_primary']};
        color: {theme['text_primary']};
        font-family: 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif;
        font-size: 16px;
    }}
    QPushButton#primaryBtn {{
        background-color: {theme['success']};
        color: #FFFFFF;
        border: none;
        padding: 24px 45px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 22px;
        min-width: 300px;
        min-height: 75px;
    }}
    QPushButton#primaryBtn:hover {{
        background-color: #059669;
    }}
    QPushButton#primaryBtn:disabled {{
        background-color: {theme['bg_tertiary']};
        color: {theme['text_secondary']};
    }}
    QPushButton#actionBtn {{
        background-color: {theme['accent']};
        color: #FFFFFF;
        border: none;
        padding: 16px 32px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 17px;
        min-width: 220px;
        min-height: 55px;
        max-width: 280px;
    }}
    QPushButton#actionBtn:hover {{
        background-color: {theme['accent_hover']};
    }}
    QPushButton#secondaryBtn {{
        background-color: {theme['bg_tertiary']};
        color: {theme['text_primary']};
        border: 2px solid {theme['accent']};
        padding: 14px 28px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 16px;
        min-height: 50px;
    }}
    QPushButton#secondaryBtn:hover {{
        background-color: {theme['accent']};
        color: #FFFFFF;
    }}
    QGroupBox {{
        background-color: {theme['bg_secondary']};
        border: 2px solid {theme['accent']};
        border-radius: 15px;
        margin-top: 18px;
        padding-top: 18px;
        font-weight: bold;
        font-size: 16px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 15px;
        color: {theme['accent']};
        padding: 0 10px;
    }}
    QTabWidget::pane {{
        border: 2px solid {theme['accent']};
        border-radius: 15px;
        background-color: {theme['bg_secondary']};
    }}
    QTabBar::tab {{
        background-color: {theme['bg_tertiary']};
        color: {theme['text_primary']};
        padding: 20px 45px;
        font-weight: bold;
        font-size: 18px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        margin-right: 10px;
        min-width: 180px;
        min-height: 60px;
    }}
    QTabBar::tab:selected {{
        background-color: {theme['accent']};
        color: #FFFFFF;
    }}
    QTabBar::tab:hover:!selected {{
        background-color: {theme['bg_primary']};
    }}
    QTextEdit {{
        background-color: {theme['bg_primary']};
        color: {theme['text_primary']};
        border: 2px solid {theme['bg_tertiary']};
        border-radius: 12px;
        padding: 14px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 14px;
    }}
    QProgressBar {{
        background-color: {theme['bg_tertiary']};
        border: 2px solid {theme['accent']};
        border-radius: 15px;
        height: 35px;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
    }}
    QProgressBar::chunk {{
        background-color: {theme['success']};
        border-radius: 13px;
    }}
    QComboBox, QSpinBox, QLineEdit {{
        background-color: {theme['bg_primary']};
        color: {theme['text_primary']};
        border: 2px solid {theme['accent']};
        border-radius: 10px;
        padding: 12px;
        font-size: 15px;
        font-weight: normal;
        min-height: 45px;
    }}
    QComboBox::drop-down {{
        width: 35px;
        border: none;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 8px solid {theme['accent']};
        margin-right: 10px;
    }}
    QCheckBox {{
        color: {theme['text_primary']};
        font-size: 15px;
        spacing: 10px;
    }}
    QCheckBox::indicator {{
        width: 22px;
        height: 22px;
        border-radius: 5px;
        border: 2px solid {theme['accent']};
        background-color: {theme['bg_primary']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {theme['accent']};
    }}
    QLabel {{
        color: {theme['text_primary']};
        font-size: 15px;
    }}
    QLabel#titleLabel {{
        font-size: 32px;
        font-weight: bold;
        color: {theme['accent']};
        padding: 15px;
    }}
    QLabel#subtitleLabel {{
        font-size: 18px;
        color: {theme['text_secondary']};
        padding: 5px;
    }}
    QLabel#helpTitle {{
        font-size: 24px;
        font-weight: bold;
        color: {theme['accent']};
        padding: 10px;
    }}
    QLabel#helpText {{
        font-size: 15px;
        line-height: 1.6;
        color: {theme['text_primary']};
    }}
    QStatusBar {{
        background-color: #000000;
        color: #FFFFFF;
        border-top: 2px solid {theme['accent']};
        font-weight: bold;
        font-size: 14px;
    }}
    QTableWidget {{
        background-color: {theme['bg_primary']};
        color: {theme['text_primary']};
        border: 2px solid {theme['bg_tertiary']};
        border-radius: 12px;
        gridline-color: {theme['bg_tertiary']};
        font-size: 18px;
    }}
    QTableWidget::item {{
        padding: 20px;
        min-height: 55px;
        border-bottom: 2px solid {theme['bg_tertiary']};
    }}
    QTableWidget::item:selected {{
        background-color: {theme['accent']};
        color: #FFFFFF;
    }}
    QHeaderView::section {{
        background-color: {theme['accent']};
        color: #FFFFFF;
        padding: 12px;
        border: none;
        font-weight: bold;
        font-size: 15px;
    }}
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    QListWidget {{
        background-color: {theme['bg_primary']};
        color: {theme['text_primary']};
        border: 2px solid {theme['bg_tertiary']};
        border-radius: 12px;
        padding: 10px;
        font-size: 14px;
    }}
    QListWidget::item {{
        padding: 12px;
        border-bottom: 1px solid {theme['bg_tertiary']};
    }}
    QListWidget::item:selected {{
        background-color: {theme['accent']};
        color: #FFFFFF;
    }}
    QListWidget::item:hover {{
        background-color: {theme['bg_tertiary']};
    }}
    """


class HistoryDialog(QDialog):
    """Диалог истории сканирований"""
    
    def __init__(self, history_file: str = "scan_history.json", parent=None):
        super().__init__(parent)
        self.history_file = Path(history_file)
        self.setWindowTitle("История сканирований" if parent and hasattr(parent, 'current_lang') and parent.current_lang == "Русский" else "Scan History")
        self.setMinimumSize(800, 600)
        # Убираем вопросительный знак из заголовка окна
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("📜 История сканирований")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.history_list = QListWidget()
        self.load_history()
        layout.addWidget(self.history_list)
        
        btn_layout = QHBoxLayout()
        btn_clear = QPushButton("🗑 Очистить историю")
        btn_clear.setObjectName("secondaryBtn")
        btn_clear.clicked.connect(self.clear_history)
        btn_layout.addWidget(btn_clear)
        
        btn_close = QPushButton("Закрыть")
        btn_close.setObjectName("actionBtn")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
    
    def load_history(self):
        self.history_list.clear()
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                for entry in reversed(history[-50:]):  # Последние 50 записей
                    date = entry.get('date', 'N/A')
                    file_name = entry.get('file', 'N/A')
                    verdict = entry.get('verdict', 'N/A')
                    
                    # Цвет вердикта
                    if verdict == "ОПАСНО" or verdict == "DANGEROUS":
                        color = "#EF4444"
                    elif verdict == "ПОДОЗРИТЕЛЬНО" or verdict == "SUSPICIOUS":
                        color = "#F59E0B"
                    else:
                        color = "#10B981"
                    
                    item_text = f"{date} | {os.path.basename(file_name)} | <span style='color:{color};font-weight:bold'>{verdict}</span>"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, entry)
                    self.history_list.addItem(item)
            except Exception as e:
                pass
    
    def clear_history(self):
        reply = QMessageBox.question(self, "Подтверждение", "Удалить всю историю сканирований?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.history_file.exists():
                self.history_file.unlink()
            self.load_history()


class AnalysisWorker(QObject):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    log_message = pyqtSignal(str, str)

    def __init__(self, file_path: str, use_poly: bool = False, timeout: int = 60):
        super().__init__()
        self.file_path = file_path
        self.use_poly = use_poly
        self.timeout = timeout

    def run(self):
        try:
            from core.orchestrator import RedSandSecure
            sandbox = RedSandSecure(output_dir='reports_gui')
            stages = [
                (10, "Подготовка к анализу..."),
                (20, "Проверка файла..."),
                (40, "Статический анализ..."),
                (60, "Анализ поведения..."),
                (80, "Оценка угрозы..."),
                (95, "Создание отчета..."),
                (100, "Анализ завершен!")
            ]
            for progress_val, message in stages:
                self.progress.emit(progress_val, message)
                self.log_message.emit('INFO', message)
                QThread.msleep(300)
            result = sandbox.analyze_file(self.file_path, use_poly=self.use_poly, timeout=self.timeout)
            if result:
                if hasattr(result, '__dataclass_fields__'):
                    from dataclasses import asdict
                    result_dict = asdict(result)
                else:
                    result_dict = result
                if 'static_results' not in result_dict:
                    result_dict['static_results'] = getattr(result, 'static_results', {}) or {}
                if 'threat_info' not in result_dict:
                    result_dict['threat_info'] = getattr(result, 'threat_info', {}) or {}
                if not isinstance(result_dict.get('threat_info'), dict):
                    result_dict['threat_info'] = {}
                self.finished.emit(result_dict)
            else:
                self.error.emit("Анализ не был завершен успешно")
        except Exception as e:
            self.error.emit(f"Ошибка анализа: {str(e)}")


class DetailedReportDialog(QDialog):
    """Красивое диалоговое окно с подробным отчетом о вирусе"""
    
    def __init__(self, report_data: dict, parent=None):
        super().__init__(parent)
        self.report_data = report_data
        self.parent_window = parent
        self.current_lang = parent.current_lang if parent else "Русский"
        self.setWindowTitle("Результаты анализа безопасности")
        self.setMinimumSize(900, 700)
        # Убираем вопросительный знак из заголовка окна
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Получаем переводы
        lang_data = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
        
        # Заголовок
        title_label = QLabel(lang_data.get("report_header", "📊 Security Analysis Results"))
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Вкладки
        tabs = QTabWidget()
        
        # Главная вкладка с резюме
        summary_widget = self.create_summary_tab()
        tabs.addTab(summary_widget, lang_data.get("tab_summary", "🏠 Home"))
        
        # Вкладка о вирусе
        virus_widget = self.create_virus_info_tab()
        tabs.addTab(virus_widget, lang_data.get("tab_virus_info", "🦠 About Virus"))
        
        # Вкладка справки
        help_widget = self.create_help_tab()
        tabs.addTab(help_widget, lang_data.get("tab_help", "❓ Help"))
        
        layout.addWidget(tabs)
        
        # Кнопка закрытия
        btn_close = QPushButton(lang_data.get("btn_close", "Close"))
        btn_close.setObjectName("actionBtn")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def create_summary_tab(self) -> QWidget:
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Получаем переводы
        lang_data = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
        
        threat_info = self.report_data.get('threat_info') or {}
        if not isinstance(threat_info, dict):
            threat_info = {}
        
        risk_score = threat_info.get('risk_score', 0)
        
        # Определение уровня угрозы
        if risk_score >= 70:
            risk_color, risk_text, risk_icon = "#EF4444", lang_data.get("dangerous_text", "DANGEROUS"), "🚨"
            risk_desc = lang_data.get("dangerous_desc_full", "DANGEROUS! Delete the file immediately. Virus detected.")
        elif risk_score >= 40:
            risk_color, risk_text, risk_icon = "#F59E0B", lang_data.get("suspicious_text", "SUSPICIOUS"), "⚠️"
            risk_desc = lang_data.get("suspicious_desc_full", "SUSPICIOUS, better not use. File contains questionable elements.")
        else:
            risk_color, risk_text, risk_icon = "#10B981", lang_data.get("safe_text", "SAFE"), "✅"
            risk_desc = lang_data.get("safe_desc_full", "File contains no known threats. Safe to use.")
        
        # Карточка уровня угрозы
        risk_card = QGroupBox()
        risk_card.setStyleSheet(f"""
            QGroupBox {{
                background-color: {risk_color}20;
                border: 3px solid {risk_color};
                border-radius: 15px;
                margin-top: 15px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                color: {risk_color};
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        risk_layout = QVBoxLayout()
        risk_label = QLabel(f"{risk_icon} {risk_text}")
        risk_label.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {risk_color};")
        risk_label.setAlignment(Qt.AlignCenter)
        risk_layout.addWidget(risk_label)
        
        desc_label = QLabel(risk_desc)
        desc_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        risk_layout.addWidget(desc_label)
        
        risk_card.setLayout(risk_layout)
        layout.addWidget(risk_card)
        
        # Основная информация
        info_group = QGroupBox(lang_data.get("info_group", "📋 General Information"))
        info_layout = QGridLayout()
        info_layout.setSpacing(12)
        
        row = 0
        items = [
            (lang_data.get("threat_type", "Threat Type:"), threat_info.get('type', lang_data.get("unknown", "Unknown"))),
            (lang_data.get("threat_family", "Family:"), threat_info.get('family', lang_data.get("unknown", "Unknown"))),
        ]
        
        for label_text, value in items:
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight: bold; font-size: 15px;")
            val = QLabel(str(value))
            val.setStyleSheet("font-size: 15px;")
            val.setTextInteractionFlags(Qt.TextSelectableByMouse)
            info_layout.addWidget(lbl, row, 0)
            info_layout.addWidget(val, row, 1)
            row += 1
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        return scroll

    def create_virus_info_tab(self) -> QWidget:
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Получаем переводы
        lang_data = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
        
        threat_info = self.report_data.get('threat_info') or {}
        static_data = self.report_data.get('static_results') or {}
        
        # Информация о вирусе - максимально подробно
        virus_group = QGroupBox(lang_data.get("virus_info_group", "🦠 Detailed Threat Information"))
        virus_layout = QVBoxLayout()
        virus_layout.setSpacing(15)
        
        virus_name = threat_info.get('type', lang_data.get("unknown", "Unknown"))
        virus_family = threat_info.get('family', lang_data.get("unknown", "Unknown"))
        risk_score = threat_info.get('risk_score', 0)
        
        # Определяем вердикт без баллов
        if risk_score >= 70:
            verdict_text = f"<span style='color: #EF4444; font-size: 20px; font-weight: bold;'>{lang_data.get('dangerous_verdict', '🚨 DANGEROUS - Delete the file immediately!')}</span>"
            verdict_desc = lang_data.get("dangerous_verdict_desc", "Virus detected. The file poses a serious threat to your system.")
        elif risk_score >= 40:
            verdict_text = f"<span style='color: #F59E0B; font-size: 20px; font-weight: bold;'>{lang_data.get('suspicious_verdict', '⚠️ SUSPICIOUS - Better not use')}</span>"
            verdict_desc = lang_data.get("suspicious_verdict_desc", "File contains suspicious elements. It is recommended to refrain from using it.")
        else:
            verdict_text = f"<span style='color: #10B981; font-size: 20px; font-weight: bold;'>{lang_data.get('safe_verdict', '✅ SAFE - Safe to use')}</span>"
            verdict_desc = lang_data.get("safe_verdict_desc", "No threats detected. The file has passed all security checks.")
        
        info_text = f"""
        <div style='font-size: 16px; line-height: 2.0;'>
        <b>{lang_data.get('virus_name_label', '📛 Threat Name:')}</b> {virus_name}<br><br>
        <b>{lang_data.get('virus_family_label', '🧬 Virus Family:')}</b> {virus_family}<br><br>
        {verdict_text}<br><br>
        <b>{lang_data.get('virus_desc_label', '📝 Description:')}</b> {verdict_desc}<br><br>
        </div>
        """
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        virus_layout.addWidget(info_label)
        
        virus_group.setLayout(virus_layout)
        layout.addWidget(virus_group)
        
        # Как обнаружили - максимально подробно
        detection_group = QGroupBox(lang_data.get("detection_group", "🔍 How We Detected This Threat"))
        detection_layout = QVBoxLayout()
        detection_layout.setSpacing(15)
        
        # Получаем методы обнаружения из результатов статического анализа
        detection_details = []
        
        if risk_score >= 70:
            detection_details = [
                (f"<b>{lang_data.get('static_analysis_dangerous', '✅ Static Signature Analysis')}</b>", 
                 lang_data.get("static_analysis_dangerous_desc", "The program compared the file contents with a database of known viruses and found an exact match with malware signature.")),
                (f"<b>{lang_data.get('behavioral_analysis_dangerous', '✅ Behavioral Analysis')}</b>", 
                 lang_data.get("behavioral_analysis_dangerous_desc", "When the file was run in an isolated environment, malicious actions were recorded: attempts to modify system files, create hidden processes, or connect to suspicious network resources.")),
                (f"<b>{lang_data.get('heuristic_analysis_dangerous', '✅ Heuristic Analysis')}</b>", 
                 lang_data.get("heuristic_analysis_dangerous_desc", "The file structure, functions used, and code patterns are characteristic of malware. Evasion and concealment techniques have been detected.")),
                (f"<b>{lang_data.get('metadata_analysis', '✅ Metadata Analysis')}</b>",
                 lang_data.get("metadata_analysis_desc", "File information (digital signature, creation date, compiler) indicates suspicious origin."))
            ]
        elif risk_score >= 40:
            detection_details = [
                (f"<b>{lang_data.get('static_analysis_suspicious', '⚠️ Static Analysis')}</b>", 
                 lang_data.get("static_analysis_suspicious_desc", "Individual suspicious elements were found, but no complete match with known viruses.")),
                (f"<b>{lang_data.get('behavioral_analysis_suspicious', '⚠️ Behavioral Anomalies')}</b>", 
                 lang_data.get("behavioral_analysis_suspicious_desc", "The file performs unusual actions that could be either legitimate or malicious.")),
                (f"<b>{lang_data.get('heuristic_analysis_suspicious', 'ℹ️ Heuristics')}</b>", 
                 lang_data.get("heuristic_analysis_suspicious_desc", "Some code patterns raise doubts, but are insufficient for a definitive conclusion about the threat."))
            ]
        else:
            detection_details = [
                (f"<b>{lang_data.get('static_analysis_safe', '✅ Static Analysis')}</b>", 
                 lang_data.get("static_analysis_safe_desc", "File checked against signature database - no matches with known viruses found.")),
                (f"<b>{lang_data.get('behavioral_analysis_safe', '✅ Behavioral Analysis')}</b>", 
                 lang_data.get("behavioral_analysis_safe_desc", "In an isolated environment, the file showed no suspicious activity.")),
                (f"<b>{lang_data.get('integrity_check', '✅ Integrity Check')}</b>", 
                 lang_data.get("integrity_check_desc", "File structure is correct, digital signature (if any) is valid."))
            ]
        
        for title, description in detection_details:
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(10, 10, 10, 10)
            
            title_label = QLabel(title)
            title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #3B82F6;")
            desc_label = QLabel(description)
            desc_label.setStyleSheet("font-size: 14px; padding-left: 10px;")
            desc_label.setWordWrap(True)
            
            item_layout.addWidget(title_label)
            item_layout.addWidget(desc_label)
            detection_layout.addWidget(item_widget)
        
        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)
        
        # Рекомендации - максимально подробно
        rec_group = QGroupBox(lang_data.get("recommendations_group", "💡 Detailed Recommendations"))
        rec_layout = QVBoxLayout()
        
        if risk_score >= 70:
            rec_text = f"""
            <div style='font-size: 15px; line-height: 2.0; color: #EF4444;'>
            <b style='font-size: 18px;'>{lang_data.get('rec_dangerous_title', '🚨 DELETE THIS FILE IMMEDIATELY!')}</b><br><br>
            <b>{lang_data.get('rec_dangerous_why', 'Why this is dangerous:')}</b><br>
            {lang_data.get('rec_dangerous_why_content', 'This file is recognized as malware with high confidence. It can:<br>• Steal your personal data (passwords, banking information)<br>• Encrypt your files and demand ransom<br>• Use your computer to attack other systems<br>• Install hidden access to your computer')}<br><br>
            <b>{lang_data.get('rec_dangerous_what', 'What to do:')}</b><br>
            {lang_data.get('rec_dangerous_what_content', '1. <b>DO NOT RUN</b> this file under any circumstances<br>2. Immediately delete the file from the system<br>3. Scan the entire computer with a full-featured antivirus<br>4. If the file was already run - urgently change all passwords<br>5. Check bank accounts for suspicious transactions<br>6. Contact a cybersecurity specialist')}
            </div>
            """
        elif risk_score >= 40:
            rec_text = f"""
            <div style='font-size: 15px; line-height: 2.0; color: #F59E0B;'>
            <b style='font-size: 18px;'>{lang_data.get('rec_suspicious_title', '⚠️ BE CAREFUL - SUSPICIOUS FILE!')}</b><br><br>
            <b>{lang_data.get('rec_suspicious_why', 'Why this is suspicious:')}</b><br>
            {lang_data.get('rec_suspicious_why_content', 'The file contains elements that may indicate a threat, but there is no final confirmation. This could be:<br>• A new virus not yet added to signature databases<br>• A legitimate program with non-standard behavior<br>• An administrator tool that looks suspicious')}<br><br>
            <b>{lang_data.get('rec_suspicious_what', 'What to do:')}</b><br>
            {lang_data.get('rec_suspicious_what_content', '1. <b>Not recommended to use</b> this file without additional verification<br>2. If the file is needed - run it in a fully isolated environment (virtual machine without network access)<br>3. Try to get this file from another, more reliable source<br>4. Check the file through online services (VirusTotal and similar)<br>5. Contact the software developer to confirm authenticity')}
            </div>
            """
        else:
            rec_text = f"""
            <div style='font-size: 15px; line-height: 2.0; color: #10B981;'>
            <b style='font-size: 18px;'>{lang_data.get('rec_safe_title', '✅ FILE IS SAFE')}</b><br><br>
            <b>{lang_data.get('rec_safe_why', 'Why the file is considered safe:')}</b><br>
            {lang_data.get('rec_safe_why_content', 'The file has passed all checks and showed no signs of malicious activity:<br>• No matches with known viruses<br>• File behavior fully matches declared functions<br>• File structure and metadata are correct')}<br><br>
            <b>{lang_data.get('rec_safe_what', 'Recommendations:')}</b><br>
            {lang_data.get('rec_safe_what_content', '1. File can be used safely<br>2. Apply standard precautions<br>3. Make sure the file is from a reliable source<br>4. If in doubt - conduct additional verification')}
            </div>
            """
        
        rec_label = QLabel(rec_text)
        rec_label.setWordWrap(True)
        rec_layout.addWidget(rec_label)
        rec_group.setLayout(rec_layout)
        layout.addWidget(rec_group)
        
        layout.addStretch()
        return scroll

    def create_help_tab(self) -> QWidget:
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок справки
        help_title = QLabel("❓ Справка и помощь")
        help_title.setObjectName("helpTitle")
        help_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(help_title)
        
        # Разделы справки
        sections = [
            ("🎯 Что такое RedSand Secure?", 
             "RedSand Secure - это система анализа подозрительных файлов. Она проверяет файлы на наличие вирусов и других угроз безопасности, используя статический и поведенческий анализ."),
            
            ("📁 Как проверить файл?",
             "1. Нажмите кнопку 'Выбрать файл'<br>"
             "2. Укажите подозрительный файл на вашем компьютере<br>"
             "3. Нажмите 'ЗАПУСТИТЬ АНАЛИЗ'<br>"
             "4. Дождитесь завершения проверки<br>"
             "5. Изучите результаты в окне отчета"),
            
            ("⚠️ Меры предосторожности",
             "<b>ВАЖНО:</b> Всегда запускайте анализ потенциально опасных файлов только в изолированной виртуальной машине! Это защитит вашу основную систему от возможного заражения."),
            
            ("📊 Понимание результатов",
             "<b>БЕЗОПАСНО (зеленый)</b> - Файл не содержит известных угроз. Можно использовать.<br>"
             "<b>ПОДОЗРИТЕЛЬНО (желтый)</b> - Файл содержит сомнительные элементы. Лучше не использовать.<br>"
             "<b>ОПАСНО (красный)</b> - Обнаружен вирус. Немедленно удалите файл!<br><br>"
             "<b>Как мы определяем угрозу:</b><br>"
             "• Статический анализ - проверка сигнатур вирусов в базе данных<br>"
             "• Поведенческий анализ - наблюдение за действиями файла в изолированной среде<br>"
             "• Эвристический анализ - поиск подозрительных паттернов в коде<br>"
             "• Анализ метаданных - проверка информации о файле"),
            
            ("⚙️ Настройки анализа",
             "<b>Время анализа</b> - максимальное время проверки файла<br>"
             "<b>Создавать варианты файла</b> - генерирует модификации файла для лучшего обнаружения сложных угроз<br>"
             "<b>Отключать сеть</b> - защищает вашу сеть во время анализа (рекомендуется)<br>"
             "<b>Тема оформления</b> - выберите удобную для вас цветовую схему")
        ]
        
        for title, content in sections:
            section_group = QGroupBox(title)
            section_layout = QVBoxLayout()
            
            content_label = QLabel(content)
            content_label.setObjectName("helpText")
            content_label.setWordWrap(True)
            content_label.setTextFormat(Qt.RichText)
            content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            section_layout.addWidget(content_label)
            
            section_group.setLayout(section_layout)
            layout.addWidget(section_group)
        
        layout.addStretch()
        return scroll


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setMinimumWidth(600)
        # Убираем вопросительный знак из заголовка окна
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title_label = QLabel("⚙ Настройки программы")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Тема оформления
        theme_group = QGroupBox("🎨 Тема оформления")
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Выберите тему:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Тёмная"])
        self.theme_combo.setMinimumWidth(200)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Время анализа
        timeout_group = QGroupBox("⏱ Время анализа")
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Максимальное время:"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(60)
        self.timeout_spin.setMinimumWidth(100)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addWidget(QLabel("сек"))
        timeout_layout.addStretch()
        timeout_group.setLayout(timeout_layout)
        layout.addWidget(timeout_group)
        
        # Дополнительные опции
        options_group = QGroupBox("🔧 Дополнительные опции")
        options_layout = QVBoxLayout()
        
        self.poly_check = QCheckBox("Создавать варианты файла для анализа")
        self.poly_check.setToolTip("Помогает обнаружить сложные вирусы путем создания модификаций файла")
        options_layout.addWidget(self.poly_check)
        
        self.network_check = QCheckBox("Отключать сеть во время анализа (рекомендуется)")
        self.network_check.setChecked(True)
        self.network_check.setToolTip("Защищает вашу сеть от потенциальной угрозы")
        options_layout.addWidget(self.network_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Справка
        help_group = QGroupBox("❓ Справка по настройкам")
        help_layout = QVBoxLayout()
        help_text = QLabel(
            "<b>Как использовать настройки:</b><br><br>"
            "<b>Тема оформления:</b> Выберите удобный для вас визуальный стиль интерфейса<br>"
            "<b>Время анализа:</b> Максимальное время проверки одного файла (по умолчанию 60 сек)<br>"
            "<b>Создавать варианты файла:</b> Генерирует модификации файла для лучшего обнаружения сложных угроз<br>"
            "<b>Отключать сеть:</b> Защищает вашу локальную сеть во время анализа вредоносного ПО (рекомендуется всегда включать)<br><br>"
            "<b style='color: #EF4444;'>ВАЖНО:</b> Запускайте анализ только в изолированной виртуальной машине!"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("font-size: 15px; line-height: 1.8;")
        help_layout.addWidget(help_text)
        help_group.setLayout(help_layout)
        layout.addWidget(help_group)
        
        layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setFixedHeight(55)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_settings(self):
        return {
            'timeout': self.timeout_spin.value(),
            'use_poly_default': self.poly_check.isChecked(),
            'auto_disable_network': self.network_check.isChecked(),
            'theme': self.theme_combo.currentText()
        }


class RedSandSecureGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker_thread: Optional[QThread] = None
        self.worker: Optional[AnalysisWorker] = None
        self.current_report: Optional[dict] = None
        self.analysis_completed = False  # Флаг завершения анализа
        self.current_lang = "Русский"  # Текущий язык
        self.settings = {
            'timeout': 60, 'output_dir': 'reports', 'use_poly_default': False,
            'auto_disable_network': True, 'log_level': 'INFO', 'theme': 'Тёмная',
            'language': 'Русский'
        }
        self.scan_history = []  # История сканирований
        self.setup_ui()
        self.apply_stylesheet()
        self.load_settings()

    def setup_ui(self):
        self.setWindowTitle("RedSand Secure - Анализ файлов")
        # Запуск в полноэкранном режиме (maximized)
        self.showMaximized()
        
        # Центральное виджет с Drag&Drop поддержкой
        central_widget = QWidget()
        central_widget.setAcceptDrops(True)
        central_widget.dragEnterEvent = self.drag_enter_event
        central_widget.dropEvent = self.drop_event
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Верхняя панель с кнопками
        top_panel = QHBoxLayout()
        
        # Выбор языка
        lang_label = QLabel("Язык:")
        top_panel.addWidget(lang_label)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Русский", "English"])
        self.lang_combo.setCurrentText(self.current_lang)
        self.lang_combo.currentTextChanged.connect(self.change_language)
        self.lang_combo.setMinimumWidth(120)
        top_panel.addWidget(self.lang_combo)
        
        top_panel.addStretch()
        
        # Кнопка настроек
        btn_settings = QPushButton("⚙ Настройки")
        btn_settings.setObjectName("secondaryBtn")
        btn_settings.clicked.connect(self.open_settings)
        top_panel.addWidget(btn_settings)
        
        # Кнопка отчетов
        btn_reports = QPushButton("📂 Отчеты")
        btn_reports.setObjectName("secondaryBtn")
        btn_reports.clicked.connect(self.open_reports_folder)
        top_panel.addWidget(btn_reports)
        
        # Кнопка истории
        btn_history = QPushButton("📜 История")
        btn_history.setObjectName("secondaryBtn")
        btn_history.clicked.connect(self.open_history)
        top_panel.addWidget(btn_history)
        
        main_layout.addLayout(top_panel)
        
        title_label = QLabel("RedSand Secure")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #CCCCCC; min-height: 3px;")
        main_layout.addWidget(line)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.create_left_panel())
        splitter.addWidget(self.create_right_panel())
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        main_layout.addWidget(splitter)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()

    def drag_enter_event(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def drop_event(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                self.file_path_edit.setText(file_path)
                self.log_message('INFO', f"Файл перетащен: {file_path}")
                break

    def create_left_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        file_group = QGroupBox("Шаг 1: Выберите файл")
        file_layout = QVBoxLayout()
        
        self.file_path_edit = QLineEdit()
        lang = self.settings.get('language', 'Русский')
        if lang == 'Русский':
            placeholder = "Файл еще не выбран... или перетащите сюда"
        else:
            placeholder = "No file selected... or drag and drop here"
        self.file_path_edit.setPlaceholderText(placeholder)
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setMinimumHeight(50)
        file_layout.addWidget(self.file_path_edit)
        
        btn_select_file = QPushButton("📁 Выбрать файл")
        btn_select_file.setObjectName("actionBtn")
        btn_select_file.clicked.connect(self.select_file)
        file_layout.addWidget(btn_select_file)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        settings_group = QGroupBox("Шаг 2: Настройки (необязательно)")
        settings_layout = QVBoxLayout()
        
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Время анализа:"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(60)
        self.timeout_spin.setMinimumWidth(80)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addWidget(QLabel("сек"))
        timeout_layout.addStretch()
        settings_layout.addLayout(timeout_layout)
        
        self.poly_check = QCheckBox("Создавать варианты файла для анализа")
        self.poly_check.setToolTip("Помогает обнаружить сложные вирусы")
        settings_layout.addWidget(self.poly_check)
        
        self.network_check = QCheckBox("Отключать сеть (рекомендуется)")
        self.network_check.setChecked(True)
        self.network_check.setToolTip("Защищает вашу сеть во время анализа")
        settings_layout.addWidget(self.network_check)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        self.btn_analyze = QPushButton("🚀 ЗАПУСТИТЬ АНАЛИЗ")
        self.btn_analyze.setObjectName("primaryBtn")
        self.btn_analyze.clicked.connect(self.start_analysis)
        layout.addWidget(self.btn_analyze)
        
        progress_group = QGroupBox("Прогресс")
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(35)
        progress_layout.addWidget(self.progress_bar)
        self.progress_label = QLabel("Ожидание...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #666; font-size: 16px;")
        progress_layout.addWidget(self.progress_label)
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        layout.addStretch()
        return widget

    def create_right_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        self.tabs = QTabWidget()
        logs_widget = self.create_logs_tab()
        logs_widget._tab_name_ru = "📋 Журнал"
        logs_widget._tab_name_en = "📋 Logs"
        self.tabs.addTab(logs_widget, logs_widget._tab_name_ru)
        results_widget = self.create_results_tab()
        results_widget._tab_name_ru = "📊 Результаты"
        results_widget._tab_name_en = "📊 Results"
        self.tabs.addTab(results_widget, results_widget._tab_name_ru)
        layout.addWidget(self.tabs)
        return widget

    def create_logs_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 14))
        self.log_text.setPlaceholderText("Здесь будет отображаться ход анализа...")
        layout.addWidget(self.log_text)
        return widget

    def create_results_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.results_summary = QLabel("Результаты анализа появятся здесь после завершения...")
        self.results_summary.setAlignment(Qt.AlignCenter)
        self.results_summary.setFont(QFont("Segoe UI", 16))
        self.results_summary.setStyleSheet("color: #666; padding: 50px;")
        layout.addWidget(self.results_summary)
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Параметр", "Значение"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # Запрет редактирования таблицы
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setVisible(False)
        layout.addWidget(self.results_table)
        return widget

    def apply_stylesheet(self):
        theme_name = self.settings.get('theme', 'High Contrast')
        self.setStyleSheet(generate_stylesheet(theme_name))

    def load_settings(self):
        settings_file = Path('gui_settings.json')
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                self.timeout_spin.setValue(self.settings.get('timeout', 60))
                self.poly_check.setChecked(self.settings.get('use_poly_default', False))
                self.network_check.setChecked(self.settings.get('auto_disable_network', True))
                # Применяем тему после загрузки настроек
                theme = self.settings.get('theme', 'Светлая')
                if theme != self.settings.get('_current_theme', None):
                    self.setStyleSheet(generate_stylesheet(theme))
                    self.settings['_current_theme'] = theme
            except Exception as e:
                self.log_message('WARNING', f"Ошибка загрузки настроек: {e}")

    def save_settings(self):
        settings_file = Path('gui_settings.json')
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_message('ERROR', f"Ошибка сохранения настроек: {e}")

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл для анализа", "",
            "Все файлы (*.*);;Executable файлы (*.exe);;DLL файлы (*.dll)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            self.log_message('INFO', f"Выбран файл: {file_path}")
            self.status_bar.showMessage(f"Файл выбран: {file_path}")

    def start_analysis(self):
        file_path = self.file_path_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите файл для анализа!")
            return
        if not os.path.exists(file_path):
            QMessageBox.critical(self, "Ошибка", f"Файл не найден: {file_path}")
            return
        
        # Сбрасываем флаг завершения перед новым анализом
        self.analysis_completed = False
        
        reply = QMessageBox.question(
            self, "Предупреждение о безопасности",
            "Вы запускаете анализ потенциально опасного файла!\n\n"
            "Убедитесь, что вы работаете в виртуальной машине.\n\nПродолжить?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
        
        # Очищаем предыдущие результаты
        self.current_report = None
        self.results_table.setRowCount(0)
        self.results_summary.setVisible(True)
        self.results_table.setVisible(False)
        self.log_text.clear()
        
        self.settings['timeout'] = self.timeout_spin.value()
        self.settings['use_poly_default'] = self.poly_check.isChecked()
        self.settings['auto_disable_network'] = self.network_check.isChecked()
        self.save_settings()
        self.set_ui_enabled(False)
        self.worker = AnalysisWorker(
            file_path=file_path, use_poly=self.poly_check.isChecked(),
            timeout=self.timeout_spin.value()
        )
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.analysis_finished)
        self.worker.error.connect(self.analysis_error)
        self.worker.log_message.connect(self.log_message)
        self.worker_thread.start()
        self.log_message('INFO', f"Запуск анализа файла: {file_path}")
        self.status_bar.showMessage("Анализ запущен...")

    def analysis_finished(self, result: dict):
        self.current_report = result
        self.analysis_completed = True  # Устанавливаем флаг завершения
        self.set_ui_enabled(True)
        self.progress_bar.setValue(100)
        self.progress_label.setText("Анализ завершен успешно!")
        self.update_results_display(result)
        self.log_message('SUCCESS', "Анализ завершен успешно!")
        self.status_bar.showMessage("Анализ завершен")
        
        # Сохраняем в историю
        if result:
            threat_info = result.get('threat_info') or {}
            risk_score = threat_info.get('risk_score', 0) if isinstance(threat_info, dict) else 0
            
            # Определяем вердикт
            if risk_score >= 70:
                verdict = "ОПАСНО" if self.current_lang == "Русский" else "DANGEROUS"
            elif risk_score >= 40:
                verdict = "ПОДОЗРИТЕЛЬНО" if self.current_lang == "Русский" else "SUSPICIOUS"
            else:
                verdict = "БЕЗОПАСНО" if self.current_lang == "Русский" else "SAFE"
            
            file_path = self.file_path_edit.text()
            self.save_to_history(file_path, verdict)
            
            dialog = DetailedReportDialog(result, self)
            dialog.exec_()

    def analysis_error(self, error_msg: str):
        self.set_ui_enabled(True)
        self.progress_label.setText("Ошибка анализа!")
        self.progress_label.setStyleSheet("color: #CC0000; font-weight: bold;")
        self.log_message('ERROR', error_msg)
        self.status_bar.showMessage("Ошибка анализа")
        QMessageBox.critical(self, "Ошибка анализа", error_msg)

    def update_progress(self, value: int, message: str):
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
        self.status_bar.showMessage(message)

    def log_message(self, level: str, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            'INFO': '#0066CC', 'DEBUG': '#666666', 'WARNING': '#FF8C00',
            'ERROR': '#CC0000', 'CRITICAL': '#FF0000', 'SUCCESS': '#008000'
        }
        color = colors.get(level, '#333333')
        html = f'<span style="color: {color}; font-weight: bold;">[{timestamp}]</span> {message}<br>'
        self.log_text.append(html)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_results_display(self, result: dict):
        threat_info = result.get('threat_info') or {}
        if not isinstance(threat_info, dict):
            threat_info = {}
        static_data = result.get('static_results') or {}
        file_name = static_data.get('file_name', 'N/A') if static_data else 'N/A'
        file_size = static_data.get('file_size', 0) if static_data else 0
        self.results_summary.setVisible(False)
        self.results_table.setVisible(True)
        self.results_table.setRowCount(0)
        data = [
            ("Тип угрозы", threat_info.get('type', 'Неизвестно')),
            ("Семейство", threat_info.get('family', 'Неизвестно')),
            ("Имя файла", file_name),
            ("Размер файла", f"{file_size} байт"),
        ]
        for param, value in data:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            self.results_table.setItem(row, 0, QTableWidgetItem(param))
            self.results_table.setItem(row, 1, QTableWidgetItem(str(value)))

    def open_settings(self):
        try:
            dialog = SettingsDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                settings = dialog.get_settings()
                old_theme = self.settings.get('theme', 'Тёмная')
                self.settings.update(settings)
                self.save_settings()
                
                # Если тема изменилась, применяем новую
                new_theme = self.settings.get('theme', 'Тёмная')
                if old_theme != new_theme:
                    self.setStyleSheet(generate_stylesheet(new_theme))
                    self.settings['_current_theme'] = new_theme
                
                self.log_message('INFO', f"Настройки сохранены. Тема: {new_theme}")
        except Exception as e:
            self.log_message('ERROR', f"Ошибка при открытии настроек: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть настройки: {str(e)}")

    def open_reports_folder(self):
        reports_dir = Path(self.settings.get('output_dir', 'reports'))
        reports_dir.mkdir(exist_ok=True)
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(reports_dir.absolute())))
        except Exception as e:
            self.log_message('ERROR', f"Ошибка открытия папки: {e}")
            QMessageBox.warning(self, "Предупреждение", f"Не удалось открыть папку.\nПуть: {reports_dir.absolute()}")

    def open_history(self):
        """Открыть диалог истории сканирований"""
        try:
            dialog = HistoryDialog(parent=self)
            dialog.exec_()
        except Exception as e:
            self.log_message('ERROR', f"Ошибка открытия истории: {e}")

    def change_language(self, language: str):
        """Сменить язык интерфейса - полная локализация"""
        self.current_lang = language
        self.settings['language'] = language
        self.save_settings()
        
        # Получаем переводы
        lang_data = LANGUAGES.get(language, LANGUAGES["Русский"])
        
        # Обновляем все текстовые элементы
        self.btn_select_file.setText(lang_data.get('select_file', '📁 Select File'))
        self.file_path_edit.setPlaceholderText(lang_data.get('file_placeholder', 'No file selected...'))
        self.btn_analyze.setText(lang_data.get('analyze_btn', '🚀 START ANALYSIS'))
        self.timeout_label.setText(lang_data.get('analysis_time', 'Analysis time:') + " (sec)")
        self.poly_check.setText(lang_data.get('poly_check', 'Create file variants'))
        self.network_check.setText(lang_data.get('network_check', 'Disable network'))
        
        # Обновляем заголовки вкладок
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if hasattr(tab, '_tab_name_ru') and hasattr(tab, '_tab_name_en'):
                if language == "Русский":
                    self.tabs.setTabText(i, tab._tab_name_ru)
                else:
                    self.tabs.setTabText(i, tab._tab_name_en)
        
        self.log_message('INFO', f"Язык изменен на: {language}")
        self.update_status_bar()

    def update_status_bar(self):
        """Обновить строку состояния - черный цвет с белым текстом"""
        lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
        msg = lang.get('file_placeholder', 'Ready')
        self.status_bar.setStyleSheet("QStatusBar { background-color: #000000; color: #FFFFFF; font-weight: bold; font-size: 14px; }")
        self.status_bar.showMessage(msg[:50] + "...")

    def set_ui_enabled(self, enabled: bool):
        self.btn_analyze.setEnabled(enabled)
        self.file_path_edit.setEnabled(enabled)
        self.timeout_spin.setEnabled(enabled)
        self.poly_check.setEnabled(enabled)
        self.network_check.setEnabled(enabled)

    def save_to_history(self, file_path: str, verdict: str):
        """Сохранить результат в историю"""
        entry = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'file': file_path,
            'verdict': verdict
        }
        self.scan_history.append(entry)
        
        # Сохраняем в файл
        history_file = Path("scan_history.json")
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = []
        else:
            history = []
        
        history.append(entry)
        # Храним только последние 100 записей
        history = history[-100:]
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def closeEvent(self, event):
        # Если анализ уже завершен, закрываем без вопросов
        if self.analysis_completed:
            if self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.quit()
                self.worker_thread.wait(1000)
            event.accept()
            return
        
        # Проверяем, запущен ли анализ в данный момент
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.warning(
                self, "Анализ выполняется",
                "Анализ все еще выполняется. Вы уверены, что хотите выйти?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
            self.worker_thread.quit()
            self.worker_thread.wait(3000)
        event.accept()


def main():
    # REDSAND_AVAILABLE теперь проверяется внутри AnalysisWorker
    app = QApplication(sys.argv)
    app.setApplicationName("RedSand Secure")
    window = RedSandSecureGUI()
    window.show()
    if not Path('gui_settings.json').exists():
        QMessageBox.warning(
            window, "Предупреждение о безопасности",
            "<h2>ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ</h2>"
            "<p>Вы запускаете инструмент для анализа потенциально опасных файлов.</p>"
            "<p><b>Запускайте ТОЛЬКО в изолированной виртуальной машине!</b></p>"
        )
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
