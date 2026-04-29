#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Secure GUI v12.0 - Главный экран с выбором режима
- Главный экран с двумя кнопками: Антивирус и Анализ файлов
- Все настройки перенесены на главный экран
- Красивое оформление с темной темой
- Docker изоляция по умолчанию
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
    QScrollArea, QGridLayout, QListWidget, QListWidgetItem, QStackedWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QSize, QUrl, QMimeData
from PyQt5.QtGui import QFont, QColor, QDesktopServices, QIcon, QPixmap, QDragEnterEvent, QDropEvent

# Импорт компонентов ядра
from core.realtime_antivirus import RealTimeAntivirus, QuarantineManager
from core.virus_scanner import VirusScanner


# Только тёмная тема оформления
THEMES = {
    "Dark": {
        "bg_primary": "#1a1a2e",
        "bg_secondary": "#16213e",
        "bg_tertiary": "#0f3460",
        "accent": "#e94560",
        "accent_hover": "#ff6b6b",
        "text_primary": "#ffffff",
        "text_secondary": "#b0b0b0",
        "success": "#00ff88",
        "warning": "#ffaa00",
        "danger": "#ff4444",
        "border": "#2a2a4e",
        "card_bg": "#1f1f3a"
    }
}


def generate_stylesheet(theme_name: str = "Dark") -> str:
    """Генерация CSS стилей для приложения"""
    theme = THEMES.get(theme_name, THEMES["Dark"])
    
    return f"""
    QMainWindow {{
        background-color: {theme['bg_primary']};
    }}
    
    QWidget {{
        background-color: {theme['bg_primary']};
        color: {theme['text_primary']};
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
    }}
    
    QLabel {{
        color: {theme['text_primary']};
    }}
    
    QLabel#titleLabel {{
        font-size: 48px;
        font-weight: bold;
        color: {theme['accent']};
        padding: 20px;
    }}
    
    QLabel#subtitleLabel {{
        font-size: 18px;
        color: {theme['text_secondary']};
        padding: 10px;
    }}
    
    QPushButton {{
        background-color: {theme['accent']};
        color: white;
        border: none;
        border-radius: 12px;
        padding: 15px 30px;
        font-size: 16px;
        font-weight: bold;
        min-width: 200px;
        min-height: 60px;
    }}
    
    QPushButton:hover {{
        background-color: {theme['accent_hover']};
    }}
    
    QPushButton:pressed {{
        background-color: {theme['accent']};
    }}
    
    QPushButton#secondaryBtn {{
        background-color: {theme['bg_tertiary']};
        color: {theme['text_primary']};
        min-width: 120px;
        min-height: 45px;
        font-size: 14px;
        border: 2px solid {theme['border']};
        font-weight: bold;
    }}
    
    QPushButton#secondaryBtn:hover {{
        background-color: {theme['accent']};
        color: white;
        border-color: {theme['accent']};
    }}
    
    QPushButton#actionBtn {{
        background-color: {theme['accent']};
        color: white;
        min-width: 140px;
        min-height: 50px;
        border: 2px solid {theme['border']};
    }}
    
    QPushButton#actionBtn:hover {{
        background-color: {theme['accent_hover']};
        border-color: {theme['accent']};
    }}
    
    QPushButton#dangerBtn {{
        background-color: {theme['bg_tertiary']};
        color: {theme['text_primary']};
        min-width: 140px;
        min-height: 50px;
        border: 2px solid {theme['border']};
    }}
    
    QPushButton#dangerBtn:hover {{
        background-color: #ff6b6b;
        color: white;
        border-color: #ff6b6b;
    }}
    
    QPushButton#langBtn {{
        background-color: {theme['bg_tertiary']};
        color: {theme['text_primary']};
        min-width: 50px;
        min-height: 50px;
        max-width: 50px;
        max-height: 50px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: bold;
        border: 2px solid {theme['border']};
    }}
    
    QPushButton#langBtn:checked {{
        background-color: {theme['accent']};
        color: white;
        border-color: {theme['accent']};
    }}
    
    QPushButton#langBtn:hover:!checked {{
        background-color: {theme['accent']};
        color: white;
        border-color: {theme['accent']};
    }}
    
    QPushButton#modeBtn {{
        background-color: {theme['card_bg']};
        border: 3px solid {theme['border']};
        border-radius: 20px;
        min-width: 280px;
        min-height: 280px;
        max-width: 280px;
        max-height: 280px;
        font-size: 24px;
        padding: 30px;
        color: {theme['text_primary']};
        font-weight: bold;
    }}
    
    QPushButton#modeBtn:hover {{
        border-color: {theme['accent']};
        background-color: {theme['bg_tertiary']};
        color: {theme['text_primary']};
    }}
    
    QPushButton#modeBtn:checked {{
        border-color: {theme['accent']};
        background-color: {theme['accent']};
        color: white;
    }}
    
    /* Стиль для placeholder текста в QLineEdit */
    QLineEdit::placeholder {{
        color: {theme['text_secondary']};
    }}
    
    QGroupBox {{
        font-weight: bold;
        font-size: 16px;
        color: {theme['text_primary']};
        border: 2px solid {theme['border']};
        border-radius: 12px;
        margin-top: 20px;
        padding-top: 20px;
        background-color: {theme['card_bg']};
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 10px;
        color: {theme['accent']};
    }}
    
    QProgressBar {{
        border: 2px solid {theme['border']};
        border-radius: 10px;
        text-align: center;
        background-color: {theme['bg_secondary']};
        height: 35px;
        color: {theme['text_primary']};
    }}
    
    QProgressBar::chunk {{
        background-color: {theme['accent']};
        border-radius: 8px;
    }}
    
    QTextEdit {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 2px solid {theme['border']};
        border-radius: 10px;
        padding: 10px;
        font-family: 'Consolas', monospace;
        font-size: 14px;
    }}
    
    QTableWidget {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 2px solid {theme['border']};
        border-radius: 10px;
        gridline-color: {theme['border']};
    }}
    
    QTableWidget::item {{
        padding: 10px;
        border-bottom: 1px solid {theme['border']};
    }}
    
    QTableWidget::item:selected {{
        background-color: {theme['accent']};
        color: white;
    }}
    
    QHeaderView::section {{
        background-color: {theme['bg_tertiary']};
        color: {theme['text_primary']};
        padding: 12px;
        border: none;
        font-weight: bold;
        font-size: 15px;
    }}
    
    QSpinBox, QComboBox, QLineEdit {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 2px solid {theme['border']};
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
    }}
    
    QSpinBox::disabled, QComboBox::disabled, QLineEdit::disabled {{
        color: {theme['text_secondary']};
    }}
    
    QLineEdit::placeholder {{
        color: {theme['text_secondary']};
    }}
    
    QSpinBox:focus, QComboBox:focus, QLineEdit:focus {{
        border-color: {theme['accent']};
    }}
    
    QCheckBox {{
        color: {theme['text_primary']};
        font-size: 15px;
        spacing: 10px;
    }}
    
    QCheckBox::indicator {{
        width: 22px;
        height: 22px;
        border-radius: 6px;
        border: 2px solid {theme['border']};
        background-color: {theme['bg_secondary']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {theme['accent']};
        border-color: {theme['accent']};
    }}
    
    QTabWidget::pane {{
        border: 2px solid {theme['border']};
        border-radius: 10px;
        background-color: {theme['card_bg']};
    }}
    
    QTabBar::tab {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_secondary']};
        padding: 12px 25px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-right: 3px;
        font-weight: bold;
    }}
    
    QTabBar::tab:selected {{
        background-color: {theme['accent']};
        color: white;
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {theme['bg_tertiary']};
    }}
    
    QScrollBar:vertical {{
        background-color: {theme['bg_secondary']};
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {theme['border']};
        border-radius: 6px;
        min-height: 30px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {theme['accent']};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QFrame {{
        background-color: transparent;
    }}
    """


