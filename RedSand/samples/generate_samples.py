#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор безопасных тестовых образцов вирусов
Создает симуляции различных типов угроз для проверки системы
ВНИМАНИЕ: Это НЕ настоящие вирусы, а безопасные симуляции!
"""

import os
import random
import string
import json
from pathlib import Path
from datetime import datetime

SAMPLES_DIR = Path(__file__).parent
THREAT_TYPES = ['trojan', 'ransomware', 'spyware', 'adware', 'worm', 'rootkit', 'miner']

def random_string(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_fake_exe(filename: str, threat_type: str):
    """Создает безопасный EXE-файл с сигнатурами угрозы."""
    content = f"""MZ_HEADER_SIMULATION
THREAT_TYPE: {threat_type.upper()}
GENERATED: {datetime.now().isoformat()}
RANDOM_ID: {random_string(12)}

[MOCK_BEHAVIOR]
- Network: false
- Filesystem: false
- Registry: false
- Process: false

[SIGNATURE]
This is a SAFE test file for RedSand Sandbox testing.
NOT A REAL MALWARE!
"""
    with open(filename, 'w') as f:
        f.write(content)
    print(f"✓ Создан: {filename}")

def create_fake_sys(filename: str):
    """Создает безопасный SYS-файл (rootkit симуляция)."""
    content = f"""DRIVER_HEADER_SIMULATION
TYPE: ROOTKIT_MOCK
GENERATED: {datetime.now().isoformat()}
RANDOM_ID: {random_string(12)}

[MOCK_BEHAVIOR]
- Kernel hooks: false
- SSDT modifications: false
- Hidden files: false

[NOTE]
This is a SAFE test file for RedSand Sandbox testing.
NOT A REAL ROOTKIT!
"""
    with open(filename, 'w') as f:
        f.write(content)
    print(f"✓ Создан: {filename}")

def create_clean_file(filename: str):
    """Создает чистый файл без угроз."""
    content = f"""CLEAN_FILE_MARKER
GENERATED: {datetime.now().isoformat()}
RANDOM_ID: {random_string(12)}

This is a completely safe file with no malicious content.
Used for testing false positive detection in RedSand Sandbox.
"""
    with open(filename, 'w') as f:
        f.write(content)
    print(f"✓ Создан: {filename}")

def create_poly_variant(filename: str, variant_id: int):
    """Создает полиморфный вариант для теста."""
    noise = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(50, 200)))
    content = f"""POLYMORPHIC_SAMPLE_V{variant_id}
GENERATED: {datetime.now().isoformat()}
RANDOM_ID: {random_string(12)}
NOISE_BLOCK: {noise}

[METAMORPHIC_CODE]
Variant: {variant_id}
Encryption: XOR_MOCK
Decryption_Routine: SIMULATED

[NOTE]
This is a SAFE polymorphic test file.
NOT REAL MALWARE!
"""
    with open(filename, 'w') as f:
        f.write(content)
    print(f"✓ Создан: {filename}")

def generate_all_samples():
    """Генерирует полный набор тестовых образцов."""
    print("=" * 60)
    print("Генерация тестовых образцов для RedSand Sandbox")
    print("=" * 60)
    
    # Создаем чистые файлы
    for i in range(2):
        create_clean_file(SAMPLES_DIR / f"clean_file_{random_string(6)}.txt")
    
    # Создаем фейковые угрозы каждого типа
    for threat_type in THREAT_TYPES:
        for i in range(2):
            ext = ".sys" if threat_type == "rootkit" else ".exe"
            filename = SAMPLES_DIR / f"fake_{threat_type}_{random_string(6)}{ext}"
            if ext == ".sys":
                create_fake_sys(filename)
            else:
                create_fake_exe(filename, threat_type)
    
    # Создаем полиморфные варианты
    for variant_id in range(5):
        for i in range(2):
            create_poly_variant(
                SAMPLES_DIR / f"poly_variant_{variant_id}_{random_string(6)}.exe",
                variant_id
            )
    
    # Создаем информацию об образцах
    samples_info = {
        "generated_at": datetime.now().isoformat(),
        "total_samples": len(list(SAMPLES_DIR.glob("*"))),
        "types": {
            "clean": 2,
            "trojan": 2,
            "ransomware": 2,
            "spyware": 2,
            "adware": 2,
            "worm": 2,
            "rootkit": 2,
            "miner": 2,
            "polymorphic": 10
        },
        "warning": "ВСЕ ФАЙЛЫ БЕЗОПАСНЫ И ПРЕДНАЗНАЧЕНЫ ТОЛЬКО ДЛЯ ТЕСТИРОВАНИЯ!"
    }
    
    with open(SAMPLES_DIR / "samples_info.json", 'w') as f:
        json.dump(samples_info, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✓ Готово! Создано {samples_info['total_samples']} тестовых образцов")
    print("=" * 60)
    print("\n⚠️  ВНИМАНИЕ: Все файлы безопасны и не содержат реального вредоносного кода!")

if __name__ == '__main__':
    generate_all_samples()
