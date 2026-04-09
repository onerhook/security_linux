#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Antivirus GUI v7.0 - Modern Professional Interface
Современный антивирусный сканер с реальной логикой обнаружения угроз
Запускать ТОЛЬКО в изолированной виртуальной машине!
"""

import sys
import os
import hashlib
import json
import re
import magic
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from threading import Thread, Lock
import configparser

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QTextEdit, QFileDialog, QGroupBox, QGridLayout,
    QSplitter, QTabWidget, QFrame, QScrollArea, QMessageBox, QCheckBox,
    QSpinBox, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QStatusBar,
    QToolBar, QAction, QMenu, QMenuBar, QTreeWidget, QTreeWidgetItem,
    QListWidget, QListWidgetItem, QSlider, QColorDialog, QFontDialog,
    QRadioButton, QButtonGroup, QDoubleSpinBox, QPlainTextEdit,
    QStackedWidget, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect,
    QSystemTrayIcon, QStyleFactory, QCompleter, QDateEdit, QTimeEdit,
    QCalendarWidget, QLCDNumber, QDial, QTreeView, QColumnView, QTableView,
    QAbstractItemView, QActionGroup, QToolButton, QDockWidget, QWizard,
    QWizardPage, QKeySequenceEdit, QShortcut
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QObject, QThread, QMetaObject, Q_ARG,
    QPropertyAnimation, QEasingCurve, QSize, QUrl, QSettings, QMimeData,
    QPoint, QRect, QVariant, QMargins, QParallelAnimationGroup,
    QSequentialAnimationGroup, pyqtProperty, QStateMachine, QState,
    QSignalTransition, QEventTransition, QFile, QTextStream, QIODevice,
    QFileInfo, QDir, QStandardPaths, QDateTime, QLocale, QMutex,
    QWaitCondition, QTranslator, QLibraryInfo, QCoreApplication,
    QMimeDatabase, QStorageInfo, QTimeZone, QXmlStreamReader,
    QJsonDocument, QJsonObject, QJsonValue, QJsonArray,
    QRegularExpression, QRegularExpressionMatch,
    QElapsedTimer, QBuffer, QDataStream, QBinaryIO
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QIcon, QPixmap, QPainter, QBrush, QPen,
    QLinearGradient, QRadialGradient, QConicalGradient, QTextCursor,
    QTextDocument, QGradient, QFontDatabase, QSyntaxHighlighter,
    QTextCharFormat, QKeySequence, QImage, QTransform, QPolygon,
    QPolygonF, QFontMetrics, QFontInfo, QGuiApplication, QScreen,
    QClipboard, QDrag, QEnterEvent, QPaintDevice, QPaintEngine,
    QTextOption, QTextBlock, QTextFragment, QCursor, QMovie, QBitmap,
    QMaskGenerator, QRasterWindowSurface, QSurfaceFormat, QOpenGLContext,
    QOffscreenSurface, QWindow, QBackingStore, QExposeEvent, QHideEvent,
    QMoveEvent, QResizeEvent, QShowEvent, QCloseEvent, QFocusEvent,
    QKeyEvent, QMouseEvent, QWheelEvent, QHoverEvent, QTabletEvent,
    QTouchEvent, QGestureEvent, QNativeGestureEvent, QInputEvent,
    QInputMethodEvent, QAccessibleEvent, QAccessibleStateChangeEvent,
    QAccessibleTextCursorEvent, QAccessibleTextInsertEvent,
    QAccessibleTextRemoveEvent, QAccessibleTextSelectionEvent,
    QAccessibleTextUpdateEvent, QAccessibleValueChangeEvent,
    QActionEvent, QContextMenuEvent, QDragEnterEvent, QDragLeaveEvent,
    QDragMoveEvent, QDropEvent, QHelpEvent, QStatusTipEvent,
    QWhatsThisClickedEvent, QToolBarChangeEvent, QDynamicPropertyChangeEvent,
    QFileSystemWatcher, QCollator, QCollationKey, QCommandLineParser,
    QCommandLineOption, QCoreApplication, QEvent, QEventLoop,
    QIdentityProxyModel, QItemSelection, QItemSelectionModel,
    QItemSelectionRange, QMimeType, QOperatingSystemVersion,
    QPauseAnimation, QPluginLoader, QProcess, QProcessEnvironment,
    QPropertyAnimation, QRandomGenerator, QReadLocker, QReadWriteLock,
    QResource, QRunnable, QSaveFile, QSemaphore, QSequentialAnimationGroup,
    QSettings, QSharedMemory, QSignalBlocker, QSignalMapper, QSocketNotifier,
    QStandardPaths, QStorageInfo, QSysInfo, QSystemSemaphore, QTemporaryDir,
    QTemporaryFile, QTextBoundaryFinder, QTextCodec, QTextDecoder,
    QTextEncoder, QThread, QThreadPool, QTime, QTimeLine, QTimeZone,
    QTranslator, QUrlQuery, QUuid, QVarLengthArray, QVersionNumber,
    QWriteLocker, QXmlAttributes, QXmlDefaultHandler, QXmlDTDHandler,
    QXmlEntityResolver, QXmlErrorHandler, QXmlInputSource, QXmlLexicalHandler,
    QXmlLocator, QXmlNamespaceSupport, QXmlParseException,
    QXmlReader, QXmlSimpleReader
)

# ============================================================================
# МЕНЕДЖЕР ЯЗЫКОВ
# ============================================================================

class LanguageManager(QObject):
    """Менеджер локализации приложения."""
    
    language_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_language = 'ru'
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Загрузка переводов."""
        return {
            'ru': {
                'app_title': 'RedSand Antivirus v7.0',
                'menu_file': 'Файл',
                'menu_settings': 'Настройки',
                'menu_view': 'Вид',
                'menu_help': 'Помощь',
                'action_open': 'Открыть файл...',
                'action_scan_folder': 'Сканировать папку...',
                'action_exit': 'Выход',
                'action_settings': 'Настройки...',
                'action_theme': 'Тема',
                'action_language': 'Язык',
                'action_about': 'О программе',
                'btn_scan': 'СКАНИРОВАТЬ',
                'btn_stop': 'СТОП',
                'btn_browse': 'Обзор',
                'btn_export': 'Экспорт отчёта',
                'btn_clear': 'Очистить',
                'lbl_file': 'Файл для проверки:',
                'lbl_status': 'Статус:',
                'lbl_progress': 'Прогресс сканирования:',
                'lbl_time': 'Время:',
                'lbl_threats': 'Угроз найдено:',
                'lbl_verdict': 'Вердикт:',
                'tab_logs': 'Журнал событий',
                'tab_results': 'Результаты',
                'tab_ioc': 'Индикаторы компрометации',
                'tab_visualization': 'Визуализация',
                'tab_graph': 'Граф вызовов',
                'tab_memory': 'Карта памяти',
                'tab_strings': 'Подозрительные строки',
                'status_ready': 'Готов к сканированию',
                'status_scanning': 'Сканирование...',
                'status_complete': 'Сканирование завершено',
                'msg_no_file': 'Файл не выбран',
                'msg_scan_complete': 'Сканирование завершено',
                'msg_clean': 'Файл чист',
                'msg_infected': 'Обнаружены угрозы!',
                'settings_title': 'Настройки RedSand',
                'settings_general': 'Общие',
                'settings_security': 'Безопасность',
                'settings_appearance': 'Внешний вид',
                'chk_deep_scan': 'Глубокий анализ',
                'chk_heuristic': 'Эвристический анализ',
                'chk_sandbox': 'Режим песочницы',
                'chk_auto_delete': 'Автоудаление угроз',
                'chk_unpack_archives': 'Распаковка архивов',
                'chk_check_signatures': 'Проверка цифровых подписей',
                'chk_cloud_analysis': 'Облачный анализ',
                'lbl_sensitivity': 'Чувствительность:',
                'lbl_threads': 'Потоков сканирования:',
                'lbl_font_size': 'Размер шрифта:',
                'lbl_animation': 'Анимация:',
                'chk_enable_animations': 'Включить анимации',
                'lbl_theme': 'Тема:',
                'lbl_language': 'Язык интерфейса:',
                'btn_save': 'Сохранить',
                'btn_cancel': 'Отмена',
                'verdict_clean': 'ЧИСТЫЙ',
                'verdict_suspicious': 'ПОДОЗРИТЕЛЬНЫЙ',
                'verdict_malicious': 'ВРЕДОНОСНЫЙ',
                'severity_low': 'Низкий',
                'severity_medium': 'Средний',
                'severity_high': 'Высокий',
                'severity_critical': 'Критический',
                'lang_ru': 'Русский',
                'lang_en': 'English',
                'lang_cn': '中文',
                'lang_es': 'Español',
                'lang_de': 'Deutsch',
                'lang_fr': 'Français',
            },
            'en': {
                'app_title': 'RedSand Antivirus v7.0',
                'menu_file': 'File',
                'menu_settings': 'Settings',
                'menu_view': 'View',
                'menu_help': 'Help',
                'action_open': 'Open File...',
                'action_scan_folder': 'Scan Folder...',
                'action_exit': 'Exit',
                'action_settings': 'Settings...',
                'action_theme': 'Theme',
                'action_language': 'Language',
                'action_about': 'About',
                'btn_scan': 'SCAN NOW',
                'btn_stop': 'STOP',
                'btn_browse': 'Browse',
                'btn_export': 'Export Report',
                'btn_clear': 'Clear',
                'lbl_file': 'File to scan:',
                'lbl_status': 'Status:',
                'lbl_progress': 'Scan Progress:',
                'lbl_time': 'Time:',
                'lbl_threats': 'Threats Found:',
                'lbl_verdict': 'Verdict:',
                'tab_logs': 'Event Log',
                'tab_results': 'Results',
                'tab_ioc': 'Indicators of Compromise',
                'tab_visualization': 'Visualization',
                'tab_graph': 'Call Graph',
                'tab_memory': 'Memory Map',
                'tab_strings': 'Suspicious Strings',
                'status_ready': 'Ready to scan',
                'status_scanning': 'Scanning...',
                'status_complete': 'Scan Complete',
                'msg_no_file': 'No file selected',
                'msg_scan_complete': 'Scan completed',
                'msg_clean': 'File is clean',
                'msg_infected': 'Threats detected!',
                'settings_title': 'RedSand Settings',
                'settings_general': 'General',
                'settings_security': 'Security',
                'settings_appearance': 'Appearance',
                'chk_deep_scan': 'Deep Scan',
                'chk_heuristic': 'Heuristic Analysis',
                'chk_sandbox': 'Sandbox Mode',
                'chk_auto_delete': 'Auto-delete Threats',
                'chk_unpack_archives': 'Unpack Archives',
                'chk_check_signatures': 'Check Digital Signatures',
                'chk_cloud_analysis': 'Cloud Analysis',
                'lbl_sensitivity': 'Sensitivity:',
                'lbl_threads': 'Scan Threads:',
                'lbl_font_size': 'Font Size:',
                'lbl_animation': 'Animation:',
                'chk_enable_animations': 'Enable Animations',
                'lbl_theme': 'Theme:',
                'lbl_language': 'Interface Language:',
                'btn_save': 'Save',
                'btn_cancel': 'Cancel',
                'verdict_clean': 'CLEAN',
                'verdict_suspicious': 'SUSPICIOUS',
                'verdict_malicious': 'MALICIOUS',
                'severity_low': 'Low',
                'severity_medium': 'Medium',
                'severity_high': 'High',
                'severity_critical': 'Critical',
                'lang_ru': 'Русский',
                'lang_en': 'English',
                'lang_cn': '中文',
                'lang_es': 'Español',
                'lang_de': 'Deutsch',
                'lang_fr': 'Français',
            },
            'cn': {
                'app_title': 'RedSand 杀毒软件 v7.0',
                'menu_file': '文件',
                'menu_settings': '设置',
                'menu_view': '视图',
                'menu_help': '帮助',
                'action_open': '打开文件...',
                'action_scan_folder': '扫描文件夹...',
                'action_exit': '退出',
                'action_settings': '设置...',
                'action_theme': '主题',
                'action_language': '语言',
                'action_about': '关于',
                'btn_scan': '立即扫描',
                'btn_stop': '停止',
                'btn_browse': '浏览',
                'btn_export': '导出报告',
                'btn_clear': '清除',
                'lbl_file': '要扫描的文件:',
                'lbl_status': '状态:',
                'lbl_progress': '扫描进度:',
                'lbl_time': '时间:',
                'lbl_threats': '发现威胁:',
                'lbl_verdict': '结论:',
                'tab_logs': '事件日志',
                'tab_results': '结果',
                'tab_ioc': '入侵指标',
                'tab_visualization': '可视化',
                'tab_graph': '调用图',
                'tab_memory': '内存映射',
                'tab_strings': '可疑字符串',
                'status_ready': '准备扫描',
                'status_scanning': '扫描中...',
                'status_complete': '扫描完成',
                'msg_no_file': '未选择文件',
                'msg_scan_complete': '扫描完成',
                'msg_clean': '文件干净',
                'msg_infected': '发现威胁!',
                'settings_title': 'RedSand 设置',
                'settings_general': '常规',
                'settings_security': '安全',
                'settings_appearance': '外观',
                'chk_deep_scan': '深度扫描',
                'chk_heuristic': '启发式分析',
                'chk_sandbox': '沙盒模式',
                'chk_auto_delete': '自动删除威胁',
                'chk_unpack_archives': '解压档案',
                'chk_check_signatures': '检查数字签名',
                'chk_cloud_analysis': '云分析',
                'lbl_sensitivity': '灵敏度:',
                'lbl_threads': '扫描线程:',
                'lbl_font_size': '字体大小:',
                'lbl_animation': '动画:',
                'chk_enable_animations': '启用动画',
                'lbl_theme': '主题:',
                'lbl_language': '界面语言:',
                'btn_save': '保存',
                'btn_cancel': '取消',
                'verdict_clean': '干净',
                'verdict_suspicious': '可疑',
                'verdict_malicious': '恶意',
                'severity_low': '低',
                'severity_medium': '中',
                'severity_high': '高',
                'severity_critical': '严重',
                'lang_ru': 'Русский',
                'lang_en': 'English',
                'lang_cn': '中文',
                'lang_es': 'Español',
                'lang_de': 'Deutsch',
                'lang_fr': 'Français',
            },
            'es': {
                'app_title': 'RedSand Antivirus v7.0',
                'menu_file': 'Archivo',
                'menu_settings': 'Configuración',
                'menu_view': 'Vista',
                'menu_help': 'Ayuda',
                'action_open': 'Abrir archivo...',
                'action_scan_folder': 'Escanear carpeta...',
                'action_exit': 'Salir',
                'action_settings': 'Configuración...',
                'action_theme': 'Tema',
                'action_language': 'Idioma',
                'action_about': 'Acerca de',
                'btn_scan': 'ESCANEAR AHORA',
                'btn_stop': 'DETENER',
                'btn_browse': 'Examinar',
                'btn_export': 'Exportar informe',
                'btn_clear': 'Limpiar',
                'lbl_file': 'Archivo a escanear:',
                'lbl_status': 'Estado:',
                'lbl_progress': 'Progreso del escaneo:',
                'lbl_time': 'Tiempo:',
                'lbl_threats': 'Amenazas encontradas:',
                'lbl_verdict': 'Veredicto:',
                'tab_logs': 'Registro de eventos',
                'tab_results': 'Resultados',
                'tab_ioc': 'Indicadores de compromiso',
                'tab_visualization': 'Visualización',
                'tab_graph': 'Gráfico de llamadas',
                'tab_memory': 'Mapa de memoria',
                'tab_strings': 'Cadenas sospechosas',
                'status_ready': 'Listo para escanear',
                'status_scanning': 'Escaneando...',
                'status_complete': 'Escaneo completado',
                'msg_no_file': 'Ningún archivo seleccionado',
                'msg_scan_complete': 'Escaneo completado',
                'msg_clean': 'Archivo limpio',
                'msg_infected': '¡Amenazas detectadas!',
                'settings_title': 'Configuración de RedSand',
                'settings_general': 'General',
                'settings_security': 'Seguridad',
                'settings_appearance': 'Apariencia',
                'chk_deep_scan': 'Escaneo profundo',
                'chk_heuristic': 'Análisis heurístico',
                'chk_sandbox': 'Modo sandbox',
                'chk_auto_delete': 'Eliminación automática',
                'chk_unpack_archives': 'Descomprimir archivos',
                'chk_check_signatures': 'Verificar firmas digitales',
                'chk_cloud_analysis': 'Análisis en la nube',
                'lbl_sensitivity': 'Sensibilidad:',
                'lbl_threads': 'Hilos de escaneo:',
                'lbl_font_size': 'Tamaño de fuente:',
                'lbl_animation': 'Animación:',
                'chk_enable_animations': 'Habilitar animaciones',
                'lbl_theme': 'Tema:',
                'lbl_language': 'Idioma de interfaz:',
                'btn_save': 'Guardar',
                'btn_cancel': 'Cancelar',
                'verdict_clean': 'LIMPIO',
                'verdict_suspicious': 'SOSPECHOSO',
                'verdict_malicious': 'MALICIOSO',
                'severity_low': 'Bajo',
                'severity_medium': 'Medio',
                'severity_high': 'Alto',
                'severity_critical': 'Crítico',
                'lang_ru': 'Русский',
                'lang_en': 'English',
                'lang_cn': '中文',
                'lang_es': 'Español',
                'lang_de': 'Deutsch',
                'lang_fr': 'Français',
            },
            'de': {
                'app_title': 'RedSand Antivirus v7.0',
                'menu_file': 'Datei',
                'menu_settings': 'Einstellungen',
                'menu_view': 'Ansicht',
                'menu_help': 'Hilfe',
                'action_open': 'Datei öffnen...',
                'action_scan_folder': 'Ordner scannen...',
                'action_exit': 'Beenden',
                'action_settings': 'Einstellungen...',
                'action_theme': 'Design',
                'action_language': 'Sprache',
                'action_about': 'Über',
                'btn_scan': 'JETZT SCANNEN',
                'btn_stop': 'STOPP',
                'btn_browse': 'Durchsuchen',
                'btn_export': 'Bericht exportieren',
                'btn_clear': 'Löschen',
                'lbl_file': 'Zu scannende Datei:',
                'lbl_status': 'Status:',
                'lbl_progress': 'Scan-Fortschritt:',
                'lbl_time': 'Zeit:',
                'lbl_threats': 'Gefundene Bedrohungen:',
                'lbl_verdict': 'Urteil:',
                'tab_logs': 'Ereignisprotokoll',
                'tab_results': 'Ergebnisse',
                'tab_ioc': 'Kompromittierungsindikatoren',
                'tab_visualization': 'Visualisierung',
                'tab_graph': 'Aufrufdiagramm',
                'tab_memory': 'Speicherkarte',
                'tab_strings': 'Verdächtige Zeichenfolgen',
                'status_ready': 'Bereit zum Scannen',
                'status_scanning': 'Scannen...',
                'status_complete': 'Scan abgeschlossen',
                'msg_no_file': 'Keine Datei ausgewählt',
                'msg_scan_complete': 'Scan abgeschlossen',
                'msg_clean': 'Datei ist sauber',
                'msg_infected': 'Bedrohungen erkannt!',
                'settings_title': 'RedSand Einstellungen',
                'settings_general': 'Allgemein',
                'settings_security': 'Sicherheit',
                'settings_appearance': 'Aussehen',
                'chk_deep_scan': 'Tiefenanalyse',
                'chk_heuristic': 'Heuristische Analyse',
                'chk_sandbox': 'Sandbox-Modus',
                'chk_auto_delete': 'Automatisches Löschen',
                'chk_unpack_archives': 'Archive entpacken',
                'chk_check_signatures': 'Digitale Signaturen prüfen',
                'chk_cloud_analysis': 'Cloud-Analyse',
                'lbl_sensitivity': 'Empfindlichkeit:',
                'lbl_threads': 'Scan-Threads:',
                'lbl_font_size': 'Schriftgröße:',
                'lbl_animation': 'Animation:',
                'chk_enable_animations': 'Animationen aktivieren',
                'lbl_theme': 'Design:',
                'lbl_language': 'Oberflächensprache:',
                'btn_save': 'Speichern',
                'btn_cancel': 'Abbrechen',
                'verdict_clean': 'SAUBER',
                'verdict_suspicious': 'VERDÄCHTIG',
                'verdict_malicious': 'SCHÄDLICH',
                'severity_low': 'Niedrig',
                'severity_medium': 'Mittel',
                'severity_high': 'Hoch',
                'severity_critical': 'Kritisch',
                'lang_ru': 'Русский',
                'lang_en': 'English',
                'lang_cn': '中文',
                'lang_es': 'Español',
                'lang_de': 'Deutsch',
                'lang_fr': 'Français',
            },
            'fr': {
                'app_title': 'RedSand Antivirus v7.0',
                'menu_file': 'Fichier',
                'menu_settings': 'Paramètres',
                'menu_view': 'Affichage',
                'menu_help': 'Aide',
                'action_open': 'Ouvrir un fichier...',
                'action_scan_folder': 'Scanner un dossier...',
                'action_exit': 'Quitter',
                'action_settings': 'Paramètres...',
                'action_theme': 'Thème',
                'action_language': 'Langue',
                'action_about': 'À propos',
                'btn_scan': 'SCANNER MAINTENANT',
                'btn_stop': 'ARRÊTER',
                'btn_browse': 'Parcourir',
                'btn_export': 'Exporter le rapport',
                'btn_clear': 'Effacer',
                'lbl_file': 'Fichier à scanner:',
                'lbl_status': 'Statut:',
                'lbl_progress': 'Progression du scan:',
                'lbl_time': 'Temps:',
                'lbl_threats': 'Menaces trouvées:',
                'lbl_verdict': 'Verdict:',
                'tab_logs': 'Journal des événements',
                'tab_results': 'Résultats',
                'tab_ioc': 'Indicateurs de compromission',
                'tab_visualization': 'Visualisation',
                'tab_graph': 'Graphe d\'appel',
                'tab_memory': 'Carte mémoire',
                'tab_strings': 'Chaînes suspectes',
                'status_ready': 'Prêt à scanner',
                'status_scanning': 'Analyse en cours...',
                'status_complete': 'Analyse terminée',
                'msg_no_file': 'Aucun fichier sélectionné',
                'msg_scan_complete': 'Analyse terminée',
                'msg_clean': 'Fichier propre',
                'msg_infected': 'Menaces détectées!',
                'settings_title': 'Paramètres RedSand',
                'settings_general': 'Général',
                'settings_security': 'Sécurité',
                'settings_appearance': 'Apparence',
                'chk_deep_scan': 'Analyse approfondie',
                'chk_heuristic': 'Analyse heuristique',
                'chk_sandbox': 'Mode bac à sable',
                'chk_auto_delete': 'Suppression automatique',
                'chk_unpack_archives': 'Décompresser les archives',
                'chk_check_signatures': 'Vérifier les signatures numériques',
                'chk_cloud_analysis': 'Analyse cloud',
                'lbl_sensitivity': 'Sensibilité:',
                'lbl_threads': 'Threads de scan:',
                'lbl_font_size': 'Taille de police:',
                'lbl_animation': 'Animation:',
                'chk_enable_animations': 'Activer les animations',
                'lbl_theme': 'Thème:',
                'lbl_language': 'Langue de l\'interface:',
                'btn_save': 'Enregistrer',
                'btn_cancel': 'Annuler',
                'verdict_clean': 'PROPRE',
                'verdict_suspicious': 'SUSPECT',
                'verdict_malicious': 'MALVEILLANT',
                'severity_low': 'Faible',
                'severity_medium': 'Moyen',
                'severity_high': 'Élevé',
                'severity_critical': 'Critique',
                'lang_ru': 'Русский',
                'lang_en': 'English',
                'lang_cn': '中文',
                'lang_es': 'Español',
                'lang_de': 'Deutsch',
                'lang_fr': 'Français',
            },
        }
    
    def get_text(self, key: str) -> str:
        """Получение текста для текущего языка."""
        return self.translations.get(self.current_language, {}).get(key, key)
    
    def set_language(self, lang: str):
        """Установка языка."""
        if lang in self.translations:
            self.current_language = lang
            self.language_changed.emit(lang)
    
    def get_all_languages(self) -> List[Tuple[str, str]]:
        """Получение всех доступных языков."""
        return [
            ('ru', self.translations['ru']['lang_ru']),
            ('en', self.translations['ru']['lang_en']),
            ('cn', self.translations['ru']['lang_cn']),
            ('es', self.translations['ru']['lang_es']),
            ('de', self.translations['ru']['lang_de']),
            ('fr', self.translations['ru']['lang_fr']),
        ]


