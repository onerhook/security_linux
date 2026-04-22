#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Secure GUI v4.0 - Полностью переработанный профессиональный интерфейс
Современный минималистичный дизайн на PyQt5 с улучшенной эргономикой
Запускать ТОЛЬКО в изолированной виртуальной машине!
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json
import logging
from threading import Thread, Lock
import configparser

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QTextEdit, QFileDialog,
    QGroupBox, QGridLayout, QSplitter, QTabWidget, QFrame,
    QScrollArea, QMessageBox, QCheckBox, QSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QDialogButtonBox, QFormLayout, QLineEdit, QStatusBar,
    QToolBar, QAction, QMenu, QMenuBar, QSystemTrayIcon,
    QTreeWidget, QTreeWidgetItem, QSlider, QColorDialog,
    QFontDialog, QListWidget, QListWidgetItem, QStackedWidget,
    QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy,
    QDoubleSpinBox, QDateEdit, QTimeEdit
)
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QObject, QThread, QMetaObject,
    Q_ARG, QPropertyAnimation, QEasingCurve, QSize, QUrl,
    QPoint, QRect, QSettings, QTranslator, QLocale, QMargins
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QIcon, QPixmap, QPainter,
    QBrush, QPen, QLinearGradient, QDesktopServices,
    QTextCursor, QTextDocument, QMovie, QKeySequence,
    QCursor, QIntValidator
)
from PyQt5.QtWidgets import QShortcut

# Добавляем модули в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.orchestrator import RedSandSecure
    REDSAND_AVAILABLE = True
except ImportError:
    REDSAND_AVAILABLE = False


# ============================================================================
# ЦВЕТОВЫЕ ТЕМЫ
# ============================================================================

THEMES = {
    "Dark Professional": {
        "bg_primary": "#1a1d23",
        "bg_secondary": "#242832",
        "bg_tertiary": "#2d3240",
        "bg_hover": "#363c4a",
        "accent": "#4a9eff",
        "accent_hover": "#6bb3ff",
        "text_primary": "#e8eaed",
        "text_secondary": "#9aa0a6",
        "text_muted": "#5f6368",
        "success": "#34a853",
        "warning": "#fbbc04",
        "danger": "#ea4335",
        "info": "#4285f4",
        "border": "#3c4043",
        "panel_bg": "#20242a"
    },
    "Midnight Blue": {
        "bg_primary": "#0f141f",
        "bg_secondary": "#1a2332",
        "bg_tertiary": "#243045",
        "bg_hover": "#2d3a52",
        "accent": "#5c87ff",
        "accent_hover": "#7a9eff",
        "text_primary": "#e6e9f0",
        "text_secondary": "#8b95a5",
        "text_muted": "#5a6478",
        "success": "#4ade80",
        "warning": "#fbbf24",
        "danger": "#f87171",
        "info": "#60a5fa",
        "border": "#334155",
        "panel_bg": "#151b28"
    },
    "Carbon Dark": {
        "bg_primary": "#121212",
        "bg_secondary": "#1e1e1e",
        "bg_tertiary": "#2a2a2a",
        "bg_hover": "#333333",
        "accent": "#bb86fc",
        "accent_hover": "#cf9dff",
        "text_primary": "#ffffff",
        "text_secondary": "#b0b0b0",
        "text_muted": "#666666",
        "success": "#03dac6",
        "warning": "#ffb74d",
        "danger": "#cf6679",
        "info": "#64b5f6",
        "border": "#333333",
        "panel_bg": "#181818"
    },
    "Arctic White": {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f5f7fa",
        "bg_tertiary": "#ebeef2",
        "bg_hover": "#e2e6eb",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "text_primary": "#1f2937",
        "text_secondary": "#6b7280",
        "text_muted": "#9ca3af",
        "success": "#059669",
        "warning": "#d97706",
        "danger": "#dc2626",
        "info": "#2563eb",
        "border": "#e5e7eb",
        "panel_bg": "#fafbfc"
    },
    "Forest Green": {
        "bg_primary": "#0d1f14",
        "bg_secondary": "#14291c",
        "bg_tertiary": "#1a3525",
        "bg_hover": "#20402d",
        "accent": "#4ade80",
        "accent_hover": "#6ee78a",
        "text_primary": "#e8f5e9",
        "text_secondary": "#86a890",
        "text_muted": "#4a6b55",
        "success": "#22c55e",
        "warning": "#facc15",
        "danger": "#ef4444",
        "info": "#3b82f6",
        "border": "#2d4a36",
        "panel_bg": "#102217"
    },
    "Crimson Night": {
        "bg_primary": "#1a0f12",
        "bg_secondary": "#2a181c",
        "bg_tertiary": "#3a2026",
        "bg_hover": "#4a2830",
        "accent": "#f43f5e",
        "accent_hover": "#fb7185",
        "text_primary": "#fef2f2",
        "text_secondary": "#fca5a5",
        "text_muted": "#991b1b",
        "success": "#22c55e",
        "warning": "#fbbf24",
        "danger": "#ef4444",
        "info": "#60a5fa",
        "border": "#4a2830",
        "panel_bg": "#1f1216"
    }
}


