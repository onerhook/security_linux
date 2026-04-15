#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор безопасных тестовых образцов для RedSand Sandbox
Создает БЕЗОПАСНЫЕ файлы, имитирующие поведение вредоносного ПО
Использовать ТОЛЬКО для тестирования в изолированной среде!
"""

import os
import sys
import hashlib
import json
import random
import string
from pathlib import Path
from datetime import datetime


def generate_random_string(length=10):
    """Генерация случайной строки."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def create_fake_ransomware(output_dir='test_samples'):
    """
    Создает БЕЗОПАСНЫЙ файл, имитирующий признаки ransomware.
    Не шифрует файлы, не наносит вреда.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    filename = f"fake_ransom_{generate_random_string(6)}.exe"
    filepath = output_path / filename
    
    # Создаем файл с "подозрительными" строками
    content = b"MZ" + b"\x00" * 58  # Фейковый PE заголовок
    content += b"FAKE_RANSOMWARE_SIGNATURE_" + generate_random_string(20).encode()
    content += b"\x00" * 100
    content += b"C:\\Users\\victim\\documents"
    content += b"encrypt_files()"
    content += b"bitcoin_wallet_address_1A2B3C4D5E6F"
    content += b"YOUR_FILES_ARE_ENCRYPTED.txt"
    content += b"ransom_note.html"
    content += b"shadow_copy_delete_cmd.exe"
    content += b"\x00" * 200
    
    with open(filepath, 'wb') as f:
        f.write(content)
    
    print(f"[+] Создан фейковый ransomware: {filepath}")
    return str(filepath)


def create_fake_trojan(output_dir='test_samples'):
    """
    Создает БЕЗОПАСНЫЙ файл, имитирующий троян.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    filename = f"fake_trojan_{generate_random_string(6)}.exe"
    filepath = output_path / filename
    
    content = b"MZ" + b"\x00" * 58
    content += b"FAKE_TROJAN_SIGNATURE_" + generate_random_string(20).encode()
    content += b"\x00" * 100
    content += b"CreateRemoteThread"
    content += b"VirtualAllocEx"
    content += b"WriteProcessMemory"
    content += b"NtUnmapViewOfSection"
    content += b"process_hollowing_detected"
    content += b"suspicious_registry_key"
    content += b"HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    content += b"cmd.exe /c start malware.exe"
    content += b"\x00" * 200
    
    with open(filepath, 'wb') as f:
        f.write(content)
    
    print(f"[+] Создан фейковый троян: {filepath}")
    return str(filepath)


def create_fake_spyware(output_dir='test_samples'):
    """
    Создает БЕЗОПАСНЫЙ файл, имитирующий spyware.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    filename = f"fake_spyware_{generate_random_string(6)}.exe"
    filepath = output_path / filename
    
    content = b"MZ" + b"\x00" * 58
    content += b"FAKE_SPYWARE_SIGNATURE_" + generate_random_string(20).encode()
    content += b"\x00" * 100
    content += b"SetWindowsHookEx"
    content += b"GetAsyncKeyState"
    content += b"keylogger_active"
    content += b"screenshot_capture"
    content += b"clipboard_monitor"
    content += b"send_data_to_c2_server"
    content += b"192.168.1.100:4444"
    content += b"exfiltrate_credentials"
    content += b"\x00" * 200
    
    with open(filepath, 'wb') as f:
        f.write(content)
    
    print(f"[+] Создан фейковый spyware: {filepath}")
    return str(filepath)


def create_fake_miner(output_dir='test_samples'):
    """
    Создает БЕЗОПАСНЫЙ файл, имитирующий криптомайнер.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    filename = f"fake_miner_{generate_random_string(6)}.exe"
    filepath = output_path / filename
    
    content = b"MZ" + b"\x00" * 58
    content += b"FAKE_MINER_SIGNATURE_" + generate_random_string(20).encode()
    content += b"\x00" * 100
    content += b"stratum+tcp://pool.mining.com:3333"
    content += b"wallet_address_crypto_currency"
    content += b"cryptonight_algorithm"
    content += b"high_cpu_usage_detected"
    content += b"disable_windows_defender"
    content += b"XMRig_miner_clone"
    content += b"monero_mining_pool"
    content += b"\x00" * 200
    
    with open(filepath, 'wb') as f:
        f.write(content)
    
    print(f"[+] Создан фейковый майнер: {filepath}")
    return str(filepath)


def create_fake_adware(output_dir='test_samples'):
    """
    Создает БЕЗОПАСНЫЙ файл, имитирующий adware.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    filename = f"fake_adware_{generate_random_string(6)}.exe"
    filepath = output_path / filename
    
    content = b"MZ" + b"\x00" * 58
    content += b"FAKE_ADWARE_SIGNATURE_" + generate_random_string(20).encode()
    content += b"\x00" * 100
    content += b"popup_ads_injector"
    content += b"browser_extension_install"
    content += b"homepage_hijack"
    content += b"search_redirect"
    content += b"display_unwanted_ads"
    content += b"track_user_behavior"
    content += b"Chrome/Firefox/Edge"
    content += b"\x00" * 200
    
    with open(filepath, 'wb') as f:
        f.write(content)
    
    print(f"[+] Создан фейковый adware: {filepath}")
    return str(filepath)


def create_fake_rootkit(output_dir='test_samples'):
    """
    Создает БЕЗОПАСНЫЙ файл, имитирующий руткит.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    filename = f"fake_rootkit_{generate_random_string(6)}.sys"
    filepath = output_path / filename
    
    content = b"MZ" + b"\x00" * 58
    content += b"FAKE_ROOTKIT_SIGNATURE_" + generate_random_string(20).encode()
    content += b"\x00" * 100
    content += b"kernel_driver_load"
    content += b"SSDT_hooking"
    content += b"IDT_modification"
    content += b"hide_processes"
    content += b"hide_files"
    content += b"hide_registry_keys"
    content += b"disable_antivirus"
    content += b"bootkit_installed"
    content += b"\x00" * 200
    
    with open(filepath, 'wb') as f:
        f.write(content)
    
    print(f"[+] Создан фейковый rootkit: {filepath}")
    return str(filepath)


