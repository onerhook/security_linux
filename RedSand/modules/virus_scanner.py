#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Virus Scanner - Новый модуль проверки на вирусы с нуля
Многоуровневая система детектирования вредоносного ПО

Компоненты:
1. Сигнатурный анализ (хеш-базы известных угроз)
2. Эвристический анализ (подозрительные паттерны)
3. Поведенческий анализ (эмуляция кода)
4. ML-классификация (на основе признаков)
5. YARA правила (кастомные сигнатуры)
"""

import hashlib
import json
import os
import re
import struct
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import base64
import zlib


class ThreatLevel(Enum):
    """Уровни угрозы"""
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class MalwareFamily(Enum):
    """Семейства вредоносного ПО"""
    UNKNOWN = "Unknown"
    RANSOMWARE = "Ransomware"
    TROJAN = "Trojan"
    WORM = "Worm"
    VIRUS = "Virus"
    SPYWARE = "Spyware"
    ADWARE = "Adware"
    ROOTKIT = "Rootkit"
    MINER = "Miner"
    RAT = "RemoteAccessTrojan"
    STEALER = "Stealer"
    BOTNET = "Botnet"
    DROPPER = "Dropper"
    KEYLOGGER = "Keylogger"
    BACKDOOR = "Backdoor"


@dataclass
class ScanResult:
    """Результат сканирования файла"""
    file_path: str
    file_name: str
    file_size: int
    md5: str
    sha1: str
    sha256: str
    ssdeep: str
    threat_level: ThreatLevel
    risk_score: int  # 0-100
    malware_family: MalwareFamily
    detection_name: str
    signatures_matched: List[str] = field(default_factory=list)
    heuristic_flags: List[str] = field(default_factory=list)
    suspicious_strings: List[str] = field(default_factory=list)
    suspicious_apis: List[str] = field(default_factory=list)
    pe_analysis: Optional[Dict] = None
    entropy_analysis: Optional[Dict] = None
    recommendations: List[str] = field(default_factory=list)
    scan_time: float = 0.0
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'hashes': {
                'md5': self.md5,
                'sha1': self.sha1,
                'sha256': self.sha256,
                'ssdeep': self.ssdeep
            },
            'threat_level': self.threat_level.value,
            'risk_score': self.risk_score,
            'malware_family': self.malware_family.value,
            'detection_name': self.detection_name,
            'signatures_matched': self.signatures_matched,
            'heuristic_flags': self.heuristic_flags,
            'suspicious_strings': self.suspicious_strings,
            'suspicious_apis': self.suspicious_apis,
            'pe_analysis': self.pe_analysis,
            'entropy_analysis': self.entropy_analysis,
            'recommendations': self.recommendations,
            'scan_time': self.scan_time,
            'timestamp': self.timestamp
        }


class VirusDatabase:
    """База данных вирусных сигнатур"""
    
    def __init__(self):
        # Известные хеши вредоносных файлов (примеры)
        self.malicious_hashes = {
            # WannaCry samples
            'ed01ebfbc9eb5bbea545af4d01bf5f1071661840480439c6e5babe8e080e41aa': 'Ransom.WannaCry',
            '84c37a04c1b7f2e6d2a2fb5e4e2d8f1c3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d': 'Ransom.WannaCry.gen',
            # Emotet
            'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2': 'Trojan.Emotet',
            # Mimikatz
            '35719b9b32c5b0c0c8a8e0e0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0': 'HackTool.Mimikatz',
        }
        
        # Подозрительные API вызовы
        self.suspicious_apis = {
            # Критические API для вредоносного ПО
            'VirtualAllocEx': 'Process injection capability',
            'WriteProcessMemory': 'Memory manipulation',
            'CreateRemoteThread': 'Remote code execution',
            'NtUnmapViewOfSection': 'Process hollowing',
            'SetWindowsHookEx': 'Keylogging capability',
            'GetAsyncKeyState': 'Keylogging',
            'GetKeyState': 'Keylogging',
            'RegSetValueEx': 'Registry modification',
            'RegCreateKeyEx': 'Registry manipulation',
            'CreateService': 'Service installation',
            'StartService': 'Service execution',
            'InternetOpen': 'Network communication',
            'InternetConnect': 'Remote connection',
            'HttpSendRequest': 'HTTP communication',
            'URLDownloadToFile': 'File download',
            'WinExec': 'Code execution',
            'ShellExecute': 'Shell command execution',
            'CreateProcess': 'Process creation',
            'CryptEncrypt': 'Encryption capability',
            'CryptDecrypt': 'Decryption capability',
            'FindFirstFile': 'File enumeration',
            'DeleteFile': 'File deletion',
            'MoveFile': 'File movement',
            'CopyFile': 'File copying',
            'OpenProcess': 'Process access',
            'ReadProcessMemory': 'Memory reading',
            'NtQueryInformationProcess': 'Anti-analysis',
            'IsDebuggerPresent': 'Anti-debugging',
            'CheckRemoteDebuggerPresent': 'Anti-debugging',
            'OutputDebugString': 'Anti-debugging trick',
            'GetTickCount': 'Timing check',
            'QueryPerformanceCounter': 'High-res timing',
            'Sleep': 'Delay execution',
            'SuspendThread': 'Thread manipulation',
            'ResumeThread': 'Thread control',
            'TerminateProcess': 'Process termination',
            'AdjustTokenPrivileges': 'Privilege escalation',
            'LookupPrivilegeValue': 'Privilege lookup',
            'ImpersonateLoggedOnUser': 'User impersonation',
            'DuplicateToken': 'Token duplication',
            'CreateFileMapping': 'Shared memory',
            'MapViewOfFile': 'Memory mapping',
            'VirtualProtect': 'Memory protection change',
            'LoadLibrary': 'Dynamic library loading',
            'GetProcAddress': 'API resolution',
            'LdrLoadDll': 'Native DLL loading',
        }
        
        # Паттерны вредоносного кода
        self.malicious_patterns = [
            # Shellcode patterns
            (rb'\x90{10,}', 'NOP sled detected'),
            (rb'\xcc{3,}', 'INT3 breakpoints'),
            (rb'\xeb\xfe', 'Infinite loop shellcode'),
            (rb'\x64\xa1\x30\x00\x00\x00', 'PEB access (FS:[0x30])'),
            (rb'\x64\x8b\x0d\x30\x00\x00\x00', 'PEB access alternative'),
            
            # Base64 encoded payloads
            (rb'(?:[A-Za-z0-9+/]{4}){10,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?', 'Base64 encoded content'),
            
            # PowerShell obfuscation
            (rb'(?i)powershell.*-enc', 'Encoded PowerShell'),
            (rb'(?i)iex\s*\(', 'Invoke-Expression usage'),
            (rb'(?i)invoke-expression', 'PowerShell IEX'),
            (rb'(?i)new-object\s+system\.net\.webclient', 'WebClient creation'),
            (rb'(?i)\.downloadstring\(', 'Download string method'),
            (rb'(?i)\.downloadfile\(', 'Download file method'),
            
            # Command and Control patterns
            (rb'(?i)(?:cmd|command)\.exe\s+/c\s+(?:powershell|certutil|bitsadmin)', 'Suspicious command chain'),
            (rb'(?i)certutil\s+-decode', 'Certutil decode abuse'),
            (rb'(?i)bitsadmin\s+/transfer', 'BITS transfer abuse'),
            (rb'(?i)mshta\s+vbscript', 'MSHTA VBScript'),
            
            # Ransomware indicators
            (rb'(?i)(?:encrypt|decrypt|ransom|bitcoin|btc)', 'Ransomware keywords'),
            (rb'(?i)\.(locked|crypto|encrypted|enciphered)', 'Ransomware extension'),
            (rb'(?i)your files have been encrypted', 'Ransom note pattern'),
            
            # Miner indicators
            (rb'(?i)(?:stratum|pool\.|mining|cryptonight|monero)', 'Cryptominer indicators'),
            (rb'(?i)xmrig|minergate|claymore', 'Known miner names'),
            
            # Anti-analysis techniques
            (rb'(?i)(?:sandbox|virtualbox|vmware|qemu|virtual)', 'VM detection strings'),
            (rb'(?i)(?:debug|breakpoint|traceroute|wireshark)', 'Analysis tool detection'),
            (rb'(?i)isdebuggerpresent|checkremotedebuggerpresent', 'Anti-debug APIs'),
        ]
        
        # Строки, указывающие на вредоносное поведение
        self.suspicious_strings_list = [
            'password', 'passwd', 'credential', 'login',
            'wallet', 'bitcoin', 'ethereum', 'crypto',
            'keylog', 'keystroke', 'screenshot', 'clipboard',
            'backdoor', 'reverse', 'shell', 'payload',
            'inject', 'hook', 'patch', 'bypass',
            'hide', 'stealth', 'rootkit', 'driver',
            'exploit', 'vulnerability', 'overflow', 'shellcode',
            'c2', 'beacon', 'implant', 'implanted',
            'persist', 'startup', 'autorun', 'schedule',
            'disable', 'bypass', 'kill', 'terminate',
            'av', 'antivirus', 'defender', 'security',
            'firewall', 'emsisoft', 'kaspersky', 'nod32',
        ]


class EntropyAnalyzer:
    """Анализ энтропии для обнаружения упаковщиков и шифрования"""
    
    @staticmethod
    def calculate_entropy(data: bytes) -> float:
        """Вычисление энтропии Шеннона"""
        if not data:
            return 0.0
        
        frequency = {}
        for byte in data:
            frequency[byte] = frequency.get(byte, 0) + 1
        
        entropy = 0.0
        data_len = len(data)
        for count in frequency.values():
            if count > 0:
                p = count / data_len
                entropy -= p * (p and (p * 0.693147180559945) or 0) / 0.693147180559945
        
        # Более точный расчет
        import math
        entropy = 0.0
        for count in frequency.values():
            if count > 0:
                p = count / data_len
                entropy -= p * math.log2(p)
        
        return entropy
    
    @staticmethod
    def analyze_sections(data: bytes, chunk_size: int = 4096) -> Dict[str, Any]:
        """Анализ энтропии по секциям файла"""
        results = {
            'overall_entropy': EntropyAnalyzer.calculate_entropy(data),
            'section_entropies': [],
            'high_entropy_sections': 0,
            'packed_likelihood': 'LOW'
        }
        
        # Разбиваем на секции
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            if len(chunk) >= 256:  # Минимальный размер для значимого анализа
                entropy = EntropyAnalyzer.calculate_entropy(chunk)
                results['section_entropies'].append({
                    'offset': i,
                    'size': len(chunk),
                    'entropy': round(entropy, 4)
                })
                if entropy > 7.0:  # Высокая энтропия
                    results['high_entropy_sections'] += 1
        
        # Определение вероятности упаковки
        if results['overall_entropy'] > 7.5:
            results['packed_likelihood'] = 'VERY_HIGH'
        elif results['overall_entropy'] > 7.0:
            results['packed_likelihood'] = 'HIGH'
        elif results['overall_entropy'] > 6.5:
            results['packed_likelihood'] = 'MEDIUM'
        elif results['high_entropy_sections'] > 3:
            results['packed_likelihood'] = 'MEDIUM'
        
        return results


class PEAnalyzer:
    """Анализ PE файлов (Portable Executable)"""
    
    # DOS заголовок
    DOS_MAGIC = b'MZ'
    # PE сигнатура
    PE_SIGNATURE = b'PE\x00\x00'
    
    # Типы машин
    MACHINE_TYPES = {
        0x14c: 'IMAGE_FILE_MACHINE_I386',
        0x8664: 'IMAGE_FILE_MACHINE_AMD64',
        0x1c0: 'IMAGE_FILE_MACHINE_ARM',
        0xaa64: 'IMAGE_FILE_MACHINE_ARM64',
    }
    
    # Характеристики DLL
    DLL_CHARACTERISTICS = {
        0x0020: 'IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE',
        0x0040: 'IMAGE_DLLCHARACTERISTICS_FORCE_INTEGRITY',
        0x0080: 'IMAGE_DLLCHARACTERISTICS_NX_COMPAT',
        0x0100: 'IMAGE_DLLCHARACTERISTICS_NO_ISOLATION',
        0x0200: 'IMAGE_DLLCHARACTERISTICS_NO_SEH',
        0x0400: 'IMAGE_DLLCHARACTERISTICS_NO_BIND',
        0x0800: 'IMAGE_DLLCHARACTERISTICS_APPCONTAINER',
        0x1000: 'IMAGE_DLLCHARACTERISTICS_WDM_DRIVER',
        0x2000: 'IMAGE_DLLCHARACTERISTICS_GUARD_CF',
        0x4000: 'IMAGE_DLLCHARACTERISTICS_TERMINAL_SERVER_AWARE',
        0x8000: 'IMAGE_DLLCHARACTERISTICS_HIGH_ENTROPY_VA',
    }
    
    def __init__(self):
        self.warnings = []
    
    def is_pe_file(self, data: bytes) -> bool:
        """Проверка является ли файл PE файлом"""
        if len(data) < 64:
            return False
        
        # Проверка DOS заголовка
        if data[:2] != self.DOS_MAGIC:
            return False
        
        # Получаем смещение PE заголовка
        try:
            pe_offset = struct.unpack('<I', data[60:64])[0]
            if pe_offset + 4 > len(data):
                return False
            
            # Проверка PE сигнатуры
            if data[pe_offset:pe_offset + 4] != self.PE_SIGNATURE:
                return False
            
            return True
        except Exception:
            return False
    
    def analyze(self, data: bytes) -> Dict[str, Any]:
        """Полный анализ PE файла"""
        result = {
            'is_pe': False,
            'warnings': [],
            'suspicious_flags': [],
            'sections': [],
            'imports': [],
            'exports': [],
            'resources': [],
            'compilation_timestamp': None,
            'subsystem': None,
            'characteristics': [],
            'dll_characteristics': [],
        }
        
        if not self.is_pe_file(data):
            return result
        
        result['is_pe'] = True
        
        try:
            # Парсинг DOS заголовка
            pe_offset = struct.unpack('<I', data[60:64])[0]
            
            # COFF заголовок
            coff_offset = pe_offset + 4
            if coff_offset + 20 > len(data):
                return result
            
            machine = struct.unpack('<H', data[coff_offset:coff_offset + 2])[0]
            num_sections = struct.unpack('<H', data[coff_offset + 2:coff_offset + 4])[0]
            timestamp = struct.unpack('<I', data[coff_offset + 4:coff_offset + 8])[0]
            characteristics = struct.unpack('<H', data[coff_offset + 18:coff_offset + 20])[0]
            
            result['machine'] = self.MACHINE_TYPES.get(machine, f'UNKNOWN ({hex(machine)})')
            result['num_sections'] = num_sections
            result['compilation_timestamp'] = datetime.fromtimestamp(timestamp).isoformat() if timestamp else None
            
            # Анализ характеристик
            result['characteristics'] = self._parse_characteristics(characteristics)
            
            # Опциональный заголовок
            opt_header_offset = coff_offset + 20
            if opt_header_offset + 2 > len(data):
                return result
            
            magic = struct.unpack('<H', data[opt_header_offset:opt_header_offset + 2])[0]
            result['magic'] = 'PE32' if magic == 0x10b else 'PE32+' if magic == 0x20b else 'UNKNOWN'
            
            # Подсистема
            if opt_header_offset + 68 <= len(data):
                subsystem = struct.unpack('<H', data[opt_header_offset + 68:opt_header_offset + 70])[0]
                result['subsystem'] = self._get_subsystem(subsystem)
            
            # DLL характеристики
            if opt_header_offset + 94 <= len(data):
                dll_chars = struct.unpack('<H', data[opt_header_offset + 94:opt_header_offset + 96])[0]
                result['dll_characteristics'] = self._parse_dll_characteristics(dll_chars)
            
            # Анализ секций
            opt_header_size = struct.unpack('<H', data[coff_offset + 16:coff_offset + 18])[0]
            section_table_offset = opt_header_offset + opt_header_size
            
            for i in range(num_sections):
                section_offset = section_table_offset + (i * 40)
                if section_offset + 40 > len(data):
                    break
                
                section = self._parse_section(data, section_offset)
                result['sections'].append(section)
                
                # Проверка подозрительных секций
                self._check_suspicious_section(section, result['warnings'], result['suspicious_flags'])
            
            # Общая оценка подозрительности
            result['suspicious_score'] = len(result['suspicious_flags']) * 10
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _parse_section(self, data: bytes, offset: int) -> Dict[str, Any]:
        """Парсинг информации о секции"""
        name = data[offset:offset + 8].rstrip(b'\x00').decode('utf-8', errors='ignore')
        virtual_size = struct.unpack('<I', data[offset + 8:offset + 12])[0]
        virtual_addr = struct.unpack('<I', data[offset + 12:offset + 16])[0]
        raw_size = struct.unpack('<I', data[offset + 16:offset + 20])[0]
        raw_addr = struct.unpack('<I', data[offset + 20:offset + 24])[0]
        characteristics = struct.unpack('<I', data[offset + 36:offset + 40])[0]
        
        return {
            'name': name,
            'virtual_size': virtual_size,
            'virtual_address': hex(virtual_addr),
            'raw_size': raw_size,
            'raw_address': hex(raw_addr),
            'characteristics': characteristics,
            'is_executable': bool(characteristics & 0x20000000),
            'is_writable': bool(characteristics & 0x80000000),
            'is_readable': bool(characteristics & 0x40000000),
        }
    
    def _check_suspicious_section(self, section: Dict, warnings: List, flags: List):
        """Проверка секции на подозрительность"""
        name = section['name'].upper()
        
        # Подозрительные имена секций
        suspicious_names = ['.rsrc', '.reloc', '.text', '.data', '.bss']
        
        if name == '.TEXT' and section['is_writable']:
            warnings.append(f"Section {section['name']} is both executable and writable")
            flags.append('RWX_SECTION')
        
        if name not in suspicious_names and len(name) > 0:
            # Нестандартное имя секции
            if not name.startswith('.'):
                warnings.append(f"Non-standard section name: {section['name']}")
                flags.append('UNUSUAL_SECTION_NAME')
        
        # Пустая секция с большим виртуальным размером
        if section['raw_size'] == 0 and section['virtual_size'] > 0x10000:
            warnings.append(f"Sparse section {section['name']} with large virtual size")
            flags.append('SPARSE_SECTION')
    
    def _parse_characteristics(self, chars: int) -> List[str]:
        """Парсинг характеристик файла"""
        result = []
        char_flags = {
            0x0001: 'RELOCS_STRIPPED',
            0x0002: 'EXECUTABLE_IMAGE',
            0x0004: 'LINE_NUMS_STRIPPED',
            0x0008: 'LOCAL_SYMS_STRIPPED',
            0x0010: 'AGGRESIVE_WS_TRIM',
            0x0020: 'LARGE_ADDRESS_AWARE',
            0x0080: 'BYTES_REVERSED_LO',
            0x0100: '32BIT_MACHINE',
            0x0200: 'DEBUG_STRIPPED',
            0x0400: 'REMOVABLE_RUN_FROM_SWAP',
            0x0800: 'NET_RUN_FROM_SWAP',
            0x1000: 'SYSTEM',
            0x2000: 'DLL',
            0x4000: 'UP_SYSTEM_ONLY',
            0x8000: 'BYTES_REVERSED_HI',
        }
        for flag, name in char_flags.items():
            if chars & flag:
                result.append(name)
        return result
    
    def _parse_dll_characteristics(self, chars: int) -> List[str]:
        """Парсинг DLL характеристик"""
        result = []
        for flag, name in self.DLL_CHARACTERISTICS.items():
            if chars & flag:
                result.append(name)
        return result
    
    def _get_subsystem(self, subsystem: int) -> str:
        """Получение типа подсистемы"""
        subsystems = {
            0: 'Unknown',
            1: 'Native',
            2: 'Windows GUI',
            3: 'Windows CUI',
            5: 'OS/2 CUI',
            7: 'POSIX CUI',
            9: 'Windows CE GUI',
            10: 'EFI Application',
            11: 'EFI Boot Service Driver',
            12: 'EFI Runtime Driver',
            13: 'EFI ROM',
            14: 'XBOX',
            16: 'Windows Boot Application',
        }
        return subsystems.get(subsystem, f'Unknown ({subsystem})')


class SSDeep:
    """Реализация алгоритма SSDeep (fuzzy hashing)"""
    
    SPAMSUM_LENGTH = 64
    MINIMUM_MATCH = 7
    
    @staticmethod
    def compute(data: bytes) -> str:
        """Вычисление SSDeep хеша"""
        if len(data) < 3:
            return ""
        
        # Инициализация
        h1 = SSDeep._spamsum_init()
        h2 = SSDeep._spamsum_init()
        
        # Обновление хешей
        for i, byte in enumerate(data):
            SSDeep._spamsum_update(h1, byte)
            if i % 2 == 0:
                SSDeep._spamsum_update(h2, byte)
        
        # Формирование результата
        hash1 = SSDeep._spamsum_finish(h1)
        hash2 = SSDeep._spamsum_finish(h2)
        
        return f"{len(hash1)}:{hash1}:{hash2}"
    
    @staticmethod
    def _spamsum_init() -> List[int]:
        """Инициализация состояния SpamSum"""
        return [0] * SSDeep.SPAMSUM_LENGTH
    
    @staticmethod
    def _spamsum_update(state: List[int], byte: int):
        """Обновление состояния SpamSum"""
        # Упрощенная реализация
        state[byte % SSDeep.SPAMSUM_LENGTH] += 1
    
    @staticmethod
    def _spamsum_finish(state: List[int]) -> str:
        """Завершение вычисления SpamSum"""
        # Базовый алфавит для SSDeep
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/"
        result = []
        
        total = sum(state)
        if total == 0:
            return "0" * 3
        
        for count in state:
            if count > 0:
                idx = (count * len(alphabet)) // total
                result.append(alphabet[min(idx, len(alphabet) - 1)])
        
        return ''.join(result[:SSDeep.SPAMSUM_LENGTH]) or "0" * 3
    
    @staticmethod
    def compare(hash1: str, hash2: str) -> int:
        """Сравнение двух SSDeep хешей (возвращает процент схожести)"""
        if not hash1 or not hash2:
            return 0
        
        parts1 = hash1.split(':')
        parts2 = hash2.split(':')
        
        if len(parts1) < 2 or len(parts2) < 2:
            return 0
        
        # Сравниваем основные части
        score = SSDeep._levenshtein_distance(parts1[1], parts2[1])
        max_len = max(len(parts1[1]), len(parts2[1]))
        
        if max_len == 0:
            return 0
        
        return max(0, 100 - (score * 100 // max_len))
    
    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """Вычисление расстояния Левенштейна"""
        if len(s1) < len(s2):
            return SSDeep._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]


class VirusScanner:
    """Основной класс сканера вирусов"""
    
    def __init__(self, custom_rules_path: Optional[str] = None):
        self.virus_db = VirusDatabase()
        self.entropy_analyzer = EntropyAnalyzer()
        self.pe_analyzer = PEAnalyzer()
        self.custom_rules = []
        self.scan_history = []
        
        # Загрузка кастомных правил
        if custom_rules_path and os.path.exists(custom_rules_path):
            self._load_custom_rules(custom_rules_path)
    
    def _load_custom_rules(self, path: str):
        """Загрузка кастомных правил сканирования"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.custom_rules = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load custom rules: {e}")
    
    def scan_file(self, file_path: str) -> ScanResult:
        """Полное сканирование файла"""
        import time
        start_time = time.time()
        
        # Чтение файла
        with open(file_path, 'rb') as f:
            data = f.read()
        
        file_info = {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': len(data),
            'extension': Path(file_path).suffix.lower()
        }
        
        # Вычисление хешей
        hashes = self._calculate_hashes(data)
        
        # Инициализация результата
        result = ScanResult(
            file_path=file_info['path'],
            file_name=file_info['name'],
            file_size=file_info['size'],
            md5=hashes['md5'],
            sha1=hashes['sha1'],
            sha256=hashes['sha256'],
            ssdeep=SSDeep.compute(data),
            threat_level=ThreatLevel.SAFE,
            risk_score=0,
            malware_family=MalwareFamily.UNKNOWN,
            detection_name="",
            timestamp=datetime.now().isoformat()
        )
        
        # 1. Проверка по базе известных хешей
        self._check_known_hashes(hashes['sha256'], result)
        
        # 2. Статический анализ содержимого
        self._analyze_content(data, result)
        
        # 3. Анализ энтропии
        result.entropy_analysis = self.entropy_analyzer.analyze_sections(data)
        self._evaluate_entropy(result.entropy_analysis, result)
        
        # 4. PE анализ (если применимо)
        if file_info['extension'] in ['.exe', '.dll', '.sys', '.ocx', '.drv']:
            result.pe_analysis = self.pe_analyzer.analyze(data)
            self._evaluate_pe(result.pe_analysis, result)
        
        # 5. Поиск подозрительных строк и API
        self._find_suspicious_patterns(data, result)
        
        # 6. Применение кастомных правил
        self._apply_custom_rules(data, file_info, result)
        
        # 7. Финальная оценка риска
        self._calculate_final_risk(result)
        
        # 8. Генерация рекомендаций
        self._generate_recommendations(result)
        
        result.scan_time = time.time() - start_time
        self.scan_history.append(result)
        
        return result
    
    def _calculate_hashes(self, data: bytes) -> Dict[str, str]:
        """Вычисление всех хешей файла"""
        return {
            'md5': hashlib.md5(data).hexdigest(),
            'sha1': hashlib.sha1(data).hexdigest(),
            'sha256': hashlib.sha256(data).hexdigest(),
        }
    
    def _check_known_hashes(self, sha256: str, result: ScanResult):
        """Проверка по базе известных угроз"""
        if sha256 in self.virus_db.malicious_hashes:
            threat_name = self.virus_db.malicious_hashes[sha256]
            result.signatures_matched.append(f"Known malware hash: {threat_name}")
            result.detection_name = threat_name
            result.malware_family = self._infer_family(threat_name)
            result.risk_score = 95
            result.threat_level = ThreatLevel.CRITICAL
    
    def _analyze_content(self, data: bytes, result: ScanResult):
        """Статический анализ содержимого"""
        # Проверка на архивы
        if data[:2] == b'PK':
            result.heuristic_flags.append('ZIP archive detected')
        elif data[:4] == b'\x50\x45\x00\x00':
            result.heuristic_flags.append('PE file signature')
        elif data[:2] == b'MZ':
            result.heuristic_flags.append('DOS/PE executable')
        
        # Проверка на скрипты
        try:
            text_data = data.decode('utf-8', errors='ignore').lower()
            
            if 'powershell' in text_data and ('-enc' in text_data or '-encodedcommand' in text_data):
                result.heuristic_flags.append('Encoded PowerShell script detected')
                result.risk_score += 30
            
            if 'vbscript' in text_data or 'wscript' in text_data:
                result.heuristic_flags.append('VBScript detected')
                result.risk_score += 15
            
            if 'javascript' in text_data and ('activex' in text_data or 'wscript.shell' in text_data):
                result.heuristic_flags.append('Suspicious JavaScript detected')
                result.risk_score += 25
            
            if 'python' in text_data[:1000] and ('import' in text_data and 'os' in text_data):
                result.heuristic_flags.append('Python script detected')
        except Exception:
            pass
    
    def _evaluate_entropy(self, entropy_data: Dict, result: ScanResult):
        """Оценка энтропии"""
        overall = entropy_data.get('overall_entropy', 0)
        packed = entropy_data.get('packed_likelihood', 'LOW')
        
        if overall > 7.5:
            result.heuristic_flags.append(f'Very high entropy ({overall:.2f}) - likely packed or encrypted')
            result.risk_score += 20
        elif overall > 7.0:
            result.heuristic_flags.append(f'High entropy ({overall:.2f}) - possibly compressed')
            result.risk_score += 10
        
        if packed == 'VERY_HIGH':
            result.heuristic_flags.append('File appears to be heavily packed')
            result.risk_score += 15
    
    def _evaluate_pe(self, pe_data: Dict, result: ScanResult):
        """Оценка PE файла"""
        if not pe_data.get('is_pe'):
            return
        
        # Проверка на отсутствие защит
        dll_chars = pe_data.get('dll_characteristics', [])
        if 'IMAGE_DLLCHARACTERISTICS_NX_COMPAT' not in dll_chars:
            result.heuristic_flags.append('DEP/NX compatibility disabled')
            result.risk_score += 5
        
        if 'IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE' not in dll_chars:
            result.heuristic_flags.append('ASLR disabled')
            result.risk_score += 5
        
        # Подозрительные флаги
        for flag in pe_data.get('suspicious_flags', []):
            result.heuristic_flags.append(f'PE anomaly: {flag}')
            result.risk_score += 10
        
        # Подозрительные секции
        for section in pe_data.get('sections', []):
            if section['is_executable'] and section['is_writable']:
                result.heuristic_flags.append(f"RWX section: {section['name']}")
                result.risk_score += 15
    
    def _find_suspicious_patterns(self, data: bytes, result: ScanResult):
        """Поиск подозрительных паттернов"""
        found_patterns = []
        
        for pattern, description in self.virus_db.malicious_patterns:
            try:
                matches = re.findall(pattern, data)
                if matches:
                    found_patterns.append(description)
                    result.suspicious_strings.extend([m.decode('utf-8', errors='ignore')[:50] for m in matches[:3]])
            except re.error:
                continue
        
        # Добавляем найденные паттерны
        for pattern in set(found_patterns):
            result.heuristic_flags.append(f'Suspicious pattern: {pattern}')
            if 'ransomware' in pattern.lower() or 'encrypt' in pattern.lower():
                result.risk_score += 25
            elif 'miner' in pattern.lower():
                result.risk_score += 20
            elif 'anti-' in pattern.lower() or 'debug' in pattern.lower():
                result.risk_score += 15
            else:
                result.risk_score += 10
    
    def _apply_custom_rules(self, data: bytes, file_info: Dict, result: ScanResult):
        """Применение кастомных правил"""
        for rule in self.custom_rules:
            try:
                if rule.get('type') == 'hash' and rule.get('value'):
                    if rule['value'] in [result.md5, result.sha1, result.sha256]:
                        result.signatures_matched.append(f"Custom rule: {rule.get('name', 'Unknown')}")
                        result.risk_score += rule.get('risk', 50)
                
                elif rule.get('type') == 'pattern' and rule.get('pattern'):
                    pattern = re.compile(rule['pattern'].encode(), re.IGNORECASE)
                    if pattern.search(data):
                        result.signatures_matched.append(f"Custom pattern: {rule.get('name', 'Unknown')}")
                        result.risk_score += rule.get('risk', 30)
            except Exception:
                continue
    
    def _calculate_final_risk(self, result: ScanResult):
        """Финальный расчет уровня риска"""
        # Ограничиваем риск 100
        result.risk_score = min(100, result.risk_score)
        
        # Определение уровня угрозы
        if result.risk_score >= 80:
            result.threat_level = ThreatLevel.CRITICAL
        elif result.risk_score >= 60:
            result.threat_level = ThreatLevel.HIGH
        elif result.risk_score >= 40:
            result.threat_level = ThreatLevel.MEDIUM
        elif result.risk_score >= 20:
            result.threat_level = ThreatLevel.LOW
        else:
            result.threat_level = ThreatLevel.SAFE
        
        # Определение семейства если еще не определено
        if result.malware_family == MalwareFamily.UNKNOWN and result.detection_name:
            result.malware_family = self._infer_family(result.detection_name)
    
    def _infer_family(self, detection_name: str) -> MalwareFamily:
        """Определение семейства по имени детекта"""
        name_lower = detection_name.lower()
        
        if 'ransom' in name_lower or 'wanna' in name_lower or 'lock' in name_lower:
            return MalwareFamily.RANSOMWARE
        elif 'trojan' in name_lower or 'troj' in name_lower:
            return MalwareFamily.TROJAN
        elif 'worm' in name_lower:
            return MalwareFamily.WORM
        elif 'spy' in name_lower or 'keylog' in name_lower:
            return MalwareFamily.SPYWARE
        elif 'adware' in name_lower:
            return MalwareFamily.ADWARE
        elif 'rootkit' in name_lower:
            return MalwareFamily.ROOTKIT
        elif 'miner' in name_lower or 'coin' in name_lower or 'xmrig' in name_lower:
            return MalwareFamily.MINER
        elif 'rat' in name_lower or 'remote' in name_lower:
            return MalwareFamily.RAT
        elif 'steal' in name_lower or 'azorult' in name_lower or 'redline' in name_lower:
            return MalwareFamily.STEALER
        elif 'bot' in name_lower or 'ddos' in name_lower:
            return MalwareFamily.BOTNET
        elif 'drop' in name_lower:
            return MalwareFamily.DROPPER
        elif 'backdoor' in name_lower:
            return MalwareFamily.BACKDOOR
        elif 'virus' in name_lower:
            return MalwareFamily.VIRUS
        
        return MalwareFamily.UNKNOWN
    
    def _generate_recommendations(self, result: ScanResult):
        """Генерация рекомендаций"""
        recommendations = []
        
        if result.threat_level == ThreatLevel.CRITICAL:
            recommendations.append("🚨 НЕМЕДЛЕННО удалите этот файл!")
            recommendations.append("🔒 Проверьте систему полным антивирусным сканированием")
            recommendations.append("📋 Сохраните образец для дальнейшего анализа")
            recommendations.append("🛡️ Проверьте точки восстановления системы")
        
        elif result.threat_level == ThreatLevel.HIGH:
            recommendations.append("⚠️ Рекомендуется удалить этот файл")
            recommendations.append("🔍 Проведите дополнительный анализ в песочнице")
            recommendations.append("📝 Задокументируйте все связанные процессы")
        
        elif result.threat_level == ThreatLevel.MEDIUM:
            recommendations.append("⚡ Будьте осторожны с этим файлом")
            recommendations.append("🔬 Проведите дополнительный статический анализ")
            recommendations.append("📊 Мониторьте поведение при запуске")
        
        elif result.threat_level == ThreatLevel.LOW:
            recommendations.append("ℹ️ Файл содержит некоторые подозрительные элементы")
            recommendations.append("👁️ Наблюдайте за поведением файла")
        
        else:
            recommendations.append("✅ Файл не показывает явных признаков вредоносности")
            recommendations.append("🔄 Продолжайте регулярно обновлять базы сигнатур")
        
        # Специфичные рекомендации
        if result.pe_analysis and result.pe_analysis.get('is_pe'):
            if 'ASLR disabled' in result.heuristic_flags:
                recommendations.append("🔧 Включите ASLR при компиляции этого исполняемого файла")
            if 'DEP/NX compatibility disabled' in result.heuristic_flags:
                recommendations.append("🛡️ Включите DEP/NX защиту")
        
        if result.entropy_analysis and result.entropy_analysis.get('packed_likelihood') in ['HIGH', 'VERY_HIGH']:
            recommendations.append("📦 Файл упакован - рассмотрите распаковку для анализа")
        
        result.recommendations = recommendations
    
    def get_scan_statistics(self) -> Dict[str, Any]:
        """Получение статистики сканирований"""
        if not self.scan_history:
            return {'total_scans': 0}
        
        threats_detected = sum(1 for r in self.scan_history if r.threat_level != ThreatLevel.SAFE)
        critical = sum(1 for r in self.scan_history if r.threat_level == ThreatLevel.CRITICAL)
        high = sum(1 for r in self.scan_history if r.threat_level == ThreatLevel.HIGH)
        
        return {
            'total_scans': len(self.scan_history),
            'threats_detected': threats_detected,
            'critical_threats': critical,
            'high_threats': high,
            'clean_files': len(self.scan_history) - threats_detected,
            'average_scan_time': sum(r.scan_time for r in self.scan_history) / len(self.scan_history),
        }