def generate_stylesheet(theme_name: str = "Dark Professional") -> str:
    """Генерация таблицы стилей на основе выбранной темы."""
    theme = THEMES.get(theme_name, THEMES["Dark Professional"])
    
    return f"""
    QMainWindow, QDialog {{
        background-color: {theme['bg_primary']};
        color: {theme['text_primary']};
        font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
        font-size: 14px;
        line-height: 1.5;
    }}
    
    QToolBar {{
        background-color: {theme['bg_secondary']};
        border-bottom: 1px solid {theme['border']};
        padding: 6px 10px;
        spacing: 8px;
        min-height: 52px;
    }}
    
    QToolBar QToolButton {{
        background-color: transparent;
        color: {theme['text_primary']};
        border: none;
        padding: 10px 18px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 13px;
    }}
    
    QToolBar QToolButton:hover {{
        background-color: {theme['bg_hover']};
    }}
    
    QToolBar QToolButton:pressed {{
        background-color: {theme['bg_tertiary']};
    }}
    
    QPushButton#primaryBtn {{
        background-color: {theme['accent']};
        color: #ffffff;
        border: none;
        padding: 14px 32px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        min-width: 160px;
    }}
    
    QPushButton#primaryBtn:hover {{
        background-color: {theme['accent_hover']};
    }}
    
    QPushButton#primaryBtn:pressed {{
        background-color: {theme['bg_tertiary']};
    }}
    
    QPushButton#primaryBtn:disabled {{
        background-color: {theme['bg_tertiary']};
        color: {theme['text_muted']};
    }}
    
    QPushButton#dangerBtn {{
        background-color: {theme['danger']};
        color: #ffffff;
        border: none;
        padding: 14px 32px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
    }}
    
    QPushButton#dangerBtn:hover {{
        background-color: #dc2626;
    }}
    
    QPushButton {{
        background-color: {theme['bg_tertiary']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        padding: 12px 24px;
        border-radius: 6px;
        font-weight: 500;
        min-width: 120px;
    }}
    
    QPushButton:hover {{
        background-color: {theme['bg_hover']};
        border-color: {theme['accent']};
    }}
    
    QPushButton:pressed {{
        background-color: {theme['bg_tertiary']};
    }}
    
    QPushButton:disabled {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_muted']};
        border-color: {theme['border']};
    }}
    
    QGroupBox {{
        background-color: {theme['panel_bg']};
        border: 1px solid {theme['border']};
        border-radius: 10px;
        margin-top: 20px;
        padding-top: 20px;
        font-weight: 600;
        color: {theme['text_primary']};
        font-size: 14px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 12px;
        color: {theme['accent']};
        font-size: 13px;
        font-weight: 600;
    }}
    
    QTabWidget::pane {{
        border: 1px solid {theme['border']};
        border-radius: 10px;
        background-color: {theme['panel_bg']};
    }}
    
    QTabBar::tab {{
        background-color: transparent;
        color: {theme['text_secondary']};
        padding: 14px 28px;
        margin-right: 4px;
        border-bottom: 3px solid transparent;
        font-weight: 500;
        font-size: 13px;
    }}
    
    QTabBar::tab:selected {{
        color: {theme['accent']};
        border-bottom: 3px solid {theme['accent']};
        font-weight: 600;
    }}
    
    QTabBar::tab:hover:!selected {{
        color: {theme['text_primary']};
        background-color: {theme['bg_hover']};
    }}
    
    QTextEdit, QPlainTextEdit {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 8px;
        padding: 14px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 13px;
        selection-background-color: {theme['accent']}40;
    }}
    
    QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {theme['accent']};
    }}
    
    QProgressBar {{
        background-color: {theme['bg_tertiary']};
        border: none;
        border-radius: 12px;
        height: 28px;
        text-align: center;
        color: {theme['text_primary']};
        font-weight: 600;
        font-size: 13px;
    }}
    
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {theme['accent']}, stop:1 {theme['accent_hover']});
        border-radius: 12px;
    }}
    
    QSlider::groove:horizontal {{
        background-color: {theme['bg_tertiary']};
        height: 10px;
        border-radius: 5px;
    }}
    
    QSlider::handle:horizontal {{
        background-color: {theme['accent']};
        width: 24px;
        margin: -7px 0;
        border-radius: 12px;
    }}
    
    QSlider::handle:horizontal:hover {{
        background-color: {theme['accent_hover']};
    }}
    
    QComboBox {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 6px;
        padding: 12px 16px;
        min-height: 42px;
    }}
    
    QComboBox:hover {{
        border: 1px solid {theme['accent']};
    }}
    
    QComboBox:focus {{
        border: 1px solid {theme['accent']};
        outline: none;
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 36px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        border-top: 8px solid {theme['text_secondary']};
        margin-right: 14px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        selection-background-color: {theme['bg_hover']};
        border-radius: 6px;
        outline: none;
        padding: 6px;
    }}
    
    QSpinBox, QDoubleSpinBox {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 6px;
        padding: 12px 16px;
        min-height: 42px;
    }}
    
    QSpinBox:hover, QDoubleSpinBox:hover {{
        border: 1px solid {theme['accent']};
    }}
    
    QLineEdit {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 6px;
        padding: 12px 16px;
        min-height: 42px;
        selection-background-color: {theme['accent']}40;
    }}
    
    QLineEdit:hover {{
        border: 1px solid {theme['border']};
    }}
    
    QLineEdit:focus {{
        border: 1px solid {theme['accent']};
        background-color: {theme['bg_primary']};
        outline: none;
    }}
    
    QCheckBox {{
        color: {theme['text_primary']};
        spacing: 14px;
        font-size: 14px;
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
        border: 2px solid {theme['accent']};
    }}
    
    QCheckBox::indicator:hover {{
        border: 2px solid {theme['accent']};
    }}
    
    QRadioButton {{
        color: {theme['text_primary']};
        spacing: 14px;
        font-size: 14px;
    }}
    
    QRadioButton::indicator {{
        width: 22px;
        height: 22px;
        border-radius: 11px;
        border: 2px solid {theme['border']};
        background-color: {theme['bg_secondary']};
    }}
    
    QRadioButton::indicator:checked {{
        background-color: {theme['accent']};
        border: 2px solid {theme['accent']};
    }}
    
    QTableWidget {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 10px;
        gridline-color: {theme['border']};
        alternate-background-color: {theme['bg_primary']};
    }}
    
    QTableWidget::item {{
        padding: 14px;
        border-bottom: 1px solid {theme['border']};
    }}
    
    QTableWidget::item:selected {{
        background-color: {theme['bg_hover']};
        color: {theme['text_primary']};
    }}
    
    QTableWidget::item:hover {{
        background-color: {theme['bg_hover']};
    }}
    
    QHeaderView::section {{
        background-color: {theme['bg_tertiary']};
        color: {theme['text_secondary']};
        padding: 16px;
        border: none;
        font-weight: 600;
        border-bottom: 2px solid {theme['border']};
        text-transform: uppercase;
        font-size: 12px;
        letter-spacing: 0.5px;
    }}
    
    QTreeWidget {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 10px;
    }}
    
    QTreeWidget::item {{
        padding: 10px;
        border-bottom: 1px solid {theme['border']};
    }}
    
    QTreeWidget::item:selected {{
        background-color: {theme['bg_hover']};
        color: {theme['text_primary']};
    }}
    
    QTreeWidget::item:hover {{
        background-color: {theme['bg_hover']};
    }}
    
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    
    QScrollBar:vertical {{
        background-color: {theme['bg_primary']};
        width: 14px;
        border-radius: 7px;
        margin: 2px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {theme['bg_tertiary']};
        min-height: 50px;
        border-radius: 7px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {theme['bg_hover']};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background-color: {theme['bg_primary']};
        height: 14px;
        border-radius: 7px;
        margin: 2px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {theme['bg_tertiary']};
        min-width: 50px;
        border-radius: 7px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {theme['bg_hover']};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    QMessageBox {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
    }}
    
    QMessageBox QLabel {{
        color: {theme['text_primary']};
        font-size: 14px;
    }}
    
    QMessageBox QPushButton {{
        min-width: 110px;
        padding: 12px 24px;
    }}
    
    QMenu {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 8px;
        padding: 8px;
    }}
    
    QMenu::item {{
        padding: 12px 32px;
        border-radius: 6px;
        margin: 2px 8px;
    }}
    
    QMenu::item:selected {{
        background-color: {theme['bg_hover']};
        color: {theme['text_primary']};
    }}
    
    QMenu::separator {{
        height: 1px;
        background-color: {theme['border']};
        margin: 8px 12px;
    }}
    
    QStatusBar {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_secondary']};
        border-top: 1px solid {theme['border']};
        font-size: 13px;
        padding: 8px 14px;
    }}
    
    QListWidget {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 10px;
    }}
    
    QListWidget::item {{
        padding: 14px;
        border-radius: 6px;
        margin: 4px;
        border-bottom: 1px solid {theme['border']};
    }}
    
    QListWidget::item:selected {{
        background-color: {theme['bg_hover']};
        color: {theme['text_primary']};
    }}
    
    QListWidget::item:hover {{
        background-color: {theme['bg_hover']};
    }}
    
    QSplitter::handle {{
        background-color: {theme['border']};
        width: 3px;
    }}
    
    QSplitter::handle:horizontal {{
        width: 3px;
    }}
    
    QSplitter::handle:vertical {{
        height: 3px;
    }}
    
    QToolTip {{
        background-color: {theme['bg_tertiary']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 6px;
        padding: 10px 16px;
        font-size: 13px;
    }}
    
    QLabel#titleLabel {{
        font-size: 26px;
        font-weight: 700;
        color: {theme['text_primary']};
        padding: 10px;
    }}
    
    QLabel#subtitleLabel {{
        font-size: 14px;
        color: {theme['text_secondary']};
    }}
    
    QFrame#separatorLine {{
        background-color: {theme['border']};
        max-height: 1px;
    }}
    
    QFrame#riskFrame {{
        background-color: {theme['panel_bg']};
        border: 2px solid {theme['accent']};
        border-radius: 12px;
        padding: 20px;
    }}
    
    QLabel#riskLabel {{
        font-size: 48px;
        font-weight: 700;
        color: {theme['danger']};
    }}
    
    QLabel#threatTypeLabel {{
        font-size: 20px;
        font-weight: 600;
        color: {theme['accent']};
    }}
    
    QFrame#cardFrame {{
        background-color: {theme['panel_bg']};
        border: 1px solid {theme['border']};
        border-radius: 10px;
        padding: 18px;
    }}
    
    QFrame#infoPanel {{
        background-color: {theme['bg_secondary']};
        border: 1px solid {theme['border']};
        border-radius: 8px;
        padding: 16px;
    }}
    
    QFrame#settingsPanel {{
        background-color: {theme['panel_bg']};
        border: 1px solid {theme['border']};
        border-radius: 10px;
        padding: 20px;
    }}
    
    QFrame#actionPanel {{
        background-color: {theme['bg_secondary']};
        border: 1px solid {theme['border']};
        border-radius: 10px;
        padding: 16px;
    }}
    
    QMenuBar {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border-bottom: 1px solid {theme['border']};
        padding: 4px;
    }}
    
    QMenuBar::item {{
        padding: 8px 16px;
        border-radius: 6px;
        margin: 2px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {theme['bg_hover']};
    }}
    
    QMenuBar::item:pressed {{
        background-color: {theme['bg_tertiary']};
    }}
    
    QDockWidget {{
        titlebar-close-icon: none;
        titlebar-normal-icon: none;
    }}
    
    QDockWidget::title {{
        background-color: {theme['bg_tertiary']};
        padding: 10px;
        text-align: center;
        font-weight: 600;
    }}
    
    QDockWidget::close-button, QDockWidget::float-button {{
        border: none;
        padding: 4px;
        margin: 4px;
    }}
    """