def create_fake_worm(output_dir='test_samples'):
    """
    Создает БЕЗОПАСНЫЙ файл, имитирующий червь.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    filename = f"fake_worm_{generate_random_string(6)}.exe"
    filepath = output_path / filename
    
    content = b"MZ" + b"\x00" * 58
    content += b"FAKE_WORM_SIGNATURE_" + generate_random_string(20).encode()
    content += b"\x00" * 100
    content += b"spread_via_network"
    content += b"spread_via_usb"
    content += b"copy_to_removable_drives"
    content += b"autorun_inf_creator"
    content += b"network_share_scanner"
    content += b"SMB_exploit_attempt"
    content += b"email_spreader"
    content += b"\x00" * 200
    
    with open(filepath, 'wb') as f:
        f.write(content)
    
    print(f"[+] Создан фейковый червь: {filepath}")
    return str(filepath)


def create_clean_file(output_dir='test_samples'):
    """
    Создает чистый файл для проверки на ложные срабатывания.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    filename = f"clean_file_{generate_random_string(6)}.txt"
    filepath = output_path / filename
    
    content = f"""This is a clean test file.
Created at: {datetime.now().isoformat()}
Random ID: {generate_random_string(32)}

This file should NOT be detected as malicious.
It contains no suspicious patterns or behaviors.
Used for testing false positive rate of the sandbox.
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[+] Создан чистый файл: {filepath}")
    return str(filepath)


def create_polyphic_test_file(output_dir='test_samples'):
    """
    Создает файл для тестирования полиморфного анализа.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    samples = []
    for i in range(5):
        filename = f"poly_variant_{i}_{generate_random_string(6)}.exe"
        filepath = output_path / filename
        
        # Каждый вариант имеет уникальное "тело", но одинаковую сигнатуру
        content = b"MZ" + b"\x00" * 58
        content += f"VARIANT_{i}_".encode() + generate_random_string(50).encode()
        content += b"\x00" * (100 + i * 20)
        content += b"POLYMORPHIC_ENGINE_TEST"
        content += b"same_malicious_payload_different_wrappers"
        content += b"evasion_technique_test"
        content += b"\x00" * 200
        
        with open(filepath, 'wb') as f:
            f.write(content)
        
        samples.append(str(filepath))
        print(f"[+] Создан полиморфный вариант {i}: {filepath}")
    
    return samples


def generate_sample_info(samples):
    """Генерирует JSON с информацией о созданных образцах."""
    info = {
        "created_at": datetime.now().isoformat(),
        "total_samples": len(samples),
        "samples": []
    }
    
    for sample_path in samples:
        path = Path(sample_path)
        if path.exists():
            with open(path, 'rb') as f:
                content = f.read()
            
            info["samples"].append({
                "filename": path.name,
                "path": str(path),
                "size": len(content),
                "md5": hashlib.md5(content).hexdigest(),
                "sha256": hashlib.sha256(content).hexdigest()
            })
    
    info_path = Path("test_samples/samples_info.json")
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    
    print(f"\n[+] Информация о образцах сохранена в: {info_path}")
    return info


def main():
    """Создает все тестовые образцы."""
    print("=" * 60)
    print("RedSand Sandbox - Генератор тестовых образцов")
    print("=" * 60)
    print("\n⚠️  Все создаваемые файлы БЕЗОПАСНЫ и используются только для тестирования!")
    print("=" * 60 + "\n")
    
    samples = []
    
    # Создаем разные типы угроз
    print("[*] Создание тестовых образцов...\n")
    
    samples.append(create_fake_ransomware())
    samples.append(create_fake_trojan())
    samples.append(create_fake_spyware())
    samples.append(create_fake_miner())
    samples.append(create_fake_adware())
    samples.append(create_fake_rootkit())
    samples.append(create_fake_worm())
    samples.append(create_clean_file())
    
    # Полиморфные варианты
    print("\n[*] Создание полиморфных вариантов...")
    poly_samples = create_polyphic_test_file()
    samples.extend(poly_samples)
    
    # Генерируем информацию
    print("\n[*] Генерация информации об образцах...")
    info = generate_sample_info(samples)
    
    print("\n" + "=" * 60)
    print(f"✅ Создано {len(samples)} тестовых образцов")
    print("=" * 60)
    print(f"\nДиректория: test_samples/")
    print(f"Всего файлов: {info['total_samples']}")
    print(f"Информация: test_samples/samples_info.json")
    print("\nТеперь можно запустить анализ:")
    print("  python redsand_secure.py test_samples/fake_ransom_*.exe")
    print("  или через GUI: python redsand_gui.py\n")


if __name__ == "__main__":
    main()
