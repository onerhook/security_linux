#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Образовательный симулятор антивируса с расширенным функционалом.
ВНИМАНИЕ: Это только симуляция для учебных целей. Не содержит реального вредоносного кода.
"""

import sys
import random
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QProgressBar, 
                             QTextEdit, QTabWidget, QListWidget, QListWidgetItem,
                             QMessageBox, QGroupBox, QGridLayout, QScrollArea,
                             QFrame, QSplitter, QCheckBox, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QColor, QIcon

# Расширенный список фейковых угроз (25 типов)
FAKE_VIRUSES = [
    {"name": "Trojan.Win32.Generic", "type": "Троян", "severity": "Высокая", 
     "description": "Кража данных, удаленный доступ к системе"},
    {"name": "Worm.Autorun", "type": "Червь", "severity": "Средняя", 
     "description": "Автозапуск через съемные носители, распространение по сети"},
    {"name": "Ransomware.CryptoLocker", "type": "Вымогатель", "severity": "Критическая", 
     "description": "Шифрование файлов с требованием выкупа"},
    {"name": "Spyware.Keylogger", "type": "Шпион", "severity": "Высокая", 
     "description": "Запись нажатий клавиш для кражи паролей"},
    {"name": "Adware.BrowserHijacker", "type": "Рекламный", "severity": "Низкая", 
     "description": "Перенаправление браузера на рекламные сайты"},
    {"name": "Rootkit.Bootkit", "type": "Руткит", "severity": "Критическая", 
     "description": "Скрытие в загрузочном секторе, глубокая интеграция в ОС"},
    {"name": "Backdoor.RemoteAccess", "type": "Бэкдор", "severity": "Высокая", 
     "description": "Удаленное управление системой злоумышленником"},
    {"name": "Virus.FileInfector", "type": "Вирус", "severity": "Средняя", 
     "description": "Заражение исполняемых файлов"},
    {"name": "PUP.OptionalToolbar", "type": "Потенциально нежелательная программа", "severity": "Низкая", 
     "description": "Установка панелей инструментов без согласия"},
    {"name": "Exploit.CVE-2023-1234", "type": "Эксплойт", "severity": "Высокая", 
     "description": "Использование уязвимости в ПО"},
    {"name": "Miner.CoinHive", "type": "Майнер", "severity": "Средняя", 
     "description": "Скрытый майнинг криптовалюты"},
    {"name": "Phishing.FakeBank", "type": "Фишинг", "severity": "Высокая", 
     "description": "Поддельные страницы банков для кражи данных"},
    {"name": "Botnet.Mirai", "type": "Ботнет", "severity": "Критическая", 
     "description": "Включение устройства в сеть зомби"},
    {"name": "Rogue.Antivirus", "type": "Лжеантивирус", "severity": "Средняя", 
     "description": "Фальшивые сообщения о вирусах для вымогательства"},
    {"name": "Dialer.PremiumSMS", "type": "Дилер", "severity": "Средняя", 
     "description": "Отправка платных SMS без ведома пользователя"},
    {"name": "Hoax.FakeAlert", "type": "Мистификация", "severity": "Низкая", 
     "description": "Ложные предупреждения о заражении"},
    {"name": "Joke.ScreenFreeze", "type": "Шутка", "severity": "Низкая", 
     "description": "Безобидные шутки над пользователем"},
    {"name": "LogicBomb.TimeTrigger", "type": "Логическая бомба", "severity": "Высокая", 
     "description": "Активация по времени или событию"},
    {"name": "Macro.WordMacro", "type": "Макровирус", "severity": "Средняя", 
     "description": "Заражение документов Office"},
    {"name": "Script.VBSDownloader", "type": "Скрипт", "severity": "Средняя", 
     "description": "Загрузка дополнительного вредоносного ПО"},
    {"name": "Polymorphic.Mutation", "type": "Полиморфный", "severity": "Высокая", 
     "description": "Изменение кода для обхода обнаружения"},
    {"name": "Fileless.PowerShell", "type": "Бесфайловый", "severity": "Критическая", 
     "description": "Работа через системные утилиты без файлов"},
    {"name": "SupplyChain.Backdoor", "type": "Цепочка поставок", "severity": "Критическая", 
     "description": "Заражение через легитимное ПО"},
    {"name": "Trojan.Banker", "type": "Банковский троян", "severity": "Критическая", 
     "description": "Кража банковских данных и платежной информации"},
    {"name": "Worm.Conficker", "type": "Сетевой червь", "severity": "Высокая", 
     "description": "Массовое распространение через уязвимости Windows"},
    {"name": "Ransomware.WannaCry", "type": "Вымогатель-червь", "severity": "Критическая", 
     "description": "Глобальная эпидемия, шифрование и самораспространение"},
    {"name": "Spyware.Stalkerware", "type": "Стаalkerware", "severity": "Высокая", 
     "description": "Слежка за пользователем, перехват сообщений и звонков"},
    {"name": "Adware.CoinMiner", "type": "Рекламный майнер", "severity": "Средняя", 
     "description": "Майнинг через браузер с навязчивой рекламой"},
]

class ScanWorker(QThread):
    """Поток для симуляции сканирования"""
    progress_signal = pyqtSignal(int)
    found_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal()
    log_signal = pyqtSignal(str)
    
    def __init__(self, viruses_count=0):
        super().__init__()
        self.viruses_count = viruses_count
        self._stop = False
        
    def run(self):
        total_steps = 100
        found_count = 0
        
        for i in range(total_steps):
            if self._stop:
                break
                
            time.sleep(0.05)  # Симуляция работы
            self.progress_signal.emit(i + 1)
            
            # Случайное обнаружение угроз
            if random.random() < 0.15 and found_count < self.viruses_count:
                virus = random.choice(FAKE_VIRUSES)
                self.found_signal.emit(virus)
                self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] Обнаружено: {virus['name']}")
                found_count += 1
                
            # Логирование процесса
            if i % 10 == 0:
                folders = ["C:\\Windows\\System32", "C:\\Program Files", "C:\\Users", 
                          "D:\\Documents", "E:\\Backup", "F:\\Games", "G:\\Media"]
                folder = random.choice(folders)
                self.log_signal.emit(f"Сканирование: {folder}...")
        
        self.log_signal.emit("Сканирование завершено!")
        self.finished_signal.emit()
    
    def stop(self):
        self._stop = True


class RealTimeProtection(QObject):
    """Симуляция защиты в реальном времени"""
    threat_detected = pyqtSignal(dict)
    log_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.enabled = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_threats)
        
    def start(self):
        self.enabled = True
        self.timer.start(3000)  # Проверка каждые 3 секунды
        self.log_message.emit("Защита в реальном времени включена")
        
    def stop(self):
        self.enabled = False
        self.timer.stop()
        self.log_message.emit("Защита в реальном времени выключена")
        
    def check_threats(self):
        if not self.enabled:
            return
            
        # 20% шанс обнаружения угрозы
        if random.random() < 0.2:
            virus = random.choice(FAKE_VIRUSES)
            self.threat_detected.emit(virus)
            self.log_message.emit(f"Блокирована попытка запуска: {virus['name']}")


class EducationWindow(QDialog):
    """Окно с образовательной информацией"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Образовательный раздел - Теория вирусов")
        self.setMinimumSize(900, 700)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Типы вредоносного программного обеспечения")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Создаем прокручиваемую область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        
        # Информация по типам угроз
        types_info = [
            ("Трояны (Trojans)", "Программы, маскирующиеся под легитимное ПО, но выполняющие вредоносные действия. Не размножаются самостоятельно. Крадут данные, открывают доступ к системе."),
            ("Черви (Worms)", "Самовоспроизводящиеся программы, распространяющиеся по сетям без участия пользователя. Используют уязвимости ОС и почты."),
            ("Вирусы-вымогатели (Ransomware)", "Шифруют файлы пользователя и требуют выкуп за расшифровку. Часто распространяются через фишинг и уязвимости."),
            ("Шпионское ПО (Spyware)", "Тайно собирают информацию о действиях пользователя: пароли, историю браузера, данные карт, переписку."),
            ("Рекламное ПО (Adware)", "Навязчивая реклама, перенаправление на рекламные сайты, замедление системы. Часто устанавливается с бесплатным ПО."),
            ("Руткиты (Rootkits)", "Скрывают свое присутствие в системе, предоставляют привилегированный доступ злоумышленнику. Внедряются глубоко в ОС."),
            ("Бэкдоры (Backdoors)", "Обходят стандартную аутентификацию для удаленного доступа к системе. Позволяют злоумышленнику полный контроль."),
            ("Ботнеты (Botnets)", "Сети зараженных компьютеров, управляемые злоумышленником для DDoS-атак, рассылки спама, майнинга."),
            ("Эксплойты (Exploits)", "Используют уязвимости в программном обеспечении для проникновения. Часто нацелены на браузеры и плагины."),
            ("Майнеры (Miners)", "Используют ресурсы компьютера для добычи криптовалюты без согласия владельца. Замедляют систему, увеличивают потребление энергии."),
            ("Фишинг (Phishing)", "Поддельные письма и сайты для кражи конфиденциальной информации. Имитируют банки, соцсети, популярные сервисы."),
            ("Лжеантивирусы (Rogue AV)", "Фальшивые программы безопасности, вымогающие деньги за 'лечение' несуществующих угроз. Блокируют систему."),
            ("Макровирусы (Macro Viruses)", "Заражают документы Office через макросы. Активируются при открытии файла с включенными макросами."),
            ("Бесфайловые вирусы (Fileless)", "Работают через системные утилиты (PowerShell, WMI) без создания файлов. Сложно обнаружить традиционными методами."),
            ("Полиморфные вирусы", "Изменяют свой код при каждом заражении для обхода сигнатурного анализа. Используют шифрование и мутацию."),
            ("Логические бомбы", "Активируются по времени или событию. Могут долго оставаться незамеченными перед нанесением ущерба."),
        ]
        
        for title_text, description in types_info:
            group = QGroupBox(title_text)
            group_layout = QVBoxLayout()
            label = QLabel(description)
            label.setWordWrap(True)
            label.setFont(QFont("Arial", 10))
            group_layout.addWidget(label)
            group.setLayout(group_layout)
            content_layout.addWidget(group)
        
        # Меры защиты
        protection_group = QGroupBox("Меры защиты от вирусов")
        protection_layout = QVBoxLayout()
        protection_text = QLabel(
            "✅ Регулярно обновляйте ОС и все программы\n"
            "✅ Используйте надежные антивирусы и брандмауэры\n"
            "✅ Не открывайте подозрительные вложения и ссылки\n"
            "✅ Делайте резервные копии важных данных (правило 3-2-1)\n"
            "✅ Используйте сложные уникальные пароли и 2FA\n"
            "✅ Будьте осторожны с публичным Wi-Fi (используйте VPN)\n"
            "✅ Проверяйте USB-накопители перед использованием\n"
            "✅ Ограничьте права пользователей в системе\n"
            "✅ Отключите автозапуск съемных носителей\n"
            "✅ Обучайте сотрудников основам кибербезопасности"
        )
        protection_text.setWordWrap(True)
        protection_text.setFont(QFont("Arial", 10))
        protection_layout.addWidget(protection_text)
        protection_group.setLayout(protection_layout)
        content_layout.addWidget(protection_group)
        
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.setFont(QFont("Arial", 12))
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


