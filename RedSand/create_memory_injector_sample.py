#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEMORY_INJECTOR Test Sample Generator
Создает фейковый файл, имитирующий поведение вируса типа MEMORY_INJECTOR
для тестирования системы RedSand Secure.

Этот файл НЕ является вирусом и не содержит вредоносного кода.
Он только эмулирует сигнатуры и паттерны для тестирования детектора.
"""

import os
import sys

def create_memory_injector_sample():
    """Создает тестовый файл с сигнатурами MEMORY_INJECTOR"""
    
    # Директория для тестовых образцов
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_samples")
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.join(output_dir, "memory_injector_test.exe")
    
    # Фейковые сигнатуры и паттерны, характерные для MEMORY_INJECTOR
    # Эти паттерны имитируют вызовы API для инъекции в память
    
    malicious_patterns = [
        # Заголовки PE файла (фейковые)
        b"MZ" + b"\x90" * 60,  # DOS заголовок
        
        # Строки, имитирующие импорт опасных API функций
        b"VirtualAllocEx\x00",
        b"WriteProcessMemory\x00",
        b"CreateRemoteThread\x00",
        b"NtUnmapViewOfSection\x00",
        b"OpenProcess\x00",
        b"ReadProcessMemory\x00",
        
        # Сигнатуры Process Hollowing
        b"PROCESS_ALL_ACCESS\x00",
        b"MEM_COMMIT\x00",
        b"PAGE_EXECUTE_READWRITE\x00",
        
        # Имитация шеллкода в памяти (NOP sled + фейковый payload)
        b"\x90" * 100,  # NOP sled
        
        # Строки, характерные для инъекторов
        b"cmd.exe /c whoami\x00",
        b"powershell -enc\x00",
        b"inject.dll\x00",
        b"payload.bin\x00",
        
        # Методы обхода защиты
        b"DisableAntiSpyware\x00",
        b"BypassUAC\x00",
        b"EtwPatch\x00",
        
        # Дополнительный мусор для увеличения размера
        b"\x00" * 500,
        
        # Фейковая секция кода с подозрительными байтами
        b"\x55\x48\x89\xe5\x48\x83\xec\x20" * 50,
        
        # Маркер для идентификации нашего тестового образца
        b"REDSAND_TEST_SAMPLE_MEMORY_INJECTOR_V1\x00",
    ]
    
    # Собираем файл
    file_content = b"".join(malicious_patterns)
    
    # Добавляем случайный мусор для реалистичности
    import random
    random.seed(42)  # Для воспроизводимости
    junk_data = bytes([random.randint(0, 255) for _ in range(2048)])
    file_content += junk_data
    
    # Записываем файл
    with open(filename, "wb") as f:
        f.write(file_content)
    
    file_size = os.path.getsize(filename)
    
    print(f"✅ Тестовый образец MEMORY_INJECTOR создан!")
    print(f"📁 Путь: {filename}")
    print(f"📏 Размер: {file_size} байт")
    print(f"\n⚠️  ВНИМАНИЕ: Это тестовый файл, имитирующий вирус.")
    print(f"   Он безопасен, но может быть определен антивирусом как угроза.")
    print(f"   Используйте только для тестирования RedSand Secure!")
    
    return filename

if __name__ == "__main__":
    try:
        sample_path = create_memory_injector_sample()
        print(f"\n🎯 Готов к тестированию: {os.path.basename(sample_path)}")
    except Exception as e:
        print(f"❌ Ошибка при создании образца: {e}")
        sys.exit(1)
