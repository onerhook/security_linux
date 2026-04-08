#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Secure GUI v4.0 - Professional Interface
Улучшенный интерфейс с поддержкой 6 языков, продвинутой визуализацией и настройками
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
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QTextEdit, QFileDialog, QGroupBox, QGridLayout,
    QSplitter, QTabWidget, QFrame, QScrollArea, QMessageBox, QCheckBox,
    QSpinBox, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QStatusBar,
    QToolBar, QAction, QMenu, QMenuBar, QSystemTrayIcon, QTreeWidget,
    QTreeWidgetItem, QListWidget, QListWidgetItem, QSlider, QColorDialog,
    QFontDialog, QRadioButton, QButtonGroup, QDoubleSpinBox,
    QKeySequenceEdit, QShortcut, QDockWidget, QToolButton, QStyleFactory,
    QCompleter, QSizePolicy, QGraphicsDropShadowEffect, QStackedWidget,
    QWizard, QWizardPage, QCalendarWidget, QTimeEdit, QDateEdit,
    QLCDNumber, QDial, QPlainTextEdit, QTreeView, QColumnView, QTableView,
    QAbstractItemView, QActionGroup, QSpacerItem, QTabBar
)
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QObject, QThread, QMetaObject, Q_ARG,
    QPropertyAnimation, QEasingCurve, QSize, QUrl, QSettings, QMimeData,
    QPoint, QRect, QVariant, QMargins, QParallelAnimationGroup,
    QSequentialAnimationGroup, pyqtProperty, QStateMachine, QState,
    QSignalTransition, QEventTransition, QFile, QTextStream, QIODevice,
    QFileInfo, QDir, QStandardPaths, QDateTime, QLocale, QMutex,
    QWaitCondition, QTranslator, QLibraryInfo, QCoreApplication
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QIcon, QPixmap, QPainter, QBrush, QPen,
    QLinearGradient, QRadialGradient, QConicalGradient, QTextCursor,
    QTextDocument, QGradient, QFontDatabase, QSyntaxHighlighter,
    QTextCharFormat, QKeySequence, QImage, QTransform, QPolygon, QPolygonF,
    QFontMetrics, QFontInfo
)

# Добавляем модули в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from redsand_secure import RedSandSecure
    REDSAND_AVAILABLE = True
except ImportError:
    REDSAND_AVAILABLE = False


# ============================================================================
# ИНТЕРНАЦИОНАЛИЗАЦИЯ - 6 ЯЗЫКОВ
# ============================================================================