LANGUAGES = {
    "Русский": {
        "title": "RedSand Secure",
        "subtitle": "",
        "antivirus_mode": "🛡️ АНТИВИРУС",
        "analysis_mode": "АНАЛИЗ ФАЙЛОВ",
        "settings": "⚙ Настройки",
        "history": "📜 История",
        "quarantine": "⚠️ Карантин",
        "select_file": "📁 Выбрать файл",
        "analyze_btn": "🚀 ЗАПУСТИТЬ АНАЛИЗ",
        "av_on": "⏹️ ВЫКЛ",
        "av_off": "▶️ ВКЛ",
        "av_status_on": "🛡️ Антивирус: ВКЛ",
        "av_status_off": "🛡️ Антивирус: ВЫКЛ",
        "save": "Сохранить",
        "cancel": "Отмена",
        "back": "← Назад",
        "theme": "Тема оформления",
        "analysis_time": "Время анализа:",
        "poly_check": "Создавать варианты файла для анализа",
        "network_check": "Отключать сеть (рекомендуется)",
        "monitored_folders": "Мониторинг папок:",
        "auto_quarantine": "Авто-карантин угроз",
        "scan_on_access": "Сканирование при доступе",
        "language_label": "Язык/Language:",
        "add_folder": "📁 Добавить",
        "remove_folder": "🗑️ Удалить",
        "event_log": "Журнал событий антивируса",
        "log_placeholder": "Здесь будут отображаться события антивируса...",
        "protection_status": "Статус защиты",
        "folder_monitoring": "Мониторинг папок",
        "back_to_menu": "← Назад к главному меню",
        "quarantine_title": "🛡️ Карантин - Обнаруженные угрозы",
        "quarantine_info": "Файлы в карантине обезврежены и не могут нанести вред системе.",
        "quarantine_empty": "Карантин пуст",
        "refresh": "🔄 Обновить",
        "restore": "♻️ Восстановить",
        "delete_forever": "🗑️ Удалить навсегда",
        "close": "Закрыть",
        "col_date": "Дата",
        "col_filename": "Имя файла",
        "col_path": "Оригинальный путь",
        "col_reason": "Причина",
        "col_id": "ID",
        "restore_confirm": "Вы уверены, что хотите восстановить этот файл?\\nУбедитесь, что он безопасен!",
        "restore_success": "Файл успешно восстановлен!",
        "restore_error": "Не удалось восстановить файл",
        "delete_confirm": "Вы уверены, что хотите удалить этот файл НАВСЕГДА?\\nЭто действие необратимо!",
        "delete_success": "Файл успешно удален!",
        "history_title": "📋 История сканирований файлов",
        "history_info": "Здесь отображаются все файлы, которые были проанализированы.",
        "history_empty": "История пуста",
        "clear_history": "🗑️ Очистить историю",
        "clear_history_confirm": "Вы уверены, что хотите очистить всю историю сканирований?",
        "col_status": "Статус",
        "col_threats": "Угрозы",
        "col_file": "Файл",
        "status_clean": "БЕЗОПАСНЫЙ",
        "status_suspicious": "ПОДОЗРИТЕЛЬНЫЙ",
        "status_malicious": "ОПАСНЫЙ",
        "settings_title": "⚙ Настройки приложения",
        "theme_group": "Тема оформления",
        "analysis_settings_group": "Настройки анализа",
        "application_settings": "⚙ Настройки приложения",
        "analysis_settings": "Настройки анализа",
        "timeout_label": "Время анализа (сек):",
        "app_language": "Язык интерфейса",
        "av_running": "Антивирус запущен. Мониторинг: ",
        "av_start_error": "Не удалось запустить антивирус:",
        "av_stop_error": "Ошибка остановки: ",
        "av_start_msg": "Защита реального времени включена!\\n\\nМониторимые папки:\\n",
        "folder_exists": "Эта папка уже добавлена",
        "folder_added": "Добавлена папка: ",
        "folder_removed": "Удалена папка: ",
        "no_folders": "Не найдены стандартные папки для мониторинга.\\nАнтивирус не может быть запущен.",
        "docker_info": "ℹ️ Все файлы анализируются в изолированном Docker контейнере",
        "file_selected": "Выбран файл: ",
        "no_file": "Файл не выбран",
        "analyzing": "Анализ файла...",
        "analysis_complete": "Анализ завершён!",
        "threat_level": "Уровень угрозы: ",
        "detected_threats": "Обнаруженные угрозы:",
        "step1_file": "Шаг 1: Выберите файл",
        "step2_settings": "Шаг 2: Настройки анализа",
        "file_placeholder": "Файл еще не выбран... или перетащите сюда",
        "analysis_progress": "Прогресс анализа",
        "waiting": "Ожидание...",
        "logs_tab": "📋 Журнал      ",
        "results_tab": "📊 Результаты   ",
        "log_placeholder": "Здесь будет отображаться ход анализа...",
        "results_placeholder": "Результаты анализа появятся здесь после завершения...",
        "param_column": "Параметр",
        "value_column": "Значение",
        "static_analysis": "Статический анализ...",
        "dynamic_analysis": "Динамический анализ в Docker...",
        "behavior_analysis": "Анализ поведения...",
        "docker_isolated": "ℹ️ Все файлы анализируются в изолированном Docker контейнере",
        "select_file_title": "Выберите файл для анализа",
        "file_filter": "Все файлы (*);;EXE файлы (*.exe);;PDF файлы (*.pdf);;Office документы (*.docx *.xlsx *.pptx)",
        "no_file_error": "Пожалуйста, выберите существующий файл для анализа.",
        "analysis_started": "Начало анализа файла: ",
        "docker_security": "Используется Docker изоляция для безопасности",
        "scan_time": "Время сканирования",
        "clear_history_confirm_en": "Вы уверены, что хотите очистить всю историю сканирований?",
        "settings_saved": "Настройки сохранены",
        "rec_malicious": "НЕ ИСПОЛЬЗОВАТЬ! Файл содержит вредоносный код.",
        "rec_suspicious": "Будьте осторожны. Файл содержит подозрительные элементы.",
        "rec_clean": "Файл безопасен. Вы можете его использовать.",
        "action_quarantine": "Карантин",
        "action_delete": "Удалить",
        "action_keep": "Оставить",
        "action_required": "Требуемое действие",
        "recommendation": "Рекомендация",
        "file_type": "Тип файла",
        "size": "Размер",
        "detected_threats": "Обнаруженные угрозы",
        "matched_signatures": "Совпавшие сигнатуры",
        "matched_patterns": "Подозрительные паттерны",
        "static_analysis_progress": "Статический анализ...",
        "signature_check_progress": "Проверка сигнатур вирусов...",
        "behavior_analysis_progress": "Анализ поведения...",
        "static_analysis_log": "Выполняется статический анализ файла...",
        "signature_check_log": "Проверка по базе вредоносных сигнатур...",
        "behavior_analysis_log": "Анализ подозрительных паттернов...",
        "scan_error_log": "Ошибка сканирования:",
        "quarantine_error_log": "Ошибка карантина:",
        "file_quarantined_log": "Файл помещен в карантин:",
        "no_file_selected_error": "Пожалуйста, выберите существующий файл для анализа.",
        "analysis_start_log": "Начало анализа файла:",
        "using_virus_scanner": "Используется VirusScanner для проверки на вирусы",
        "warning": "Предупреждение",
        "information": "Информация",
        "error": "Ошибка",
        "av_activated": "Антивирус активирован",
        "deletion_error": "Ошибка удаления:",
        "no_threats": "Нет угроз"
    },
    "English": {
        "title": "RedSand Secure",
        "subtitle": "",
        "antivirus_mode": "🛡️ ANTIVIRUS",
        "analysis_mode": "FILE ANALYSIS",
        "settings": "⚙ Settings",
        "history": "📜 History",
        "quarantine": "⚠️ Quarantine",
        "select_file": "📁 Select File",
        "analyze_btn": "🚀 START ANALYSIS",
        "av_on": "⏹️ OFF",
        "av_off": "▶️ ON",
        "av_status_on": "🛡️ Antivirus: ON",
        "av_status_off": "🛡️ Antivirus: OFF",
        "save": "Save",
        "cancel": "Cancel",
        "back": "← Back",
        "theme": "Theme",
        "analysis_time": "Analysis Time:",
        "poly_check": "Create file variants for analysis",
        "network_check": "Disable network (recommended)",
        "monitored_folders": "Monitored Folders:",
        "auto_quarantine": "Auto-quarantine threats",
        "scan_on_access": "Scan on access",
        "language_label": "Language/Language:",
        "add_folder": "📁 Add",
        "remove_folder": "🗑️ Remove",
        "event_log": "Antivirus Event Log",
        "log_placeholder": "Antivirus events will be displayed here...",
        "protection_status": "Protection Status",
        "folder_monitoring": "Folder Monitoring",
        "back_to_menu": "← Back to Main Menu",
        "quarantine_title": "🛡️ Quarantine - Detected Threats",
        "quarantine_info": "Files in quarantine are neutralized and cannot harm the system.",
        "quarantine_empty": "Quarantine is empty",
        "refresh": "🔄 Refresh",
        "restore": "♻️ Restore",
        "delete_forever": "🗑️ Delete Forever",
        "close": "Close",
        "col_date": "Date",
        "col_filename": "File Name",
        "col_path": "Original Path",
        "col_reason": "Reason",
        "col_id": "ID",
        "restore_confirm": "Are you sure you want to restore this file?\\nMake sure it is safe!",
        "restore_success": "File successfully restored!",
        "restore_error": "Failed to restore file",
        "delete_confirm": "Are you sure you want to delete this file FOREVER?\\nThis action is irreversible!",
        "delete_success": "File successfully deleted!",
        "history_title": "📋 Scan History",
        "history_info": "All analyzed files are displayed here.",
        "history_empty": "History is empty",
        "clear_history": "🗑️ Clear History",
        "clear_history_confirm": "Are you sure you want to clear all scan history?",
        "col_status": "Status",
        "col_threats": "Threats",
        "col_file": "File",
        "status_clean": "SAFE",
        "status_suspicious": "SUSPICIOUS",
        "status_malicious": "DANGEROUS",
        "settings_title": "⚙ Application Settings",
        "theme_group": "Theme",
        "analysis_settings_group": "Analysis Settings",
        "application_settings": "⚙ Application Settings",
        "analysis_settings": "Analysis Settings",
        "timeout_label": "Analysis Time (sec):",
        "app_language": "Interface Language",
        "av_running": "Antivirus running. Monitoring: ",
        "av_start_error": "Failed to start antivirus:",
        "av_stop_error": "Stop error: ",
        "av_start_msg": "Real-time protection enabled!\\n\\nMonitored folders:\\n",
        "folder_exists": "This folder is already added",
        "folder_added": "Folder added: ",
        "folder_removed": "Folder removed: ",
        "no_folders": "No standard folders found for monitoring.\\nAntivirus cannot be started.",
        "docker_info": "ℹ️ All files are analyzed in an isolated Docker container",
        "file_selected": "Selected file: ",
        "no_file": "No file selected",
        "analyzing": "Analyzing file...",
        "analysis_complete": "Analysis complete!",
        "threat_level": "Threat level: ",
        "detected_threats": "Detected threats:",
        "step1_file": "Step 1: Select File",
        "step2_settings": "Step 2: Analysis Settings",
        "file_placeholder": "File not selected... or drag and drop here",
        "analysis_progress": "Analysis Progress",
        "waiting": "Waiting...",
        "logs_tab": "📋 Logs      ",
        "results_tab": "📊 Results   ",
        "log_placeholder": "Analysis progress will be displayed here...",
        "results_placeholder": "Analysis results will appear here after completion...",
        "param_column": "Parameter",
        "value_column": "Value",
        "static_analysis": "Static analysis...",
        "dynamic_analysis": "Dynamic analysis in Docker...",
        "behavior_analysis": "Behavior analysis...",
        "docker_isolated": "ℹ️ All files are analyzed in an isolated Docker container",
        "select_file_title": "Select file for analysis",
        "file_filter": "All files (*);;EXE files (*.exe);;PDF files (*.pdf);;Office documents (*.docx *.xlsx *.pptx)",
        "no_file_error": "Please select an existing file for analysis.",
        "analysis_started": "Starting file analysis: ",
        "docker_security": "Using Docker isolation for security",
        "scan_time": "Scan Time",
        "clear_history_confirm_en": "Are you sure you want to clear all scan history?",
        "settings_saved": "Settings saved",
        "rec_malicious": "DO NOT USE! File contains malicious code.",
        "rec_suspicious": "Be careful. File contains suspicious elements.",
        "rec_clean": "File is safe. You can use it.",
        "action_quarantine": "Quarantine",
        "action_delete": "Delete",
        "action_keep": "Keep",
        "action_required": "Action Required",
        "recommendation": "Recommendation",
        "file_type": "File Type",
        "size": "Size",
        "detected_threats": "Detected Threats",
        "matched_signatures": "Matched Signatures",
        "matched_patterns": "Suspicious Patterns",
        "static_analysis_progress": "Static analysis...",
        "signature_check_progress": "Virus signature check...",
        "behavior_analysis_progress": "Behavior analysis...",
        "static_analysis_log": "Performing static file analysis...",
        "signature_check_log": "Checking against malware signatures database...",
        "behavior_analysis_log": "Analyzing suspicious patterns...",
        "scan_error_log": "Scan error:",
        "quarantine_error_log": "Quarantine error:",
        "file_quarantined_log": "File quarantined:",
        "no_file_selected_error": "Please select an existing file for analysis.",
        "analysis_start_log": "Starting file analysis:",
        "using_virus_scanner": "Using VirusScanner for virus detection",
        "warning": "Warning",
        "information": "Information",
        "error": "Error",
        "av_activated": "Antivirus Activated",
        "deletion_error": "Deletion error:",
        "no_threats": "None"
    }
}


