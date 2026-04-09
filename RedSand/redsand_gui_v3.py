#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Secure GUI v3.0 - Ultra Customizable Interface
Профессиональный интерфейс с расширенной кастомизацией
Запускать ТОЛЬКО в изолированной виртуальной машине!
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import logging
from threading import Thread, Lock
import configparser

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QTextEdit, QFileDialog, QGroupBox, QGridLayout, QSplitter, QTabWidget, QFrame, QScrollArea, QMessageBox, QCheckBox, QSpinBox, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QStatusBar, QToolBar, QAction, QMenu, QMenuBar, QSystemTrayIcon, QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem, QSlider, QColorDialog, QFontDialog, QRadioButton, QButtonGroup, QDoubleSpinBox, QKeySequenceEdit, QShortcut, QDockWidget, QToolButton, QStyleFactory, QCompleter, QSizePolicy, QGraphicsDropShadowEffect, QStackedWidget, QWizard, QWizardPage, QCalendarWidget, QTimeEdit, QDateEdit, QLCDNumber, QDial, QPlainTextEdit, QTreeView, QColumnView, QTableView, QAbstractItemView, QActionGroup
)
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QObject, QThread, QMetaObject, Q_ARG, QPropertyAnimation, QEasingCurve, QSize, QUrl, QSettings, QMimeData, QPoint, QRect, QVariant, QMargins, QParallelAnimationGroup, QSequentialAnimationGroup, pyqtProperty, QStateMachine, QState, QSignalTransition, QEventTransition, QFile, QTextStream, QIODevice, QFileInfo, QDir, QStandardPaths, QDateTime, QLocale, QMutex, QWaitCondition
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QIcon, QPixmap, QPainter, QBrush, QPen, QLinearGradient, QDesktopServices, QTextCursor, QTextDocument, QGradient
)


# Добавляем модули в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from redsand_secure import RedSandSecure
    REDSAND_AVAILABLE = True
except ImportError:
    REDSAND_AVAILABLE = False


# ============================================================================
# МЕНЕДЖЕР ТЕМ И СТИЛЕЙ
# ============================================================================

