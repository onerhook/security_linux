#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Poly Engine - Модуль полиморфизма
Генерация уникальных вариантов тестовых образцов с одинаковым поведением
"""

import os
import random
import string
import shutil
import hashlib
from pathlib import Path
from typing import List, Dict

class PolyEngine:
    def __init__(self):
        self.variants_generated = 0
        self.output_dir = Path("test_samples/poly_variants")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_variants(self, source_file: str, count: int = 3) -> List[Dict]:
        """Генерация полиморфных вариантов файла"""
        variants = []
        source_path = Path(source_file)
        
        if not source_path.exists():
            return variants
        
        for i in range(count):
            try:
                variant_info = self._create_variant(source_path, i)
                variants.append(variant_info)
                self.variants_generated += 1
            except Exception as e:
                print(f"⚠️  Ошибка создания варианта {i}: {e}")
        
        return variants
    
    def _create_variant(self, source_path: Path, index: int) -> Dict:
        """Создание одного полиморфного варианта"""
        # Генерация уникального имени
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        variant_name = f"{source_path.stem}_poly{index}_{suffix}{source_path.suffix}"
        variant_path = self.output_dir / variant_name
        
        # Копирование файла с модификациями
        self._modify_file_copy(source_path, variant_path)
        
        # Вычисление хешей
        hashes = self._calculate_hashes(variant_path)
        
        variant_info = {
            "original": str(source_path),
            "variant": str(variant_path),
            "hashes": hashes,
            "size": variant_path.stat().st_size,
            "modification_type": "padding_and_rename"
        }
        
        return variant_info
    
    def _modify_file_copy(self, source: Path, dest: Path):
        """Модификация копии файла (добавление паддинга)"""
        with open(source, 'rb') as f:
            content = bytearray(f.read())
        
        # Добавление случайного паддинга в конец
        padding_length = random.randint(100, 1000)
        padding = bytes(random.randint(0, 255) for _ in range(padding_length))
        content.extend(padding)
        
        # Запись модифицированного файла
        with open(dest, 'wb') as f:
            f.write(content)
    
    def _calculate_hashes(self, file_path: Path) -> Dict[str, str]:
        """Вычисление хешей файла"""
        hashes = {}
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # MD5
        hashes['md5'] = hashlib.md5(content).hexdigest()
        
        # SHA1
        hashes['sha1'] = hashlib.sha1(content).hexdigest()
        
        # SHA256
        hashes['sha256'] = hashlib.sha256(content).hexdigest()
        
        return hashes
    
    def generate_python_simulator(self, threat_type: str, output_name: str = None) -> str:
        """Генерация безопасного симулятора поведения угрозы на Python"""
        
        simulators = {
            "ransomware": '''
# Симулятор Ransomware (БЕЗОПАСНЫЙ)
import time
import os

def simulate_ransomware_behavior():
    """Эмуляция поведения ransomware без реального шифрования"""
    print("[RANSOMWARE SIM] Начало эмуляции...")
    
    # Эмуляция поиска файлов
    target_extensions = ['.doc', '.docx', '.xls', '.xlsx', '.pdf', '.jpg', '.png']
    print(f"[RANSOMWARE SIM] Поиск файлов с расширениями: {target_extensions}")
    
    # Эмуляция шифрования (только логирование)
    for i in range(5):
        fake_file = f"document_{i}.docx"
        print(f"[RANSOMWARE SIM] 'Шифрование' файла: {fake_file}")
        time.sleep(0.5)
    
    # Эмуляция создания ransom note
    print("[RANSOMWARE SIM] Создание 'ransom_note.txt'")
    print("[RANSOMWARE SIM] Эмуляция завершена!")

if __name__ == "__main__":
    simulate_ransomware_behavior()
''',
            "stealer": '''
# Симулятор Stealer (БЕЗОПАСНЫЙ)
import time

def simulate_stealer_behavior():
    """Эмуляция поведения стилера без кражи реальных данных"""
    print("[STEALER SIM] Начало эмуляции...")
    
    # Эмуляция сбора данных
    targets = [
        "browser_passwords",
        "cookies", 
        "crypto_wallets",
        "system_info",
        "clipboard_data"
    ]
    
    for target in targets:
        print(f"[STEALER SIM] 'Сбор' данных: {target}")
        time.sleep(0.3)
    
    # Эмуляция отправки данных
    print("[STEALER SIM] 'Отправка' данных на C&C сервер...")
    print("[STEALER SIM] Эмуляция завершена!")

if __name__ == "__main__":
    simulate_stealer_behavior()
''',
            "miner": '''
# Симулятор Miner (БЕЗОПАСНЫЙ)
import time
import random

def simulate_miner_behavior():
    """Эмуляция майнера без реальной нагрузки на CPU/GPU"""
    print("[MINER SIM] Начало эмуляции...")
    
    # Эмуляция подключения к пулу
    print("[MINER SIM] Подключение к mining pool...")
    time.sleep(0.5)
    
    # Эмуляция майнинга
    for i in range(10):
        fake_hashrate = random.uniform(10.5, 99.9)
        fake_shares = random.randint(1, 50)
        print(f"[MINER SIM] Хешрейт: {fake_hashrate:.2f} H/s, Принято шар: {fake_shares}")
        time.sleep(0.5)
    
    print("[MINER SIM] Эмуляция завершена!")

if __name__ == "__main__":
    simulate_miner_behavior()
''',
            "rat": '''
# Симулятор RAT (БЕЗОПАСНЫЙ)
import time

def simulate_rat_behavior():
    """Эмуляция Remote Access Trojan без реального доступа"""
    print("[RAT SIM] Начало эмуляции...")
    
    commands = [
        "get_system_info",
        "list_processes",
        "capture_screen",
        "keylog_start",
        "file_browser",
        "webcam_capture",
        "microphone_record"
    ]
    
    print("[RAT SIM] Ожидание команд от C&C...")
    time.sleep(0.5)
    
    for cmd in commands:
        print(f"[RAT SIM] Выполнение команды: {cmd}")
        time.sleep(0.3)
    
    print("[RAT SIM] Эмуляция завершена!")

if __name__ == "__main__":
    simulate_rat_behavior()
''',
            "worm": '''
# Симулятор Worm (БЕЗОПАСНЫЙ)
import time
import random

def simulate_worm_behavior():
    """Эмуляция червя без реального распространения"""
    print("[WORM SIM] Начало эмуляции...")
    
    # Эмуляция сканирования сети
    print("[WORM SIM] Сканирование локальной сети...")
    for i in range(5):
        fake_ip = f"192.168.1.{random.randint(1, 254)}"
        print(f"[WORM SIM] Найден узел: {fake_ip}")
        time.sleep(0.3)
    
    # Эмуляция распространения
    print("[WORM SIM] Попытка распространения...")
    for i in range(3):
        print(f"[WORM SIM] 'Заражение' узла {i+1}/3")
        time.sleep(0.5)
    
    print("[WORM SIM] Эмуляция завершена!")

if __name__ == "__main__":
    simulate_worm_behavior()
'''
        }
        
        if threat_type.lower() not in simulators:
            raise ValueError(f"Неизвестный тип угрозы: {threat_type}")
        
        if output_name is None:
            output_name = f"sim_{threat_type}_{random.randint(1000, 9999)}.py"
        
        output_path = self.output_dir / output_name
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(simulators[threat_type.lower()])
        
        return str(output_path)
    
    def get_stats(self) -> Dict:
        """Получение статистики"""
        return {
            "variants_generated": self.variants_generated,
            "output_directory": str(self.output_dir),
            "files_count": len(list(self.output_dir.glob("*"))) if self.output_dir.exists() else 0
        }
