#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Secure GUI - Simplified High-Contrast Interface
Version 7.0
For non-technical users.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import os
import hashlib
import json
import random
from datetime import datetime

class RedSandApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RedSand Secure")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Настройки по умолчанию
        self.current_theme = "dark"
        self.language = "ru"
        self.is_analyzing = False
        self.analysis_complete = False
        
        # Локализация
        self.translations = {
            "ru": {
                # Главное окно
                "app_title": "RedSand Secure",
                "status_ready": "Готов к работе. Выберите файл для анализа.",
                "info_text": "Выберите файл для проверки на вирусы.\nСистема автоматически обнаружит угрозы и даст рекомендации.",
                "btn_select_file": "📁 ВЫБРАТЬ ФАЙЛ",
                "btn_run_analysis": "🚀 ЗАПУСТИТЬ АНАЛИЗ",
                "btn_analyzing": "⏳ АНАЛИЗ...",
                "file_selected": "Файл выбран: {}",
                "scanning_signatures": "Сканирование сигнатур...",
                "heuristic_analysis": "Эвристический анализ...",
                "behavior_analysis": "Анализ поведения...",
                "analysis_complete": "Анализ завершен.",
                # Верхняя панель
                "btn_settings": "⚙️ Настройки",
                "btn_reports": "📊 Отчеты",
                "btn_theme": "🌓 Тема",
                # Результаты
                "result_title": "Результаты анализа",
                "verdict": "ВЕРДИКТ: {}",
                "tab_main": "🏠 Главная",
                "tab_virus": "🦠 О вирусе",
                "tab_help": "❓ Справка",
                "btn_close": "ЗАКРЫТЬ",
                # Вкладка главная
                "file_info": "📄 Информация о файле",
                "file_name": "Имя файла:",
                "file_path": "Полный путь:",
                "scan_date": "Дата проверки:",
                # Вкладка о вирусе
                "threat_detected": "🦠 Обнаруженная угроза",
                "threat_family": "Семейство: {}",
                "what_is_it": "📖 Что это такое?",
                "how_found": "🔍 Как мы это нашли?",
                "what_to_do": "✅ Что делать? (Инструкция)",
                # Вердикты
                "verdict_danger": "ОПАСНО",
                "verdict_suspicious": "ПОДОЗРИТЕЛЬНО",
                "verdict_safe": "БЕЗОПАСНО",
                "no_threats": "Нет угроз",
                "clean_file": "Чистый файл",
                # Настройки
                "settings_title": "⚙️ НАСТРОЙКИ ПРОГРАММЫ",
                "opt_auto_update": "Автоматическая проверка обновлений",
                "opt_deep_analysis": "Глубокий анализ (медленнее, но точнее)",
                "opt_scan_archives": "Проверять архивы внутри файлов",
                "opt_show_help": "Показывать справку после каждого анализа",
                "settings_help": "ℹ️ Здесь вы можете настроить поведение сканера.\nРекомендуется оставить все галочки включенными для максимальной защиты.",
                "lbl_language": "Язык интерфейса:",
                "lang_ru": "Русский",
                "lang_en": "English",
                # Отчеты
                "reports_title": "📊 ИСТОРИЯ ОТЧЕТОВ",
                "reports_empty": "Здесь будет отображаться история ваших сканирований.\nПока что отчетов нет.\n\nПример будущего отчета:\n[2023-10-27 12:00] Файл: test.exe - ОПАСНО (Trojan)",
                # Справка
                "help_title": "❓ СПРАВКА ПО ИСПОЛЬЗОВАНИЮ",
                "help_howto": "📌 Как пользоваться программой:",
                "help_step1": "1. Нажмите кнопку \"ВЫБРАТЬ ФАЙЛ\".",
                "help_step2": "2. Выберите подозрительный файл на компьютере.",
                "help_step3": "3. Нажмите \"ЗАПУСТИТЬ АНАЛИЗ\".",
                "help_step4": "4. Дождитесь окончания проверки.",
                "help_step5": "5. Изучите вердикт и рекомендации.",
                "help_themes": "🎨 Темы оформления:",
                "help_theme_desc": "Нажмите кнопку \"Тема\" сверху, чтобы переключить светлую/темную тему.",
                "help_settings": "⚙️ Настройки:",
                "help_settings_desc": "В разделе настроек вы можете изменить параметры сканирования.",
                "help_reports": "📊 Отчеты:",
                "help_reports_desc": "Здесь сохраняется история последних проверок.",
                "help_interpretation": "🛡️ Интерпретация результатов:",
                "help_safe": "- БЕЗОПАСНО (Зеленый): Файл чист, можно использовать.",
                "help_suspicious": "- ПОДОЗРИТЕЛЬНО (Желтый): Есть сомнения. Лучше удалить, если не знаете источник.",
                "help_danger": "- ОПАСНО (Красный): Вирус найден! Немедленно удалите файл!",
                "help_about": "ℹ️ О программе:",
                "help_about_desc": "RedSand Secure использует современные методы эвристического анализа\nи базу сигнатур для защиты вашего компьютера.",
                # Диалоги
                "dialog_exit_title": "Выход",
                "dialog_exit_msg": "Анализ еще идет. Вы действительно хотите выйти?",
                "dialog_select_file_title": "Выберите файл для анализа"
            },
            "en": {
                # Main window
                "app_title": "RedSand Secure",
                "status_ready": "Ready to work. Select a file for analysis.",
                "info_text": "Select a file to scan for viruses.\nThe system will automatically detect threats and provide recommendations.",
                "btn_select_file": "📁 SELECT FILE",
                "btn_run_analysis": "🚀 START ANALYSIS",
                "btn_analyzing": "⏳ ANALYZING...",
                "file_selected": "File selected: {}",
                "scanning_signatures": "Scanning signatures...",
                "heuristic_analysis": "Heuristic analysis...",
                "behavior_analysis": "Behavior analysis...",
                "analysis_complete": "Analysis complete.",
                # Top bar
                "btn_settings": "⚙️ Settings",
                "btn_reports": "📊 Reports",
                "btn_theme": "🌓 Theme",
                # Results
                "result_title": "Analysis Results",
                "verdict": "VERDICT: {}",
                "tab_main": "🏠 Main",
                "tab_virus": "🦠 About Threat",
                "tab_help": "❓ Help",
                "btn_close": "CLOSE",
                # Main tab
                "file_info": "📄 File Information",
                "file_name": "File name:",
                "file_path": "Full path:",
                "scan_date": "Scan date:",
                # Virus tab
                "threat_detected": "🦠 Detected Threat",
                "threat_family": "Family: {}",
                "what_is_it": "📖 What is it?",
                "how_found": "🔍 How we found it?",
                "what_to_do": "✅ What to do? (Instructions)",
                # Verdicts
                "verdict_danger": "DANGEROUS",
                "verdict_suspicious": "SUSPICIOUS",
                "verdict_safe": "SAFE",
                "no_threats": "No threats",
                "clean_file": "Clean file",
                # Settings
                "settings_title": "⚙️ PROGRAM SETTINGS",
                "opt_auto_update": "Automatic update check",
                "opt_deep_analysis": "Deep analysis (slower but more accurate)",
                "opt_scan_archives": "Scan archives inside files",
                "opt_show_help": "Show help after each analysis",
                "settings_help": "ℹ️ Here you can configure scanner behavior.\nRecommended to keep all options enabled for maximum protection.",
                "lbl_language": "Interface Language:",
                "lang_ru": "Русский",
                "lang_en": "English",
                # Reports
                "reports_title": "📊 REPORT HISTORY",
                "reports_empty": "Your scan history will be displayed here.\nNo reports yet.\n\nExample future report:\n[2023-10-27 12:00] File: test.exe - DANGEROUS (Trojan)",
                # Help
                "help_title": "❓ USER GUIDE",
                "help_howto": "📌 How to use the program:",
                "help_step1": "1. Click \"SELECT FILE\" button.",
                "help_step2": "2. Select a suspicious file on your computer.",
                "help_step3": "3. Click \"START ANALYSIS\" button.",
                "help_step4": "4. Wait for the scan to complete.",
                "help_step5": "5. Review the verdict and recommendations.",
                "help_themes": "🎨 Themes:",
                "help_theme_desc": "Click \"Theme\" button at the top to switch between light/dark theme.",
                "help_settings": "⚙️ Settings:",
                "help_settings_desc": "In settings section you can change scanning parameters.",
                "help_reports": "📊 Reports:",
                "help_reports_desc": "History of recent scans is saved here.",
                "help_interpretation": "🛡️ Result interpretation:",
                "help_safe": "- SAFE (Green): File is clean, safe to use.",
                "help_suspicious": "- SUSPICIOUS (Yellow): Doubts exist. Better delete if source unknown.",
                "help_danger": "- DANGEROUS (Red): Virus found! Delete this file immediately!",
                "help_about": "ℹ️ About:",
                "help_about_desc": "RedSand Secure uses modern heuristic analysis methods\nand signature database to protect your computer.",
                # Dialogs
                "dialog_exit_title": "Exit",
                "dialog_exit_msg": "Analysis is still running. Do you really want to exit?",
                "dialog_select_file_title": "Select file for analysis"
            }
        }
        
        # Применение тем
        self.styles = {
            "dark": {
                "bg": "#121212",
                "fg": "#FFFFFF",
                "frame_bg": "#1E1E1E",
                "button_bg": "#333333",
                "button_fg": "#FFFFFF",
                "accent": "#BB86FC",
                "safe": "#00E676",
                "warn": "#FFEA00",
                "danger": "#FF5252",
                "text_highlight": "#FFFFFF",
                "entry_bg": "#2C2C2C",
                "border": "#444444"
            },
            "light": {
                "bg": "#FFFFFF",
                "fg": "#000000",
                "frame_bg": "#F0F0F0",
                "button_bg": "#E0E0E0",
                "button_fg": "#000000",
                "accent": "#6200EE",
                "safe": "#00C853",
                "warn": "#FFD600",
                "danger": "#D50000",
                "text_highlight": "#000000",
                "entry_bg": "#FFFFFF",
                "border": "#CCCCCC"
            }
        }
        
        self.apply_theme(self.current_theme)
        
        # Верхняя панель
        self.create_top_bar()
        
        # Основной контент
        self.create_main_area()
        
        # Статус бар
        self.status_var = tk.StringVar(value=self.get_text("status_ready"))
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, height=1, font=("Segoe UI", 10))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Окно результатов (скрыто по умолчанию)
        self.result_window = None
    
    def get_text(self, key, *args):
        """Получение локализованного текста"""
        text = self.translations[self.language].get(key, key)
        if args:
            return text.format(*args)
        return text

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        colors = self.styles[theme_name]
        
        self.root.configure(bg=colors["bg"])
        
        # Стили для виджетов
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка цветов для всех элементов
        self.colors = colors
        
        # Обновление существующих виджетов если они есть
        if hasattr(self, 'main_frame'):
            self.main_frame.configure(bg=colors["bg"])
        if hasattr(self, 'content_frame'):
            self.content_frame.configure(bg=colors["frame_bg"])
        if hasattr(self, 'status_bar'):
            self.status_bar.configure(bg=colors["frame_bg"], fg=colors["fg"])

    def create_top_bar(self):
        top_frame = tk.Frame(self.root, bg=self.colors["frame_bg"], height=50)
        top_frame.pack(fill=tk.X, side=tk.TOP)
        top_frame.pack_propagate(False)
        
        # Заголовок
        title_label = tk.Label(top_frame, text="🛡️ RedSand Secure", font=("Segoe UI", 18, "bold"), 
                               bg=self.colors["frame_bg"], fg=self.colors["accent"])
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Кнопки справа
        btn_frame = tk.Frame(top_frame, bg=self.colors["frame_bg"])
        btn_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        settings_btn = tk.Button(btn_frame, text=self.get_text("btn_settings"), command=self.open_settings,
                                 bg=self.colors["button_bg"], fg=self.colors["button_fg"],
                                 font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15, pady=5,
                                 activebackground=self.colors["accent"], activeforeground="#FFFFFF",
                                 borderwidth=2, borderrelief=tk.RAISED)
        settings_btn.pack(side=tk.LEFT, padx=5)
        
        reports_btn = tk.Button(btn_frame, text=self.get_text("btn_reports"), command=self.open_reports,
                                bg=self.colors["button_bg"], fg=self.colors["button_fg"],
                                font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15, pady=5,
                                activebackground=self.colors["accent"], activeforeground="#FFFFFF",
                                borderwidth=2, borderrelief=tk.RAISED)
        reports_btn.pack(side=tk.LEFT, padx=5)
        
        # Переключатель темы
        theme_btn = tk.Button(btn_frame, text=self.get_text("btn_theme"), command=self.toggle_theme,
                              bg=self.colors["button_bg"], fg=self.colors["button_fg"],
                              font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15, pady=5,
                              activebackground=self.colors["accent"], activeforeground="#FFFFFF",
                              borderwidth=2, borderrelief=tk.RAISED)
        theme_btn.pack(side=tk.LEFT, padx=5)

    def create_main_area(self):
        self.main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.content_frame = tk.Frame(self.main_frame, bg=self.colors["frame_bg"], relief=tk.RAISED, borderwidth=2)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Инструкция
        info_label = tk.Label(self.content_frame, 
                              text=self.get_text("info_text"),
                              font=("Segoe UI", 12), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                              justify=tk.CENTER, pady=20)
        info_label.pack(anchor=tk.N)
        
        # Большая кнопка выбора файла
        self.select_btn = tk.Button(self.content_frame, text=self.get_text("btn_select_file"), command=self.select_file,
                                    bg=self.colors["accent"], fg="#FFFFFF",
                                    font=("Segoe UI", 16, "bold"), relief=tk.FLAT, padx=40, pady=20,
                                    activebackground="#9965F4", activeforeground="#FFFFFF",
                                    borderwidth=0, cursor="hand2")
        self.select_btn.pack(pady=20)
        
        # Путь к файлу
        self.file_path_var = tk.StringVar()
        self.path_label = tk.Label(self.content_frame, textvariable=self.file_path_var, 
                                   font=("Consolas", 10), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                   wraplength=700, justify=tk.CENTER)
        self.path_label.pack(pady=10)
        
        # Кнопка запуска
        self.run_btn = tk.Button(self.content_frame, text=self.get_text("btn_run_analysis"), command=self.start_analysis,
                                 bg=self.colors["safe"], fg="#000000",
                                 font=("Segoe UI", 16, "bold"), relief=tk.FLAT, padx=40, pady=20,
                                 activebackground="#00BFA5", activeforeground="#000000",
                                 borderwidth=0, state=tk.DISABLED, cursor="hand2")
        self.run_btn.pack(pady=20)
        
        # Прогресс бар
        self.progress = ttk.Progressbar(self.content_frame, mode='determinate', length=400)
        self.progress.pack(pady=20)
        self.progress_style = ttk.Style()
        self.progress_style.configure("horizontal.TProgressbar", troughcolor=self.colors["entry_bg"], background=self.colors["accent"])

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.apply_theme("light")
        else:
            self.apply_theme("dark")
        # Перерисовка элементов с новыми цветами
        if hasattr(self, 'select_btn'):
            self.select_btn.configure(bg=self.colors["accent"])
        if hasattr(self, 'run_btn'):
            self.run_btn.configure(bg=self.colors["safe"])
        if self.result_window:
            self.update_result_theme()

    def select_file(self):
        filename = filedialog.askopenfilename(title=self.get_text("dialog_select_file_title"),
                                              filetypes=[("Все файлы", "*.*"), ("EXE файлы", "*.exe"), ("Script files", "*.bat *.cmd *.ps1 *.vbs")])
        if filename:
            self.file_path_var.set(filename)
            self.run_btn.config(state=tk.NORMAL)
            self.status_var.set(self.get_text("file_selected", os.path.basename(filename)))

    def start_analysis(self):
        if not self.file_path_var.get():
            return
        
        self.is_analyzing = True
        self.analysis_complete = False
        self.run_btn.config(state=tk.DISABLED, text=self.get_text("btn_analyzing"))
        self.select_btn.config(state=tk.DISABLED)
        self.progress['value'] = 0
        
        # Запуск в потоке
        thread = threading.Thread(target=self.run_analysis_process)
        thread.daemon = True
        thread.start()

    def run_analysis_process(self):
        steps = 100
        for i in range(steps):
            time.sleep(0.05)  # Имитация работы
            self.progress['value'] = i + 1
            self.root.update_idletasks()
            
            if i == 30:
                self.status_var.set("Сканирование сигнатур...")
            elif i == 60:
                self.status_var.set("Эвристический анализ...")
            elif i == 80:
                self.status_var.set("Анализ поведения...")
        
        self.analysis_complete = True
        self.is_analyzing = False
        self.root.after(100, self.show_results)

    def show_results(self):
        self.run_btn.config(state=tk.NORMAL, text=self.get_text("btn_run_analysis"))
        self.select_btn.config(state=tk.NORMAL)
        self.status_var.set("Анализ завершен.")
        
        # Генерация фейкового результата для демонстрации (в реальности тут был бы движок)
        # Для примера рандомим результат, но с уклоном в опасность для демонстрации интерфейса
        risk_level = random.choice(["safe", "suspicious", "danger"])
        
        file_name = os.path.basename(self.file_path_var.get())
        
        result_data = {
            "file": file_name,
            "path": self.file_path_var.get(),
            "risk": risk_level,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": self.generate_mock_details(risk_level, file_name)
        }
        
        self.create_result_window(result_data)

    def generate_mock_details(self, risk, filename):
        if risk == "danger":
            return {
                "verdict": self.get_text("verdict_danger"),
                "color": self.colors["danger"],
                "threat_name": f"Trojan.Win32.Generic.{random.randint(1000,9999)}",
                "family": self.get_text("threat_family").format(self.get_text("lang_ru") == "Русский" and "Семейство троянов-загрузчиков" or "Trojan loader family"),
                "description": self.get_text("lang_ru") == "Русский" and "Этот файл является вредоносной программой, маскирующейся под легитимное приложение. При запуске он пытается внедриться в системные процессы, украсть ваши пароли и зашифровать личные данные." or "This file is malware disguised as a legitimate application. When launched, it tries to infiltrate system processes, steal your passwords and encrypt personal data.",
                "detection_method": self.get_text("lang_ru") == "Русский" and "Обнаружен по уникальной цифровой подписи (сигнатуре) в базе данных вирусов. Также выявлено подозрительное поведение: попытка скрытого подключения к интернету и модификация реестра." or "Detected by unique digital signature in virus database. Also detected suspicious behavior: attempt to connect to internet secretly and modify registry.",
                "recommendations": [
                    self.get_text("lang_ru") == "Русский" and "НЕМЕДЛЕННО УДАЛИТЕ ЭТОТ ФАЙЛ!" or "DELETE THIS FILE IMMEDIATELY!",
                    self.get_text("lang_ru") == "Русский" and "Не пытайтесь его открывать или запускать." or "Do not try to open or run it.",
                    self.get_text("lang_ru") == "Русский" and "Проверьте компьютер полным сканированием антивируса." or "Run a full antivirus scan on your computer.",
                    self.get_text("lang_ru") == "Русский" and "Если вы уже запустили файл, смените все важные пароли." or "If you already ran this file, change all important passwords.",
                    self.get_text("lang_ru") == "Русский" and "Проверьте банковские счета на наличие подозрительных операций." or "Check your bank accounts for suspicious transactions."
                ]
            }
        elif risk == "suspicious":
            return {
                "verdict": self.get_text("verdict_suspicious"),
                "color": self.colors["warn"],
                "threat_name": "Heuristic.Suspicious.Tool",
                "family": self.get_text("lang_ru") == "Русский" and "Инструменты администрирования / Потенциально нежелательное ПО" or "Administration tools / Potentially unwanted software",
                "description": self.get_text("lang_ru") == "Русский" and "Файл содержит код, который может использоваться как во благо, так и во вред. Это может быть инструмент для взлома, майнер или программа для скрытого наблюдения. Сам по себе он не является вирусом, но несет риски." or "File contains code that can be used for good or bad. It could be a hacking tool, miner or spyware. By itself it's not a virus but carries risks.",
                "detection_method": self.get_text("lang_ru") == "Русский" and "Выявлено подозрительное поведение при эвристическом анализе. Файл пытается получить права администратора без явной необходимости и скрывает свои процессы." or "Suspicious behavior detected during heuristic analysis. File tries to get admin rights without clear need and hides its processes.",
                "recommendations": [
                    self.get_text("lang_ru") == "Русский" and "Лучше не использовать этот файл, если вы не уверены в источнике на 100%." or "Better not use this file unless you're 100% sure of the source.",
                    self.get_text("lang_ru") == "Русский" and "Удалите файл, если вы не скачивали его специально." or "Delete the file if you didn't download it intentionally.",
                    self.get_text("lang_ru") == "Русский" and "Если файл нужен, запустите его в изолированной среде (песочнице)." or "If you need the file, run it in isolated environment (sandbox).",
                    self.get_text("lang_ru") == "Русский" and "Проверьте цифровую подпись издателя (скорее всего её нет)." or "Check publisher's digital signature (most likely there isn't one)."
                ]
            }
        else:
            return {
                "verdict": self.get_text("verdict_safe"),
                "color": self.colors["safe"],
                "threat_name": self.get_text("no_threats"),
                "family": self.get_text("clean_file"),
                "description": self.get_text("lang_ru") == "Русский" and "Файл прошел все проверки. В нем не обнаружено известных вирусов, троянов или подозрительного кода. Цифровая подпись (если есть) действительна." or "File passed all checks. No known viruses, trojans or suspicious code found. Digital signature (if present) is valid.",
                "detection_method": self.get_text("lang_ru") == "Русский" and "Сравнение с базой известных вирусов не дало совпадений. Поведенческий анализ не выявил опасных действий." or "Comparison with known virus database found no matches. Behavioral analysis detected no dangerous actions.",
                "recommendations": [
                    self.get_text("lang_ru") == "Русский" and "Файл можно использовать." or "File is safe to use.",
                    self.get_text("lang_ru") == "Русский" and "Все равно соблюдайте базовую осторожность." or "Still exercise basic caution.",
                    self.get_text("lang_ru") == "Русский" and "Убедитесь, что файл скачан с официального сайта." or "Make sure file was downloaded from official website.",
                    self.get_text("lang_ru") == "Русский" and "Храните резервные копии важных данных." or "Keep backups of important data."
                ]
            }

    def create_result_window(self, data):
        if self.result_window:
            self.result_window.destroy()
            
        self.result_window = tk.Toplevel(self.root)
        self.result_window.title("Результаты анализа")
        self.result_window.geometry("800x650")
        self.result_window.configure(bg=self.colors["bg"])
        self.result_window.transient(self.root)
        self.result_window.grab_set()
        
        # Обработка закрытия окна
        def on_close():
            self.result_window.destroy()
            self.result_window = None
            
        self.result_window.protocol("WM_DELETE_WINDOW", on_close)

        # Заголовок с вердиктом
        verdict_frame = tk.Frame(self.result_window, bg=data["details"]["color"], height=80)
        verdict_frame.pack(fill=tk.X)
        verdict_frame.pack_propagate(False)
        
        verdict_label = tk.Label(verdict_frame, text=f"ВЕРДИКТ: {data['details']['verdict']}", 
                                 font=("Segoe UI", 24, "bold"), bg=data["details"]["color"], fg="#000000" if data["risk"] != "danger" else "#FFFFFF",
                                 pady=20)
        verdict_label.pack()
        
        # Контейнер для вкладок
        notebook_frame = tk.Frame(self.result_window, bg=self.colors["bg"])
        notebook_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Создаем вкладки вручную для полного контроля стиля
        tab_control = ttk.Notebook(notebook_frame)
        tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка 1: Главная
        tab_main = tk.Frame(tab_control, bg=self.colors["frame_bg"])
        tab_control.add(tab_main, text=self.get_text("tab_main"))
        self.create_main_result_tab(tab_main, data)
        
        # Вкладка 2: О вирусе
        tab_virus = tk.Frame(tab_control, bg=self.colors["frame_bg"])
        tab_control.add(tab_virus, text=self.get_text("tab_virus"))
        self.create_virus_info_tab(tab_virus, data)
        
        # Вкладка 3: Справка
        tab_help = tk.Frame(tab_control, bg=self.colors["frame_bg"])
        tab_control.add(tab_help, text=self.get_text("tab_help"))
        self.create_help_tab(tab_help)
        
        # Кнопка закрыть
        close_btn = tk.Button(self.result_window, text=self.get_text("btn_close"), command=on_close,
                              bg=self.colors["button_bg"], fg=self.colors["fg"],
                              font=("Segoe UI", 12, "bold"), relief=tk.FLAT, padx=20, pady=10,
                              activebackground=self.colors["accent"], activeforeground="#FFFFFF")
        close_btn.pack(pady=10)

    def update_result_theme(self):
        if not self.result_window:
            return
        # Перекраиваем элементы результата при смене темы
        # (Упрощенно: просто обновляем цвета основных фреймов)
        for widget in self.result_window.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.colors["bg"])
                for child in widget.winfo_children():
                    if isinstance(child, tk.Frame):
                        child.configure(bg=self.colors["frame_bg"])

    def create_main_result_tab(self, parent, data):
        # Скролл
        canvas = tk.Canvas(parent, bg=self.colors["frame_bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["frame_bg"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Информация о файле
        info_box = tk.LabelFrame(scrollable_frame, text=self.get_text("file_info"),
                                 font=("Segoe UI", 12, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                 padx=15, pady=15)
        info_box.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(info_box, text=self.get_text("file_name"), font=("Segoe UI", 11, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"]).pack(anchor=tk.W)
        tk.Label(info_box, text=data["file"], font=("Consolas", 10), bg=self.colors["frame_bg"], fg=self.colors["text_highlight"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W, pady=(0,10))
        
        tk.Label(info_box, text=self.get_text("file_path"), font=("Segoe UI", 11, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"]).pack(anchor=tk.W)
        tk.Label(info_box, text=data["path"], font=("Consolas", 9), bg=self.colors["frame_bg"], fg=self.colors["text_highlight"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W, pady=(0,10))
        
        tk.Label(info_box, text=self.get_text("scan_date"), font=("Segoe UI", 11, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"]).pack(anchor=tk.W)
        tk.Label(info_box, text=data["date"], font=("Segoe UI", 10), bg=self.colors["frame_bg"], fg=self.colors["fg"]).pack(anchor=tk.W)

    def create_virus_info_tab(self, parent, data):
        details = data["details"]
        
        canvas = tk.Canvas(parent, bg=self.colors["frame_bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["frame_bg"])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        padding = 20
        
        # Название угрозы
        name_frame = tk.LabelFrame(scrollable_frame, text=self.get_text("threat_detected"),
                                   font=("Segoe UI", 12, "bold"), bg=self.colors["frame_bg"], fg=details["color"],
                                   padx=padding, pady=padding)
        name_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(name_frame, text=details["threat_name"], font=("Segoe UI", 14, "bold"), 
                 bg=self.colors["frame_bg"], fg=self.colors["fg"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W)
        tk.Label(name_frame, text=f"Семейство: {details['family']}", font=("Segoe UI", 11), 
                 bg=self.colors["frame_bg"], fg=self.colors["fg"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W, pady=(5,0))

        # Описание
        desc_frame = tk.LabelFrame(scrollable_frame, text=self.get_text("what_is_it"),
                                   font=("Segoe UI", 12, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                   padx=padding, pady=padding)
        desc_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(desc_frame, text=details["description"], font=("Segoe UI", 11), 
                 bg=self.colors["frame_bg"], fg=self.colors["fg"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W)

        # Метод обнаружения
        method_frame = tk.LabelFrame(scrollable_frame, text=self.get_text("how_found"),
                                     font=("Segoe UI", 12, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                     padx=padding, pady=padding)
        method_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(method_frame, text=details["detection_method"], font=("Segoe UI", 11), 
                 bg=self.colors["frame_bg"], fg=self.colors["fg"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W)

        # Рекомендации
        rec_frame = tk.LabelFrame(scrollable_frame, text=self.get_text("what_to_do"),
                                  font=("Segoe UI", 12, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                  padx=padding, pady=padding)
        rec_frame.pack(fill=tk.X, padx=20, pady=10)
        
        for i, rec in enumerate(details["recommendations"], 1):
            rec_text = f"{i}. {rec}"
            color = details["color"] if "НЕ" in rec or "УДАЛИ" in rec.upper() else self.colors["fg"]
            tk.Label(rec_frame, text=rec_text, font=("Segoe UI", 11, "bold" if "НЕ" in rec or "УДАЛИ" in rec.upper() else "normal"), 
                     bg=self.colors["frame_bg"], fg=color, wraplength=600, justify=tk.LEFT, anchor=tk.W).pack(fill=tk.X, pady=5)


    def create_help_tab(self, parent):
        canvas = tk.Canvas(parent, bg=self.colors["frame_bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["frame_bg"])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        help_text = f"""
        {self.get_text("help_title")}
        
        {self.get_text("help_howto")}
        {self.get_text("help_step1")}
        {self.get_text("help_step2")}
        {self.get_text("help_step3")}
        {self.get_text("help_step4")}
        {self.get_text("help_step5")}
        
        {self.get_text("help_themes")}
        {self.get_text("help_theme_desc")}
        
        {self.get_text("help_settings")}
        {self.get_text("help_settings_desc")}
        
        {self.get_text("help_reports")}
        {self.get_text("help_reports_desc")}
        
        {self.get_text("help_interpretation")}
        {self.get_text("help_safe")}
        {self.get_text("help_suspicious")}
        {self.get_text("help_danger")}
        
        {self.get_text("help_about")}
        {self.get_text("help_about_desc")}
        """
        
        label = tk.Label(scrollable_frame, text=help_text, font=("Segoe UI", 11), 
                         bg=self.colors["frame_bg"], fg=self.colors["fg"], 
                         justify=tk.LEFT, anchor=tk.W, padx=20, pady=20)
        label.pack()

    def open_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title(self.get_text("btn_settings"))
        settings_win.geometry("500x400")
        settings_win.configure(bg=self.colors["bg"])
        settings_win.transient(self.root)
        
        frame = tk.Frame(settings_win, bg=self.colors["frame_bg"], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text=self.get_text("settings_title"), font=("Segoe UI", 16, "bold"), 
                 bg=self.colors["frame_bg"], fg=self.colors["accent"]).pack(pady=10)
        
        # Опции с локализацией
        opts_keys = ["opt_auto_update", "opt_deep_analysis", "opt_scan_archives", "opt_show_help"]
        
        vars_list = []
        for opt_key in opts_keys:
            var = tk.BooleanVar(value=True)
            vars_list.append(var)
            cb = tk.Checkbutton(frame, text=self.get_text(opt_key), variable=var, 
                                bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                selectcolor=self.colors["bg"], font=("Segoe UI", 11))
            cb.pack(anchor=tk.W, pady=5)
            
        # Справка внизу
        help_lbl = tk.Label(frame, text=self.get_text("settings_help"),
                            font=("Segoe UI", 10, "italic"), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                            justify=tk.CENTER, pady=20)
        help_lbl.pack(side=tk.BOTTOM)
        
        # Переключатель языка
        lang_frame = tk.Frame(frame, bg=self.colors["frame_bg"])
        lang_frame.pack(side=tk.BOTTOM, pady=10)
        
        tk.Label(lang_frame, text=self.get_text("lbl_language"), font=("Segoe UI", 11),
                 bg=self.colors["frame_bg"], fg=self.colors["fg"]).pack(side=tk.LEFT, padx=5)
        
        self.lang_var = tk.StringVar(value=self.language)
        
        self.ru_radio = tk.Radiobutton(lang_frame, text=self.get_text("lang_ru"), variable=self.lang_var, value="ru",
                                       bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                       selectcolor=self.colors["bg"], font=("Segoe UI", 11),
                                       command=self.change_language)
        self.ru_radio.pack(side=tk.LEFT, padx=5)
        
        self.en_radio = tk.Radiobutton(lang_frame, text=self.get_text("lang_en"), variable=self.lang_var, value="en",
                                       bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                       selectcolor=self.colors["bg"], font=("Segoe UI", 11),
                                       command=self.change_language)
        self.en_radio.pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame, text=self.get_text("btn_close"), command=settings_win.destroy,
                  bg=self.colors["accent"], fg="#FFFFFF", font=("Segoe UI", 12, "bold"),
                  relief=tk.FLAT, padx=20, pady=10).pack(side=tk.BOTTOM, pady=10)
    
    def change_language(self):
        """Смена языка интерфейса - только одна кнопка может быть активна"""
        new_lang = self.lang_var.get()
        if new_lang != self.language:
            self.language = new_lang
            # Перерисовываем интерфейс
            self.rebuild_ui()

    def rebuild_ui(self):
        """Пересоздание интерфейса с новым языком"""
        # Сохраняем текущие данные
        current_file = self.file_path_var.get()
        
        # Очищаем основной фрейм
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Пересоздаем элементы
        self.create_main_area()
        
        # Восстанавливаем путь к файлу
        self.file_path_var.set(current_file)
        if current_file:
            self.run_btn.config(state=tk.NORMAL)
        
        # Обновляем статус бар
        self.status_var.set(self.get_text("status_ready"))


    def open_reports(self):
        rep_win = tk.Toplevel(self.root)
        rep_win.title(self.get_text("btn_reports"))
        rep_win.geometry("600x400")
        rep_win.configure(bg=self.colors["bg"])
        rep_win.transient(self.root)
        
        frame = tk.Frame(rep_win, bg=self.colors["frame_bg"], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text=self.get_text("reports_title"), font=("Segoe UI", 16, "bold"), 
                 bg=self.colors["frame_bg"], fg=self.colors["accent"]).pack(pady=10)
        
        text = scrolledtext.ScrolledText(frame, font=("Consolas", 10), bg=self.colors["bg"], fg=self.colors["fg"])
        text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        text.insert(tk.END, self.get_text("reports_empty") + "\n")
        
        tk.Button(frame, text=self.get_text("btn_close"), command=rep_win.destroy,
                  bg=self.colors["accent"], fg="#FFFFFF", font=("Segoe UI", 12, "bold"),
                  relief=tk.FLAT, padx=20, pady=10).pack(pady=10)

    def on_closing(self):
        if self.is_analyzing:
            if messagebox.askokcancel(self.get_text("dialog_exit_title"), self.get_text("dialog_exit_msg")):
                self.is_analyzing = False
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RedSandApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
