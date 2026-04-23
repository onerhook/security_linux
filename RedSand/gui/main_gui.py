#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Secure GUI v6.0 - Красивый и простой интерфейс для массового пользователя
Современный дизайн с высоким контрастом, подробной справкой и интуитивным управлением
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
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QSize, QUrl
from PyQt5.QtGui import QFont, QColor, QDesktopServices, QIcon, QPixmap


THEMES = {
    "Светлая": {
        "bg_primary": "#FFFFFF",
        "bg_secondary": "#F5F7FA",
        "bg_tertiary": "#E8ECF1",
        "accent": "#2563EB",
        "accent_hover": "#1D4ED8",
        "text_primary": "#1F2937",
        "text_secondary": "#6B7280",
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "info": "#3B82F6"
    },
    "Тёмная": {
        "bg_primary": "#1F2937",
        "bg_secondary": "#111827",
        "bg_tertiary": "#374151",
        "accent": "#3B82F6",
        "accent_hover": "#2563EB",
        "text_primary": "#F9FAFB",
        "text_secondary": "#9CA3AF",
        "success": "#34D399",
        "warning": "#FBBF24",
        "danger": "#F87171",
        "info": "#60A5FA"
    }
}

LANGUAGES = {
    "Русский": {
        "title": "RedSand Secure",
        "subtitle": "Простой анализ подозрительных файлов",
        "step1": "Шаг 1: Выберите файл",
        "step2": "Шаг 2: Настройки анализа",
        "select_file": "📁 Выбрать файл",
        "file_placeholder": "Файл еще не выбран...",
        "analysis_time": "Время анализа:",
        "seconds": "сек",
        "poly_check": "Создавать варианты файла для анализа",
        "poly_tooltip": "Помогает обнаружить сложные вирусы путем создания модификаций файла",
        "network_check": "Отключать сеть (рекомендуется)",
        "network_tooltip": "Защищает вашу сеть во время анализа вредоносного ПО",
        "analyze_btn": "🚀 ЗАПУСТИТЬ АНАЛИЗ",
        "progress": "Прогресс анализа",
        "waiting": "Ожидание запуска...",
        "settings": "⚙ Настройки",
        "reports": "📂 Отчеты",
        "logs_tab": "📋 Журнал событий",
        "results_tab": "📊 Результаты",
        "summary_tab": "🏠 Главная",
        "virus_info_tab": "🦠 О вирусе",
        "help_tab": "❓ Справка",
        "logs_placeholder": "Здесь будет отображаться ход анализа в реальном времени...",
        "results_placeholder": "Результаты анализа появятся здесь после завершения...",
        "risk_level": "Уровень угрозы",
        "virus_type": "Тип угрозы",
        "family": "Семейство вируса",
        "confidence": "Доверие к результату",
        "file_name": "Имя файла",
        "file_size": "Размер файла",
        "detection_method": "Как мы обнаружили угрозу",
        "recommendation": "Рекомендация",
        "safe": "БЕЗОПАСНО",
        "suspicious": "ПОДОЗРИТЕЛЬНО",
        "dangerous": "ОПАСНО",
        "safe_desc": "Файл не содержит известных угроз. Можно использовать.",
        "suspicious_desc": "ПОДОЗРИТЕЛЬНО, лучше не использовать. Файл содержит сомнительные элементы.",
        "dangerous_desc": "ОПАСНО! Немедленно удалите файл. Обнаружен вирус.",
        "no_threat": "Угроз не обнаружено",
        "unknown": "Неизвестно"
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
        padding: 20px 40px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 20px;
        min-width: 280px;
        min-height: 65px;
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
        padding: 14px 28px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 16px;
        min-width: 200px;
        min-height: 50px;
        max-width: 250px;
    }}
    QPushButton#actionBtn:hover {{
        background-color: {theme['accent_hover']};
    }}
    QPushButton#secondaryBtn {{
        background-color: {theme['bg_tertiary']};
        color: {theme['text_primary']};
        border: 2px solid {theme['accent']};
        padding: 12px 24px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 15px;
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
        padding: 12px 24px;
        font-weight: bold;
        font-size: 15px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        margin-right: 3px;
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
        background-color: {theme['bg_secondary']};
        border-top: 2px solid {theme['accent']};
        font-weight: normal;
        font-size: 14px;
    }}
    QTableWidget {{
        background-color: {theme['bg_primary']};
        color: {theme['text_primary']};
        border: 2px solid {theme['bg_tertiary']};
        border-radius: 12px;
        gridline-color: {theme['bg_tertiary']};
        font-size: 14px;
    }}
    QTableWidget::item {{
        padding: 10px;
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
        
        # Добавляем подробное объяснение доверия
        trust_label = QLabel("<b>Доверие к результату:</b>")
        trust_label.setStyleSheet("font-weight: bold; font-size: 15px; margin-top: 10px;")
        info_layout.addWidget(trust_label, row, 0, 1, 2)
        row += 1
        
        confidence = threat_info.get('confidence', 'Низкое')
        if confidence == 'Высокое' or confidence == 'высокое':
            trust_desc = "<span style='color: #10B981;'>✅ Высокое доверие - результат анализа очень надежен, обнаружены четкие признаки угрозы</span>"
        elif confidence == 'Среднее' or confidence == 'среднее':
            trust_desc = "<span style='color: #F59E0B;'>⚠️ Среднее доверие - есть признаки угрозы, но требуются дополнительные проверки</span>"
        else:
            trust_desc = "<span style='color: #6B7280;'>ℹ️ Низкое доверие - признаков угрозы мало, файл скорее всего безопасен</span>"
        
        trust_val = QLabel(trust_desc)
        trust_val.setStyleSheet("font-size: 14px; line-height: 1.6;")
        trust_val.setWordWrap(True)
        info_layout.addWidget(trust_val, row, 0, 1, 2)
        
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
        confidence = threat_info.get('confidence', 'Низкое')
        
        # Расшифровка уровня доверия
        confidence_explanation = ""
        if confidence == 'Высокое' or confidence == 'высокое':
            confidence_explanation = "<span style='color: #10B981; font-weight: bold;'>Высокое доверие</span> - результат анализа очень надежен, обнаружены четкие признаки угрозы"
        elif confidence == 'Среднее' or confidence == 'среднее':
            confidence_explanation = "<span style='color: #F59E0B; font-weight: bold;'>Среднее доверие</span> - есть признаки угрозы, но требуются дополнительные проверки"
        else:
            confidence_explanation = "<span style='color: #6B7280; font-weight: bold;'>Низкое доверие</span> - признаков угрозы мало, результат может быть ложноположительным"
        
        info_text = f"""
        <div style='font-size: 16px; line-height: 2.0;'>
        <b>📛 Название угрозы:</b> {virus_name}<br><br>
        <b>🧬 Семейство вирусов:</b> {virus_family}<br><br>
        <b>⚠️ Уровень опасности:</b> <span style='font-size: 18px; color: {"#EF4444" if risk_score >= 70 else "#F59E0B" if risk_score >= 40 else "#10B981"};'>{risk_score}/100</span><br><br>
        <b>🎯 Доверие к результату:</b> {confidence_explanation}<br><br>
        </div>
        """
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        virus_layout.addWidget(info_label)
        
        virus_group.setLayout(virus_layout)
        layout.addWidget(virus_group)
        
        # Что такое доверие - подробное объяснение
        trust_group = QGroupBox("❓ Что такое \"Доверие\"?")
        trust_layout = QVBoxLayout()
        trust_text = QLabel("""
        <div style='font-size: 15px; line-height: 1.8;'>
        <b>Доверие</b> - это показатель надежности результата анализа.<br><br>
        
        🔹 <b>Высокое доверие (70-100%)</b>:<br>
        • Обнаружены четкие сигнатуры известного вируса<br>
        • Поведенческий анализ подтвердил вредоносные действия<br>
        • Множественные эвристические проверки указывают на угрозу<br>
        • Можно с уверенностью считать файл опасным<br><br>
        
        🔸 <b>Среднее доверие (40-69%)</b>:<br>
        • Обнаружены подозрительные элементы, но не все проверки положительны<br>
        • Файл содержит необычный код, но не явные вирусы<br>
        • Рекомендуется дополнительная проверка в другой среде<br>
        • Может быть как угрозой, так и ложной тревогой<br><br>
        
        ⚪ <b>Низкое доверие (0-39%)</b>:<br>
        • Минимальное количество подозрительных признаков<br>
        • Скорее всего файл безопасен<br>
        • Результат может быть ложноположительным<br>
        • Стандартные меры предосторожности достаточны
        </div>
        """)
        trust_text.setWordWrap(True)
        trust_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        trust_layout.addWidget(trust_text)
        trust_group.setLayout(trust_layout)
        layout.addWidget(trust_group)
        
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
             "<b>БЕЗОПАСНО (зеленый)</b> - Файл не содержит известных угроз<br>"
             "<b>ПОДОЗРИТЕЛЬНО (желтый)</b> - Файл содержит сомнительные элементы, лучше не использовать<br>"
             "<b>ОПАСНО (красный)</b> - Обнаружен вирус, немедленно удалите файл<br><br>"
             "<b>Система оценки:</b> Программа оценивает угрозу по шкале от 0 до 100 баллов.<br>"
             "• 0-39 баллов: БЕЗОПАСНО - файл прошел все проверки<br>"
             "• 40-69 баллов: ПОДОЗРИТЕЛЬНО - есть сомнения в безопасности<br>"
             "• 70-100 баллов: ОПАСНО - обнаружены явные признаки вируса"),
            
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
        self.setWindowTitle("Настройки")
        self.setMinimumWidth(600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title_label = QLabel("⚙ Настройки программы")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Тема оформления
        theme_group = QGroupBox("🎨 Тема оформления")
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Выберите тему:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Тёмная"])
        self.theme_combo.setMinimumWidth(200)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Время анализа
        timeout_group = QGroupBox("⏱ Время анализа")
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
        
        # Дополнительные опции
        options_group = QGroupBox("🔧 Дополнительные опции")
        options_layout = QVBoxLayout()
        
        self.poly_check = QCheckBox("Создавать варианты файла для анализа")
        self.poly_check.setToolTip("Помогает обнаружить сложные вирусы путем создания модификаций файла")
        options_layout.addWidget(self.poly_check)
        
        self.network_check = QCheckBox("Отключать сеть во время анализа (рекомендуется)")
        self.network_check.setChecked(True)
        self.network_check.setToolTip("Защищает вашу сеть от потенциальной угрозы")
        options_layout.addWidget(self.network_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Справка
        help_group = QGroupBox("❓ Справка по настройкам")
        help_layout = QVBoxLayout()
        help_text = QLabel(
            "<b>Как использовать настройки:</b><br><br>"
            "<b>Тема оформления:</b> Выберите удобный для вас визуальный стиль интерфейса<br>"
            "<b>Время анализа:</b> Максимальное время проверки одного файла (по умолчанию 60 сек)<br>"
            "<b>Создавать варианты файла:</b> Генерирует модификации файла для лучшего обнаружения сложных угроз<br>"
            "<b>Отключать сеть:</b> Защищает вашу локальную сеть во время анализа вредоносного ПО (рекомендуется всегда включать)<br><br>"
            "<b style='color: #EF4444;'>ВАЖНО:</b> Запускайте анализ только в изолированной виртуальной машине!"
        )
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

    def get_settings(self):
        return {
            'timeout': self.timeout_spin.value(),
            'use_poly_default': self.poly_check.isChecked(),
            'auto_disable_network': self.network_check.isChecked(),
            'theme': self.theme_combo.currentText()
        }


class RedSandSecureGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker_thread: Optional[QThread] = None
        self.worker: Optional[AnalysisWorker] = None
        self.current_report: Optional[dict] = None
        self.analysis_completed = False  # Флаг завершения анализа
        self.settings = {
            'timeout': 60, 'output_dir': 'reports', 'use_poly_default': False,
            'auto_disable_network': True, 'log_level': 'INFO', 'theme': 'Тёмная'
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
        # Убран подзаголовок для упрощения интерфейса
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
        # Кнопки настроек и отчетов убраны для упрощения интерфейса
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
        self.analysis_completed = True  # Устанавливаем флаг завершения
        self.set_ui_enabled(True)
        self.progress_bar.setValue(100)
        self.progress_label.setText("Анализ завершен успешно!")
        self.update_results_display(result)
        self.log_message('SUCCESS', "Анализ завершен успешно!")
        self.status_bar.showMessage("Анализ завершен")
        if result:
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
        try:
            dialog = SettingsDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                settings = dialog.get_settings()
                old_theme = self.settings.get('theme', 'Светлая')
                self.settings.update(settings)
                self.save_settings()
                
                # Если тема изменилась, применяем новую
                new_theme = self.settings.get('theme', 'Светлая')
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

    def set_ui_enabled(self, enabled: bool):
        self.btn_analyze.setEnabled(enabled)
        self.file_path_edit.setEnabled(enabled)
        self.timeout_spin.setEnabled(enabled)
        self.poly_check.setEnabled(enabled)
        self.network_check.setEnabled(enabled)

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