# ============================================================================
# МЕНЕДЖЕР ТЕМ
# ============================================================================

class ThemeManager(QObject):
    """Менеджер тем оформления."""
    
    theme_changed = pyqtSignal()
    
    THEMES = {
        'dark_modern': {
            'primary_bg': '#0f0f1a',
            'secondary_bg': '#1a1a2e',
            'tertiary_bg': '#252542',
            'accent_color': '#00d9ff',
            'accent_hover': '#00b8d9',
            'danger_color': '#ff4757',
            'warning_color': '#ffa502',
            'success_color': '#2ed573',
            'text_primary': '#ffffff',
            'text_secondary': '#a0a0a0',
            'border_color': '#3d3d5c',
            'hover_color': '#00d9ff33',
            'gradient_start': '#00d9ff',
            'gradient_end': '#0099cc',
        },
        'cyberpunk': {
            'primary_bg': '#0a0a12',
            'secondary_bg': '#16162a',
            'tertiary_bg': '#2a2a4a',
            'accent_color': '#ff00ff',
            'accent_hover': '#cc00cc',
            'danger_color': '#ff0055',
            'warning_color': '#ffaa00',
            'success_color': '#00ff88',
            'text_primary': '#ffffff',
            'text_secondary': '#bbbbbb',
            'border_color': '#4a4a6a',
            'hover_color': '#ff00ff33',
            'gradient_start': '#ff00ff',
            'gradient_end': '#00ffff',
        },
        'matrix': {
            'primary_bg': '#001100',
            'secondary_bg': '#002200',
            'tertiary_bg': '#003300',
            'accent_color': '#00ff00',
            'accent_hover': '#00cc00',
            'danger_color': '#ff3333',
            'warning_color': '#ffff00',
            'success_color': '#00ff00',
            'text_primary': '#00ff00',
            'text_secondary': '#00aa00',
            'border_color': '#004400',
            'hover_color': '#00ff0033',
            'gradient_start': '#00ff00',
            'gradient_end': '#008800',
        },
        'light_professional': {
            'primary_bg': '#f5f5f5',
            'secondary_bg': '#ffffff',
            'tertiary_bg': '#e8e8e8',
            'accent_color': '#2196f3',
            'accent_hover': '#1976d2',
            'danger_color': '#f44336',
            'warning_color': '#ff9800',
            'success_color': '#4caf50',
            'text_primary': '#212121',
            'text_secondary': '#757575',
            'border_color': '#bdbdbd',
            'hover_color': '#2196f333',
            'gradient_start': '#2196f3',
            'gradient_end': '#1976d2',
        },
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = 'dark_modern'
        self.font_size = 10
        self.animations_enabled = True
    
    def get_theme(self, theme_name: str) -> dict:
        """Получение темы по имени."""
        return self.THEMES.get(theme_name, self.THEMES['dark_modern'])
    
    def set_current_theme(self, theme_name: str):
        """Установка текущей темы."""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            self.theme_changed.emit()
    
    def get_all_theme_names(self) -> List[str]:
        """Получение всех имён тем."""
        return list(self.THEMES.keys())
    
    def generate_stylesheet(self) -> str:
        """Генерация таблицы стилей."""
        theme = self.get_theme(self.current_theme)
        fs = self.font_size
        
        return f"""
/* Основные стили */
QMainWindow {{
    background-color: {theme['primary_bg']};
}}

QWidget {{
    background-color: transparent;
    color: {theme['text_primary']};
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    font-size: {fs}px;
}}

/* Заголовки */
QLabel#titleLabel {{
    font-size: {fs + 8}px;
    font-weight: 700;
    color: {theme['accent_color']};
    padding: 15px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {theme['gradient_start']},
                                stop:1 {theme['gradient_end']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

/* Кнопки */
QPushButton {{
    background-color: {theme['tertiary_bg']};
    color: {theme['text_primary']};
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: {fs}px;
}}

QPushButton:hover {{
    background-color: {theme['accent_color']};
    color: {theme['primary_bg']};
}}

QPushButton:pressed {{
    background-color: {theme['accent_hover']};
}}

QPushButton:disabled {{
    background-color: {theme['border_color']};
    color: {theme['text_secondary']};
}}

QPushButton#primaryBtn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {theme['gradient_start']},
                                stop:1 {theme['gradient_end']});
    color: {theme['primary_bg']};
    font-size: {fs + 2}px;
    padding: 15px 40px;
}}

QPushButton#primaryBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {theme['accent_hover']},
                                stop:1 {theme['gradient_end']});
}}

QPushButton#dangerBtn {{
    background-color: {theme['danger_color']};
    color: white;
}}

QPushButton#dangerBtn:hover {{
    background-color: #ff6b7a;
}}

/* Прогресс бар */
QProgressBar {{
    background-color: {theme['tertiary_bg']};
    border: none;
    border-radius: 8px;
    height: 20px;
    text-align: center;
    color: {theme['text_primary']};
    font-weight: 600;
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
    padding: 12px;
    font-family: 'Consolas', 'Courier New', 'DejaVu Sans Mono', monospace;
    font-size: {fs - 1}px;
    selection-background-color: {theme['accent_color']};
    selection-color: {theme['primary_bg']};
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
    padding: 10px;
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
    padding: 12px;
    border: none;
    font-weight: 700;
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
    padding: 12px 24px;
    margin-right: 3px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    background-color: {theme['accent_color']};
    font-weight: 700;
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
    padding: 10px;
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
    padding: 10px 15px;
    min-width: 150px;
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
    spacing: 10px;
    font-size: {fs}px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 5px;
    border: 2px solid {theme['border_color']};
    background-color: {theme['secondary_bg']};
}}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {theme['accent_color']};
    border: 2px solid {theme['accent_color']};
}}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
    border: 2px solid {theme['accent_color']};
}}

/* Спинбоксы */
QSpinBox, QDoubleSpinBox {{
    background-color: {theme['tertiary_bg']};
    color: {theme['text_primary']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    padding: 10px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {theme['accent_color']};
}}

/* Слайдеры */
QSlider::groove:horizontal {{
    border: 1px solid {theme['border_color']};
    height: 10px;
    background: {theme['tertiary_bg']};
    border-radius: 5px;
}}

QSlider::handle:horizontal {{
    background: {theme['accent_color']};
    border: none;
    width: 20px;
    margin: -5px 0;
    border-radius: 10px;
}}

QSlider::handle:horizontal:hover {{
    background: {theme['accent_hover']};
}}

/* Меню */
QMenuBar {{
    background-color: {theme['secondary_bg']};
    color: {theme['text_primary']};
    border-bottom: 2px solid {theme['border_color']};
    padding: 8px;
}}

QMenuBar::item {{
    padding: 10px 20px;
    border-radius: 5px;
}}

QMenuBar::item:selected {{
    background-color: {theme['hover_color']};
}}

QMenu {{
    background-color: {theme['secondary_bg']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
}}

QMenu::item {{
    padding: 10px 30px;
    color: {theme['text_primary']};
}}

QMenu::item:selected {{
    background-color: {theme['accent_color']};
    color: {theme['primary_bg']};
}}

/* Группы */
QGroupBox {{
    background-color: {theme['secondary_bg']};
    border: 2px solid {theme['border_color']};
    border-radius: 12px;
    margin-top: 15px;
    padding-top: 15px;
    font-weight: 600;
    color: {theme['accent_color']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 10px;
    color: {theme['accent_color']};
}}

/* Статус бар */
QStatusBar {{
    background-color: {theme['tertiary_bg']};
    color: {theme['text_secondary']};
    border-top: 2px solid {theme['border_color']};
}}

/* Разделитель */
QSplitter::handle {{
    background-color: {theme['border_color']};
    width: 5px;
}}

QSplitter::handle:hover {{
    background-color: {theme['accent_color']};
}}

/* LCD дисплей */
QLCDNumber {{
    background-color: {theme['tertiary_bg']};
    color: {theme['accent_color']};
    border: 2px solid {theme['border_color']};
    border-radius: 8px;
    padding: 5px;
}}

/* Полоса прокрутки */
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
    background-color: {theme['accent_color']};
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
    background-color: {theme['accent_color']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
"""


# ============================================================================
# АНАЛИЗАТОР УГРОЗ (РЕАЛЬНАЯ ЛОГИКА)
# ============================================================================

class ThreatAnalyzer:
    """Реальный анализатор угроз с эвристическим поиском."""
    
    # Опасные API функции Windows
    DANGEROUS_APIS = {
        'VirtualAlloc': 'Выделение исполняемой памяти',
        'VirtualProtect': 'Изменение прав доступа к памяти',
        'WriteProcessMemory': 'Запись в память другого процесса',
        'CreateRemoteThread': 'Создание потока в другом процессе',
        'NtCreateThreadEx': 'Создание потока (низкоуровневое)',
        'SetWindowsHookEx': 'Установка хука',
        'GetAsyncKeyState': 'Перехват нажатий клавиш',
        'RegSetValueEx': 'Изменение реестра',
        'RegCreateKeyEx': 'Создание ключа реестра',
        'InternetOpen': 'Инициализация интернет-соединения',
        'URLDownloadToFile': 'Скачивание файла',
        'WinExec': 'Запуск программы',
        'ShellExecute': 'Выполнение команды оболочки',
        'CreateProcess': 'Создание процесса',
        'LoadLibrary': 'Загрузка DLL',
        'GetProcAddress': 'Получение адреса функции',
        'CryptEncrypt': 'Шифрование данных',
        'CryptDecrypt': 'Дешифрование данных',
        'DeleteFile': 'Удаление файла',
        'MoveFile': 'Перемещение файла',
        'CopyFile': 'Копирование файла',
        'FindFirstFile': 'Поиск файлов',
        'ReadFile': 'Чтение файла',
        'WriteFile': 'Запись файла',
        'CreateFile': 'Создание/открытие файла',
        'OpenProcess': 'Открытие процесса',
        'TerminateProcess': 'Завершение процесса',
        'SuspendThread': 'Приостановка потока',
        'ResumeThread': 'Возобновление потока',
        'NtUnmapViewOfSection': 'Отключение отображения раздела',
        'AdjustTokenPrivileges': 'Изменение привилегий токена',
        'LookupPrivilegeValue': 'Поиск значения привилегии',
    }
    
    # Подозрительные строки
    SUSPICIOUS_STRINGS = {
        'password': 'Поиск паролей',
        'credential': 'Работа с учётными данными',
        'bank': 'Банковская тематика',
        'crypto': 'Криптовалютная тематика',
        'wallet': 'Кошельки',
        'bitcoin': 'Биткоин',
        'ethereum': 'Эфириум',
        'keylog': 'Кейлоггер',
        'spy': 'Шпионское ПО',
        'backdoor': 'Бэкдор',
        'trojan': 'Троян',
        'ransom': 'Вымогатель',
        'encrypt': 'Шифрование',
        'decrypt': 'Дешифрование',
        'inject': 'Инъекция кода',
        'hook': 'Перехват',
        'steal': 'Кража',
        'exfil': 'Эксфильтрация',
        'c2': 'Command & Control',
        'beacon': 'Маяк',
        'payload': 'Полезная нагрузка',
        'shellcode': 'Шеллкод',
        'exploit': 'Эксплойт',
        'vulnerability': 'Уязвимость',
        'privilege': 'Привилегия',
        'escalat': 'Повышение привилегий',
        'persist': 'Персистентность',
        'autorun': 'Автозапуск',
        'startup': 'Запуск при старте',
        'hidden': 'Скрытие',
        'stealth': 'Стеалс',
        'obfuscate': 'Обфускация',
        'unpack': 'Распаковка',
        'decode': 'Декодирование',
        'base64': 'Base64 кодирование',
        'xor': 'XOR шифрование',
        'rc4': 'RC4 шифрование',
        'aes': 'AES шифрование',
        'rsa': 'RSA шифрование',
    }
    
    # Опасные расширения
    DANGEROUS_EXTENSIONS = {
        '.exe': 'Исполняемый файл',
        '.dll': 'Библиотека динамической компоновки',
        '.sys': 'Системный драйвер',
        '.bat': 'Пакетный файл',
        '.cmd': 'Командный файл',
        '.ps1': 'PowerShell скрипт',
        '.vbs': 'VBScript',
        '.js': 'JavaScript',
        '.jse': 'Зашифрованный JavaScript',
        '.wsf': 'Windows Script File',
        '.wsh': 'Windows Script Host',
        '.msi': 'Установщик Windows',
        '.msp': 'Патч Windows Installer',
        '.scr': 'Скринсейвер (исполняемый)',
        '.pif': 'Программный информационный файл',
        '.com': 'COM файл',
        '.lnk': 'Ярлык (может быть опасен)',
        '.reg': 'Файл реестра',
        '.inf': 'Файл установки',
        '.drv': 'Драйвер',
        '.ocx': 'ActiveX контрол',
        '.cpl': 'Панель управления',
        '.msc': 'Консоль управления',
    }
    
    # Белые списки (признаки чистого ПО)
    SAFE_STRINGS = [
        'copyright', 'license', 'version', 'author', 'microsoft',
        'python', 'oracle', 'google', 'apple', 'intel', 'amd',
        'nvidia', 'adobe', 'mozilla', 'firefox', 'chrome',
        'openssl', 'apache', 'nginx', 'postgresql', 'mysql',
        'github', 'gitlab', 'bitbucket', 'stackoverflow',
        'creative commons', 'gpl', 'mit license', 'bsd',
        'all rights reserved', 'trademark', 'registered',
        'official', 'certified', 'verified', 'signed',
        'digital signature', 'code signing', 'authenticode',
    ]
    
    # Критические индикаторы для каждого типа угроз
    THREAT_INDICATORS = {
        'RANSOMWARE': ['ransom', 'encrypt', 'bitcoin', 'wallet', 'decrypt', 'your files', 'pay'],
        'STEALER': ['password', 'credential', 'browser', 'cookie', 'autofill', 'wallet'],
        'KEYLOGGER': ['keylog', 'getasynckeystate', 'keyboard', 'keystroke', 'input hook'],
        'BACKDOOR': ['backdoor', 'c2', 'beacon', 'remote shell', 'reverse shell'],
        'TROJAN': ['trojan', 'payload', 'dropper', 'downloader'],
        'ROOTKIT': ['rootkit', 'hide process', 'hide file', 'ssdt', 'idt'],
        'BOTNET': ['botnet', 'ddos', 'zombie', 'irc bot', 'spam bot'],
        'CRYPTOMINER': ['cryptonight', 'monero', 'mining pool', 'stratum', 'coinhive'],
        'SPYWARE': ['spy', 'screenshot', 'webcam', 'microphone', 'clipboard'],
        'ADWARE': ['adware', 'popup', 'banner', 'redirect', 'click fraud'],
        'EXPLOIT': ['exploit', 'shellcode', 'buffer overflow', 'rop', 'use after free'],
        'WORM': ['worm', 'spread', 'replicate', 'network share', 'usb spread'],
    }
    
    def __init__(self):
        self.results = {}
    
    def analyze_file(self, file_path: str, settings: dict = None) -> dict:
        """
        Полный анализ файла на угрозы.
        
        Возвращает словарь с результатами:
        - verdict: CLEAN, SUSPICIOUS, MALICIOUS
        - threat_score: 0-100
        - threats: список найденных угроз
        - details: подробная информация
        """
        if settings is None:
            settings = {
                'deep_scan': True,
                'heuristic': True,
                'check_signatures': True,
            }
        
        result = {
            'verdict': 'CLEAN',
            'threat_score': 0,
            'threats': [],
            'details': {},
            'file_info': {},
        }
        
        path = Path(file_path)
        
        # 1. Базовая информация о файле
        result['file_info'] = self._get_file_info(path)
        
        # 2. Проверка расширения
        ext_result = self._check_extension(path)
        if ext_result:
            result['threats'].append(ext_result)
            result['threat_score'] += ext_result['score']
        
        # 3. Анализ Magic Bytes
        magic_result = self._check_magic_bytes(path)
        if magic_result:
            result['threats'].append(magic_result)
            result['threat_score'] += magic_result['score']
        
        # 4. Поиск опасных строк и API
        if settings.get('deep_scan', True):
            strings_result = self._analyze_strings(path)
            for threat in strings_result:
                result['threats'].append(threat)
                result['threat_score'] += threat['score']
        
        # 5. Эвристический анализ
        if settings.get('heuristic', True):
            heuristic_result = self._heuristic_analysis(path, result)
            result['threat_score'] += heuristic_result
        
        # 6. Проверка на признаки чистого ПО
        safe_score = self._check_safe_indicators(path)
        result['threat_score'] = max(0, result['threat_score'] - safe_score)
        
        # 7. Нормализация и определение вердикта
        result['threat_score'] = min(100, result['threat_score'])
        result['verdict'] = self._determine_verdict(result['threat_score'])
        
        # 8. Детальная информация
        result['details'] = {
            'path': str(path),
            'size': result['file_info'].get('size', 0),
            'md5': result['file_info'].get('md5', ''),
            'sha256': result['file_info'].get('sha256', ''),
            'mime_type': result['file_info'].get('mime_type', ''),
            'extension': path.suffix.lower(),
            'threat_count': len(result['threats']),
            'safe_indicators': safe_score > 0,
        }
        
        return result
    
    def _get_file_info(self, path: Path) -> dict:
        """Получение базовой информации о файле."""
        info = {
            'name': path.name,
            'size': 0,
            'md5': '',
            'sha256': '',
            'mime_type': '',
        }
        
        try:
            info['size'] = path.stat().st_size
            
            # Хэши
            with open(path, 'rb') as f:
                data = f.read(8192)
                md5_hash = hashlib.md5()
                sha256_hash = hashlib.sha256()
                
                md5_hash.update(data)
                sha256_hash.update(data)
                
                info['md5'] = md5_hash.hexdigest()
                info['sha256'] = sha256_hash.hexdigest()
            
            # MIME тип
            try:
                info['mime_type'] = magic.from_file(str(path), mime=True)
            except:
                info['mime_type'] = 'unknown'
                
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def _check_extension(self, path: Path) -> Optional[dict]:
        """Проверка расширения файла."""
        ext = path.suffix.lower()
        
        if ext in self.DANGEROUS_EXTENSIONS:
            return {
                'type': 'Extension Check',
                'threat': f'Опасное расширение: {ext}',
                'description': self.DANGEROUS_EXTENSIONS[ext],
                'severity': 'medium',
                'score': 15,
            }
        
        # Двойное расширение (например, file.txt.exe)
        if path.stem.count('.') > 0:
            return {
                'type': 'Extension Check',
                'threat': 'Двойное расширение',
                'description': 'Возможная маскировка вредоносного файла',
                'severity': 'high',
                'score': 30,
            }
        
        return None
    
    def _check_magic_bytes(self, path: Path) -> Optional[dict]:
        """Проверка Magic Bytes (сигнатур файла)."""
        try:
            with open(path, 'rb') as f:
                header = f.read(16)
            
            # PE файл (Windows executable)
            if header[:2] == b'MZ':
                return {
                    'type': 'Magic Bytes',
                    'threat': 'PE Executable',
                    'description': 'Исполняемый файл Windows',
                    'severity': 'info',
                    'score': 5,
                }
            
            # ELF файл (Linux executable)
            if header[:4] == b'\x7fELF':
                return {
                    'type': 'Magic Bytes',
                    'threat': 'ELF Executable',
                    'description': 'Исполняемый файл Linux',
                    'severity': 'info',
                    'score': 5,
                }
            
            # Скрипты
            if header[:2] == b'#!':
                return {
                    'type': 'Magic Bytes',
                    'threat': 'Script File',
                    'description': 'Скриптовый файл',
                    'severity': 'info',
                    'score': 3,
                }
                
        except Exception:
            pass
        
        return None
    
    def _analyze_strings(self, path: Path) -> List[dict]:
        """Анализ строк в файле."""
        threats = []
        
        try:
            with open(path, 'rb') as f:
                content = f.read()
            
            # Декодирование (попытка разных кодировок)
            text_content = ''
            for encoding in ['utf-8', 'latin-1', 'cp1251']:
                try:
                    text_content = content.decode(encoding, errors='ignore')
                    break
                except:
                    continue
            
            text_lower = text_content.lower()
            
            # Проверка на опасные API
            for api, description in self.DANGEROUS_APIS.items():
                if api.lower() in text_lower:
                    severity = 'high' if api in ['VirtualAlloc', 'WriteProcessMemory', 'CreateRemoteThread'] else 'medium'
                    score = 20 if severity == 'high' else 10
                    
                    threats.append({
                        'type': 'Dangerous API',
                        'threat': f'Обнаружен API: {api}',
                        'description': description,
                        'severity': severity,
                        'score': score,
                    })
            
            # Проверка на подозрительные строки
            for string, description in self.SUSPICIOUS_STRINGS.items():
                if string in text_lower:
                    # Проверка на критические индикаторы
                    is_critical = False
                    for threat_type, indicators in self.THREAT_INDICATORS.items():
                        if any(ind in text_lower for ind in indicators):
                            is_critical = True
                            threats.append({
                                'type': 'Threat Indicator',
                                'threat': f'Индикатор угрозы: {threat_type}',
                                'description': f'Найдены признаки: {", ".join([i for i in indicators if i in text_lower])}',
                                'severity': 'critical',
                                'score': 40,
                            })
                            break
                    
                    if not is_critical:
                        threats.append({
                            'type': 'Suspicious String',
                            'threat': f'Подозрительная строка: {string}',
                            'description': description,
                            'severity': 'low',
                            'score': 5,
                        })
                        
        except Exception as e:
            pass
        
        return threats
    
    def _heuristic_analysis(self, path: Path, current_result: dict) -> int:
        """Эвристический анализ."""
        score = 0
        
        # Анализ размера файла
        size = path.stat().st_size if path.exists() else 0
        
        # Очень маленький исполняемый файл (< 1KB)
        if size < 1024 and path.suffix.lower() in ['.exe', '.dll', '.scr']:
            score += 20
        
        # Подозрительно большой скрипт (> 1MB)
        if size > 1024 * 1024 and path.suffix.lower() in ['.js', '.vbs', '.ps1']:
            score += 15
        
        # Анализ имени файла
        name_lower = path.name.lower()
        suspicious_names = ['update', 'install', 'setup', 'patch', 'crack', 'keygen', 'activator']
        if any(s in name_lower for s in suspicious_names):
            score += 10
        
        # Скрытые файлы
        if path.name.startswith('.'):
            score += 10
        
        return score
    
    def _check_safe_indicators(self, path: Path) -> int:
        """Проверка на признаки чистого ПО."""
        safe_score = 0
        
        try:
            with open(path, 'rb') as f:
                content = f.read(65536).decode('utf-8', errors='ignore').lower()
            
            # Проверка белых списков
            for safe_string in self.SAFE_STRINGS:
                if safe_string in content:
                    safe_score += 10
            
            # Наличие цифровой подписи (упрощённо)
            if 'signature' in content or 'signed' in content:
                safe_score += 20
            
            # Стандартные лицензии
            if any(lic in content for lic in ['gpl', 'mit', 'apache', 'bsd']):
                safe_score += 15
                
        except Exception:
            pass
        
        return safe_score
    
    def _determine_verdict(self, score: int) -> str:
        """Определение вердикта по очкам."""
        if score >= 60:
            return 'MALICIOUS'
        elif score >= 25:
            return 'SUSPICIOUS'
        else:
            return 'CLEAN'


# ============================================================================
# РАБОЧИЙ ПОТОК СКАНИРОВАНИЯ
# ============================================================================

class ScanWorker(QObject):
    """Рабочий поток для сканирования."""
    
    progress = pyqtSignal(int)
    log_message = pyqtSignal(str)
    scan_complete = pyqtSignal(dict)
    finished = pyqtSignal()
    
    def __init__(self, file_path: str, settings: dict):
        super().__init__()
        self.file_path = file_path
        self.settings = settings
        self.analyzer = ThreatAnalyzer()
    
    def run(self):
        """Запуск сканирования."""
        try:
            self.log_message.emit(f"[INFO] Начало анализа файла: {self.file_path}")
            self.progress.emit(10)
            
            # Получение информации о файле
            self.log_message.emit("[INFO] Сбор информации о файле...")
            self.progress.emit(20)
            
            # Запуск анализа
            self.log_message.emit("[INFO] Запуск эвристического анализа...")
            self.progress.emit(30)
            
            result = self.analyzer.analyze_file(self.file_path, self.settings)
            self.progress.emit(80)
            
            # Логирование результатов
            if result['verdict'] == 'CLEAN':
                self.log_message.emit(f"[INFO] Вердикт: Файл чист (угроз не обнаружено)")
            elif result['verdict'] == 'SUSPICIOUS':
                self.log_message.emit(f"[WARNING] Вердикт: Подозрительный файл (найденные угрозы: {len(result['threats'])})")
            else:
                self.log_message.emit(f"[DANGER] Вердикт: Вредоносный файл обнаружен!")
            
            # Детальное логирование угроз
            for i, threat in enumerate(result['threats'], 1):
                severity_tag = {
                    'critical': '[CRITICAL]',
                    'high': '[HIGH]',
                    'medium': '[MEDIUM]',
                    'low': '[LOW]',
                    'info': '[INFO]',
                }.get(threat.get('severity', 'info'), '[INFO]')
                
                self.log_message.emit(
                    f"{severity_tag} Угроза #{i}: {threat['threat']}"
                )
                self.log_message.emit(
                    f"  Тип: {threat['type']}"
                )
                self.log_message.emit(
                    f"  Описание: {threat['description']}"
                )
            
            if not result['threats']:
                self.log_message.emit("[INFO] Детальных угроз не найдено")
            
            self.progress.emit(100)
            self.scan_complete.emit(result)
            
        except Exception as e:
            self.log_message.emit(f"[ERROR] Ошибка сканирования: {str(e)}")
        
        finally:
            self.finished.emit()


# ============================================================================
# ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ
# ============================================================================

class RedSandGUI(QMainWindow):
    """Главное окно приложения RedSand Antivirus."""
    
    def __init__(self):
        super().__init__()
        
        # Менеджеры
        self.language_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        
        # Состояние
        self.file_path = ''
        self.is_scanning = False
        self.scan_thread = None
        self.scan_worker = None
        
        # Настройка интерфейса
        self.setup_ui()
        self.apply_theme()
        self.update_texts()
        
        # Настройка соединений
        self.setup_connections()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        self.setWindowTitle(self.language_manager.get_text('app_title'))
        self.setMinimumSize(1400, 900)
        
        # Центральное окно
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title_label = QLabel(self.language_manager.get_text('app_title'))
        title_label.setObjectName('titleLabel')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Основной разделитель
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(6)
        
        # Левая панель
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Правая панель
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        
        # Создание меню
        self.create_menu()
        
        # Статус бар
        self.statusBar().showMessage(self.language_manager.get_text('status_ready'))
        
        # Таймер
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_seconds = 0
    
    def create_left_panel(self) -> QWidget:
        """Создание левой панели."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)
        
        # Группа выбора файла
        file_group = QGroupBox(self.language_manager.get_text('lbl_file'))
        file_layout = QVBoxLayout(file_group)
        
        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText('Выберите файл для сканирования...')
        self.file_edit.setReadOnly(True)
        file_layout.addWidget(self.file_edit)
        
        browse_btn = QPushButton(self.language_manager.get_text('btn_browse'))
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        
        layout.addWidget(file_group)
        
        # Группа настроек сканирования
        scan_group = QGroupBox('Настройки сканирования')
        scan_layout = QVBoxLayout(scan_group)
        
        self.chk_deep_scan = QCheckBox(self.language_manager.get_text('chk_deep_scan'))
        self.chk_deep_scan.setChecked(True)
        scan_layout.addWidget(self.chk_deep_scan)
        
        self.chk_heuristic = QCheckBox(self.language_manager.get_text('chk_heuristic'))
        self.chk_heuristic.setChecked(True)
        scan_layout.addWidget(self.chk_heuristic)
        
        self.chk_unpack = QCheckBox(self.language_manager.get_text('chk_unpack_archives'))
        self.chk_unpack.setChecked(False)
        scan_layout.addWidget(self.chk_unpack)
        
        # Чувствительность
        sensitivity_layout = QHBoxLayout()
        sensitivity_label = QLabel(self.language_manager.get_text('lbl_sensitivity'))
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setMinimum(1)
        self.sensitivity_slider.setMaximum(100)
        self.sensitivity_slider.setValue(75)
        sensitivity_layout.addWidget(sensitivity_label)
        sensitivity_layout.addWidget(self.sensitivity_slider)
        scan_layout.addLayout(sensitivity_layout)
        
        layout.addWidget(scan_group)
        
        # Кнопки управления
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(15)
        
        self.scan_btn = QPushButton(self.language_manager.get_text('btn_scan'))
        self.scan_btn.setObjectName('primaryBtn')
        self.scan_btn.clicked.connect(self.start_scan)
        btn_layout.addWidget(self.scan_btn)
        
        self.stop_btn = QPushButton(self.language_manager.get_text('btn_stop'))
        self.stop_btn.setObjectName('dangerBtn')
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_scan)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Создание правой панели."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Вкладки
        self.tabs = QTabWidget()
        
        # Вкладка логов
        logs_tab = self.create_logs_tab()
        self.tabs.addTab(logs_tab, self.language_manager.get_text('tab_logs'))
        
        # Вкладка результатов
        results_tab = self.create_results_tab()
        self.tabs.addTab(results_tab, self.language_manager.get_text('tab_results'))
        
        # Вкладка IOC
        ioc_tab = self.create_ioc_tab()
        self.tabs.addTab(ioc_tab, self.language_manager.get_text('tab_ioc'))
        
        # Вкладка визуализации
        viz_tab = self.create_viz_tab()
        self.tabs.addTab(viz_tab, self.language_manager.get_text('tab_visualization'))
        
        layout.addWidget(self.tabs)
        
        # Группа прогресса
        progress_group = QGroupBox(self.language_manager.get_text('lbl_progress'))
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        # Время и угрозы
        info_layout = QHBoxLayout()
        
        time_label = QLabel(self.language_manager.get_text('lbl_time'))
        info_layout.addWidget(time_label)
        
        self.time_lcd = QLCDNumber()
        self.time_lcd.setDigitCount(8)
        self.time_lcd.display('00:00:00')
        info_layout.addWidget(self.time_lcd)
        
        info_layout.addStretch()
        
        threats_label = QLabel(self.language_manager.get_text('lbl_threats'))
        info_layout.addWidget(threats_label)
        
        self.threat_count = QLabel('0')
        self.threat_count.setStyleSheet('font-size: 24px; font-weight: bold; color: #ff4757;')
        info_layout.addWidget(self.threat_count)
        
        info_layout.addStretch()
        
        verdict_label = QLabel(self.language_manager.get_text('lbl_verdict'))
        info_layout.addWidget(verdict_label)
        
        self.verdict_label = QLabel(self.language_manager.get_text('verdict_clean'))
        self.verdict_label.setStyleSheet('font-size: 20px; font-weight: bold; color: #2ed573;')
        info_layout.addWidget(self.verdict_label)
        
        progress_layout.addLayout(info_layout)
        
        layout.addWidget(progress_group)
        
        return panel
    
    def create_logs_tab(self) -> QWidget:
        """Создание вкладки логов."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont('Consolas', 9))
        self.log_text.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.appendPlainText(f"[{timestamp}] {self.language_manager.get_text('status_ready')}")
        
        layout.addWidget(self.log_text)
        
        return tab
    
    def create_results_tab(self) -> QWidget:
        """Создание вкладки результатов."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            'Тип', 'Угроза', 'Описание', 'Серьёзность', 'Оценка'
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.results_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.results_table)
        
        return tab
    
    def create_ioc_tab(self) -> QWidget:
        """Создание вкладки IOC."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.ioc_tree = QTreeWidget()
        self.ioc_tree.setHeaderLabels(['Категория', 'Тип', 'Значение'])
        self.ioc_tree.setAlternatingRowColors(True)
        
        layout.addWidget(self.ioc_tree)
        
        return tab
    
    def create_viz_tab(self) -> QWidget:
        """Создание вкладки визуализации."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Заглушка для визуализации
        placeholder = QLabel('Визуализация будет доступна в следующей версии')
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet('font-size: 18px; color: #a0a0a0;')
        
        layout.addWidget(placeholder)
        
        return tab
    
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
        self.statusBar().showMessage(self.language_manager.get_text('status_ready'))
    
    def change_theme(self, theme_name: str):
        """Смена темы."""
        self.theme_manager.set_current_theme(theme_name)
        self.apply_theme()
        self.log_message(f"Тема изменена на: {theme_name}")
    
    def change_language(self, lang: str):
        """Смена языка."""
        self.language_manager.set_language(lang)
        self.update_texts()
        self.log_message(f"Язык изменён на: {lang}")
    
    def open_settings(self):
        """Открытие диалога настроек."""
        dialog = SettingsDialog(self, self.theme_manager, self.language_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            
            if settings['theme'] != self.theme_manager.current_theme:
                self.change_theme(settings['theme'])
            
            if settings['language'] != self.language_manager.current_language:
                self.change_language(settings['language'])
            
            self.theme_manager.font_size = settings['font_size']
            self.theme_manager.animations_enabled = settings['animations_enabled']
            
            self.apply_theme()
            self.log_message("Настройки сохранены")
    
    def browse_file(self):
        """Выбор файла."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Выберите файл для сканирования',
            '',
            'Все файлы (*);;Исполняемые файлы (*.exe *.elf *.bin);;Скрипты (*.py *.js *.ps1 *.vbs)'
        )
        if file_path:
            self.file_path = file_path
            self.file_edit.setText(file_path)
            self.log_message(f"Файл выбран: {file_path}")
    
    def start_scan(self):
        """Начало сканирования."""
        if not self.file_path:
            QMessageBox.warning(self, 'Предупреждение', self.language_manager.get_text('msg_no_file'))
            return
        
        self.is_scanning = True
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.elapsed_seconds = 0
        self.timer.start(1000)
        
        # Очистка предыдущих результатов
        self.results_table.setRowCount(0)
        self.ioc_tree.clear()
        self.threat_count.setText('0')
        self.verdict_label.setText(self.language_manager.get_text('verdict_clean'))
        self.verdict_label.setStyleSheet('font-size: 20px; font-weight: bold; color: #2ed573;')
        
        self.log_message(f"Начало сканирования: {self.file_path}")
        self.statusBar().showMessage(self.language_manager.get_text('status_scanning'))
        
        # Создание рабочего потока
        settings = {
            'deep_scan': self.chk_deep_scan.isChecked(),
            'heuristic': self.chk_heuristic.isChecked(),
            'unpack_archives': self.chk_unpack.isChecked(),
        }
        
        self.scan_thread = QThread()
        self.scan_worker = ScanWorker(self.file_path, settings)
        self.scan_worker.moveToThread(self.scan_thread)
        
        # Подключение сигналов
        self.scan_thread.started.connect(self.scan_worker.run)
        self.scan_worker.progress.connect(self.progress_bar.setValue)
        self.scan_worker.log_message.connect(self.log_message)
        self.scan_worker.scan_complete.connect(self.on_scan_complete)
        self.scan_worker.finished.connect(self.scan_thread.quit)
        self.scan_worker.finished.connect(self.scan_worker.deleteLater)
        self.scan_thread.finished.connect(self.scan_thread.deleteLater)
        
        self.scan_thread.start()
    
    def stop_scan(self):
        """Остановка сканирования."""
        if self.is_scanning and self.scan_thread:
            self.scan_thread.quit()
            self.scan_thread.wait()
            self.is_scanning = False
            self.scan_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.timer.stop()
            self.log_message("Сканирование остановлено пользователем")
            self.statusBar().showMessage('Остановлено')
    
    def on_scan_complete(self, result: dict):
        """Обработка завершения сканирования."""
        self.is_scanning = False
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.timer.stop()
        
        # Обновление вердикта
        verdict_key = {
            'CLEAN': 'verdict_clean',
            'SUSPICIOUS': 'verdict_suspicious',
            'MALICIOUS': 'verdict_malicious',
        }.get(result['verdict'], 'verdict_clean')
        
        verdict_text = self.language_manager.get_text(verdict_key)
        
        verdict_color = {
            'CLEAN': '#2ed573',
            'SUSPICIOUS': '#ffa502',
            'MALICIOUS': '#ff4757',
        }.get(result['verdict'], '#2ed573')
        
        self.verdict_label.setText(verdict_text)
        self.verdict_label.setStyleSheet(f'font-size: 20px; font-weight: bold; color: {verdict_color};')
        
        # Обновление счётчика угроз
        self.threat_count.setText(str(len(result['threats'])))
        
        # Заполнение таблицы результатов
        self.results_table.setRowCount(len(result['threats']))
        for i, threat in enumerate(result['threats']):
            severity_map = {
                'critical': self.language_manager.get_text('severity_critical'),
                'high': self.language_manager.get_text('severity_high'),
                'medium': self.language_manager.get_text('severity_medium'),
                'low': self.language_manager.get_text('severity_low'),
                'info': 'Инфо',
            }
            
            self.results_table.setItem(i, 0, QTableWidgetItem(threat.get('type', '')))
            self.results_table.setItem(i, 1, QTableWidgetItem(threat.get('threat', '')))
            self.results_table.setItem(i, 2, QTableWidgetItem(threat.get('description', '')))
            self.results_table.setItem(i, 3, QTableWidgetItem(severity_map.get(threat.get('severity', 'info'), '')))
            self.results_table.setItem(i, 4, QTableWidgetItem(str(threat.get('score', 0))))
        
        # Заполнение IOC дерева
        if result.get('file_info'):
            root_item = QTreeWidgetItem(['Информация о файле', '', ''])
            
            items = [
                ('Путь', result['details'].get('path', '')),
                ('Размер', f"{result['details'].get('size', 0)} байт"),
                ('MD5', result['details'].get('md5', '')),
                ('SHA-256', result['details'].get('sha256', '')),
                ('MIME тип', result['details'].get('mime_type', '')),
                ('Расширение', result['details'].get('extension', '')),
            ]
            
            for label, value in items:
                child = QTreeWidgetItem([label, value, ''])
                root_item.addChild(child)
            
            self.ioc_tree.addTopLevelItem(root_item)
        
        self.log_message(self.language_manager.get_text('msg_scan_complete'))
        self.statusBar().showMessage(self.language_manager.get_text('status_complete'))
        
        # Показ итогового окна
        self.show_scan_summary(result)
    
    def show_scan_summary(self, result: dict):
        """Показ окна с итогами сканирования."""
        verdict_key = {
            'CLEAN': 'verdict_clean',
            'SUSPICIOUS': 'verdict_suspicious',
            'MALICIOUS': 'verdict_malicious',
        }.get(result['verdict'], 'verdict_clean')
        
        verdict_text = self.language_manager.get_text(verdict_key)
        
        message = (
            f"<h2>Результаты сканирования</h2>"
            f"<p><b>Вердикт:</b> <span style='color: {'#2ed573' if result['verdict'] == 'CLEAN' else '#ff4757'}'>{verdict_text}</span></p>"
            f"<p><b>Уровень угрозы:</b> {result['threat_score']}%</p>"
            f"<p><b>Найдено угроз:</b> {len(result['threats'])}</p>"
            f"<p><b>Файл:</b> {Path(self.file_path).name}</p>"
            f"<p><b>Размер:</b> {result['details'].get('size', 0)} байт</p>"
        )
        
        if result['threats']:
            message += "<h3>Обнаруженные угрозы:</h3><ul>"
            for threat in result['threats']:
                message += f"<li>{threat['threat']} ({threat.get('severity', 'info')})</li>"
            message += "</ul>"
        else:
            message += "<p><i>Детальных угроз не найдено</i></p>"
        
        QMessageBox.information(self, 'Результаты сканирования', message)
    
    def update_timer(self):
        """Обновление таймера."""
        self.elapsed_seconds += 1
        hours = self.elapsed_seconds // 3600
        minutes = (self.elapsed_seconds % 3600) // 60
        seconds = self.elapsed_seconds % 60
        self.time_lcd.display(f'{hours:02d}:{minutes:02d}:{seconds:02d}')
    
    def log_message(self, message: str):
        """Добавление сообщения в лог."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.appendPlainText(f"[{timestamp}] {message}")
    
    def show_about(self):
        """Показ информации о программе."""
        QMessageBox.about(
            self,
            'О RedSand Antivirus',
            '<h2>RedSand Antivirus v7.0</h2>'
            '<p>Современная система защиты от вредоносного ПО</p>'
            '<p><b>Возможности:</b></p>'
            '<ul>'
            '<li>Реальное эвристическое сканирование</li>'
            '<li>Обнаружение 12+ типов угроз</li>'
            '<li>Анализ Magic Bytes и сигнатур</li>'
            '<li>Поддержка 6 языков</li>'
            '<li>4 темы оформления</li>'
            '<li>Глубокий анализ строк и API</li>'
            '<li>Белый список чистого ПО</li>'
            '</ul>'
            '<p>© 2024 RedSand Security Team</p>'
        )


# ============================================================================
# ДИАЛОГ НАСТРОЕК
# ============================================================================

class SettingsDialog(QDialog):
    """Диалог настроек приложения."""
    
    def __init__(self, parent=None, theme_manager=None, language_manager=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.language_manager = language_manager
        self.setWindowTitle(self.language_manager.get_text('settings_title') if hasattr(self, 'language_manager') else 'Настройки')
        self.setMinimumSize(600, 500)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
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
        general_layout.addRow(self.language_manager.get_text('lbl_language') if hasattr(self, 'language_manager') else 'Язык:', self.lang_combo)
        
        # Тема
        self.theme_combo = QComboBox()
        if self.theme_manager:
            for theme_name in self.theme_manager.get_all_theme_names():
                self.theme_combo.addItem(theme_name.replace('_', ' ').title(), theme_name)
        general_layout.addRow(self.language_manager.get_text('lbl_theme') if hasattr(self, 'language_manager') else 'Тема:', self.theme_combo)
        
        # Размер шрифта
        self.font_spin = QSpinBox()
        self.font_spin.setMinimum(8)
        self.font_spin.setMaximum(20)
        self.font_spin.setValue(self.theme_manager.font_size if self.theme_manager else 10)
        general_layout.addRow(self.language_manager.get_text('lbl_font_size') if hasattr(self, 'language_manager') else 'Размер шрифта:', self.font_spin)
        
        tab_widget.addTab(general_tab, self.language_manager.get_text('settings_general') if hasattr(self, 'language_manager') else 'Общие')
        
        # Вкладка "Безопасность"
        security_tab = QWidget()
        security_layout = QVBoxLayout(security_tab)
        security_layout.setSpacing(12)
        
        self.chk_deep_scan = QCheckBox(self.language_manager.get_text('chk_deep_scan') if hasattr(self, 'language_manager') else 'Глубокий анализ')
        self.chk_deep_scan.setChecked(True)
        security_layout.addWidget(self.chk_deep_scan)
        
        self.chk_heuristic = QCheckBox(self.language_manager.get_text('chk_heuristic') if hasattr(self, 'language_manager') else 'Эвристический анализ')
        self.chk_heuristic.setChecked(True)
        security_layout.addWidget(self.chk_heuristic)
        
        self.chk_sandbox = QCheckBox(self.language_manager.get_text('chk_sandbox') if hasattr(self, 'language_manager') else 'Режим песочницы')
        self.chk_sandbox.setChecked(False)
        security_layout.addWidget(self.chk_sandbox)
        
        self.chk_auto_delete = QCheckBox(self.language_manager.get_text('chk_auto_delete') if hasattr(self, 'language_manager') else 'Автоудаление угроз')
        self.chk_auto_delete.setChecked(False)
        security_layout.addWidget(self.chk_auto_delete)
        
        self.chk_unpack = QCheckBox(self.language_manager.get_text('chk_unpack_archives') if hasattr(self, 'language_manager') else 'Распаковка архивов')
        self.chk_unpack.setChecked(False)
        security_layout.addWidget(self.chk_unpack)
        
        self.chk_signatures = QCheckBox(self.language_manager.get_text('chk_check_signatures') if hasattr(self, 'language_manager') else 'Проверка цифровых подписей')
        self.chk_signatures.setChecked(True)
        security_layout.addWidget(self.chk_signatures)
        
        tab_widget.addTab(security_tab, self.language_manager.get_text('settings_security') if hasattr(self, 'language_manager') else 'Безопасность')
        
        # Вкладка "Внешний вид"
        appearance_tab = QWidget()
        appearance_layout = QFormLayout(appearance_tab)
        appearance_layout.setSpacing(15)
        
        self.chk_animations = QCheckBox(self.language_manager.get_text('chk_enable_animations') if hasattr(self, 'language_manager') else 'Включить анимации')
        self.chk_animations.setChecked(self.theme_manager.animations_enabled if self.theme_manager else True)
        appearance_layout.addRow('', self.chk_animations)
        
        tab_widget.addTab(appearance_tab, self.language_manager.get_text('settings_appearance') if hasattr(self, 'language_manager') else 'Внешний вид')
        
        layout.addWidget(tab_widget)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Save).setText(
            self.language_manager.get_text('btn_save') if hasattr(self, 'language_manager') else 'Сохранить'
        )
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(
            self.language_manager.get_text('btn_cancel') if hasattr(self, 'language_manager') else 'Отмена'
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def get_settings(self) -> dict:
        """Получение настроек."""
        return {
            'language': self.lang_combo.currentData(),
            'theme': self.theme_combo.currentData(),
            'font_size': self.font_spin.value(),
            'animations_enabled': self.chk_animations.isChecked(),
            'deep_scan': self.chk_deep_scan.isChecked(),
            'heuristic': self.chk_heuristic.isChecked(),
            'sandbox': self.chk_sandbox.isChecked(),
            'auto_delete': self.chk_auto_delete.isChecked(),
            'unpack_archives': self.chk_unpack.isChecked(),
            'check_signatures': self.chk_signatures.isChecked(),
        }


# ============================================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ============================================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    app.setOrganizationName('RedSand')
    app.setApplicationName('RedSand Antivirus')
    
    window = RedSandGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