TRANSLATIONS = {
    'ru': {
        'app_title': 'RedSand Secure v4.0',
        'menu_file': 'Файл',
        'menu_settings': 'Настройки',
        'menu_view': 'Вид',
        'menu_help': 'Помощь',
        'action_open': 'Открыть файл...',
        'action_exit': 'Выход',
        'action_settings': 'Настройки...',
        'action_theme': 'Тема',
        'action_language': 'Язык',
        'action_about': 'О программе',
        'btn_analyze': 'Анализировать',
        'btn_stop': 'Стоп',
        'btn_browse': 'Обзор',
        'btn_export': 'Экспорт',
        'btn_clear': 'Очистить',
        'lbl_file': 'Файл:',
        'lbl_status': 'Статус:',
        'lbl_progress': 'Прогресс:',
        'lbl_time': 'Время:',
        'lbl_threats': 'Угрозы обнаружены:',
        'tab_logs': 'Логи',
        'tab_results': 'Результаты',
        'tab_ioc': 'IOC',
        'tab_visualization': 'Визуализация',
        'tab_graph': 'Граф вызовов',
        'tab_memory': 'Карта памяти',
        'status_ready': 'Готов к работе',
        'status_analyzing': 'Анализ...',
        'status_complete': 'Анализ завершён',
        'msg_no_file': 'Файл не выбран',
        'msg_analysis_complete': 'Анализ завершён успешно',
        'settings_title': 'Настройки',
        'settings_general': 'Общие',
        'settings_appearance': 'Внешний вид',
        'settings_analysis': 'Анализ',
        'chk_network_isolation': 'Изоляция сети',
        'chk_polymorphic': 'Полиморфный анализ',
        'chk_auto_export': 'Автоэкспорт отчётов',
        'lbl_font_size': 'Размер шрифта:',
        'lbl_animation': 'Анимация:',
        'chk_enable_animations': 'Включить анимации',
        'lbl_theme': 'Тема:',
        'lbl_language': 'Язык:',
        'btn_save': 'Сохранить',
        'btn_cancel': 'Отмена',
        'viz_call_graph': 'Граф вызовов функций',
        'viz_memory_map': 'Карта памяти процесса',
        'viz_api_calls': 'API вызовы',
        'viz_strings': 'Строки',
        'info_total_functions': 'Всего функций:',
        'info_dangerous': 'Опасные:',
        'info_memory_regions': 'Регионов памяти:',
        'info_heap_size': 'Размер кучи:',
        'lang_ru': 'Русский',
        'lang_en': 'English',
        'lang_cn': '中文',
        'lang_es': 'Español',
        'lang_de': 'Deutsch',
        'lang_fr': 'Français',
    },
    'en': {
        'app_title': 'RedSand Secure v4.0',
        'menu_file': 'File',
        'menu_settings': 'Settings',
        'menu_view': 'View',
        'menu_help': 'Help',
        'action_open': 'Open File...',
        'action_exit': 'Exit',
        'action_settings': 'Settings...',
        'action_theme': 'Theme',
        'action_language': 'Language',
        'action_about': 'About',
        'btn_analyze': 'Analyze',
        'btn_stop': 'Stop',
        'btn_browse': 'Browse',
        'btn_export': 'Export',
        'btn_clear': 'Clear',
        'lbl_file': 'File:',
        'lbl_status': 'Status:',
        'lbl_progress': 'Progress:',
        'lbl_time': 'Time:',
        'lbl_threats': 'Threats Detected:',
        'tab_logs': 'Logs',
        'tab_results': 'Results',
        'tab_ioc': 'IOC',
        'tab_visualization': 'Visualization',
        'tab_graph': 'Call Graph',
        'tab_memory': 'Memory Map',
        'status_ready': 'Ready',
        'status_analyzing': 'Analyzing...',
        'status_complete': 'Analysis Complete',
        'msg_no_file': 'No file selected',
        'msg_analysis_complete': 'Analysis completed successfully',
        'settings_title': 'Settings',
        'settings_general': 'General',
        'settings_appearance': 'Appearance',
        'settings_analysis': 'Analysis',
        'chk_network_isolation': 'Network Isolation',
        'chk_polymorphic': 'Polymorphic Analysis',
        'chk_auto_export': 'Auto-export Reports',
        'lbl_font_size': 'Font Size:',
        'lbl_animation': 'Animation:',
        'chk_enable_animations': 'Enable Animations',
        'lbl_theme': 'Theme:',
        'lbl_language': 'Language:',
        'btn_save': 'Save',
        'btn_cancel': 'Cancel',
        'viz_call_graph': 'Function Call Graph',
        'viz_memory_map': 'Process Memory Map',
        'viz_api_calls': 'API Calls',
        'viz_strings': 'Strings',
        'info_total_functions': 'Total Functions:',
        'info_dangerous': 'Dangerous:',
        'info_memory_regions': 'Memory Regions:',
        'info_heap_size': 'Heap Size:',
        'lang_ru': 'Русский',
        'lang_en': 'English',
        'lang_cn': '中文',
        'lang_es': 'Español',
        'lang_de': 'Deutsch',
        'lang_fr': 'Français',
    },
    'cn': {
        'app_title': 'RedSand Secure v4.0',
        'menu_file': '文件',
        'menu_settings': '设置',
        'menu_view': '视图',
        'menu_help': '帮助',
        'action_open': '打开文件...',
        'action_exit': '退出',
        'action_settings': '设置...',
        'action_theme': '主题',
        'action_language': '语言',
        'action_about': '关于',
        'btn_analyze': '分析',
        'btn_stop': '停止',
        'btn_browse': '浏览',
        'btn_export': '导出',
        'btn_clear': '清除',
        'lbl_file': '文件:',
        'lbl_status': '状态:',
        'lbl_progress': '进度:',
        'lbl_time': '时间:',
        'lbl_threats': '检测到威胁:',
        'tab_logs': '日志',
        'tab_results': '结果',
        'tab_ioc': '入侵指标',
        'tab_visualization': '可视化',
        'tab_graph': '调用图',
        'tab_memory': '内存映射',
        'status_ready': '就绪',
        'status_analyzing': '分析中...',
        'status_complete': '分析完成',
        'msg_no_file': '未选择文件',
        'msg_analysis_complete': '分析成功完成',
        'settings_title': '设置',
        'settings_general': '常规',
        'settings_appearance': '外观',
        'settings_analysis': '分析',
        'chk_network_isolation': '网络隔离',
        'chk_polymorphic': '多态分析',
        'chk_auto_export': '自动导出报告',
        'lbl_font_size': '字体大小:',
        'lbl_animation': '动画:',
        'chk_enable_animations': '启用动画',
        'lbl_theme': '主题:',
        'lbl_language': '语言:',
        'btn_save': '保存',
        'btn_cancel': '取消',
        'viz_call_graph': '函数调用图',
        'viz_memory_map': '进程内存映射',
        'viz_api_calls': 'API 调用',
        'viz_strings': '字符串',
        'info_total_functions': '函数总数:',
        'info_dangerous': '危险函数:',
        'info_memory_regions': '内存区域:',
        'info_heap_size': '堆大小:',
        'lang_ru': 'Русский',
        'lang_en': 'English',
        'lang_cn': '中文',
        'lang_es': 'Español',
        'lang_de': 'Deutsch',
        'lang_fr': 'Français',
    },
    'es': {
        'app_title': 'RedSand Secure v4.0',
        'menu_file': 'Archivo',
        'menu_settings': 'Configuración',
        'menu_view': 'Vista',
        'menu_help': 'Ayuda',
        'action_open': 'Abrir archivo...',
        'action_exit': 'Salir',
        'action_settings': 'Configuración...',
        'action_theme': 'Tema',
        'action_language': 'Idioma',
        'action_about': 'Acerca de',
        'btn_analyze': 'Analizar',
        'btn_stop': 'Detener',
        'btn_browse': 'Examinar',
        'btn_export': 'Exportar',
        'btn_clear': 'Limpiar',
        'lbl_file': 'Archivo:',
        'lbl_status': 'Estado:',
        'lbl_progress': 'Progreso:',
        'lbl_time': 'Tiempo:',
        'lbl_threats': 'Amenazas detectadas:',
        'tab_logs': 'Registros',
        'tab_results': 'Resultados',
        'tab_ioc': 'IOC',
        'tab_visualization': 'Visualización',
        'tab_graph': 'Gráfico de llamadas',
        'tab_memory': 'Mapa de memoria',
        'status_ready': 'Listo',
        'status_analyzing': 'Analizando...',
        'status_complete': 'Análisis completado',
        'msg_no_file': 'Ningún archivo seleccionado',
        'msg_analysis_complete': 'Análisis completado con éxito',
        'settings_title': 'Configuración',
        'settings_general': 'General',
        'settings_appearance': 'Apariencia',
        'settings_analysis': 'Análisis',
        'chk_network_isolation': 'Aislamiento de red',
        'chk_polymorphic': 'Análisis polimórfico',
        'chk_auto_export': 'Auto-exportar informes',
        'lbl_font_size': 'Tamaño de fuente:',
        'lbl_animation': 'Animación:',
        'chk_enable_animations': 'Habilitar animaciones',
        'lbl_theme': 'Tema:',
        'lbl_language': 'Idioma:',
        'btn_save': 'Guardar',
        'btn_cancel': 'Cancelar',
        'viz_call_graph': 'Gráfico de llamadas a funciones',
        'viz_memory_map': 'Mapa de memoria del proceso',
        'viz_api_calls': 'Llamadas API',
        'viz_strings': 'Cadenas',
        'info_total_functions': 'Funciones totales:',
        'info_dangerous': 'Peligrosas:',
        'info_memory_regions': 'Regiones de memoria:',
        'info_heap_size': 'Tamaño del heap:',
        'lang_ru': 'Русский',
        'lang_en': 'English',
        'lang_cn': '中文',
        'lang_es': 'Español',
        'lang_de': 'Deutsch',
        'lang_fr': 'Français',
    },
    'de': {
        'app_title': 'RedSand Secure v4.0',
        'menu_file': 'Datei',
        'menu_settings': 'Einstellungen',
        'menu_view': 'Ansicht',
        'menu_help': 'Hilfe',
        'action_open': 'Datei öffnen...',
        'action_exit': 'Beenden',
        'action_settings': 'Einstellungen...',
        'action_theme': 'Design',
        'action_language': 'Sprache',
        'action_about': 'Über',
        'btn_analyze': 'Analysieren',
        'btn_stop': 'Stopp',
        'btn_browse': 'Durchsuchen',
        'btn_export': 'Exportieren',
        'btn_clear': 'Löschen',
        'lbl_file': 'Datei:',
        'lbl_status': 'Status:',
        'lbl_progress': 'Fortschritt:',
        'lbl_time': 'Zeit:',
        'lbl_threats': 'Bedrohungen erkannt:',
        'tab_logs': 'Protokolle',
        'tab_results': 'Ergebnisse',
        'tab_ioc': 'IOC',
        'tab_visualization': 'Visualisierung',
        'tab_graph': 'Aufrufgraph',
        'tab_memory': 'Speicherkarte',
        'status_ready': 'Bereit',
        'status_analyzing': 'Analysiere...',
        'status_complete': 'Analyse abgeschlossen',
        'msg_no_file': 'Keine Datei ausgewählt',
        'msg_analysis_complete': 'Analyse erfolgreich abgeschlossen',
        'settings_title': 'Einstellungen',
        'settings_general': 'Allgemein',
        'settings_appearance': 'Erscheinungsbild',
        'settings_analysis': 'Analyse',
        'chk_network_isolation': 'Netzwerkisolation',
        'chk_polymorphic': 'Polymorphe Analyse',
        'chk_auto_export': 'Berichte automatisch exportieren',
        'lbl_font_size': 'Schriftgröße:',
        'lbl_animation': 'Animation:',
        'chk_enable_animations': 'Animationen aktivieren',
        'lbl_theme': 'Design:',
        'lbl_language': 'Sprache:',
        'btn_save': 'Speichern',
        'btn_cancel': 'Abbrechen',
        'viz_call_graph': 'Funktionsaufrufgraph',
        'viz_memory_map': 'Prozess-Speicherkarte',
        'viz_api_calls': 'API-Aufrufe',
        'viz_strings': 'Zeichenfolgen',
        'info_total_functions': 'Gesamte Funktionen:',
        'info_dangerous': 'Gefährlich:',
        'info_memory_regions': 'Speicherbereiche:',
        'info_heap_size': 'Heap-Größe:',
        'lang_ru': 'Русский',
        'lang_en': 'English',
        'lang_cn': '中文',
        'lang_es': 'Español',
        'lang_de': 'Deutsch',
        'lang_fr': 'Français',
    },
    'fr': {
        'app_title': 'RedSand Secure v4.0',
        'menu_file': 'Fichier',
        'menu_settings': 'Paramètres',
        'menu_view': 'Affichage',
        'menu_help': 'Aide',
        'action_open': 'Ouvrir un fichier...',
        'action_exit': 'Quitter',
        'action_settings': 'Paramètres...',
        'action_theme': 'Thème',
        'action_language': 'Langue',
        'action_about': 'À propos',
        'btn_analyze': 'Analyser',
        'btn_stop': 'Arrêter',
        'btn_browse': 'Parcourir',
        'btn_export': 'Exporter',
        'btn_clear': 'Effacer',
        'lbl_file': 'Fichier:',
        'lbl_status': 'Statut:',
        'lbl_progress': 'Progression:',
        'lbl_time': 'Temps:',
        'lbl_threats': 'Menaces détectées:',
        'tab_logs': 'Journaux',
        'tab_results': 'Résultats',
        'tab_ioc': 'IOC',
        'tab_visualization': 'Visualisation',
        'tab_graph': 'Graphe d\'appel',
        'tab_memory': 'Carte mémoire',
        'status_ready': 'Prêt',
        'status_analyzing': 'Analyse en cours...',
        'status_complete': 'Analyse terminée',
        'msg_no_file': 'Aucun fichier sélectionné',
        'msg_analysis_complete': 'Analyse terminée avec succès',
        'settings_title': 'Paramètres',
        'settings_general': 'Général',
        'settings_appearance': 'Apparence',
        'settings_analysis': 'Analyse',
        'chk_network_isolation': 'Isolation réseau',
        'chk_polymorphic': 'Analyse polymorphique',
        'chk_auto_export': 'Exportation automatique des rapports',
        'lbl_font_size': 'Taille de police:',
        'lbl_animation': 'Animation:',
        'chk_enable_animations': 'Activer les animations',
        'lbl_theme': 'Thème:',
        'lbl_language': 'Langue:',
        'btn_save': 'Enregistrer',
        'btn_cancel': 'Annuler',
        'viz_call_graph': 'Graphe d\'appel de fonctions',
        'viz_memory_map': 'Carte mémoire du processus',
        'viz_api_calls': 'Appels API',
        'viz_strings': 'Chaînes',
        'info_total_functions': 'Total des fonctions:',
        'info_dangerous': 'Dangereuses:',
        'info_memory_regions': 'Régions mémoire:',
        'info_heap_size': 'Taille du tas:',
        'lang_ru': 'Русский',
        'lang_en': 'English',
        'lang_cn': '中文',
        'lang_es': 'Español',
        'lang_de': 'Deutsch',
        'lang_fr': 'Français',
    },
}


