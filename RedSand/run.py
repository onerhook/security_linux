#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Secure - Точка входа
Запуск GUI или CLI версии
"""

import sys
import os
import argparse

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(__file__))

def main():
    parser = argparse.ArgumentParser(description='RedSand Secure Sandbox')
    parser.add_argument('--gui', action='store_true', help='Запустить GUI интерфейс')
    parser.add_argument('--cli', action='store_true', help='Запустить CLI версию')
    parser.add_argument('--file', type=str, help='Файл для анализа (CLI режим)')
    parser.add_argument('--output', type=str, default='reports', help='Папка для отчетов')
    
    args = parser.parse_args()
    
    # По умолчанию запускаем GUI
    if args.gui or not (args.gui or args.cli):
        try:
            from gui.main_gui import RedSandGUI
            from PyQt5.QtWidgets import QApplication
            app = QApplication(sys.argv)
            window = RedSandGUI()
            window.show()
            sys.exit(app.exec_())
        except ImportError as e:
            print(f"Ошибка запуска GUI: {e}")
            print("Убедитесь, что PyQt5 установлен: pip install PyQt5")
            sys.exit(1)
    
    elif args.cli:
        from core.orchestrator import RedSandSecure
        
        if not args.file:
            print("Ошибка: укажите файл для анализа через --file")
            sys.exit(1)
        
        sandbox = RedSandSecure(output_dir=args.output)
        result = sandbox.analyze_file(args.file)
        
        if result.success:
            print(f"\n✓ Анализ завершен успешно!")
            print(f"Вердикт: {result.threat_info.get('verdict', 'UNKNOWN')}")
            print(f"Тип угрозы: {result.threat_info.get('threat_type', 'N/A')}")
            print(f"Уровень опасности: {result.threat_info.get('severity', 'N/A')}")
            print(f"Отчет сохранен в: {result.report_path}")
        else:
            print(f"\n✗ Ошибка анализа: {result.error}")
            sys.exit(1)

if __name__ == '__main__':
    main()