class ThemeManager(QObject):
    """Менеджер тем для гибкой кастомизации интерфейса."""
    
    theme_changed = pyqtSignal(str)
    
    # Предопределённые темы
    PRESET_THEMES = {
        'dark_modern': {
            'primary_bg': '#1a1a2e',
            'secondary_bg': '#16213e',
            'accent_color': '#e94560',
            'text_primary': '#eaeaea',
            'text_secondary': '#8a8a8a',
            'border_color': '#0f3460',
            'hover_color': '#1a4a7a',
            'success_color': '#28a745',
            'warning_color': '#ffc107',
            'danger_color': '#dc3545',
            'gradient_start': '#e94560',
            'gradient_end': '#ff6b7a',
        },
        'cyberpunk': {
            'primary_bg': '#0d0d1a',
            'secondary_bg': '#1a1a2e',
            'accent_color': '#00ff9f',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'border_color': '#00d4ff',
            'hover_color': '#00ff9f',
            'success_color': '#00ff9f',
            'warning_color': '#ffaa00',
            'danger_color': '#ff0055',
            'gradient_start': '#00ff9f',
            'gradient_end': '#00d4ff',
        },
        'corporate_blue': {
            'primary_bg': '#f5f7fa',
            'secondary_bg': '#ffffff',
            'accent_color': '#2196f3',
            'text_primary': '#2c3e50',
            'text_secondary': '#7f8c8d',
            'border_color': '#bdc3c7',
            'hover_color': '#e3f2fd',
            'success_color': '#4caf50',
            'warning_color': '#ff9800',
            'danger_color': '#f44336',
            'gradient_start': '#2196f3',
            'gradient_end': '#21cbf3',
        },
        'midnight_purple': {
            'primary_bg': '#1e1e2e',
            'secondary_bg': '#2d2d44',
            'accent_color': '#bb86fc',
            'text_primary': '#ffffff',
            'text_secondary': '#a0a0a0',
            'border_color': '#3d3d5c',
            'hover_color': '#bb86fc',
            'success_color': '#03dac6',
            'warning_color': '#ffb74d',
            'danger_color': '#cf6679',
            'gradient_start': '#bb86fc',
            'gradient_end': '#3700b3',
        },
        'forest_green': {
            'primary_bg': '#1b2e1b',
            'secondary_bg': '#2d4a2d',
            'accent_color': '#4caf50',
            'text_primary': '#e8f5e9',
            'text_secondary': '#a5d6a7',
            'border_color': '#1b5e20',
            'hover_color': '#66bb6a',
            'success_color': '#4caf50',
            'warning_color': '#ffeb3b',
            'danger_color': '#f44336',
            'gradient_start': '#4caf50',
            'gradient_end': '#8bc34a',
        },
        'ocean_blue': {
            'primary_bg': '#0a1628',
            'secondary_bg': '#12263f',
            'accent_color': '#00adb5',
            'text_primary': '#eeeeee',
            'text_secondary': '#aaaaaa',
            'border_color': '#005f73',
            'hover_color': '#00adb5',
            'success_color': '#00adb5',
            'warning_color': '#ffdd00',
            'danger_color': '#ef476f',
            'gradient_start': '#00adb5',
            'gradient_end': '#005f73',
        },
        'grayscale': {
            'primary_bg': '#2b2b2b',
            'secondary_bg': '#3c3c3c',
            'accent_color': '#808080',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'border_color': '#505050',
            'hover_color': '#909090',
            'success_color': '#707070',
            'warning_color': '#a0a0a0',
            'danger_color': '#606060',
            'gradient_start': '#808080',
            'gradient_end': '#505050',
        },
        'sunset_orange': {
            'primary_bg': '#2d132c',
            'secondary_bg': '#401e3f',
            'accent_color': '#ff6b6b',
            'text_primary': '#f7f7f7',
            'text_secondary': '#c7c7c7',
            'border_color': '#801e3f',
            'hover_color': '#ff6b6b',
            'success_color': '#4ecdc4',
            'warning_color': '#ffe66d',
            'danger_color': '#ff6b6b',
            'gradient_start': '#ff6b6b',
            'gradient_end': '#ffa502',
        }
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = 'dark_modern'
        self.custom_themes = {}
        self.load_custom_themes()
    
    def load_custom_themes(self):
        """Загрузка пользовательских тем из файла."""
        config_path = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
        themes_file = os.path.join(config_path, 'custom_themes.json')
        
        if os.path.exists(themes_file):
            try:
                with open(themes_file, 'r', encoding='utf-8') as f:
                    self.custom_themes = json.load(f)
            except Exception as e:
                logging.error(f"Ошибка загрузки тем: {e}")
    
    def save_custom_themes(self):
        """Сохранение пользовательских тем."""
        config_path = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
        os.makedirs(config_path, exist_ok=True)
        themes_file = os.path.join(config_path, 'custom_themes.json')
        
        try:
            with open(themes_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_themes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Ошибка сохранения тем: {e}")
    
    def get_theme(self, theme_name: str) -> dict:
        """Получение темы по имени."""
        if theme_name in self.PRESET_THEMES:
            return self.PRESET_THEMES[theme_name].copy()
        elif theme_name in self.custom_themes:
            return self.custom_themes[theme_name].copy()
        else:
            return self.PRESET_THEMES['dark_modern'].copy()
    
    def set_current_theme(self, theme_name: str):
        """Установка текущей темы."""
        if theme_name in self.PRESET_THEMES or theme_name in self.custom_themes:
            self.current_theme = theme_name
            self.theme_changed.emit(theme_name)
    
    def create_custom_theme(self, name: str, colors: dict) -> bool:
        """Создание пользовательской темы."""
        if not name or not colors:
            return False
        
        self.custom_themes[name] = colors
        self.save_custom_themes()
        return True
    
    def delete_custom_theme(self, name: str) -> bool:
        """Удаление пользовательской темы."""
        if name in self.custom_themes:
            del self.custom_themes[name]
            self.save_custom_themes()
            return True
        return False
    
    def get_all_theme_names(self) -> List[str]:
        """Получение списка всех тем."""
        return list(self.PRESET_THEMES.keys()) + list(self.custom_themes.keys())
    
    def generate_stylesheet(self, theme: dict = None) -> str:
        """Генерация полной таблицы стилей на основе темы."""
        if theme is None:
            theme = self.get_theme(self.current_theme)
        
        stylesheet = f"""
/* === RedSand Secure v3.0 - Dynamic Theme === */
/* Theme: {self.current_theme} */

QMainWindow {{
    background-color: {theme['primary_bg']};
    color: {theme['text_primary']};
}}

QWidget {{
    font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
    font-size: 13px;
    background-color: {theme['primary_bg']};
    color: {theme['text_primary']};
}}

/* Заголовки */
QLabel#titleLabel {{
    font-size: 28px;
    font-weight: bold;
    color: {theme['accent_color']};
    padding: 15px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {theme['gradient_start']}, 
                                stop:1 {theme['gradient_end']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    border-radius: 8px;
}}

QLabel#sectionTitle {{
    font-size: 16px;
    font-weight: bold;
    color: {theme['primary_bg']};
    background-color: {theme['accent_color']};
    padding: 10px;
    border-radius: 6px;
}}

/* Группы */
QGroupBox {{
    font-weight: bold;
    border: 2px solid {theme['border_color']};
    border-radius: 10px;
    margin-top: 15px;
    padding-top: 12px;
    background-color: {theme['secondary_bg']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 10px;
    color: {theme['accent_color']};
}}

/* Кнопки */
QPushButton {{
    background-color: {theme['border_color']};
    color: {theme['text_primary']};
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: bold;
    min-width: 140px;
}}

QPushButton:hover {{
    background-color: {theme['hover_color']};
}}

QPushButton:pressed {{
    background-color: {theme['accent_color']};
    color: {theme['primary_bg']};
}}

QPushButton:disabled {{
    background-color: {theme['secondary_bg']};
    color: {theme['text_secondary']};
}}

QPushButton#primaryBtn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {theme['gradient_start']}, 
                                stop:1 {theme['gradient_end']});
    font-size: 15px;
    padding: 15px 35px;
    color: white;
}}

QPushButton#primaryBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {theme['hover_color']}, 
                                stop:1 {theme['accent_color']});
}}

QPushButton#dangerBtn {{
    background-color: {theme['danger_color']};
    color: white;
}}

QPushButton#dangerBtn:hover {{
    background-color: {theme['danger_color']};
    opacity: 0.8;
}}

QPushButton#successBtn {{
    background-color: {theme['success_color']};
    color: white;
}}

QPushButton#successBtn:hover {{
    background-color: {theme['success_color']};
    opacity: 0.8;
}}

/* Прогресс бар */
QProgressBar {{
    border: 2px solid {theme['border_color']};
    border-radius: 10px;
    text-align: center;
    font-weight: bold;
    background-color: {theme['secondary_bg']};
    height: 30px;
    color: {theme['text_primary']};
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {theme['gradient_start']}, 
                                stop:1 {theme['gradient_end']});
    border-radius: 8px;
}}

/* Текстовые поля */
QTextEdit, QPlainTextEdit, QLineEdit {{
    background-color: {theme['secondary_bg']};
    color: {theme['text_primary']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}}

QTextEdit:focus, QPlainTextEdit:focus, QLineEdit:focus {{
    border: 2px solid {theme['accent_color']};
}}

/* Таблицы */
QTableWidget {{
    background-color: {theme['secondary_bg']};
    alternate-background-color: {theme['border_color']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    gridline-color: {theme['primary_bg']};
}}

QTableWidget::item {{
    padding: 10px;
    border-bottom: 1px solid {theme['border_color']};
}}

QTableWidget::item:selected {{
    background-color: {theme['accent_color']};
    color: {theme['primary_bg']};
}}

QHeaderView::section {{
    background-color: {theme['border_color']};
    color: {theme['accent_color']};
    padding: 10px;
    border: none;
    font-weight: bold;
}}

/* Вкладки */
QTabWidget::pane {{
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    background-color: {theme['secondary_bg']};
}}

QTabBar::tab {{
    background-color: {theme['border_color']};
    color: {theme['text_primary']};
    padding: 12px 25px;
    margin-right: 3px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}}

QTabBar::tab:selected {{
    background-color: {theme['accent_color']};
    font-weight: bold;
    color: {theme['primary_bg']};
}}

QTabBar::tab:hover:!selected {{
    background-color: {theme['hover_color']};
}}

/* Дерево и списки */
QTreeWidget, QListWidget {{
    background-color: {theme['secondary_bg']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    padding: 8px;
}}

QTreeWidget::item, QListWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {theme['border_color']};
}}

QTreeWidget::item:selected, QListWidget::item:selected {{
    background-color: {theme['accent_color']};
    color: {theme['primary_bg']};
}}

QTreeWidget::item:hover, QListWidget::item:hover {{
    background-color: {theme['hover_color']};
}}

/* SpinBox, ComboBox */
QSpinBox, QComboBox, QDoubleSpinBox {{
    background-color: {theme['secondary_bg']};
    color: {theme['text_primary']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    padding: 10px;
    min-width: 120px;
}}

QSpinBox:focus, QComboBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {theme['accent_color']};
}}

QComboBox::drop-down {{
    border: none;
    width: 35px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 10px solid {theme['accent_color']};
    margin-right: 12px;
}}

/* Чекбоксы и радиокнопки */
QCheckBox, QRadioButton {{
    spacing: 12px;
    font-weight: normal;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 22px;
    height: 22px;
    border-radius: 5px;
    border: 2px solid {theme['border_color']};
    background-color: {theme['secondary_bg']};
}}

QCheckBox::indicator:checked {{
    background-color: {theme['accent_color']};
    border: 2px solid {theme['accent_color']};
}}

QRadioButton::indicator {{
    border-radius: 11px;
}}

QRadioButton::indicator:checked {{
    background-color: {theme['accent_color']};
    border: 2px solid {theme['accent_color']};
}}

/* Слайдеры */
QSlider::groove:horizontal {{
    border: 1px solid {theme['border_color']};
    height: 10px;
    background: {theme['secondary_bg']};
    border-radius: 5px;
}}

QSlider::handle:horizontal {{
    background: {theme['accent_color']};
    border: 2px solid {theme['hover_color']};
    width: 20px;
    margin: -6px 0;
    border-radius: 10px;
}}

QSlider::sub-page:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {theme['gradient_start']}, 
                                stop:1 {theme['gradient_end']});
    border-radius: 5px;
}}

/* Полосы прокрутки */
QScrollBar:vertical {{
    background-color: {theme['secondary_bg']};
    width: 14px;
    border-radius: 7px;
}}

QScrollBar::handle:vertical {{
    background-color: {theme['accent_color']};
    border-radius: 7px;
    min-height: 40px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {theme['secondary_bg']};
    height: 14px;
    border-radius: 7px;
}}

QScrollBar::handle:horizontal {{
    background-color: {theme['accent_color']};
    border-radius: 7px;
    min-width: 40px;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* Меню и тулбары */
QMenuBar {{
    background-color: {theme['secondary_bg']};
    color: {theme['text_primary']};
    border-bottom: 2px solid {theme['accent_color']};
}}

QMenuBar::item:selected {{
    background-color: {theme['accent_color']};
    color: {theme['primary_bg']};
}}

QMenu {{
    background-color: {theme['secondary_bg']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
}}

QMenu::item:selected {{
    background-color: {theme['accent_color']};
    color: {theme['primary_bg']};
}}

QToolBar {{
    background-color: {theme['secondary_bg']};
    border: none;
    padding: 5px;
    spacing: 5px;
}}

QToolButton {{
    background-color: {theme['border_color']};
    color: {theme['text_primary']};
    border: none;
    padding: 8px;
    border-radius: 6px;
}}

QToolButton:hover {{
    background-color: {theme['hover_color']};
}}

QToolButton:pressed {{
    background-color: {theme['accent_color']};
}}

/* Статус бар */
QStatusBar {{
    background-color: {theme['secondary_bg']};
    color: {theme['text_primary']};
    border-top: 2px solid {theme['accent_color']};
}}

/* Подсказки */
QToolTip {{
    background-color: {theme['accent_color']};
    color: {theme['primary_bg']};
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
}}

/* Разделители */
QFrame#line {{
    background-color: {theme['border_color']};
    max-height: 2px;
}}

/* LCD Number */
QLCDNumber {{
    background-color: {theme['secondary_bg']};
    color: {theme['accent_color']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    padding: 5px;
}}

/* Dial */
QDial {{
    background-color: {theme['secondary_bg']};
    border: 2px solid {theme['border_color']};
    border-radius: 50px;
}}

/* Scroll Area */
QScrollArea {{
    background-color: {theme['primary_bg']};
    border: none;
}}

/* Splitter */
QSplitter::handle {{
    background-color: {theme['border_color']};
}}

QSplitter::handle:horizontal {{
    width: 3px;
}}

QSplitter::handle:vertical {{
    height: 3px;
}}

/* Calendar */
QCalendarWidget {{
    background-color: {theme['secondary_bg']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
}}

QCalendarWidget QToolButton {{
    background-color: {theme['border_color']};
    color: {theme['text_primary']};
    border-radius: 6px;
}}

QCalendarWidget QMenu {{
    background-color: {theme['secondary_bg']};
}}

QCalendarWidget QSpinBox {{
    background-color: {theme['border_color']};
}}

/* Dock Widget */
QDockWidget {{
    background-color: {theme['secondary_bg']};
    titlebar-close-icon: url(:/close.png);
    titlebar-normal-icon: url(:/normal.png);
}}

QDockWidget::title {{
    background-color: {theme['border_color']};
    padding: 8px;
    color: {theme['accent_color']};
}}

/* MessageBox */
QMessageBox {{
    background-color: {theme['secondary_bg']};
}}

QMessageBox QLabel {{
    color: {theme['text_primary']};
}}

QMessageBox QPushButton {{
    min-width: 100px;
}}

/* Wizard */
QWizard {{
    background-color: {theme['primary_bg']};
}}

QWizard::title {{
    color: {theme['accent_color']};
    font-size: 18px;
    font-weight: bold;
}}

QWizardPage {{
    background-color: {theme['primary_bg']};
}}

/* Градиентные эффекты для особых элементов */
QLabel#gradientLabel {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {theme['gradient_start']}, 
                                stop:1 {theme['gradient_end']});
    color: white;
    padding: 20px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: bold;
}}

/* Анимированные элементы */
QPushButton#animatedBtn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {theme['gradient_start']}, 
                                stop:1 {theme['gradient_end']});
    border-radius: 10px;
    padding: 15px 30px;
    font-size: 14px;
    font-weight: bold;
}}

QPushButton#animatedBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {theme['hover_color']}, 
                                stop:1 {theme['accent_color']});
}}

/* Индикаторы риска */
QLabel#riskCritical {{
    color: {theme['danger_color']};
    font-size: 20px;
    font-weight: bold;
}}

QLabel#riskHigh {{
    color: #ff9800;
    font-size: 20px;
    font-weight: bold;
}}

QLabel#riskMedium {{
    color: {theme['warning_color']};
    font-size: 20px;
    font-weight: bold;
}}

QLabel#riskLow {{
    color: {theme['success_color']};
    font-size: 20px;
    font-weight: bold;
}}

/* Специальные виджеты */
QListView {{
    background-color: {theme['secondary_bg']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    outline: none;
}}

QTableView {{
    background-color: {theme['secondary_bg']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    gridline-color: {theme['primary_bg']};
}}

QColumnView {{
    background-color: {theme['secondary_bg']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
}}

/* Item views */
QAbstractItemView {{
    background-color: {theme['secondary_bg']};
    alternate-background-color: {theme['border_color']};
    selection-background-color: {theme['accent_color']};
    selection-color: {theme['primary_bg']};
    outline: none;
}}

QAbstractItemView::item:hover {{
    background-color: {theme['hover_color']};
}}

/* Focus */
*:focus {{
    outline: 2px solid {theme['accent_color']};
    outline-offset: 2px;
}}

/* Disabled state */
*:disabled {{
    color: {theme['text_secondary']};
}}

/* Hover effects */
QLabel:hover {{
    color: {theme['accent_color']};
}}

/* Custom properties support */
QWidget[highlighted="true"] {{
    border: 3px solid {theme['accent_color']};
    background-color: {theme['hover_color']};
}}

QWidget[urgent="true"] {{
    border: 3px solid {theme['danger_color']};
}}

QWidget[success="true"] {{
    border: 3px solid {theme['success_color']};
}}
"""
        return stylesheet


# ============================================================================
# КОНФИГУРАТОР ИНТЕРФЕЙСА
# ============================================================================

class InterfaceConfigurator:
    """Конфигуратор для настройки различных аспектов интерфейса."""
    
    @staticmethod
    def apply_shadow_effect(widget, color='#000000', blur_radius=20, offset=(3, 3)):
        """Применение эффекта тени к виджету."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur_radius)
        shadow.setOffset(*offset)
        shadow.setColor(QColor(color))
        widget.setGraphicsEffect(shadow)
    
    @staticmethod
    def apply_gradient_background(widget, start_color, end_color, direction='horizontal'):
        """Применение градиентного фона."""
        # Реализуется через stylesheet
        if direction == 'horizontal':
            gradient = f'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {start_color}, stop:1 {end_color})'
        else:
            gradient = f'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {start_color}, stop:1 {end_color})'
        
        widget.setStyleSheet(f'background: {gradient};')
    
    @staticmethod
    def create_rounded_widget(widget, radius=10):
        """Создание виджета со скругленными углами."""
        widget.setStyleSheet(f'{widget.styleSheet()} border-radius: {radius}px;')
    
    @staticmethod
    def setup_completer(line_edit, suggestions):
        """Настройка автодополнения для поля ввода."""
        completer = QCompleter(suggestions)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setPopupCompletion(True)
        line_edit.setCompleter(completer)


# ============================================================================
# ДИАЛОГ КАСТОМИЗАЦИИ ТЕМЫ
# ============================================================================

class ThemeCustomizerDialog(QDialog):
    """Диалог для создания и редактирования пользовательских тем."""
    
    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.current_colors = {}
        self.setWindowTitle("🎨 Конструктор Тем")
        self.setMinimumSize(800, 700)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Выбор базовой темы
        base_theme_group = QGroupBox("Базовая тема")
        base_layout = QHBoxLayout()
        
        self.base_theme_combo = QComboBox()
        self.base_theme_combo.addItems(self.theme_manager.get_all_theme_names())
        self.base_theme_combo.currentTextChanged.connect(self.on_base_theme_changed)
        base_layout.addWidget(QLabel("Выберите базу:"))
        base_layout.addWidget(self.base_theme_combo)
        
        base_theme_group.setLayout(base_layout)
        layout.addWidget(base_theme_group)
        
        # Настройки цветов
        colors_group = QGroupBox("Настройка цветов")
        colors_layout = QGridLayout()
        
        self.color_editors = {}
        color_labels = [
            ('primary_bg', 'Основной фон'),
            ('secondary_bg', 'Вторичный фон'),
            ('accent_color', 'Акцентный цвет'),
            ('text_primary', 'Основной текст'),
            ('text_secondary', 'Вторичный текст'),
            ('border_color', 'Цвет границ'),
            ('hover_color', 'Цвет при наведении'),
            ('success_color', 'Цвет успеха'),
            ('warning_color', 'Цвет предупреждения'),
            ('danger_color', 'Цвет опасности'),
            ('gradient_start', 'Начало градиента'),
            ('gradient_end', 'Конец градиента'),
        ]
        
        for i, (key, label) in enumerate(color_labels):
            colors_layout.addWidget(QLabel(label), i // 2, (i % 2) * 2)
            
            btn = QPushButton()
            btn.setFixedHeight(30)
            btn.clicked.connect(lambda checked, k=key: self.choose_color(k))
            self.color_editors[key] = {'button': btn, 'label': label}
            colors_layout.addWidget(btn, i // 2, (i % 2) * 2 + 1)
        
        colors_group.setLayout(colors_layout)
        layout.addWidget(colors_group)
        
        # Предпросмотр
        preview_group = QGroupBox("Предпросмотр")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("Предпросмотр текста")
        self.preview_label.setObjectName('previewLabel')
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(50)
        preview_layout.addWidget(self.preview_label)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Название темы
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Название темы:"))
        self.theme_name_edit = QLineEdit()
        self.theme_name_edit.setPlaceholderText("Введите название новой темы")
        name_layout.addWidget(self.theme_name_edit)
        layout.addLayout(name_layout)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        
        btn_save = QPushButton("💾 Сохранить тему")
        btn_save.setObjectName('successBtn')
        btn_save.clicked.connect(self.save_theme)
        buttons_layout.addWidget(btn_save)
        
        btn_apply = QPushButton("✨ Применить")
        btn_apply.setObjectName('primaryBtn')
        btn_apply.clicked.connect(self.apply_theme)
        buttons_layout.addWidget(btn_apply)
        
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.accept)
        buttons_layout.addWidget(btn_close)
        
        layout.addLayout(buttons_layout)
        
        # Инициализация цветами текущей темы
        self.on_base_theme_changed(self.base_theme_combo.currentText())
    
    def on_base_theme_changed(self, theme_name):
        """Обработка изменения базовой темы."""
        self.current_colors = self.theme_manager.get_theme(theme_name)
        self.update_color_buttons()
        self.update_preview()
    
    def update_color_buttons(self):
        """Обновление кнопок выбора цвета."""
        for key, data in self.color_editors.items():
            color = self.current_colors.get(key, '#000000')
            data['button'].setStyleSheet(f'background-color: {color}; border: 1px solid #000;')
    
    def choose_color(self, key):
        """Выбор цвета через диалог."""
        current_color = self.current_colors.get(key, '#000000')
        color = QColorDialog.getColor(QColor(current_color), self, f"Выберите {self.color_editors[key]['label']}")
        
        if color.isValid():
            self.current_colors[key] = color.name()
            self.update_color_buttons()
            self.update_preview()
    
    def update_preview(self):
        """Обновление предпросмотра."""
        colors = self.current_colors
        stylesheet = f"""
            background-color: {colors.get('secondary_bg', '#ffffff')};
            color: {colors.get('text_primary', '#000000')};
            border: 2px solid {colors.get('border_color', '#000000')};
            border-radius: 8px;
            padding: 10px;
        """
        self.preview_label.setStyleSheet(stylesheet)
    
    def save_theme(self):
        """Сохранение новой темы."""
        theme_name = self.theme_name_edit.text().strip()
        if not theme_name:
            QMessageBox.warning(self, "Ошибка", "Введите название темы")
            return
        
        if self.theme_manager.create_custom_theme(theme_name, self.current_colors):
            QMessageBox.information(self, "Успех", f"Тема '{theme_name}' сохранена!")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить тему")
    
    def apply_theme(self):
        """Применение темы без сохранения."""
        self.theme_manager.theme_changed.emit('custom')
        self.accept()


# ============================================================================
# ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ
# ============================================================================

class RedSandSecureGUI(QMainWindow):
    """Главное окно приложения RedSand Secure v3.0."""
    
    def __init__(self):
        super().__init__()
        self.worker_thread: Optional[QThread] = None
        self.worker: Optional[QObject] = None
        self.current_report: Optional[dict] = None
        self.theme_manager = ThemeManager(self)
        
        # Применение темы
        self.theme_manager.theme_changed.connect(self.apply_theme)
        
        self.setup_ui()
        self.apply_theme()
        self.load_settings()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        self.setWindowTitle("🛡️ RedSand Secure v3.0 - Анализ вредоносного ПО")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # Центральное виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # Заголовок с градиентом
        title_label = QLabel("🛡️ RedSand Secure v3.0")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        InterfaceConfigurator.apply_shadow_effect(title_label)
        main_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Профессиональная система анализа вредоносного ПО с расширенной кастомизацией")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #8a8a8a; font-size: 15px;")
        main_layout.addWidget(subtitle_label)
        
        # Разделитель
        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        main_layout.addWidget(line)
        
        # Основной сплиттер
        splitter = QSplitter(Qt.Horizontal)
        
        # Левая панель - Управление
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Правая панель - Результаты и логи
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        
        # Создание меню
        self.create_menu_bar()
        
        # Создание тулбара
        self.create_tool_bar()
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе | Тема: Dark Modern")
    
    def create_left_panel(self) -> QWidget:
        """Создание левой панели управления."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(18)
        
        # Группа выбора файла
        file_group = QGroupBox("📁 Выбор файла для анализа")
        file_layout = QVBoxLayout()
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Перетащите файл сюда или выберите...")
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setAcceptDrops(True)
        file_layout.addWidget(self.file_path_edit)
        
        btn_select_file = QPushButton("📂 Выбрать файл")
        btn_select_file.setObjectName("primaryBtn")
        btn_select_file.clicked.connect(self.select_file)
        file_layout.addWidget(btn_select_file)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Группа настроек анализа
        settings_group = QGroupBox("⚙️ Настройки анализа")
        settings_layout = QGridLayout()
        
        # Таймаут
        settings_layout.addWidget(QLabel("Таймаут (сек):"), 0, 0)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(60)
        settings_layout.addWidget(self.timeout_spin, 0, 1)
        
        # Полиморфный анализ
        self.poly_check = QCheckBox("🧬 Полиморфный анализ")
        self.poly_check.setToolTip("Генерировать полиморфные варианты образца")
        settings_layout.addWidget(self.poly_check, 1, 0, 1, 2)
        
        # Отключение сети
        self.network_check = QCheckBox("🔒 Отключать сеть")
        self.network_check.setChecked(True)
        self.network_check.setToolTip("Автоматически отключать сетевые адаптеры")
        settings_layout.addWidget(self.network_check, 2, 0, 1, 2)
        
        # Уровень эмуляции
        settings_layout.addWidget(QLabel("Уровень эмуляции:"), 3, 0)
        self.emulation_level_combo = QComboBox()
        self.emulation_level_combo.addItems(["Минимальный", "Стандартный", "Расширенный", "Максимальный"])
        self.emulation_level_combo.setCurrentIndex(1)
        settings_layout.addWidget(self.emulation_level_combo, 3, 1)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Кнопка запуска анализа
        self.btn_analyze = QPushButton("🚀 ЗАПУСТИТЬ АНАЛИЗ")
        self.btn_analyze.setObjectName("primaryBtn")
        self.btn_analyze.setMinimumHeight(70)
        self.btn_analyze.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.btn_analyze.clicked.connect(self.start_analysis)
        InterfaceConfigurator.apply_shadow_effect(self.btn_analyze)
        layout.addWidget(self.btn_analyze)
        
        # Кнопка экстренной остановки
        self.btn_panic = QPushButton("🔴 ЭКСТРЕННАЯ ОСТАНОВКА")
        self.btn_panic.setObjectName("dangerBtn")
        self.btn_panic.setMinimumHeight(60)
        self.btn_panic.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.btn_panic.clicked.connect(self.emergency_stop)
        self.btn_panic.setEnabled(False)
        layout.addWidget(self.btn_panic)
        
        # Прогресс бар
        progress_group = QGroupBox("📊 Прогресс анализа")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(30)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ожидание запуска...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #8a8a8a;")
        progress_layout.addWidget(self.progress_label)
        
        # Индикатор времени
        self.time_lcd = QLCDNumber()
        self.time_lcd.setDigitCount(5)
        self.time_lcd.display(0)
        self.time_lcd.setMinimumHeight(40)
        progress_layout.addWidget(self.time_lcd)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Быстрые действия
        actions_group = QGroupBox("⚡ Быстрые действия")
        actions_layout = QVBoxLayout()
        
        btn_settings = QPushButton("⚙️ Настройки")
        btn_settings.clicked.connect(self.open_settings)
        actions_layout.addWidget(btn_settings)
        
        btn_theme = QPushButton("🎨 Конструктор тем")
        btn_theme.clicked.connect(self.open_theme_customizer)
        actions_layout.addWidget(btn_theme)
        
        btn_reports_folder = QPushButton("📂 Открыть папку отчетов")
        btn_reports_folder.clicked.connect(self.open_reports_folder)
        actions_layout.addWidget(btn_reports_folder)
        
        btn_clear_logs = QPushButton("🗑️ Очистить логи")
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
        layout.setSpacing(18)
        
        # Вкладки результатов
        self.tabs = QTabWidget()
        
        # Вкладка логов
        logs_widget = self.create_logs_tab()
        self.tabs.addTab(logs_widget, "📝 Логи анализа")
        
        # Вкладка результатов
        results_widget = self.create_results_tab()
        self.tabs.addTab(results_widget, "📊 Результаты")
        
        # Вкладка IOC
        ioc_widget = self.create_ioc_quick_tab()
        self.tabs.addTab(ioc_widget, "🎯 IOC")
        
        # Вкладка визуализации
        viz_widget = self.create_visualization_tab()
        self.tabs.addTab(viz_widget, "📈 Визуализация")
        
        layout.addWidget(self.tabs)
        return widget
    
    def create_logs_tab(self) -> QWidget:
        """Создание вкладки логов."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setFont(QFont("Consolas", 11))
        layout.addWidget(self.log_viewer)
        
        # Фильтры логов
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Фильтр:"))
        
        self.log_filter_combo = QComboBox()
        self.log_filter_combo.addItems(["Все", "INFO", "WARNING", "ERROR", "DEBUG"])
        self.log_filter_combo.currentTextChanged.connect(self.filter_logs)
        filter_layout.addWidget(self.log_filter_combo)
        
        btn_export_logs = QPushButton("Экспорт логов")
        btn_export_logs.clicked.connect(self.export_logs)
        filter_layout.addWidget(btn_export_logs)
        
        layout.addLayout(filter_layout)
        return widget
    
    def create_results_tab(self) -> QWidget:
        """Создание вкладки результатов."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Индикатор риска
        risk_layout = QHBoxLayout()
        self.risk_label = QLabel("Уровень риска: --/100")
        self.risk_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.risk_label.setAlignment(Qt.AlignCenter)
        risk_layout.addWidget(self.risk_label)
        layout.addLayout(risk_layout)
        
        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Параметр", "Значение"])
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.results_table)
        
        # Детали угрозы
        threat_group = QGroupBox("🦠 Информация об угрозе")
        threat_layout = QVBoxLayout()
        
        self.threat_info_text = QTextEdit()
        self.threat_info_text.setReadOnly(True)
        threat_layout.addWidget(self.threat_info_text)
        
        threat_group.setLayout(threat_layout)
        layout.addWidget(threat_group)
        
        return widget
    
    def create_ioc_quick_tab(self) -> QWidget:
        """Создание вкладки IOC."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.ioc_tree = QTreeWidget()
        self.ioc_tree.setHeaderLabels(["Тип IOC", "Значение", "Доверие"])
        self.ioc_tree.setColumnWidth(0, 200)
        self.ioc_tree.setColumnWidth(1, 400)
        layout.addWidget(self.ioc_tree)
        
        # Кнопки экспорта
        export_layout = QHBoxLayout()
        
        btn_export_ioc_json = QPushButton("Экспорт JSON")
        btn_export_ioc_json.clicked.connect(lambda: self.export_ioc('json'))
        export_layout.addWidget(btn_export_ioc_json)
        
        btn_export_ioc_stix = QPushButton("Экспорт STIX")
        btn_export_ioc_stix.clicked.connect(lambda: self.export_ioc('stix'))
        export_layout.addWidget(btn_export_ioc_stix)
        
        layout.addLayout(export_layout)
        return widget
    
    def create_visualization_tab(self) -> QWidget:
        """Создание вкладки визуализации."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Placeholder для графиков
        placeholder = QLabel("📊 Визуализация данных анализа\n\nГрафики будут отображаться здесь после завершения анализа")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("font-size: 16px; color: #8a8a8a; padding: 50px;")
        layout.addWidget(placeholder)
        
        return widget
    
    def create_menu_bar(self):
        """Создание меню приложения."""
        menubar = self.menuBar()
        
        # Файл
        file_menu = menubar.addMenu("📁 Файл")
        
        action_open = QAction("📂 Открыть файл", self)
        action_open.setShortcut("Ctrl+O")
        action_open.triggered.connect(self.select_file)
        file_menu.addAction(action_open)
        
        file_menu.addSeparator()
        
        action_exit = QAction("🚪 Выход", self)
        action_exit.setShortcut("Ctrl+Q")
        action_exit.triggered.connect(self.close)
        file_menu.addAction(action_exit)
        
        # Настройки
        settings_menu = menubar.addMenu("⚙️ Настройки")
        
        action_theme = QAction("🎨 Конструктор тем", self)
        action_theme.setShortcut("Ctrl+T")
        action_theme.triggered.connect(self.open_theme_customizer)
        settings_menu.addAction(action_theme)
        
        action_prefs = QAction("⚙️ Параметры", self)
        action_prefs.setShortcut("Ctrl+,")
        action_prefs.triggered.connect(self.open_settings)
        settings_menu.addAction(action_prefs)
        
        # Инструменты
        tools_menu = menubar.addMenu("🛠️ Инструменты")
        
        action_generate_samples = QAction("🧪 Генерировать тестовые образцы", self)
        action_generate_samples.triggered.connect(self.generate_test_samples)
        tools_menu.addAction(action_generate_samples)
        
        # Помощь
        help_menu = menubar.addMenu("❓ Помощь")
        
        action_about = QAction("ℹ️ О программе", self)
        action_about.triggered.connect(self.show_about)
        help_menu.addAction(action_about)
    
    def create_tool_bar(self):
        """Создание панели инструментов."""
        toolbar = QToolBar("Главная панель")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Кнопки тулбара
        btn_open = QToolButton()
        btn_open.setText("📂 Открыть")
        btn_open.clicked.connect(self.select_file)
        toolbar.addWidget(btn_open)
        
        btn_analyze = QToolButton()
        btn_analyze.setText("🚀 Анализ")
        btn_analyze.clicked.connect(self.start_analysis)
        toolbar.addWidget(btn_analyze)
        
        toolbar.addSeparator()
        
        btn_theme = QToolButton()
        btn_theme.setText("🎨 Темы")
        btn_theme.clicked.connect(self.open_theme_customizer)
        toolbar.addWidget(btn_theme)
        
        btn_settings = QToolButton()
        btn_settings.setText("⚙️ Настройки")
        btn_settings.clicked.connect(self.open_settings)
        toolbar.addWidget(btn_settings)
    
    def apply_theme(self):
        """Применение текущей темы."""
        theme = self.theme_manager.get_theme(self.theme_manager.current_theme)
        stylesheet = self.theme_manager.generate_stylesheet(theme)
        self.setStyleSheet(stylesheet)
        
        # Обновление статус бара
        self.status_bar.showMessage(f"Готов к работе | Тема: {self.theme_manager.current_theme.replace('_', ' ').title()}")
    
    def select_file(self):
        """Выбор файла для анализа."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл для анализа",
            "",
            "Все файлы (*);;EXE файлы (*.exe);;DLL файлы (*.dll);;BAT файлы (*.bat)"
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
            self.log_message('INFO', f"Выбран файл: {file_path}")
    
    def start_analysis(self):
        """Запуск анализа."""
        file_path = self.file_path_edit.text()
        
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Ошибка", "Выберите корректный файл для анализа")
            return
        
        self.btn_analyze.setEnabled(False)
        self.btn_panic.setEnabled(True)
        self.progress_bar.setValue(0)
        
        self.log_message('INFO', f"Запуск анализа файла: {file_path}")
        
        # TODO: Реализовать worker thread для анализа
        self.progress_bar.setValue(100)
        self.progress_label.setText("Анализ завершен!")
        self.btn_analyze.setEnabled(True)
        self.btn_panic.setEnabled(False)
    
    def emergency_stop(self):
        """Экстренная остановка анализа."""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите остановить анализ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.log_message('WARNING', "Экстренная остановка анализа!")
            self.btn_analyze.setEnabled(True)
            self.btn_panic.setEnabled(False)
    
    def log_message(self, level: str, message: str):
        """Добавление сообщения в лог."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colored_message = f"[{timestamp}] [{level}] {message}"
        
        self.log_viewer.append(colored_message)
        self.log_viewer.verticalScrollBar().setValue(
            self.log_viewer.verticalScrollBar().maximum()
        )
    
    def clear_logs(self):
        """Очистка логов."""
        self.log_viewer.clear()
        self.log_message('INFO', "Логи очищены")
    
    def filter_logs(self, filter_text):
        """Фильтрация логов."""
        # TODO: Реализовать фильтрацию
        pass
    
    def export_logs(self):
        """Экспорт логов."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить логи",
            "logs.txt",
            "Текстовые файлы (*.txt)"
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.log_viewer.toPlainText())
            self.log_message('INFO', f"Логи экспортированы в {file_path}")
    
    def export_ioc(self, format_type: str):
        """Экспорт IOC."""
        QMessageBox.information(self, "Информация", f"Экспорт IOC в формате {format_type}")
    
    def open_settings(self):
        """Открытие диалога настроек."""
        QMessageBox.information(self, "Настройки", "Диалог настроек будет реализован")
    
    def open_theme_customizer(self):
        """Открытие конструктора тем."""
        dialog = ThemeCustomizerDialog(self.theme_manager, self)
        dialog.exec_()
    
    def open_reports_folder(self):
        """Открытие папки отчетов."""
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(reports_dir)))
    
    def generate_test_samples(self):
        """Генерация тестовых образцов."""
        QMessageBox.information(self, "Генерация образцов", "Функция генерации тестовых образцов")
    
    def show_about(self):
        """Показ информации о программе."""
        QMessageBox.about(
            self,
            "О программе",
            "<h2>🛡️ RedSand Secure v3.0</h2>"
            "<p>Профессиональная система анализа вредоносного ПО</p>"
            "<p><b>Версия:</b> 3.0 Ultra Customizable</p>"
            "<p><b>Особенности:</b></p>"
            "<ul>"
            "<li>8 предустановленных тем</li>"
            "<li>Конструктор пользовательских тем</li>"
            "<li>Расширенная кастомизация интерфейса</li>"
            "<li>Градиентные эффекты и анимации</li>"
            "</ul>"
        )
    
    def load_settings(self):
        """Загрузка настроек."""
        # TODO: Загрузка настроек из файла
        pass
    
    def save_settings(self):
        """Сохранение настроек."""
        # TODO: Сохранение настроек в файл
        pass
    
    def closeEvent(self, event):
        """Обработка закрытия окна."""
        reply = QMessageBox.question(
            self,
            "Выход",
            "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.save_settings()
            event.accept()
        else:
            event.ignore()


# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================

def main():
    """Точка входа в приложение."""
    app = QApplication(sys.argv)
    app.setApplicationName("RedSand Secure")
    app.setOrganizationName("RedSand Security")
    app.setStyle(QStyleFactory.create('Fusion'))
    
    # Установка иконки приложения
    # app.setWindowIcon(QIcon('icon.png'))
    
    window = RedSandSecureGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