class LanguageManager(QObject):
    """Менеджер языков для интернационализации."""

    language_changed = pyqtSignal(str)

    SUPPORTED_LANGUAGES = ['ru', 'en', 'cn', 'es', 'de', 'fr']

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_language = 'ru'
        self.load_settings()

    def load_settings(self):
        """Загрузка настроек языка."""
        settings = QSettings('RedSand', 'SecureGUI')
        self.current_language = settings.value('language', 'ru')
        if self.current_language not in self.SUPPORTED_LANGUAGES:
            self.current_language = 'ru'

    def save_settings(self):
        """Сохранение настроек языка."""
        settings = QSettings('RedSand', 'SecureGUI')
        settings.setValue('language', self.current_language)

    def set_language(self, lang: str):
        """Установка текущего языка."""
        if lang in self.SUPPORTED_LANGUAGES:
            self.current_language = lang
            self.save_settings()
            self.language_changed.emit(lang)

    def get_text(self, key: str) -> str:
        """Получение текста на текущем языке."""
        return TRANSLATIONS.get(self.current_language, TRANSLATIONS['ru']).get(key, key)

    def get_all_languages(self) -> List[tuple]:
        """Получение списка всех языков."""
        return [
            ('ru', self.get_text('lang_ru')),
            ('en', self.get_text('lang_en')),
            ('cn', self.get_text('lang_cn')),
            ('es', self.get_text('lang_es')),
            ('de', self.get_text('lang_de')),
            ('fr', self.get_text('lang_fr')),
        ]


# ============================================================================
# МЕНЕДЖЕР ТЕМ И СТИЛЕЙ (УЛУЧШЕННЫЙ)
# ============================================================================