class MainModeSelector(QWidget):
    """Главный экран выбора режима работы"""
    
    mode_selected = pyqtSignal(str)  # "antivirus" или "analysis"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_ref = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Верхняя панель с кнопкой выхода
        top_panel = QHBoxLayout()
        top_panel.addStretch()
        
        # Кнопка выхода в правом верхнем углу
        self.btn_exit = QPushButton("❌ Выйти")
        self.btn_exit.setObjectName("exitBtn")
        self.btn_exit.setFixedSize(120, 40)
        self.btn_exit.clicked.connect(lambda: self.parent_ref.close() if self.parent_ref else None)
        self.btn_exit.setToolTip("Закрыть приложение")
        top_panel.addWidget(self.btn_exit)
        
        layout.addLayout(top_panel)
        
        # Заголовок
        title_label = QLabel("RedSand Secure")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(30)
        
        # Кнопки режимов
        modes_layout = QHBoxLayout()
        modes_layout.setSpacing(40)
        modes_layout.setAlignment(Qt.AlignCenter)
        
        # Кнопка Антивирус - убрано "Реального времени"
        self.btn_antivirus = QPushButton("🛡️\nАНТИВИРУС")
        self.btn_antivirus.setObjectName("modeBtn")
        self.btn_antivirus.clicked.connect(lambda: self.mode_selected.emit("antivirus"))
        self.btn_antivirus.setToolTip("Мониторинг системы и автоматическая защита")
        modes_layout.addWidget(self.btn_antivirus)
        
        # Кнопка Анализ файлов
        # Используем язык по умолчанию (Русский) при инициализации
        default_lang = LANGUAGES["Русский"]
        self.btn_analysis = QPushButton("🔍\n" + default_lang["analysis_mode"])
        self.btn_analysis.setObjectName("modeBtn")
        self.btn_analysis.clicked.connect(lambda: self.mode_selected.emit("analysis"))
        self.btn_analysis.setToolTip("Ручной анализ подозрительных файлов в Docker")
        modes_layout.addWidget(self.btn_analysis)
        
        layout.addLayout(modes_layout)
        
        layout.addStretch()
        
        # Нижняя панель с настройками
        bottom_panel = QHBoxLayout()
        bottom_panel.setAlignment(Qt.AlignCenter)
        
        # Выбор языка
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Язык/Language:")
        lang_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        lang_layout.addWidget(lang_label)
        lang_layout.addSpacing(10)
        
        self.btn_ru = QPushButton("RU")
        self.btn_ru.setObjectName("langBtn")
        self.btn_ru.setCheckable(True)
        self.btn_ru.setChecked(True)
        self.btn_ru.clicked.connect(lambda: self.parent_ref.change_language("Русский") if self.parent_ref else None)
        lang_layout.addWidget(self.btn_ru)
        
        self.btn_en = QPushButton("EN")
        self.btn_en.setObjectName("langBtn")
        self.btn_en.setCheckable(True)
        self.btn_en.setChecked(False)
        self.btn_en.clicked.connect(lambda: self.parent_ref.change_language("English") if self.parent_ref else None)
        lang_layout.addWidget(self.btn_en)
        
        bottom_panel.addLayout(lang_layout)
        bottom_panel.addSpacing(50)
        
        # Кнопка настроек
        self.btn_settings = QPushButton("⚙ Настройки")
        self.btn_settings.setObjectName("secondaryBtn")
        self.btn_settings.clicked.connect(lambda: self.parent_ref.open_settings() if self.parent_ref else None)
        bottom_panel.addWidget(self.btn_settings)
        
        # Кнопка истории
        self.btn_history = QPushButton("📜 История")
        self.btn_history.setObjectName("secondaryBtn")
        self.btn_history.clicked.connect(lambda: self.parent_ref.open_history() if self.parent_ref else None)
        bottom_panel.addWidget(self.btn_history)
        
        # Кнопка карантина - по центру свободного пространства
        self.btn_quarantine = QPushButton("⚠️ Карантин")
        self.btn_quarantine.setObjectName("secondaryBtn")
        self.btn_quarantine.clicked.connect(lambda: self.parent_ref.open_quarantine() if self.parent_ref else None)
        bottom_panel.addWidget(self.btn_quarantine)
        
        layout.addLayout(bottom_panel)
    
    def update_texts(self):
        """Обновить тексты при смене языка"""
        if not self.parent_ref:
            return
        lang = LANGUAGES.get(self.parent_ref.current_lang, LANGUAGES["Русский"])
        
        self.btn_antivirus.setText(lang["antivirus_mode"])
        self.btn_analysis.setText("🔍\n" + lang["analysis_mode"])
        self.btn_settings.setText(lang["settings"])
        self.btn_history.setText(lang["history"])
        self.btn_quarantine.setText(lang["quarantine"])


