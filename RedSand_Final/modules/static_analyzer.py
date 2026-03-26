#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Static Analyzer - Статический анализ файлов
Анализ PE-заголовков, строк, хешей, YARA правил
"""

import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class StaticAnalyzer:
    def __init__(self):
        self.yara_rules = []
    
    def analyze(self, file_path: str) -> Dict:
        """Полный статический анализ файла"""
        results = {}
        
        path = Path(file_path)
        if not path.exists():
            return {"error": "File not found"}
        
        # Базовая информация
        results["file_info"] = self._get_file_info(path)
        
        # Хэши
        results["hashes"] = self._calculate_hashes(path)
        
        # PE анализ (для Windows executables)
        if path.suffix.lower() in ['.exe', '.dll', '.sys', '.ocx']:
            results["pe_info"] = self._analyze_pe(path)
        
        # Строки
        results["strings"] = self._extract_strings(path)
        
        # YARA анализ
        results["yara_matches"] = self._run_yara_scan(path)
        
        return results
    
    def _get_file_info(self, path: Path) -> Dict:
        """Получение базовой информации о файле"""
        return {
            "name": path.name,
            "size": path.stat().st_size,
            "extension": path.suffix,
            "path": str(path.absolute())
        }
    
    def _calculate_hashes(self, path: Path) -> Dict[str, str]:
        """Вычисление хешей файла"""
        hashes = {}
        
        with open(path, 'rb') as f:
            content = f.read()
        
        hashes['md5'] = hashlib.md5(content).hexdigest()
        hashes['sha1'] = hashlib.sha1(content).hexdigest()
        hashes['sha256'] = hashlib.sha256(content).hexdigest()
        
        return hashes
    
    def _analyze_pe(self, path: Path) -> Dict:
        """Анализ PE-файла"""
        pe_info = {}
        
        try:
            import pefile
            
            pe = pefile.PE(str(path))
            
            pe_info["valid"] = True
            pe_info["machine_type"] = hex(pe.FILE_HEADER.Machine)
            pe_info["timestamp"] = pe.FILE_HEADER.TimeDateStamp
            pe_info["sections"] = []
            
            for section in pe.sections:
                section_info = {
                    "name": section.Name.decode('utf-8', errors='ignore').strip('\x00'),
                    "virtual_size": section.Misc_VirtualSize,
                    "raw_size": section.SizeOfRawData,
                    "characteristics": section.Characteristics
                }
                pe_info["sections"].append(section_info)
            
            # Импорты
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                pe_info["imports"] = []
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    dll_name = entry.dll.decode('utf-8', errors='ignore')
                    pe_info["imports"].append(dll_name)
            
            # Экспорты
            if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
                pe_info["exports_count"] = len(pe.DIRECTORY_ENTRY_EXPORT.symbols)
            
        except Exception as e:
            logger.warning(f"Ошибка PE анализа: {e}")
            pe_info["valid"] = False
            pe_info["error"] = str(e)
        
        return pe_info
    
    def _extract_strings(self, path: Path, min_length: int = 4) -> List[str]:
        """Извлечение строк из файла"""
        strings = []
        
        try:
            with open(path, 'rb') as f:
                content = f.read()
            
            # ASCII строки
            ascii_pattern = b'[\x20-\x7e]{' + str(min_length).encode() + b',}'
            import re
            ascii_strings = re.findall(ascii_pattern, content)
            strings.extend([s.decode('ascii', errors='ignore') for s in ascii_strings])
            
            # Unicode строки
            unicode_pattern = b'(?:[\x20-\x7e]\x00){' + str(min_length).encode() + b',}'
            unicode_strings = re.findall(unicode_pattern, content)
            strings.extend([s.decode('utf-16-le', errors='ignore') for s in unicode_strings])
            
        except Exception as e:
            logger.warning(f"Ошибка извлечения строк: {e}")
        
        return strings[:1000]  # Ограничение на количество строк
    
    def _run_yara_scan(self, path: Path) -> List[Dict]:
        """Сканирование YARA правилами"""
        matches = []
        
        try:
            import yara
            
            # Загрузка правил из директории rules/
            rules_dir = Path("rules")
            if rules_dir.exists():
                rule_files = list(rules_dir.glob("*.yar")) + list(rules_dir.glob("*.yara"))
                
                if rule_files:
                    compiled_rules = yara.compile(filepaths={str(f): str(f) for f in rule_files})
                    file_matches = compiled_rules.match(str(path))
                    
                    for match in file_matches:
                        matches.append({
                            "rule": match.rule,
                            "namespace": match.namespace,
                            "strings": [s[2] for s in match.strings]
                        })
        except ImportError:
            logger.info("YARA не установлен, пропускаем сканирование")
        except Exception as e:
            logger.warning(f"Ошибка YARA сканирования: {e}")
        
        return matches