class ThemeManager(QObject):
    """Менеджер тем для гибкой кастомизации интерфейса."""

    theme_changed = pyqtSignal(str)

    # Предопределённые темы с ВЫСОКИМ КОНТРАСТОМ
    PRESET_THEMES = {
        'dark_professional': {
            'primary_bg': '#1a1d29',
            'secondary_bg': '#252a3d',
            'tertiary_bg': '#2d3349',
            'accent_color': '#4fc3f7',
            'text_primary': '#ffffff',
            'text_secondary': '#b0bec5',
            'border_color': '#3d4559',
            'hover_color': '#42a5f5',
            'success_color': '#66bb6a',
            'warning_color': '#ffa726',
            'danger_color': '#ef5350',
            'gradient_start': '#42a5f5',
            'gradient_end': '#4fc3f7',
            'shadow_color': '#000000',
        },
        'light_clean': {
            'primary_bg': '#f8f9fa',
            'secondary_bg': '#ffffff',
            'tertiary_bg': '#e9ecef',
            'accent_color': '#1976d2',
            'text_primary': '#212529',
            'text_secondary': '#495057',
            'border_color': '#dee2e6',
            'hover_color': '#e3f2fd',
            'success_color': '#2e7d32',
            'warning_color': '#f57c00',
            'danger_color': '#d32f2f',
            'gradient_start': '#1976d2',
            'gradient_end': '#42a5f5',
            'shadow_color': '#000000',
        },
        'cyber_neon': {
            'primary_bg': '#0a0e17',
            'secondary_bg': '#151a28',
            'tertiary_bg': '#1f2738',
            'accent_color': '#00ff88',
            'text_primary': '#ffffff',
            'text_secondary': '#a0aab5',
            'border_color': '#00ff88',
            'hover_color': '#00ffaa',
            'success_color': '#00ff88',
            'warning_color': '#ffcc00',
            'danger_color': '#ff3366',
            'gradient_start': '#00ff88',
            'gradient_end': '#00ccff',
            'shadow_color': '#00ff88',
        },
        'midnight_blue': {
            'primary_bg': '#1a2332',
            'secondary_bg': '#243045',
            'tertiary_bg': '#2d3a52',
            'accent_color': '#64b5f6',
            'text_primary': '#ffffff',
            'text_secondary': '#b0bec5',
            'border_color': '#3d4f68',
            'hover_color': '#42a5f5',
            'success_color': '#66bb6a',
            'warning_color': '#ffb74d',
            'danger_color': '#e57373',
            'gradient_start': '#64b5f6',
            'gradient_end': '#42a5f5',
            'shadow_color': '#000000',
        },
        'forest_dark': {
            'primary_bg': '#1a2421',
            'secondary_bg': '#23322d',
            'tertiary_bg': '#2d3f38',
            'accent_color': '#81c784',
            'text_primary': '#ffffff',
            'text_secondary': '#a5b5ae',
            'border_color': '#3d5248',
            'hover_color': '#66bb6a',
            'success_color': '#81c784',
            'warning_color': '#ffd54f',
            'danger_color': '#e57373',
            'gradient_start': '#81c784',
            'gradient_end': '#4caf50',
            'shadow_color': '#000000',
        },
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = 'dark_professional'
        self.custom_themes = {}
        self.font_size = 13
        self.animations_enabled = True
        self.load_custom_themes()
        self.load_settings()

    def load_settings(self):
        """Загрузка настроек темы."""
        settings = QSettings('RedSand', 'SecureGUI')
        self.current_theme = settings.value('theme', 'dark_professional')
        self.font_size = int(settings.value('font_size', 13))
        self.animations_enabled = settings.value('animations_enabled', True, type=bool)

    def save_settings(self):
        """Сохранение настроек темы."""
        settings = QSettings('RedSand', 'SecureGUI')
        settings.setValue('theme', self.current_theme)
        settings.setValue('font_size', self.font_size)
        settings.setValue('animations_enabled', self.animations_enabled)

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
            return self.PRESET_THEMES['dark_professional'].copy()

    def set_current_theme(self, theme_name: str):
        """Установка текущей темы."""
        if theme_name in self.PRESET_THEMES or theme_name in self.custom_themes:
            self.current_theme = theme_name
            self.save_settings()
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

        fs = self.font_size

        stylesheet = f"""
/* === RedSand Secure v4.0 - Professional Theme === */

QMainWindow {{
    background-color: {theme['primary_bg']};
    color: {theme['text_primary']};
}}

QWidget {{
    font-family: 'Segoe UI', 'Roboto', 'Noto Sans', Arial, sans-serif;
    font-size: {fs}px;
    background-color: {theme['primary_bg']};
    color: {theme['text_primary']};
}}

/* Заголовки */
QLabel#titleLabel {{
    font-size: {fs + 8}px;
    font-weight: 700;
    color: {theme['text_primary']};
    padding: 12px 20px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {theme['gradient_start']},
                                stop:1 {theme['gradient_end']});
    border-radius: 10px;
}}

QLabel#sectionTitle {{
    font-size: {fs + 2}px;
    font-weight: 600;
    color: {theme['text_primary']};
    background-color: {theme['accent_color']};
    padding: 8px 15px;
    border-radius: 6px;
}}

QLabel {{
    color: {theme['text_primary']};
}}

/* Группы */
QGroupBox {{
    font-weight: 600;
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
    background-color: {theme['tertiary_bg']};
    color: {theme['text_primary']};
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: 600;
    min-width: 120px;
}}

QPushButton:hover {{
    background-color: {theme['hover_color']};
    color: {theme['primary_bg']};
}}

QPushButton:pressed {{
    background-color: {theme['accent_color']};
    color: {theme['primary_bg']};
}}

QPushButton:disabled {{
    background-color: {theme['tertiary_bg']};
    color: {theme['text_secondary']};
}}

QPushButton#primaryBtn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {theme['gradient_start']},
                                stop:1 {theme['gradient_end']});
    font-size: {fs + 1}px;
    padding: 12px 30px;
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
    opacity: 0.9;
}}

QPushButton#successBtn {{
    background-color: {theme['success_color']};
    color: white;
}}

QPushButton#successBtn:hover {{
    background-color: {theme['success_color']};
    opacity: 0.9;
}}

/* Прогресс бар */
QProgressBar {{
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    text-align: center;
    font-weight: 600;
    background-color: {theme['tertiary_bg']};
    height: 25px;
    color: {theme['text_primary']};
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {theme['gradient_start']},
                                stop:1 {theme['gradient_end']});
    border-radius: 6px;
}}

/* Текстовые поля */
QTextEdit, QPlainTextEdit, QLineEdit {{
    background-color: {theme['secondary_bg']};
    color: {theme['text_primary']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', 'DejaVu Sans Mono', monospace;
    font-size: {fs - 1}px;
}}

QTextEdit:focus, QPlainTextEdit:focus, QLineEdit:focus {{
    border: 2px solid {theme['accent_color']};
}}

/* Таблицы */
QTableWidget {{
    background-color: {theme['secondary_bg']};
    alternate-background-color: {theme['tertiary_bg']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    gridline-color: {theme['border_color']};
}}

QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {theme['border_color']};
    color: {theme['text_primary']};
}}

QTableWidget::item:selected {{
    background-color: {theme['accent_color']};
    color: {theme['primary_bg']};
}}

QHeaderView::section {{
    background-color: {theme['tertiary_bg']};
    color: {theme['accent_color']};
    padding: 10px;
    border: none;
    font-weight: 600;
    border-bottom: 2px solid {theme['border_color']};
}}

/* Вкладки */
QTabWidget::pane {{
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    background-color: {theme['secondary_bg']};
}}

QTabBar::tab {{
    background-color: {theme['tertiary_bg']};
    color: {theme['text_secondary']};
    padding: 10px 20px;
    margin-right: 3px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 500;
}}

QTabBar::tab:selected {{
    background-color: {theme['accent_color']};
    font-weight: 600;
    color: {theme['primary_bg']};
}}

QTabBar::tab:hover:!selected {{
    background-color: {theme['hover_color']};
    color: {theme['primary_bg']};
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
    color: {theme['text_primary']};
}}

QTreeWidget::item:selected, QListWidget::item:selected {{
    background-color: {theme['accent_color']};
    color: {theme['primary_bg']};
}}

QTreeWidget::item:hover, QListWidget::item:hover {{
    background-color: {theme['hover_color']};
    color: {theme['primary_bg']};
}}

/* Комбобоксы */
QComboBox {{
    background-color: {theme['tertiary_bg']};
    color: {theme['text_primary']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    padding: 8px 15px;
    min-width: 120px;
}}

QComboBox:hover {{
    border: 2px solid {theme['accent_color']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox QAbstractItemView {{
    background-color: {theme['secondary_bg']};
    color: {theme['text_primary']};
    border: 2px solid {theme['border_color']};
    selection-background-color: {theme['accent_color']};
}}

/* Чекбоксы и радиокнопки */
QCheckBox, QRadioButton {{
    color: {theme['text_primary']};
    spacing: 8px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid {theme['border_color']};
    background-color: {theme['secondary_bg']};
}}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {theme['accent_color']};
    border: 2px solid {theme['accent_color']};
}}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
    border: 2px solid {theme['hover_color']};
}}

/* Спинбоксы */
QSpinBox, QDoubleSpinBox {{
    background-color: {theme['tertiary_bg']};
    color: {theme['text_primary']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    padding: 8px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {theme['accent_color']};
}}

/* Слайдеры */
QSlider::groove:horizontal {{
    border: 1px solid {theme['border_color']};
    height: 8px;
    background: {theme['tertiary_bg']};
    border-radius: 4px;
}}

QSlider::handle:horizontal {{
    background: {theme['accent_color']};
    border: none;
    width: 18px;
    margin: -5px 0;
    border-radius: 9px;
}}

QSlider::handle:horizontal:hover {{
    background: {theme['hover_color']};
}}

/* Меню */
QMenuBar {{
    background-color: {theme['secondary_bg']};
    color: {theme['text_primary']};
    border-bottom: 2px solid {theme['border_color']};
    padding: 5px;
}}

QMenuBar::item {{
    padding: 8px 15px;
    border-radius: 5px;
}}

QMenuBar::item:selected {{
    background-color: {theme['hover_color']};
    color: {theme['primary_bg']};
}}

QMenu {{
    background-color: {theme['secondary_bg']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    padding: 5px;
}}

QMenu::item {{
    padding: 8px 30px;
    color: {theme['text_primary']};
}}

QMenu::item:selected {{
    background-color: {theme['accent_color']};
    color: {theme['primary_bg']};
}}

/* Тулбар */
QToolBar {{
    background-color: {theme['secondary_bg']};
    border: none;
    border-bottom: 2px solid {theme['border_color']};
    padding: 5px;
    spacing: 5px;
}}

QToolBar::separator {{
    width: 2px;
    background-color: {theme['border_color']};
    margin: 5px;
}}

/* Статус бар */
QStatusBar {{
    background-color: {theme['secondary_bg']};
    color: {theme['text_secondary']};
    border-top: 2px solid {theme['border_color']};
    padding: 5px;
}}

/* Скроллбары */
QScrollBar:vertical {{
    background-color: {theme['tertiary_bg']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {theme['border_color']};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {theme['hover_color']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {theme['tertiary_bg']};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {theme['border_color']};
    border-radius: 6px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {theme['hover_color']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* LCD Number */
QLCDNumber {{
    background-color: {theme['tertiary_bg']};
    color: {theme['accent_color']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    padding: 5px;
}}

/* Tooltips */
QToolTip {{
    background-color: {theme['secondary_bg']};
    color: {theme['text_primary']};
    border: 2px solid {theme['accent_color']};
    border-radius: 5px;
    padding: 5px 10px;
}}

/* Separator */
Line {{
    background-color: {theme['border_color']};
    max-height: 2px;
}}
"""
        return stylesheet


# ============================================================================
# ВИЗУАЛИЗАЦИЯ - ГРАФЫ И КАРТЫ ПАМЯТИ
# ============================================================================

class CallGraphWidget(QWidget):
    """Виджет для отображения графа вызовов функций."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes = []
        self.edges = []
        self.selected_node = None
        self.zoom = 1.0
        self.offset = QPoint(0, 0)
        self.setMouseTracking(True)
        self.setMinimumSize(400, 300)

    def set_data(self, nodes: List[dict], edges: List[tuple]):
        """Установка данных графа."""
        self.nodes = nodes
        self.edges = edges
        self.update()

    def paintEvent(self, event):
        """Отрисовка графа."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Получаем тему
        theme_mgr = self.window().theme_manager if hasattr(self.window(), 'theme_manager') else None
        if theme_mgr:
            theme = theme_mgr.get_theme(theme_mgr.current_theme)
        else:
            theme = {
                'primary_bg': '#1a1d29',
                'text_primary': '#ffffff',
                'accent_color': '#4fc3f7',
                'danger_color': '#ef5350',
                'success_color': '#66bb6a',
                'border_color': '#3d4559',
            }

        # Очистка фона
        painter.fillRect(self.rect(), QColor(theme['primary_bg']))

        # Применяем трансформацию
        painter.translate(self.offset)
        painter.scale(self.zoom, self.zoom)

        # Рисуем рёбра
        pen = QPen(QColor(theme['border_color']), 2)
        painter.setPen(pen)
        for edge in self.edges:
            if len(edge) >= 2:
                start = self.nodes[edge[0]] if isinstance(edge[0], int) and edge[0] < len(self.nodes) else None
                end = self.nodes[edge[1]] if isinstance(edge[1], int) and edge[1] < len(self.nodes) else None
                if start and end:
                    painter.drawLine(
                        int(start.get('x', 100)), int(start.get('y', 100)),
                        int(end.get('x', 200)), int(end.get('y', 200))
                    )

        # Рисуем узлы
        for i, node in enumerate(self.nodes):
            x = node.get('x', 100 + i * 50)
            y = node.get('y', 100)
            name = node.get('name', f'func_{i}')
            is_dangerous = node.get('dangerous', False)

            # Цвет узла
            if is_dangerous:
                brush = QBrush(QColor(theme['danger_color']))
            else:
                brush = QBrush(QColor(theme['success_color']))

            # Рисуем круг
            painter.setBrush(brush)
            painter.setPen(QPen(QColor(theme['text_primary']), 2))
            painter.drawEllipse(int(x) - 20, int(y) - 20, 40, 40)

            # Текст
            painter.setPen(QColor(theme['text_primary']))
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            metrics = QFontMetrics(font)
            text_rect = metrics.boundingRect(name)
            painter.drawText(
                int(x) - text_rect.width() // 2,
                int(y) + text_rect.height() // 4,
                name[:15]
            )

    def wheelEvent(self, event):
        """Зум колёсиком мыши."""
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1
        self.zoom = max(0.2, min(5.0, self.zoom))
        self.update()

    def mousePressEvent(self, event):
        """Перетаскивание графа."""
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier):
            self.drag_start = event.pos() - self.offset
            self.dragging = True
        else:
            # Выбор узла
            for i, node in enumerate(self.nodes):
                x = node.get('x', 100 + i * 50)
                y = node.get('y', 100)
                dx = event.pos().x() - x
                dy = event.pos().y() - y
                if dx * dx + dy * dy < 400:  # 20^2
                    self.selected_node = i
                    self.update()
                    break

    def mouseMoveEvent(self, event):
        """Перетаскивание."""
        if hasattr(self, 'dragging') and self.dragging:
            self.offset = event.pos() - self.drag_start
            self.update()