class AntivirusPanel(QWidget):
    """Панель управления антивирусом"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_ref = parent
        self.av_active = False
        self.av_monitor = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title_label = QLabel("🛡️ АНТИВИРУС")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Статус
        status_group = QGroupBox("Статус защиты")
        status_layout = QVBoxLayout(status_group)
        
        self.av_status_label = QLabel("🛡️ Антивирус: ВЫКЛ")
        self.av_status_label.setStyleSheet("color: #DC2626; font-weight: bold; font-size: 24px;")
        self.av_status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.av_status_label)
        
        self.btn_toggle_av = QPushButton("▶️ ВКЛ")
        self.btn_toggle_av.setObjectName("actionBtn")
        self.btn_toggle_av.setCheckable(True)
        self.btn_toggle_av.setChecked(False)
        self.btn_toggle_av.setMinimumHeight(60)
        self.btn_toggle_av.clicked.connect(self.toggle_antivirus)
        status_layout.addWidget(self.btn_toggle_av)
        
        layout.addWidget(status_group)
        
        # Настройки мониторинга
        monitor_group = QGroupBox("Мониторинг папок")
        monitor_layout = QVBoxLayout(monitor_group)
        
        # Список папок - сначала список с отступом снизу
        self.folder_list = QListWidget()
        self.folder_list.addItems([
            "~/Downloads",
            "~/Desktop", 
            "~/Documents"
        ])
        self.folder_list.setMaximumHeight(150)
        monitor_layout.addWidget(self.folder_list)
        
        # Кнопки управления папками - под списком папок, впритык снизу
        folder_btn_widget = QWidget()
        folder_btn_layout = QHBoxLayout(folder_btn_widget)
        folder_btn_layout.setContentsMargins(0, 0, 0, 0)
        folder_btn_layout.setSpacing(10)
        
        self.btn_add_folder = QPushButton(self.tr("Add"))
        self.btn_add_folder.setObjectName("secondaryBtn")
        self.btn_add_folder.setMinimumHeight(45)
        self.btn_add_folder.clicked.connect(self.add_folder)
        folder_btn_layout.addWidget(self.btn_add_folder)
        
        self.btn_remove_folder = QPushButton(self.tr("Remove"))
        self.btn_remove_folder.setObjectName("dangerBtn")
        self.btn_remove_folder.setMinimumHeight(45)
        self.btn_remove_folder.clicked.connect(self.remove_folder)
        self.btn_remove_folder.setEnabled(False)
        folder_btn_layout.addWidget(self.btn_remove_folder)
        
        monitor_layout.addWidget(folder_btn_widget)
        
        self.folder_list.itemSelectionChanged.connect(lambda: self.btn_remove_folder.setEnabled(len(self.folder_list.selectedItems()) > 0))
        
        self.chk_auto_quarantine = QCheckBox("Автоматический карантин угроз")
        self.chk_auto_quarantine.setChecked(True)
        monitor_layout.addWidget(self.chk_auto_quarantine)
        
        self.chk_scan_on_access = QCheckBox("Сканирование при доступе к файлу")
        self.chk_scan_on_access.setChecked(True)
        monitor_layout.addWidget(self.chk_scan_on_access)
        
        layout.addWidget(monitor_group)
        
        # Лог событий
        log_group = QGroupBox("Журнал событий антивируса")
        log_layout = QVBoxLayout(log_group)
        
        self.av_log = QTextEdit()
        self.av_log.setReadOnly(True)
        self.av_log.setFont(QFont("Consolas", 12))
        self.av_log.setPlaceholderText("Здесь будут отображаться события антивируса...")
        self.av_log.setMinimumHeight(200)
        log_layout.addWidget(self.av_log)
        
        layout.addWidget(log_group)
        
        # Кнопка назад
        btn_back = QPushButton("← Назад к главному меню")
        btn_back.setObjectName("secondaryBtn")
        btn_back.clicked.connect(lambda: self.parent_ref.show_main_menu() if self.parent_ref else None)
        layout.addWidget(btn_back)
    
    def toggle_antivirus(self):
        """Включение/выключение антивируса"""
        if not self.parent_ref:
            return
            
        # Получаем текущий язык
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        
        if self.av_active:
            # Выключаем
            try:
                if self.av_monitor:
                    self.av_monitor.stop()
                self.av_active = False
                self.btn_toggle_av.setChecked(False)
                self.btn_toggle_av.setText("▶️ ВКЛ")
                self.av_status_label.setText("🛡️ Антивирус: ВЫКЛ")
                self.av_status_label.setStyleSheet("color: #DC2626; font-weight: bold; font-size: 24px;")
                self.log_event("Антивирус остановлен")
            except Exception as e:
                self.log_event(f"Ошибка остановки: {e}")
        else:
            # Включаем
            try:
                monitor_paths = []
                for i in range(self.folder_list.count()):
                    path = self.folder_list.item(i).text()
                    expanded = os.path.expanduser(path)
                    if os.path.exists(expanded):
                        monitor_paths.append(expanded)
                
                if not monitor_paths:
                    QMessageBox.warning(self, lang.get("warning", "Warning"), 
                        lang.get("no_folders", "No standard folders found for monitoring.\nAntivirus cannot be started."))
                    self.btn_toggle_av.setChecked(False)
                    return
                
                self.av_monitor = RealTimeAntivirus(
                    monitored_folders=monitor_paths,
                    auto_quarantine=self.chk_auto_quarantine.isChecked(),
                    scan_on_access=self.chk_scan_on_access.isChecked()
                )
                # Привязываем менеджер карантина из главного окна
                self.av_monitor.quarantine_manager = self.parent_ref.quarantine_manager
                self.av_monitor.enable()
                self.av_monitor.start_background()
                
                self.av_active = True
                self.btn_toggle_av.setText(lang["av_on"])
                self.av_status_label.setText(lang["av_status_on"])
                self.av_status_label.setStyleSheet("color: #059669; font-weight: bold; font-size: 24px;")
                self.log_event(f"{lang['av_running']} {', '.join(monitor_paths)}")
                
                QMessageBox.information(self, lang.get("av_activated", "Antivirus Activated"),
                    f"{lang.get('av_start_msg', 'Real-time protection enabled!')}\n\n{lang.get('monitored_folders', 'Monitored folders:')}\n{chr(10).join(monitor_paths)}\n\n{lang.get('auto_quarantine_msg', 'All suspicious files will be automatically quarantined.')}")
                    
            except Exception as e:
                self.log_event(f"{lang.get('av_start_error', 'Failed to start antivirus:')} {e}")
                QMessageBox.critical(self, lang.get("error", "Error"), f"{lang.get('av_start_error', 'Failed to start antivirus:')}\\n{str(e)}")
                self.btn_toggle_av.setChecked(False)
    
    def log_event(self, message: str):
        """Запись события в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.av_log.append(f"[{timestamp}] {message}")
    
    def add_folder(self):
        """Добавить папку для мониторинга"""
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        folder = QFileDialog.getExistingDirectory(self, lang.get("select_folder_title", "Select folder for monitoring"))
        if folder:
            # Проверяем, нет ли уже такой папки в списке
            for i in range(self.folder_list.count()):
                if os.path.expanduser(self.folder_list.item(i).text()) == folder:
                    QMessageBox.information(self, lang.get("information", "Information"), lang.get("folder_exists", "This folder is already added"))
                    return
            
            self.folder_list.addItem(folder)
            self.log_event(lang.get("folder_added", "Folder added: ") + folder)
    
    def remove_folder(self):
        """Удалить выбранную папку из мониторинга"""
        selected_items = self.folder_list.selectedItems()
        if not selected_items:
            return
        
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        
        for item in selected_items:
            row = self.folder_list.row(item)
            folder_path = item.text()
            self.folder_list.takeItem(row)
            self.log_event(lang["folder_removed"] + folder_path)
        
        self.btn_remove_folder.setEnabled(False)
    
    def update_texts(self):
        """Обновить тексты при смене языка"""
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        
        # Обновляем заголовок
        title_widget = self.findChild(QLabel, "titleLabel")
        if title_widget:
            title_widget.setText(lang["antivirus_mode"])
        
        # Обновляем статусы
        if self.av_active:
            self.av_status_label.setText(lang["av_status_on"])
            self.btn_toggle_av.setText(lang["av_on"])
        else:
            self.av_status_label.setText(lang["av_status_off"])
            self.btn_toggle_av.setText(lang["av_off"])
        
        # Обновляем GroupBox
        groups = self.findChildren(QGroupBox)
        for group in groups:
            if group.title() == "Статус защиты":
                group.setTitle(lang["protection_status"])
            elif group.title() == "Мониторинг папок":
                group.setTitle(lang["folder_monitoring"])
            elif group.title() == "Журнал событий антивируса":
                group.setTitle(lang["event_log"])
        
        # Обновляем кнопки
        self.btn_add_folder.setText(lang["add_folder"])
        self.btn_remove_folder.setText(lang["remove_folder"])
        
        # Обновляем чекбоксы
        self.chk_auto_quarantine.setText(lang["auto_quarantine"])
        self.chk_scan_on_access.setText(lang["scan_on_access"])
        
        # Обновляем placeholder лога
        self.av_log.setPlaceholderText(lang["log_placeholder"])
        
        # Находим кнопку назад и обновляем
        for btn in self.findChildren(QPushButton):
            if btn.text().startswith("←"):
                btn.setText(lang["back_to_menu"])


