"""
RedSand Secure - Многопоточный сканер с кэшированием результатов
Поддерживает параллельное сканирование, прогресс-бары и экспорт результатов
"""

import os
import re
import json
import hashlib
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import OrderedDict
from datetime import datetime
import threading

from .extended_scanner import ExtendedVirusScanner, ScanResult, ThreatLevel


@dataclass
class CacheEntry:
    result: ScanResult
    timestamp: float
    access_count: int


class LRUCache:
    """LRU кэш для результатов сканирования"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[ScanResult]:
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                # Перемещаем в конец (recently used)
                self.cache.move_to_end(key)
                entry.access_count += 1
                self.hits += 1
                return entry.result
            self.misses += 1
            return None
    
    def put(self, key: str, result: ScanResult):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                self.cache[key] = CacheEntry(result, time.time(), 1)
            else:
                if len(self.cache) >= self.max_size:
                    # Удаляем oldest entry
                    self.cache.popitem(last=False)
                self.cache[key] = CacheEntry(result, time.time(), 1)
    
    def clear(self):
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    def get_stats(self) -> Dict:
        total = self.hits + self.misses
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / total if total > 0 else 0
        }


@dataclass
class ScanProgress:
    current_file: str
    completed: int
    total: int
    progress_percent: float
    elapsed_time: float
    estimated_remaining: float
    results_summary: Dict


class ThreadSafeVirusScanner:
    """
    Многопоточный сканер вирусов с кэшированием
    """
    
    def __init__(self, max_workers: Optional[int] = None, cache_size: int = 10000):
        self.scanner = ExtendedVirusScanner()
        self.max_workers = max_workers or os.cpu_count() or 4
        self.cache = LRUCache(cache_size)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.lock = threading.Lock()
        self.scan_history: List[Dict] = []
        
        # Статистика
        self.total_files_scanned = 0
        self.threats_detected = 0
        self.clean_files = 0
    
    def _get_file_hash(self, file_path: str) -> str:
        """Быстрый хеш для кэширования"""
        try:
            stat = os.stat(file_path)
            content_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                # Хэшируем только первые и последние 8KB для скорости
                content_hash.update(f.read(8192))
                f.seek(-min(8192, stat.st_size), 2)
                content_hash.update(f.read())
            return f"{stat.st_mtime}_{stat.st_size}_{content_hash.hexdigest()}"
        except Exception:
            return "unknown"
    
    def scan_file(self, file_path: str, use_cache: bool = True) -> ScanResult:
        """Сканирование одного файла с кэшированием"""
        if use_cache:
            cache_key = self._get_file_hash(file_path)
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
        
        # Полное сканирование
        result = self.scanner.scan_file(file_path)
        
        # Сохраняем в кэш
        if use_cache:
            self.cache.put(cache_key, result)
        
        # Обновляем статистику
        with self.lock:
            self.total_files_scanned += 1
            if result.threat_level == ThreatLevel.CLEAN:
                self.clean_files += 1
            else:
                self.threats_detected += 1
        
        return result
    
    def scan_files_parallel(self, file_paths: List[str], 
                           progress_callback: Optional[callable] = None) -> List[ScanResult]:
        """Параллельное сканирование множества файлов"""
        if not file_paths:
            return []
        
        results = []
        start_time = time.time()
        completed = 0
        total = len(file_paths)
        
        def scan_with_progress(file_path):
            nonlocal completed
            result = self.scan_file(file_path)
            with self.lock:
                completed += 1
                current_time = time.time()
                elapsed = current_time - start_time
                avg_time = elapsed / completed if completed > 0 else 0
                remaining = (total - completed) * avg_time
                
                progress = ScanProgress(
                    current_file=file_path,
                    completed=completed,
                    total=total,
                    progress_percent=(completed / total) * 100,
                    elapsed_time=elapsed,
                    estimated_remaining=remaining,
                    results_summary={
                        'clean': sum(1 for r in results if r.threat_level == ThreatLevel.CLEAN),
                        'suspicious': sum(1 for r in results if r.threat_level == ThreatLevel.SUSPICIOUS),
                        'malicious': sum(1 for r in results if r.threat_level == ThreatLevel.MALICIOUS)
                    }
                )
                
                if progress_callback:
                    progress_callback(progress)
            
            return result
        
        # Запуск в пуле потоков
        futures = {self.executor.submit(scan_with_progress, fp): fp for fp in file_paths}
        
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                file_path = futures[future]
                results.append(ScanResult(
                    file_path=file_path,
                    threat_level=ThreatLevel.SUSPICIOUS,
                    score=50,
                    threats_found=[f"ERROR: {str(e)}"],
                    threat_types=['ERROR'],
                    sha256="error",
                    details={'error': str(e)}
                ))
        
        return results
    
    def scan_directory(self, directory: str, 
                      recursive: bool = True,
                      extensions: Optional[List[str]] = None,
                      progress_callback: Optional[callable] = None) -> List[ScanResult]:
        """Сканирование директории"""
        file_paths = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                # Пропускаем системные директории
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
                for file in files:
                    file_path = os.path.join(root, file)
                    if extensions is None or any(file.endswith(ext) for ext in extensions):
                        file_paths.append(file_path)
        else:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    if extensions is None or any(file.endswith(ext) for ext in extensions):
                        file_paths.append(file_path)
        
        return self.scan_files_parallel(file_paths, progress_callback)
    
    def quick_scan(self, critical_paths: Optional[List[str]] = None) -> Dict:
        """Быстрое сканирование критических мест системы"""
        if critical_paths is None:
            critical_paths = [
                os.path.expanduser("~/Downloads"),
                os.path.expanduser("~/Desktop"),
                "/tmp",
                "/var/tmp"
            ]
        
        start_time = time.time()
        all_results = []
        
        for path in critical_paths:
            if os.path.exists(path):
                results = self.scan_directory(path, recursive=False, progress_callback=None)
                all_results.extend(results)
        
        elapsed = time.time() - start_time
        
        return {
            'scan_type': 'quick_scan',
            'timestamp': datetime.now().isoformat(),
            'elapsed_seconds': elapsed,
            'files_scanned': len(all_results),
            'threats_found': sum(1 for r in all_results if r.threat_level != ThreatLevel.CLEAN),
            'clean_files': sum(1 for r in all_results if r.threat_level == ThreatLevel.CLEAN),
            'suspicious_files': sum(1 for r in all_results if r.threat_level == ThreatLevel.SUSPICIOUS),
            'malicious_files': sum(1 for r in all_results if r.threat_level == ThreatLevel.MALICIOUS),
            'cache_stats': self.cache.get_stats(),
            'results': [
                {
                    'file': r.file_path,
                    'level': r.threat_level.value,
                    'score': r.score,
                    'threats': r.threat_types
                }
                for r in all_results[:100]  # Ограничиваем вывод
            ]
        }
    
    def export_results(self, results: List[ScanResult], output_path: str, format: str = 'json'):
        """Экспорт результатов сканирования"""
        if format == 'json':
            data = {
                'scan_timestamp': datetime.now().isoformat(),
                'total_files': len(results),
                'summary': {
                    'clean': sum(1 for r in results if r.threat_level == ThreatLevel.CLEAN),
                    'suspicious': sum(1 for r in results if r.threat_level == ThreatLevel.SUSPICIOUS),
                    'malicious': sum(1 for r in results if r.threat_level == ThreatLevel.MALICIOUS)
                },
                'results': [
                    {
                        'file_path': r.file_path,
                        'threat_level': r.threat_level.value,
                        'score': r.score,
                        'sha256': r.sha256,
                        'threats_found': r.threats_found,
                        'threat_types': r.threat_types,
                        'details': r.details
                    }
                    for r in results
                ]
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format == 'csv':
            import csv
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['File Path', 'Threat Level', 'Score', 'SHA256', 'Threat Types', 'Details'])
                for r in results:
                    writer.writerow([
                        r.file_path,
                        r.threat_level.value,
                        r.score,
                        r.sha256,
                        '|'.join(r.threat_types),
                        json.dumps(r.details)
                    ])
    
    def get_statistics(self) -> Dict:
        """Получение статистики сканера"""
        return {
            'total_files_scanned': self.total_files_scanned,
            'threats_detected': self.threats_detected,
            'clean_files': self.clean_files,
            'cache_stats': self.cache.get_stats(),
            'scanner_stats': self.scanner.get_statistics(),
            'max_workers': self.max_workers,
            'scan_history_count': len(self.scan_history)
        }
    
    def clear_cache(self):
        """Очистка кэша"""
        self.cache.clear()
    
    def shutdown(self):
        """Корректное завершение работы"""
        self.executor.shutdown(wait=True)
