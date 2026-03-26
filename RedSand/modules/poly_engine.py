#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Poly Engine - Полиморфный движок
Генерация уникальных вариантов тестовых образцов
"""

import os
import random
import string
import hashlib
import shutil
from pathlib import Path

class PolyEngine:
    def __init__(self):
        self.garbage_templates = [
            b'\x90' * 10,  # NOP sled
            b'\xCC' * 5,   # INT3
            bytes(random.randint(0, 255) for _ in range(20)),
            b'\xEB\xFE',   # JMP short
        ]
        
    def generate_variants(self, file_path, count=3):
        """Генерация полиморфных вариантов файла"""
        variants = []
        original_size = os.path.getsize(file_path)
        
        with open(file_path, 'rb') as f:
            original_data = f.read()
        
        base_name = Path(file_path).stem
        base_dir = Path(file_path).parent
        
        for i in range(count):
            variant_name = f"{base_name}_poly_{i}.bin"
            variant_path = base_dir / variant_name
            
            # Создаем вариант с добавлением мусора
            variant_data = self._morph(original_data, i)
            
            with open(variant_path, 'wb') as f:
                f.write(variant_data)
            
            variant_hash = hashlib.sha256(variant_data).hexdigest()[:16]
            variants.append({
                'path': str(variant_path),
                'hash': variant_hash,
                'size': len(variant_data),
                'original_size': original_size,
                'morph_type': self._get_morph_type(i)
            })
            
        return variants
    
    def _morph(self, data, variant_id):
        """Применение полиморфных трансформаций"""
        result = bytearray(data)
        
        # Добавляем случайный префикс
        prefix_len = random.randint(10, 50)
        prefix = bytes(random.randint(0, 255) for _ in range(prefix_len))
        
        # Добавляем случайный суффикс
        suffix_len = random.randint(10, 50)
        suffix = bytes(random.randint(0, 255) for _ in range(suffix_len))
        
        # Вставляем мусор в случайные позиции
        insert_positions = sorted(random.sample(range(len(result)), min(3, len(result))))
        offset = 0
        for pos in insert_positions:
            garbage = random.choice(self.garbage_templates)
            result[pos+offset:pos+offset] = garbage
            offset += len(garbage)
        
        return prefix + bytes(result) + suffix
    
    def _get_morph_type(self, variant_id):
        """Описание типа трансформации"""
        types = [
            'NOP insertion + random padding',
            'INT3 breakpoints + garbage bytes',
            'Random byte injection + junk code'
        ]
        return types[variant_id % len(types)]
    
    def calculate_similarity(self, file1, file2):
        """Вычисление схожести двух файлов"""
        with open(file1, 'rb') as f:
            data1 = f.read()
        with open(file2, 'rb') as f:
            data2 = f.read()
        
        # Простая метрика схожести по хешу
        hash1 = hashlib.md5(data1).hexdigest()
        hash2 = hashlib.md5(data2).hexdigest()
        
        matching_chars = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
        similarity = (matching_chars / len(hash1)) * 100
        
        return {
            'similarity_percent': similarity,
            'hash1': hash1,
            'hash2': hash2,
            'size1': len(data1),
            'size2': len(data2)
        }
