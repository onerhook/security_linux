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
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QSize, QUrl, QMimeData, QPropertyAnimation, QEasingCurve, QFileSystemWatcher
from PyQt5.QtGui import QFont, QColor, QDesktopServices, QIcon, QPixmap, QDragEnterEvent, QDropEvent

# Импорт компонентов ядра
from core.realtime_antivirus import RealTimeAntivirus, QuarantineManager, FileMonitorHandler
from core.virus_scanner import VirusScanner
from core.extended_scanner import ExtendedVirusScanner, ThreatLevel

# Импорты для watchdog
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None
    FileCreatedEvent = None


class AnalysisWorker(QThread):
    """Рабочий поток для анализа файлов без блокировки GUI"""
    progress = pyqtSignal(int, str)  # прогресс, текст
    result_ready = pyqtSignal(dict)  # результаты анализа как словарь
    error_occurred = pyqtSignal(str)  # ошибка
    
    def __init__(self, file_path: str, use_poly: bool = False, timeout: int = 60):
        super().__init__()
        self.file_path = file_path
        self.use_poly = use_poly
        self.timeout = timeout
        self.scanner = ExtendedVirusScanner()
    
    def run(self):
        try:
            # Прогресс 25% - начало анализа
            self.progress.emit(25, "Starting analysis...")
            
            # Прогресс 50% - статический анализ
            self.progress.emit(50, "Static analysis...")
            
            # Прогресс 75% - проверка сигнатур
            self.progress.emit(75, "Signature check...")
            
            # Реальный анализ файла
            scan_result = self.scanner.scan_file(self.file_path)
            
            # Прогресс 100% - завершено
            self.progress.emit(100, "Analysis complete!")
            
            # Конвертируем ScanResult в словарь для передачи через сигнал
            result_dict = {
                'file_path': scan_result.file_path,
                'threat_level': scan_result.threat_level.value if hasattr(scan_result.threat_level, 'value') else str(scan_result.threat_level),
                'risk_score': scan_result.score,
                'detected_threats': scan_result.threats_found,
                'threat_types': scan_result.threat_types,
                'sha256': scan_result.sha256,
                'matched_signatures': scan_result.details.get('matched_signatures', []),
                'matched_patterns': scan_result.details.get('matched_patterns', []),
                'details': scan_result.details
            }
            self.result_ready.emit(result_dict)
            
        except Exception as e:
            self.error_occurred.emit(str(e))


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
        padding: 12px 40px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-right: 3px;
        font-weight: bold;
        text-align: center;
    }}
    
    QTabBar::tab:selected {{
        background-color: {theme['accent']};
        color: white;
        text-align: center;
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {theme['bg_tertiary']};
        text-align: center;
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
        "antivirus_mode": "АНТИВИРУС",
        "analysis_mode": "АНАЛИЗ ФАЙЛОВ",
        "settings": "⚙ Настройки",
        "history": "📜 История",
        "quarantine": "⚠️ Карантин",
        "select_file": "Выбрать файл",
        "analyze_btn": "🚀 ЗАПУСТИТЬ АНАЛИЗ",
        "av_on": "⏹️ ВЫКЛ",
        "av_off": "▶️ ВКЛ",
        "av_status_on": "Антивирус: ВКЛ",
        "av_status_off": "Антивирус: ВЫКЛ",
        "save": "Сохранить",
        "cancel": "Отмена",
        "back": "← Назад",
        "theme": "Тема оформления",
        "analysis_time": "Время анализа:",
        "network_check": "Отключать сеть (рекомендуется)",
        "monitored_folders": "Мониторинг папок:",
        "auto_quarantine": "Авто-карантин угроз",
        "scan_on_access": "Сканирование при доступе",
        "language_label": "Язык/Language:",
        "add_folder": "Добавить",
        "remove_folder": "Удалить",
        "event_log": "Журнал событий антивируса",
        "log_placeholder": "Здесь будут отображаться события антивируса...",
        "protection_status": "Статус защиты",
        "folder_monitoring": "Мониторинг папок",
        "back_to_menu": "← Назад к главному меню",
        "quarantine_title": "Карантин - Обнаруженные угрозы",
        "quarantine_info": "Файлы в карантине обезврежены и не могут нанести вред системе.",
        "quarantine_empty": "Карантин пуст",
        "refresh": "Обновить",
        "restore": "Восстановить",
        "delete_forever": "Удалить навсегда",
        "close": "Закрыть",
        "col_date": "Дата",
        "col_filename": "Имя файла",
        "col_path": "Оригинальный путь",
        "col_reason": "Причина",
        "col_id": "ID",
        "restore_confirm": "Вы уверены, что хотите восстановить этот файл? Убедитесь, что он безопасен!",
        "restore_success": "Файл успешно восстановлен!",
        "restore_error": "Не удалось восстановить файл",
        "delete_confirm": "Вы уверены, что хотите удалить этот файл НАВСЕГДА?\nЭто действие необратимо!",
        "delete_success": "Файл успешно удален!",
        "history_title": "История сканирований файлов",
        "history_info": "Здесь отображаются все файлы, которые были проанализированы.",
        "history_empty": "История пуста",
        "clear_history": "Очистить историю",
        "clear_history_confirm": "Вы уверены, что хотите очистить всю историю сканирований?",
        "col_status": "Статус",
        "col_threats": "Угрозы",
        "col_file": "Файл",
        "status_clean": "БЕЗОПАСНЫЙ",
        "status_suspicious": "ПОДОЗРИТЕЛЬНЫЙ",
        "status_malicious": "ОПАСНЫЙ",
        "settings_title": "Настройки приложения",
        "theme_group": "Тема оформления",
        "analysis_settings_group": "Настройки анализа",
        "application_settings": "Настройки приложения",
        "analysis_settings": "Настройки анализа",
        "timeout_label": "Время анализа (сек):",
        "app_language": "Язык интерфейса",
        "av_running": "Антивирус запущен. Мониторинг: ",
        "av_start_error": "Не удалось запустить антивирус:",
        "av_stop_error": "Ошибка остановки: ",
        "av_start_msg": "Защита реального времени включена!\n\nМониторимые папки:\n",
        "auto_quarantine_msg": "Все подозрительные файлы будут автоматически помещены в карантин.",
        "folder_exists": "Эта папка уже добавлена",
        "folder_added": "Добавлена папка: ",
        "folder_removed": "Удалена папка: ",
        "no_folders": "Не найдены стандартные папки для мониторинга.\nАнтивирус не может быть запущен.",
        "new_file_detected": "Обнаружен новый файл: ",
        "file_is_virus": " - ВИРУС!",
        "file_is_clean": " - чистый",
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
        "logs_tab": "Журнал      ",
        "results_tab": "Результаты   ",
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
        "no_threats": "Нет угроз",
        "yes": "Да",
        "no": "Нет",
        "suspicious_file_warning": "Подозрительный файл обнаружен. Рекомендуется дополнительная проверка.",
        # Подсказки настроек
        "poly_check_tooltip": "Использовать полиморфный движок по умолчанию (устарело)",
        "network_check_tooltip": "Автоматически отключать сеть при анализе",
        "deep_scan_tooltip": "Выполнять полный эвристический анализ",
        "ml_analysis_tooltip": "Использовать машинное обучение для классификации угроз",
        "multi_thread_tooltip": "Использовать несколько потоков для ускорения сканирования",
        "auto_quarantine_tooltip": "Автоматически помещать опасные файлы в карантин",
        "scan_on_access_tooltip": "Сканировать файлы при каждом обращении к ним",
        "docker_tooltip": "Запускать подозрительные файлы в Docker контейнере",
        "behavioral_tooltip": "Использовать эмуляцию Windows API для анализа поведения",
        "panic_button_tooltip": "Отображать кнопку для немедленной остановки всех процессов",
        "auto_update_tooltip": "Автоматически обновлять базу сигнатур вирусов",
        "reset_defaults": "Сбросить настройки",
        "confirm_reset": "Подтверждение сброса",
        "reset_confirm_msg": "Вы уверены, что хотите сбросить все настройки?",
        "sensitivity_low": "Низкая",
        "sensitivity_medium": "Средняя",
        "sensitivity_high": "Высокая",
        "log_level_low": "Низкий",
        "log_level_medium": "Средний",
        "log_level_high": "Высокий",
        "antivirus_settings_group": "Настройки антивируса",
        "sandbox_settings_group": "Настройки песочницы",
        "interface_settings_group": "Настройки интерфейса",
        "security_settings_group": "Настройки безопасности",
        "interface_language_label": "Язык интерфейса:",
        "notifications_check": "Показывать уведомления",
        "sound_check": "Звуковые уведомления",
        "minimize_tray_check": "Сворачивать в трей",
        "panic_button_check": "Кнопка экстренной остановки",
        "auto_update_check": "Автообновление сигнатур",
        "update_interval_label": "Интервал обновления (часы):",
        "select_folder_btn": "📁 Выбрать папку"
    },
    "English": {
        "title": "RedSand Secure",
        "subtitle": "",
        "antivirus_mode": "ANTIVIRUS",
        "analysis_mode": "FILE ANALYSIS",
        "settings": "⚙ Settings",
        "history": "📜 History",
        "quarantine": "⚠️ Quarantine",
        "select_file": "Select File",
        "analyze_btn": "🚀 START ANALYSIS",
        "av_on": "⏹️ OFF",
        "av_off": "▶️ ON",
        "av_status_on": "Antivirus: ON",
        "av_status_off": "Antivirus: OFF",
        "save": "Save",
        "cancel": "Cancel",
        "back": "← Back",
        "theme": "Theme",
        "analysis_time": "Analysis Time:",
        "network_check": "Disable network (recommended)",
        "monitored_folders": "Monitored Folders:",
        "auto_quarantine": "Auto-quarantine threats",
        "scan_on_access": "Scan on access",
        "language_label": "Language/Language:",
        "add_folder": "Add",
        "remove_folder": "Remove",
        "event_log": "Antivirus Event Log",
        "log_placeholder": "Antivirus events will be displayed here...",
        "protection_status": "Protection Status",
        "folder_monitoring": "Folder Monitoring",
        "back_to_menu": "← Back to Main Menu",
        "quarantine_title": "Quarantine - Detected Threats",
        "quarantine_info": "Files in quarantine are neutralized and cannot harm the system.",
        "quarantine_empty": "Quarantine is empty",
        "refresh": "Refresh",
        "restore": "Restore",
        "delete_forever": "Delete Forever",
        "close": "Close",
        "col_date": "Date",
        "col_filename": "File Name",
        "col_path": "Original Path",
        "col_reason": "Reason",
        "col_id": "ID",
        "restore_confirm": "Are you sure you want to restore this file? Make sure it is safe!",
        "restore_success": "File successfully restored!",
        "restore_error": "Failed to restore file",
        "delete_confirm": "Are you sure you want to delete this file FOREVER?\nThis action is irreversible!",
        "delete_success": "File successfully deleted!",
        "history_title": "Scan History",
        "history_info": "All analyzed files are displayed here.",
        "history_empty": "History is empty",
        "clear_history": "Clear History",
        "clear_history_confirm": "Are you sure you want to clear all scan history?",
        "col_status": "Status",
        "col_threats": "Threats",
        "col_file": "File",
        "status_clean": "SAFE",
        "status_suspicious": "SUSPICIOUS",
        "status_malicious": "DANGEROUS",
        "settings_title": "Application Settings",
        "theme_group": "Theme",
        "analysis_settings_group": "Analysis Settings",
        "application_settings": "Application Settings",
        "analysis_settings": "Analysis Settings",
        "timeout_label": "Analysis Time (sec):",
        "app_language": "Interface Language",
        "av_running": "Antivirus running. Monitoring: ",
        "av_start_error": "Failed to start antivirus:",
        "av_stop_error": "Stop error: ",
        "av_start_msg": "Real-time protection enabled!\n\nMonitored folders:\n",
        "auto_quarantine_msg": "All suspicious files will be automatically quarantined.",
        "folder_exists": "This folder is already added",
        "folder_added": "Folder added: ",
        "folder_removed": "Folder removed: ",
        "no_folders": "No standard folders found for monitoring.\nAntivirus cannot be started.",
        "new_file_detected": "New file detected: ",
        "file_is_virus": " - VIRUS!",
        "file_is_clean": " - clean",
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
        "logs_tab": "Logs      ",
        "results_tab": "Results   ",
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
        "no_threats": "None",
        "yes": "Yes",
        "no": "No",
        "suspicious_file_warning": "Suspicious file detected. Additional verification recommended.",
        # Settings tooltips
        "poly_check_tooltip": "Use polymorphic engine by default (deprecated)",
        "network_check_tooltip": "Automatically disable network during analysis",
        "deep_scan_tooltip": "Perform full heuristic analysis",
        "ml_analysis_tooltip": "Use machine learning for threat classification",
        "multi_thread_tooltip": "Use multiple threads to speed up scanning",
        "auto_quarantine_tooltip": "Automatically quarantine dangerous files",
        "scan_on_access_tooltip": "Scan files on every access",
        "docker_tooltip": "Run suspicious files in Docker container",
        "behavioral_tooltip": "Use Windows API emulation for behavior analysis",
        "panic_button_tooltip": "Display button for immediate stop of all processes",
        "auto_update_tooltip": "Automatically update virus signatures database",
        "reset_defaults": "Reset Settings",
        "confirm_reset": "Confirm Reset",
        "reset_confirm_msg": "Are you sure you want to reset all settings?",
        "antivirus_settings_group": "Real-time Antivirus Settings",
        "deep_scan_check": "Deep file analysis",
        "ml_analysis_check": "Use ML classifier",
        "multi_thread_check": "Multi-threaded scanning",
        "thread_count_label": "Number of threads:",
        "auto_quarantine_check": "Automatic quarantine",
        "scan_on_access_check": "Scan on access",
        "sensitivity_label": "Sensitivity:",
        "sensitivity_low": "Low",
        "sensitivity_medium": "Medium",
        "sensitivity_high": "High",
        "sandbox_settings_group": "Sandbox Settings",
        "log_level_label": "Log level:",
        "log_level_low": "Low",
        "log_level_medium": "Medium",
        "log_level_high": "High",
        "interface_settings_group": "Interface Settings",
        "security_settings_group": "Security Settings",
        "interface_language_label": "Interface Language:",
        "notifications_check": "Show notifications",
        "sound_check": "Sound notifications",
        "minimize_tray_check": "Minimize to tray",
        "panic_button_check": "Emergency stop button",
        "auto_update_check": "Auto-update signatures",
        "update_interval_label": "Update interval (hours):",
        "select_folder_btn": "📁 Select Folder",
        "reset_defaults": "Reset Settings",
        "confirm_reset": "Confirm Reset",
        "reset_confirm_msg": "Are you sure you want to reset all settings?"
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
        
        # Кнопка выхода в правом верхнем углу (маленькая, прямоугольная, без эмодзи)
        self.btn_exit = QPushButton("Выйти")
        self.btn_exit.setObjectName("exitBtn")
        self.btn_exit.setFixedSize(80, 30)  # Маленький прямоугольный размер
        self.btn_exit.setStyleSheet("""
            QPushButton#exitBtn {
                background-color: #c0392b;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                padding: 5px 10px;
            }
            QPushButton#exitBtn:hover {
                background-color: #e74c3c;
            }
            QPushButton#exitBtn:pressed {
                background-color: #a93226;
            }
        """)
        self.btn_exit.clicked.connect(lambda: self.parent_ref.close() if self.parent_ref else None)
        self.btn_exit.setToolTip("Закрыть приложение / Exit")
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
        
        # Кнопка Антивирус - убрано "Реального времени" и эмодзи
        self.btn_antivirus = QPushButton("АНТИВИРУС")
        self.btn_antivirus.setObjectName("modeBtn")
        self.btn_antivirus.clicked.connect(lambda: self.mode_selected.emit("antivirus"))
        self.btn_antivirus.setToolTip("Мониторинг системы и автоматическая защита")
        modes_layout.addWidget(self.btn_antivirus)
        
        # Кнопка Анализ файлов - без переноса строки
        # Используем язык по умолчанию (Русский) при инициализации
        default_lang = LANGUAGES["Русский"]
        self.btn_analysis = QPushButton(default_lang["analysis_mode"])
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
        
        # Exit button translation
        if self.parent_ref.current_lang == "English":
            self.btn_exit.setText("Exit")
        else:
            self.btn_exit.setText("Выйти")
        
        self.btn_antivirus.setText(lang["antivirus_mode"])
        self.btn_analysis.setText(lang["analysis_mode"])
        self.btn_settings.setText(lang["settings"])
        self.btn_history.setText(lang["history"])
        self.btn_quarantine.setText(lang["quarantine"])


class AntivirusPanel(QWidget):
    """Панель управления антивирусом с мониторингом новых файлов"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_ref = parent
        self.av_active = False
        self.av_monitor = None
        self.setup_ui()
        self.file_watcher = None  # QFileSystemWatcher для отслеживания новых файлов
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title_label = QLabel("АНТИВИРУС")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Статус
        status_group = QGroupBox("Статус защиты")
        status_layout = QVBoxLayout(status_group)
        
        self.av_status_label = QLabel("Антивирус: ВЫКЛ")
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
        # Удалены папки Downloads, Desktop, Documents по требованию
        self.folder_list.addItems([
            # Папки добавляются пользователем вручную
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
        
        # Получаем текущий язык для чекбоксов
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        
        self.chk_auto_quarantine = QCheckBox(lang.get("auto_quarantine", "Автоматический карантин угроз"))
        self.chk_auto_quarantine.setChecked(True)
        monitor_layout.addWidget(self.chk_auto_quarantine)
        
        self.chk_scan_on_access = QCheckBox(lang.get("scan_on_access", "Сканирование при доступе к файлу"))
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
        """Включение/выключение антивируса с мониторингом новых файлов"""
        if not self.parent_ref:
            return
            
        # Получаем текущий язык
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        
        if self.av_active:
            # Выключаем
            try:
                if self.av_monitor:
                    self.av_monitor.stop()
                # Останавливаем QFileSystemWatcher
                if self.file_watcher:
                    self.file_watcher.deleteLater()
                    self.file_watcher = None
                self.av_active = False
                self.btn_toggle_av.setChecked(False)
                self.btn_toggle_av.setText("▶️ ВКЛ")
                self.av_status_label.setText("Антивирус: ВЫКЛ")
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
                
                # Инициализируем QFileSystemWatcher для отслеживания новых файлов
                from PyQt5.QtCore import QFileSystemWatcher
                self.file_watcher = QFileSystemWatcher()
                self.file_watcher.addPaths(monitor_paths)
                self.file_watcher.directoryChanged.connect(self.on_directory_changed)
                
                self.av_active = True
                self.btn_toggle_av.setText(lang["av_on"])
                self.av_status_label.setText(lang["av_status_on"])
                self.av_status_label.setStyleSheet("color: #059669; font-weight: bold; font-size: 24px;")
                self.log_event(f"{lang['av_running']} {', '.join(monitor_paths)}")
                
                QMessageBox.information(self, lang.get("av_activated", "Antivirus Activated"),
                    f"{lang.get('av_start_msg', 'Real-time protection enabled!')}\n\n{lang.get('monitored_folders', 'Monitored folders:')}\n{chr(10).join(monitor_paths)}\n\n{lang.get('auto_quarantine_msg', 'All suspicious files will be automatically quarantined.')}")
                    
            except Exception as e:
                self.log_event(f"{lang.get('av_start_error', 'Failed to start antivirus:')} {e}")
                QMessageBox.critical(self, lang.get("error", "Error"), f"{lang.get('av_start_error', 'Failed to start antivirus:')}\n{str(e)}")
                self.btn_toggle_av.setChecked(False)
    
    def on_directory_changed(self, directory_path):
        """Обработка изменений в директории - обнаружение новых файлов / Handle directory changes - detect new files"""
        try:
            # Небольшая задержка чтобы файл полностью записался / Small delay for file to be fully written
            import time
            time.sleep(0.5)
            
            self.log_event(f"Directory changed: {directory_path}")
            
            # Проверяем файлы в директории / Check files in directory
            if os.path.exists(directory_path):
                try:
                    files = os.listdir(directory_path)
                except PermissionError:
                    self.log_event(f"Permission denied: {directory_path}")
                    return
                    
                for filename in files:
                    file_path = os.path.join(directory_path, filename)
                    
                    # Пропускаем директории / Skip directories
                    if os.path.isdir(file_path):
                        continue
                        
                    # Проверяем только новые файлы (созданные/модифицированные в последние 2 минуты) 
                    # Check only new files (created/modified in last 2 minutes)
                    try:
                        mtime = os.path.getmtime(file_path)
                        ctime = os.path.getctime(file_path)
                        import datetime
                        now = datetime.datetime.now().timestamp()
                        
                        # Файл новый если создан или изменен в последние 2 минуты
                        # File is new if created or modified in last 2 minutes
                        is_new = (now - mtime < 120) or (now - ctime < 120)
                        
                        if not is_new:
                            continue
                            
                        # Проверяем расширение / Check extension
                        ext = os.path.splitext(filename)[1].lower()
                        monitored_exts = ['.exe', '.bat', '.cmd', '.ps1', '.vbs', '.js', '.msi', '.dll', '.scr', '.pif', '.com', '.txt']
                        
                        if ext in monitored_exts and not filename.startswith('~$') and not filename.startswith('.'):
                            lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
                            self.log_event(f"{lang.get('new_file_detected', 'New file detected: ')}{filename}")
                            
                            # Запускаем сканирование в отдельном потоке / Start scanning in separate thread
                            worker = AnalysisWorker(file_path)
                            worker.result_ready.connect(self.on_new_file_scanned)
                            worker.error_occurred.connect(lambda err: self.log_event(f"[-] Error scanning {filename}: {err}"))
                            worker.start()
                    except (OSError, IOError) as e:
                        pass  # Файл может быть еще не готов / File may not be ready yet
                        
            # Перезапускаем watcher если директория изменилась / Restart watcher if directory changed
            if self.file_watcher and directory_path not in self.file_watcher.directories():
                self.file_watcher.addPath(directory_path)
        except Exception as e:
            self.log_event(f"Error processing changes: {e}")
    
    def on_new_file_scanned(self, scan_result: dict):
        """Обработка результатов сканирования нового файла / Handle new file scan results"""
        threat_level = scan_result.get('threat_level', 'CLEAN')
        file_path = scan_result.get('file_path', 'Unknown')
        file_name = os.path.basename(file_path)
        detected_threats = scan_result.get('detected_threats', [])
        
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        
        if threat_level == 'MALICIOUS':
            threat_info = ""
            if detected_threats:
                threat_info = f" ({', '.join(detected_threats)})"
            self.log_event(f"🚨 {lang.get('status_malicious', 'MALICIOUS')}! {file_name}{threat_info} - {lang.get('file_is_virus', 'VIRUS!')}")
            # Автоматический карантин / Auto quarantine
            if self.chk_auto_quarantine.isChecked():
                try:
                    reason = f"{threat_level}: Risk Score {scan_result.get('risk_score', 1.0)}"
                    if detected_threats:
                        reason += f" - {', '.join(detected_threats[:2])}"
                    self.parent_ref.quarantine_manager.move_to_quarantine(file_path=file_path, reason=reason)
                    self.log_event(f"⚠️ {lang.get('file_quarantined_log', 'File quarantined:')} {reason}")
                except Exception as e:
                    self.log_event(f"❌ {lang.get('quarantine_error_log', 'Quarantine error:')} {e}")
        elif threat_level == 'SUSPICIOUS':
            self.log_event(f"⚠️ {lang.get('status_suspicious', 'SUSPICIOUS')} - {file_name}")
        else:
            self.log_event(f"✅ {lang.get('status_clean', 'CLEAN')} - {file_name} - {lang.get('file_is_clean', 'clean')}")
    
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
    
    # Сигналы для обновления прогресса при сканировании папки
    progress = pyqtSignal(int, str)  # прогресс, текст
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_ref = parent
        self.worker_thread = None
        self.worker = None
        self.analysis_completed = False
        self.setup_ui()
        
        # Подключаем сигнал прогресса к слоту обновления
        self.progress.connect(self.update_progress)
    
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
        
        # Кнопки выбора файла и папки в одну строку
        btn_layout = QHBoxLayout()
        
        self.btn_select_file = QPushButton(lang["select_file"])
        self.btn_select_file.setObjectName("actionBtn")
        self.btn_select_file.clicked.connect(self.select_file)
        btn_layout.addWidget(self.btn_select_file)
        
        self.btn_select_dir = QPushButton(lang.get("select_folder_btn", "📁 Выбрать папку"))
        self.btn_select_dir.setObjectName("actionBtn")
        self.btn_select_dir.clicked.connect(self.select_directory)
        btn_layout.addWidget(self.btn_select_dir)
        
        file_layout.addLayout(btn_layout)
        
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
    
    def select_directory(self):
        """Выбор папки для сканирования всех файлов"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Выберите папку для сканирования", ""
        )
        if dir_path:
            self.file_path_edit.setText(dir_path)
            self.log_message('INFO', f"Выбрана папка для сканирования: {dir_path}")
    
    def start_analysis(self):
        """Запуск анализа файла или папки в отдельном потоке без блокировки GUI"""
        target_path = self.file_path_edit.text().strip()
        
        # Получаем язык ПЕРЕД использованием
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        
        if not target_path or not os.path.exists(target_path):
            QMessageBox.warning(self, lang.get("warning", "Warning"), 
                               lang.get("no_file_selected_error", "Please select an existing file for analysis."))
            return
        
        # Проверяем, не запущен ли уже анализ
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, lang.get("warning", "Warning"),
                               lang.get("analysis_in_progress", "Analysis is already in progress!"))
            return
        
        self.btn_analyze.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.results_summary.setVisible(True)
        self.results_table.setVisible(False)
        self.analysis_completed = False
        
        # Определяем тип цели: файл или папка
        is_directory = os.path.isdir(target_path)
        
        if is_directory:
            self.log_message('INFO', f"{lang['analysis_start_log']} папка: {target_path}")
            self.log_message('INFO', 'Сканирование всех файлов в папке...')
            
            # Сканируем папку
            scanner = ExtendedVirusScanner()
            try:
                results = []
                total_files = 0
                malicious_count = 0
                
                for root, dirs, files in os.walk(target_path):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        total_files += 1
                        
                        self.progress.emit(int((total_files / max(total_files, 1)) * 100), f"Сканирование: {filename}")
                        
                        scan_result = scanner.scan_file(file_path)
                        results.append({
                            'file': file_path,
                            'threat_level': scan_result.threat_level.value,
                            'score': scan_result.score,
                            'threats': scan_result.threats_found
                        })
                        
                        if scan_result.threat_level == ThreatLevel.MALICIOUS:
                            malicious_count += 1
                            self.log_message('MALICIOUS', f"Угроза обнаружена: {file_path} - {scan_result.threats_found}")
                        elif scan_result.threat_level == ThreatLevel.SUSPICIOUS:
                            self.log_message('SUSPICIOUS', f"Подозрительный файл: {file_path}")
                        else:
                            self.log_message('CLEAN', f"Чистый файл: {file_path}")
                
                # Показываем сводку
                self.progress.emit(100, "Сканирование завершено!")
                self.show_directory_results(results, total_files, malicious_count)
                self.btn_analyze.setEnabled(True)
                return
                
            except Exception as e:
                self.log_message('ERROR', f"Ошибка сканирования папки: {str(e)}")
                self.btn_analyze.setEnabled(True)
                return
        else:
            self.log_message('INFO', f"{lang['analysis_start_log']} {target_path}")
            self.log_message('INFO', lang['using_virus_scanner'])
        
        # Добавляем запись в историю сканирований
        scan_record = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'file_name': os.path.basename(target_path),
            'file_path': target_path,
            'status': 'IN_PROGRESS',
            'threats': 0
        }
        if self.parent_ref:
            self.parent_ref.scan_history.append(scan_record)
        
        # Создаём и запускаем worker в отдельном потоке (только для单个 файлов)
        use_poly = self.poly_check.isChecked() if hasattr(self, 'poly_check') else False
        timeout = self.timeout_spin.value() if hasattr(self, 'timeout_spin') else 60
        
        self.worker = AnalysisWorker(target_path, use_poly=use_poly, timeout=timeout)
        self.worker.progress.connect(self.update_progress)
        self.worker.result_ready.connect(self.on_analysis_complete)
        self.worker.error_occurred.connect(self.on_analysis_error)
        self.worker.start()
    
    def update_progress(self, value: int, text: str):
        """Обновление прогресс-бара из потока"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(text)
        self.log_message('INFO', text)
    
    def on_analysis_complete(self, scan_result: dict):
        """Обработка результатов анализа (вызывается в главном потоке)"""
        if self.analysis_completed:
            return
        self.analysis_completed = True
        
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        is_ru = (self.parent_ref.current_lang if self.parent_ref else "Русский") == "Русский"
        
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
        
        # Автоматически помещаем в карантин ТОЛЬКО опасные файлы (MALICIOUS)
        if threat_level == 'MALICIOUS' and self.parent_ref:
            try:
                reason = f"{threat_level}: Risk Score {risk_score}"
                if detected_threats:
                    reason += f" - {', '.join(detected_threats[:2])}"
                # Используем правильный метод move_to_quarantine
                self.parent_ref.quarantine_manager.move_to_quarantine(
                    file_path=self.file_path_edit.text().strip(),
                    reason=reason
                )
                self.log_message('WARNING', f"{lang['file_quarantined_log']} {reason}")
            except Exception as e:
                self.log_message('ERROR', f"{lang['quarantine_error_log']} {e}")
        elif threat_level == 'SUSPICIOUS':
            # Для подозрительных файлов только предупреждение, без карантина
            self.log_message('INFO', lang.get('suspicious_file_warning', 'Подозрительный файл обнаружен. Рекомендуется дополнительная проверка.'))
        
        self.progress_bar.setValue(100)
        self.progress_label.setText(lang["analysis_complete"])
        self.log_message('SUCCESS', lang["analysis_complete"])
        
        # Показываем результаты
        self.results_summary.setVisible(False)
        self.results_table.setVisible(True)
        
        # Формируем данные для таблицы результатов
        file_type = lang.get("file_type", "File Type")
        size_label = lang.get("size", "Size")
        
        # Безопасное получение размера файла
        file_path = self.file_path_edit.text().strip()
        try:
            if os.path.exists(file_path):
                size_value = f"{os.path.getsize(file_path)} bytes"
            else:
                size_value = "Unknown (Quarantined)"
        except Exception:
            size_value = "Unknown"
        
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
            msg = f"⚠️ {lang['status_malicious']}!\n\n{recommendation}\n\n{lang.get('action_quarantine', 'Quarantine')}: {os.path.basename(self.file_path_edit.text().strip())}"
            QMessageBox.warning(self, msg_title, msg)
        elif threat_level == 'SUSPICIOUS':
            msg = f"⚠️ {lang['status_suspicious']}!\n\n{recommendation}"
            QMessageBox.warning(self, msg_title, msg)
        else:
            msg = f"✅ {lang['status_clean']}!\n\n{recommendation}"
            QMessageBox.information(self, msg_title, msg)
    
    def on_analysis_error(self, error_msg: str):
        """Обработка ошибки анализа (вызывается в главном потоке)"""
        if self.analysis_completed:
            return
        self.analysis_completed = True
        
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        
        self.progress_bar.setValue(100)
        self.progress_label.setText(f"❌ Error: {error_msg}")
        self.log_message('ERROR', f"{lang.get('scan_error_log', 'Scan error:')} {error_msg}")
        
        self.results_summary.setVisible(False)
        self.results_table.setVisible(True)
        self.results_table.setRowCount(1)
        
        error_param = QTableWidgetItem(lang.get("error", "Error"))
        error_param.setFlags(error_param.flags() & ~Qt.ItemIsEditable)
        error_param.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.results_table.setItem(0, 0, error_param)
        
        error_value = QTableWidgetItem(error_msg)
        error_value.setFlags(error_value.flags() & ~Qt.ItemIsEditable)
        error_value.setFont(QFont("Segoe UI", 12))
        error_value.setBackground(QColor("#666666"))
        error_value.setForeground(QColor("#ffffff"))
        self.results_table.setItem(0, 1, error_value)
        
        self.btn_analyze.setEnabled(True)
        QMessageBox.critical(self, lang.get("error", "Error"), f"{lang.get('analysis_error', 'Analysis failed:')} {error_msg}")
    
    def log_message(self, level: str, message: str):
        """Запись сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {'INFO': '#4CAF50', 'WARNING': '#FF9800', 'ERROR': '#F44336', 'SUCCESS': '#00BCD4', 'MALICIOUS': '#dc2626', 'SUSPICIOUS': '#d97706', 'CLEAN': '#059669'}
        color = colors.get(level, '#FFFFFF')
        self.log_text.append(f'<span style="color: {color};">[{timestamp}] [{level}] {message}</span>')
    
    def show_directory_results(self, results: list, total_files: int, malicious_count: int):
        """Показывает результаты сканирования папки"""
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        
        self.results_summary.setVisible(False)
        self.results_table.setVisible(True)
        
        # Показываем сводку
        summary_text = f"Всего файлов: {total_files}\n"
        summary_text += f"Обнаружено угроз: {malicious_count}\n"
        summary_text += f"Чистых файлов: {total_files - malicious_count}\n"
        
        if malicious_count > 0:
            summary_text += f"\n⚠️ ОБНАРУЖЕНЫ УГРОЗЫ! Рекомендуется карантин или удаление."
        else:
            summary_text += f"\n✅ Все файлы чистые!"
        
        self.results_summary.setText(summary_text)
        self.results_summary.setVisible(True)
        
        # Заполняем таблицу результатами (показываем только угрозы и подозрительные)
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Файл", "Статус", "Угрозы", "Путь"])
        
        threat_rows = []
        for r in results:
            if r['threat_level'] in ['MALICIOUS', 'SUSPICIOUS']:
                threat_rows.append(r)
        
        self.results_table.setRowCount(len(threat_rows))
        
        for i, r in enumerate(threat_rows):
            # Файл
            file_item = QTableWidgetItem(os.path.basename(r['file']))
            file_item.setForeground(QColor("#ffffff"))
            self.results_table.setItem(i, 0, file_item)
            
            # Статус
            status = r['threat_level']
            status_color = "#dc2626" if status == 'MALICIOUS' else "#d97706"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor(status_color))
            self.results_table.setItem(i, 1, status_item)
            
            # Угрозы
            threats = ', '.join(r['threats']) if r['threats'] else '-'
            threats_item = QTableWidgetItem(threats)
            threats_item.setForeground(QColor("#ffffff"))
            self.results_table.setItem(i, 2, threats_item)
            
            # Путь
            path_item = QTableWidgetItem(r['file'])
            path_item.setForeground(QColor("#b0b0b0"))
            self.results_table.setItem(i, 3, path_item)
        
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        
        self.btn_analyze.setEnabled(True)
    
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
        
        self.btn_refresh = QPushButton(self.tr("refresh"))
        self.btn_refresh.setObjectName("secondaryBtn")
        self.btn_refresh.setMinimumHeight(45)
        self.btn_refresh.clicked.connect(self.load_history)
        btn_layout.addWidget(self.btn_refresh)
        
        self.btn_clear = QPushButton(self.tr("Clear History"))
        self.btn_clear.setObjectName("dangerBtn")
        self.btn_clear.setMinimumHeight(45)
        self.btn_clear.clicked.connect(self.clear_history)
        btn_layout.addWidget(self.btn_clear)
        
        btn_layout.addStretch()
        
        # Кнопка "Закрыть" - уменьшена до размера кнопки "Сбросить настройки"
        self.btn_close = QPushButton(self.tr("Close"))
        self.btn_close.setObjectName("secondaryBtn")
        self.btn_close.setMinimumHeight(45)
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
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(lang["clear_history"])
        msg_box.setText(lang.get(confirm_key, lang["clear_history_confirm"]))
        
        # Локализованные кнопки
        yes_btn = QPushButton(lang.get("yes", "Да"))
        no_btn = QPushButton(lang.get("no", "Нет"))
        
        msg_box.addButton(yes_btn, QMessageBox.YesRole)
        msg_box.addButton(no_btn, QMessageBox.NoRole)
        
        reply = msg_box.exec()
        
        if reply == 0 and self.parent_ref:  # 0 = YesRole
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
        
        self.title_label = QLabel("Карантин - Обнаруженные угрозы")
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
        self.btn_refresh = QPushButton(self.tr("refresh"))
        self.btn_refresh.setObjectName("secondaryBtn")
        self.btn_refresh.setMinimumHeight(45)
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
        self.btn_restore.setMinimumHeight(45)
        self.btn_restore.clicked.connect(self.restore_selected)
        self.btn_restore.setEnabled(False)
        center_layout.addWidget(self.btn_restore)
        
        self.btn_delete = QPushButton(self.tr("Delete Permanently"))
        self.btn_delete.setObjectName("dangerBtn")
        self.btn_delete.setMinimumHeight(45)
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_delete.setEnabled(False)
        center_layout.addWidget(self.btn_delete)
        
        btn_layout.addWidget(center_widget)
        btn_layout.addStretch()
        
        # Кнопка "Закрыть" - уменьшена до размера кнопки "Сбросить настройки"
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
            lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
            
            reply = QMessageBox.warning(self, lang.get("delete_forever", "Delete Forever"),
                lang.get("delete_confirm", "Are you sure you want to delete this file FOREVER?\nThis action is irreversible!"),
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
            lang = LANGUAGES.get(self.current_lang, LANGUAGES["Русский"])
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
        self.setMinimumSize(700, 650)
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
        
        # Создаем скролл-область для настроек
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        # === Настройки анализа ===
        analysis_group = QGroupBox(lang["analysis_settings_group"])
        analysis_layout = QVBoxLayout(analysis_group)
        
        timeout_layout = QHBoxLayout()
        timeout_label = QLabel(lang["timeout_label"])
        timeout_layout.addWidget(timeout_label)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(self.settings.get('timeout', 60))
        self.timeout_spin.setSuffix(" сек")
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        analysis_layout.addLayout(timeout_layout)
        
        self.network_check = QCheckBox(lang["network_check"])
        self.network_check.setChecked(self.settings.get('auto_disable_network', True))
        self.network_check.setToolTip(lang.get("network_check_tooltip", "Автоматически отключать сеть при анализе"))
        analysis_layout.addWidget(self.network_check)
        
        # Дополнительные настройки анализа
        self.deep_scan_check = QCheckBox(lang.get("deep_scan_check", "Глубокий анализ файлов"))
        self.deep_scan_check.setChecked(self.settings.get('deep_scan', True))
        self.deep_scan_check.setToolTip(lang.get("deep_scan_tooltip", "Выполнять полный эвристический анализ"))
        analysis_layout.addWidget(self.deep_scan_check)
        
        self.ml_analysis_check = QCheckBox(lang.get("ml_analysis_check", "Использовать ML классификатор"))
        self.ml_analysis_check.setChecked(self.settings.get('ml_analysis', True))
        self.ml_analysis_check.setToolTip(lang.get("ml_analysis_tooltip", "Использовать машинное обучение для классификации угроз"))
        analysis_layout.addWidget(self.ml_analysis_check)
        
        self.multi_thread_check = QCheckBox(lang.get("multi_thread_check", "Многопоточное сканирование"))
        self.multi_thread_check.setChecked(self.settings.get('multi_thread', True))
        self.multi_thread_check.setToolTip(lang.get("multi_thread_tooltip", "Использовать несколько потоков для ускорения сканирования"))
        analysis_layout.addWidget(self.multi_thread_check)
        
        thread_layout = QHBoxLayout()
        thread_label = QLabel(lang.get("thread_count_label", "Количество потоков:"))
        thread_layout.addWidget(thread_label)
        self.thread_spin = QSpinBox()
        self.thread_spin.setRange(1, 16)
        self.thread_spin.setValue(self.settings.get('thread_count', 4))
        self.thread_spin.setSuffix(" шт")
        thread_layout.addWidget(self.thread_spin)
        thread_layout.addStretch()
        analysis_layout.addLayout(thread_layout)
        
        scroll_layout.addWidget(analysis_group)
        
        # === Настройки антивируса реального времени ===
        antivirus_group = QGroupBox(lang.get("antivirus_settings_group", "Настройки антивируса"))
        av_layout = QVBoxLayout(antivirus_group)
        
        self.auto_quarantine_check = QCheckBox(lang.get("auto_quarantine_check", "Автоматический карантин"))
        self.auto_quarantine_check.setChecked(self.settings.get('auto_quarantine', True))
        self.auto_quarantine_check.setToolTip(lang.get("auto_quarantine_tooltip", "Автоматически помещать подозрительные файлы в карантин"))
        av_layout.addWidget(self.auto_quarantine_check)
        
        self.scan_on_access_check = QCheckBox(lang.get("scan_on_access_check", "Сканирование при доступе"))
        self.scan_on_access_check.setChecked(self.settings.get('scan_on_access', True))
        self.scan_on_access_check.setToolTip(lang.get("scan_on_access_tooltip", "Сканировать файлы при каждом обращении к ним"))
        av_layout.addWidget(self.scan_on_access_check)
        
        sensitivity_layout = QHBoxLayout()
        sensitivity_label = QLabel(lang.get("sensitivity_label", "Чувствительность:"))
        sensitivity_layout.addWidget(sensitivity_label)
        self.sensitivity_combo = QComboBox()
        self.sensitivity_combo.addItems([lang.get("sensitivity_low", "Низкая"), 
                                         lang.get("sensitivity_medium", "Средняя"), 
                                         lang.get("sensitivity_high", "Высокая")])
        sens_idx = self.settings.get('sensitivity', 1)
        # Гарантируем, что индекс целочисленный
        if isinstance(sens_idx, str):
            try:
                sens_idx = int(sens_idx)
            except ValueError:
                sens_idx = 1
        elif not isinstance(sens_idx, int):
            sens_idx = 1
        # Проверяем диапазон
        sens_idx = max(0, min(2, sens_idx))
        self.sensitivity_combo.setCurrentIndex(sens_idx)
        sensitivity_layout.addWidget(self.sensitivity_combo)
        sensitivity_layout.addStretch()
        av_layout.addLayout(sensitivity_layout)
        
        scroll_layout.addWidget(antivirus_group)
        
        # === Настройки песочницы ===
        sandbox_group = QGroupBox(lang.get("sandbox_settings_group", "Настройки песочницы"))
        sandbox_layout = QVBoxLayout(sandbox_group)
        
        self.docker_check = QCheckBox(lang.get("docker_check", "Использовать Docker изоляцию"))
        self.docker_check.setChecked(self.settings.get('use_docker', True))
        self.docker_check.setToolTip(lang.get("docker_tooltip", "Запускать подозрительные файлы в Docker контейнере"))
        sandbox_layout.addWidget(self.docker_check)
        
        self.behavioral_check = QCheckBox(lang.get("behavioral_check", "Поведенческий анализ v2.0"))
        self.behavioral_check.setChecked(self.settings.get('behavioral_analysis', True))
        self.behavioral_check.setToolTip(lang.get("behavioral_tooltip", "Использовать эмуляцию Windows API для анализа поведения"))
        sandbox_layout.addWidget(self.behavioral_check)
        
        emu_timeout_layout = QHBoxLayout()
        emu_timeout_label = QLabel(lang.get("emu_timeout_label", "Таймаут эмуляции (сек):"))
        emu_timeout_layout.addWidget(emu_timeout_label)
        self.emu_timeout_spin = QSpinBox()
        self.emu_timeout_spin.setRange(5, 120)
        self.emu_timeout_spin.setValue(self.settings.get('emu_timeout', 10))
        self.emu_timeout_spin.setSuffix(" сек")
        emu_timeout_layout.addWidget(self.emu_timeout_spin)
        emu_timeout_layout.addStretch()
        sandbox_layout.addLayout(emu_timeout_layout)
        
        scroll_layout.addWidget(sandbox_group)
        
        # === Настройки интерфейса ===
        interface_group = QGroupBox(lang.get("interface_settings_group", "Настройки интерфейса"))
        interface_layout = QVBoxLayout(interface_group)
        
        lang_interface_layout = QHBoxLayout()
        lang_interface_label = QLabel(lang.get("interface_language_label", "Язык интерфейса:"))
        lang_interface_layout.addWidget(lang_interface_label)
        self.interface_lang_combo = QComboBox()
        self.interface_lang_combo.addItems(["Русский", "English"])
        current_lang_idx = 0 if self.settings.get('language', 'Русский') == 'Русский' else 1
        self.interface_lang_combo.setCurrentIndex(current_lang_idx)
        self.interface_lang_combo.currentTextChanged.connect(self.on_language_changed)
        lang_interface_layout.addWidget(self.interface_lang_combo)
        lang_interface_layout.addStretch()
        interface_layout.addLayout(lang_interface_layout)
        
        self.notifications_check = QCheckBox(lang.get("notifications_check", "Показывать уведомления"))
        self.notifications_check.setChecked(self.settings.get('show_notifications', True))
        interface_layout.addWidget(self.notifications_check)
        
        self.sound_check = QCheckBox(lang.get("sound_check", "Звуковые уведомления"))
        self.sound_check.setChecked(self.settings.get('sound_enabled', False))
        interface_layout.addWidget(self.sound_check)
        
        self.minimize_tray_check = QCheckBox(lang.get("minimize_tray_check", "Сворачивать в трей"))
        self.minimize_tray_check.setChecked(self.settings.get('minimize_to_tray', False))
        interface_layout.addWidget(self.minimize_tray_check)
        
        scroll_layout.addWidget(interface_group)
        
        # === Настройки безопасности ===
        security_group = QGroupBox(lang.get("security_settings_group", "Настройки безопасности"))
        security_layout = QVBoxLayout(security_group)
        
        self.panic_button_check = QCheckBox(lang.get("panic_button_check", "Кнопка экстренной остановки"))
        self.panic_button_check.setChecked(self.settings.get('panic_button_enabled', True))
        self.panic_button_check.setToolTip(lang.get("panic_button_tooltip", "Отображать кнопку для немедленной остановки всех процессов"))
        security_layout.addWidget(self.panic_button_check)
        
        self.auto_update_check = QCheckBox(lang.get("auto_update_check", "Автообновление сигнатур"))
        self.auto_update_check.setChecked(self.settings.get('auto_update_signatures', True))
        self.auto_update_check.setToolTip(lang.get("auto_update_tooltip", "Автоматически обновлять базу сигнатур вирусов"))
        security_layout.addWidget(self.auto_update_check)
        
        update_interval_layout = QHBoxLayout()
        update_interval_label = QLabel(lang.get("update_interval_label", "Интервал обновления (часы):"))
        update_interval_layout.addWidget(update_interval_label)
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setRange(1, 168)
        self.update_interval_spin.setValue(self.settings.get('update_interval', 24))
        self.update_interval_spin.setSuffix(" ч")
        update_interval_layout.addWidget(self.update_interval_spin)
        update_interval_layout.addStretch()
        security_layout.addLayout(update_interval_layout)
        
        self.log_level_layout = QHBoxLayout()
        log_level_label = QLabel(lang.get("log_level_label", "Уровень логирования:"))
        self.log_level_layout.addWidget(log_level_label)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems([lang.get("log_level_low", "Low"),
                                       lang.get("log_level_medium", "Medium"),
                                       lang.get("log_level_high", "High")])
        log_level = self.settings.get('log_level', 'Medium')
        log_levels_display = [lang.get("log_level_low", "Low"),
                              lang.get("log_level_medium", "Medium"),
                              lang.get("log_level_high", "High")]
        try:
            log_idx = log_levels_display.index(log_level)
        except ValueError:
            log_idx = 1
        self.log_level_combo.setCurrentIndex(log_idx)
        self.log_level_layout.addWidget(self.log_level_combo)
        self.log_level_layout.addStretch()
        security_layout.addLayout(self.log_level_layout)
        
        scroll_layout.addWidget(security_group)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Кнопка "Сбросить настройки" - переводится на английский
        self.btn_reset = QPushButton(lang.get("reset_defaults", "Reset Settings"))
        self.btn_reset.setObjectName("secondaryBtn")
        self.btn_reset.setFixedHeight(45)
        self.btn_reset.clicked.connect(self.reset_to_defaults)
        buttons_layout.addWidget(self.btn_reset)
        
        # Кнопка "Закрыть" - переводится на английский
        self.btn_close_settings = QPushButton(lang.get("close", "Close"))
        self.btn_close_settings.setObjectName("secondaryBtn")
        self.btn_close_settings.setFixedHeight(45)
        self.btn_close_settings.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_close_settings)
        
        layout.addLayout(buttons_layout)
    
    def on_language_changed(self, new_lang):
        """Обработчик смены языка в настройках"""
        if self.parent_ref:
            self.parent_ref.change_language(new_lang)
    
    def reset_to_defaults(self):
        """Сброс настроек к значениям по умолчанию"""
        lang = LANGUAGES.get(self.parent_ref.current_lang if self.parent_ref else "Русский", LANGUAGES["Русский"])
        
        reply = QMessageBox.question(self, lang.get("confirm_reset", "Подтверждение"),
                                    lang.get("reset_confirm_msg", "Вы уверены, что хотите сбросить все настройки?"),
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.timeout_spin.setValue(60)
            self.network_check.setChecked(True)
            self.deep_scan_check.setChecked(True)
            self.ml_analysis_check.setChecked(True)
            self.multi_thread_check.setChecked(True)
            self.thread_spin.setValue(4)
            self.auto_quarantine_check.setChecked(True)
            self.scan_on_access_check.setChecked(True)
            self.sensitivity_combo.setCurrentIndex(1)
            self.docker_check.setChecked(True)
            self.behavioral_check.setChecked(True)
            self.emu_timeout_spin.setValue(10)
            self.interface_lang_combo.setCurrentIndex(0)
            self.notifications_check.setChecked(True)
            self.sound_check.setChecked(False)
            self.minimize_tray_check.setChecked(False)
            self.panic_button_check.setChecked(True)
            self.auto_update_check.setChecked(True)
            self.update_interval_spin.setValue(24)
            self.log_level_combo.setCurrentIndex(1)
            
            QMessageBox.information(self, lang.get("information", "Информация"),
                                   lang.get("reset_success", "Настройки сброшены к значениям по умолчанию"))
    
    def get_settings(self):
        """Получить текущие настройки"""
        sensitivity_map = {0: 'low', 1: 'medium', 2: 'high'}
        return {
            'theme': 'Dark',  # Теперь только тёмная тема
            'timeout': self.timeout_spin.value(),
            'auto_disable_network': self.network_check.isChecked(),
            'deep_scan': self.deep_scan_check.isChecked(),
            'ml_analysis': self.ml_analysis_check.isChecked(),
            'multi_thread': self.multi_thread_check.isChecked(),
            'thread_count': self.thread_spin.value(),
            'auto_quarantine': self.auto_quarantine_check.isChecked(),
            'scan_on_access': self.scan_on_access_check.isChecked(),
            'sensitivity': sensitivity_map.get(self.sensitivity_combo.currentIndex(), 'medium'),
            'use_docker': self.docker_check.isChecked(),
            'behavioral_analysis': self.behavioral_check.isChecked(),
            'emu_timeout': self.emu_timeout_spin.value(),
            'language': self.interface_lang_combo.currentText(),
            'show_notifications': self.notifications_check.isChecked(),
            'sound_enabled': self.sound_check.isChecked(),
            'minimize_to_tray': self.minimize_tray_check.isChecked(),
            'panic_button_enabled': self.panic_button_check.isChecked(),
            'auto_update_signatures': self.auto_update_check.isChecked(),
            'update_interval': self.update_interval_spin.value(),
            'log_level': self.log_level_combo.currentText()
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
        
        # Обновляем все GroupBox
        groups = self.findChildren(QGroupBox)
        group_map = {
            0: lang["analysis_settings_group"],
            1: lang.get("antivirus_settings_group", "Настройки антивируса"),
            2: lang.get("sandbox_settings_group", "Настройки песочницы"),
            3: lang.get("interface_settings_group", "Настройки интерфейса"),
            4: lang.get("security_settings_group", "Настройки безопасности")
        }
        for i, group in enumerate(groups):
            if i in group_map:
                group.setTitle(group_map[i])
        
        # Обновляем все label, checkbox, button
        for label in self.findChildren(QLabel):
            text = label.text()
            if any(kw in text.lower() for kw in ["timeout", "time", "время анализа", "analysis time"]):
                label.setText(lang["timeout_label"])
            elif any(kw in text.lower() for kw in ["thread", "поток"]):
                label.setText(lang.get("thread_count_label", "Количество потоков:"))
            elif any(kw in text.lower() for kw in ["sensitivity", "чувствительность"]):
                label.setText(lang.get("sensitivity_label", "Чувствительность:"))
            elif any(kw in text.lower() for kw in ["emu timeout", "таймаут эмуляции"]):
                label.setText(lang.get("emu_timeout_label", "Таймаут эмуляции (сек):"))
            elif any(kw in text.lower() for kw in ["language", "язык интерфейса"]):
                label.setText(lang.get("interface_language_label", "Язык интерфейса:"))
            elif any(kw in text.lower() for kw in ["update interval", "интервал обновления"]):
                label.setText(lang.get("update_interval_label", "Интервал обновления (часы):"))
            elif any(kw in text.lower() for kw in ["log level", "уровень логирования"]):
                label.setText(lang.get("log_level_label", "Уровень логирования:"))
        
        # Обновляем чекбоксы
        self.network_check.setText(lang["network_check"])
        self.deep_scan_check.setText(lang.get("deep_scan_check", "Глубокий анализ файлов"))
        self.ml_analysis_check.setText(lang.get("ml_analysis_check", "Использовать ML классификатор"))
        self.multi_thread_check.setText(lang.get("multi_thread_check", "Многопоточное сканирование"))
        self.auto_quarantine_check.setText(lang.get("auto_quarantine_check", "Автоматический карантин"))
        self.scan_on_access_check.setText(lang.get("scan_on_access_check", "Сканирование при доступе"))
        self.docker_check.setText(lang.get("docker_check", "Использовать Docker изоляцию"))
        self.behavioral_check.setText(lang.get("behavioral_check", "Поведенческий анализ v2.0"))
        self.notifications_check.setText(lang.get("notifications_check", "Показывать уведомления"))
        self.sound_check.setText(lang.get("sound_check", "Звуковые уведомления"))
        self.minimize_tray_check.setText(lang.get("minimize_tray_check", "Сворачивать в трей"))
        self.panic_button_check.setText(lang.get("panic_button_check", "Кнопка экстренной остановки"))
        self.auto_update_check.setText(lang.get("auto_update_check", "Автообновление сигнатур"))
        
        # Обновляем combobox sensitivity
        self.sensitivity_combo.clear()
        self.sensitivity_combo.addItems([lang.get("sensitivity_low", "Низкая"), 
                                         lang.get("sensitivity_medium", "Средняя"), 
                                         lang.get("sensitivity_high", "Высокая")])
        
        # Обновляем кнопки - перевод на английский
        self.btn_reset.setText(lang.get("reset_defaults", "Reset Settings"))
        self.btn_close_settings.setText(lang.get("close", "Close"))


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
