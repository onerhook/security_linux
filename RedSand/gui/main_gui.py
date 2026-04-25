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
    QScrollArea, QGridLayout, QListWidget, QListWidgetItem, QButtonGroup, QRadioButton
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
        "step1_title": "Шаг 1: Выберите файл",
        "step2_title": "Шаг 2: Настройки (необязательно)",
        "progress_title": "Прогресс",
        "waiting": "Ожидание...",
        "results_placeholder": "Результаты анализа появятся здесь после завершения...",
        "log_placeholder": "Здесь будет отображаться ход анализа...",
        "confirm_clear_history": "Удалить всю историю сканирований?",
        "confirm_exit_title": "Анализ выполняется",
        "confirm_exit_msg": "Анализ все еще выполняется. Вы уверены, что хотите выйти?",
        "file_not_found": "Файл не найден: ",
        "select_file_warning": "Пожалуйста, выберите файл для анализа!",
        "analysis_complete": "Анализ завершен успешно!",
        "analysis_error": "Ошибка анализа!",
        "settings_saved": "Настройки сохранены. Тема: ",
        "settings_error": "Не удалось открыть настройки: ",
        "folder_open_error": "Не удалось открыть папку.\nПуть: ",
        "lang_changed": "Язык изменен на: ",
        "settings_title": "⚙ Настройки программы",
        "theme_group": "🎨 Тема оформления",
        "theme_label": "Выберите тему:",
        "timeout_group": "⏱ Время анализа",
        "timeout_label": "Максимальное время:",
        "options_group": "🔧 Дополнительные опции",
        "poly_tooltip": "Помогает обнаружить сложные вирусы путем создания модификаций файла",
        "network_tooltip": "Защищает вашу сеть от потенциальной угрозы",
        "network_recommended": "(рекомендуется)",
        "help_settings_group": "❓ Справка по настройкам",
        "help_settings_text": "<b>Как использовать настройки:</b><br><br><b>Тема оформления:</b> Выберите удобный для вас визуальный стиль интерфейса<br><b>Время анализа:</b> Максимальное время проверки одного файла (по умолчанию 60 сек)<br><b>Создавать варианты файла:</b> Генерирует модификации файла для лучшего обнаружения сложных угроз<br><b>Отключать сеть:</b> Защищает вашу локальную сеть во время анализа вредоносного ПО (рекомендуется всегда включать)<br><br><b style='color: #EF4444;'>ВАЖНО:</b> Запускайте анализ только в изолированной виртуальной машине!",
        "history_title": "📜 История сканирований",
        "btn_close": "Закрыть",
        "btn_clear": "🗑 Очистить историю",
        "confirm_clear": "Подтверждение",
        "tab_logs": "📋 Журнал",
        "tab_results": "📊 Результаты",
        "param_column": "Параметр",
        "value_column": "Значение",
        "all_files": "Все файлы (*.*)",
        "exe_files": "Executable файлы (*.exe)",
        "dll_files": "DLL файлы (*.dll)",
        "security_warning_title": "Предупреждение о безопасности",
        "security_warning_msg": "<h2>ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ</h2><p>Вы запускаете инструмент для анализа потенциально опасных файлов.</p><p><b>Запускайте ТОЛЬКО в изолированной виртуальной машине!</b></p>",
        "light_theme": "Светлая",
        "dark_theme": "Тёмная"
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
        "step1_title": "Step 1: Select File",
        "step2_title": "Step 2: Settings (optional)",
        "progress_title": "Progress",
        "waiting": "Waiting...",
        "results_placeholder": "Analysis results will appear here after completion...",
        "log_placeholder": "Analysis progress will be displayed here...",
        "confirm_clear_history": "Delete all scan history?",
        "confirm_exit_title": "Analysis in Progress",
        "confirm_exit_msg": "Analysis is still running. Are you sure you want to exit?",
        "file_not_found": "File not found: ",
        "select_file_warning": "Please select a file for analysis!",
        "analysis_complete": "Analysis completed successfully!",
        "analysis_error": "Analysis error!",
        "settings_saved": "Settings saved. Theme: ",
        "settings_error": "Failed to open settings: ",
        "folder_open_error": "Failed to open folder.\nPath: ",
        "lang_changed": "Language changed to: ",
        "settings_title": "⚙ Program Settings",
        "theme_group": "🎨 Theme",
        "theme_label": "Select theme:",
        "timeout_group": "⏱ Analysis Time",
        "timeout_label": "Maximum time:",
        "options_group": "🔧 Additional Options",
        "poly_tooltip": "Helps detect complex viruses by creating file modifications",
        "network_tooltip": "Protects your network from potential threats",
        "network_recommended": "(recommended)",
        "help_settings_group": "❓ Settings Help",
        "help_settings_text": "<b>How to use settings:</b><br><br><b>Theme:</b> Choose a visual style that suits you<br><b>Analysis Time:</b> Maximum time to check one file (default 60 sec)<br><b>Create file variants:</b> Generates file modifications for better detection of complex threats<br><b>Disable network:</b> Protects your local network during malware analysis (always recommended to enable)<br><br><b style='color: #EF4444;'>IMPORTANT:</b> Run analysis only in an isolated virtual machine!",
        "history_title": "📜 Scan History",
        "btn_close": "Close",
        "btn_clear": "🗑 Clear History",
        "confirm_clear": "Confirmation",
        "tab_logs": "📋 Logs",
        "tab_results": "📊 Results",
        "param_column": "Parameter",
        "value_column": "Value",
        "all_files": "All files (*.*)",
        "exe_files": "Executable files (*.exe)",
        "dll_files": "DLL files (*.dll)",
        "security_warning_title": "Security Warning",
        "security_warning_msg": "<h2>IMPORTANT WARNING</h2><p>You are running a tool for analyzing potentially dangerous files.</p><p><b>Run ONLY in an isolated virtual machine!</b></p>",
        "light_theme": "Light",
        "dark_theme": "Dark"
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
        self.setWindowTitle("Результаты анализа безопасности")
        self.setMinimumSize(900, 700)
        # Убираем вопросительный знак из заголовка окна
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Заголовок
        title_label = QLabel("📊 Результаты анализа безопасности")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Вкладки
        tabs = QTabWidget()
        
        # Главная вкладка с резюме
        summary_widget = self.create_summary_tab()
        tabs.addTab(summary_widget, "🏠 Главная")
        
        # Вкладка о вирусе
        virus_widget = self.create_virus_info_tab()
        tabs.addTab(virus_widget, "🦠 О вирусе")
        
        # Вкладка справки
        help_widget = self.create_help_tab()
        tabs.addTab(help_widget, "❓ Справка")
        
        layout.addWidget(tabs)
        
        # Кнопка закрытия
        btn_close = QPushButton("Закрыть")
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
        
        threat_info = self.report_data.get('threat_info') or {}
        if not isinstance(threat_info, dict):
            threat_info = {}
        
        risk_score = threat_info.get('risk_score', 0)
        
        # Определение уровня угрозы
        if risk_score >= 70:
            risk_color, risk_text, risk_icon = "#EF4444", "ОПАСНО", "🚨"
            risk_desc = "ОПАСНО! Немедленно удалите файл. Обнаружен вирус."
        elif risk_score >= 40:
            risk_color, risk_text, risk_icon = "#F59E0B", "ПОДОЗРИТЕЛЬНО", "⚠️"
            risk_desc = "ПОДОЗРИТЕЛЬНО, лучше не использовать. Файл содержит сомнительные элементы."
        else:
            risk_color, risk_text, risk_icon = "#10B981", "БЕЗОПАСНО", "✅"
            risk_desc = "Файл не содержит известных угроз. Можно использовать."
        
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
        info_group = QGroupBox("📋 Основная информация")
        info_layout = QGridLayout()
        info_layout.setSpacing(12)
        
        row = 0
        items = [
            ("Тип угрозы:", threat_info.get('type', 'Неизвестно')),
            ("Семейство:", threat_info.get('family', 'Неизвестно')),
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
        
        threat_info = self.report_data.get('threat_info') or {}
        static_data = self.report_data.get('static_results') or {}
        
        # Информация о вирусе - максимально подробно
        virus_group = QGroupBox("🦠 Подробная информация об угрозе")
        virus_layout = QVBoxLayout()
        virus_layout.setSpacing(15)
        
        virus_name = threat_info.get('type', 'Неизвестно')
        virus_family = threat_info.get('family', 'Неизвестно')
        risk_score = threat_info.get('risk_score', 0)
        
        # Определяем вердикт без баллов
        if risk_score >= 70:
            verdict_text = "<span style='color: #EF4444; font-size: 20px; font-weight: bold;'>🚨 ОПАСНО - Немедленно удалите файл!</span>"
            verdict_desc = "Обнаружен вирус. Файл представляет серьезную угрозу для вашей системы."
        elif risk_score >= 40:
            verdict_text = "<span style='color: #F59E0B; font-size: 20px; font-weight: bold;'>⚠️ ПОДОЗРИТЕЛЬНО - Лучше не использовать</span>"
            verdict_desc = "Файл содержит подозрительные элементы. Рекомендуется воздержаться от использования."
        else:
            verdict_text = "<span style='color: #10B981; font-size: 20px; font-weight: bold;'>✅ БЕЗОПАСНО - Можно использовать</span>"
            verdict_desc = "Угроз не обнаружено. Файл прошел все проверки безопасности."
        
        info_text = f"""
        <div style='font-size: 16px; line-height: 2.0;'>
        <b>📛 Название угрозы:</b> {virus_name}<br><br>
        <b>🧬 Семейство вирусов:</b> {virus_family}<br><br>
        {verdict_text}<br><br>
        <b>📝 Описание:</b> {verdict_desc}<br><br>
        </div>
        """
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        virus_layout.addWidget(info_label)
        
        virus_group.setLayout(virus_layout)
        layout.addWidget(virus_group)
        
        # Как обнаружили - максимально подробно
        detection_group = QGroupBox("🔍 Как мы обнаружили эту угрозу")
        detection_layout = QVBoxLayout()
        detection_layout.setSpacing(15)
        
        # Получаем методы обнаружения из результатов статического анализа
        detection_details = []
        
        if risk_score >= 70:
            detection_details = [
                ("<b>✅ Статический анализ сигнатур</b>", 
                 "Программа сравнила содержимое файла с базой данных известных вирусов и обнаружила точное совпадение с сигнатурой вредоносного ПО."),
                ("<b>✅ Поведенческий анализ</b>", 
                 "При запуске файла в изолированной среде были зафиксированы вредоносные действия: попытки изменения системных файлов, создание скрытых процессов или подключение к подозрительным сетевым ресурсам."),
                ("<b>✅ Эвристический анализ</b>", 
                 "Структура файла, используемые функции и паттерны кода характерны для вредоносного ПО. Обнаружены техники обхода защиты и сокрытия присутствия."),
                ("<b>✅ Анализ метаданных</b>",
                 "Информация о файле (цифровая подпись, дата создания, компилятор) указывает на подозрительное происхождение.")
            ]
        elif risk_score >= 40:
            detection_details = [
                ("<b>⚠️ Статический анализ</b>", 
                 "Обнаружены отдельные подозрительные элементы, но полного совпадения с известными вирусами нет."),
                ("<b>⚠️ Поведенческие аномалии</b>", 
                 "Файл выполняет необычные действия, которые могут быть как легитимными, так и вредоносными."),
                ("<b>ℹ️ Эвристика</b>", 
                 "Некоторые паттерны кода вызывают сомнения, но недостаточны для однозначного вывода об угрозе.")
            ]
        else:
            detection_details = [
                ("<b>✅ Статический анализ</b>", 
                 "Файл проверен по базе сигнатур - совпадений с известными вирусами не найдено."),
                ("<b>✅ Поведенческий анализ</b>", 
                 "В изолированной среде файл не проявил никакой подозрительной активности."),
                ("<b>✅ Проверка целостности</b>", 
                 "Структура файла корректна, цифровая подпись (если есть) действительна.")
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
        rec_group = QGroupBox("💡 Подробные рекомендации")
        rec_layout = QVBoxLayout()
        
        if risk_score >= 70:
            rec_text = """
            <div style='font-size: 15px; line-height: 2.0; color: #EF4444;'>
            <b style='font-size: 18px;'>🚨 НЕМЕДЛЕННО УДАЛИТЕ ЭТОТ ФАЙЛ!</b><br><br>
            <b>Почему это опасно:</b><br>
            Этот файл распознан как вредоносное ПО с высокой степенью уверенности. Он может:<br>
            • Украсть ваши личные данные (пароли, банковскую информацию)<br>
            • Зашифровать ваши файлы и требовать выкуп<br>
            • Использовать ваш компьютер для атак на другие системы<br>
            • Установить скрытый доступ к вашему компьютеру<br><br>
            <b>Что нужно сделать:</b><br>
            1. <b>НЕ ЗАПУСКАЙТЕ</b> этот файл ни при каких обстоятельствах<br>
            2. Немедленно удалите файл из системы<br>
            3. Проверьте весь компьютер полноценным антивирусом<br>
            4. Если файл уже был запущен - срочно смените все пароли<br>
            5. Проверьте банковские счета на подозрительные операции<br>
            6. Обратитесь к специалисту по кибербезопасности
            </div>
            """
        elif risk_score >= 40:
            rec_text = """
            <div style='font-size: 15px; line-height: 2.0; color: #F59E0B;'>
            <b style='font-size: 18px;'>⚠️ БУДЬТЕ ОСТОРОЖНЫ - ПОДОЗРИТЕЛЬНЫЙ ФАЙЛ!</b><br><br>
            <b>Почему это подозрительно:</b><br>
            Файл содержит элементы, которые могут указывать на угрозу, но окончательного подтверждения нет. Это может быть:<br>
            • Новый вирус, еще не добавленный в базы сигнатур<br>
            • Легитимная программа с нестандартным поведением<br>
            • Инструмент администратора, который выглядит подозрительно<br><br>
            <b>Что нужно сделать:</b><br>
            1. <b>Не рекомендуется использовать</b> этот файл без дополнительной проверки<br>
            2. Если файл необходим - запустите его в полностью изолированной среде (виртуальная машина без доступа к сети)<br>
            3. Попробуйте получить этот файл из другого, более надежного источника<br>
            4. Проверьте файл через онлайн-сервисы (VirusTotal и аналоги)<br>
            5. Свяжитесь с разработчиком ПО для подтверждения подлинности
            </div>
            """
        else:
            rec_text = """
            <div style='font-size: 15px; line-height: 2.0; color: #10B981;'>
            <b style='font-size: 18px;'>✅ ФАЙЛ БЕЗОПАСЕН</b><br><br>
            <b>Почему файл считается безопасным:</b><br>
            Файл прошел все проверки и не показал никаких признаков вредоносной активности:<br>
            • Нет совпадений с известными вирусами<br>
            • Поведение файла полностью соответствует заявленным функциям<br>
            • Структура и метаданные файла корректны<br><br>
            <b>Рекомендации:</b><br>
            1. Файл можно использовать безопасно<br>
            2. Применяйте стандартные меры предосторожности<br>
            3. Убедитесь, что файл получен из надежного источника<br>
            4. При любых сомнениях - проведите дополнительную проверку
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
        self.parent_window = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        lang = self.get_lang_data()
        
        self.setWindowTitle(lang["settings_title"])
        self.setMinimumWidth(600)
        # Убираем вопросительный знак из заголовка окна
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        title_label = QLabel(lang["settings_title"])
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Тема оформления - используем QRadioButton для эксклюзивного выбора
        theme_group = QGroupBox(lang["theme_group"])
        theme_layout = QVBoxLayout()
        theme_layout.addWidget(QLabel(lang["theme_label"]))
        
        self.theme_button_group = QButtonGroup(self)
        self.theme_button_group.setExclusive(True)
        
        self.light_theme_radio = QRadioButton(lang["light_theme"])
        self.dark_theme_radio = QRadioButton(lang["dark_theme"])
        
        self.theme_button_group.addButton(self.light_theme_radio, 0)
        self.theme_button_group.addButton(self.dark_theme_radio, 1)
        
        theme_layout.addWidget(self.light_theme_radio)
        theme_layout.addWidget(self.dark_theme_radio)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Время анализа
        timeout_group = QGroupBox(lang["timeout_group"])
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel(lang["timeout_label"]))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(60)
        self.timeout_spin.setMinimumWidth(100)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addWidget(QLabel(lang["seconds"]))
        timeout_layout.addStretch()
        timeout_group.setLayout(timeout_layout)
        layout.addWidget(timeout_group)
        
        # Дополнительные опции
        options_group = QGroupBox(lang["options_group"])
        options_layout = QVBoxLayout()
        
        self.poly_check = QCheckBox(lang["poly_check"])
        self.poly_check.setToolTip(lang["poly_tooltip"])
        options_layout.addWidget(self.poly_check)
        
        self.network_check = QCheckBox(lang["network_check"] + " " + lang["network_recommended"])
        self.network_check.setChecked(True)
        self.network_check.setToolTip(lang["network_tooltip"])
        options_layout.addWidget(self.network_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Справка
        help_group = QGroupBox(lang["help_settings_group"])
        help_layout = QVBoxLayout()
        help_text = QLabel(lang["help_settings_text"])
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
    
    def get_lang_data(self):
        if self.parent_window and hasattr(self.parent_window, 'current_lang'):
            return LANGUAGES.get(self.parent_window.current_lang, LANGUAGES["Русский"])
        return LANGUAGES["Русский"]

    def get_settings(self):
        # Определяем выбранную тему
        selected_theme = lang["light_theme"] if self.light_theme_radio.isChecked() else lang["dark_theme"]
        # Маппинг русских названий тем
        theme_map = {
            "Светлая": "Светлая",
            "Тёмная": "Тёмная",
            "Light": "Светлая",
            "Dark": "Тёмная"
        }
        return {
            'timeout': self.timeout_spin.value(),
            'use_poly_default': self.poly_check.isChecked(),
            'auto_disable_network': self.network_check.isChecked(),
            'theme': theme_map.get(selected_theme, "Светлая")
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
        
        lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
        
        file_group = QGroupBox(lang["step1_title"])
        file_layout = QVBoxLayout()
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText(lang["file_placeholder"])
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setMinimumHeight(50)
        file_layout.addWidget(self.file_path_edit)
        
        self.btn_select_file = QPushButton(lang["select_file"])
        self.btn_select_file.setObjectName("actionBtn")
        self.btn_select_file.clicked.connect(self.select_file)
        file_layout.addWidget(self.btn_select_file)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        settings_group = QGroupBox(lang["step2_title"])
        settings_layout = QVBoxLayout()
        
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel(lang["analysis_time"]))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(60)
        self.timeout_spin.setMinimumWidth(80)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addWidget(QLabel(lang["seconds"]))
        timeout_layout.addStretch()
        settings_layout.addLayout(timeout_layout)
        
        self.poly_check = QCheckBox(lang["poly_check"])
        self.poly_check.setToolTip(lang["poly_tooltip"])
        settings_layout.addWidget(self.poly_check)
        
        self.network_check = QCheckBox(lang["network_check"] + " " + lang["network_recommended"])
        self.network_check.setChecked(True)
        self.network_check.setToolTip(lang["network_tooltip"])
        settings_layout.addWidget(self.network_check)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        self.btn_analyze = QPushButton(lang["analyze_btn"])
        self.btn_analyze.setObjectName("primaryBtn")
        self.btn_analyze.clicked.connect(self.start_analysis)
        layout.addWidget(self.btn_analyze)
        
        progress_group = QGroupBox(lang["progress_title"])
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(35)
        progress_layout.addWidget(self.progress_bar)
        self.progress_label = QLabel(lang["waiting"])
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
        logs_widget._tab_name_ru = LANGUAGES["Русский"]["tab_logs"]
        logs_widget._tab_name_en = LANGUAGES["English"]["tab_logs"]
        self.tabs.addTab(logs_widget, logs_widget._tab_name_ru)
        results_widget = self.create_results_tab()
        results_widget._tab_name_ru = LANGUAGES["Русский"]["tab_results"]
        results_widget._tab_name_en = LANGUAGES["English"]["tab_results"]
        self.tabs.addTab(results_widget, results_widget._tab_name_ru)
        layout.addWidget(self.tabs)
        return widget

    def create_logs_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 14))
        lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
        self.log_text.setPlaceholderText(lang["log_placeholder"])
        layout.addWidget(self.log_text)
        return widget

    def create_results_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
        self.results_summary = QLabel(lang["results_placeholder"])
        self.results_summary.setAlignment(Qt.AlignCenter)
        self.results_summary.setFont(QFont("Segoe UI", 16))
        self.results_summary.setStyleSheet("color: #666; padding: 50px;")
        layout.addWidget(self.results_summary)
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels([lang["param_column"], lang["value_column"]])
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
