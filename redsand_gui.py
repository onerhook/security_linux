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
        title_label = tk.Label(top_frame, text="🛡️ RedSand Secure", font=("Segoe UI", 18, "bold"), 
                               bg=self.colors["frame_bg"], fg=self.colors["accent"])
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Кнопки справа
        btn_frame = tk.Frame(top_frame, bg=self.colors["frame_bg"])
        btn_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        settings_btn = tk.Button(btn_frame, text="⚙️ Настройки", command=self.open_settings,
                                 bg=self.colors["button_bg"], fg=self.colors["button_fg"],
                                 font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15, pady=5,
                                 activebackground=self.colors["accent"], activeforeground="#FFFFFF",
                                 borderwidth=2, borderrelief=tk.RAISED)
        settings_btn.pack(side=tk.LEFT, padx=5)
        
        reports_btn = tk.Button(btn_frame, text="📊 Отчеты", command=self.open_reports,
                                bg=self.colors["button_bg"], fg=self.colors["button_fg"],
                                font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15, pady=5,
                                activebackground=self.colors["accent"], activeforeground="#FFFFFF",
                                borderwidth=2, borderrelief=tk.RAISED)
        reports_btn.pack(side=tk.LEFT, padx=5)
        
        # Переключатель темы
        theme_btn = tk.Button(btn_frame, text="🌓 Тема", command=self.toggle_theme,
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
                              text="Выберите файл для проверки на вирусы.\nСистема автоматически обнаружит угрозы и даст рекомендации.",
                              font=("Segoe UI", 12), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                              justify=tk.CENTER, pady=20)
        info_label.pack(anchor=tk.N)
        
        # Большая кнопка выбора файла
        self.select_btn = tk.Button(self.content_frame, text="📁 ВЫБРАТЬ ФАЙЛ", command=self.select_file,
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
        self.run_btn = tk.Button(self.content_frame, text="🚀 ЗАПУСТИТЬ АНАЛИЗ", command=self.start_analysis,
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
        filename = filedialog.askopenfilename(title="Выберите файл для анализа",
                                              filetypes=[("Все файлы", "*.*"), ("EXE файлы", "*.exe"), ("Script files", "*.bat *.cmd *.ps1 *.vbs")])
        if filename:
            self.file_path_var.set(filename)
            self.run_btn.config(state=tk.NORMAL)
            self.status_var.set(f"Файл выбран: {os.path.basename(filename)}")

    def start_analysis(self):
        if not self.file_path_var.get():
            return
        
        self.is_analyzing = True
        self.analysis_complete = False
        self.run_btn.config(state=tk.DISABLED, text="⏳ АНАЛИЗ...")
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
        self.run_btn.config(state=tk.NORMAL, text="🚀 ЗАПУСТИТЬ АНАЛИЗ")
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
                "verdict": "ОПАСНО",
                "color": self.colors["danger"],
                "threat_name": f"Trojan.Win32.Generic.{random.randint(1000,9999)}",
                "family": "Семейство троянов-загрузчиков",
                "description": "Этот файл является вредоносной программой, маскирующейся под легитимное приложение. При запуске он пытается внедриться в системные процессы, украсть ваши пароли и зашифровать личные данные.",
                "detection_method": "Обнаружен по уникальной цифровой подписи (сигнатуре) в базе данных вирусов. Также выявлено подозрительное поведение: попытка скрытого подключения к интернету и модификация реестра.",
                "recommendations": [
                    "НЕМЕДЛЕННО УДАЛИТЕ ЭТОТ ФАЙЛ!",
                    "Не пытайтесь его открывать или запускать.",
                    "Проверьте компьютер полным сканированием антивируса.",
                    "Если вы уже запустили файл, смените все важные пароли.",
                    "Проверьте банковские счета на наличие подозрительных операций."
                ]
            }
        elif risk == "suspicious":
            return {
                "verdict": "ПОДОЗРИТЕЛЬНО",
                "color": self.colors["warn"],
                "threat_name": "Heuristic.Suspicious.Tool",
                "family": "Инструменты администрирования / Потенциально нежелательное ПО",
                "description": "Файл содержит код, который может использоваться как во благо, так и во вред. Это может быть инструмент для взлома, майнер или программа для скрытого наблюдения. Сам по себе он не является вирусом, но несет риски.",
                "detection_method": "Выявлено подозрительное поведение при эвристическом анализе. Файл пытается получить права администратора без явной необходимости и скрывает свои процессы.",
                "recommendations": [
                    "Лучше не использовать этот файл, если вы не уверены в источнике на 100%.",
                    "Удалите файл, если вы не скачивали его специально.",
                    "Если файл нужен, запустите его в изолированной среде (песочнице).",
                    "Проверьте цифровую подпись издателя (скорее всего её нет)."
                ]
            }
        else:
            return {
                "verdict": "БЕЗОПАСНО",
                "color": self.colors["safe"],
                "threat_name": "Нет угроз",
                "family": "Чистый файл",
                "description": "Файл прошел все проверки. В нем не обнаружено известных вирусов, троянов или подозрительного кода. Цифровая подпись (если есть) действительна.",
                "detection_method": "Сравнение с базой известных вирусов не дало совпадений. Поведенческий анализ не выявил опасных действий.",
                "recommendations": [
                    "Файл можно использовать.",
                    "Все равно соблюдайте базовую осторожность.",
                    "Убедитесь, что файл скачан с официального сайта.",
                    "Храните резервные копии важных данных."
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
        tab_control.add(tab_main, text="🏠 Главная")
        self.create_main_result_tab(tab_main, data)
        
        # Вкладка 2: О вирусе
        tab_virus = tk.Frame(tab_control, bg=self.colors["frame_bg"])
        tab_control.add(tab_virus, text="🦠 О вирусе")
        self.create_virus_info_tab(tab_virus, data)
        
        # Вкладка 3: Справка
        tab_help = tk.Frame(tab_control, bg=self.colors["frame_bg"])
        tab_control.add(tab_help, text="❓ Справка")
        self.create_help_tab(tab_help)
        
        # Кнопка закрыть
        close_btn = tk.Button(self.result_window, text="ЗАКРЫТЬ", command=on_close,
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
        info_box = tk.LabelFrame(scrollable_frame, text="📄 Информация о файле", 
                                 font=("Segoe UI", 12, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                 padx=15, pady=15)
        info_box.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(info_box, text=f"Имя файла:", font=("Segoe UI", 11, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"]).pack(anchor=tk.W)
        tk.Label(info_box, text=data["file"], font=("Consolas", 10), bg=self.colors["frame_bg"], fg=self.colors["text_highlight"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W, pady=(0,10))
        
        tk.Label(info_box, text="Полный путь:", font=("Segoe UI", 11, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"]).pack(anchor=tk.W)
        tk.Label(info_box, text=data["path"], font=("Consolas", 9), bg=self.colors["frame_bg"], fg=self.colors["text_highlight"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W, pady=(0,10))
        
        tk.Label(info_box, text="Дата проверки:", font=("Segoe UI", 11, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"]).pack(anchor=tk.W)
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
        name_frame = tk.LabelFrame(scrollable_frame, text="🦠 Обнаруженная угроза", 
                                   font=("Segoe UI", 12, "bold"), bg=self.colors["frame_bg"], fg=details["color"],
                                   padx=padding, pady=padding)
        name_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(name_frame, text=details["threat_name"], font=("Segoe UI", 14, "bold"), 
                 bg=self.colors["frame_bg"], fg=self.colors["fg"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W)
        tk.Label(name_frame, text=f"Семейство: {details['family']}", font=("Segoe UI", 11), 
                 bg=self.colors["frame_bg"], fg=self.colors["fg"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W, pady=(5,0))

        # Описание
        desc_frame = tk.LabelFrame(scrollable_frame, text="📖 Что это такое?", 
                                   font=("Segoe UI", 12, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                   padx=padding, pady=padding)
        desc_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(desc_frame, text=details["description"], font=("Segoe UI", 11), 
                 bg=self.colors["frame_bg"], fg=self.colors["fg"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W)

        # Метод обнаружения
        method_frame = tk.LabelFrame(scrollable_frame, text="🔍 Как мы это нашли?", 
                                     font=("Segoe UI", 12, "bold"), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                     padx=padding, pady=padding)
        method_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(method_frame, text=details["detection_method"], font=("Segoe UI", 11), 
                 bg=self.colors["frame_bg"], fg=self.colors["fg"], wraplength=600, justify=tk.LEFT).pack(anchor=tk.W)

        # Рекомендации
        rec_frame = tk.LabelFrame(scrollable_frame, text="✅ Что делать? (Инструкция)", 
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
        
        help_text = """
        ❓ СПРАВКА ПО ИСПОЛЬЗОВАНИЮ
        
        📌 Как пользоваться программой:
        1. Нажмите кнопку "ВЫБРАТЬ ФАЙЛ".
        2. Выберите подозрительный файл на компьютере.
        3. Нажмите "ЗАПУСТИТЬ АНАЛИЗ".
        4. Дождитесь окончания проверки.
        5. Изучите вердикт и рекомендации.
        
        🎨 Темы оформления:
        Нажмите кнопку "Тема" сверху, чтобы переключить светлую/темную тему.
        
        ⚙️ Настройки:
        В разделе настроек вы можете изменить параметры сканирования.
        
        📊 Отчеты:
        Здесь сохраняется история последних проверок.
        
        🛡️ Интерпретация результатов:
        - БЕЗОПАСНО (Зеленый): Файл чист, можно использовать.
        - ПОДОЗРИТЕЛЬНО (Желтый): Есть сомнения. Лучше удалить, если не знаете источник.
        - ОПАСНО (Красный): Вирус найден! Немедленно удалите файл!
        
        ℹ️ О программе:
        RedSand Secure использует современные методы эвристического анализа
        и базу сигнатур для защиты вашего компьютера.
        """
        
        label = tk.Label(scrollable_frame, text=help_text, font=("Segoe UI", 11), 
                         bg=self.colors["frame_bg"], fg=self.colors["fg"], 
                         justify=tk.LEFT, anchor=tk.W, padx=20, pady=20)
        label.pack()

    def open_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Настройки")
        settings_win.geometry("500x400")
        settings_win.configure(bg=self.colors["bg"])
        settings_win.transient(self.root)
        
        frame = tk.Frame(settings_win, bg=self.colors["frame_bg"], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="⚙️ НАСТРОЙКИ ПРОГРАММЫ", font=("Segoe UI", 16, "bold"), 
                 bg=self.colors["frame_bg"], fg=self.colors["accent"]).pack(pady=10)
        
        # Опции
        opts = [
            "Автоматическая проверка обновлений",
            "Глубокий анализ (медленнее, но точнее)",
            "Проверять архивы внутри файлов",
            "Показывать справку после каждого анализа"
        ]
        
        vars_list = []
        for opt in opts:
            var = tk.BooleanVar(value=True)
            vars_list.append(var)
            cb = tk.Checkbutton(frame, text=opt, variable=var, 
                                bg=self.colors["frame_bg"], fg=self.colors["fg"],
                                selectcolor=self.colors["bg"], font=("Segoe UI", 11))
            cb.pack(anchor=tk.W, pady=5)
            
        # Справка внизу
        help_lbl = tk.Label(frame, text="ℹ️ Здесь вы можете настроить поведение сканера.\nРекомендуется оставить все галочки включенными для максимальной защиты.",
                            font=("Segoe UI", 10, "italic"), bg=self.colors["frame_bg"], fg=self.colors["fg"],
                            justify=tk.CENTER, pady=20)
        help_lbl.pack(side=tk.BOTTOM)
        
        tk.Button(frame, text="ЗАКРЫТЬ", command=settings_win.destroy,
                  bg=self.colors["accent"], fg="#FFFFFF", font=("Segoe UI", 12, "bold"),
                  relief=tk.FLAT, padx=20, pady=10).pack(side=tk.BOTTOM, pady=10)

    def open_reports(self):
        rep_win = tk.Toplevel(self.root)
        rep_win.title("Отчеты")
        rep_win.geometry("600x400")
        rep_win.configure(bg=self.colors["bg"])
        rep_win.transient(self.root)
        
        frame = tk.Frame(rep_win, bg=self.colors["frame_bg"], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="📊 ИСТОРИЯ ОТЧЕТОВ", font=("Segoe UI", 16, "bold"), 
                 bg=self.colors["frame_bg"], fg=self.colors["accent"]).pack(pady=10)
        
        text = scrolledtext.ScrolledText(frame, font=("Consolas", 10), bg=self.colors["bg"], fg=self.colors["fg"])
        text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        text.insert(tk.END, "Здесь будет отображаться история ваших сканирований.\n")
        text.insert(tk.END, "Пока что отчетов нет.\n")
        text.insert(tk.END, "\nПример будущего отчета:\n[2023-10-27 12:00] Файл: test.exe - ОПАСНО (Trojan)\n")
        
        tk.Button(frame, text="ЗАКРЫТЬ", command=rep_win.destroy,
                  bg=self.colors["accent"], fg="#FFFFFF", font=("Segoe UI", 12, "bold"),
                  relief=tk.FLAT, padx=20, pady=10).pack(pady=10)

    def on_closing(self):
        if self.is_analyzing:
            if messagebox.askokcancel("Выход", "Анализ еще идет. Вы действительно хотите выйти?"):
                self.is_analyzing = False
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RedSandApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
