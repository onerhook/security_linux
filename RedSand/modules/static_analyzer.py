#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Static Analyzer - Статический анализ файлов
PE анализ, хеши, строки, YARA правила
"""

import hashlib
import os
from pathlib import Path

try:
    import pefile
    PE_AVAILABLE = True
except ImportError:
    PE_AVAILABLE = False

try:
    import yara
    YARA_AVAILABLE = True
except ImportError:
    YARA_AVAILABLE = False

class StaticAnalyzer:
    def __init__(self):
        self.yara_rules = []
        if YARA_AVAILABLE:
            self._load_yara_rules()
    
    def _load_yara_rules(self):
        """Загрузка YARA правил"""
        rules_dir = Path('rules')
        if rules_dir.exists():
            for rule_file in rules_dir.glob('*.yar'):
                try:
                    rule = yara.compile(str(rule_file))
                    self.yara_rules.append(rule)
                except Exception as e:
                    print(f"[-] Ошибка загрузки правила {rule_file}: {e}")
    
    def analyze(self, file_path):
        """Полный статический анализ файла"""
        results = {
            'file_info': self._get_file_info(file_path),
            'hashes': self._calculate_hashes(file_path),
            'strings': self._extract_strings(file_path),
            'pe_info': {},
            'yara_matches': []
        }
        
        # PE анализ для Windows исполняемых файлов
        if PE_AVAILABLE and file_path.lower().endswith(('.exe', '.dll', '.sys')):
            results['pe_info'] = self._analyze_pe(file_path)
        
        # YARA сканирование
        if YARA_AVAILABLE:
            results['yara_matches'] = self._scan_yara(file_path)
        
        return results
    
    def _get_file_info(self, file_path):
        """Базовая информация о файле"""
        return {
            'name': os.path.basename(file_path),
            'size': os.path.getsize(file_path),
            'path': file_path,
            'extension': Path(file_path).suffix.lower()
        }
    
    def _calculate_hashes(self, file_path):
        """Вычисление хешей файла"""
        hashes = {}
        
        with open(file_path, 'rb') as f:
            data = f.read()
            
            hashes['md5'] = hashlib.md5(data).hexdigest()
            hashes['sha1'] = hashlib.sha1(data).hexdigest()
            hashes['sha256'] = hashlib.sha256(data).hexdigest()
            hashes['sha512'] = hashlib.sha512(data).hexdigest()
        
        return hashes
    
    def _extract_strings(self, file_path, min_length=4):
        """Извлечение строк из файла"""
        strings = []
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                
                # ASCII строки
                ascii_strings = []
                current_string = []
                
                for byte in data:
                    if 32 <= byte <= 126:  # Печатаемые ASCII символы
                        current_string.append(chr(byte))
                    else:
                        if len(current_string) >= min_length:
                            ascii_strings.append(''.join(current_string))
                        current_string = []
                
                if len(current_string) >= min_length:
                    ascii_strings.append(''.join(current_string))
                
                strings = ascii_strings[:1000]  # Ограничиваем количество
                
        except Exception as e:
            strings = [f"Error extracting strings: {str(e)}"]
        
        return strings
    
    def _analyze_pe(self, file_path):
        """Анализ PE файла"""
        pe_info = {}
        
        try:
            pe = pefile.PE(file_path)
            
            pe_info = {
                'machine': pefile.MACHINE_TYPE[pe.FILE_HEADER.Machine] if hasattr(pefile, 'MACHINE_TYPE') else pe.FILE_HEADER.Machine,
                'subsystem': pefile.SUBSYSTEM_TYPE[pe.OPTIONAL_HEADER.Subsystem] if hasattr(pefile, 'SUBSYSTEM_TYPE') else pe.OPTIONAL_HEADER.Subsystem,
                'entry_point': hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint),
                'image_base': hex(pe.OPTIONAL_HEADER.ImageBase),
                'sections': [],
                'imports': [],
                'exports': [],
                'resources': []
            }
            
            # Информация о секциях
            for section in pe.sections:
                section_info = {
                    'name': section.Name.decode('utf-8', errors='ignore').rstrip('\x00'),
                    'virtual_size': section.Misc_VirtualSize,
                    'raw_size': section.SizeOfRawData,
                    'characteristics': section.Characteristics
                }
                pe_info['sections'].append(section_info)
            
            # Импорты
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    pe_info['imports'].append(entry.dll.decode('utf-8', errors='ignore'))
            
            # Экспорты
            if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
                pe_info['exports_count'] = len(pe.DIRECTORY_ENTRY_EXPORT.symbols)
            
            # Ресурсы
            if hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE'):
                pe_info['resources_count'] = len(pe.DIRECTORY_ENTRY_RESOURCE.entries)
            
        except Exception as e:
            pe_info = {'error': str(e)}
        
        return pe_info
    
    def _scan_yara(self, file_path):
        """Сканирование YARA правилами"""
        matches = []
        
        for rule in self.yara_rules:
            try:
                result = rule.match(file_path)
                for match in result:
                    matches.append({
                        'rule_name': match.rule,
                        'namespace': match.namespace,
                        'strings': [s for s in match.strings]
                    })
            except Exception as e:
                continue
        
        return matches
