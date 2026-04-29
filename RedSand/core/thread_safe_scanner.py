#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thread-Safe Virus Scanner - Многопоточный сканер вирусов с кэшированием
Оптимизирован для высокой производительности при сканировании больших объёмов файлов
Поддержка многопоточности, кэширования результатов и прогресс-баров
"""

import os
import hashlib
import re
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import OrderedDict
from dataclasses import dataclass
import json

from core.virus_scanner import VirusScanner


@dataclass
class ScanProgress:
    """Прогресс сканирования."""
    total_files: int
    scanned_files: int
    malicious_found: int
    suspicious_found: int
    clean_files: int
    current_file: str
    elapsed_time: float
    files_per_second: float


class LRUCache:
    """LRU кэш для хранения результатов сканирования."""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.cache: OrderedDict[str, Dict] = OrderedDict()
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Dict]:
        with self.lock:
            if key in self.cache:
                # Перемещаем в конец (recently used)
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key]
            self.misses += 1
            return None
    
    def put(self, key: str, value: Dict):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.max_size:
                    # Удаляем oldest entry
                    self.cache.popitem(last=False)
            self.cache[key] = value
    
    def clear(self):
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': f"{hit_rate:.2f}%"
            }


class ThreadSafeVirusScanner(VirusScanner):
    """
    Многопоточный сканер вирусов с кэшированием.
    Наследуется от базового VirusScanner, добавляя многопоточность и кэш.
    """
    
    def __init__(self, max_workers: int = 4, cache_size: int = 10000):
        super().__init__()
        self.max_workers = max_workers or os.cpu_count() or 4
        self.cache = LRUCache(cache_size)
        self.scan_lock = threading.Lock()
        self.progress_callback = None
        self.stop_flag = False
    
    def set_progress_callback(self, callback):
        """Установка callback функции для обновления прогресса."""
        self.progress_callback = callback
    
    def stop_scan(self):
        """Остановка текущего сканирования."""
        self.stop_flag = True
    
    def reset_stop_flag(self):
        """Сброс флага остановки."""
        self.stop_flag = False
    
    def _calculate_hash_fast(self, file_path: str) -> str:
        """Быстрое вычисление хеша с использованием буфера большего размера."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Читаем большими блоками для скорости
                for byte_block in iter(lambda: f.read(65536), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return 'N/A'
    
    def scan_file_cached(self, file_path: str) -> Dict:
        """
        Сканирование файла с использованием кэша.
        Если файл уже сканировался, возвращает кэшированный результат.
        """
        # Вычисляем хеш для ключа кэша
        file_hash = self._calculate_hash_fast(file_path)
        cache_key = f"{file_path}:{file_hash}"
        
        # Проверяем кэш
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Сканируем файл
        result = self.scan_file(file_path)
        
        # Сохраняем в кэш
        self.cache.put(cache_key, result)
        
        return result
    
    def scan_directory(self, directory: str, recursive: bool = True,
                      extensions: Optional[List[str]] = None,
                      exclude_dirs: Optional[List[str]] = None) -> List[Dict]:
        """
        Сканирование директории с использованием многопоточности.
        
        Args:
            directory: Путь к директории
            recursive: Рекурсивное сканирование
            extensions: Список расширений для сканирования (None = все)
            exclude_dirs: Список директорий для исключения
        
        Returns:
            Список результатов сканирования
        """
        self.reset_stop_flag()
        
        # Сбор списка файлов
        files_to_scan = self._collect_files(
            directory, recursive, extensions, exclude_dirs
        )
        
        if not files_to_scan:
            return []
        
        results = []
        start_time = time.time()
        malicious_count = 0
        suspicious_count = 0
        clean_count = 0
        
        # Многопоточное сканирование
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self.scan_file_cached, f): f
                for f in files_to_scan
            }
            
            completed = 0
            total = len(future_to_file)
            
            for future in as_completed(future_to_file):
                if self.stop_flag:
                    # Отменяем оставшиеся задачи
                    for f in future_to_file:
                        f.cancel()
                    break
                
                file_path = future_to_file[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Статистика
                    if result.get('threat_level') == 'MALICIOUS':
                        malicious_count += 1
                    elif result.get('threat_level') == 'SUSPICIOUS':
                        suspicious_count += 1
                    else:
                        clean_count += 1
                    
                    completed += 1
                    elapsed = time.time() - start_time
                    
                    # Callback прогресса
                    if self.progress_callback:
                        progress = ScanProgress(
                            total_files=total,
                            scanned_files=completed,
                            malicious_found=malicious_count,
                            suspicious_found=suspicious_count,
                            clean_files=clean_count,
                            current_file=os.path.basename(file_path),
                            elapsed_time=elapsed,
                            files_per_second=completed / elapsed if elapsed > 0 else 0
                        )
                        self.progress_callback(progress)
                
                except Exception as e:
                    results.append({
                        'file_path': file_path,
                        'error': str(e),
                        'threat_level': 'ERROR'
                    })
        
        return results
    
    def _collect_files(self, directory: str, recursive: bool,
                      extensions: Optional[List[str]],
                      exclude_dirs: Optional[List[str]]) -> List[str]:
        """Сбор списка файлов для сканирования."""
        files = []
        exclude_dirs = exclude_dirs or [
            '__pycache__', '.git', 'node_modules', 
            'venv', '.venv', 'env', '.env'
        ]
        
        directory = Path(directory)
        
        if not directory.exists():
            return files
        
        if recursive:
            iterator = directory.rglob('*')
        else:
            iterator = directory.glob('*')
        
        for path in iterator:
            if path.is_file():
                # Проверка расширений
                if extensions:
                    ext = path.suffix.lower()
                    if ext not in [e.lower() if e.startswith('.') else f'.{e.lower()}' 
                                   for e in extensions]:
                        continue
                
                # Проверка исключённых директорий
                path_parts = path.parts
                if any(excl in path_parts for excl in exclude_dirs):
                    continue
                
                files.append(str(path))
        
        return files
    
    def scan_files_batch(self, file_list: List[str]) -> List[Dict]:
        """
        Пакетное сканирование списка файлов.
        Оптимизировано для обработки большого количества файлов.
        """
        self.reset_stop_flag()
        
        if not file_list:
            return []
        
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self.scan_file_cached, f): f
                for f in file_list
            }
            
            for future in as_completed(future_to_file):
                if self.stop_flag:
                    for f in future_to_file:
                        f.cancel()
                    break
                
                file_path = future_to_file[future]
                
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'file_path': file_path,
                        'error': str(e),
                        'threat_level': 'ERROR'
                    })
        
        return results
    
    def quick_scan(self, paths: List[str]) -> Dict[str, Any]:
        """
        Быстрое сканирование критических мест системы.
        Возвращает сводную статистику.
        """
        self.reset_stop_flag()
        
        critical_paths = paths or [
            os.path.expanduser('~\\Downloads'),
            os.path.expanduser('~\\Desktop'),
            os.path.expanduser('~\\Documents'),
        ]
        
        all_files = []
        for path in critical_paths:
            if os.path.exists(path):
                all_files.extend(self._collect_files(path, recursive=True))
        
        start_time = time.time()
        results = self.scan_files_batch(all_files[:1000])  # Ограничение на 1000 файлов
        
        elapsed = time.time() - start_time
        
        # Статистика
        stats = {
            'total_scanned': len(results),
            'malicious': sum(1 for r in results if r.get('threat_level') == 'MALICIOUS'),
            'suspicious': sum(1 for r in results if r.get('threat_level') == 'SUSPICIOUS'),
            'clean': sum(1 for r in results if r.get('threat_level') == 'CLEAN'),
            'errors': sum(1 for r in results if r.get('threat_level') == 'ERROR'),
            'elapsed_time': elapsed,
            'files_per_second': len(results) / elapsed if elapsed > 0 else 0,
            'cache_stats': self.cache.get_stats()
        }
        
        return stats
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша."""
        return self.cache.get_stats()
    
    def clear_cache(self):
        """Очистка кэша."""
        self.cache.clear()
    
    def export_results(self, results: List[Dict], output_file: str, 
                      format: str = 'json'):
        """Экспорт результатов сканирования в файл."""
        if format == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        elif format == 'csv':
            import csv
            if results:
                keys = results[0].keys()
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    dict_writer = csv.DictWriter(f, fieldnames=keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(results)
        
        print(f"[+] Результаты экспортированы в {output_file}")


# Для совместимости
if __name__ == "__main__":
    # Пример использования
    scanner = ThreadSafeVirusScanner(max_workers=4)
    
    # Быстрое сканирование
    stats = scanner.quick_scan([])
    print(f"Отсканировано: {stats['total_scanned']}")
    print(f"Найдено угроз: {stats['malicious']}")
    print(f"Статистика кэша: {stats['cache_stats']}")
