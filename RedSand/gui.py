#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Secure GUI - Современный интерфейс на PyQt6
Многоязычный интерфейс (RU/EN) с темами оформления и расширенными настройками
"""

import sys
import os
import json
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QFileDialog, QProgressBar,
    QTextEdit, QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QScrollArea, QSplitter, QTreeWidget,
    QTreeWidgetItem, QMessageBox, QSystemTrayIcon, QMenu,
    QToolBar, QStatusBar, QFrame, QSlider, QColorDialog, QFontDialog,
    QListWidget, QListWidgetItem, QRadioButton, QButtonGroup,
    QStackedWidget, QDialog, QDialogButtonBox, QLineEdit
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSettings, QTranslator,
    QLocale, QSize, QPoint, QPropertyAnimation, QEasingCurve,
    pyqtProperty
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QPainter, QColor, QPalette, QBrush,
    QFont, QActionGroup, QKeySequence, QShortcut, QMovie, QAction
)


class ThemeManager:
    """Менеджер тем оформления"""
    
    THEMES = {
        'dark': {
            'name_ru': 'Тёмная',
            'name_en': 'Dark',
            'colors': {
                'bg_primary': '#1a1a2e',
                'bg_secondary': '#16213e',
                'bg_tertiary': '#0f3460',
                'text_primary': '#ffffff',
                'text_secondary': '#b8b8b8',
                'accent': '#e94560',
                'accent_hover': '#ff6b6b',
                'success': '#4ecca3',
                'warning': '#ffc857',
                'danger': '#e94560',
                'border': '#2d4a7c',
            }
        },
        'light': {
            'name_ru': 'Светлая',
            'name_en': 'Light',
            'colors': {
                'bg_primary': '#f5f5f5',
                'bg_secondary': '#ffffff',
                'bg_tertiary': '#e8e8e8',
                'text_primary': '#1a1a1a',
                'text_secondary': '#555555',
                'accent': '#e94560',
                'accent_hover': '#d63850',
                'success': '#2ecc71',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'border': '#dddddd',
            }
        },
        'cyber': {
            'name_ru': 'Киберпанк',
            'name_en': 'Cyberpunk',
            'colors': {
                'bg_primary': '#0d0d0d',
                'bg_secondary': '#1a0a2e',
                'bg_tertiary': '#16213e',
                'text_primary': '#00ff9f',
                'text_secondary': '#00b8ff',
                'accent': '#ff00ff',
                'accent_hover': '#ff69b4',
                'success': '#00ff9f',
                'warning': '#ffcc00',
                'danger': '#ff0066',
                'border': '#00ff9f',
            }
        },
        'ocean': {
            'name_ru': 'Океан',
            'name_en': 'Ocean',
            'colors': {
                'bg_primary': '#0a1628',
                'bg_secondary': '#1a3a5c',
                'bg_tertiary': '#2d5a7a',
                'text_primary': '#e0f0ff',
                'text_secondary': '#a8c8dc',
                'accent': '#00d4ff',
                'accent_hover': '#00a8cc',
                'success': '#00ff88',
                'warning': '#ffaa00',
                'danger': '#ff4466',
                'border': '#1a5a8a',
            }
        },
        'forest': {
            'name_ru': 'Лес',
            'name_en': 'Forest',
            'colors': {
                'bg_primary': '#1a281a',
                'bg_secondary': '#2d3a2d',
                'bg_tertiary': '#3a4a3a',
                'text_primary': '#d4e8d4',
                'text_secondary': '#a8c8a8',
                'accent': '#7cb342',
                'accent_hover': '#689f38',
                'success': '#81c784',
                'warning': '#ffb74d',
                'danger': '#e57373',
                'border': '#3a5a3a',
            }
        },
        'midnight': {
            'name_ru': 'Полночь',
            'name_en': 'Midnight',
            'colors': {
                'bg_primary': '#0f0f1a',
                'bg_secondary': '#1a1a2e',
                'bg_tertiary': '#2d2d44',
                'text_primary': '#f0f0f0',
                'text_secondary': '#a0a0a0',
                'accent': '#7c4dff',
                'accent_hover': '#651fff',
                'success': '#69f0ae',
                'warning': '#ffd740',
                'danger': '#ff5252',
                'border': '#3a3a5a',
            }
        }
    }
    
    def __init__(self):
        self.current_theme = 'dark'
    
    def get_stylesheet(self, theme_name: str) -> str:
        """Генерация CSS stylesheet для темы"""
        theme = self.THEMES.get(theme_name, self.THEMES['dark'])
        colors = theme['colors']
        
        return f"""
        /* Global Styles */
        QMainWindow {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
        }}
        
        QWidget {{
            background-color: transparent;
            color: {colors['text_primary']};
        }}
        
        QGroupBox {{
            background-color: {colors['bg_secondary']};
            border: 2px solid {colors['border']};
            border-radius: 10px;
            margin-top: 15px;
            padding-top: 15px;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px;
            color: {colors['accent']};
        }}
        
        QTabWidget::pane {{
            background-color: {colors['bg_secondary']};
            border: 2px solid {colors['border']};
            border-radius: 8px;
        }}
        
        QTabBar::tab {{
            background-color: {colors['bg_tertiary']};
            color: {colors['text_secondary']};
            padding: 12px 25px;
            margin-right: 5px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            min-width: 120px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['accent']};
            color: {colors['text_primary']};
            font-weight: bold;
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {colors['bg_secondary']};
        }}
        
        QPushButton {{
            background-color: {colors['accent']};
            color: {colors['text_primary']};
            border: none;
            border-radius: 8px;
            padding: 12px 25px;
            font-weight: bold;
            font-size: 14px;
            min-height: 20px;
        }}
        
        QPushButton:hover {{
            background-color: {colors['accent_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['accent']};
            padding: 13px 24px 11px 26px;
        }}
        
        QPushButton:disabled {{
            background-color: {colors['bg_tertiary']};
            color: {colors['text_secondary']};
        }}
        
        QPushButton#secondaryBtn {{
            background-color: {colors['bg_tertiary']};
            border: 2px solid {colors['border']};
        }}
        
        QPushButton#secondaryBtn:hover {{
            background-color: {colors['border']};
        }}
        
        QPushButton#dangerBtn {{
            background-color: {colors['danger']};
        }}
        
        QPushButton#dangerBtn:hover {{
            background-color: #ff6b6b;
        }}
        
        QPushButton#successBtn {{
            background-color: {colors['success']};
        }}
        
        QProgressBar {{
            background-color: {colors['bg_tertiary']};
            border: none;
            border-radius: 8px;
            height: 20px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['accent']};
            border-radius: 8px;
        }}
        
        QTextEdit, QPlainTextEdit {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            border: 2px solid {colors['border']};
            border-radius: 8px;
            padding: 10px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
        }}
        
        QComboBox {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 2px solid {colors['border']};
            border-radius: 8px;
            padding: 8px 15px;
            min-width: 150px;
        }}
        
        QComboBox:hover {{
            border: 2px solid {colors['accent']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 8px solid {colors['accent']};
            margin-right: 10px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 2px solid {colors['border']};
            selection-background-color: {colors['accent']};
            border-radius: 8px;
        }}
        
        QCheckBox {{
            color: {colors['text_primary']};
            spacing: 10px;
            font-size: 14px;
        }}
        
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 5px;
            border: 2px solid {colors['border']};
            background-color: {colors['bg_secondary']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors['accent']};
            border: 2px solid {colors['accent']};
        }}
        
        QCheckBox::indicator:hover {{
            border: 2px solid {colors['accent']};
        }}
        
        QRadioButton {{
            color: {colors['text_primary']};
            spacing: 10px;
            font-size: 14px;
        }}
        
        QRadioButton::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 10px;
            border: 2px solid {colors['border']};
            background-color: {colors['bg_secondary']};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {colors['accent']};
            border: 2px solid {colors['accent']};
        }}
        
        QSpinBox, QDoubleSpinBox {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 2px solid {colors['border']};
            border-radius: 8px;
            padding: 8px 15px;
        }}
        
        QSpinBox:hover, QDoubleSpinBox:hover {{
            border: 2px solid {colors['accent']};
        }}
        
        QSlider::groove:horizontal {{
            background-color: {colors['bg_tertiary']};
            height: 8px;
            border-radius: 4px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {colors['accent']};
            width: 20px;
            margin: -6px 0;
            border-radius: 10px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {colors['accent_hover']};
        }}
        
        QTreeWidget, QListWidget {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            border: 2px solid {colors['border']};
            border-radius: 8px;
            outline: none;
        }}
        
        QTreeWidget::item, QListWidget::item {{
            padding: 8px;
            border-radius: 5px;
        }}
        
        QTreeWidget::item:selected, QListWidget::item:selected {{
            background-color: {colors['accent']};
            color: {colors['text_primary']};
        }}
        
        QTreeWidget::item:hover, QListWidget::item:hover {{
            background-color: {colors['bg_tertiary']};
        }}
        
        QHeaderView::section {{
            background-color: {colors['bg_tertiary']};
            color: {colors['text_primary']};
            padding: 10px;
            border: none;
            border-bottom: 2px solid {colors['border']};
            font-weight: bold;
        }}
        
        QScrollBar:vertical {{
            background-color: {colors['bg_primary']};
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['bg_tertiary']};
            min-height: 30px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['border']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        
        QScrollBar:horizontal {{
            background-color: {colors['bg_primary']};
            height: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {colors['bg_tertiary']};
            min-width: 30px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {colors['border']};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
        
        QMenu {{
            background-color: {colors['bg_secondary']};
            border: 2px solid {colors['border']};
            border-radius: 8px;
            padding: 10px;
        }}
        
        QMenu::item {{
            padding: 10px 25px;
            border-radius: 5px;
            margin: 2px 5px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors['accent']};
        }}
        
        QMenu::separator {{
            height: 2px;
            background-color: {colors['border']};
            margin: 5px 10px;
        }}
        
        QToolBar {{
            background-color: {colors['bg_secondary']};
            border: none;
            border-bottom: 2px solid {colors['border']};
            padding: 5px;
            spacing: 10px;
        }}
        
        QToolButton {{
            background-color: transparent;
            border: none;
            border-radius: 8px;
            padding: 10px;
            color: {colors['text_primary']};
        }}
        
        QToolButton:hover {{
            background-color: {colors['bg_tertiary']};
        }}
        
        QToolButton:pressed {{
            background-color: {colors['accent']};
        }}
        
        QStatusBar {{
            background-color: {colors['bg_secondary']};
            border-top: 2px solid {colors['border']};
            color: {colors['text_secondary']};
            padding: 5px;
        }}
        
        QLabel#titleLabel {{
            font-size: 24px;
            font-weight: bold;
            color: {colors['accent']};
            padding: 10px;
        }}
        
        QLabel#subtitleLabel {{
            font-size: 14px;
            color: {colors['text_secondary']};
            padding: 5px;
        }}
        
        QFrame#separator {{
            background-color: {colors['border']};
            max-height: 2px;
        }}
        
        /* Scroll Area */
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        /* Dialog */
        QDialog {{
            background-color: {colors['bg_primary']};
        }}
        
        /* Line Edit */
        QLineEdit {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 2px solid {colors['border']};
            border-radius: 8px;
            padding: 8px 15px;
            font-size: 14px;
        }}
        
        QLineEdit:hover {{
            border: 2px solid {colors['accent']};
        }}
        
        QLineEdit:focus {{
            border: 2px solid {colors['accent']};
            background-color: {colors['bg_primary']};
        }}
        """


class LanguageManager:
    """Менеджер локализации"""
    
    TRANSLATIONS = {
        'ru': {
            'app_title': 'RedSand Secure - Анализ вредоносного ПО',
            'menu_file': 'Файл',
            'menu_settings': 'Настройки',
            'menu_help': 'Помощь',
            'menu_language': 'Язык',
            'menu_theme': 'Тема',
            'action_open': 'Открыть файл',
            'action_open_folder': 'Открыть папку',
            'action_scan': 'Сканировать',
            'action_stop': 'Остановить',
            'action_exit': 'Выход',
            'action_settings': 'Настройки',
            'action_about': 'О программе',
            'action_docs': 'Документация',
            'tab_analysis': 'Анализ',
            'tab_settings': 'Настройки',
            'tab_reports': 'Отчёты',
            'tab_logs': 'Логи',
            'btn_select_file': 'Выбрать файл',
            'btn_select_folder': 'Выбрать папку',
            'btn_start_scan': 'Начать сканирование',
            'btn_stop_scan': 'Остановить сканирование',
            'btn_clear_logs': 'Очистить логи',
            'btn_export_report': 'Экспорт отчёта',
            'lbl_file_selected': 'Выбранный файл:',
            'lbl_no_file': 'Файл не выбран',
            'lbl_progress': 'Прогресс:',
            'lbl_status': 'Статус:',
            'lbl_threats_found': 'Угроз найдено:',
            'lbl_analysis_time': 'Время анализа:',
            'grp_static_analysis': 'Статический анализ',
            'grp_dynamic_analysis': 'Динамический анализ',
            'grp_network': 'Сеть',
            'grp_sandbox': 'Анти-песочница',
            'grp_reporting': 'Отчёты',
            'chk_pe_analysis': 'PE анализ',
            'chk_strings': 'Извлечение строк',
            'chk_hashes': 'Вычисление хешей',
            'chk_yara': 'YARA правила',
            'chk_run_sample': 'Запуск образца',
            'chk_monitor_processes': 'Мониторинг процессов',
            'chk_monitor_network': 'Мониторинг сети',
            'chk_monitor_registry': 'Мониторинг реестра',
            'chk_emulate_dns': 'Эмуляция DNS',
            'chk_emulate_http': 'Эмуляция HTTP',
            'chk_disable_network': 'Отключить сеть',
            'chk_fake_user_activity': 'Фейк активность пользователя',
            'chk_fake_registry': 'Фейк записи реестра',
            'chk_fake_processes': 'Фейк процессы',
            'chk_json_report': 'JSON',
            'chk_html_report': 'HTML',
            'chk_txt_report': 'TXT',
            'lbl_timeout': 'Таймаут (сек):',
            'lbl_max_workers': 'Макс. потоков:',
            'lbl_log_level': 'Уровень логов:',
            'lbl_theme': 'Тема:',
            'lbl_language': 'Язык:',
            'status_ready': 'Готов к работе',
            'status_scanning': 'Сканирование...',
            'status_completed': 'Завершено',
            'status_error': 'Ошибка',
            'msg_no_file': 'Пожалуйста, выберите файл для анализа',
            'msg_scan_complete': 'Сканирование завершено',
            'msg_confirm_stop': 'Вы уверены, что хотите остановить сканирование?',
            'msg_about_title': 'О RedSand Secure',
            'msg_about_text': 'RedSand Secure v3.0\n\nСовременная система анализа вредоносного ПО\n\nФункции:\n• Статический и динамический анализ\n• Эмуляция сети\n• Анти-песочница\n• Многоядерная обработка\n• Расширенные отчёты\n\n© 2024 RedSand Security',
            'cfg_analysis': 'Анализ',
            'cfg_behavior': 'Поведение',
            'cfg_security': 'Безопасность',
            'cfg_interface': 'Интерфейс',
            'cfg_advanced': 'Дополнительно',
            'chk_auto_delete': 'Автоудаление угроз',
            'chk_quarantine': 'Карантин',
            'chk_heuristic': 'Эвристический анализ',
            'chk_ml_classification': 'ML классификация',
            'chk_cloud_lookup': 'Проверка в облаке',
            'lbl_scan_depth': 'Глубина сканирования:',
            'lbl_sensitivity': 'Чувствительность:',
            'chk_verbose_logging': 'Подробное логирование',
            'chk_color_logs': 'Цветные логи',
            'chk_tray_icon': 'Иконка в трее',
            'chk_minimize_tray': 'Сворачивать в трей',
            'chk_startup_scan': 'Сканирование при старте',
            'chk_auto_update': 'Автообновление баз',
            'btn_reset_settings': 'Сброс настроек',
            'btn_save_settings': 'Сохранить настройки',
            'msg_settings_saved': 'Настройки сохранены',
            'msg_settings_reset': 'Настройки сброшены',
        },
        'en': {
            'app_title': 'RedSand Secure - Malware Analysis',
            'menu_file': 'File',
            'menu_settings': 'Settings',
            'menu_help': 'Help',
            'menu_language': 'Language',
            'menu_theme': 'Theme',
            'action_open': 'Open File',
            'action_open_folder': 'Open Folder',
            'action_scan': 'Scan',
            'action_stop': 'Stop',
            'action_exit': 'Exit',
            'action_settings': 'Settings',
            'action_about': 'About',
            'action_docs': 'Documentation',
            'tab_analysis': 'Analysis',
            'tab_settings': 'Settings',
            'tab_reports': 'Reports',
            'tab_logs': 'Logs',
            'btn_select_file': 'Select File',
            'btn_select_folder': 'Select Folder',
            'btn_start_scan': 'Start Scan',
            'btn_stop_scan': 'Stop Scan',
            'btn_clear_logs': 'Clear Logs',
            'btn_export_report': 'Export Report',
            'lbl_file_selected': 'Selected File:',
            'lbl_no_file': 'No file selected',
            'lbl_progress': 'Progress:',
            'lbl_status': 'Status:',
            'lbl_threats_found': 'Threats Found:',
            'lbl_analysis_time': 'Analysis Time:',
            'grp_static_analysis': 'Static Analysis',
            'grp_dynamic_analysis': 'Dynamic Analysis',
            'grp_network': 'Network',
            'grp_sandbox': 'Anti-Sandbox',
            'grp_reporting': 'Reporting',
            'chk_pe_analysis': 'PE Analysis',
            'chk_strings': 'Extract Strings',
            'chk_hashes': 'Calculate Hashes',
            'chk_yara': 'YARA Rules',
            'chk_run_sample': 'Run Sample',
            'chk_monitor_processes': 'Monitor Processes',
            'chk_monitor_network': 'Monitor Network',
            'chk_monitor_registry': 'Monitor Registry',
            'chk_emulate_dns': 'Emulate DNS',
            'chk_emulate_http': 'Emulate HTTP',
            'chk_disable_network': 'Disable Network',
            'chk_fake_user_activity': 'Fake User Activity',
            'chk_fake_registry': 'Fake Registry Entries',
            'chk_fake_processes': 'Fake Processes',
            'chk_json_report': 'JSON',
            'chk_html_report': 'HTML',
            'chk_txt_report': 'TXT',
            'lbl_timeout': 'Timeout (sec):',
            'lbl_max_workers': 'Max Workers:',
            'lbl_log_level': 'Log Level:',
            'lbl_theme': 'Theme:',
            'lbl_language': 'Language:',
            'status_ready': 'Ready',
            'status_scanning': 'Scanning...',
            'status_completed': 'Completed',
            'status_error': 'Error',
            'msg_no_file': 'Please select a file to analyze',
            'msg_scan_complete': 'Scan completed',
            'msg_confirm_stop': 'Are you sure you want to stop scanning?',
            'msg_about_title': 'About RedSand Secure',
            'msg_about_text': 'RedSand Secure v3.0\n\nModern Malware Analysis System\n\nFeatures:\n• Static and Dynamic Analysis\n• Network Emulation\n• Anti-Sandbox\n• Multi-core Processing\n• Advanced Reporting\n\n© 2024 RedSand Security',
            'cfg_analysis': 'Analysis',
            'cfg_behavior': 'Behavior',
            'cfg_security': 'Security',
            'cfg_interface': 'Interface',
            'cfg_advanced': 'Advanced',
            'chk_auto_delete': 'Auto-delete Threats',
            'chk_quarantine': 'Quarantine',
            'chk_heuristic': 'Heuristic Analysis',
            'chk_ml_classification': 'ML Classification',
            'chk_cloud_lookup': 'Cloud Lookup',
            'lbl_scan_depth': 'Scan Depth:',
            'lbl_sensitivity': 'Sensitivity:',
            'chk_verbose_logging': 'Verbose Logging',
            'chk_color_logs': 'Color Logs',
            'chk_tray_icon': 'Tray Icon',
            'chk_minimize_tray': 'Minimize to Tray',
            'chk_startup_scan': 'Scan on Startup',
            'chk_auto_update': 'Auto-update Databases',
            'btn_reset_settings': 'Reset Settings',
            'btn_save_settings': 'Save Settings',
            'msg_settings_saved': 'Settings saved',
            'msg_settings_reset': 'Settings reset',
        }
    }
    
    def __init__(self):
        self.current_language = 'ru'
    
    def get(self, key: str) -> str:
        """Получение переведённой строки"""
        return self.TRANSLATIONS.get(self.current_language, {}).get(key, key)
    
    def set_language(self, lang: str):
        """Установка языка"""
        if lang in self.TRANSLATIONS:
            self.current_language = lang


class AnalysisWorker(QThread):
    """Worker поток для анализа файлов"""
    
    progress_signal = pyqtSignal(int)
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal(bool)
    
    def __init__(self, file_path: str, settings: dict):
        super().__init__()
        self.file_path = file_path
        self.settings = settings
        self._stop_flag = False
    
    def run(self):
        """Основной метод анализа"""
        try:
            self.log_signal.emit(f"Starting analysis of: {self.file_path}")
            
            # Имитация процесса анализа (в реальности здесь вызов redsand_secure.py)
            for i in range(100):
                if self._stop_flag:
                    self.finished_signal.emit(False)
                    return
                
                self.progress_signal.emit(i + 1)
                
                # Симуляция различных этапов анализа
                if i == 10:
                    self.log_signal.emit("Calculating file hashes...")
                elif i == 30:
                    self.log_signal.emit("Performing static analysis...")
                elif i == 50:
                    self.log_signal.emit("Extracting strings...")
                elif i == 70:
                    self.log_signal.emit("Running dynamic analysis...")
                elif i == 90:
                    self.log_signal.emit("Generating report...")
                
                # Симуляция задержки
                QThread.msleep(50)
            
            # Результат анализа
            result = {
                'file': self.file_path,
                'threats': 0,
                'time': 5.0,
                'status': 'clean'
            }
            
            self.result_signal.emit(result)
            self.log_signal.emit("Analysis completed successfully")
            self.finished_signal.emit(True)
            
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(False)
    
    def stop(self):
        """Остановка анализа"""
        self._stop_flag = True


class RedSandGUI(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        
        self.theme_manager = ThemeManager()
        self.language_manager = LanguageManager()
        self.settings = self.load_settings()
        self.analysis_worker: Optional[AnalysisWorker] = None
        self.selected_file: Optional[str] = None
        
        self.init_ui()
        self.apply_theme(self.settings.get('theme', 'dark'))
        self.apply_language(self.settings.get('language', 'ru'))
        self.restore_window_state()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle(self.language_manager.get('app_title'))
        self.setMinimumSize(1400, 900)
        
        # Центральное виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Заголовок
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("🛡️ RedSand Secure")
        title_label.setObjectName("titleLabel")
        subtitle_label = QLabel("Advanced Malware Analysis System")
        subtitle_label.setObjectName("subtitleLabel")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addStretch()
        
        main_layout.addWidget(header_frame)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Создание вкладок
        self.create_analysis_tab()
        self.create_settings_tab()
        self.create_reports_tab()
        self.create_logs_tab()
        
        # Тулбар
        self.create_toolbar()
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.language_manager.get('status_ready'))
        
        # Трей
        self.create_tray_icon()
        
        # Горячие клавиши
        self.create_shortcuts()
    
    def create_analysis_tab(self):
        """Создание вкладки анализа"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setSpacing(15)
        
        # Левая панель - управление
        left_panel = QScrollArea()
        left_panel.setWidgetResizable(True)
        left_panel.setMaximumWidth(400)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)
        
        # Выбор файла
        file_group = QGroupBox(self.language_manager.get('lbl_file_selected'))
        file_layout = QVBoxLayout(file_group)
        
        self.file_label = QLabel(self.language_manager.get('lbl_no_file'))
        self.file_label.setWordWrap(True)
        file_layout.addWidget(self.file_label)
        
        btn_layout = QHBoxLayout()
        self.btn_select_file = QPushButton(self.language_manager.get('btn_select_file'))
        self.btn_select_file.clicked.connect(self.select_file)
        self.btn_select_folder = QPushButton(self.language_manager.get('btn_select_folder'))
        self.btn_select_folder.clicked.connect(self.select_folder)
        
        btn_layout.addWidget(self.btn_select_file)
        btn_layout.addWidget(self.btn_select_folder)
        file_layout.addLayout(btn_layout)
        
        left_layout.addWidget(file_group)
        
        # Кнопки управления
        control_group = QGroupBox("Control")
        control_layout = QVBoxLayout(control_group)
        
        self.btn_start_scan = QPushButton(self.language_manager.get('btn_start_scan'))
        self.btn_start_scan.setObjectName("successBtn")
        self.btn_start_scan.clicked.connect(self.start_scan)
        self.btn_stop_scan = QPushButton(self.language_manager.get('btn_stop_scan'))
        self.btn_stop_scan.setObjectName("dangerBtn")
        self.btn_stop_scan.clicked.connect(self.stop_scan)
        self.btn_stop_scan.setEnabled(False)
        
        control_layout.addWidget(self.btn_start_scan)
        control_layout.addWidget(self.btn_stop_scan)
        left_layout.addWidget(control_group)
        
        # Прогресс
        progress_group = QGroupBox(self.language_manager.get('lbl_progress'))
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel(self.language_manager.get('status_ready'))
        progress_layout.addWidget(self.status_label)
        
        left_layout.addWidget(progress_group)
        
        # Статистика
        stats_group = QGroupBox("Statistics")
        stats_layout = QFormLayout(stats_group)
        
        self.lbl_threats = QLabel("0")
        self.lbl_time = QLabel("0.0s")
        
        stats_layout.addRow(self.language_manager.get('lbl_threats_found'), self.lbl_threats)
        stats_layout.addRow(self.language_manager.get('lbl_analysis_time'), self.lbl_time)
        
        left_layout.addWidget(stats_group)
        left_layout.addStretch()
        
        left_panel.setWidget(left_widget)
        layout.addWidget(left_panel)
        
        # Правая панель - настройки анализа
        right_panel = QScrollArea()
        right_panel.setWidgetResizable(True)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        
        # Статический анализ
        static_group = QGroupBox(self.language_manager.get('grp_static_analysis'))
        static_layout = QVBoxLayout(static_group)
        
        self.chk_pe = QCheckBox(self.language_manager.get('chk_pe_analysis'))
        self.chk_pe.setChecked(True)
        self.chk_strings = QCheckBox(self.language_manager.get('chk_strings'))
        self.chk_strings.setChecked(True)
        self.chk_hashes = QCheckBox(self.language_manager.get('chk_hashes'))
        self.chk_hashes.setChecked(True)
        self.chk_yara = QCheckBox(self.language_manager.get('chk_yara'))
        self.chk_yara.setChecked(True)
        
        static_layout.addWidget(self.chk_pe)
        static_layout.addWidget(self.chk_strings)
        static_layout.addWidget(self.chk_hashes)
        static_layout.addWidget(self.chk_yara)
        
        right_layout.addWidget(static_group)
        
        # Динамический анализ
        dynamic_group = QGroupBox(self.language_manager.get('grp_dynamic_analysis'))
        dynamic_layout = QVBoxLayout(dynamic_group)
        
        self.chk_run = QCheckBox(self.language_manager.get('chk_run_sample'))
        self.chk_run.setChecked(True)
        self.chk_monitor_proc = QCheckBox(self.language_manager.get('chk_monitor_processes'))
        self.chk_monitor_proc.setChecked(True)
        self.chk_monitor_net = QCheckBox(self.language_manager.get('chk_monitor_network'))
        self.chk_monitor_net.setChecked(True)
        self.chk_monitor_reg = QCheckBox(self.language_manager.get('chk_monitor_registry'))
        self.chk_monitor_reg.setChecked(False)
        
        dynamic_layout.addWidget(self.chk_run)
        dynamic_layout.addWidget(self.chk_monitor_proc)
        dynamic_layout.addWidget(self.chk_monitor_net)
        dynamic_layout.addWidget(self.chk_monitor_reg)
        
        right_layout.addWidget(dynamic_group)
        
        # Сеть
        network_group = QGroupBox(self.language_manager.get('grp_network'))
        network_layout = QVBoxLayout(network_group)
        
        self.chk_dns = QCheckBox(self.language_manager.get('chk_emulate_dns'))
        self.chk_dns.setChecked(True)
        self.chk_http = QCheckBox(self.language_manager.get('chk_emulate_http'))
        self.chk_http.setChecked(True)
        self.chk_disable_net = QCheckBox(self.language_manager.get('chk_disable_network'))
        self.chk_disable_net.setChecked(False)
        
        network_layout.addWidget(self.chk_dns)
        network_layout.addWidget(self.chk_http)
        network_layout.addWidget(self.chk_disable_net)
        
        right_layout.addWidget(network_group)
        
        # Анти-песочница
        sandbox_group = QGroupBox(self.language_manager.get('grp_sandbox'))
        sandbox_layout = QVBoxLayout(sandbox_group)
        
        self.chk_fake_user = QCheckBox(self.language_manager.get('chk_fake_user_activity'))
        self.chk_fake_user.setChecked(True)
        self.chk_fake_reg = QCheckBox(self.language_manager.get('chk_fake_registry'))
        self.chk_fake_reg.setChecked(True)
        self.chk_fake_proc = QCheckBox(self.language_manager.get('chk_fake_processes'))
        self.chk_fake_proc.setChecked(True)
        
        sandbox_layout.addWidget(self.chk_fake_user)
        sandbox_layout.addWidget(self.chk_fake_reg)
        sandbox_layout.addWidget(self.chk_fake_proc)
        
        right_layout.addWidget(sandbox_group)
        
        # Настройки
        settings_group = QGroupBox("Advanced Settings")
        settings_layout = QFormLayout(settings_group)
        
        self.spin_timeout = QSpinBox()
        self.spin_timeout.setRange(10, 600)
        self.spin_timeout.setValue(60)
        self.spin_workers = QSpinBox()
        self.spin_workers.setRange(1, 32)
        self.spin_workers.setValue(4)
        
        settings_layout.addRow(self.language_manager.get('lbl_timeout'), self.spin_timeout)
        settings_layout.addRow(self.language_manager.get('lbl_max_workers'), self.spin_workers)
        
        right_layout.addWidget(settings_group)
        right_layout.addStretch()
        
        right_panel.setWidget(right_widget)
        layout.addWidget(right_panel, stretch=1)
        
        self.tab_widget.addTab(tab, self.language_manager.get('tab_analysis'))
    
    def create_settings_tab(self):
        """Создание вкладки настроек"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Вкладки настроек
        settings_tabs = QTabWidget()
        
        # Анализ
        analysis_settings = self.create_analysis_settings()
        settings_tabs.addTab(analysis_settings, self.language_manager.get('cfg_analysis'))
        
        # Поведение
        behavior_settings = self.create_behavior_settings()
        settings_tabs.addTab(behavior_settings, self.language_manager.get('cfg_behavior'))
        
        # Безопасность
        security_settings = self.create_security_settings()
        settings_tabs.addTab(security_settings, self.language_manager.get('cfg_security'))
        
        # Интерфейс
        interface_settings = self.create_interface_settings()
        settings_tabs.addTab(interface_settings, self.language_manager.get('cfg_interface'))
        
        # Дополнительно
        advanced_settings = self.create_advanced_settings()
        settings_tabs.addTab(advanced_settings, self.language_manager.get('cfg_advanced'))
        
        layout.addWidget(settings_tabs)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_reset = QPushButton(self.language_manager.get('btn_reset_settings'))
        self.btn_reset.clicked.connect(self.reset_settings)
        self.btn_save = QPushButton(self.language_manager.get('btn_save_settings'))
        self.btn_save.setObjectName("successBtn")
        self.btn_save.clicked.connect(self.save_settings)
        
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
        
        self.tab_widget.addTab(tab, self.language_manager.get('tab_settings'))
    
    def create_analysis_settings(self):
        """Настройки анализа"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        grp = QGroupBox("Detection Settings")
        form = QFormLayout(grp)
        
        spin_depth = QSpinBox()
        spin_depth.setRange(1, 10)
        spin_depth.setValue(5)
        form.addRow(self.language_manager.get('lbl_scan_depth'), spin_depth)
        
        slider_sens = QSlider(Qt.Orientation.Horizontal)
        slider_sens.setRange(1, 100)
        slider_sens.setValue(75)
        form.addRow(self.language_manager.get('lbl_sensitivity'), slider_sens)
        
        chk_heuristic = QCheckBox(self.language_manager.get('chk_heuristic'))
        chk_heuristic.setChecked(True)
        chk_ml = QCheckBox(self.language_manager.get('chk_ml_classification'))
        chk_ml.setChecked(True)
        chk_cloud = QCheckBox(self.language_manager.get('chk_cloud_lookup'))
        chk_cloud.setChecked(False)
        
        layout.addWidget(grp)
        layout.addWidget(chk_heuristic)
        layout.addWidget(chk_ml)
        layout.addWidget(chk_cloud)
        layout.addStretch()
        
        return widget
    
    def create_behavior_settings(self):
        """Настройки поведения"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        chk_auto = QCheckBox(self.language_manager.get('chk_auto_delete'))
        chk_auto.setChecked(False)
        chk_quarantine = QCheckBox(self.language_manager.get('chk_quarantine'))
        chk_quarantine.setChecked(True)
        
        layout.addWidget(chk_auto)
        layout.addWidget(chk_quarantine)
        layout.addStretch()
        
        return widget
    
    def create_security_settings(self):
        """Настройки безопасности"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        grp = QGroupBox("Security Options")
        form = QFormLayout(grp)
        
        chk_isolate = QCheckBox("Isolate Network")
        chk_isolate.setChecked(True)
        chk_sandbox = QCheckBox("Enable Sandbox Mode")
        chk_sandbox.setChecked(True)
        
        layout.addWidget(grp)
        layout.addWidget(chk_isolate)
        layout.addWidget(chk_sandbox)
        layout.addStretch()
        
        return widget
    
    def create_interface_settings(self):
        """Настройки интерфейса"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Тема
        theme_group = QGroupBox(self.language_manager.get('lbl_theme'))
        theme_layout = QVBoxLayout(theme_group)
        
        self.combo_theme = QComboBox()
        for theme_key, theme_data in self.theme_manager.THEMES.items():
            name = theme_data[f'name_{self.language_manager.current_language}']
            self.combo_theme.addItem(name, theme_key)
        self.combo_theme.currentTextChanged.connect(lambda: self.apply_theme(self.combo_theme.currentData()))
        
        theme_layout.addWidget(self.combo_theme)
        layout.addWidget(theme_group)
        
        # Язык
        lang_group = QGroupBox(self.language_manager.get('lbl_language'))
        lang_layout = QVBoxLayout(lang_group)
        
        self.combo_lang = QComboBox()
        self.combo_lang.addItem("Русский", "ru")
        self.combo_lang.addItem("English", "en")
        self.combo_lang.currentTextChanged.connect(lambda: self.apply_language(self.combo_lang.currentData()))
        
        lang_layout.addWidget(self.combo_lang)
        layout.addWidget(lang_group)
        
        # Опции
        chk_verbose = QCheckBox(self.language_manager.get('chk_verbose_logging'))
        chk_color = QCheckBox(self.language_manager.get('chk_color_logs'))
        chk_color.setChecked(True)
        chk_tray = QCheckBox(self.language_manager.get('chk_tray_icon'))
        chk_tray.setChecked(True)
        chk_minimize = QCheckBox(self.language_manager.get('chk_minimize_tray'))
        chk_minimize.setChecked(False)
        
        layout.addWidget(chk_verbose)
        layout.addWidget(chk_color)
        layout.addWidget(chk_tray)
        layout.addWidget(chk_minimize)
        layout.addStretch()
        
        return widget
    
    def create_advanced_settings(self):
        """Дополнительные настройки"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        chk_startup = QCheckBox(self.language_manager.get('chk_startup_scan'))
        chk_startup.setChecked(False)
        chk_autoupdate = QCheckBox(self.language_manager.get('chk_auto_update'))
        chk_autoupdate.setChecked(True)
        
        layout.addWidget(chk_startup)
        layout.addWidget(chk_autoupdate)
        layout.addStretch()
        
        return widget
    
    def create_reports_tab(self):
        """Создание вкладки отчётов"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Список отчётов
        list_group = QGroupBox("Report History")
        list_layout = QVBoxLayout(list_group)
        
        self.report_list = QListWidget()
        list_layout.addWidget(self.report_list)
        
        btn_layout = QHBoxLayout()
        self.btn_export = QPushButton(self.language_manager.get('btn_export_report'))
        self.btn_export.clicked.connect(self.export_report)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addStretch()
        
        list_layout.addLayout(btn_layout)
        layout.addWidget(list_group)
        
        # Предпросмотр
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        self.tab_widget.addTab(tab, self.language_manager.get('tab_reports'))
    
    def create_logs_tab(self):
        """Создание вкладки логов"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Логи
        log_group = QGroupBox("Analysis Logs")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        btn_layout = QHBoxLayout()
        self.btn_clear_logs = QPushButton(self.language_manager.get('btn_clear_logs'))
        self.btn_clear_logs.clicked.connect(self.clear_logs)
        btn_layout.addWidget(self.btn_clear_logs)
        btn_layout.addStretch()
        
        log_layout.addLayout(btn_layout)
        layout.addWidget(log_group)
        
        self.tab_widget.addTab(tab, self.language_manager.get('tab_logs'))
    
    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Actions
        open_action = QAction("📁 Open", self)
        open_action.triggered.connect(self.select_file)
        toolbar.addAction(open_action)
        
        scan_action = QAction("▶️ Scan", self)
        scan_action.triggered.connect(self.start_scan)
        toolbar.addAction(scan_action)
        
        stop_action = QAction("⏹️ Stop", self)
        stop_action.triggered.connect(self.stop_scan)
        toolbar.addAction(stop_action)
        
        toolbar.addSeparator()
        
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        toolbar.addAction(settings_action)
        
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
    
    def create_tray_icon(self):
        """Создание иконки в трее"""
        self.tray_icon = QSystemTrayIcon(self)
        # Создаём простую иконку программно
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor("#e94560"))
        icon = QIcon(pixmap)
        self.tray_icon.setIcon(icon)
        
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_activated)
        self.tray_icon.show()
    
    def create_shortcuts(self):
        """Создание горячих клавиш"""
        # Ctrl+O - Открыть файл
        shortcut_open = QShortcut(QKeySequence("Ctrl+O"), self)
        shortcut_open.activated.connect(self.select_file)
        
        # F5 - Сканировать
        shortcut_scan = QShortcut(QKeySequence("F5"), self)
        shortcut_scan.activated.connect(self.start_scan)
        
        # Esc - Остановить
        shortcut_stop = QShortcut(QKeySequence("Esc"), self)
        shortcut_stop.activated.connect(self.stop_scan)
        
        # Ctrl+S - Сохранить настройки
        shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut_save.activated.connect(self.save_settings)
    
    # Методы управления
    def select_file(self):
        """Выбор файла для анализа"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File to Analyze",
            "",
            "All Files (*);;Executable Files (*.exe *.dll *.bat *.cmd *.ps1);;Scripts (*.py *.sh)"
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(file_path)
            self.log_message(f"File selected: {file_path}")
    
    def select_folder(self):
        """Выбор папки для анализа"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Analyze"
        )
        if folder_path:
            self.selected_file = folder_path
            self.file_label.setText(folder_path)
            self.log_message(f"Folder selected: {folder_path}")
    
    def start_scan(self):
        """Запуск сканирования"""
        if not self.selected_file:
            QMessageBox.warning(self, "Warning", self.language_manager.get('msg_no_file'))
            return
        
        self.btn_start_scan.setEnabled(False)
        self.btn_stop_scan.setEnabled(True)
        self.status_label.setText(self.language_manager.get('status_scanning'))
        
        # Сбор настроек
        settings = {
            'static': {
                'pe': self.chk_pe.isChecked(),
                'strings': self.chk_strings.isChecked(),
                'hashes': self.chk_hashes.isChecked(),
                'yara': self.chk_yara.isChecked(),
            },
            'dynamic': {
                'run': self.chk_run.isChecked(),
                'monitor_processes': self.chk_monitor_proc.isChecked(),
                'monitor_network': self.chk_monitor_net.isChecked(),
                'monitor_registry': self.chk_monitor_reg.isChecked(),
            },
            'network': {
                'dns': self.chk_dns.isChecked(),
                'http': self.chk_http.isChecked(),
                'disable': self.chk_disable_net.isChecked(),
            },
            'sandbox': {
                'fake_user': self.chk_fake_user.isChecked(),
                'fake_registry': self.chk_fake_reg.isChecked(),
                'fake_processes': self.chk_fake_proc.isChecked(),
            },
            'timeout': self.spin_timeout.value(),
            'workers': self.spin_workers.value(),
        }
        
        # Запуск worker
        self.analysis_worker = AnalysisWorker(self.selected_file, settings)
        self.analysis_worker.progress_signal.connect(self.progress_bar.setValue)
        self.analysis_worker.log_signal.connect(self.log_message)
        self.analysis_worker.result_signal.connect(self.handle_result)
        self.analysis_worker.finished_signal.connect(self.scan_finished)
        self.analysis_worker.start()
    
    def stop_scan(self):
        """Остановка сканирования"""
        reply = QMessageBox.question(
            self,
            "Confirm Stop",
            self.language_manager.get('msg_confirm_stop'),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes and self.analysis_worker:
            self.analysis_worker.stop()
            self.log_message("Scan stopped by user")
    
    def scan_finished(self, success: bool):
        """Завершение сканирования"""
        self.btn_start_scan.setEnabled(True)
        self.btn_stop_scan.setEnabled(False)
        
        if success:
            self.status_label.setText(self.language_manager.get('status_completed'))
            QMessageBox.information(self, "Complete", self.language_manager.get('msg_scan_complete'))
        else:
            self.status_label.setText(self.language_manager.get('status_error'))
    
    def handle_result(self, result: dict):
        """Обработка результата"""
        self.lbl_threats.setText(str(result.get('threats', 0)))
        self.lbl_time.setText(f"{result.get('time', 0):.1f}s")
        
        # Добавление в список отчётов
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item_text = f"{timestamp} - {Path(result.get('file', '')).name}"
        self.report_list.addItem(item_text)
    
    def export_report(self):
        """Экспорт отчёта"""
        current_item = self.report_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "No report selected")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Report",
            "",
            "JSON (*.json);;HTML (*.html);;Text (*.txt)"
        )
        if file_path:
            self.log_message(f"Report exported to: {file_path}")
    
    def clear_logs(self):
        """Очистка логов"""
        self.log_text.clear()
        self.log_message("Logs cleared")
    
    def log_message(self, message: str):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def apply_theme(self, theme_name: str):
        """Применение темы"""
        stylesheet = self.theme_manager.get_stylesheet(theme_name)
        self.setStyleSheet(stylesheet)
        self.settings['theme'] = theme_name
    
    def apply_language(self, lang: str):
        """Применение языка"""
        self.language_manager.set_language(lang)
        self.settings['language'] = lang
        
        # Обновление текстов
        self.setWindowTitle(self.language_manager.get('app_title'))
        # TODO: Обновить все тексты в интерфейсе
    
    def save_settings(self):
        """Сохранение настроек"""
        settings_file = Path('gui_settings.json')
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=2, ensure_ascii=False)
        
        QMessageBox.information(self, "Settings", self.language_manager.get('msg_settings_saved'))
    
    def load_settings(self) -> dict:
        """Загрузка настроек"""
        settings_file = Path('gui_settings.json')
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'theme': 'dark',
            'language': 'ru',
            'window_size': [1400, 900],
        }
    
    def reset_settings(self):
        """Сброс настроек"""
        self.settings = {
            'theme': 'dark',
            'language': 'ru',
            'window_size': [1400, 900],
        }
        QMessageBox.information(self, "Settings", self.language_manager.get('msg_settings_reset'))
    
    def restore_window_state(self):
        """Восстановление состояния окна"""
        size = self.settings.get('window_size', [1400, 900])
        self.resize(size[0], size[1])
        self.move(
            QApplication.primaryScreen().availableGeometry().width() // 2 - size[0] // 2,
            QApplication.primaryScreen().availableGeometry().height() // 2 - size[1] // 2
        )
    
    def tray_activated(self, reason):
        """Обработка активации трея"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.activateWindow()
    
    def show_about(self):
        """Показать информацию о программе"""
        QMessageBox.about(
            self,
            self.language_manager.get('msg_about_title'),
            self.language_manager.get('msg_about_text')
        )
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if self.settings.get('minimize_tray', False) and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "RedSand Secure",
                "Minimized to tray",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            if self.analysis_worker and self.analysis_worker.isRunning():
                self.analysis_worker.stop()
            self.save_window_state()
            event.accept()
    
    def save_window_state(self):
        """Сохранение состояния окна"""
        self.settings['window_size'] = [self.width(), self.height()]


def main():
    """Точка входа приложения"""
    app = QApplication(sys.argv)
    app.setApplicationName("RedSand Secure")
    app.setOrganizationName("RedSand Security")
    
    # Применение стиля
    window = RedSandGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
