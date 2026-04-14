#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Secure GUI v3.0 - Профессиональный интерфейс с темами и настройками
Современный дизайн на PyQt5 с поддержкой тем, анимаций и расширенных настроек
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
    QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QObject, QThread, QMetaObject,
    Q_ARG, QPropertyAnimation, QEasingCurve, QSize, QUrl,
    QPoint, QRect, QSettings, QTranslator, QLocale
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QIcon, QPixmap, QPainter,
    QBrush, QPen, QLinearGradient, QDesktopServices,
    QTextCursor, QTextDocument, QMovie, QKeySequence,
    QShortcut, QCursor
)

# Добавляем модули в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from redsand_secure import RedSandSecure
    REDSAND_AVAILABLE = True
except ImportError:
    REDSAND_AVAILABLE = False


# ============================================================================
# ЦВЕТОВЫЕ ТЕМЫ
# ============================================================================

THEMES = {
    "Dark Red": {
        "bg_primary": "#1a1a2e",
        "bg_secondary": "#16213e",
        "bg_tertiary": "#0f3460",
        "accent": "#e94560",
        "accent_hover": "#ff6b7a",
        "text_primary": "#eaeaea",
        "text_secondary": "#a0a0a0",
        "success": "#28a745",
        "warning": "#ffc107",
        "danger": "#dc3545",
        "info": "#17a2b8"
    },
    "Cyber Blue": {
        "bg_primary": "#0a0e1a",
        "bg_secondary": "#111827",
        "bg_tertiary": "#1e293b",
        "accent": "#3b82f6",
        "accent_hover": "#60a5fa",
        "text_primary": "#f3f4f6",
        "text_secondary": "#9ca3af",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "info": "#8b5cf6"
    },
    "Matrix Green": {
        "bg_primary": "#0d1117",
        "bg_secondary": "#161b22",
        "bg_tertiary": "#21262d",
        "accent": "#00ff41",
        "accent_hover": "#00cc33",
        "text_primary": "#c9d1d9",
        "text_secondary": "#8b949e",
        "success": "#2ea043",
        "warning": "#d29922",
        "danger": "#f85149",
        "info": "#58a6ff"
    },
    "Purple Haze": {
        "bg_primary": "#1e1b2e",
        "bg_secondary": "#2d2640",
        "bg_tertiary": "#3d3452",
        "accent": "#a855f7",
        "accent_hover": "#c084fc",
        "text_primary": "#f5f3ff",
        "text_secondary": "#c4b5fd",
        "success": "#22c55e",
        "warning": "#fbbf24",
        "danger": "#f43f5e",
        "info": "#06b6d4"
    },
    "Ocean Depth": {
        "bg_primary": "#0c1929",
        "bg_secondary": "#0f2338",
        "bg_tertiary": "#143446",
        "accent": "#00bcd4",
        "accent_hover": "#26c6da",
        "text_primary": "#e0f7fa",
        "text_secondary": "#80deea",
        "success": "#4caf50",
        "warning": "#ff9800",
        "danger": "#f44336",
        "info": "#2196f3"
    },
    "Light Modern": {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f8f9fa",
        "bg_tertiary": "#e9ecef",
        "accent": "#dc3545",
        "accent_hover": "#c82333",
        "text_primary": "#212529",
        "text_secondary": "#6c757d",
        "success": "#28a745",
        "warning": "#ffc107",
        "danger": "#dc3545",
        "info": "#17a2b8"
    }
}


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
            result = sandbox.analyze(
                self.file_path,
                use_poly=self.use_poly,
                timeout=self.timeout
            )
            
            if result:
                self.finished.emit(result)
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
        self.setWindowTitle("Настройки")
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        # Таймаут анализа
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(60)
        self.timeout_spin.setSuffix(" сек")
        form.addRow("Таймаут анализа:", self.timeout_spin)
        
        # Директория отчетов
        self.output_dir_edit = QLineEdit("reports")
        btn_browse = QPushButton("Обзор...")
        btn_browse.clicked.connect(self.browse_output_dir)
        
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(btn_browse)
        form.addRow("Директория отчетов:", output_layout)
        
        # Поли морфный анализ по умолчанию
        self.poly_check = QCheckBox("Включить полиморфный анализ по умолчанию")
        form.addRow("", self.poly_check)
        
        # Автозакрытие сети
        self.network_check = QCheckBox("Автоматически отключать сеть при анализе")
        self.network_check.setChecked(True)
        form.addRow("", self.network_check)
        
        # Уровень логирования
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        form.addRow("Уровень логирования:", self.log_level_combo)
        
        layout.addLayout(form)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Выберите директорию для отчетов"
        )
        if directory:
            self.output_dir_edit.setText(directory)
    
    def get_settings(self):
        return {
            'timeout': self.timeout_spin.value(),
            'output_dir': self.output_dir_edit.text(),
            'use_poly_default': self.poly_check.isChecked(),
            'auto_disable_network': self.network_check.isChecked(),
            'log_level': self.log_level_combo.currentText()
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
        tabs.addTab(summary_widget, "📊 Сводка")
        
        # Вкладка статического анализа
        static_widget = self.create_static_tab()
        tabs.addTab(static_widget, "🔍 Статический анализ")
        
        # Вкладка динамического анализа
        dynamic_widget = self.create_dynamic_tab()
        tabs.addTab(dynamic_widget, "🎬 Динамический анализ")
        
        # Вкладка IOC
        ioc_widget = self.create_ioc_tab()
        tabs.addTab(ioc_widget, "🎯 IOC")
        
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
        
        threat_info = self.report_data.get('threat_classification', {})
        file_info = self.report_data.get('file', {})
        analysis_time = self.report_data.get('analysis_time', {})
        
        # Индикатор риска
        risk_score = threat_info.get('risk_score', 0)
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
        info_layout.addWidget(QLabel(threat_info.get('type', 'Неизвестно')), 0, 1)
        
        info_layout.addWidget(QLabel("Семейство:"), 1, 0)
        info_layout.addWidget(QLabel(threat_info.get('family', 'Неизвестно')), 1, 1)
        
        info_layout.addWidget(QLabel("Доверие:"), 2, 0)
        info_layout.addWidget(QLabel(threat_info.get('confidence', 'Низкое')), 2, 1)
        
        info_layout.addWidget(QLabel("MITRE ATT&CK:"), 3, 0)
        mitre_text = QLabel(', '.join(threat_info.get('mitre_tactics', [])))
        mitre_text.setWordWrap(True)
        info_layout.addWidget(mitre_text, 3, 1)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Информация о файле
        file_group = QGroupBox("Информация о файле")
        file_layout = QGridLayout()
        
        file_layout.addWidget(QLabel("Имя:"), 0, 0)
        file_layout.addWidget(QLabel(file_info.get('name', 'N/A')), 0, 1)
        
        file_layout.addWidget(QLabel("Размер:"), 1, 0)
        file_layout.addWidget(QLabel(f"{file_info.get('size', 0)} байт"), 1, 1)
        
        file_layout.addWidget(QLabel("Путь:"), 2, 0)
        path_label = QLabel(file_info.get('path', 'N/A'))
        path_label.setWordWrap(True)
        file_layout.addWidget(path_label, 2, 1)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Время анализа
        time_group = QGroupBox("Время анализа")
        time_layout = QGridLayout()
        
        time_layout.addWidget(QLabel("Начало:"), 0, 0)
        time_layout.addWidget(QLabel(analysis_time.get('start', 'N/A')), 0, 1)
        
        time_layout.addWidget(QLabel("Длительность:"), 1, 0)
        time_layout.addWidget(QLabel(f"{analysis_time.get('duration', 0):.2f} сек"), 1, 1)
        
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        layout.addStretch()
        return widget
    
    def create_static_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        static_data = self.report_data.get('static_analysis', {})
        
        # Хеши
        hashes_group = QGroupBox("Хеши файла")
        hashes_layout = QGridLayout()
        hashes = static_data.get('hashes', {})
        
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
        if static_data.get('pe_info'):
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
        if static_data.get('strings'):
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
        
        dynamic_events = self.report_data.get('dynamic_analysis', [])
        
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
        
        static_data = self.report_data.get('static_analysis', {})
        hashes = static_data.get('hashes', {})
        
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
        self.setWindowTitle("🛡️ RedSand Secure v2.0 - Анализ вредоносного ПО")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Центральное виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title_label = QLabel("🛡️ RedSand Secure v2.0")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Профессиональная система анализа вредоносного ПО")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #8a8a8a; font-size: 14px;")
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
        self.status_bar.showMessage("Готов к работе")
    
    def create_left_panel(self) -> QWidget:
        """Создание левой панели управления."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Группа выбора файла
        file_group = QGroupBox("📁 Выбор файла для анализа")
        file_layout = QVBoxLayout()
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Выберите файл для анализа...")
        self.file_path_edit.setReadOnly(True)
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
        self.poly_check = QCheckBox("Полиморфный анализ")
        self.poly_check.setToolTip("Генерировать полиморфные варианты образца")
        settings_layout.addWidget(self.poly_check, 1, 0, 1, 2)
        
        # Отключение сети
        self.network_check = QCheckBox("Отключать сеть")
        self.network_check.setChecked(True)
        self.network_check.setToolTip("Автоматически отключать сетевые адаптеры")
        settings_layout.addWidget(self.network_check, 2, 0, 1, 2)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Кнопка запуска анализа
        self.btn_analyze = QPushButton("🚀 ЗАПУСТИТЬ АНАЛИЗ")
        self.btn_analyze.setObjectName("primaryBtn")
        self.btn_analyze.setMinimumHeight(60)
        self.btn_analyze.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.btn_analyze.clicked.connect(self.start_analysis)
        layout.addWidget(self.btn_analyze)
        
        # Кнопка экстренной остановки
        self.btn_panic = QPushButton("🔴 ЭКСТРЕННАЯ ОСТАНОВКА")
        self.btn_panic.setObjectName("dangerBtn")
        self.btn_panic.setMinimumHeight(50)
        self.btn_panic.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_panic.clicked.connect(self.emergency_stop)
        self.btn_panic.setEnabled(False)
        layout.addWidget(self.btn_panic)
        
        # Прогресс бар
        progress_group = QGroupBox("📊 Прогресс анализа")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(25)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ожидание запуска...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #8a8a8a;")
        progress_layout.addWidget(self.progress_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Быстрые действия
        actions_group = QGroupBox("⚡ Быстрые действия")
        actions_layout = QVBoxLayout()
        
        btn_settings = QPushButton("⚙️ Настройки")
        btn_settings.clicked.connect(self.open_settings)
        actions_layout.addWidget(btn_settings)
        
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
        layout.setSpacing(15)
        
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
        
        layout.addWidget(self.tabs)
        return widget
    
    def create_logs_tab(self) -> QWidget:
        """Создание вкладки логов."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
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
        
        # Сводная информация
        self.results_summary = QLabel("Результаты анализа появятся здесь после завершения...")
        self.results_summary.setAlignment(Qt.AlignCenter)
        self.results_summary.setFont(QFont("Segoe UI", 14))
        self.results_summary.setStyleSheet("color: #8a8a8a; padding: 50px;")
        layout.addWidget(self.results_summary)
        
        # Детальная таблица (скрыта по умолчанию)
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Параметр", "Значение"])
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_table.setVisible(False)
        layout.addWidget(self.results_table)
        
        return widget
    
    def create_ioc_quick_tab(self) -> QWidget:
        """Создание быстрой вкладки IOC."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.ioc_text = QTextEdit()
        self.ioc_text.setReadOnly(True)
        self.ioc_text.setFont(QFont("Consolas", 11))
        self.ioc_text.setPlaceholderText("Indicators of Compromise появятся здесь после анализа...")
        layout.addWidget(self.ioc_text)
        
        btn_copy_ioc = QPushButton("📋 Копировать IOC")
        btn_copy_ioc.clicked.connect(self.copy_ioc_to_clipboard)
        layout.addWidget(btn_copy_ioc)
        
        return widget
    
    def create_menu_bar(self):
        """Создание меню приложения."""
        menubar = self.menuBar()
        
        # Файл
        file_menu = menubar.addMenu("📁 Файл")
        
        open_action = QAction("📂 Открыть файл", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.select_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("❌ Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Анализ
        analysis_menu = menubar.addMenu("🔍 Анализ")
        
        start_action = QAction("🚀 Запустить анализ", self)
        start_action.setShortcut("F5")
        start_action.triggered.connect(self.start_analysis)
        analysis_menu.addAction(start_action)
        
        stop_action = QAction("🔴 Остановить", self)
        stop_action.setShortcut("F6")
        stop_action.triggered.connect(self.emergency_stop)
        analysis_menu.addAction(stop_action)
        
        # Отчеты
        reports_menu = menubar.addMenu("📊 Отчеты")
        
        view_action = QAction("👁️ Просмотреть последний отчет", self)
        view_action.triggered.connect(self.view_last_report)
        reports_menu.addAction(view_action)
        
        folder_action = QAction("📂 Открыть папку отчетов", self)
        folder_action.triggered.connect(self.open_reports_folder)
        reports_menu.addAction(folder_action)
        
        # Настройки
        settings_menu = menubar.addMenu("⚙️ Настройки")
        
        settings_action = QAction("⚙️ Параметры", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)
        
        # Справка
        help_menu = menubar.addMenu("❓ Справка")
        
        about_action = QAction("ℹ️ О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        warning_action = QAction("⚠️ Предупреждение о безопасности", self)
        warning_action.triggered.connect(self.show_security_warning)
        help_menu.addAction(warning_action)
    
    def create_tool_bar(self):
        """Создание панели инструментов."""
        toolbar = QToolBar("Главная панель")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        btn_open = QAction("📂 Открыть", self)
        btn_open.triggered.connect(self.select_file)
        toolbar.addAction(btn_open)
        
        toolbar.addSeparator()
        
        btn_analyze = QAction("🚀 Анализ", self)
        btn_analyze.triggered.connect(self.start_analysis)
        toolbar.addAction(btn_analyze)
        
        btn_stop = QAction("🔴 Стоп", self)
        btn_stop.triggered.connect(self.emergency_stop)
        toolbar.addAction(btn_stop)
        
        toolbar.addSeparator()
        
        btn_reports = QAction("📊 Отчеты", self)
        btn_reports.triggered.connect(self.open_reports_folder)
        toolbar.addAction(btn_reports)
        
        btn_settings = QAction("⚙️ Настройки", self)
        btn_settings.triggered.connect(self.open_settings)
        toolbar.addAction(btn_settings)
    
    def apply_stylesheet(self):
        """Применение таблицы стилей."""
        self.setStyleSheet(STYLESHEET)
    
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
                "⚠️ Предупреждение о безопасности",
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
            "🔴 ЭКСТРЕННАЯ ОСТАНОВКА",
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
        threat_info = result.get('threat_classification', {})
        file_info = result.get('file', {})
        
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
            ("Имя файла", file_info.get('name', 'N/A')),
            ("Размер файла", f"{file_info.get('size', 0)} байт"),
        ]
        
        for param, value in data:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            self.results_table.setItem(row, 0, QTableWidgetItem(param))
            self.results_table.setItem(row, 1, QTableWidgetItem(str(value)))
    
    def update_ioc_display(self, result: dict):
        """Обновление отображения IOC."""
        static_data = result.get('static_analysis', {})
        hashes = static_data.get('hashes', {})
        
        content = "=== INDICATORS OF COMPROMISE (IOC) ===\n\n"
        
        if hashes:
            content += "ХЕШИ ФАЙЛА:\n"
            for hash_type, hash_value in hashes.items():
                content += f"  {hash_type.upper()}: {hash_value}\n"
        
        content += "\n=========================================\n"
        content += "💡 Совет: Используйте эти IOC для поиска угроз в вашей инфраструктуре"
        
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
            self.log_message('INFO', "Настройки сохранены")
    
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
            "<h2>🛡️ RedSand Secure v2.0</h2>"
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
            "<p><b>⚠️ Внимание:</b> Запускайте только в изолированной VM!</p>"
        )
    
    def show_security_warning(self):
        """Показ предупреждения о безопасности."""
        QMessageBox.warning(
            self,
            "⚠️ Предупреждение о безопасности",
            "<h2>ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ</h2>"
            "<p>Вы используете инструмент для анализа <b>вредоносного программного обеспечения</b>.</p>"
            "<p><b>Обязательные требования:</b></p>"
            "<ul>"
            "<li>✅ Работайте ТОЛЬКО в изолированной виртуальной машине</li>"
            "<li>✅ Отключите общие папки с хост-системой</li>"
            "<li>✅ Изолируйте сеть (отключите адаптеры или используйте host-only)</li>"
            "<li>✅ Сделайте снапшот VM перед анализом</li>"
            "<li>✅ Не анализируйте образцы на рабочей машине</li>"
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
        print("❌ Ошибка: Модуль redsand_secure.py не найден!")
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
            "⚠️ Предупреждение о безопасности",
            "<h2>ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ</h2>"
            "<p>Вы запускаете инструмент для анализа <b>вредоносного ПО</b>.</p>"
            "<p><b>Запускайте ТОЛЬКО в изолированной виртуальной машине!</b></p>"
            "<p>Автор не несет ответственности за любой ущерб.</p>"
        )
    
    # Запуск цикла событий
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