# ============================================================================
# РАБОЧИЙ ПОТОК АНАЛИЗА
# ============================================================================

class AnalysisWorker(QObject):
    """Рабочий поток для выполнения анализа без блокировки UI."""

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
        """Выполнение анализа в отдельном потоке."""
        if not REDSAND_AVAILABLE:
            self.error.emit("Модуль RedSand Secure не найден")
            return

        try:
            sandbox = RedSandSecure(output_dir='reports_gui')

            # Этапы анализа
            stages = [
                (10, "Отключение сети..."),
                (20, "Применение анти-песочницы..."),
                (30, "Запуск эмуляции сети..."),
                (40, "Статический анализ..."),
                (50, "Генерация полиморфных вариантов..." if self.use_poly else "Пропуск полиморфного анализа..."),
                (70, "Динамический анализ..."),
                (85, "Классификация угрозы..."),
                (95, "Генерация отчетов..."),
                (100, "Анализ завершен!")
            ]

            for progress_val, message in stages:
                self.progress.emit(progress_val, message)
                self.log_message.emit('INFO', message)
                QThread.msleep(200)

            # Запуск реального анализа
            result = sandbox.analyze_file(
                self.file_path,
                use_poly=self.use_poly,
                timeout=self.timeout
            )

            if result:
                # Конвертируем AnalysisResult в dict для сигнала
                if hasattr(result, '__dataclass_fields__'):
                    from dataclasses import asdict
                    result_dict = asdict(result)
                else:
                    result_dict = result
                
                # Добавляем недостающие поля для GUI
                if 'static_results' not in result_dict and hasattr(result, 'static_results'):
                    result_dict['static_results'] = result.static_results or {}
                if 'dynamic_events' not in result_dict and hasattr(result, 'dynamic_events'):
                    result_dict['dynamic_events'] = result.dynamic_events or []
                if 'threat_info' not in result_dict and hasattr(result, 'threat_info'):
                    result_dict['threat_info'] = result.threat_info or {}
                
                # Гарантируем корректный формат analysis_time (должен быть dict)
                if 'analysis_time' in result_dict:
                    at = result_dict['analysis_time']
                    if isinstance(at, (int, float)):
                        result_dict['analysis_time'] = {'start': None, 'duration': float(at)}
                    elif not isinstance(at, dict):
                        result_dict['analysis_time'] = {'start': None, 'duration': 0.0}
                else:
                    result_dict['analysis_time'] = {'start': None, 'duration': 0.0}
                
                # Гарантируем что threat_info это dict
                if result_dict.get('threat_info') is None or not isinstance(result_dict['threat_info'], dict):
                    result_dict['threat_info'] = {}
                
                self.finished.emit(result_dict)
            else:
                self.error.emit("Анализ не был завершен успешно")

        except Exception as e:
            self.error.emit(f"Ошибка анализа: {str(e)}")


# ============================================================================
# ДИАЛОГОВЫЕ ОКНА
# ============================================================================

