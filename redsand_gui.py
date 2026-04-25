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

# Словари локализации
TRANSLATIONS = {
    "ru": {
        # Основное окно
        "app_title": "RedSand Secure",
        "header": "🛡️ RedSand Secure",
        "settings_btn": "⚙️ Настройки",
        "reports_btn": "📊 Отчеты",
        "theme_btn": "🌓 Тема",
        "lang_btn_ru": "🇷🇺 RU",
        "lang_btn_en": "🇬🇧 EN",
        "status_ready": "Готов к работе. Выберите файл для анализа.",
        "status_file_selected": "Файл выбран: ",
        "status_scanning_sigs": "Сканирование сигнатур...",
        "status_heuristic": "Эвристический анализ...",
        "status_behavior": "Анализ поведения...",
        "status_complete": "Анализ завершен.",
        "info_text": "Выберите файл для проверки на вирусы.\nСистема автоматически обнаружит угрозы и даст рекомендации.",
        "select_file_btn": "📁 ВЫБРАТЬ ФАЙЛ",
        "run_analysis_btn": "🚀 ЗАПУСТИТЬ АНАЛИЗ",
        "analyzing_btn": "⏳ АНАЛИЗ...",
        # Окно результатов
        "result_title": "Результаты анализа",
        "verdict_label": "ВЕРДИКТ: ",
        "tab_main": "🏠 Главная",
        "tab_virus": "🦠 О вирусе",
        "tab_help": "❓ Справка",
        "close_btn": "ЗАКРЫТЬ",
        # Вкладка Главная
        "file_info_title": "📄 Информация о файле",
        "file_name_label": "Имя файла:",
        "file_path_label": "Полный путь:",
        "scan_date_label": "Дата проверки:",
        # Вкладка О вирусе
        "threat_title": "🦠 Обнаруженная угроза",
        "family_label": "Семейство: ",
        "description_title": "📖 Что это такое?",
        "method_title": "🔍 Как мы это нашли?",
        "recommendations_title": "✅ Что делать? (Инструкция)",
        # Вкладка Справка
        "help_title": "❓ СПРАВКА ПО ИСПОЛЬЗОВАНИЮ",
        "help_usage_title": "📌 Как пользоваться программой:",
        "help_step1": "Нажмите кнопку \"ВЫБРАТЬ ФАЙЛ\".",
        "help_step2": "Выберите подозрительный файл на компьютере.",
        "help_step3": "Нажмите \"ЗАПУСТИТЬ АНАЛИЗ\".",
        "help_step4": "Дождитесь окончания проверки.",
        "help_step5": "Изучите вердикт и рекомендации.",
        "help_theme_title": "🎨 Темы оформления:",
        "help_theme_desc": "Нажмите кнопку \"Тема\" сверху, чтобы переключить светлую/темную тему.",
        "help_settings_title": "⚙️ Настройки:",
        "help_settings_desc": "В разделе настроек вы можете изменить параметры сканирования.",
        "help_reports_title": "📊 Отчеты:",
        "help_reports_desc": "Здесь сохраняется история последних проверок.",
        "help_verdicts_title": "🛡️ Интерпретация результатов:",
        "help_safe": "- БЕЗОПАСНО (Зеленый): Файл чист, можно использовать.",
        "help_suspicious": "- ПОДОЗРИТЕЛЬНО (Желтый): Есть сомнения. Лучше удалить, если не знаете источник.",
        "help_danger": "- ОПАСНО (Красный): Вирус найден! Немедленно удалите файл!",
        "help_about_title": "ℹ️ О программе:",
        "help_about_desc": "RedSand Secure использует современные методы эвристического анализа\nи базу сигнатур для защиты вашего компьютера.",
        # Окно настроек
        "settings_title": "Настройки",
        "settings_header": "⚙️ НАСТРОЙКИ ПРОГРАММЫ",
        "opt_auto_update": "Автоматическая проверка обновлений",
        "opt_deep_scan": "Глубокий анализ (медленнее, но точнее)",
        "opt_scan_archives": "Проверять архивы внутри файлов",
        "opt_show_help": "Показывать справку после каждого анализа",
        "settings_help": "ℹ️ Здесь вы можете настроить поведение сканера.\nРекомендуется оставить все галочки включенными для максимальной защиты.",
        # Окно отчетов
        "reports_title": "Отчеты",
        "reports_header": "📊 ИСТОРИЯ ОТЧЕТОВ",
        "reports_empty": "Здесь будет отображаться история ваших сканирований.\nПока что отчетов нет.\n\nПример будущего отчета:\n[2023-10-27 12:00] Файл: test.exe - ОПАСНО (Trojan)",
        # Вердикты
        "verdict_safe": "БЕЗОПАСНО",
        "verdict_suspicious": "ПОДОЗРИТЕЛЬНО",
        "verdict_danger": "ОПАСНО",
        # Диалоги
        "file_dialog_title": "Выберите файл для анализа",
        "all_files": "Все файлы",
        "exe_files": "EXE файлы",
        "script_files": "Script files",
        "exit_confirm": "Анализ еще идет. Вы действительно хотите выйти?",
        "exit_title": "Выход",
        # Детали угроз
        "threat_no_threats": "Нет угроз",
        "threat_clean_file": "Чистый файл",
        "desc_safe": "Файл прошел все проверки. В нем не обнаружено известных вирусов, троянов или подозрительного кода. Цифровая подпись (если есть) действительна.",
        "method_safe": "Сравнение с базой известных вирусов не дало совпадений. Поведенческий анализ не выявил опасных действий.",
        "rec_safe_1": "Файл можно использовать.",
        "rec_safe_2": "Все равно соблюдайте базовую осторожность.",
        "rec_safe_3": "Убедитесь, что файл скачан с официального сайта.",
        "rec_safe_4": "Храните резервные копии важных данных.",
        # Danger threat texts
        "danger_family": "Семейство троянов-загрузчиков",
        "danger_desc": "Этот файл является вредоносной программой, маскирующейся под легитимное приложение. При запуске он пытается внедриться в системные процессы, украсть ваши пароли и зашифровать личные данные.",
        "danger_method": "Обнаружен по уникальной цифровой подписи (сигнатуре) в базе данных вирусов. Также выявлено подозрительное поведение: попытка скрытого подключения к интернету и модификация реестра.",
        "danger_rec_1": "НЕМЕДЛЕННО УДАЛИТЕ ЭТОТ ФАЙЛ!",
        "danger_rec_2": "Не пытайтесь его открывать или запускать.",
        "danger_rec_3": "Проверьте компьютер полным сканированием антивируса.",
        "danger_rec_4": "Если вы уже запустили файл, смените все важные пароли.",
        "danger_rec_5": "Проверьте банковские счета на наличие подозрительных операций.",
        # Suspicious threat texts
        "suspicious_family": "Инструменты администрирования / Потенциально нежелательное ПО",
        "suspicious_desc": "Файл содержит код, который может использоваться как во благо, так и во вред. Это может быть инструмент для взлома, майнер или программа для скрытого наблюдения. Сам по себе он не является вирусом, но несет риски.",
        "suspicious_method": "Выявлено подозрительное поведение при эвристическом анализе. Файл пытается получить права администратора без явной необходимости и скрывает свои процессы.",
        "suspicious_rec_1": "Лучше не использовать этот файл, если вы не уверены в источнике на 100%.",
        "suspicious_rec_2": "Удалите файл, если вы не скачивали его специально.",
        "suspicious_rec_3": "Если файл нужен, запустите его в изолированной среде (песочнице).",
        "suspicious_rec_4": "Проверьте цифровую подпись издателя (скорее всего её нет).",
    },
    "en": {
        # Main window
        "app_title": "RedSand Secure",
        "header": "🛡️ RedSand Secure",
        "settings_btn": "⚙️ Settings",
        "reports_btn": "📊 Reports",
        "theme_btn": "🌓 Theme",
        "lang_btn_ru": "🇷🇺 RU",
        "lang_btn_en": "🇬🇧 EN",
        "status_ready": "Ready. Select a file to analyze.",
        "status_file_selected": "File selected: ",
        "status_scanning_sigs": "Scanning signatures...",
        "status_heuristic": "Heuristic analysis...",
        "status_behavior": "Behavior analysis...",
        "status_complete": "Analysis complete.",
        "info_text": "Select a file to scan for viruses.\nThe system will automatically detect threats and provide recommendations.",
        "select_file_btn": "📁 SELECT FILE",
        "run_analysis_btn": "🚀 START ANALYSIS",
        "analyzing_btn": "⏳ ANALYZING...",
        # Result window
        "result_title": "Analysis Results",
        "verdict_label": "VERDICT: ",
        "tab_main": "🏠 Main",
        "tab_virus": "🦠 About Virus",
        "tab_help": "❓ Help",
        "close_btn": "CLOSE",
        # Main tab
        "file_info_title": "📄 File Information",
        "file_name_label": "File name:",
        "file_path_label": "Full path:",
        "scan_date_label": "Scan date:",
        # Virus tab
        "threat_title": "🦠 Detected Threat",
        "family_label": "Family: ",
        "description_title": "📖 What is it?",
        "method_title": "🔍 How we found it?",
        "recommendations_title": "✅ What to do? (Instructions)",
        # Help tab
        "help_title": "❓ USER GUIDE",
        "help_usage_title": "📌 How to use the program:",
        "help_step1": "Click the \"SELECT FILE\" button.",
        "help_step2": "Select a suspicious file on your computer.",
        "help_step3": "Click \"START ANALYSIS\".",
        "help_step4": "Wait for the scan to complete.",
        "help_step5": "Review the verdict and recommendations.",
        "help_theme_title": "🎨 Themes:",
        "help_theme_desc": "Click the \"Theme\" button at the top to switch between light/dark theme.",
        "help_settings_title": "⚙️ Settings:",
        "help_settings_desc": "In the settings section you can change scanning parameters.",
        "help_reports_title": "📊 Reports:",
        "help_reports_desc": "History of recent scans is saved here.",
        "help_verdicts_title": "🛡️ Result Interpretation:",
        "help_safe": "- SAFE (Green): File is clean, safe to use.",
        "help_suspicious": "- SUSPICIOUS (Yellow): Doubts exist. Better delete if source is unknown.",
        "help_danger": "- DANGEROUS (Red): Virus found! Delete the file immediately!",
        "help_about_title": "ℹ️ About:",
        "help_about_desc": "RedSand Secure uses modern heuristic analysis methods\nand a signature database to protect your computer.",
        # Settings window
        "settings_title": "Settings",
        "settings_header": "⚙️ PROGRAM SETTINGS",
        "opt_auto_update": "Automatic update check",
        "opt_deep_scan": "Deep scan (slower but more accurate)",
        "opt_scan_archives": "Scan archives inside files",
        "opt_show_help": "Show help after each analysis",
        "settings_help": "ℹ️ Here you can configure scanner behavior.\nRecommended to keep all options enabled for maximum protection.",
        # Reports window
        "reports_title": "Reports",
        "reports_header": "📊 REPORT HISTORY",
        "reports_empty": "Your scan history will be displayed here.\nNo reports yet.\n\nExample future report:\n[2023-10-27 12:00] File: test.exe - DANGEROUS (Trojan)",
        # Verdicts
        "verdict_safe": "SAFE",
        "verdict_suspicious": "SUSPICIOUS",
        "verdict_danger": "DANGEROUS",
        # Dialogs
        "file_dialog_title": "Select file to analyze",
        "all_files": "All files",
        "exe_files": "EXE files",
        "script_files": "Script files",
        "exit_confirm": "Analysis is still running. Do you really want to exit?",
        "exit_title": "Exit",
        # Threat details
        "threat_no_threats": "No threats",
        "threat_clean_file": "Clean file",
        "desc_safe": "The file passed all checks. No known viruses, trojans or suspicious code detected. Digital signature (if present) is valid.",
        "method_safe": "Comparison with known virus database yielded no matches. Behavioral analysis revealed no dangerous actions.",
        "rec_safe_1": "File is safe to use.",
        "rec_safe_2": "Still exercise basic caution.",
        "rec_safe_3": "Make sure the file is downloaded from official website.",
        "rec_safe_4": "Keep backups of important data.",
        # Danger threat texts
        "danger_family": "Trojan downloader family",
        "danger_desc": "This file is malware disguised as a legitimate application. When run, it tries to inject into system processes, steal your passwords and encrypt personal data.",
        "danger_method": "Detected by unique digital signature in virus database. Also suspicious behavior detected: attempt to connect to internet secretly and modify registry.",
        "danger_rec_1": "DELETE THIS FILE IMMEDIATELY!",
        "danger_rec_2": "Do not try to open or run it.",
        "danger_rec_3": "Run a full antivirus scan on your computer.",
        "danger_rec_4": "If you already ran this file, change all important passwords.",
        "danger_rec_5": "Check bank accounts for suspicious transactions.",
        # Suspicious threat texts
        "suspicious_family": "Admin tools / Potentially unwanted software",
        "suspicious_desc": "File contains code that can be used for good or bad purposes. It could be a hacking tool, miner or spyware. By itself it's not a virus but carries risks.",
        "suspicious_method": "Suspicious behavior detected during heuristic analysis. File tries to get admin rights without clear need and hides its processes.",
        "suspicious_rec_1": "Better not use this file unless you're 100% sure of the source.",
        "suspicious_rec_2": "Delete the file if you didn't download it intentionally.",
        "suspicious_rec_3": "If you need the file, run it in an isolated environment (sandbox).",
        "suspicious_rec_4": "Check publisher's digital signature (most likely there isn't one).",
    }
}