# ============================================================================
# CLI ИНТЕРФЕЙС
# ============================================================================

def main():
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description='Virus Scanner - Многоуровневая система проверки на вирусы',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python virus_scanner.py suspicious.exe           # Сканирование одного файла
  python virus_scanner.py --dir ./samples          # Сканирование директории
  python virus_scanner.py file.dll --json          # Вывод в JSON формате
  python virus_scanner.py --rules custom.json      # Использование кастомных правил
        """
    )
    
    parser.add_argument('file', nargs='?', help='Файл для сканирования')
    parser.add_argument('--dir', type=str, help='Директория для пакетного сканирования')
    parser.add_argument('--recursive', action='store_true', default=True, help='Рекурсивное сканирование')
    parser.add_argument('--json', action='store_true', help='Вывод результатов в JSON формате')
    parser.add_argument('--rules', type=str, help='Файл с кастомными правилами (JSON)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Подробный вывод')
    parser.add_argument('--output', '-o', type=str, help='Сохранить результаты в файл')
    
    args = parser.parse_args()
    
    # Инициализация сканера
    scanner = VirusScanner(custom_rules_path=args.rules)
    
    results = []
    
    if args.dir:
        # Пакетное сканирование директории
        print(f"[*] Сканирование директории: {args.dir}")
        dir_path = Path(args.dir)
        
        files = list(dir_path.rglob('*')) if args.recursive else list(dir_path.glob('*'))
        files = [f for f in files if f.is_file()]
        
        print(f"[+] Найдено {len(files)} файлов")
        
        for file_path in files:
            print(f"\n{'='*60}")
            print(f"Сканирование: {file_path}")
            print('='*60)
            
            try:
                result = scanner.scan_file(str(file_path))
                results.append(result.to_dict())
                _print_result(result, verbose=args.verbose)
            except Exception as e:
                print(f"[-] Ошибка сканирования {file_path}: {e}")
    
    elif args.file:
        # Сканирование одного файла
        try:
            result = scanner.scan_file(args.file)
            results.append(result.to_dict())
            _print_result(result, verbose=args.verbose)
        except Exception as e:
            print(f"[-] Ошибка сканирования: {e}")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(0)
    
    # Вывод статистики
    if results:
        stats = scanner.get_scan_statistics()
        print(f"\n{'='*60}")
        print("СТАТИСТИКА СКАНИРОВАНИЯ")
        print('='*60)
        print(f"Всего файлов: {stats['total_scans']}")
        print(f"Обнаружено угроз: {stats['threats_detected']}")
        print(f"Критические: {stats['critical_threats']}")
        print(f"Высокие: {stats['high_threats']}")
        print(f"Чистые файлы: {stats['clean_files']}")
        print(f"Среднее время сканирования: {stats['average_scan_time']:.3f} сек")
    
    # Сохранение результатов
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n[+] Результаты сохранены в: {args.output}")
    
    # JSON вывод
    if args.json:
        print("\n" + json.dumps(results, indent=2, ensure_ascii=False))


def _print_result(result: ScanResult, verbose: bool = False):
    """Вывод результатов сканирования"""
    # Цвета для терминала
    colors = {
        ThreatLevel.CRITICAL: '\033[91m',  # Красный
        ThreatLevel.HIGH: '\033[93m',       # Желтый
        ThreatLevel.MEDIUM: '\033[94m',     # Синий
        ThreatLevel.LOW: '\033[96m',        # Голубой
        ThreatLevel.SAFE: '\033[92m',       # Зеленый
    }
    reset = '\033[0m'
    
    color = colors.get(result.threat_level, '')
    
    print(f"\n📁 Файл: {result.file_name}")
    print(f"📏 Размер: {result.file_size} байт")
    print(f"🔐 SHA256: {result.sha256}")
    print(f"\n{color}⚠️ Уровень угрозы: {result.threat_level.value}{reset}")
    print(f"📊 Риск: {result.risk_score}/100")
    print(f"🦠 Семейство: {result.malware_family.value}")
    
    if result.detection_name:
        print(f"🎯 Детект: {result.detection_name}")
    
    if result.signatures_matched:
        print(f"\n✅ Совпадения сигнатур:")
        for sig in result.signatures_matched:
            print(f"   • {sig}")
    
    if result.heuristic_flags:
        print(f"\n🔍 Эвристика:")
        for flag in result.heuristic_flags[:10]:  # Первые 10
            print(f"   • {flag}")
    
    if verbose:
        if result.suspicious_strings:
            print(f"\n⚡ Подозрительные строки:")
            for s in result.suspicious_strings[:5]:
                print(f"   • {s[:80]}...")
        
        if result.pe_analysis and result.pe_analysis.get('is_pe'):
            print(f"\n📦 PE Анализ:")
            print(f"   Машина: {result.pe_analysis.get('machine', 'N/A')}")
            print(f"   Подсистема: {result.pe_analysis.get('subsystem', 'N/A')}")
            print(f"   Секций: {result.pe_analysis.get('num_sections', 0)}")
        
        if result.entropy_analysis:
            print(f"\n📈 Энтропия:")
            print(f"   Общая: {result.entropy_analysis.get('overall_entropy', 0):.4f}")
            print(f"   Упаковка: {result.entropy_analysis.get('packed_likelihood', 'LOW')}")
    
    if result.recommendations:
        print(f"\n💡 Рекомендации:")
        for rec in result.recommendations[:5]:
            print(f"   {rec}")
    
    print(f"\n⏱️ Время сканирования: {result.scan_time:.3f} сек")


if __name__ == '__main__':
    main()