class AnalysisPanel(QWidget):
    """Панель анализа файлов"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_ref = parent
        self.worker_thread = None
        self.worker = None
        self.analysis_completed = False
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Получаем язык для инициализации текстов
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        
        # Заголовок
        title_label = QLabel(lang["analysis_mode"])
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Создание основного макета
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Левая панель
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(20)
        
        # Выбор файла
        file_group = QGroupBox(lang["step1_file"])
        file_layout = QVBoxLayout(file_group)
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText(lang["file_placeholder"])
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setMinimumHeight(50)
        file_layout.addWidget(self.file_path_edit)
        
        self.btn_select_file = QPushButton(lang["select_file"])
        self.btn_select_file.setObjectName("actionBtn")
        self.btn_select_file.clicked.connect(self.select_file)
        file_layout.addWidget(self.btn_select_file)
        
        left_layout.addWidget(file_group)
        
        # Настройки анализа
        settings_group = QGroupBox(lang["step2_settings"])
        settings_layout = QVBoxLayout(settings_group)
        
        timeout_layout = QHBoxLayout()
        timeout_label = QLabel(lang["timeout_label"])
        timeout_layout.addWidget(timeout_label)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(60)
        self.timeout_spin.setMinimumWidth(80)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        settings_layout.addLayout(timeout_layout)
        
        self.poly_check = QCheckBox(lang["poly_check"])
        self.poly_check.setToolTip("Helps detect complex viruses")
        settings_layout.addWidget(self.poly_check)
        
        self.network_check = QCheckBox(lang["network_check"])
        self.network_check.setChecked(True)
        self.network_check.setToolTip("Protects your network during analysis")
        settings_layout.addWidget(self.network_check)
        
        docker_info = QLabel(lang["docker_info"])
        docker_info.setStyleSheet("color: #00ff88; font-style: italic;")
        settings_layout.addWidget(docker_info)
        
        left_layout.addWidget(settings_group)
        
        # Кнопка анализа
        self.btn_analyze = QPushButton(lang["analyze_btn"])
        self.btn_analyze.setObjectName("primaryBtn")
        self.btn_analyze.setMinimumHeight(60)
        self.btn_analyze.clicked.connect(self.start_analysis)
        left_layout.addWidget(self.btn_analyze)
        
        # Прогресс
        progress_group = QGroupBox(lang["analysis_progress"])
        progress_layout = QVBoxLayout(progress_group)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(35)
        progress_layout.addWidget(self.progress_bar)
        self.progress_label = QLabel(lang["waiting"])
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #666; font-size: 16px;")
        progress_layout.addWidget(self.progress_label)
        left_layout.addWidget(progress_group)
        
        left_layout.addStretch()
        main_splitter.addWidget(left_widget)
        
        # Правая панель с вкладками
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.tabs = QTabWidget()
        
        # Вкладка логов
        logs_widget = QWidget()
        logs_layout = QVBoxLayout(logs_widget)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 12))
        self.log_text.setPlaceholderText(lang["log_placeholder"])
        logs_layout.addWidget(self.log_text)
        # Увеличена ширина кнопки вкладки Журнал через stylesheet
        logs_widget.setStyleSheet("padding: 5px;")
        self.tabs.addTab(logs_widget, lang["logs_tab"])
        
        # Вкладка результатов
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        self.results_summary = QLabel(lang["results_placeholder"])
        self.results_summary.setAlignment(Qt.AlignCenter)
        self.results_summary.setFont(QFont("Segoe UI", 16))
        self.results_summary.setStyleSheet("color: #666; padding: 50px;")
        results_layout.addWidget(self.results_summary)
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels([lang["param_column"], lang["value_column"]])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setMinimumSectionSize(250)  # Увеличена ширина первой колонки
        self.results_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setVisible(False)
        results_layout.addWidget(self.results_table)
        # Увеличена ширина кнопки вкладки Результаты через stylesheet
        results_widget.setStyleSheet("padding: 5px;")
        self.tabs.addTab(results_widget, lang["results_tab"])
        
        right_layout.addWidget(self.tabs)
        main_splitter.addWidget(right_widget)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)
        
        layout.addWidget(main_splitter)
        
        # Кнопка назад
        btn_back = QPushButton(lang["back_to_menu"])
        btn_back.setObjectName("secondaryBtn")
        btn_back.clicked.connect(lambda: self.parent_ref.show_main_menu() if self.parent_ref else None)
        layout.addWidget(btn_back)
    
    def select_file(self):
        """Выбор файла для анализа"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл для анализа", "",
            "Все файлы (*);;EXE файлы (*.exe);;PDF файлы (*.pdf);;Office документы (*.docx *.xlsx *.pptx)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def start_analysis(self):
        """Запуск анализа файла с использованием VirusScanner"""
        file_path = self.file_path_edit.text().strip()
        
        # Получаем язык ПЕРЕД использованием
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, lang.get("warning", "Warning"), 
                               lang.get("no_file_selected_error", "Please select an existing file for analysis."))
            return
        
        self.btn_analyze.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.results_summary.setVisible(True)
        self.results_table.setVisible(False)
        
        is_ru = (self.parent_ref.current_lang if self.parent_ref else "Русский") == "Русский"
        
        self.log_message('INFO', f"{lang['analysis_start_log']} {file_path}")
        self.log_message('INFO', lang['using_virus_scanner'])
        
        # Добавляем запись в историю сканирований
        scan_record = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'file_name': os.path.basename(file_path),
            'file_path': file_path,
            'status': 'IN_PROGRESS',
            'threats': 0
        }
        if self.parent_ref:
            self.parent_ref.scan_history.append(scan_record)
        
        # Прогресс анализа
        self.progress_bar.setValue(25)
        self.progress_label.setText(lang['static_analysis_progress'])
        self.log_message('INFO', lang['static_analysis_log'])
        
        self.progress_bar.setValue(50)
        self.progress_label.setText(lang['signature_check_progress'])
        self.log_message('INFO', lang['signature_check_log'])
        
        self.progress_bar.setValue(75)
        self.progress_label.setText(lang['behavior_analysis_progress'])
        self.log_message('INFO', lang['behavior_analysis_log'])
        
        # Используем VirusScanner для реального анализа
        try:
            scanner = VirusScanner()
            scan_result = scanner.scan_file(file_path)
            
            threat_level = scan_result.get('threat_level', 'CLEAN')
            risk_score = scan_result.get('risk_score', 0)
            detected_threats = scan_result.get('detected_threats', [])
            matched_signatures = scan_result.get('matched_signatures', [])
            matched_patterns = scan_result.get('matched_patterns', [])
            
            # Определяем статус и цвет
            if threat_level == 'MALICIOUS':
                status_text = lang["status_malicious"]
                status_color = "#dc2626"
                final_threat_level = 'MALICIOUS'
            elif threat_level == 'SUSPICIOUS':
                status_text = lang["status_suspicious"]
                status_color = "#d97706"
                final_threat_level = 'SUSPICIOUS'
            else:
                status_text = lang["status_clean"]
                status_color = "#059669"
                final_threat_level = 'CLEAN'
            
            # Получаем рекомендацию
            if threat_level == 'MALICIOUS':
                recommendation = lang.get("rec_malicious", "DO NOT USE! File contains malicious code.")
                action_text = lang.get("action_quarantine", "Quarantine") + " / " + lang.get("action_delete", "Delete")
            elif threat_level == 'SUSPICIOUS':
                recommendation = lang.get("rec_suspicious", "Be careful. File contains suspicious elements.")
                action_text = lang.get("action_quarantine", "Quarantine") + " / " + lang.get("action_keep", "Keep")
            else:
                recommendation = lang.get("rec_clean", "File is safe. You can use it.")
                action_text = lang.get("action_keep", "Keep")
            
            # Автоматически помещаем в карантин опасные и подозрительные файлы
            if threat_level in ['MALICIOUS', 'SUSPICIOUS'] and self.parent_ref:
                try:
                    reason = f"{threat_level}: Risk Score {risk_score}"
                    if detected_threats:
                        reason += f" - {', '.join(detected_threats[:2])}"
                    self.parent_ref.quarantine_manager.add_to_quarantine(
                        file_path=file_path,
                        reason=reason
                    )
                    self.log_message('WARNING', f"{lang['file_quarantined_log']} {reason}")
                except Exception as e:
                    self.log_message('ERROR', f"{lang['quarantine_error_log']} {e}")
            
        except Exception as e:
            threat_level = 'ERROR'
            status_text = "❌ " + lang.get("status_malicious", "Error") if is_ru else "❌ Error"
            status_color = "#666666"
            final_threat_level = 'ERROR'
            recommendation = str(e)
            action_text = ""
            detected_threats = []
            matched_signatures = []
            matched_patterns = []
            risk_score = 0
            self.log_message('ERROR', f"{lang['scan_error_log']} {e}")
        
        self.progress_bar.setValue(100)
        self.progress_label.setText(lang["analysis_complete"])
        self.log_message('SUCCESS', lang["analysis_complete"])
        
        # Показываем результаты
        self.results_summary.setVisible(False)
        self.results_table.setVisible(True)
        
        # Формируем данные для таблицы результатов
        file_type = lang.get("file_type", "File Type")
        
        size_label = lang.get("size", "Size")
        size_value = f"{os.path.getsize(file_path)} bytes"
        
        results_data = [
            (lang.get("col_file", "File"), os.path.basename(file_path)),
            (lang.get("col_status", "Status"), status_text),
            (lang.get("recommendation", "Recommendation"), recommendation),
            (lang.get("action_required", "Action Required"), action_text),
            (file_type, file_type),
            (size_label, size_value),
        ]
        
        # Добавляем обнаруженные угрозы если есть
        if detected_threats:
            threats_label = lang.get("detected_threats", "Detected Threats")
            threats_str = ', '.join(detected_threats)
            results_data.append((threats_label, threats_str))
        
        # Добавляем matched signatures если есть
        if matched_signatures:
            sig_label = lang.get("matched_signatures", "Matched Signatures")
            sig_str = ', '.join(matched_signatures[:3])
            if len(matched_signatures) > 3:
                sig_str += f" (+{len(matched_signatures)-3})"
            results_data.append((sig_label, sig_str))
        
        # Добавляем matched patterns если есть
        if matched_patterns:
            pat_label = lang.get("matched_patterns", "Suspicious Patterns")
            pat_str = ', '.join(matched_patterns[:3])
            if len(matched_patterns) > 3:
                pat_str += f" (+{len(matched_patterns)-3})"
            results_data.append((pat_label, pat_str))
        
        self.results_table.setRowCount(len(results_data))
        for i, (param, value) in enumerate(results_data):
            item_param = QTableWidgetItem(param)
            item_param.setFlags(item_param.flags() & ~Qt.ItemIsEditable)
            item_param.setFont(QFont("Segoe UI", 12, QFont.Bold))
            self.results_table.setItem(i, 0, item_param)
            
            item_value = QTableWidgetItem(value)
            item_value.setFlags(item_value.flags() & ~Qt.ItemIsEditable)
            item_value.setFont(QFont("Segoe UI", 12))
            # Подсветка статуса
            if param == lang.get("col_status", "Status"):
                item_value.setBackground(QColor(status_color))
                item_value.setForeground(QColor("#ffffff"))
                item_value.setTextAlignment(Qt.AlignCenter)
            self.results_table.setItem(i, 1, item_value)
        
        # Обновляем запись в истории
        if self.parent_ref and len(self.parent_ref.scan_history) > 0:
            last_record = self.parent_ref.scan_history[-1]
            last_record['scan_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_record['threat_level'] = final_threat_level
            last_record['detected_threats'] = detected_threats
            last_record['status'] = final_threat_level
            last_record['threats'] = len(detected_threats)
            last_record['risk_score'] = risk_score
            last_record['recommendation'] = recommendation
        
        self.btn_analyze.setEnabled(True)
        
        # Показываем результат
        msg_title = lang["analysis_complete"]
        if threat_level == 'MALICIOUS':
            msg = f"⚠️ {lang['status_malicious']}!\n\n{recommendation}\n\n{lang.get('action_quarantine', 'Quarantine')}: {os.path.basename(file_path)}"
            QMessageBox.warning(self, msg_title, msg)
        elif threat_level == 'SUSPICIOUS':
            msg = f"⚠️ {lang['status_suspicious']}!\n\n{recommendation}"
            QMessageBox.warning(self, msg_title, msg)
        else:
            msg = f"✅ {lang['status_clean']}!\n\n{recommendation}"
            QMessageBox.information(self, msg_title, msg)
    
    def log_message(self, level: str, message: str):
        """Запись сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {'INFO': '#4CAF50', 'WARNING': '#FF9800', 'ERROR': '#F44336', 'SUCCESS': '#00BCD4'}
        color = colors.get(level, '#FFFFFF')
        self.log_text.append(f'<span style="color: {color};">[{timestamp}] [{level}] {message}</span>')
    
    def update_texts(self):
        """Обновление текстов при смене языка"""
        if not self.parent_ref:
            return
        
        lang = LANGUAGES.get(self.parent_ref.current_lang, LANGUAGES["Русский"])
        
        # Обновляем заголовок
        title_widgets = self.findChildren(QLabel, "titleLabel")
        for widget in title_widgets:
            if widget.objectName() == "titleLabel" and ("АНАЛИЗ" in widget.text() or "FILE ANALYSIS" in widget.text()):
                widget.setText(lang["analysis_mode"])
        
        # Обновляем GroupBox
        groups = self.findChildren(QGroupBox)
        for group in groups:
            if group.title().startswith("Шаг 1:") or "Select File" in group.title():
                group.setTitle(lang["step1_file"])
            elif group.title().startswith("Шаг 2:") or "Analysis Settings" in group.title():
                group.setTitle(lang["step2_settings"])
            elif group.title() == "Прогресс анализа" or group.title() == "Analysis Progress":
                group.setTitle(lang["analysis_progress"])
        
        # Обновляем кнопки и лейблы
        self.btn_select_file.setText(lang["select_file"])
        self.btn_analyze.setText(lang["analyze_btn"])
        
        # Обновляем placeholder
        self.file_path_edit.setPlaceholderText(lang["file_placeholder"])
        self.log_text.setPlaceholderText(lang["log_placeholder"])
        self.results_summary.setText(lang["results_placeholder"])
        self.progress_label.setText(lang["waiting"])
        
        # Обновляем labels timeout
        for label in self.findChildren(QLabel):
            if label.text().startswith("Время анализа") or label.text().startswith("Analysis Time"):
                label.setText(lang["timeout_label"])
        
        # Обновляем чекбоксы
        self.poly_check.setText(lang["poly_check"])
        self.network_check.setText(lang["network_check"])
        
        # Обновляем docker info
        for label in self.findChildren(QLabel):
            if "Docker" in label.text() and "ℹ️" in label.text():
                label.setText(lang["docker_info"])
        
        # Обновляем вкладки
        if self.tabs.count() >= 2:
            self.tabs.setTabText(0, lang["logs_tab"])
            self.tabs.setTabText(1, lang["results_tab"])
        
        # Обновляем заголовки таблицы
        if self.results_table.columnCount() >= 2:
            self.results_table.setHorizontalHeaderLabels([lang["param_column"], lang["value_column"]])
        
        # Находим кнопку назад и обновляем
        for btn in self.findChildren(QPushButton):
            if btn.text().startswith("←"):
                btn.setText(lang["back_to_menu"])


class ScanHistoryDialog(QDialog):
    """Диалог истории сканирований"""
    
    def __init__(self, scan_history=None, parent=None):
        super().__init__(parent)
        self.scan_history = scan_history or []
        self.parent_ref = parent
        self.current_lang = parent.current_lang if parent else "Русский"
        lang_key = "history_window_title"
        title_text = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"]).get(lang_key, "📜 История сканирований")
        self.setWindowTitle(title_text)
        self.setMinimumSize(1000, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.title_label = QLabel("📋 История сканирований файлов")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        self.info_label = QLabel("Здесь отображаются все файлы, которые были проанализированы.")
        self.info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.info_label)
        
        # Таблица истории
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.update_table_headers()
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.verticalHeader().setDefaultSectionSize(50)
        self.history_table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.history_table)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.setObjectName("secondaryBtn")
        self.btn_refresh.clicked.connect(self.load_history)
        btn_layout.addWidget(self.btn_refresh)
        
        self.btn_clear = QPushButton(self.tr("Clear History"))
        self.btn_clear.setObjectName("dangerBtn")
        self.btn_clear.clicked.connect(self.clear_history)
        btn_layout.addWidget(self.btn_clear)
        
        btn_layout.addStretch()
        
        self.btn_close = QPushButton(self.tr("Close"))
        self.btn_close.setObjectName("secondaryBtn")
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)
        
        self.load_history()
    
    def update_texts(self):
        """Обновить тексты при смене языка"""
        lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
        self.title_label.setText(lang["history_title"])
        self.info_label.setText(lang["history_info"])
        self.btn_refresh.setText(lang["refresh"])
        self.btn_clear.setText(lang["clear_history"])
        self.btn_close.setText(lang["close"])
        self.update_table_headers()
        self.load_history()
    
    def update_table_headers(self):
        """Обновить заголовки таблицы"""
        lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
        self.history_table.setHorizontalHeaderLabels([
            lang["col_date"], lang["col_file"], lang["col_status"], 
            lang["col_threats"], lang["col_path"]
        ])
    
    def load_history(self):
        """Загрузить историю сканирований"""
        self.history_table.setRowCount(0)
        
        lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
        
        if not self.scan_history:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            item = QTableWidgetItem(lang["history_empty"])
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.history_table.setItem(row, 0, item)
            return
        
        for item_data in self.scan_history:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            # Дата
            date_item = QTableWidgetItem(item_data.get('scan_time', 'N/A'))
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            self.history_table.setItem(row, 0, date_item)
            
            # Имя файла
            file_name = os.path.basename(item_data.get('file_path', 'Unknown'))
            file_item = QTableWidgetItem(file_name)
            file_item.setFlags(file_item.flags() & ~Qt.ItemIsEditable)
            font = file_item.font()
            font.setBold(True)
            file_item.setFont(font)
            self.history_table.setItem(row, 1, file_item)
            
            # Статус
            status = item_data.get('threat_level', 'UNKNOWN')
            status_item = QTableWidgetItem(status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            status_bg_color = QColor("#1a1a2e")  # Цвет фона для CLEAN
            
            # Перевод статуса
            if status == 'CLEAN':
                status_text = lang["status_clean"]
                status_bg_color = QColor("#059669")
            elif status == 'SUSPICIOUS':
                status_text = lang["status_suspicious"]
                status_bg_color = QColor("#d97706")
            elif status == 'MALICIOUS':
                status_text = lang["status_malicious"]
                status_bg_color = QColor("#dc2626")
            else:
                status_text = status
            
            status_item.setText(status_text)
            # Делаем текст белым на цветном фоне
            status_item.setBackground(status_bg_color)
            status_item.setForeground(QColor("#ffffff"))
            status_item.setTextAlignment(Qt.AlignCenter)
            font = status_item.font()
            font.setBold(True)
            status_item.setFont(font)
            self.history_table.setItem(row, 2, status_item)
            
            # Угрозы
            threats = ', '.join(item_data.get('detected_threats', []))
            no_threats_text = lang.get("no_threats", "Нет" if self.current_lang == "Русский" else "None")
            threats_item = QTableWidgetItem(threats if threats else no_threats_text)
            threats_item.setFlags(threats_item.flags() & ~Qt.ItemIsEditable)
            self.history_table.setItem(row, 3, threats_item)
            
            # Путь
            path_item = QTableWidgetItem(item_data.get('file_path', 'N/A'))
            path_item.setFlags(path_item.flags() & ~Qt.ItemIsEditable)
            path_item.setToolTip(item_data.get('file_path', ''))
            self.history_table.setItem(row, 4, path_item)
    
    def on_selection_changed(self):
        """Обработка выбора элемента"""
        # Детали больше не отображаются (удален details_text)
        pass
    
    def clear_history(self):
        """Очистить историю"""
        lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
        confirm_key = "clear_history_confirm" if self.current_lang == "Русский" else "clear_history_confirm_en"
        reply = QMessageBox.question(self, lang["clear_history"],
            lang.get(confirm_key, lang["clear_history_confirm"]),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes and self.parent_ref:
            self.parent_ref.scan_history = []
            self.scan_history = []
            self.load_history()


class QuarantineDialog(QDialog):
    """Диалог управления карантином"""
    
    def __init__(self, quarantine_manager=None, parent=None):
        super().__init__(parent)
        self.quarantine_manager = quarantine_manager
        self.parent_ref = parent
        self.current_lang = parent.current_lang if parent else "Русский"
        lang_key = "quarantine_window_title"
        title_text = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"]).get(lang_key, "⚠️ Карантин")
        self.setWindowTitle(title_text)
        self.setMinimumSize(900, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.title_label = QLabel("🛡️ Карантин - Обнаруженные угрозы")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        self.info_label = QLabel("Файлы в карантине обезврежены и не могут нанести вред системе.")
        self.info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.info_label)
        
        # Таблица файлов - увеличенная, занимает больше места
        self.quarantine_table = QTableWidget()
        self.quarantine_table.setColumnCount(5)
        self.update_table_headers()
        self.quarantine_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.quarantine_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.quarantine_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.quarantine_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.quarantine_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.quarantine_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.quarantine_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.quarantine_table.verticalHeader().setDefaultSectionSize(60)
        self.quarantine_table.itemSelectionChanged.connect(self.on_selection_changed)
        # Увеличиваем таблицу с помощью stretch factor
        layout.addWidget(self.quarantine_table, stretch=1)
        
        # Кнопки управления - все в одну линию с правильным расположением и вертикальным центрированием
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 15, 0, 15)
        
        # Кнопка "Обновить" слева
        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.setObjectName("secondaryBtn")
        self.btn_refresh.setMinimumHeight(50)
        self.btn_refresh.clicked.connect(self.load_quarantine)
        btn_layout.addWidget(self.btn_refresh)
        
        btn_layout.addStretch()
        
        # Кнопки "Восстановить" и "Удалить навсегда" по центру - динамичные кнопки
        center_widget = QWidget()
        center_layout = QHBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(10)
        self.btn_restore = QPushButton(self.tr("Restore"))
        self.btn_restore.setObjectName("actionBtn")
        self.btn_restore.setMinimumHeight(55)
        self.btn_restore.clicked.connect(self.restore_selected)
        self.btn_restore.setEnabled(False)
        center_layout.addWidget(self.btn_restore)
        
        self.btn_delete = QPushButton(self.tr("Delete Permanently"))
        self.btn_delete.setObjectName("dangerBtn")
        self.btn_delete.setMinimumHeight(55)
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_delete.setEnabled(False)
        center_layout.addWidget(self.btn_delete)
        
        btn_layout.addWidget(center_widget)
        btn_layout.addStretch()
        
        # Кнопка "Закрыть" справа
        self.btn_close = QPushButton(self.tr("Close"))
        self.btn_close.setObjectName("secondaryBtn")
        self.btn_close.setMinimumHeight(45)
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)
        
        self.load_quarantine()
    
    def update_texts(self):
        """Обновить тексты при смене языка"""
        lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
        self.title_label.setText(lang["quarantine_title"])
        self.info_label.setText(lang["quarantine_info"])
        self.btn_refresh.setText(lang["refresh"])
        self.btn_restore.setText(lang["restore"])
        self.btn_delete.setText(lang["delete_forever"])
        self.btn_close.setText(lang["close"])
        self.update_table_headers()
        self.load_quarantine()
    
    def update_table_headers(self):
        """Обновить заголовки таблицы"""
        lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
        self.quarantine_table.setHorizontalHeaderLabels([
            lang["col_date"], lang["col_filename"], lang["col_path"], 
            lang["col_reason"], lang["col_id"]
        ])
    
    def load_quarantine(self):
        """Загрузить список файлов из карантина"""
        self.quarantine_table.setRowCount(0)
        
        lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
        
        if not self.quarantine_manager:
            return
        
        items = self.quarantine_manager.list_quarantined()
        
        if not items:
            row = self.quarantine_table.rowCount()
            self.quarantine_table.insertRow(row)
            item = QTableWidgetItem(lang["quarantine_empty"])
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.quarantine_table.setItem(row, 0, item)
            return
        
        for idx, item_data in enumerate(items):
            row = self.quarantine_table.rowCount()
            self.quarantine_table.insertRow(row)
            
            # Дата
            date_item = QTableWidgetItem(item_data.get('quarantine_time', 'N/A')[:19])
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            self.quarantine_table.setItem(row, 0, date_item)
            
            # Имя файла
            file_name = os.path.basename(item_data.get('original_name', 'Unknown'))
            file_item = QTableWidgetItem(file_name)
            file_item.setToolTip(item_data.get('original_path', ''))
            file_item.setFlags(file_item.flags() & ~Qt.ItemIsEditable)
            font = file_item.font()
            font.setBold(True)
            file_item.setFont(font)
            self.quarantine_table.setItem(row, 1, file_item)
            
            # Оригинальный путь
            path_item = QTableWidgetItem(item_data.get('original_path', 'N/A'))
            path_item.setFlags(path_item.flags() & ~Qt.ItemIsEditable)
            path_item.setToolTip(item_data.get('original_path', ''))
            self.quarantine_table.setItem(row, 2, path_item)
            
            # Причина
            reason_item = QTableWidgetItem(item_data.get('reason', 'Unknown'))
            reason_item.setFlags(reason_item.flags() & ~Qt.ItemIsEditable)
            reason_item.setToolTip(f"Full reason: {item_data.get('reason', 'Unknown')}")
            self.quarantine_table.setItem(row, 3, reason_item)
            
            # ID (индекс для доступа)
            id_item = QTableWidgetItem(str(idx))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.quarantine_table.setItem(row, 4, id_item)
    
    def on_selection_changed(self):
        """Обработка выбора элемента"""
        selected_rows = self.quarantine_table.selectedItems()
        if not selected_rows:
            self.btn_restore.setEnabled(False)
            self.btn_delete.setEnabled(False)
            return
        
        row = selected_rows[0].row()
        self.btn_restore.setEnabled(True)
        self.btn_delete.setEnabled(True)
        
        # Детали отображаются прямо в строке таблицы
    
    def restore_selected(self):
        """Восстановление выбранного файла"""
        selected_rows = self.quarantine_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        # Берем ID из колонки 4 (индекс для доступа)
        id_item = self.quarantine_table.item(row, 4)
        if not id_item:
            return
        
        try:
            idx = int(id_item.text())
            items = self.quarantine_manager.list_quarantined()
            if idx >= len(items):
                return
            
            quarantine_path = list(self.quarantine_manager.quarantined_files.keys())[idx]
            lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
            
            reply = QMessageBox.question(self, lang["restore"],
                lang["restore_confirm"])
            
            if reply == QMessageBox.Yes:
                if self.quarantine_manager.restore_from_quarantine(quarantine_path):
                    QMessageBox.information(self, lang["restore"], lang["restore_success"])
                    self.load_quarantine()
                else:
                    QMessageBox.critical(self, lang.get("error", "Error"), lang["restore_error"])
        except Exception as e:
            lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
            QMessageBox.critical(self, lang.get("error", "Error"), f"{lang['restore_error']}: {str(e)}")
    
    def delete_selected(self):
        """Удаление выбранного файла"""
        selected_rows = self.quarantine_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        # Берем ID из колонки 4 (индекс для доступа)
        id_item = self.quarantine_table.item(row, 4)
        if not id_item:
            return
        
        try:
            idx = int(id_item.text())
            items = self.quarantine_manager.list_quarantined()
            if idx >= len(items):
                return
            
            quarantine_path = list(self.quarantine_manager.quarantined_files.keys())[idx]
            
            reply = QMessageBox.warning(self, lang.get("delete_forever", "Delete Forever"),
                lang.get("delete_confirm", "Are you sure you want to delete this file FOREVER?\\nThis action is irreversible!"),
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                import shutil
                if os.path.exists(quarantine_path):
                    shutil.rmtree(quarantine_path) if os.path.isdir(quarantine_path) else os.remove(quarantine_path)
                
                # Удаляем из журнала
                del self.quarantine_manager.quarantined_files[quarantine_path]
                self.quarantine_manager._save_quarantine_log()
                
                QMessageBox.information(self, lang.get("delete_success", "Deletion"), lang.get("delete_success", "File successfully deleted!"))
                self.load_quarantine()
        except Exception as e:
            QMessageBox.critical(self, lang.get("error", "Error"), f"{lang.get('deletion_error', 'Deletion error:')} {str(e)}")


class SettingsDialog(QDialog):
    """Диалог настроек приложения"""
    
    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.parent_ref = parent  # Сохраняем ссылку на родителя
        lang_key = "application_settings"
        title_text = LANGUAGES.get(parent.current_lang if parent else "Русский", LANGUAGES["Русский"]).get(lang_key, "⚙ Настройки приложения")
        self.setWindowTitle(title_text)
        self.setMinimumSize(600, 500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        
        title = QLabel(lang["application_settings"])
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Настройки анализа (тема оформления теперь только тёмная)
        analysis_group = QGroupBox(lang["analysis_settings_group"])
        analysis_layout = QVBoxLayout(analysis_group)
        
        timeout_layout = QHBoxLayout()
        timeout_label = QLabel(lang["timeout_label"])
        timeout_layout.addWidget(timeout_label)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(self.settings.get('timeout', 60))
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        analysis_layout.addLayout(timeout_layout)
        
        self.poly_check = QCheckBox(lang["poly_check"])
        self.poly_check.setChecked(self.settings.get('use_poly_default', False))
        analysis_layout.addWidget(self.poly_check)
        
        self.network_check = QCheckBox(lang["network_check"])
        self.network_check.setChecked(self.settings.get('auto_disable_network', True))
        analysis_layout.addWidget(self.network_check)
        
        layout.addWidget(analysis_group)
        
        # Кнопка закрытия
        self.btn_close_settings = QPushButton(lang["close"])
        self.btn_close_settings.setObjectName("secondaryBtn")
        self.btn_close_settings.setFixedHeight(45)
        self.btn_close_settings.clicked.connect(self.accept)
        layout.addWidget(self.btn_close_settings)
    
    def get_settings(self):
        """Получить текущие настройки"""
        return {
            'theme': 'Dark',  # Теперь только тёмная тема
            'timeout': self.timeout_spin.value(),
            'use_poly_default': self.poly_check.isChecked(),
            'auto_disable_network': self.network_check.isChecked()
        }
    
    def update_texts(self):
        """Обновить тексты при смене языка"""
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        
        # Обновляем заголовок окна
        self.setWindowTitle(lang["application_settings"])
        
        # Находим и обновляем titleLabel
        title_widgets = self.findChildren(QLabel)
        for widget in title_widgets:
            if widget.objectName() == "titleLabel":
                widget.setText(lang["application_settings"])
                break
        
        # Обновляем GroupBox
        groups = self.findChildren(QGroupBox)
        for group in groups:
            if group.title() == "Analysis Settings" or group.title() == "Настройки анализа" or group.title() == lang["analysis_settings_group"]:
                group.setTitle(lang["analysis_settings_group"])
        
        # Обновляем label timeout
        for label in self.findChildren(QLabel):
            if "timeout" in label.text().lower() or "time" in label.text().lower() or label.text().startswith("Время анализа") or label.text().startswith("Analysis Time"):
                label.setText(lang["timeout_label"])
        
        # Обновляем чекбоксы
        self.poly_check.setText(lang["poly_check"])
        self.network_check.setText(lang["network_check"])
        
        # Обновляем кнопку закрытия
        self.btn_close_settings.setText(lang["close"])


class RedSandSecureGUI(QMainWindow):
    """Главное окно приложения с навигацией между режимами"""
    
    def __init__(self):
        super().__init__()
        self.worker_thread: Optional[QThread] = None
        self.worker: Optional[QObject] = None
        self.current_report: Optional[dict] = None
        self.analysis_completed = False
        self.current_lang = "Русский"
        self.settings = {
            'timeout': 60, 'output_dir': 'reports', 'use_poly_default': False,
            'auto_disable_network': True, 'log_level': 'INFO', 'theme': 'Тёмная',
            'language': 'Русский'
        }
        self.scan_history = []
        
        # Интеграция антивируса и карантина
        self.quarantine_manager = QuarantineManager()
        
        self.setup_ui()
        self.apply_stylesheet()
        self.load_settings()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("RedSand Secure - Professional Malware Analysis")
        self.showFullScreen()
        
        # Стек для переключения между экранами
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Главный экран выбора режима
        self.main_selector = MainModeSelector(self)
        self.main_selector.mode_selected.connect(self.switch_to_mode)
        self.stack.addWidget(self.main_selector)
        
        # Экран антивируса
        self.antivirus_panel = AntivirusPanel(self)
        self.stack.addWidget(self.antivirus_panel)
        
        # Экран анализа файлов
        self.analysis_panel = AnalysisPanel(self)
        self.stack.addWidget(self.analysis_panel)
        
        # Показываем главный экран
        self.stack.setCurrentWidget(self.main_selector)
    
    def switch_to_mode(self, mode: str):
        """Переключение в выбранный режим"""
        if mode == "antivirus":
            self.stack.setCurrentWidget(self.antivirus_panel)
        elif mode == "analysis":
            self.stack.setCurrentWidget(self.analysis_panel)
    
    def show_main_menu(self):
        """Показать главное меню"""
        self.stack.setCurrentWidget(self.main_selector)
    
    def change_language(self, language: str):
        """Смена языка интерфейса"""
        self.current_lang = language
        self.settings['language'] = language
        self.save_settings()
        
        # Обновляем состояние кнопок языка на главном экране
        if hasattr(self, 'main_selector'):
            self.main_selector.btn_ru.setChecked(language == "Русский")
            self.main_selector.btn_en.setChecked(language == "English")
        
        # Обновляем тексты на всех экранах
        self.update_all_texts()
    
    def update_all_texts(self):
        """Обновить все тексты интерфейса при смене языка"""
        lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
        
        # Обновляем главный экран
        if hasattr(self, 'main_selector'):
            self.main_selector.update_texts()
        
        # Обновляем панель антивируса
        if hasattr(self, 'antivirus_panel'):
            self.antivirus_panel.update_texts()
        
        # Обновляем панель анализа
        if hasattr(self, 'analysis_panel'):
            self.analysis_panel.update_texts()
        
        # Обновляем открытые диалоги если они есть
        for dialog in self.findChildren(QDialog):
            if hasattr(dialog, 'update_texts'):
                dialog.update_texts()
    
    def open_history(self):
        """Открыть историю сканирований"""
        dialog = ScanHistoryDialog(scan_history=self.scan_history, parent=self)
        dialog.update_texts()  # Обновляем тексты при открытии
        dialog.exec_()
    
    def open_quarantine(self):
        """Открыть диалог карантина"""
        try:
            dialog = QuarantineDialog(quarantine_manager=self.quarantine_manager, parent=self)
            dialog.update_texts()  # Обновляем тексты при открытии
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть карантин:\n{str(e)}")
    
    def open_settings(self):
        """Открыть диалог настроек"""
        dialog = SettingsDialog(self.settings, self)
        dialog.update_texts()  # Обновляем тексты при открытии
        if dialog.exec_() == QDialog.Accepted:
            new_settings = dialog.get_settings()
            self.settings.update(new_settings)
            self.apply_stylesheet()
            self.save_settings()
    
    def apply_stylesheet(self):
        """Применить таблицу стилей"""
        theme_name = self.settings.get('theme', 'Тёмная')
        self.setStyleSheet(generate_stylesheet(theme_name))
    
    def load_settings(self):
        """Загрузить настройки из файла"""
        settings_file = Path('gui_settings.json')
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Обновляем только существующие ключи и сохраняем язык
                    for key, value in loaded_settings.items():
                        self.settings[key] = value
                    # Применяем загруженный язык
                    self.current_lang = self.settings.get('language', 'Русский')
                self.apply_stylesheet()
                # Обновляем все тексты после загрузки настроек
                self.update_all_texts()
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")
    
    def save_settings(self):
        """Сохранить настройки в файл"""
        settings_file = Path('gui_settings.json')
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")


def main():
    """Точка входа приложения"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = RedSandSecureGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