class ThreatInfoDialog(QDialog):
    """Диалог с детальной информацией об угрозе"""
    def __init__(self, virus_data, parent=None):
        super().__init__(parent)
        self.virus = virus_data
        self.setWindowTitle(f"Информация: {virus_data['name']}")
        self.setMinimumSize(600, 500)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Название
        name_label = QLabel(self.virus['name'])
        name_label.setFont(QFont("Arial", 20, QFont.Bold))
        name_label.setStyleSheet("color: #c0392b;")
        layout.addWidget(name_label)
        
        # Тип и уровень
        info_layout = QHBoxLayout()
        
        type_label = QLabel(f"Тип: {self.virus['type']}")
        type_label.setFont(QFont("Arial", 14))
        info_layout.addWidget(type_label)
        
        severity_label = QLabel(f"Уровень: {self.virus['severity']}")
        severity_label.setFont(QFont("Arial", 14, QFont.Bold))
        if self.virus['severity'] == "Критическая":
            severity_label.setStyleSheet("color: red; background-color: #ffebee; padding: 5px;")
        elif self.virus['severity'] == "Высокая":
            severity_label.setStyleSheet("color: orange; background-color: #fff3e0; padding: 5px;")
        elif self.virus['severity'] == "Средняя":
            severity_label.setStyleSheet("color: darkorange; background-color: #ffe0b2; padding: 5px;")
        else:
            severity_label.setStyleSheet("color: green; background-color: #e8f5e9; padding: 5px;")
        info_layout.addWidget(severity_label)
        
        layout.addLayout(info_layout)
        
        # Описание
        desc_group = QGroupBox("📋 Описание угрозы")
        desc_layout = QVBoxLayout()
        desc_text = QLabel(self.virus['description'])
        desc_text.setWordWrap(True)
        desc_text.setFont(QFont("Arial", 12))
        desc_text.setStyleSheet("padding: 10px;")
        desc_layout.addWidget(desc_text)
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # Симптомы заражения
        symptoms_group = QGroupBox("⚠️ Возможные симптомы заражения")
        symptoms_layout = QVBoxLayout()
        symptoms = [
            "• Замедление работы системы",
            "• Необычная активность диска/сети",
            "• Всплывающие окна рекламы",
            "• Изменение домашней страницы браузера",
            "• Блокировка антивируса",
            "• Исчезновение или шифрование файлов",
            "• Странное поведение программ"
        ]
        symptoms_text = QLabel("\n".join(symptoms))
        symptoms_text.setWordWrap(True)
        symptoms_text.setFont(QFont("Arial", 11))
        symptoms_layout.addWidget(symptoms_text)
        symptoms_group.setLayout(symptoms_layout)
        layout.addWidget(symptoms_group)
        
        # Рекомендации
        rec_group = QGroupBox("🛡️ Рекомендации по удалению")
        rec_layout = QVBoxLayout()
        rec_text = QLabel(
            "1. Немедленно изолируйте устройство от сети (отключите Wi-Fi/Ethernet)\n"
            "2. Запустите полное сканирование системы антивирусом\n"
            "3. Удалите найденные угрозы через карантин\n"
            "4. Обновите базы сигнатур антивируса до последней версии\n"
            "5. Проверьте автозагрузку на наличие подозрительных программ\n"
            "6. Смените все пароли с другого устройства\n"
            "7. Восстановите файлы из резервной копии при необходимости\n"
            "8. Обратитесь к специалисту при серьезном заражении"
        )
        rec_text.setWordWrap(True)
        rec_text.setFont(QFont("Arial", 11))
        rec_layout.addWidget(rec_text)
        rec_group.setLayout(rec_layout)
        layout.addWidget(rec_group)
        
        # Кнопки
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok)
        btn_box.accepted.connect(self.accept)
        btn_box.setStyleSheet("padding: 10px;")
        layout.addWidget(btn_box)
        
        self.setLayout(layout)


class AntivirusSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.detected_viruses = []
        self.scan_worker = None
        self.real_time_protection = RealTimeProtection()
        self.scan_count = 0
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        self.setWindowTitle("🛡️ EduAntivirus Pro - Образовательный симулятор безопасности")
        self.setGeometry(100, 100, 1400, 900)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        
        # Заголовок
        header = QLabel("🛡️ EduAntivirus Pro - Образовательный симулятор кибербезопасности")
        header.setFont(QFont("Arial", 22, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #2c3e50; padding: 15px; background-color: #ecf0f1; border-radius: 10px;")
        main_layout.addWidget(header)
        
        # Табы
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 12))
        main_layout.addWidget(self.tabs)
        
        # Вкладка 1: Мониторинг
        self.monitoring_tab = self.create_monitoring_tab()
        self.tabs.addTab(self.monitoring_tab, "📊 Мониторинг и сканирование")
        
        # Вкладка 2: Угрозы
        self.threats_tab = self.create_threats_tab()
        self.tabs.addTab(self.threats_tab, f"⚠️ Угрозы ({len(self.detected_viruses)})")
        
        # Вкладка 3: Образование
        self.education_tab = self.create_education_tab()
        self.tabs.addTab(self.education_tab, "📚 Теория и обучение")
        
        # Статус бар
        self.statusBar().setStyleSheet("background-color: #34495e; color: white; padding: 5px; font-size: 12px;")
        self.statusBar().showMessage("Готов к работе | Защита в реальном времени: ВЫКЛ")
        
    def create_monitoring_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Панель управления
        control_group = QGroupBox("🎛️ Управление сканированием")
        control_group.setFont(QFont("Arial", 13, QFont.Bold))
        control_layout = QGridLayout()
        control_layout.setSpacing(10)
        
        self.scan_btn = QPushButton("🔍 Начать полное сканирование")
        self.scan_btn.setFont(QFont("Arial", 13))
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white; 
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        control_layout.addWidget(self.scan_btn, 0, 0)
        
        self.stop_btn = QPushButton("⏹️ Остановить сканирование")
        self.stop_btn.setFont(QFont("Arial", 13))
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; 
                color: white; 
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        control_layout.addWidget(self.stop_btn, 0, 1)
        
        self.generate_btn = QPushButton("🦠 Сгенерировать тестовые угрозы")
        self.generate_btn.setFont(QFont("Arial", 13))
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6; 
                color: white; 
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        control_layout.addWidget(self.generate_btn, 1, 0, 1, 2)
        
        # Защита в реальном времени
        self.protection_checkbox = QCheckBox("🛡️ Защита в реальном времени (вкл/выкл)")
        self.protection_checkbox.setFont(QFont("Arial", 13))
        self.protection_checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 10px;
                padding: 5px;
            }
            QCheckBox:checked {
                color: #27ae60;
                font-weight: bold;
            }
        """)
        self.protection_checkbox.stateChanged.connect(self.toggle_real_time_protection)
        control_layout.addWidget(self.protection_checkbox, 2, 0, 1, 2)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Прогресс и статус
        progress_group = QGroupBox("📈 Прогресс сканирования")
        progress_group.setFont(QFont("Arial", 13, QFont.Bold))
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                text-align: center;
                font-size: 14px;
                font-weight: bold;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ecc71, stop:1 #27ae60);
                border-radius: 5px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Статус: ⏸️ Ожидание запуска")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border-radius: 5px;")
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Журнал событий
        log_group = QGroupBox("📝 Журнал событий")
        log_group.setFont(QFont("Arial", 13, QFont.Bold))
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier New", 10))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50; 
                color: #2ecc71; 
                padding: 10px;
                border-radius: 5px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        return widget
    
    def create_threats_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок
        header = QLabel("☣️ Список обнаруженных угроз")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #c0392b; padding: 10px;")
        layout.addWidget(header)
        
        # Список угроз
        self.virus_list = QListWidget()
        self.virus_list.setFont(QFont("Arial", 11))
        self.virus_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        self.virus_list.itemDoubleClicked.connect(self.show_threat_details)
        layout.addWidget(self.virus_list)
        
        # Кнопки действий
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.quarantine_btn = QPushButton("🗑️ Удалить выбранные")
        self.quarantine_btn.setFont(QFont("Arial", 12))
        self.quarantine_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; 
                color: white; 
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.quarantine_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(self.quarantine_btn)
        
        self.clear_all_btn = QPushButton("🧹 Очистить всё")
        self.clear_all_btn.setFont(QFont("Arial", 12))
        self.clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6; 
                color: white; 
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.clear_all_btn.clicked.connect(self.clear_all_threats)
        btn_layout.addWidget(self.clear_all_btn)
        
        layout.addLayout(btn_layout)
        
        # Статистика
        stats_group = QGroupBox("📊 Детальная статистика угроз")
        stats_group.setFont(QFont("Arial", 13, QFont.Bold))
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        self.total_label = QLabel("📌 Всего обнаружено: 0")
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        stats_layout.addWidget(self.total_label, 0, 0)
        
        self.critical_label = QLabel("🔴 Критические: 0")
        self.critical_label.setFont(QFont("Arial", 12))
        self.critical_label.setStyleSheet("color: red; background-color: #ffebee; padding: 8px; border-radius: 5px;")
        stats_layout.addWidget(self.critical_label, 0, 1)
        
        self.high_label = QLabel("🟠 Высокие: 0")
        self.high_label.setFont(QFont("Arial", 12))
        self.high_label.setStyleSheet("color: orange; background-color: #fff3e0; padding: 8px; border-radius: 5px;")
        stats_layout.addWidget(self.high_label, 1, 0)
        
        self.medium_label = QLabel("🟡 Средние: 0")
        self.medium_label.setFont(QFont("Arial", 12))
        self.medium_label.setStyleSheet("color: darkorange; background-color: #ffe0b2; padding: 8px; border-radius: 5px;")
        stats_layout.addWidget(self.medium_label, 1, 1)
        
        self.low_label = QLabel("🟢 Низкие: 0")
        self.low_label.setFont(QFont("Arial", 12))
        self.low_label.setStyleSheet("color: green; background-color: #e8f5e9; padding: 8px; border-radius: 5px;")
        stats_layout.addWidget(self.low_label, 2, 0)
        
        # Дополнительные метрики
        self.types_label = QLabel("📋 Уникальных типов: 0")
        self.types_label.setFont(QFont("Arial", 12))
        stats_layout.addWidget(self.types_label, 2, 1)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        return widget
    
    def create_education_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # Заголовок
        header = QLabel("📚 Образовательный центр кибербезопасности")
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #2c3e50; padding: 15px; background-color: #3498db; color: white; border-radius: 10px;")
        layout.addWidget(header)
        
        # Описание
        desc_label = QLabel(
            "Добро пожаловать в образовательный раздел!\n\n"
            "Здесь вы можете изучить теорию о вредоносном программном обеспечении, \n"
            "типах угроз, методах заражения и способах защиты.\n\n"
            "💡 Нажмите на кнопки ниже для получения подробной информации."
        )
        desc_label.setFont(QFont("Arial", 13))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("padding: 20px; background-color: #ecf0f1; border-radius: 10px;")
        layout.addWidget(desc_label)
        
        # Кнопки
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(20)
        
        theory_btn = QPushButton("📖 Открыть полную теорию вирусов")
        theory_btn.setFont(QFont("Arial", 16, QFont.Bold))
        theory_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white; 
                padding: 20px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        theory_btn.clicked.connect(self.open_education_window)
        btn_layout.addWidget(theory_btn)
        
        stats_btn = QPushButton("📊 Показать расширенную статистику сканирований")
        stats_btn.setFont(QFont("Arial", 16, QFont.Bold))
        stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; 
                color: white; 
                padding: 20px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        stats_btn.clicked.connect(self.show_scan_stats)
        btn_layout.addWidget(stats_btn)
        
        tips_btn = QPushButton("💡 Топ-20 советов по кибербезопасности")
        tips_btn.setFont(QFont("Arial", 16, QFont.Bold))
        tips_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12; 
                color: white; 
                padding: 20px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        tips_btn.clicked.connect(self.show_security_tips)
        btn_layout.addWidget(tips_btn)
        
        quiz_btn = QPushButton("🎯 Викторина: Проверь свои знания")
        quiz_btn.setFont(QFont("Arial", 16, QFont.Bold))
        quiz_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6; 
                color: white; 
                padding: 20px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        quiz_btn.clicked.connect(self.show_quiz)
        btn_layout.addWidget(quiz_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        return widget
    
    def setup_connections(self):
        self.scan_btn.clicked.connect(self.start_scan)
        self.stop_btn.clicked.connect(self.stop_scan)
        self.generate_btn.clicked.connect(self.generate_test_threats)
        
        # Подключение защиты в реальном времени
        self.real_time_protection.threat_detected.connect(self.on_real_time_threat)
        self.real_time_protection.log_message.connect(self.add_log_message)
    
    def toggle_real_time_protection(self, state):
        if state == Qt.Checked:
            self.real_time_protection.start()
            self.statusBar().showMessage("✅ Защита в реальном времени: ВКЛ | Мониторинг активен")
            self.add_log_message("🛡️ Защита в реальном времени АКТИВИРОВАНА")
        else:
            self.real_time_protection.stop()
            self.statusBar().showMessage("❌ Защита в реальном времени: ВЫКЛ")
            self.add_log_message("⚠️ Защита в реальном времени ОТКЛЮЧЕНА")
    
    def on_real_time_threat(self, virus):
        self.add_virus_to_list(virus)
        self.add_log_message(f"🚨 БЛОКИРОВАНО: {virus['name']} [{virus['type']}]")
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("🛡️ Угроза заблокирована!")
        msg.setText(f"Обнаружена и автоматически заблокирована угроза:\n\n<b>{virus['name']}</b>")
        msg.setInformativeText(f"Тип: {virus['type']}\nУровень опасности: {virus['severity']}\n\nДействие: Угроза помещена в карантин")
        msg.setStyleSheet("QLabel { font-size: 12px; }")
        msg.exec_()
    
    def start_scan(self):
        if self.scan_worker and self.scan_worker.isRunning():
            return
            
        self.scan_count += 1
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Статус: 🔍 Сканирование системы...")
        self.add_log_message("=" * 60)
        self.add_log_message(f"🚀 Запуск сканирования #{self.scan_count}")
        self.add_log_message("=" * 60)
        
        # Генерируем случайное количество угроз (0-7)
        viruses_count = random.randint(0, 7)
        
        self.scan_worker = ScanWorker(viruses_count)
        self.scan_worker.progress_signal.connect(self.progress_bar.setValue)
        self.scan_worker.found_signal.connect(self.add_virus_to_list)
        self.scan_worker.finished_signal.connect(self.scan_finished)
        self.scan_worker.log_signal.connect(self.add_log_message)
        self.scan_worker.start()
    
    def stop_scan(self):
        if self.scan_worker:
            self.scan_worker.stop()
            self.add_log_message("⏹️ Сканирование остановлено пользователем")
            self.scan_finished()
    
    def scan_finished(self):
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Статус: ✅ Сканирование завершено")
        self.add_log_message("=" * 60)
        self.add_log_message(f"✅ Сканирование завершено. Найдено угроз: {len(self.detected_viruses)}")
        self.add_log_message("=" * 60)
        self.update_stats()
        self.update_tab_title()
    
    def generate_test_threats(self):
        count = random.randint(5, 12)
        self.add_log_message(f"🧪 Генерация {count} тестовых угроз для демонстрации...")
        
        for _ in range(count):
            virus = random.choice(FAKE_VIRUSES)
            self.add_virus_to_list(virus)
            self.add_log_message(f"🦠 Создана тестовая угроза: {virus['name']} [{virus['type']}]")
        
        QMessageBox.information(self, "✅ Тестовые угрозы созданы", 
                               f"Сгенерировано {count} тестовых угроз для демонстрации работы антивируса.\n\n"
                               f"Теперь вы можете:\n"
                               f"• Просмотреть детали каждой угрозы (двойной клик)\n"
                               f"• Удалить отдельные угрозы\n"
                               f"• Очистить весь список")
        self.update_tab_title()
    
    def add_virus_to_list(self, virus):
        self.detected_viruses.append(virus)
        item_text = f"{virus['name']} | {virus['type']} | {virus['severity']}"
        item = QListWidgetItem(item_text)
        
        # Цвет и иконка в зависимости от уровня опасности
        if virus['severity'] == "Критическая":
            item.setForeground(QColor("red"))
            item.setFont(QFont("Arial", 11, QFont.Bold))
        elif virus['severity'] == "Высокая":
            item.setForeground(QColor("darkorange"))
            item.setFont(QFont("Arial", 11, QFont.Bold))
        elif virus['severity'] == "Средняя":
            item.setForeground(QColor("orange"))
        else:
            item.setForeground(QColor("green"))
        
        self.virus_list.addItem(item)
        self.update_stats()
    
    def update_stats(self):
        total = len(self.detected_viruses)
        critical = sum(1 for v in self.detected_viruses if v['severity'] == "Критическая")
        high = sum(1 for v in self.detected_viruses if v['severity'] == "Высокая")
        medium = sum(1 for v in self.detected_viruses if v['severity'] == "Средняя")
        low = sum(1 for v in self.detected_viruses if v['severity'] == "Низкая")
        
        unique_types = len(set(v['type'] for v in self.detected_viruses))
        
        self.total_label.setText(f"📌 Всего обнаружено: {total}")
        self.critical_label.setText(f"🔴 Критические: {critical}")
        self.high_label.setText(f"🟠 Высокие: {high}")
        self.medium_label.setText(f"🟡 Средние: {medium}")
        self.low_label.setText(f"🟢 Низкие: {low}")
        self.types_label.setText(f"📋 Уникальных типов: {unique_types}")
    
    def update_tab_title(self):
        self.tabs.setTabText(1, f"⚠️ Угрозы ({len(self.detected_viruses)})")
    
    def show_threat_details(self, item):
        row = self.virus_list.row(item)
        if 0 <= row < len(self.detected_viruses):
            virus = self.detected_viruses[row]
            dialog = ThreatInfoDialog(virus, self)
            dialog.exec_()
    
    def remove_selected(self):
        selected_items = self.virus_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "⚠️ Предупреждение", "Выберите одну или несколько угроз для удаления")
            return
        
        removed_count = 0
        for item in selected_items:
            row = self.virus_list.row(item)
            if 0 <= row < len(self.detected_viruses):
                self.detected_viruses.pop(row)
                self.virus_list.takeItem(row)
                removed_count += 1
        
        self.add_log_message(f"🗑️ Удалено {removed_count} угроз пользователем")
        self.update_stats()
        self.update_tab_title()
    
    def clear_all_threats(self):
        if not self.detected_viruses:
            QMessageBox.information(self, "ℹ️ Информация", "Список угроз уже пуст")
            return
            
        reply = QMessageBox.question(self, "⚠️ Подтверждение",
                                    "Вы уверены, что хотите удалить ВСЕ обнаруженные угрозы?\n\n"
                                    "Это действие нельзя отменить.",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            count = len(self.detected_viruses)
            self.detected_viruses.clear()
            self.virus_list.clear()
            self.update_stats()
            self.update_tab_title()
            self.add_log_message(f"🧹 Полная очистка: удалено {count} угроз")
    
    def add_log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def open_education_window(self):
        window = EducationWindow(self)
        window.exec_()
    
    def show_scan_stats(self):
        stats_text = (
            f"📊 Расширенная статистика сканирований\n\n"
            f"Всего сканирований: {self.scan_count}\n"
            f"Текущее количество угроз: {len(self.detected_viruses)}\n\n"
            f"Распределение по уровням опасности:\n"
            f"🔴 Критических: {sum(1 for v in self.detected_viruses if v['severity'] == 'Критическая')}\n"
            f"🟠 Высоких: {sum(1 for v in self.detected_viruses if v['severity'] == 'Высокая')}\n"
            f"🟡 Средних: {sum(1 for v in self.detected_viruses if v['severity'] == 'Средняя')}\n"
            f"🟢 Низких: {sum(1 for v in self.detected_viruses if v['severity'] == 'Низкая')}\n\n"
            f"Уникальных типов угроз: {len(set(v['type'] for v in self.detected_viruses))}\n"
            f"Всего типов в базе: {len(FAKE_VIRUSES)}"
        )
        QMessageBox.information(self, "📈 Статистика сканирований", stats_text)
    
    def show_security_tips(self):
        tips_text = (
            "💡 20 важных советов по кибербезопасности:\n\n"
            "1. Регулярно обновляйте ОС и все программы до последних версий\n"
            "2. Используйте надежные уникальные пароли для каждого сервиса\n"
            "3. Включите двухфакторную аутентификацию везде, где возможно\n"
            "4. Делайте резервные копии важных данных по правилу 3-2-1\n"
            "5. Не открывайте подозрительные вложения в письмах\n"
            "6. Проверяйте URL перед вводом конфиденциальных данных\n"
            "7. Используйте антивирус и держите его базы обновленными\n"
            "8. Включите брандмауэр для защиты от сетевых атак\n"
            "9. Осторожно с публичными Wi-Fi сетями (используйте VPN)\n"
            "10. Не используйте одинаковые пароли на разных сайтах\n"
            "11. Регулярно проверяйте настройки приватности в соцсетях\n"
            "12. Отключите автозапуск съемных носителей\n"
            "13. Проверяйте USB-флешки антивирусом перед использованием\n"
            "14. Ограничьте права пользователей в системе\n"
            "15. Используйте менеджер паролей для хранения учетных данных\n"
            "16. Будьте осторожны с ссылками в сообщениях и соцсетях\n"
            "17. Проверяйте отправителя перед открытием писем\n"
            "18. Не скачивайте ПО с непроверенных сайтов\n"
            "19. Следите за необычной активностью в аккаунтах\n"
            "20. Обучайте сотрудников и близких основам безопасности"
        )
        QMessageBox.information(self, "🛡️ Советы по кибербезопасности", tips_text)
    
    def show_quiz(self):
        quiz_text = (
            "🎯 Викторина: Проверь свои знания!\n\n"
            "Вопрос 1: Что такое фишинг?\n"
            "А) Вид рыбы\n"
            "Б) Кража данных через поддельные сайты/письма ✓\n"
            "В) Программа для рыбалки\n\n"
            "Вопрос 2: Как защититься от вирусов-вымогателей?\n"
            "А) Заплатить выкуп\n"
            "Б) Делать резервные копии ✓\n"
            "В) Игнорировать проблему\n\n"
            "Вопрос 3: Что делает бэкдор?\n"
            "А) Открывает двери\n"
            "Б) Обходит аутентификацию для удаленного доступа ✓\n"
            "В) Защищает систему\n\n"
            "Вопрос 4: Какой тип вируса меняет свой код?\n"
            "А) Полиморфный ✓\n"
            "Б) Червь\n"
            "В) Троян\n\n"
            "Вопрос 5: Что такое руткит?\n"
            "А) Набор корней\n"
            "Б) Программа для скрытия присутствия в системе ✓\n"
            "В) Антивирус"
        )
        QMessageBox.information(self, "📝 Викторина по вирусам", quiz_text)
    
    def closeEvent(self, event):
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.stop()
        self.real_time_protection.stop()
        self.add_log_message("👋 Приложение закрыто пользователем")
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Стиль приложения
    app.setStyle("Fusion")
    
    # Палитра цветов
    palette = app.palette()
    palette.setColor(palette.Window, QColor("#f5f6fa"))
    palette.setColor(palette.WindowText, QColor("#2c3e50"))
    app.setPalette(palette)
    
    window = AntivirusSimulator()
    window.show()
    
    sys.exit(app.exec_())
