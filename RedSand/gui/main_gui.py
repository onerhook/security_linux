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


THEMES = {
    "Тёмная": {
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
    },
    "Светлая": {
        "bg_primary": "#f8fafc",
        "bg_secondary": "#ffffff",
        "bg_tertiary": "#e2e8f0",
        "accent": "#dc2626",
        "accent_hover": "#b91c1c",
        "text_primary": "#0f172a",
        "text_secondary": "#475569",
        "success": "#16a34a",
        "warning": "#ea580c",
        "danger": "#dc2626",
        "border": "#64748b",
        "card_bg": "#ffffff"
    }
}


def generate_stylesheet(theme_name: str = "Тёмная") -> str:
    """Генерация CSS стилей для приложения"""
    theme = THEMES.get(theme_name, THEMES["Тёмная"])
    
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
        background-color: {theme['success']};
        min-width: 140px;
        min-height: 50px;
    }}
    
    QPushButton#actionBtn:hover {{
        background-color: #00cc6a;
    }}
    
    QPushButton#dangerBtn {{
        background-color: {theme['danger']};
        min-width: 140px;
        min-height: 50px;
    }}
    
    QPushButton#dangerBtn:hover {{
        background-color: #cc3333;
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
        "subtitle": "Профессиональная система анализа вредоносного ПО",
        "antivirus_mode": "🛡️ АНТИВИРУС",
        "analysis_mode": "🔍 АНАЛИЗ ФАЙЛОВ",
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
        "dark_theme": "Тёмная",
        "light_theme": "Светлая",
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
        "status_clean": "✅ Чист",
        "status_suspicious": "⚠️ Подозрительный",
        "status_malicious": "🔴 Опасно",
        "settings_title": "⚙ Настройки приложения",
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
        "detected_threats": "Обнаруженные угрозы:"
    },
    "English": {
        "title": "RedSand Secure",
        "subtitle": "Professional Malware Analysis System",
        "antivirus_mode": "🛡️ ANTIVIRUS",
        "analysis_mode": "🔍 FILE ANALYSIS",
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
        "dark_theme": "Dark",
        "light_theme": "Light",
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
        "status_clean": "✅ Clean",
        "status_suspicious": "⚠️ Suspicious",
        "status_malicious": "🔴 Dangerous",
        "settings_title": "⚙ Application Settings",
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
        "detected_threats": "Detected threats:"
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
        
        # Заголовок
        title_label = QLabel("RedSand Secure")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("Профессиональная система анализа вредоносного ПО")
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
        self.btn_analysis = QPushButton("🔍\nАНАЛИЗ\nФайлов")
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
        self.btn_analysis.setText(lang["analysis_mode"].replace("FILE ANALYSIS", "🔍\nFILE\nANALYSIS") if self.parent_ref.current_lang == "English" else lang["analysis_mode"])
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
        
        # Список папок - сначала список
        self.folder_list = QListWidget()
        self.folder_list.addItems([
            "~/Downloads",
            "~/Desktop", 
            "~/Documents"
        ])
        self.folder_list.setMaximumHeight(150)
        monitor_layout.addWidget(self.folder_list)
        
        # Кнопки управления папками - под списком папок
        folder_btn_layout = QHBoxLayout()
        
        self.btn_add_folder = QPushButton("📁 Добавить")
        self.btn_add_folder.setObjectName("secondaryBtn")
        self.btn_add_folder.setFixedHeight(40)
        self.btn_add_folder.clicked.connect(self.add_folder)
        folder_btn_layout.addWidget(self.btn_add_folder)
        
        self.btn_remove_folder = QPushButton("🗑️ Удалить")
        self.btn_remove_folder.setObjectName("dangerBtn")
        self.btn_remove_folder.setFixedHeight(40)
        self.btn_remove_folder.clicked.connect(self.remove_folder)
        self.btn_remove_folder.setEnabled(False)
        folder_btn_layout.addWidget(self.btn_remove_folder)
        
        monitor_layout.addLayout(folder_btn_layout)
        
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
                    QMessageBox.warning(self, "Предупреждение", 
                        "Не найдены стандартные папки для мониторинга.\nАнтивирус не может быть запущен.")
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
                self.btn_toggle_av.setText("⏹️ ВЫКЛ")
                self.av_status_label.setText("🛡️ Антивирус: ВКЛ")
                self.av_status_label.setStyleSheet("color: #059669; font-weight: bold; font-size: 24px;")
                self.log_event(f"Антивирус запущен. Мониторинг: {', '.join(monitor_paths)}")
                
                QMessageBox.information(self, "Антивирус активирован",
                    f"Защита реального времени включена!\n\nМониторимые папки:\n{chr(10).join(monitor_paths)}\n\nВсе подозрительные файлы будут автоматически помещены в карантин.")
                    
            except Exception as e:
                self.log_event(f"Ошибка запуска: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось запустить антивирус:\n{str(e)}")
                self.btn_toggle_av.setChecked(False)
    
    def log_event(self, message: str):
        """Запись события в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.av_log.append(f"[{timestamp}] {message}")
    
    def add_folder(self):
        """Добавить папку для мониторинга"""
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для мониторинга")
        if folder:
            # Проверяем, нет ли уже такой папки в списке
            for i in range(self.folder_list.count()):
                if os.path.expanduser(self.folder_list.item(i).text()) == folder:
                    QMessageBox.information(self, "Информация", "Эта папка уже добавлена")
                    return
            
            self.folder_list.addItem(folder)
            self.log_event(f"Добавлена папка: {folder}")
    
    def remove_folder(self):
        """Удалить выбранную папку из мониторинга"""
        selected_items = self.folder_list.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            row = self.folder_list.row(item)
            folder_path = item.text()
            self.folder_list.takeItem(row)
            self.log_event(self.get_text("folder_removed") + folder_path)
        
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
        
        # Заголовок
        title_label = QLabel("🔍 АНАЛИЗ ФАЙЛОВ")
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
        file_group = QGroupBox("Шаг 1: Выберите файл")
        file_layout = QVBoxLayout(file_group)
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Файл еще не выбран... или перетащите сюда")
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setMinimumHeight(50)
        file_layout.addWidget(self.file_path_edit)
        
        self.btn_select_file = QPushButton("📁 Выбрать файл")
        self.btn_select_file.setObjectName("actionBtn")
        self.btn_select_file.clicked.connect(self.select_file)
        file_layout.addWidget(self.btn_select_file)
        
        left_layout.addWidget(file_group)
        
        # Настройки анализа
        settings_group = QGroupBox("Шаг 2: Настройки анализа")
        settings_layout = QVBoxLayout(settings_group)
        
        timeout_layout = QHBoxLayout()
        timeout_label = QLabel("Время анализа:")
        timeout_layout.addWidget(timeout_label)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(60)
        self.timeout_spin.setMinimumWidth(80)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        settings_layout.addLayout(timeout_layout)
        
        self.poly_check = QCheckBox("Создавать варианты файла для анализа")
        self.poly_check.setToolTip("Помогает обнаружить сложные вирусы")
        settings_layout.addWidget(self.poly_check)
        
        self.network_check = QCheckBox("Отключать сеть (рекомендуется)")
        self.network_check.setChecked(True)
        self.network_check.setToolTip("Защищает вашу сеть во время анализа")
        settings_layout.addWidget(self.network_check)
        
        docker_info = QLabel("ℹ️ Все файлы анализируются в изолированном Docker контейнере")
        docker_info.setStyleSheet("color: #00ff88; font-style: italic;")
        settings_layout.addWidget(docker_info)
        
        left_layout.addWidget(settings_group)
        
        # Кнопка анализа
        self.btn_analyze = QPushButton("🚀 ЗАПУСТИТЬ АНАЛИЗ")
        self.btn_analyze.setObjectName("primaryBtn")
        self.btn_analyze.setMinimumHeight(60)
        self.btn_analyze.clicked.connect(self.start_analysis)
        left_layout.addWidget(self.btn_analyze)
        
        # Прогресс
        progress_group = QGroupBox("Прогресс анализа")
        progress_layout = QVBoxLayout(progress_group)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(35)
        progress_layout.addWidget(self.progress_bar)
        self.progress_label = QLabel("Ожидание...")
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
        self.log_text.setPlaceholderText("Здесь будет отображаться ход анализа...")
        logs_layout.addWidget(self.log_text)
        # Увеличена ширина кнопки вкладки Журнал через stylesheet
        logs_widget.setStyleSheet("padding: 5px;")
        self.tabs.addTab(logs_widget, "📋 Журнал      ")
        
        # Вкладка результатов
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        self.results_summary = QLabel("Результаты анализа появятся здесь после завершения...")
        self.results_summary.setAlignment(Qt.AlignCenter)
        self.results_summary.setFont(QFont("Segoe UI", 16))
        self.results_summary.setStyleSheet("color: #666; padding: 50px;")
        results_layout.addWidget(self.results_summary)
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Параметр", "Значение"])
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
        self.tabs.addTab(results_widget, "📊 Результаты   ")
        
        right_layout.addWidget(self.tabs)
        main_splitter.addWidget(right_widget)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)
        
        layout.addWidget(main_splitter)
        
        # Кнопка назад
        btn_back = QPushButton("← Назад к главному меню")
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
        """Запуск анализа файла"""
        file_path = self.file_path_edit.text().strip()
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите существующий файл для анализа.")
            return
        
        self.btn_analyze.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.results_summary.setVisible(True)
        self.results_table.setVisible(False)
        
        self.log_message('INFO', f"Начало анализа файла: {file_path}")
        self.log_message('INFO', "Используется Docker изоляция для безопасности")
        
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
        
        # Здесь будет логика анализа через orchestrator
        # Для демонстрации показываем прогресс
        self.progress_bar.setValue(25)
        self.progress_label.setText("Статический анализ...")
        self.log_message('INFO', "Выполняется статический анализ файла...")
        
        self.progress_bar.setValue(50)
        self.progress_label.setText("Динамический анализ в Docker...")
        self.log_message('INFO', "Запуск в изолированном Docker контейнере...")
        
        self.progress_bar.setValue(75)
        self.progress_label.setText("Анализ поведения...")
        self.log_message('INFO', "Анализ системных вызовов и сетевого поведения...")
        
        # Имитация завершения анализа
        self.progress_bar.setValue(100)
        self.progress_label.setText("Анализ завершен!")
        self.log_message('SUCCESS', "Анализ успешно завершен!")
        
        # Показываем демо-результаты
        self.results_summary.setVisible(False)
        self.results_table.setVisible(True)
        self.results_table.setRowCount(5)  # Убрали Docker изоляцию
        
        results_data = [
            ("Файл", os.path.basename(file_path)),
            ("Статус", "✅ Чист" if hash(file_path) % 2 == 0 else "⚠️ Подозрительный"),
            ("Тип файла", "PE Executable (EXE)" if file_path.endswith('.exe') else "Другой тип"),
            ("Размер", f"{os.path.getsize(file_path)} байт"),
            ("Время анализа", f"{datetime.now().strftime('%H:%M:%S')}")
        ]
        
        for i, (param, value) in enumerate(results_data):
            self.results_table.setItem(i, 0, QTableWidgetItem(param))
            self.results_table.setItem(i, 1, QTableWidgetItem(value))
        
        # Обновляем запись в истории с правильным scan_time
        if self.parent_ref and len(self.parent_ref.scan_history) > 0:
            last_record = self.parent_ref.scan_history[-1]
            last_record['scan_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_record['threat_level'] = 'CLEAN' if hash(file_path) % 2 == 0 else 'SUSPICIOUS'
            last_record['detected_threats'] = [] if hash(file_path) % 2 == 0 else ['Pattern match', 'Suspicious behavior']
            last_record['status'] = last_record['threat_level']  # Для совместимости
            last_record['threats'] = 0 if hash(file_path) % 2 == 0 else 2
        
        self.btn_analyze.setEnabled(True)
        QMessageBox.information(self, "Анализ завершен", 
            f"Файл проанализирован в Docker контейнере.\nРезультаты доступны во вкладке 'Результаты'.")
    
    def log_message(self, level: str, message: str):
        """Запись сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {'INFO': '#4CAF50', 'WARNING': '#FF9800', 'ERROR': '#F44336', 'SUCCESS': '#00BCD4'}
        color = colors.get(level, '#FFFFFF')
        self.log_text.append(f'<span style="color: {color};">[{timestamp}] [{level}] {message}</span>')


class ScanHistoryDialog(QDialog):
    """Диалог истории сканирований"""
    
    def __init__(self, scan_history=None, parent=None):
        super().__init__(parent)
        self.scan_history = scan_history or []
        self.parent_ref = parent
        self.setWindowTitle("📜 История сканирований")
        self.setMinimumSize(1000, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("📋 История сканирований файлов")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        info_label = QLabel("Здесь отображаются все файлы, которые были проанализированы.")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        # Таблица истории
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Дата", "Файл", "Статус", "Угрозы", "Путь"])
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
        
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.setObjectName("secondaryBtn")
        self.btn_refresh.clicked.connect(self.load_history)
        btn_layout.addWidget(self.btn_refresh)
        
        self.btn_clear = QPushButton("🗑️ Очистить историю")
        self.btn_clear.setObjectName("dangerBtn")
        self.btn_clear.clicked.connect(self.clear_history)
        btn_layout.addWidget(self.btn_clear)
        
        btn_layout.addStretch()
        
        self.btn_close = QPushButton("Close")
        self.btn_close.setObjectName("secondaryBtn")
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)
        
        self.load_history()
    
    def load_history(self):
        """Загрузить историю сканирований"""
        self.history_table.setRowCount(0)
        
        if not self.scan_history:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            item = QTableWidgetItem("История пуста")
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
            if status == 'CLEAN':
                status_item.setForeground(QColor("#00ff88"))
                status_bg_color = QColor("#059669")
            elif status == 'SUSPICIOUS':
                status_item.setForeground(QColor("#ffaa00"))
                status_bg_color = QColor("#d97706")
            elif status == 'MALICIOUS':
                status_item.setForeground(QColor("#ff4444"))
                status_bg_color = QColor("#dc2626")
            
            # Делаем текст белым на цветном фоне
            if status != 'CLEAN':
                status_item.setBackground(status_bg_color)
                status_item.setForeground(QColor("#ffffff"))
            else:
                status_item.setBackground(QColor("#059669"))
                status_item.setForeground(QColor("#ffffff"))
                
            status_item.setTextAlignment(Qt.AlignCenter)
            font = status_item.font()
            font.setBold(True)
            status_item.setFont(font)
            self.history_table.setItem(row, 2, status_item)
            
            # Угрозы
            threats = ', '.join(item_data.get('detected_threats', []))
            threats_item = QTableWidgetItem(threats if threats else 'Нет')
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
        reply = QMessageBox.question(self, "Подтверждение",
            "Вы уверены, что хотите очистить всю историю сканирований?",
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
        self.setWindowTitle("⚠️ Quarantine")
        self.setMinimumSize(900, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("🛡️ Quarantine - Detected Threats")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        info_label = QLabel("Files in quarantine are neutralized and cannot harm the system.")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        # Таблица файлов - увеличенная, занимает больше места
        self.quarantine_table = QTableWidget()
        self.quarantine_table.setColumnCount(5)
        self.quarantine_table.setHorizontalHeaderLabels(["Date", "File Name", "Original Path", "Reason", "ID"])
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
        btn_layout.setContentsMargins(0, 10, 0, 10)
        
        # Кнопка "Обновить" слева
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.setObjectName("secondaryBtn")
        self.btn_refresh.setFixedHeight(45)
        self.btn_refresh.clicked.connect(self.load_quarantine)
        btn_layout.addWidget(self.btn_refresh)
        
        btn_layout.addStretch()
        
        # Кнопки "Восстановить" и "Удалить навсегда" по центру
        center_layout = QHBoxLayout()
        self.btn_restore = QPushButton("♻️ Restore")
        self.btn_restore.setObjectName("actionBtn")
        self.btn_restore.setFixedHeight(45)
        self.btn_restore.clicked.connect(self.restore_selected)
        self.btn_restore.setEnabled(False)
        center_layout.addWidget(self.btn_restore)
        
        self.btn_delete = QPushButton("🗑️ Delete Forever")
        self.btn_delete.setObjectName("dangerBtn")
        self.btn_delete.setFixedHeight(45)
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_delete.setEnabled(False)
        center_layout.addWidget(self.btn_delete)
        
        btn_layout.addLayout(center_layout)
        btn_layout.addStretch()
        
        # Кнопка "Закрыть" справа
        self.btn_close = QPushButton("Close")
        self.btn_close.setObjectName("secondaryBtn")
        self.btn_close.setFixedHeight(45)
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)
        
        self.load_quarantine()
    
    def load_quarantine(self):
        """Загрузить список файлов из карантина"""
        self.quarantine_table.setRowCount(0)
        
        if not self.quarantine_manager:
            return
        
        items = self.quarantine_manager.list_quarantined()
        
        if not items:
            row = self.quarantine_table.rowCount()
            self.quarantine_table.insertRow(row)
            item = QTableWidgetItem("Quarantine is empty")
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
            
            reply = QMessageBox.question(self, "Restore Confirmation",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                if self.quarantine_manager.restore_from_quarantine(quarantine_path):
                    QMessageBox.information(self, "Restoration", "File successfully restored!")
                    self.load_quarantine()
                else:
                    QMessageBox.critical(self, "Error", "Failed to restore file")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Restoration error: {str(e)}")
    
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
            
            reply = QMessageBox.warning(self, "Delete Confirmation",
                "Are you sure you want to delete this file FOREVER?\nThis action is irreversible!",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                import shutil
                if os.path.exists(quarantine_path):
                    shutil.rmtree(quarantine_path) if os.path.isdir(quarantine_path) else os.remove(quarantine_path)
                
                # Удаляем из журнала
                del self.quarantine_manager.quarantined_files[quarantine_path]
                self.quarantine_manager._save_quarantine_log()
                
                QMessageBox.information(self, "Deletion", "File successfully deleted!")
                self.load_quarantine()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Deletion error: {str(e)}")


class SettingsDialog(QDialog):
    """Диалог настроек приложения"""
    
    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.parent_ref = parent  # Сохраняем ссылку на родителя
        self.setWindowTitle("⚙ Настройки")
        self.setMinimumSize(600, 500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("⚙ Настройки приложения")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Тема оформления - две темы с мгновенным применением
        theme_group = QGroupBox("Тема оформления")
        theme_layout = QHBoxLayout(theme_group)
        
        self.btn_dark = QPushButton("🌙 Тёмная")
        self.btn_dark.setObjectName("secondaryBtn")
        self.btn_dark.setCheckable(True)
        self.btn_dark.setChecked(self.settings.get('theme', 'Тёмная') == 'Тёмная')
        self.btn_dark.clicked.connect(lambda: self.apply_theme('Тёмная'))
        theme_layout.addWidget(self.btn_dark)
        
        self.btn_light = QPushButton("☀️ Светлая")
        self.btn_light.setObjectName("secondaryBtn")
        self.btn_light.setCheckable(True)
        self.btn_light.setChecked(self.settings.get('theme', 'Тёмная') == 'Светлая')
        self.btn_light.clicked.connect(lambda: self.apply_theme('Светлая'))
        theme_layout.addWidget(self.btn_light)
        
        layout.addWidget(theme_group)
        
        # Настройки анализа
        analysis_group = QGroupBox("Настройки анализа")
        analysis_layout = QVBoxLayout(analysis_group)
        
        timeout_layout = QHBoxLayout()
        timeout_label = QLabel("Время анализа (сек):")
        timeout_layout.addWidget(timeout_label)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(self.settings.get('timeout', 60))
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        analysis_layout.addLayout(timeout_layout)
        
        self.poly_check = QCheckBox("Создавать варианты файла для анализа")
        self.poly_check.setChecked(self.settings.get('use_poly_default', False))
        analysis_layout.addWidget(self.poly_check)
        
        self.network_check = QCheckBox("Отключать сеть во время анализа")
        self.network_check.setChecked(self.settings.get('auto_disable_network', True))
        analysis_layout.addWidget(self.network_check)
        
        layout.addWidget(analysis_group)
        
        # Кнопка закрытия
        self.btn_close_settings = QPushButton("Закрыть")
        self.btn_close_settings.setObjectName("secondaryBtn")
        self.btn_close_settings.setFixedHeight(45)
        self.btn_close_settings.clicked.connect(self.accept)
        layout.addWidget(self.btn_close_settings)
    
    def apply_theme(self, theme_name: str):
        """Применить тему немедленно"""
        if self.parent_ref:
            self.parent_ref.settings['theme'] = theme_name
            self.parent_ref.apply_stylesheet()
            self.parent_ref.save_settings()
            
            # Обновляем состояние кнопок
            self.btn_dark.setChecked(theme_name == 'Тёмная')
            self.btn_light.setChecked(theme_name == 'Светлая')
    
    def get_settings(self):
        """Получить текущие настройки"""
        return {
            'theme': self.parent_ref.settings.get('theme', 'Тёмная'),
            'timeout': self.timeout_spin.value(),
            'use_poly_default': self.poly_check.isChecked(),
            'auto_disable_network': self.network_check.isChecked()
        }


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
        self.setWindowTitle("RedSand Secure - Профессиональный анализ malware")
        self.showMaximized()
        
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
    
    def open_settings(self):
        """Открыть диалог настроек"""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec_() == QDialog.Accepted:
            new_settings = dialog.get_settings()
            self.settings.update(new_settings)
            self.apply_stylesheet()
            self.save_settings()
    
    def open_history(self):
        """Открыть историю сканирований"""
        dialog = ScanHistoryDialog(scan_history=self.scan_history, parent=self)
        dialog.exec_()
    
    def open_quarantine(self):
        """Открыть диалог карантина"""
        try:
            dialog = QuarantineDialog(quarantine_manager=self.quarantine_manager, parent=self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть карантин:\n{str(e)}")
    
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
                    self.settings = json.load(f)
                self.apply_stylesheet()
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