class Localization:
    def __init__(self):
        self.current_lang = "ru"
    
    def get(self, key):
        lang = self.current_lang
        value = TRANSLATIONS.get(lang, {}).get(key)
        if value is None:
            value = TRANSLATIONS.get("ru", {}).get(key, key)
        return value
    
    def set_language(self, lang):
        self.current_lang = lang


class RedSandApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RedSand Secure")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Настройки по умолчанию
        self.current_theme = "dark"
        self.language = "ru"
        self.localization = Localization()
        self.is_analyzing = False
        self.analysis_complete = False
        
        # Переменные для кнопок языка
        self.lang_button_ru = None
        self.lang_button_en = None
        
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
        self.status_var = tk.StringVar(value="Готов к работе. Выберите файл для анализа.")
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, height=1, font=("Segoe UI", 10))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Окно результатов (скрыто по умолчанию)
        self.result_window = None

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
        title_label = tk.Label(top_frame, text=self.localization.get("header"), font=("Segoe UI", 18, "bold"), 
                               bg=self.colors["frame_bg"], fg=self.colors["accent"])
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Кнопки справа
        btn_frame = tk.Frame(top_frame, bg=self.colors["frame_bg"])
        btn_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        settings_btn = tk.Button(btn_frame, text=self.localization.get("settings_btn"), command=self.open_settings,
                                 bg=self.colors["button_bg"], fg=self.colors["button_fg"],
                                 font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15, pady=5,
                                 activebackground=self.colors["accent"], activeforeground="#FFFFFF",
                                 borderwidth=2, borderrelief=tk.RAISED)
        settings_btn.pack(side=tk.LEFT, padx=5)
        
        reports_btn = tk.Button(btn_frame, text=self.localization.get("reports_btn"), command=self.open_reports,
                                bg=self.colors["button_bg"], fg=self.colors["button_fg"],
                                font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15, pady=5,
                                activebackground=self.colors["accent"], activeforeground="#FFFFFF",
                                borderwidth=2, borderrelief=tk.RAISED)
        reports_btn.pack(side=tk.LEFT, padx=5)
        
        # Переключатель темы
        theme_btn = tk.Button(btn_frame, text=self.localization.get("theme_btn"), command=self.toggle_theme,
                              bg=self.colors["button_bg"], fg=self.colors["button_fg"],
                              font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15, pady=5,
                              activebackground=self.colors["accent"], activeforeground="#FFFFFF",
                              borderwidth=2, borderrelief=tk.RAISED)
        theme_btn.pack(side=tk.LEFT, padx=5)
        
        # Разделитель
        separator = tk.Frame(btn_frame, bg=self.colors["border"], width=2)
        separator.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Кнопки переключения языка - только одна может быть активна
        self.lang_button_ru = tk.Button(btn_frame, text=self.localization.get("lang_btn_ru"), command=lambda: self.set_language("ru"),
                                        bg=self.colors["accent"], fg="#FFFFFF",
                                        font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=10, pady=5,
                                        activebackground=self.colors["accent"], activeforeground="#FFFFFF",
                                        borderwidth=2, borderrelief=tk.RAISED)
        self.lang_button_ru.pack(side=tk.LEFT, padx=2)
        
        self.lang_button_en = tk.Button(btn_frame, text=self.localization.get("lang_btn_en"), command=lambda: self.set_language("en"),
                                        bg=self.colors["button_bg"], fg=self.colors["button_fg"],
                                        font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=10, pady=5,
                                        activebackground=self.colors["accent"], activeforeground="#FFFFFF",
                                        borderwidth=2, borderrelief=tk.RAISED)
        self.lang_button_en.pack(side=tk.LEFT, padx=2)
        
        # Обновляем состояние кнопок языка
        self.update_language_buttons()

    def create_main_area(self):
        self.main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.content_frame = tk.Frame(self.main_frame, bg=self.colors["frame_bg"], relief=tk.RAISED, borderwidth=2)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Инструкция
        self.info_label = tk.Label(self.content_frame, 
                              text=self.localization.get("info_text"),
                              font=("Segoe UI", 12), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                              justify=tk.CENTER, pady=20)
        self.info_label.pack(anchor=tk.N)
        
        # Большая кнопка выбора файла
        self.select_btn = tk.Button(self.content_frame, text=self.localization.get("select_file_btn"), command=self.select_file,
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
        self.run_btn = tk.Button(self.content_frame, text=self.localization.get("run_analysis_btn"), command=self.start_analysis,
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

    def set_language(self, lang):
        """Установка языка и обновление всех текстов"""
        self.language = lang
        self.localization.set_language(lang)
        
        # Обновляем состояние кнопок языка - только одна активна
        self.update_language_buttons()
        
        # Обновляем все тексты в интерфейсе
        self.update_ui_texts()
        
        # Обновляем окно результатов если оно открыто
        if self.result_window:
            self.result_window.destroy()
            self.result_window = None

    def update_language_buttons(self):
        """Обновление визуального состояния кнопок языка"""
        if self.lang_button_ru and self.lang_button_en:
            if self.language == "ru":
                self.lang_button_ru.configure(bg=self.colors["accent"], fg="#FFFFFF")
                self.lang_button_en.configure(bg=self.colors["button_bg"], fg=self.colors["button_fg"])
            else:
                self.lang_button_en.configure(bg=self.colors["accent"], fg="#FFFFFF")
                self.lang_button_ru.configure(bg=self.colors["button_bg"], fg=self.colors["button_fg"])

    def update_ui_texts(self):
        """Обновление всех текстов в интерфейсе при смене языка"""
        # Основное окно
        if hasattr(self, 'info_label'):
            self.info_label.configure(text=self.localization.get("info_text"))
        if hasattr(self, 'select_btn'):
            self.select_btn.configure(text=self.localization.get("select_file_btn"))
        if hasattr(self, 'run_btn') and not self.is_analyzing:
            self.run_btn.configure(text=self.localization.get("run_analysis_btn"))
        
        # Статус бар - обновляем только если не идет анализ
        if hasattr(self, 'status_var') and not self.is_analyzing:
            self.status_var.set(self.localization.get("status_ready"))
        
        # Обновляем кнопки в верхней панели
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        text = child.cget("text")
                        if "⚙️" in text:
                            child.configure(text=self.localization.get("settings_btn"))
                        elif "📊" in text:
                            child.configure(text=self.localization.get("reports_btn"))
                        elif "🌓" in text:
                            child.configure(text=self.localization.get("theme_btn"))

    def select_file(self):
        title = self.localization.get("file_dialog_title")
        all_files = self.localization.get("all_files")
        exe_files = self.localization.get("exe_files")
        script_files = self.localization.get("script_files")
        
        filename = filedialog.askopenfilename(title=title,
                                              filetypes=[(all_files, "*.*"), (exe_files, "*.exe"), (script_files, "*.bat *.cmd *.ps1 *.vbs")])
        if filename:
            self.file_path_var.set(filename)
            self.run_btn.config(state=tk.NORMAL)
            prefix = self.localization.get("status_file_selected")
            self.status_var.set(f"{prefix}{os.path.basename(filename)}")

    def start_analysis(self):
        if not self.file_path_var.get():
            return
        
        self.is_analyzing = True
        self.analysis_complete = False
        analyzing_text = self.localization.get("analyzing_btn")
        self.run_btn.config(state=tk.DISABLED, text=analyzing_text)
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
                self.status_var.set(self.localization.get("status_scanning_sigs"))
            elif i == 60:
                self.status_var.set(self.localization.get("status_heuristic"))
            elif i == 80:
                self.status_var.set(self.localization.get("status_behavior"))
        
        self.analysis_complete = True
        self.is_analyzing = False
        self.root.after(100, self.show_results)

    def show_results(self):
        run_text = self.localization.get("run_analysis_btn")
        self.run_btn.config(state=tk.NORMAL, text=run_text)
        self.select_btn.config(state=tk.NORMAL)
        self.status_var.set(self.localization.get("status_complete"))
        
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
            verdict = self.localization.get("verdict_danger")
            family = self.localization.get("danger_family")
            description = self.localization.get("danger_desc")
            detection_method = self.localization.get("danger_method")
            recommendations = [
                self.localization.get("danger_rec_1"),
                self.localization.get("danger_rec_2"),
                self.localization.get("danger_rec_3"),
                self.localization.get("danger_rec_4"),
                self.localization.get("danger_rec_5")
            ]
            return {
                "verdict": verdict,
                "color": self.colors["danger"],
                "threat_name": f"Trojan.Win32.Generic.{random.randint(1000,9999)}",
                "family": family,
                "description": description,
                "detection_method": detection_method,
                "recommendations": recommendations
            }
        elif risk == "suspicious":
            verdict = self.localization.get("verdict_suspicious")
            family = self.localization.get("suspicious_family")
            description = self.localization.get("suspicious_desc")
            detection_method = self.localization.get("suspicious_method")
            recommendations = [
                self.localization.get("suspicious_rec_1"),
                self.localization.get("suspicious_rec_2"),
                self.localization.get("suspicious_rec_3"),
                self.localization.get("suspicious_rec_4")
            ]
            return {
                "verdict": verdict,
                "color": self.colors["warn"],
                "threat_name": "Heuristic.Suspicious.Tool",
                "family": family,
                "description": description,
                "detection_method": detection_method,
                "recommendations": recommendations
            }
        else:
            verdict = self.localization.get("verdict_safe")
            threat_name = self.localization.get("threat_no_threats")
            family = self.localization.get("threat_clean_file")
            description = self.localization.get("desc_safe")
            method = self.localization.get("method_safe")
            recommendations = [
                self.localization.get("rec_safe_1"),
                self.localization.get("rec_safe_2"),
                self.localization.get("rec_safe_3"),
                self.localization.get("rec_safe_4")
            ]
            return {
                "verdict": verdict,
                "color": self.colors["safe"],
                "threat_name": threat_name,
                "family": family,
                "description": description,
                "detection_method": method,
                "recommendations": recommendations
            }

    def create_result_window(self, data):
        if self.result_window:
            self.result_window.destroy()
            
        self.result_window = tk.Toplevel(self.root)
        self.result_window.title(self.localization.get("result_title"))
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
        
        verdict_text = f"{self.localization.get('verdict_label')}{data['details']['verdict']}"
        verdict_label = tk.Label(verdict_frame, text=verdict_text, 
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
        tab_control.add(tab_main, text=self.localization.get("tab_main"))
        self.create_main_result_tab(tab_main, data)
        
        # Вкладка 2: О вирусе
        tab_virus = tk.Frame(tab_control, bg=self.colors["frame_bg"])
        tab_control.add(tab_virus, text=self.localization.get("tab_virus"))
        self.create_virus_info_tab(tab_virus, data)
        
        # Вкладка 3: Справка
        tab_help = tk.Frame(tab_control, bg=self.colors["frame_bg"])
        tab_control.add(tab_help, text=self.localization.get("tab_help"))
        self.create_help_tab(tab_help)
        
        # Кнопка закрыть
        close_btn = tk.Button(self.result_window, text=self.localization.get("close_btn"), command=on_close,
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
        info_box = tk.LabelFrame(scrollable_frame, text=self.localization.get("file_info_title"), 
                                 font=("Segoe UI", 12, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                 padx=15, pady=15)
        info_box.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(info_box, text=self.localization.get("file_name_label"), font=("Segoe UI", 11, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"]).pack(anchor=tk.W)
        tk.Label(info_box, text=data["file"], font=("Consolas", 10), bg=self.colors["frame_bg"], fg=self.colors["text_highlight"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W, pady=(0,10))
        
        tk.Label(info_box, text=self.localization.get("file_path_label"), font=("Segoe UI", 11, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"]).pack(anchor=tk.W)
        tk.Label(info_box, text=data["path"], font=("Consolas", 9), bg=self.colors["frame_bg"], fg=self.colors["text_highlight"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W, pady=(0,10))
        
        tk.Label(info_box, text=self.localization.get("scan_date_label"), font=("Segoe UI", 11, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"]).pack(anchor=tk.W)
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
        name_frame = tk.LabelFrame(scrollable_frame, text=self.localization.get("threat_title"), 
                                   font=("Segoe UI", 12, "bold"), bg=self.colors["frame_bg"], fg=details["color"],
                                   padx=padding, pady=padding)
        name_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(name_frame, text=details["threat_name"], font=("Segoe UI", 14, "bold"), 
                 bg=self.colors["frame_bg"], fg=self.colors["fg"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W)
        family_label_text = self.localization.get("family_label")
        tk.Label(name_frame, text=f"{family_label_text}{details['family']}", font=("Segoe UI", 11), 
                 bg=self.colors["frame_bg"], fg=self.colors["fg"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W, pady=(5,0))

        # Описание
        desc_frame = tk.LabelFrame(scrollable_frame, text=self.localization.get("description_title"), 
                                   font=("Segoe UI", 12, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                   padx=padding, pady=padding)
        desc_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(desc_frame, text=details["description"], font=("Segoe UI", 11), 
                 bg=self.colors["frame_bg"], fg=self.colors["fg"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W)

        # Метод обнаружения
        method_frame = tk.LabelFrame(scrollable_frame, text=self.localization.get("method_title"), 
                                     font=("Segoe UI", 12, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                     padx=padding, pady=padding)
        method_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(method_frame, text=details["detection_method"], font=("Segoe UI", 11), 
                 bg=self.colors["frame_bg"], fg=self.colors["fg"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W)

        # Рекомендации
        rec_frame = tk.LabelFrame(scrollable_frame, text=self.localization.get("recommendations_title"), 
                                  font=("Segoe UI", 12, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                  padx=padding, pady=padding)
        rec_frame.pack(fill=tk.X, padx=20, pady=10)
        
        for i, rec in enumerate(details["recommendations"], 1):
            rec_text = f"{i}. {rec}"
            # Проверка на важность рекомендации для обоих языков
            is_urgent = ("НЕ" in rec or "УДАЛИ" in rec.upper() or 
                        "DELETE" in rec.upper() or "IMMEDIATELY" in rec.upper())
            color = details["color"] if is_urgent else self.colors["fg"]
            tk.Label(rec_frame, text=rec_text, font=("Segoe UI", 11, "bold" if is_urgent else "normal"), 
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
        
        # Формируем текст справки с использованием локализации
        help_lines = [
            self.localization.get("help_title"),
            "",
            self.localization.get("help_usage_title"),
            f"1. {self.localization.get('help_step1')}",
            f"2. {self.localization.get('help_step2')}",
            f"3. {self.localization.get('help_step3')}",
            f"4. {self.localization.get('help_step4')}",
            f"5. {self.localization.get('help_step5')}",
            "",
            self.localization.get("help_theme_title"),
            self.localization.get("help_theme_desc"),
            "",
            self.localization.get("help_settings_title"),
            self.localization.get("help_settings_desc"),
            "",
            self.localization.get("help_reports_title"),
            self.localization.get("help_reports_desc"),
            "",
            self.localization.get("help_verdicts_title"),
            self.localization.get("help_safe"),
            self.localization.get("help_suspicious"),
            self.localization.get("help_danger"),
            "",
            self.localization.get("help_about_title"),
            self.localization.get("help_about_desc"),
        ]
        
        help_text = "\n        ".join(help_lines)
        
        label = tk.Label(scrollable_frame, text=help_text, font=("Segoe UI", 11), 
                         bg=self.colors["frame_bg"], fg=self.colors["fg"], 
                         justify=tk.LEFT, anchor=tk.W, padx=20, pady=20)
        label.pack()

    def open_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title(self.localization.get("settings_title"))
        settings_win.geometry("500x400")
        settings_win.configure(bg=self.colors["bg"])
        settings_win.transient(self.root)
        
        frame = tk.Frame(settings_win, bg=self.colors["frame_bg"], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text=self.localization.get("settings_header"), font=("Segoe UI", 16, "bold"), 
                 bg=self.colors["frame_bg"], fg=self.colors["accent"]).pack(pady=10)
        
        # Опции с локализацией
        opts = [
            self.localization.get("opt_auto_update"),
            self.localization.get("opt_deep_scan"),
            self.localization.get("opt_scan_archives"),
            self.localization.get("opt_show_help")
        ]
        
        vars_list = []
        for opt in opts:
            var = tk.BooleanVar(value=True)
            vars_list.append(var)
            cb = tk.Checkbutton(frame, text=opt, variable=var, 
                                bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                selectcolor=self.colors["bg"], font=("Segoe UI", 11))
            cb.pack(anchor=tk.W, pady=5)
            
        # Справка внизу с локализацией
        help_lbl = tk.Label(frame, text=self.localization.get("settings_help"),
                            font=("Segoe UI", 10, "italic"), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                            justify=tk.CENTER, pady=20)
        help_lbl.pack(side=tk.BOTTOM)
        
        tk.Button(frame, text=self.localization.get("close_btn"), command=settings_win.destroy,
                  bg=self.colors["accent"], fg="#FFFFFF", font=("Segoe UI", 12, "bold"),
                  relief=tk.FLAT, padx=20, pady=10).pack(side=tk.BOTTOM, pady=10)

    def open_reports(self):
        rep_win = tk.Toplevel(self.root)
        rep_win.title(self.localization.get("reports_title"))
        rep_win.geometry("600x400")
        rep_win.configure(bg=self.colors["bg"])
        rep_win.transient(self.root)
        
        frame = tk.Frame(rep_win, bg=self.colors["frame_bg"], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text=self.localization.get("reports_header"), font=("Segoe UI", 16, "bold"), 
                 bg=self.colors["frame_bg"], fg=self.colors["accent"]).pack(pady=10)
        
        text = scrolledtext.ScrolledText(frame, font=("Consolas", 10), bg=self.colors["bg"], fg=self.colors["fg"])
        text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        reports_empty = self.localization.get("reports_empty")
        text.insert(tk.END, reports_empty)
        
        tk.Button(frame, text=self.localization.get("close_btn"), command=rep_win.destroy,
                  bg=self.colors["accent"], fg="#FFFFFF", font=("Segoe UI", 12, "bold"),
                  relief=tk.FLAT, padx=20, pady=10).pack(pady=10)

    def on_closing(self):
        if self.is_analyzing:
            if messagebox.askokcancel(self.localization.get("exit_title"), self.localization.get("exit_confirm")):
                self.is_analyzing = False
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RedSandApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