class SettingsDialog(QDialog):
    """Диалог настроек приложения."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки приложения")
        self.setMinimumSize(750, 650)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Заголовок
        title_label = QLabel("Настройки приложения")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)

        # Создаем вкладки для настроек
        tabs = QTabWidget()
        
        # Вкладка основных настроек
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        basic_layout.setSpacing(16)
        basic_layout.setContentsMargins(16, 16, 16, 16)

        # Группа: Параметры анализа
        analysis_group = QGroupBox("Параметры анализа")
        analysis_form = QFormLayout()
        analysis_form.setSpacing(14)

        # Таймаут анализа
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(60)
        self.timeout_spin.setSuffix(" сек")
        self.timeout_spin.setMinimumHeight(42)
        analysis_form.addRow("Таймаут анализа:", self.timeout_spin)

        # Максимальное количество потоков
        self.max_workers_spin = QSpinBox()
        self.max_workers_spin.setRange(1, 32)
        self.max_workers_spin.setValue(16)
        self.max_workers_spin.setSuffix(" потоков")
        self.max_workers_spin.setMinimumHeight(42)
        analysis_form.addRow("Максимум потоков:", self.max_workers_spin)

        # Уровень логирования
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        self.log_level_combo.setMinimumHeight(42)
        analysis_form.addRow("Уровень логирования:", self.log_level_combo)

        analysis_group.setLayout(analysis_form)
        basic_layout.addWidget(analysis_group)

        # Группа: Пути и файлы
        paths_group = QGroupBox("Пути и файлы")
        paths_layout = QVBoxLayout()
        paths_layout.setSpacing(12)

        # Директория отчетов
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Директория отчетов:")
        dir_label.setMinimumWidth(150)
        self.output_dir_edit = QLineEdit("reports")
        self.output_dir_edit.setMinimumHeight(42)
        btn_browse = QPushButton("Обзор...")
        btn_browse.setMinimumHeight(42)
        btn_browse.clicked.connect(self.browse_output_dir)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.output_dir_edit)
        dir_layout.addWidget(btn_browse)
        paths_layout.addLayout(dir_layout)

        # Поли морфный анализ по умолчанию
        self.poly_check = QCheckBox("Включить полиморфный анализ по умолчанию")
        self.poly_check.setMinimumHeight(36)
        paths_layout.addWidget(self.poly_check)

        paths_group.setLayout(paths_layout)
        basic_layout.addWidget(paths_group)

        # Группа: Сетевые настройки
        network_group = QGroupBox("Сетевые настройки")
        network_layout = QVBoxLayout()
        network_layout.setSpacing(12)

        # Автозакрытие сети
        self.network_check = QCheckBox("Автоматически отключать сеть при анализе")
        self.network_check.setChecked(True)
        self.network_check.setMinimumHeight(36)
        network_layout.addWidget(self.network_check)

        # Блокировка сетевых вызовов
        self.block_network_check = QCheckBox("Блокировать все сетевые вызовы образцов")
        self.block_network_check.setChecked(True)
        self.block_network_check.setMinimumHeight(36)
        network_layout.addWidget(self.block_network_check)

        network_group.setLayout(network_layout)
        basic_layout.addWidget(network_group)

        basic_layout.addStretch()
        tabs.addTab(basic_tab, "Основные")

        # Вкладка темы и внешнего вида
        theme_tab = QWidget()
        theme_layout = QVBoxLayout(theme_tab)
        theme_layout.setSpacing(16)
        theme_layout.setContentsMargins(16, 16, 16, 16)

        # Группа: Цветовая схема
        color_group = QGroupBox("Цветовая схема")
        color_form = QFormLayout()
        color_form.setSpacing(14)

        # Выбор темы
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        self.theme_combo.setCurrentText("Dark Professional")
        self.theme_combo.setMinimumHeight(42)
        color_form.addRow("Цветовая тема:", self.theme_combo)

        # Размер шрифта
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 20)
        self.font_size_spin.setValue(14)
        self.font_size_spin.setSuffix(" px")
        self.font_size_spin.setMinimumHeight(42)
        color_form.addRow("Размер шрифта:", self.font_size_spin)

        color_group.setLayout(color_form)
        theme_layout.addWidget(color_group)

        # Группа: Интерфейс
        ui_group = QGroupBox("Интерфейс")
        ui_layout = QVBoxLayout()
        ui_layout.setSpacing(12)

        # Анимации интерфейса
        self.animations_check = QCheckBox("Включить анимации интерфейса")
        self.animations_check.setChecked(True)
        self.animations_check.setMinimumHeight(36)
        ui_layout.addWidget(self.animations_check)

        # Плавная прокрутка
        self.smooth_scroll_check = QCheckBox("Плавная прокрутка")
        self.smooth_scroll_check.setChecked(True)
        self.smooth_scroll_check.setMinimumHeight(36)
        ui_layout.addWidget(self.smooth_scroll_check)

        # Показывать подсказки
        self.tooltips_check = QCheckBox("Показывать всплывающие подсказки")
        self.tooltips_check.setChecked(True)
        self.tooltips_check.setMinimumHeight(36)
        ui_layout.addWidget(self.tooltips_check)

        ui_group.setLayout(ui_layout)
        theme_layout.addWidget(ui_group)

        theme_layout.addStretch()
        tabs.addTab(theme_tab, "Тема и внешний вид")

        # Вкладка безопасности
        security_tab = QWidget()
        security_layout = QVBoxLayout(security_tab)
        security_layout.setSpacing(16)
        security_layout.setContentsMargins(16, 16, 16, 16)

        # Группа: Изоляция
        isolation_group = QGroupBox("Изоляция иsandbox")
        isolation_form = QFormLayout()
        isolation_form.setSpacing(14)

        # Время жизни sandbox
        self.sandbox_lifetime_spin = QSpinBox()
        self.sandbox_lifetime_spin.setRange(1, 60)
        self.sandbox_lifetime_spin.setValue(10)
        self.sandbox_lifetime_spin.setSuffix(" мин")
        self.sandbox_lifetime_spin.setMinimumHeight(42)
        isolation_form.addRow("Время жизни sandbox:", self.sandbox_lifetime_spin)

        # Интервал снимков
        self.snapshot_interval_spin = QSpinBox()
        self.snapshot_interval_spin.setRange(1, 300)
        self.snapshot_interval_spin.setValue(30)
        self.snapshot_interval_spin.setSuffix(" сек")
        self.snapshot_interval_spin.setMinimumHeight(42)
        isolation_form.addRow("Интервал снимков:", self.snapshot_interval_spin)

        isolation_group.setLayout(isolation_form)
        security_layout.addWidget(isolation_group)

        # Группа: Защита
        protection_group = QGroupBox("Защита системы")
        protection_layout = QVBoxLayout()
        protection_layout.setSpacing(12)

        # Отключение автозапуска процессов
        self.disable_auto_run_check = QCheckBox("Отключить автозапуск процессов после анализа")
        self.disable_auto_run_check.setChecked(True)
        self.disable_auto_run_check.setMinimumHeight(36)
        protection_layout.addWidget(self.disable_auto_run_check)

        # Блокировка опасных приложений
        self.block_dangerous_apps_check = QCheckBox("Блокировать запуск опасных приложений (paint, notepad и т.д.)")
        self.block_dangerous_apps_check.setChecked(True)
        self.block_dangerous_apps_check.setMinimumHeight(36)
        protection_layout.addWidget(self.block_dangerous_apps_check)

        # Принудительное завершение процессов
        self.force_kill_check = QCheckBox("Принудительно завершать все процессы после анализа")
        self.force_kill_check.setChecked(False)
        self.force_kill_check.setMinimumHeight(36)
        protection_layout.addWidget(self.force_kill_check)

        # Очистка временных файлов
        self.cleanup_temp_check = QCheckBox("Очищать временные файлы после анализа")
        self.cleanup_temp_check.setChecked(True)
        self.cleanup_temp_check.setMinimumHeight(36)
        protection_layout.addWidget(self.cleanup_temp_check)

        protection_group.setLayout(protection_layout)
        security_layout.addWidget(protection_group)

        security_layout.addStretch()
        tabs.addTab(security_tab, "Безопасность")

        # Вкладка дополнительных настроек
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        advanced_layout.setSpacing(16)
        advanced_layout.setContentsMargins(16, 16, 16, 16)

        # Группа: Производительность
        perf_group = QGroupBox("Производительность")
        perf_form = QFormLayout()
        perf_form.setSpacing(14)

        # Размер буфера логов
        self.log_buffer_spin = QSpinBox()
        self.log_buffer_spin.setRange(100, 10000)
        self.log_buffer_spin.setValue(1000)
        self.log_buffer_spin.setSuffix(" строк")
        self.log_buffer_spin.setMinimumHeight(42)
        perf_form.addRow("Размер буфера логов:", self.log_buffer_spin)

        # Интервал обновления UI
        self.ui_update_spin = QSpinBox()
        self.ui_update_spin.setRange(50, 1000)
        self.ui_update_spin.setValue(100)
        self.ui_update_spin.setSuffix(" мс")
        self.ui_update_spin.setMinimumHeight(42)
        perf_form.addRow("Интервал обновления UI:", self.ui_update_spin)

        perf_group.setLayout(perf_form)
        advanced_layout.addWidget(perf_group)

        # Группа: Экспорт
        export_group = QGroupBox("Экспорт данных")
        export_layout = QVBoxLayout()
        export_layout.setSpacing(12)

        # Автоэкспорт в JSON
        self.auto_export_json_check = QCheckBox("Автоматически экспортировать отчеты в JSON")
        self.auto_export_json_check.setChecked(False)
        self.auto_export_json_check.setMinimumHeight(36)
        export_layout.addWidget(self.auto_export_json_check)

        # Автоэкспорт в HTML
        self.auto_export_html_check = QCheckBox("Автоматически экспортировать отчеты в HTML")
        self.auto_export_html_check.setChecked(False)
        self.auto_export_html_check.setMinimumHeight(36)
        export_layout.addWidget(self.auto_export_html_check)

        # Сжимать архивы
        self.compress_archives_check = QCheckBox("Сжимать отчеты в ZIP-архивы")
        self.compress_archives_check.setChecked(True)
        self.compress_archives_check.setMinimumHeight(36)
        export_layout.addWidget(self.compress_archives_check)

        export_group.setLayout(export_layout)
        advanced_layout.addWidget(export_group)

        advanced_layout.addStretch()
        tabs.addTab(advanced_tab, "Дополнительно")

        layout.addWidget(tabs)

        # Кнопки
        buttons_frame = QFrame()
        buttons_frame.setObjectName("actionPanel")
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(16, 16, 16, 16)

        self.btn_apply = QPushButton("Применить")
        self.btn_apply.setMinimumHeight(44)
        self.btn_apply.clicked.connect(self.apply_settings)

        self.btn_ok = QPushButton("OK")
        self.btn_ok.setObjectName("primaryBtn")
        self.btn_ok.setMinimumHeight(44)
        self.btn_ok.clicked.connect(self.accept)

        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.setMinimumHeight(44)
        self.btn_cancel.clicked.connect(self.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_apply)
        buttons_layout.addWidget(self.btn_ok)
        buttons_layout.addWidget(self.btn_cancel)

        layout.addWidget(buttons_frame)

    def get_settings(self):
        return {
            'timeout': self.timeout_spin.value(),
            'output_dir': self.output_dir_edit.text(),
            'use_poly_default': self.poly_check.isChecked(),
            'auto_disable_network': self.network_check.isChecked(),
            'block_network': self.block_network_check.isChecked(),
            'log_level': self.log_level_combo.currentText(),
            'theme': self.theme_combo.currentText(),
            'font_size': self.font_size_spin.value(),
            'enable_animations': self.animations_check.isChecked(),
            'smooth_scroll': self.smooth_scroll_check.isChecked(),
            'show_tooltips': self.tooltips_check.isChecked(),
            'max_workers': self.max_workers_spin.value(),
            'sandbox_lifetime': self.sandbox_lifetime_spin.value(),
            'snapshot_interval': self.snapshot_interval_spin.value(),
            'disable_auto_run': self.disable_auto_run_check.isChecked(),
            'block_dangerous_apps': self.block_dangerous_apps_check.isChecked(),
            'force_kill': self.force_kill_check.isChecked(),
            'cleanup_temp': self.cleanup_temp_check.isChecked(),
            'log_buffer_size': self.log_buffer_spin.value(),
            'ui_update_interval': self.ui_update_spin.value(),
            'auto_export_json': self.auto_export_json_check.isChecked(),
            'auto_export_html': self.auto_export_html_check.isChecked(),
            'compress_archives': self.compress_archives_check.isChecked(),
        }


class ReportViewerDialog(QDialog):
    """Диалог просмотра детального отчета."""

    def __init__(self, report_data: dict, parent=None):
        super().__init__(parent)
        self.report_data = report_data
        self.setWindowTitle("Детальный отчет")
        self.setMinimumSize(900, 700)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Создаем вкладки
        tabs = QTabWidget()

        # Вкладка сводки
        summary_widget = self.create_summary_tab()
        tabs.addTab(summary_widget, "Сводка")

        # Вкладка статического анализа
        static_widget = self.create_static_tab()
        tabs.addTab(static_widget, "Статический анализ")

        # Вкладка динамического анализа
        dynamic_widget = self.create_dynamic_tab()
        tabs.addTab(dynamic_widget, "Динамический анализ")

        # Вкладка IOC
        ioc_widget = self.create_ioc_tab()
        tabs.addTab(ioc_widget, "IOC")

        layout.addWidget(tabs)

        # Кнопки действий
        btn_layout = QHBoxLayout()

        btn_export_json = QPushButton("Экспорт JSON")
        btn_export_json.clicked.connect(self.export_json)
        btn_layout.addWidget(btn_export_json)

        btn_export_html = QPushButton("Экспорт HTML")
        btn_export_html.clicked.connect(self.export_html)
        btn_layout.addWidget(btn_export_html)

        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

    def create_summary_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Адаптация структуры данных от Orchestrator
        threat_info = self.report_data.get('threat_info') or {}
        if not isinstance(threat_info, dict):
            threat_info = {}
        
        static_data = self.report_data.get('static_results') or {}
        if not isinstance(static_data, dict):
            static_data = {}
            
        analysis_time = self.report_data.get('analysis_time') or {}
        
        # Если analysis_time - это float/int (старый формат), преобразуем его
        if isinstance(analysis_time, (int, float)):
            analysis_time = {'start': None, 'duration': float(analysis_time)}
        elif not isinstance(analysis_time, dict):
            analysis_time = {'start': None, 'duration': 0.0}
        
        # Извлекаем информацию о файле из static_results
        file_name = static_data.get('file_name', 'N/A') if static_data else 'N/A'
        file_size = static_data.get('file_size', 0) if static_data else 0
        file_path = static_data.get('file_path', 'N/A') if static_data else 'N/A'

        # Индикатор риска
        risk_score = threat_info.get('risk_score', 0) if isinstance(threat_info, dict) else 0
        risk_label = QLabel(f"Уровень риска: {risk_score}/100")
        risk_label.setFont(QFont("Segoe UI", 18, QFont.Bold))

        if risk_score >= 70:
            risk_label.setStyleSheet("color: #dc3545;")
        elif risk_score >= 40:
            risk_label.setStyleSheet("color: #ffc107;")
        else:
            risk_label.setStyleSheet("color: #28a745;")

        layout.addWidget(risk_label, alignment=Qt.AlignCenter)

        # Информация об угрозе
        info_group = QGroupBox("Информация об угрозе")
        info_layout = QGridLayout()

        info_layout.addWidget(QLabel("Тип:"), 0, 0)
        info_layout.addWidget(QLabel(threat_info.get('type', 'Неизвестно') if isinstance(threat_info, dict) else 'Неизвестно'), 0, 1)

        info_layout.addWidget(QLabel("Семейство:"), 1, 0)
        info_layout.addWidget(QLabel(threat_info.get('family', 'Неизвестно') if isinstance(threat_info, dict) else 'Неизвестно'), 1, 1)

        info_layout.addWidget(QLabel("Доверие:"), 2, 0)
        info_layout.addWidget(QLabel(threat_info.get('confidence', 'Низкое') if isinstance(threat_info, dict) else 'Низкое'), 2, 1)

        info_layout.addWidget(QLabel("MITRE ATT&CK:"), 3, 0)
        mitre_tactics = threat_info.get('mitre_tactics', []) if isinstance(threat_info, dict) else []
        if isinstance(mitre_tactics, list):
            mitre_text = QLabel(', '.join(mitre_tactics))
        else:
            mitre_text = QLabel(str(mitre_tactics))
        mitre_text.setWordWrap(True)
        info_layout.addWidget(mitre_text, 3, 1)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Информация о файле
        file_group = QGroupBox("Информация о файле")
        file_layout = QGridLayout()

        file_layout.addWidget(QLabel("Имя:"), 0, 0)
        file_layout.addWidget(QLabel(file_name), 0, 1)

        file_layout.addWidget(QLabel("Размер:"), 1, 0)
        file_layout.addWidget(QLabel(f"{file_size} байт"), 1, 1)

        file_layout.addWidget(QLabel("Путь:"), 2, 0)
        path_label = QLabel(file_path)
        path_label.setWordWrap(True)
        file_layout.addWidget(path_label, 2, 1)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Время анализа
        time_group = QGroupBox("Время анализа")
        time_layout = QGridLayout()

        time_layout.addWidget(QLabel("Начало:"), 0, 0)
        start_time = analysis_time.get('start', 'N/A') if isinstance(analysis_time, dict) else 'N/A'
        time_layout.addWidget(QLabel(start_time if start_time else 'N/A'), 0, 1)

        time_layout.addWidget(QLabel("Длительность:"), 1, 0)
        duration = analysis_time.get('duration', 0) if isinstance(analysis_time, dict) else 0
        time_layout.addWidget(QLabel(f"{float(duration):.2f} сек"), 1, 1)

        time_group.setLayout(time_layout)
        layout.addWidget(time_group)

        layout.addStretch()
        return widget

    def create_static_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Адаптация структуры данных от Orchestrator
        static_data = self.report_data.get('static_results', {})

        # Хеши
        hashes_group = QGroupBox("Хеши файла")
        hashes_layout = QGridLayout()
        hashes = static_data.get('hashes', {}) if static_data else {}

        for i, (hash_type, hash_value) in enumerate(hashes.items()):
            label = QLabel(f"{hash_type.upper()}:")
            label.setFont(QFont("Consolas", 10))
            value_label = QLabel(hash_value)
            value_label.setFont(QFont("Consolas", 10))
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

            hashes_layout.addWidget(label, i // 2, (i % 2) * 2)
            hashes_layout.addWidget(value_label, i // 2, (i % 2) * 2 + 1)

        hashes_group.setLayout(hashes_layout)
        layout.addWidget(hashes_group)

        # PE информация
        if static_data and static_data.get('pe_info'):
            pe_group = QGroupBox("PE Информация")
            pe_layout = QVBoxLayout()

            pe_text = QTextEdit()
            pe_text.setReadOnly(True)
            pe_text.setMaximumHeight(200)

            pe_info = static_data['pe_info']
            pe_content = json.dumps(pe_info, indent=2, ensure_ascii=False)
            pe_text.setPlainText(pe_content)

            pe_layout.addWidget(pe_text)
            pe_group.setLayout(pe_layout)
            layout.addWidget(pe_group)

        # Строки
        if static_data and static_data.get('strings'):
            strings_group = QGroupBox("Извлеченные строки (первые 50)")
            strings_layout = QVBoxLayout()

            strings_text = QTextEdit()
            strings_text.setReadOnly(True)
            strings_text.setMaximumHeight(200)
            strings_text.setPlainText('\n'.join(static_data['strings'][:50]))

            strings_layout.addWidget(strings_text)
            strings_group.setLayout(strings_layout)
            layout.addWidget(strings_group)

        layout.addStretch()
        return widget

    def create_dynamic_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Адаптация структуры данных от Orchestrator
        dynamic_events = self.report_data.get('dynamic_events', [])

        events_table = QTableWidget()
        events_table.setColumnCount(3)
        events_table.setHorizontalHeaderLabels(["Время", "Тип", "Событие"])
        events_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        for event in dynamic_events:
            row = events_table.rowCount()
            events_table.insertRow(row)

            timestamp = event.get('timestamp', 'N/A')
            event_type = event.get('type', 'INFO')
            message = event.get('message', 'N/A')

            events_table.setItem(row, 0, QTableWidgetItem(timestamp))
            events_table.setItem(row, 1, QTableWidgetItem(event_type))
            events_table.setItem(row, 2, QTableWidgetItem(message))

            # Цвет для критических событий
            if event_type == 'CRITICAL':
                for col in range(3):
                    item = events_table.item(row, col)
                    if item:
                        item.setBackground(QColor("#dc3545"))
                        item.setForeground(QColor("white"))

        layout.addWidget(events_table)
        return widget

    def create_ioc_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Адаптация структуры данных от Orchestrator
        static_data = self.report_data.get('static_results', {})
        hashes = static_data.get('hashes', {}) if static_data else {}

        ioc_text = QTextEdit()
        ioc_text.setReadOnly(True)

        content = "=== INDICATORS OF COMPROMISE (IOC) ===\n\n"

        if hashes:
            content += "ХЕШИ ФАЙЛА:\n"
            for hash_type, hash_value in hashes.items():
                content += f"  {hash_type.upper()}: {hash_value}\n"

        content += "\n=========================================\n"

        ioc_text.setPlainText(content)
        layout.addWidget(ioc_text)

        return widget

    def export_json(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить JSON отчет", "", "JSON Files (*.json)"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.report_data, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "Успех", "JSON отчет сохранен!")

    def export_html(self):
        QMessageBox.information(
            self, "Информация",
            "HTML отчет можно найти в директории отчетов.\n"
            "Используйте кнопку 'Открыть папку отчетов' в главном окне."
        )


# ============================================================================
# ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ
# ============================================================================

class RedSandSecureGUI(QMainWindow):
    """Главное окно приложения RedSand Secure."""

    def __init__(self):
        super().__init__()
        self.worker_thread: Optional[QThread] = None
        self.worker: Optional[AnalysisWorker] = None
        self.current_report: Optional[dict] = None
        self.settings = {
            'timeout': 60,
            'output_dir': 'reports',
            'use_poly_default': False,
            'auto_disable_network': True,
            'log_level': 'INFO'
        }

        self.setup_ui()
        self.apply_stylesheet()
        self.load_settings()

    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        self.setWindowTitle("RedSand Secure v4.0 - Анализ вредоносного ПО")
        self.setMinimumSize(1280, 850)
        self.resize(1450, 950)

        # Центральное виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # Заголовок
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("RedSand Secure v4.0")
        title_label.setObjectName("titleLabel")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        main_layout.addWidget(header_frame)

        subtitle_label = QLabel("Профессиональная система анализа вредоносного ПО")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle_label)

        # Разделитель
        separator = QFrame()
        separator.setObjectName("separatorLine")
        separator.setFrameShape(QFrame.HLine)
        main_layout.addWidget(separator)

        # Основной сплиттер
        splitter = QSplitter(Qt.Horizontal)

        # Левая панель - Управление
        left_panel = self.create_left_panel()
        left_panel.setMinimumWidth(320)
        left_panel.setMaximumWidth(450)
        splitter.addWidget(left_panel)

        # Правая панель - Результаты и логи
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setHandleWidth(3)

        main_layout.addWidget(splitter)

        # Создание меню
        self.create_menu_bar()

        # Создание тулбара
        self.create_tool_bar()

        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")

    def create_left_panel(self) -> QWidget:
        """Создание левой панели управления."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(18)
        layout.setContentsMargins(16, 16, 16, 16)

        # Группа выбора файла
        file_group = QGroupBox("Файл для анализа")
        file_layout = QVBoxLayout()
        file_layout.setSpacing(10)

        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Путь к файлу...")
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setMinimumHeight(40)
        file_layout.addWidget(self.file_path_edit)

        btn_select_file = QPushButton("Выбрать файл")
        btn_select_file.setObjectName("primaryBtn")
        btn_select_file.setMinimumHeight(42)
        btn_select_file.clicked.connect(self.select_file)
        file_layout.addWidget(btn_select_file)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Группа настроек анализа
        settings_group = QGroupBox("Параметры анализа")
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(12)

        # Таймаут с подписью
        timeout_layout = QHBoxLayout()
        timeout_label = QLabel("Таймаут:")
        timeout_label.setMinimumWidth(80)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(60)
        self.timeout_spin.setSuffix(" сек")
        self.timeout_spin.setMinimumHeight(36)
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self.timeout_spin)
        settings_layout.addLayout(timeout_layout)

        # Полиморфный анализ
        self.poly_check = QCheckBox("Полиморфный анализ")
        self.poly_check.setToolTip("Генерировать полиморфные варианты образца")
        settings_layout.addWidget(self.poly_check)

        # Отключение сети
        self.network_check = QCheckBox("Отключать сеть при анализе")
        self.network_check.setChecked(True)
        self.network_check.setToolTip("Автоматически отключать сетевые адаптеры")
        settings_layout.addWidget(self.network_check)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Кнопка запуска анализа
        self.btn_analyze = QPushButton("ЗАПУСТИТЬ АНАЛИЗ")
        self.btn_analyze.setObjectName("primaryBtn")
        self.btn_analyze.setMinimumHeight(54)
        self.btn_analyze.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.btn_analyze.clicked.connect(self.start_analysis)
        layout.addWidget(self.btn_analyze)

        # Кнопка экстренной остановки
        self.btn_panic = QPushButton("ЭКСТРЕННАЯ ОСТАНОВКА")
        self.btn_panic.setObjectName("dangerBtn")
        self.btn_panic.setMinimumHeight(48)
        self.btn_panic.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_panic.clicked.connect(self.emergency_stop)
        self.btn_panic.setEnabled(False)
        layout.addWidget(self.btn_panic)

        # Прогресс бар
        progress_group = QGroupBox("Прогресс")
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(28)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("Ожидание...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet(f"color: {THEMES['Dark Professional']['text_secondary']}; font-size: 12px;")
        progress_layout.addWidget(self.progress_label)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Быстрые действия
        actions_group = QGroupBox("Действия")
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)

        btn_settings = QPushButton("Настройки приложения")
        btn_settings.setMinimumHeight(38)
        btn_settings.clicked.connect(self.open_settings)
        actions_layout.addWidget(btn_settings)

        btn_reports_folder = QPushButton("Папка отчетов")
        btn_reports_folder.setMinimumHeight(38)
        btn_reports_folder.clicked.connect(self.open_reports_folder)
        actions_layout.addWidget(btn_reports_folder)

        btn_clear_logs = QPushButton("Очистить логи")
        btn_clear_logs.setMinimumHeight(38)
        btn_clear_logs.clicked.connect(self.clear_logs)
        actions_layout.addWidget(btn_clear_logs)

        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        layout.addStretch()
        return widget

    def create_right_panel(self) -> QWidget:
        """Создание правой панели результатов."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(16, 16, 16, 16)

        # Вкладки результатов
        self.tabs = QTabWidget()
        self.tabs.setMinimumHeight(500)

        # Вкладка логов
        logs_widget = self.create_logs_tab()
        self.tabs.addTab(logs_widget, "Логи")

        # Вкладка результатов
        results_widget = self.create_results_tab()
        self.tabs.addTab(results_widget, "Результаты")

        # Вкладка IOC
        ioc_widget = self.create_ioc_quick_tab()
        self.tabs.addTab(ioc_widget, "IOC")

        layout.addWidget(self.tabs)
        return widget

    def create_logs_tab(self) -> QWidget:
        """Создание вкладки логов."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 11))
        self.log_text.setPlaceholderText("Логи анализа будут отображаться здесь...")
        layout.addWidget(self.log_text)

        return widget

    def create_results_tab(self) -> QWidget:
        """Создание вкладки результатов."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Сводная информация
        self.results_summary = QLabel("Результаты анализа появятся здесь после завершения...")
        self.results_summary.setAlignment(Qt.AlignCenter)
        self.results_summary.setFont(QFont("Segoe UI", 13))
        self.results_summary.setStyleSheet(f"color: {THEMES['Dark Professional']['text_secondary']}; padding: 50px;")
        layout.addWidget(self.results_summary)

        # Детальная таблица (скрыта по умолчанию)
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Параметр", "Значение"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setVisible(False)
        layout.addWidget(self.results_table)

        return widget

    def create_ioc_quick_tab(self) -> QWidget:
        """Создание быстрой вкладки IOC."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.ioc_text = QTextEdit()
        self.ioc_text.setReadOnly(True)
        self.ioc_text.setFont(QFont("Consolas", 11))
        self.ioc_text.setPlaceholderText("Indicators of Compromise появятся здесь после анализа...")
        layout.addWidget(self.ioc_text)

        btn_copy_ioc = QPushButton("Копировать IOC")
        btn_copy_ioc.setMinimumHeight(40)
        btn_copy_ioc.clicked.connect(self.copy_ioc_to_clipboard)
        layout.addWidget(btn_copy_ioc)

        return widget

    def create_menu_bar(self):
        """Создание меню приложения."""
        menubar = self.menuBar()

        # Файл
        file_menu = menubar.addMenu("Файл")

        open_action = QAction("Открыть файл", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.select_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        recent_files_menu = file_menu.addMenu("Недавние файлы")
        for i in range(5):
            action = QAction(f"Файл {i+1}", self)
            recent_files_menu.addAction(action)

        file_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Анализ
        analysis_menu = menubar.addMenu("Анализ")

        start_action = QAction("Запустить анализ", self)
        start_action.setShortcut("F5")
        start_action.triggered.connect(self.start_analysis)
        analysis_menu.addAction(start_action)

        stop_action = QAction("Остановить анализ", self)
        stop_action.setShortcut("F6")
        stop_action.triggered.connect(self.emergency_stop)
        analysis_menu.addAction(stop_action)

        analysis_menu.addSeparator()

        quick_scan_action = QAction("Быстрый скан", self)
        quick_scan_action.setShortcut("Ctrl+F5")
        analysis_menu.addAction(quick_scan_action)

        deep_scan_action = QAction("Глубокий анализ", self)
        deep_scan_action.setShortcut("Ctrl+Shift+F5")
        analysis_menu.addAction(deep_scan_action)

        # Отчеты
        reports_menu = menubar.addMenu("Отчеты")

        view_action = QAction("Просмотреть последний отчет", self)
        view_action.triggered.connect(self.view_last_report)
        reports_menu.addAction(view_action)

        export_json_action = QAction("Экспорт в JSON", self)
        reports_menu.addAction(export_json_action)

        export_html_action = QAction("Экспорт в HTML", self)
        reports_menu.addAction(export_html_action)

        reports_menu.addSeparator()

        folder_action = QAction("Открыть папку отчетов", self)
        folder_action.triggered.connect(self.open_reports_folder)
        reports_menu.addAction(folder_action)

        # Настройки
        settings_menu = menubar.addMenu("Настройки")

        settings_action = QAction("Параметры приложения", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)

        theme_menu = settings_menu.addMenu("Тема")
        for theme_name in list(THEMES.keys()):
            theme_action = QAction(theme_name, self)
            theme_menu.addAction(theme_action)

        settings_menu.addSeparator()

        reset_action = QAction("Сбросить настройки", self)
        settings_menu.addAction(reset_action)

        # Справка
        help_menu = menubar.addMenu("Справка")

        docs_action = QAction("Документация", self)
        help_menu.addAction(docs_action)

        shortcuts_action = QAction("Горячие клавиши", self)
        help_menu.addAction(shortcuts_action)

        help_menu.addSeparator()

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        warning_action = QAction("Предупреждение о безопасности", self)
        warning_action.triggered.connect(self.show_security_warning)
        help_menu.addAction(warning_action)

    def create_tool_bar(self):
        """Создание панели инструментов."""
        toolbar = QToolBar("Главная панель")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        btn_open = QAction("Открыть", self)
        btn_open.setShortcut("Ctrl+O")
        btn_open.triggered.connect(self.select_file)
        toolbar.addAction(btn_open)

        toolbar.addSeparator()

        btn_analyze = QAction("Анализ", self)
        btn_analyze.setShortcut("F5")
        btn_analyze.triggered.connect(self.start_analysis)
        toolbar.addAction(btn_analyze)

        btn_stop = QAction("Стоп", self)
        btn_stop.setShortcut("F6")
        btn_stop.triggered.connect(self.emergency_stop)
        toolbar.addAction(btn_stop)

        toolbar.addSeparator()

        btn_reports = QAction("Отчеты", self)
        btn_reports.triggered.connect(self.open_reports_folder)
        toolbar.addAction(btn_reports)

        btn_settings = QAction("Настройки", self)
        btn_settings.triggered.connect(self.open_settings)
        toolbar.addAction(btn_settings)

    def apply_stylesheet(self):
        """Применение таблицы стилей."""
        theme_name = self.settings.get('theme', 'Dark Red')
        stylesheet = generate_stylesheet(theme_name)
        self.setStyleSheet(stylesheet)

    def load_settings(self):
        """Загрузка настроек из файла."""
        settings_file = Path('gui_settings.json')
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)

                self.timeout_spin.setValue(self.settings.get('timeout', 60))
                self.poly_check.setChecked(self.settings.get('use_poly_default', False))
                self.network_check.setChecked(self.settings.get('auto_disable_network', True))
            except Exception as e:
                self.log_message('WARNING', f"Ошибка загрузки настроек: {e}")

    def save_settings(self):
        """Сохранение настроек в файл."""
        settings_file = Path('gui_settings.json')
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_message('ERROR', f"Ошибка сохранения настроек: {e}")

    # ========================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ
    # ========================================================================

    def select_file(self):
        """Выбор файла для анализа."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл для анализа",
            "",
            "Все файлы (*.*);;Executable файлы (*.exe);;DLL файлы (*.dll);;Script файлы (*.py *.js *.vbs)"
        )

        if file_path:
            self.file_path_edit.setText(file_path)
            self.log_message('INFO', f"Выбран файл: {file_path}")
            self.status_bar.showMessage(f"Файл выбран: {file_path}")

    def start_analysis(self):
        """Запуск анализа файла."""
        file_path = self.file_path_edit.text().strip()

        if not file_path:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите файл для анализа!")
            return

        if not os.path.exists(file_path):
            QMessageBox.critical(self, "Ошибка", f"Файл не найден: {file_path}")
            return

        # Проверка предупреждения
        if not hasattr(self, '_warning_accepted'):
            reply = QMessageBox.question(
                self,
                "Предупреждение о безопасности",
                "Вы запускаете анализ потенциально опасного вредоносного ПО!\n\n"
                "Убедитесь, что:\n"
                "• Вы работаете в изолированной виртуальной машине\n"
                "• Сеть отключена или надежно изолирована\n"
                "• У вас есть актуальные бэкапы важных данных\n"
                "• Вы понимаете риски\n\n"
                "Продолжить?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

        # Сохранение настроек
        self.settings['timeout'] = self.timeout_spin.value()
        self.settings['use_poly_default'] = self.poly_check.isChecked()
        self.settings['auto_disable_network'] = self.network_check.isChecked()
        self.save_settings()

        # Блокировка интерфейса
        self.set_ui_enabled(False)
        self.btn_panic.setEnabled(True)

        # Создание рабочего
        self.worker = AnalysisWorker(
            file_path=file_path,
            use_poly=self.poly_check.isChecked(),
            timeout=self.timeout_spin.value()
        )

        # Создание потока
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        # Подключение сигналов
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.analysis_finished)
        self.worker.error.connect(self.analysis_error)
        self.worker.log_message.connect(self.log_message)

        # Запуск
        self.worker_thread.start()

        self.log_message('INFO', f"Запуск анализа файла: {file_path}")
        self.status_bar.showMessage("Анализ запущен...")

    def emergency_stop(self):
        """Экстренная остановка анализа."""
        reply = QMessageBox.warning(
            self,
            "ЭКСТРЕННАЯ ОСТАНОВКА",
            "Вы уверены, что хотите немедленно остановить анализ?\n\n"
            "Это может оставить систему в нестабильном состоянии!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.log_message('CRITICAL', "ЭКСТРЕННАЯ ОСТАНОВКА АКТИВИРОВАНА!")

            if self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.terminate()
                self.worker_thread.wait(3000)

            self.set_ui_enabled(True)
            self.btn_panic.setEnabled(False)
            self.progress_bar.setValue(0)
            self.progress_label.setText("Анализ прерван пользователем")
            self.status_bar.showMessage("Анализ прерван")

    def analysis_finished(self, result: dict):
        """Обработка завершения анализа."""
        self.current_report = result

        # Разблокировка интерфейса
        self.set_ui_enabled(True)
        self.btn_panic.setEnabled(False)

        # Обновление прогресса
        self.progress_bar.setValue(100)
        self.progress_label.setText("Анализ завершен успешно!")

        # Обновление результатов
        self.update_results_display(result)

        # Обновление IOC
        self.update_ioc_display(result)

        self.log_message('SUCCESS', "Анализ завершен успешно!")
        self.status_bar.showMessage("Анализ завершен")

        # Показать диалог с результатами
        if result:
            dialog = ReportViewerDialog(result, self)
            dialog.exec_()

    def analysis_error(self, error_msg: str):
        """Обработка ошибки анализа."""
        self.set_ui_enabled(True)
        self.btn_panic.setEnabled(False)

        self.progress_label.setText("Ошибка анализа!")
        self.progress_label.setStyleSheet("color: #dc3545; font-weight: bold;")

        self.log_message('ERROR', error_msg)
        self.status_bar.showMessage("Ошибка анализа")

        QMessageBox.critical(self, "Ошибка анализа", error_msg)

    def update_progress(self, value: int, message: str):
        """Обновление прогресс бара."""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
        self.status_bar.showMessage(message)

    def log_message(self, level: str, message: str):
        """Добавление сообщения в лог."""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Цвета для разных уровней
        colors = {
            'INFO': '#4a9eff',
            'DEBUG': '#8a8a8a',
            'WARNING': '#ffc107',
            'ERROR': '#dc3545',
            'CRITICAL': '#ff0000',
            'SUCCESS': '#28a745'
        }

        color = colors.get(level, '#eaeaea')

        html = f'<span style="color: {color};">[{timestamp}] [{level}]</span> {message}<br>'
        self.log_text.append(html)

        # Автоскролл вниз
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_results_display(self, result: dict):
        """Обновление отображения результатов."""
        # Адаптация структуры данных: Orchestrator использует threat_info, static_results, dynamic_events
        threat_info = result.get('threat_info') or {}
        if not isinstance(threat_info, dict):
            threat_info = {}
        static_data = result.get('static_results') or {}
        file_name = static_data.get('file_name', 'N/A') if static_data else 'N/A'
        file_size = static_data.get('file_size', 0) if static_data else 0
        
        # Скрываем заглушку, показываем таблицу
        self.results_summary.setVisible(False)
        self.results_table.setVisible(True)
        self.results_table.setRowCount(0)

        # Данные для таблицы
        data = [
            ("Тип угрозы", threat_info.get('type', 'Неизвестно')),
            ("Семейство", threat_info.get('family', 'Неизвестно')),
            ("Уровень риска", f"{threat_info.get('risk_score', 0)}/100"),
            ("Доверие", threat_info.get('confidence', 'Низкое')),
            ("Имя файла", file_name),
            ("Размер файла", f"{file_size} байт"),
        ]

        for param, value in data:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            self.results_table.setItem(row, 0, QTableWidgetItem(param))
            self.results_table.setItem(row, 1, QTableWidgetItem(str(value)))

    def update_ioc_display(self, result: dict):
        """Обновление отображения IOC."""
        static_data = result.get('static_results') or {}
        hashes = static_data.get('hashes', {}) if static_data else {}

        content = "=== INDICATORS OF COMPROMISE (IOC) ===\n\n"

        if hashes:
            content += "ХЕШИ ФАЙЛА:\n"
            for hash_type, hash_value in hashes.items():
                content += f"  {hash_type.upper()}: {hash_value}\n"

        content += "\n=========================================\n"
        content += "Совет: Используйте эти IOC для поиска угроз в вашей инфраструктуре"

        self.ioc_text.setPlainText(content)

    def clear_logs(self):
        """Очистка логов."""
        self.log_text.clear()
        self.log_message('INFO', "Логи очищены")

    def copy_ioc_to_clipboard(self):
        """Копирование IOC в буфер обмена."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.ioc_text.toPlainText())
        self.status_bar.showMessage("IOC скопированы в буфер обмена")
        QMessageBox.information(self, "Успех", "IOC скопированы в буфер обмена!")

    def open_settings(self):
        """Открытие диалога настроек."""
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            settings = dialog.get_settings()
            self.settings.update(settings)
            self.save_settings()
            # Применяем новую тему сразу после закрытия диалога
            self.apply_stylesheet()
            self.log_message('INFO', "Настройки сохранены и применены")

    def open_reports_folder(self):
        """Открытие папки с отчетами."""
        reports_dir = Path(self.settings.get('output_dir', 'reports'))
        reports_dir.mkdir(exist_ok=True)

        # Попытка открыть проводник
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(reports_dir.absolute())))
        except Exception as e:
            self.log_message('ERROR', f"Ошибка открытия папки: {e}")
            QMessageBox.warning(
                self,
                "Предупреждение",
                f"Не удалось автоматически открыть папку.\nПуть: {reports_dir.absolute()}"
            )

    def view_last_report(self):
        """Просмотр последнего отчета."""
        if self.current_report:
            dialog = ReportViewerDialog(self.current_report, self)
            dialog.exec_()
        else:
            QMessageBox.information(
                self,
                "Информация",
                "Нет доступных отчетов.\nСначала выполните анализ файла."
            )

    def show_about(self):
        """Показ окна о программе."""
        QMessageBox.about(
            self,
            "О программе RedSand Secure",
            "<h2>RedSand Secure v2.0</h2>"
            "<p>Профессиональная система анализа вредоносного ПО</p>"
            "<p><b>Версия:</b> 2.0 (GUI)</p>"
            "<p><b>Возможности:</b></p>"
            "<ul>"
            "<li>Статический анализ (PE, хеши, строки, YARA)</li>"
            "<li>Динамический анализ с мониторингом</li>"
            "<li>Классификация угроз (12 типов)</li>"
            "<li>Полиморфная генерация вариантов</li>"
            "<li>Эмуляция сети</li>"
            "<li>Анти-песочница техники</li>"
            "<li>Генерация отчетов (JSON, HTML, TXT)</li>"
            "</ul>"
            "<p><b>Внимание:</b> Запускайте только в изолированной VM!</p>"
        )

    def show_security_warning(self):
        """Показ предупреждения о безопасности."""
        QMessageBox.warning(
            self,
            "Предупреждение о безопасности",
            "<h2>ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ</h2>"
            "<p>Вы используете инструмент для анализа <b>вредоносного программного обеспечения</b>.</p>"
            "<p><b>Обязательные требования:</b></p>"
            "<ul>"
            "<li>Работайте ТОЛЬКО в изолированной виртуальной машине</li>"
            "<li>Отключите общие папки с хост-системой</li>"
            "<li>Изолируйте сеть (отключите адаптеры или используйте host-only)</li>"
            "<li>Сделайте снапшот VM перед анализом</li>"
            "<li>Не анализируйте образцы на рабочей машине</li>"
            "</ul>"
            "<p><b>Автор не несет ответственности за любой ущерб,</b></p>"
            "<p><b>причиненный неправильным использованием этого инструмента.</b></p>"
        )

    def set_ui_enabled(self, enabled: bool):
        """Включение/отключение элементов UI."""
        self.btn_analyze.setEnabled(enabled)
        self.file_path_edit.setEnabled(enabled)
        self.timeout_spin.setEnabled(enabled)
        self.poly_check.setEnabled(enabled)
        self.network_check.setEnabled(enabled)

    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.warning(
                self,
                "Анализ выполняется",
                "Анализ все еще выполняется. Вы уверены, что хотите выйти?\n\n"
                "Это может оставить систему в нестабильном состоянии!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.No:
                event.ignore()
                return

            self.worker_thread.terminate()
            self.worker_thread.wait(3000)

        event.accept()


# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================

def main():
    """Точка входа приложения."""
    # Проверка наличия необходимых модулей
    if not REDSAND_AVAILABLE:
        print("Ошибка: Модуль redsand_secure.py не найден!")
        print("Убедитесь, что вы находитесь в директории RedSand/")
        sys.exit(1)

    # Создание приложения
    app = QApplication(sys.argv)
    app.setApplicationName("RedSand Secure")
    app.setOrganizationName("RedSand Security")

    # Установка иконки приложения (если есть)
    # app.setWindowIcon(QIcon("icon.png"))

    # Создание главного окна
    window = RedSandSecureGUI()
    window.show()

    # Показ предупреждения при первом запуске
    if not Path('gui_settings.json').exists():
        QMessageBox.warning(
            window,
            "Предупреждение о безопасности",
            "<h2>ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ</h2>"
            "<p>Вы запускаете инструмент для анализа <b>вредоносного ПО</b>.</p>"
            "<p><b>Запускайте ТОЛЬКО в изолированной виртуальной машине!</b></p>"
            "<p>Автор не несет ответственности за любой ущерб.</p>"
        )

    # Запуск цикла событий
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