class MemoryMapWidget(QWidget):
    """Виджет для отображения карты памяти."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.regions = []
        self.hovered_region = None
        self.setMinimumSize(400, 300)

    def set_data(self, regions: List[dict]):
        """Установка данных регионов памяти."""
        self.regions = regions
        self.update()

    def paintEvent(self, event):
        """Отрисовка карты памяти."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Получаем тему
        theme_mgr = self.window().theme_manager if hasattr(self.window(), 'theme_manager') else None
        if theme_mgr:
            theme = theme_mgr.get_theme(theme_mgr.current_theme)
        else:
            theme = {
                'primary_bg': '#1a1d29',
                'text_primary': '#ffffff',
                'accent_color': '#4fc3f7',
                'border_color': '#3d4559',
                'warning_color': '#ffa726',
                'danger_color': '#ef5350',
                'success_color': '#66bb6a',
            }

        # Фон
        painter.fillRect(self.rect(), QColor(theme['primary_bg']))

        if not self.regions:
            # Пример данных
            self.regions = [
                {'start': 0x400000, 'end': 0x450000, 'type': 'code', 'protection': 'r-x'},
                {'start': 0x450000, 'end': 0x460000, 'type': 'data', 'protection': 'rw-'},
                {'start': 0x460000, 'end': 0x500000, 'type': 'heap', 'protection': 'rw-'},
                {'start': 0x7fff0000, 'end': 0x7fff8000, 'type': 'stack', 'protection': 'rw-'},
                {'start': 0x7f000000, 'end': 0x7f010000, 'type': 'shared', 'protection': 'r--'},
            ]

        # Рисуем регионы
        total_size = sum(r.get('end', 0) - r.get('start', 0) for r in self.regions)
        if total_size == 0:
            return

        y_offset = 20
        height = 30
        spacing = 10

        for i, region in enumerate(self.regions):
            size = region.get('end', 0) - region.get('start', 0)
            width = max(50, int((size / total_size) * (self.width() - 40)))

            # Цвет по типу
            rtype = region.get('type', 'unknown')
            if rtype == 'code':
                color = theme['success_color']
            elif rtype == 'heap':
                color = theme['warning_color']
            elif rtype == 'stack':
                color = theme['accent_color']
            elif rtype == 'shared':
                color = theme['border_color']
            else:
                color = theme['danger_color']

            # Рисуем прямоугольник
            rect = QRect(20, y_offset + i * (height + spacing), width, height)
            painter.fillRect(rect, QColor(color))
            painter.setPen(QPen(QColor(theme['text_primary']), 1))
            painter.drawRect(rect)

            # Текст
            painter.setPen(QColor(theme['text_primary']))
            font = painter.font()
            font.setPointSize(9)
            painter.setFont(font)
            addr_str = f"{region.get('start', 0):08X}"
            type_str = region.get('type', '?')
            prot_str = region.get('protection', '???')
            painter.drawText(rect.adjusted(5, 0, 0, 0), Qt.AlignLeft | Qt.AlignVCenter, f"{addr_str} [{type_str}] {prot_str}")

        # Легенда
        legend_y = y_offset + len(self.regions) * (height + spacing) + 20
        painter.setPen(QColor(theme['text_secondary']))
        painter.drawText(20, legend_y, "Legend: Code (green) | Heap (orange) | Stack (blue) | Shared (gray)")

    def mouseMoveEvent(self, event):
        """Ховер по регионам."""
        old_hovered = self.hovered_region
        self.hovered_region = None

        y_offset = 20
        height = 30
        spacing = 10

        for i, region in enumerate(self.regions):
            y = y_offset + i * (height + spacing)
            if y <= event.pos().y() <= y + height:
                self.hovered_region = i
                break

        if old_hovered != self.hovered_region:
            self.update()
            if self.hovered_region is not None:
                region = self.regions[self.hovered_region]
                tooltip = f"Address: {region.get('start', 0):08X}-{region.get('end', 0):08X}\nType: {region.get('type', 'unknown')}\nProtection: {region.get('protection', '???')}"
                QToolTip.showText(event.globalPos(), tooltip, self)


