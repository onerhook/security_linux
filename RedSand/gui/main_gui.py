#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Secure GUI v5.0 - Максимально упрощенный интерфейс
Минималистичный дизайн с высоким контрастом для людей, не разбирающихся в компьютерах
Запускать ТОЛЬКО в изолированной виртуальной машине!
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
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QSize, QUrl
from PyQt5.QtGui import QFont, QColor, QDesktopServices

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.orchestrator import RedSandSecure
    REDSAND_AVAILABLE = True
except ImportError:
    REDSAND_AVAILABLE = False


THEMES = {
    "High Contrast": {
        "bg_primary": "#FFFFFF",
        "bg_secondary": "#F0F0F0",
        "bg_tertiary": "#E0E0E0",
        "accent": "#0066CC",
        "accent_hover": "#0052A3",
        "text_primary": "#000000",
        "text_secondary": "#333333",
        "success": "#008000",
        "warning": "#FF8C00",
        "danger": "#CC0000",
        "info": "#0066CC"
    }
}


def generate_stylesheet(theme_name: str = "High Contrast") -> str:
    theme = THEMES.get(theme_name, THEMES["High Contrast"])
    return f"""
    QMainWindow, QDialog {{
        background-color: {theme['bg_primary']};
        color: {theme['text_primary']};
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 18px;
    }}
    QPushButton#primaryBtn {{
        background-color: {theme['success']};
        color: #FFFFFF;
        border: 3px solid {theme['success']};
        padding: 24px 50px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 22px;
        min-width: 300px;
        min-height: 70px;
    }}
    QPushButton#primaryBtn:hover {{
        background-color: #00A000;
    }}
    QPushButton#primaryBtn:disabled {{
        background-color: {theme['bg_tertiary']};
    }}
    QPushButton#actionBtn {{
        background-color: {theme['accent']};
        color: #FFFFFF;
        border: 3px solid {theme['accent']};
        padding: 16px 32px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 18px;
        min-width: 200px;
        min-height: 55px;
    }}
    QPushButton#actionBtn:hover {{
        background-color: {theme['accent_hover']};
    }}
    QGroupBox {{
        background-color: {theme['bg_secondary']};
        border: 3px solid {theme['accent']};
        border-radius: 12px;
        margin-top: 20px;
        padding-top: 20px;
        font-weight: bold;
        font-size: 18px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 20px;
        color: {theme['accent']};
    }}
    QTabWidget::pane {{
        border: 3px solid {theme['accent']};
        border-radius: 12px;
    }}
    QTabBar::tab {{
        background-color: {theme['bg_tertiary']};
        color: {theme['text_primary']};
        padding: 16px 32px;
        font-weight: bold;
        font-size: 17px;
    }}
    QTabBar::tab:selected {{
        background-color: {theme['accent']};
        color: #FFFFFF;
    }}
    QTextEdit {{
        background-color: {theme['bg_primary']};
        color: {theme['text_primary']};
        border: 3px solid {theme['bg_tertiary']};
        border-radius: 10px;
        padding: 16px;
        font-family: 'Consolas', monospace;
        font-size: 16px;
    }}
    QProgressBar {{
        background-color: {theme['bg_tertiary']};
        border: 3px solid {theme['accent']};
        border-radius: 12px;
        height: 40px;
        font-weight: bold;
        font-size: 18px;
    }}
    QProgressBar::chunk {{
        background-color: {theme['success']};
    }}
    QComboBox, QSpinBox, QLineEdit {{
        background-color: {theme['bg_primary']};
        color: {theme['text_primary']};
        border: 3px solid {theme['accent']};
        border-radius: 10px;
        padding: 14px;
        font-size: 17px;
        font-weight: bold;
        min-height: 50px;
    }}
    QCheckBox {{
        color: {theme['text_primary']};
        font-size: 17px;
        font-weight: bold;
    }}
    QLabel {{
        color: {theme['text_primary']};
        font-size: 17px;
    }}
    QLabel#titleLabel {{
        font-size: 36px;
        font-weight: bold;
        color: {theme['accent']};
        padding: 20px;
    }}
    QLabel#subtitleLabel {{
        font-size: 20px;
        color: {theme['text_secondary']};
    }}
    QStatusBar {{
        background-color: {theme['bg_secondary']};
        border-top: 3px solid {theme['accent']};
        font-weight: bold;
    }}
    """


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
        if not REDSAND_AVAILABLE:
            self.error.emit("Модуль RedSand Secure не найден")
            return
        try:
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


class SimpleReportDialog(QDialog):
    def __init__(self, report_data: dict, parent=None):
        super().__init__(parent)
        self.report_data = report_data
        self.setWindowTitle("Результаты анализа")
        self.setMinimumSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        title_label = QLabel("Результаты анализа")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        tabs = QTabWidget()
        summary_widget = self.create_summary_tab()
        tabs.addTab(summary_widget, "Главное")
        hashes_widget = self.create_hashes_tab()
        tabs.addTab(hashes_widget, "Хеши файла")
        layout.addWidget(tabs)
        btn_close = QPushButton("Закрыть")
        btn_close.setObjectName("actionBtn")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def create_summary_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        threat_info = self.report_data.get('threat_info') or {}
        if not isinstance(threat_info, dict):
            threat_info = {}
        risk_score = threat_info.get('risk_score', 0)
        threat_type = threat_info.get('type', 'Неизвестно')
        family = threat_info.get('family', 'Неизвестно')
        if risk_score >= 70:
            risk_color, risk_text = "#CC0000", "ОПАСНО"
        elif risk_score >= 40:
            risk_color, risk_text = "#FF8C00", "ПОДОЗРИТЕЛЬНО"
        else:
            risk_color, risk_text = "#008000", "БЕЗОПАСНО"
        risk_group = QGroupBox("Уровень угрозы")
        risk_layout = QVBoxLayout()
        risk_label = QLabel(f"{risk_text} ({risk_score}/100)")
        risk_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {risk_color};")
        risk_label.setAlignment(Qt.AlignCenter)
        risk_layout.addWidget(risk_label)
        risk_group.setLayout(risk_layout)
        layout.addWidget(risk_group)
        type_group = QGroupBox("Тип угрозы")
        type_layout = QVBoxLayout()
        type_label = QLabel(f"{threat_type}")
        type_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        type_label.setAlignment(Qt.AlignCenter)
        type_layout.addWidget(type_label)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        family_group = QGroupBox("Семейство")
        family_layout = QVBoxLayout()
        family_label = QLabel(f"{family}")
        family_label.setStyleSheet("font-size: 20px;")
        family_label.setAlignment(Qt.AlignCenter)
        family_layout.addWidget(family_label)
        family_group.setLayout(family_layout)
        layout.addWidget(family_group)
        layout.addStretch()
        return widget

    def create_hashes_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        static_data = self.report_data.get('static_results') or {}
        hashes = static_data.get('hashes', {}) if static_data else {}
        if hashes:
            for hash_type, hash_value in hashes.items():
                hash_group = QGroupBox(hash_type.upper())
                hash_layout = QVBoxLayout()
                hash_label = QLabel(hash_value)
                hash_label.setStyleSheet("font-size: 16px; font-family: 'Consolas', monospace;")
                hash_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                hash_layout.addWidget(hash_label)
                hash_group.setLayout(hash_layout)
                layout.addWidget(hash_group)
        else:
            info_label = QLabel("Хеши не найдены")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("font-size: 20px; color: #888;")
            layout.addWidget(info_label)
        layout.addStretch()
        return widget


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        title_label = QLabel("Настройки")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        timeout_group = QGroupBox("Время анализа")
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Максимальное время:"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(60)
        self.timeout_spin.setMinimumWidth(100)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addWidget(QLabel("сек"))
        timeout_layout.addStretch()
        timeout_group.setLayout(timeout_layout)
        layout.addWidget(timeout_group)
        self.poly_check = QCheckBox("Генерировать варианты вируса для анализа")
        self.poly_check.setToolTip("Создает модификации файла для лучшего обнаружения")
        layout.addWidget(self.poly_check)
        self.network_check = QCheckBox("Отключать сеть во время анализа")
        self.network_check.setChecked(True)
        self.network_check.setToolTip("Защищает вашу сеть от потенциальной угрозы")
        layout.addWidget(self.network_check)
        help_group = QGroupBox("Справка")
        help_layout = QVBoxLayout()
        help_text = QLabel(
            "<b>Как использовать:</b><br><br>"
            "1. Нажмите 'Выбрать файл' и укажите подозрительный файл<br>"
            "2. Нажмите 'ЗАПУСТИТЬ АНАЛИЗ'<br>"
            "3. Дождитесь завершения анализа<br>"
            "4. Изучите результаты в окне отчета<br><br>"
            "<b>Важно:</b> Запускайте только в виртуальной машине!"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("font-size: 16px; line-height: 1.6;")
        help_layout.addWidget(help_text)
        help_group.setLayout(help_layout)
        layout.addWidget(help_group)
        layout.addStretch()
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setFixedHeight(55)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_settings(self):
        return {
            'timeout': self.timeout_spin.value(),
            'use_poly_default': self.poly_check.isChecked(),
            'auto_disable_network': self.network_check.isChecked()
        }


class RedSandSecureGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker_thread: Optional[QThread] = None
        self.worker: Optional[AnalysisWorker] = None
        self.current_report: Optional[dict] = None
        self.settings = {
            'timeout': 60, 'output_dir': 'reports', 'use_poly_default': False,
            'auto_disable_network': True, 'log_level': 'INFO', 'theme': 'High Contrast'
        }
        self.setup_ui()
        self.apply_stylesheet()
        self.load_settings()

    def setup_ui(self):
        self.setWindowTitle("RedSand Secure - Анализ файлов")
        self.setMinimumSize(1000, 700)
        self.resize(1100, 750)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        title_label = QLabel("RedSand Secure")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        subtitle_label = QLabel("Простой анализ подозрительных файлов")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle_label)
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
        self.status_bar.showMessage("Готов к работе. Выберите файл для анализа.")

    def create_left_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        file_group = QGroupBox("Шаг 1: Выберите файл")
        file_layout = QVBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Файл еще не выбран...")
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setMinimumHeight(50)
        file_layout.addWidget(self.file_path_edit)
        btn_select_file = QPushButton("📁 Выбрать файл")
        btn_select_file.setObjectName("actionBtn")
        btn_select_file.clicked.connect(self.select_file)
        file_layout.addWidget(btn_select_file)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        settings_group = QGroupBox("Шаг 2: Настройки (необязательно)")
        settings_layout = QVBoxLayout()
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Время анализа:"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(60)
        self.timeout_spin.setMinimumWidth(80)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addWidget(QLabel("сек"))
        timeout_layout.addStretch()
        settings_layout.addLayout(timeout_layout)
        self.poly_check = QCheckBox("Создавать варианты файла для анализа")
        self.poly_check.setToolTip("Помогает обнаружить сложные вирусы")
        settings_layout.addWidget(self.poly_check)
        self.network_check = QCheckBox("Отключать сеть (рекомендуется)")
        self.network_check.setChecked(True)
        self.network_check.setToolTip("Защищает вашу сеть во время анализа")
        settings_layout.addWidget(self.network_check)
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        self.btn_analyze = QPushButton("🚀 ЗАПУСТИТЬ АНАЛИЗ")
        self.btn_analyze.setObjectName("primaryBtn")
        self.btn_analyze.clicked.connect(self.start_analysis)
        layout.addWidget(self.btn_analyze)
        progress_group = QGroupBox("Прогресс")
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(35)
        progress_layout.addWidget(self.progress_bar)
        self.progress_label = QLabel("Ожидание...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #666; font-size: 16px;")
        progress_layout.addWidget(self.progress_label)
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        actions_layout = QHBoxLayout()
        btn_settings = QPushButton("⚙ Настройки")
        btn_settings.setObjectName("actionBtn")
        btn_settings.clicked.connect(self.open_settings)
        actions_layout.addWidget(btn_settings)
        btn_reports = QPushButton("📂 Отчеты")
        btn_reports.setObjectName("actionBtn")
        btn_reports.clicked.connect(self.open_reports_folder)
        actions_layout.addWidget(btn_reports)
        layout.addLayout(actions_layout)
        layout.addStretch()
        return widget

    def create_right_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        self.tabs = QTabWidget()
        logs_widget = self.create_logs_tab()
        self.tabs.addTab(logs_widget, "📋 Журнал событий")
        results_widget = self.create_results_tab()
        self.tabs.addTab(results_widget, "📊 Результаты")
        layout.addWidget(self.tabs)
        return widget

    def create_logs_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 14))
        self.log_text.setPlaceholderText("Здесь будет отображаться ход анализа...")
        layout.addWidget(self.log_text)
        return widget

    def create_results_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.results_summary = QLabel("Результаты анализа появятся здесь после завершения...")
        self.results_summary.setAlignment(Qt.AlignCenter)
        self.results_summary.setFont(QFont("Segoe UI", 16))
        self.results_summary.setStyleSheet("color: #666; padding: 50px;")
        layout.addWidget(self.results_summary)
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Параметр", "Значение"])
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
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
        reply = QMessageBox.question(
            self, "Предупреждение о безопасности",
            "Вы запускаете анализ потенциально опасного файла!\n\n"
            "Убедитесь, что вы работаете в виртуальной машине.\n\nПродолжить?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
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
        self.set_ui_enabled(True)
        self.progress_bar.setValue(100)
        self.progress_label.setText("Анализ завершен успешно!")
        self.update_results_display(result)
        self.log_message('SUCCESS', "Анализ завершен успешно!")
        self.status_bar.showMessage("Анализ завершен")
        if result:
            dialog = SimpleReportDialog(result, self)
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

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            settings = dialog.get_settings()
            self.settings.update(settings)
            self.save_settings()
            self.log_message('INFO', "Настройки сохранены")

    def open_reports_folder(self):
        reports_dir = Path(self.settings.get('output_dir', 'reports'))
        reports_dir.mkdir(exist_ok=True)
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(reports_dir.absolute())))
        except Exception as e:
            self.log_message('ERROR', f"Ошибка открытия папки: {e}")
            QMessageBox.warning(self, "Предупреждение", f"Не удалось открыть папку.\nПуть: {reports_dir.absolute()}")

    def set_ui_enabled(self, enabled: bool):
        self.btn_analyze.setEnabled(enabled)
        self.file_path_edit.setEnabled(enabled)
        self.timeout_spin.setEnabled(enabled)
        self.poly_check.setEnabled(enabled)
        self.network_check.setEnabled(enabled)

    def closeEvent(self, event):
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.warning(
                self, "Анализ выполняется",
                "Анализ все еще выполняется. Вы уверены, что хотите выйти?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
            self.worker_thread.terminate()
            self.worker_thread.wait(3000)
        event.accept()


def main():
    if not REDSAND_AVAILABLE:
        print("Ошибка: Модуль redsand_secure.py не найден!")
        sys.exit(1)
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