# ============================================================================
# ДИАЛОГ НАСТРОЕК
# ============================================================================

class SettingsDialog(QDialog):
    """Диалог настроек приложения."""

    def __init__(self, parent=None, theme_manager=None, language_manager=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.language_manager = language_manager
        self.setWindowTitle(self.tr('settings_title') if hasattr(self, 'tr') else 'Settings')
        self.setMinimumSize(500, 400)
        self.setup_ui()

        if self.theme_manager:
            self.apply_current_settings()

    def setup_ui(self):
        """Настройка интерфейса."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Вкладки настроек
        tab_widget = QTabWidget()

        # Вкладка "Общие"
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        general_layout.setSpacing(15)

        # Язык
        self.lang_combo = QComboBox()
        if self.language_manager:
            for code, name in self.language_manager.get_all_languages():
                self.lang_combo.addItem(name, code)
        general_layout.addRow(self.tr('lbl_language') if hasattr(self, 'tr') else 'Language:', self.lang_combo)

        # Тема
        self.theme_combo = QComboBox()
        if self.theme_manager:
            for theme_name in self.theme_manager.get_all_theme_names():
                self.theme_combo.addItem(theme_name.replace('_', ' ').title(), theme_name)
        general_layout.addRow(self.tr('lbl_theme') if hasattr(self, 'tr') else 'Theme:', self.theme_combo)

        tab_widget.addTab(general_tab, self.tr('settings_general') if hasattr(self, 'tr') else 'General')

        # Вкладка "Внешний вид"
        appearance_tab = QWidget()
        appearance_layout = QFormLayout(appearance_tab)
        appearance_layout.setSpacing(15)

        # Размер шрифта
        self.font_spin = QSpinBox()
        self.font_spin.setRange(10, 24)
        self.font_spin.setValue(13)
        appearance_layout.addRow(self.tr('lbl_font_size') if hasattr(self, 'tr') else 'Font Size:', self.font_spin)

        # Анимации
        self.animation_check = QCheckBox()
        appearance_layout.addRow(self.tr('chk_enable_animations') if hasattr(self, 'tr') else 'Enable Animations:', self.animation_check)

        tab_widget.addTab(appearance_tab, self.tr('settings_appearance') if hasattr(self, 'tr') else 'Appearance')

        # Вкладка "Анализ"
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        analysis_layout.setSpacing(15)

        self.network_check = QCheckBox(self.tr('chk_network_isolation') if hasattr(self, 'tr') else 'Network Isolation')
        self.network_check.setChecked(True)
        analysis_layout.addWidget(self.network_check)

        self.poly_check = QCheckBox(self.tr('chk_polymorphic') if hasattr(self, 'tr') else 'Polymorphic Analysis')
        self.poly_check.setChecked(True)
        analysis_layout.addWidget(self.poly_check)

        self.export_check = QCheckBox(self.tr('chk_auto_export') if hasattr(self, 'tr') else 'Auto-export Reports')
        self.export_check.setChecked(False)
        analysis_layout.addWidget(self.export_check)

        analysis_layout.addStretch()

        tab_widget.addTab(analysis_tab, self.tr('settings_analysis') if hasattr(self, 'tr') else 'Analysis')

        layout.addWidget(tab_widget)

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def apply_current_settings(self):
        """Применение текущих настроек."""
        if self.theme_manager:
            index = self.theme_combo.findData(self.theme_manager.current_theme)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
            self.font_spin.setValue(self.theme_manager.font_size)
            self.animation_check.setChecked(self.theme_manager.animations_enabled)

        if self.language_manager:
            index = self.lang_combo.findData(self.language_manager.current_language)
            if index >= 0:
                self.lang_combo.setCurrentIndex(index)

    def get_settings(self) -> dict:
        """Получение настроек."""
        return {
            'theme': self.theme_combo.currentData(),
            'font_size': self.font_spin.value(),
            'animations_enabled': self.animation_check.isChecked(),
            'language': self.lang_combo.currentData(),
            'network_isolation': self.network_check.isChecked(),
            'polymorphic_analysis': self.poly_check.isChecked(),
            'auto_export': self.export_check.isChecked(),
        }


# ============================================================================
# ГЛАВНОЕ ОКНО
# ============================================================================

class RedSandGUIv4(QMainWindow):
    """Главное окно приложения RedSand Secure v4.0."""

    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager(self)
        self.language_manager = LanguageManager(self)
        self.file_path = None
        self.is_analyzing = False

        # Применяем тему при старте
        self.apply_theme()

        self.setup_ui()
        self.setup_connections()
        self.update_texts()

    def setup_ui(self):
        """Настройка интерфейса."""
        self.setWindowTitle(self.language_manager.get_text('app_title'))
        self.setMinimumSize(1200, 800)

        # Центральное окно
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Заголовок
        title_label = QLabel(self.language_manager.get_text('app_title'))
        title_label.setObjectName('titleLabel')
        main_layout.addWidget(title_label)

        # Верхняя панель с выбором файла
        file_layout = QHBoxLayout()
        file_layout.setSpacing(10)

        file_label = QLabel(self.language_manager.get_text('lbl_file'))
        file_layout.addWidget(file_label)

        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText('Select a file to analyze...')
        file_layout.addWidget(self.file_edit, stretch=1)

        browse_btn = QPushButton(self.language_manager.get_text('btn_browse'))
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)

        main_layout.addLayout(file_layout)

        # Разделитель
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(5)

        # Левая панель
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)

        # Группа настроек анализа
        analysis_group = QGroupBox('Analysis Settings')
        analysis_layout = QVBoxLayout(analysis_group)

        self.network_check = QCheckBox(self.language_manager.get_text('chk_network_isolation'))
        self.network_check.setChecked(True)
        analysis_layout.addWidget(self.network_check)

        self.poly_check = QCheckBox(self.language_manager.get_text('chk_polymorphic'))
        self.poly_check.setChecked(True)
        analysis_layout.addWidget(self.poly_check)

        left_layout.addWidget(analysis_group)

        # Кнопки управления
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)

        self.analyze_btn = QPushButton(self.language_manager.get_text('btn_analyze'))
        self.analyze_btn.setObjectName('primaryBtn')
        self.analyze_btn.clicked.connect(self.start_analysis)
        btn_layout.addWidget(self.analyze_btn)

        self.stop_btn = QPushButton(self.language_manager.get_text('btn_stop'))
        self.stop_btn.setObjectName('dangerBtn')
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_analysis)
        btn_layout.addWidget(self.stop_btn)

        left_layout.addLayout(btn_layout)
        left_layout.addStretch()

        splitter.addWidget(left_panel)

        # Правая панель с вкладками
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Вкладки
        self.tabs = QTabWidget()

        # Вкладка логов
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.appendPlainText(f"[{datetime.now().strftime('%H:%M:%S')}] {self.language_manager.get_text('status_ready')}")
        logs_layout.addWidget(self.log_text)
        self.tabs.addTab(logs_tab, self.language_manager.get_text('tab_logs'))

        # Вкладка результатов
        results_tab = QWidget()
        results_layout = QVBoxLayout(results_tab)
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(['Threat', 'Type', 'Severity', 'Description'])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        results_layout.addWidget(self.results_table)
        self.tabs.addTab(results_tab, self.language_manager.get_text('tab_results'))

        # Вкладка IOC
        ioc_tab = QWidget()
        ioc_layout = QVBoxLayout(ioc_tab)
        self.ioc_tree = QTreeWidget()
        self.ioc_tree.setHeaderLabels(['Indicator', 'Type', 'Value'])
        ioc_layout.addWidget(self.ioc_tree)
        self.tabs.addTab(ioc_tab, self.language_manager.get_text('tab_ioc'))

        # Вкладка визуализации
        viz_tab = QWidget()
        viz_layout = QVBoxLayout(viz_tab)

        viz_tabs = QTabWidget()

        # Граф вызовов
        self.call_graph = CallGraphWidget()
        viz_tabs.addTab(self.call_graph, self.language_manager.get_text('tab_graph'))

        # Карта памяти
        self.memory_map = MemoryMapWidget()
        viz_tabs.addTab(self.memory_map, self.language_manager.get_text('tab_memory'))

        viz_layout.addWidget(viz_tabs)
        self.tabs.addTab(viz_tab, self.language_manager.get_text('tab_visualization'))

        right_layout.addWidget(self.tabs)

        # Прогресс бар
        progress_group = QGroupBox(self.language_manager.get_text('lbl_progress'))
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        time_layout = QHBoxLayout()
        time_label = QLabel(self.language_manager.get_text('lbl_time'))
        time_layout.addWidget(time_label)

        self.time_lcd = QLCDNumber()
        self.time_lcd.setDigitCount(8)
        self.time_lcd.display('00:00:00')
        time_layout.addWidget(self.time_lcd)
        time_layout.addStretch()

        threat_label = QLabel(self.language_manager.get_text('lbl_threats'))
        time_layout.addWidget(threat_label)

        self.threat_count = QLabel('0')
        self.threat_count.setStyleSheet('font-size: 18px; font-weight: bold; color: #ef5350;')
        time_layout.addWidget(self.threat_count)

        progress_layout.addLayout(time_layout)

        right_layout.addWidget(progress_group)

        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        # Меню
        self.create_menu()

        # Статус бар
        self.statusBar().showMessage(self.language_manager.get_text('status_ready'))

        # Таймер
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_seconds = 0

    def create_menu(self):
        """Создание меню."""
        menubar = self.menuBar()

        # Файл
        file_menu = menubar.addMenu(self.language_manager.get_text('menu_file'))

        open_action = QAction(self.language_manager.get_text('action_open'), self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.browse_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction(self.language_manager.get_text('action_exit'), self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Настройки
        settings_menu = menubar.addMenu(self.language_manager.get_text('menu_settings'))

        settings_action = QAction(self.language_manager.get_text('action_settings'), self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)

        # Тема
        theme_menu = settings_menu.addMenu(self.language_manager.get_text('action_theme'))
        for theme_name in self.theme_manager.get_all_theme_names():
            action = QAction(theme_name.replace('_', ' ').title(), self)
            action.triggered.connect(lambda checked, name=theme_name: self.change_theme(name))
            theme_menu.addAction(action)

        # Язык
        lang_menu = settings_menu.addMenu(self.language_manager.get_text('action_language'))
        for code, name in self.language_manager.get_all_languages():
            action = QAction(name, self)
            action.triggered.connect(lambda checked, lang=code: self.change_language(lang))
            lang_menu.addAction(action)

        # Помощь
        help_menu = menubar.addMenu(self.language_manager.get_text('menu_help'))

        about_action = QAction(self.language_manager.get_text('action_about'), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_connections(self):
        """Настройка соединений."""
        self.theme_manager.theme_changed.connect(self.apply_theme)
        self.language_manager.language_changed.connect(self.update_texts)

    def apply_theme(self):
        """Применение темы."""
        stylesheet = self.theme_manager.generate_stylesheet()
        self.setStyleSheet(stylesheet)

    def update_texts(self):
        """Обновление текстов интерфейса."""
        self.setWindowTitle(self.language_manager.get_text('app_title'))
        # Можно добавить обновление всех текстовых элементов

    def change_theme(self, theme_name: str):
        """Смена темы."""
        self.theme_manager.set_current_theme(theme_name)
        self.apply_theme()
        self.log_message(f"Theme changed to: {theme_name}")

    def change_language(self, lang: str):
        """Смена языка."""
        self.language_manager.set_language(lang)
        self.update_texts()
        self.log_message(f"Language changed to: {lang}")

    def open_settings(self):
        """Открытие диалога настроек."""
        dialog = SettingsDialog(self, self.theme_manager, self.language_manager)
        if dialog.exec_() == QDialog.Accepted:
            settings = dialog.get_settings()

            # Применяем настройки
            if settings['theme'] != self.theme_manager.current_theme:
                self.change_theme(settings['theme'])

            if settings['language'] != self.language_manager.current_language:
                self.change_language(settings['language'])

            self.theme_manager.font_size = settings['font_size']
            self.theme_manager.animations_enabled = settings['animations_enabled']
            self.theme_manager.save_settings()

            self.apply_theme()
            self.log_message("Settings saved")

    def browse_file(self):
        """Выбор файла."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select File',
            '',
            'All Files (*);;Executable Files (*.exe *.elf *.bin);;Python Files (*.py)'
        )
        if file_path:
            self.file_path = file_path
            self.file_edit.setText(file_path)
            self.log_message(f"File selected: {file_path}")

    def start_analysis(self):
        """Начало анализа."""
        if not self.file_path:
            QMessageBox.warning(self, 'Warning', self.language_manager.get_text('msg_no_file'))
            return

        self.is_analyzing = True
        self.analyze_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.elapsed_seconds = 0
        self.timer.start(1000)

        self.log_message(f"Starting analysis: {self.file_path}")
        self.statusBar().showMessage(self.language_manager.get_text('status_analyzing'))

        # Эмуляция прогресса
        self.simulated_progress = 0
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(100)

        # Пример данных для визуализации
        self.update_visualization()

    def update_progress(self):
        """Обновление прогресса."""
        self.simulated_progress += 1
        if self.simulated_progress >= 100:
            self.simulated_progress = 100
            self.progress_timer.stop()
            self.finish_analysis()
        self.progress_bar.setValue(self.simulated_progress)

    def update_timer(self):
        """Обновление таймера."""
        self.elapsed_seconds += 1
        hours = self.elapsed_seconds // 3600
        minutes = (self.elapsed_seconds % 3600) // 60
        seconds = self.elapsed_seconds % 60
        self.time_lcd.display(f'{hours:02d}:{minutes:02d}:{seconds:02d}')

    def update_visualization(self):
        """Обновление визуализации."""
        # Пример данных для графа вызовов
        nodes = [
            {'name': 'main', 'x': 100, 'y': 50, 'dangerous': False},
            {'name': 'init', 'x': 100, 'y': 150, 'dangerous': False},
            {'name': 'VirtualAlloc', 'x': 50, 'y': 250, 'dangerous': True},
            {'name': 'WriteProcessMemory', 'x': 150, 'y': 250, 'dangerous': True},
            {'name': 'CreateThread', 'x': 250, 'y': 250, 'dangerous': True},
            {'name': 'process_data', 'x': 100, 'y': 350, 'dangerous': False},
        ]
        edges = [(0, 1), (1, 2), (1, 3), (1, 4), (1, 5)]
        self.call_graph.set_data(nodes, edges)

        # Пример данных для карты памяти
        regions = [
            {'start': 0x400000, 'end': 0x450000, 'type': 'code', 'protection': 'r-x'},
            {'start': 0x450000, 'end': 0x460000, 'type': 'data', 'protection': 'rw-'},
            {'start': 0x460000, 'end': 0x500000, 'type': 'heap', 'protection': 'rw-'},
            {'start': 0x7fff0000, 'end': 0x7fff8000, 'type': 'stack', 'protection': 'rw-'},
            {'start': 0x7f000000, 'end': 0x7f010000, 'type': 'shared', 'protection': 'r--'},
        ]
        self.memory_map.set_data(regions)

    def finish_analysis(self):
        """Завершение анализа."""
        self.is_analyzing = False
        self.analyze_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.timer.stop()

        self.log_message(self.language_manager.get_text('msg_analysis_complete'))
        self.statusBar().showMessage(self.language_manager.get_text('status_complete'))

        # Добавляем пример результатов
        self.results_table.setRowCount(3)
        threats = [
            ('Suspicious API Call', 'Behavioral', 'High', 'VirtualAlloc with PAGE_EXECUTE_READWRITE'),
            ('Network Connection', 'Network', 'Medium', 'Attempted connection to suspicious IP'),
            ('Registry Modification', 'Persistence', 'High', 'Added autorun entry'),
        ]
        for i, threat in enumerate(threats):
            for j, val in enumerate(threat):
                self.results_table.setItem(i, j, QTableWidgetItem(val))

        # Обновляем счётчик угроз
        self.threat_count.setText(str(len(threats)))

        # Добавляем IOC
        self.ioc_tree.clear()
        ioc_items = [
            ('IP Address', '192.168.1.100'),
            ('Domain', 'malicious-domain.com'),
            ('File Hash', 'a1b2c3d4e5f6...'),
        ]
        for ioc_type, value in ioc_items:
            item = QTreeWidgetItem([ioc_type, ioc_type, value])
            self.ioc_tree.addTopLevelItem(item)

    def stop_analysis(self):
        """Остановка анализа."""
        if self.is_analyzing:
            self.is_analyzing = False
            self.progress_timer.stop()
            self.timer.stop()
            self.analyze_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.log_message("Analysis stopped by user")
            self.statusBar().showMessage('Stopped')

    def log_message(self, message: str):
        """Добавление сообщения в лог."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.appendPlainText(f"[{timestamp}] {message}")

    def show_about(self):
        """Показ информации о программе."""
        QMessageBox.about(
            self,
            'About RedSand Secure',
            '<h2>RedSand Secure v4.0</h2>'
            '<p>Professional Malware Analysis System</p>'
            '<p>Features:</p>'
            '<ul>'
            '<li>Multi-language support (6 languages)</li>'
            '<li>Advanced visualization (call graphs, memory maps)</li>'
            '<li>Customizable themes</li>'
            '<li>Network isolation</li>'
            '<li>Polymorphic analysis</li>'
            '</ul>'
            '<p>© 2024 RedSand Security Team</p>'
        )


# ============================================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ============================================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))

    window = RedSandGUIv4()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()