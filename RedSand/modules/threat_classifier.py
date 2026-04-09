#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Threat Classifier - Классификатор угроз v6.0
Определение типа вредоносного ПО по поведению и статическим признакам
Поддержка 12 типов угроз с привязкой к MITRE ATT&CK
Улучшенная версия с защитой от ложных срабатываний
"""

import os
import hashlib
import re

class ThreatClassifier:
    # Белый список легитимных издателей и хешей
    TRUSTED_PUBLISHERS = [
        'Microsoft Corporation', 'Python Software Foundation', 
        'Google LLC', 'Apple Inc.', 'Adobe Inc.',
        'Oracle Corporation', 'IBM Corporation'
    ]
    
    # Хэши известных легитимных файлов (пример)
    TRUSTED_HASHES = set()
    
    def __init__(self):
        self.threat_types = {
            'RANSOMWARE': {
                'keywords': ['encrypt', 'decrypt', 'bitcoin', 'ransom', '.locked', '.crypto', 'your files'],
                'behaviors': ['file_modification', 'mass_file_rename', 'registry_persistence'],
                'mitre_tactics': ['TA0040 - Impact', 'T1486 - Data Encrypted for Impact'],
                'risk_base': 95,
                'critical_indicators': ['ransom note', 'bitcoin address', 'encryption routine']
            },
            'STEALER': {
                'keywords': ['password', 'cookie', 'credential', 'wallet', 'browser', 'steal'],
                'behaviors': ['file_access', 'browser_data_access', 'network_exfiltration'],
                'mitre_tactics': ['TA0009 - Collection', 'T1555 - Credentials from Password Stores'],
                'risk_base': 90,
                'critical_indicators': ['browser password', 'wallet dat', 'credential manager']
            },
            'MINER': {
                'keywords': ['pool', 'mining', 'cryptonight', 'stratum', 'hashrate', 'xmrig'],
                'behaviors': ['high_cpu_usage', 'network_connection', 'process_injection'],
                'mitre_tactics': ['TA0004 - Privilege Escalation', 'T1496 - Resource Hijacking'],
                'risk_base': 75,
                'critical_indicators': ['stratum+tcp', 'mining pool', 'donate level']
            },
            'RAT': {
                'keywords': ['remote', 'desktop', 'control', 'backdoor', 'c2', 'command server'],
                'behaviors': ['network_listening', 'process_creation', 'keylogging'],
                'mitre_tactics': ['TA0011 - Command and Control', 'T1059 - Command and Scripting Interpreter'],
                'risk_base': 92,
                'critical_indicators': ['reverse shell', 'c2 beacon', 'remote desktop']
            },
            'WORM': {
                'keywords': ['spread', 'replicate', 'usb', 'network_share', 'autorun'],
                'behaviors': ['network_scan', 'file_copy', 'autorun_creation'],
                'mitre_tactics': ['TA0008 - Lateral Movement', 'T1091 - Spread via Removable Media'],
                'risk_base': 80,
                'critical_indicators': ['copy to removable', 'network propagation']
            },
            'BOTNET': {
                'keywords': ['bot', 'ddos', 'flood', 'zombie', 'irc', 'botnet'],
                'behaviors': ['network_connection', 'process_persistence', 'command_execution'],
                'mitre_tactics': ['TA0011 - Command and Control', 'T1071 - Application Layer Protocol'],
                'risk_base': 88,
                'critical_indicators': ['ddos command', 'irc bot', 'flood attack']
            },
            'ROOTKIT': {
                'keywords': ['kernel', 'driver', 'hide', 'hook', 'ssdt', 'rootkit'],
                'behaviors': ['driver_load', 'process_hiding', 'file_hiding'],
                'mitre_tactics': ['TA0005 - Defense Evasion', 'T1014 - Rootkit'],
                'risk_base': 98,
                'critical_indicators': ['ssdt hook', 'idt modification', 'kernel module']
            },
            'SPYWARE': {
                'keywords': ['spy', 'monitor', 'screenshot', 'clipboard', 'webcam', 'surveillance'],
                'behaviors': ['screen_capture', 'clipboard_monitor', 'keylogging'],
                'mitre_tactics': ['TA0009 - Collection', 'T1113 - Screen Capture'],
                'risk_base': 85,
                'critical_indicators': ['webcam capture', 'clipboard log', 'screen record']
            },
            'ADWARE': {
                'keywords': ['ad', 'popup', 'banner', 'redirect', 'promotion', 'advertisement'],
                'behaviors': ['browser_modification', 'popup_creation', 'registry_modification'],
                'mitre_tactics': ['TA0002 - Execution', 'T1547 - Boot or Logon Autostart Execution'],
                'risk_base': 45,
                'critical_indicators': ['popup ad', 'browser hijack']
            },
            'TROJAN': {
                'keywords': ['trojan', 'payload', 'dropper', 'downloader', 'backdoor'],
                'behaviors': ['file_download', 'process_injection', 'persistence'],
                'mitre_tactics': ['TA0002 - Execution', 'T1204 - User Execution'],
                'risk_base': 82,
                'critical_indicators': ['payload delivery', 'second stage']
            },
            'DROPPER': {
                'keywords': ['drop', 'install', 'stage', 'payload', 'unpack'],
                'behaviors': ['file_download', 'file_write', 'process_execution'],
                'mitre_tactics': ['TA0002 - Execution', 'T1105 - Ingress Tool Transfer'],
                'risk_base': 78,
                'critical_indicators': ['extract payload', 'drop file']
            },
            'KEYLOGGER': {
                'keywords': ['keylog', 'keystroke', 'input', 'keyboard', 'hook', 'keylogger'],
                'behaviors': ['keyboard_hook', 'input_capture', 'file_write'],
                'mitre_tactics': ['TA0009 - Collection', 'T1056.001 - Input Capture: Keylogging'],
                'risk_base': 87,
                'critical_indicators': ['getasynckeystate', 'keyboard hook', 'key log']
            }
        }
        
        # Индикаторы чистых файлов
        self.clean_indicators = [
            'copyright', 'all rights reserved', 'licensed under',
            'python software foundation', 'microsoft corporation',
            'gnu general public license', 'mit license', 'apache license',
            'version', 'author', 'description', 'official'
        ]
        
        # Критические пороги для обнаружения
        self.MIN_THREAT_SCORE = 60  # Минимальный скор для определения угрозы
        self.MIN_KEYWORD_MATCHES = 3  # Минимум совпадений ключевых слов
        self.MIN_CRITICAL_INDICATORS = 1  # Минимум критических индикаторов
        
    def classify_static(self, static_results):
        """Классификация на основе статического анализа с защитой от ложных срабатываний"""
        scores = {}
        keyword_matches = {}
        
        strings_found = static_results.get('strings', [])
        pe_info = static_results.get('pe_info', {})
        file_info = static_results.get('file_info', {})
        hashes = static_results.get('hashes', {})
        
        all_text = ' '.join(strings_found).lower()
        if pe_info:
            all_text += ' ' + str(pe_info).lower()
        
        # Проверка на доверенные хэши
        file_hash = hashes.get('sha256', '')
        if file_hash and file_hash in self.TRUSTED_HASHES:
            return 'CLEAN'
        
        # Проверка на индикаторы чистого ПО
        clean_score = 0
        for indicator in self.clean_indicators:
            if indicator.lower() in all_text:
                clean_score += 1
        
        # Если много индикаторов чистого ПО - снижаем оценку угроз
        is_likely_clean = clean_score >= 3
        
        for threat_type, config in self.threat_types.items():
            score = 0
            matches = 0
            critical_matches = 0
            
            # Поиск ключевых слов
            for keyword in config['keywords']:
                if keyword.lower() in all_text:
                    score += 15
                    matches += 1
            
            # Поиск критических индикаторов
            for indicator in config.get('critical_indicators', []):
                if indicator.lower() in all_text:
                    score += 25
                    critical_matches += 1
            
            # Применяем пороговые значения
            if matches < self.MIN_KEYWORD_MATCHES and critical_matches < self.MIN_CRITICAL_INDICATORS:
                score = 0  # Недостаточно совпадений
            
            # Снижаем оценку если файл похож на чистый
            if is_likely_clean:
                score = int(score * 0.3)
            
            scores[threat_type] = min(score, 100)
            keyword_matches[threat_type] = matches
        
        # Проверяем минимальный порог
        max_score = max(scores.values()) if scores else 0
        if max_score < self.MIN_THREAT_SCORE:
            return 'CLEAN'
        
        # Возвращаем тип с максимальным скором
        if max_score > 0:
            best_threat = max(scores, key=scores.get)
            if scores[best_threat] >= self.MIN_THREAT_SCORE:
                return best_threat
        
        return 'CLEAN'
    
    def classify(self, static_results, dynamic_events):
        """Полная классификация угрозы с улучшенной логикой"""
        threat_scores = {}
        keyword_match_counts = {}
        
        # Статический анализ
        static_type = self.classify_static(static_results)
        
        # Если файл чистый по статическому анализу
        if static_type == 'CLEAN':
            # Проверяем динамическое поведение
            behaviors_detected = self._analyze_behaviors(dynamic_events)
            if not behaviors_detected or len(behaviors_detected) < 2:
                # Нет подозрительного поведения - файл чист
                return {
                    'type': 'CLEAN',
                    'family': 'None',
                    'risk_score': 0,
                    'confidence': 'HIGH',
                    'mitre_tactics': [],
                    'all_scores': {},
                    'behaviors_detected': [],
                    'is_clean': True,
                    'analysis_notes': 'File passed static and dynamic analysis checks'
                }
        
        # Динамический анализ
        behaviors_detected = self._analyze_behaviors(dynamic_events)
        
        for threat_type, config in self.threat_types.items():
            score = 0
            keyword_matches = 0
            
            # Базовый риск только если есть совпадения
            if static_type == threat_type:
                score += config['risk_base'] * 0.4
            
            # Поведенческие совпадения (более весомые)
            behavior_matches = 0
            for behavior in behaviors_detected:
                if behavior in config['behaviors']:
                    score += 25
                    behavior_matches += 1
            
            # Ключевые слова в событиях
            events_text = str(dynamic_events).lower()
            for keyword in config['keywords']:
                if keyword.lower() in events_text:
                    score += 15
                    keyword_matches += 1
            
            # Критические индикаторы
            for indicator in config.get('critical_indicators', []):
                if indicator.lower() in events_text:
                    score += 30
            
            # Требуем минимум поведенческих или keyword совпадений
            if behavior_matches < 1 and keyword_matches < 2:
                score = int(score * 0.2)  # Сильно снижаем оценку
            
            threat_scores[threat_type] = min(int(score), 100)
            keyword_match_counts[threat_type] = keyword_matches
        
        # Определяем основной тип
        primary_threat = max(threat_scores, key=threat_scores.get)
        risk_score = threat_scores[primary_threat]
        
        # Финальная проверка порога
        if risk_score < self.MIN_THREAT_SCORE:
            return {
                'type': 'CLEAN',
                'family': 'None',
                'risk_score': 0,
                'confidence': 'HIGH',
                'mitre_tactics': [],
                'all_scores': threat_scores,
                'behaviors_detected': behaviors_detected,
                'is_clean': True,
                'analysis_notes': 'Risk score below threshold'
            }
        
        # Формируем результат
        result = {
            'type': primary_threat,
            'family': self._determine_family(primary_threat, static_results),
            'risk_score': risk_score,
            'confidence': 'HIGH' if risk_score > 70 else 'MEDIUM' if risk_score > 40 else 'LOW',
            'mitre_tactics': self.threat_types[primary_threat]['mitre_tactics'],
            'all_scores': threat_scores,
            'behaviors_detected': behaviors_detected,
            'is_clean': False,
            'keyword_matches': keyword_match_counts.get(primary_threat, 0),
            'analysis_notes': f'Detected {len(behaviors_detected)} suspicious behaviors'
        }
        
        return result
    
    def _analyze_behaviors(self, events):
        """Анализ поведения по событиям"""
        behaviors = []
        events_str = str(events).lower()
        
        if 'file' in events_str and ('encrypt' in events_str or 'rename' in events_str):
            behaviors.append('file_modification')
        if 'registry' in events_str:
            behaviors.append('registry_modification')
        if 'network' in events_str or 'connect' in events_str:
            behaviors.append('network_connection')
        if 'process' in events_str and ('create' in events_str or 'spawn' in events_str):
            behaviors.append('process_creation')
        if 'cpu' in events_str or 'high usage' in events_str:
            behaviors.append('high_cpu_usage')
        if 'password' in events_str or 'credential' in events_str:
            behaviors.append('credential_access')
            
        return behaviors
    
    def _determine_family(self, threat_type, static_results):
        """Определение семейства вируса"""
        # Упрощенная логика определения семейства
        strings_found = ' '.join(static_results.get('strings', [])).lower()
        
        families = {
            'RANSOMWARE': ['WannaCry', 'Petya', 'LockBit', 'Ryuk'],
            'STEALER': ['Azorult', 'RedLine', 'Raccoon', 'Vidar'],
            'MINER': ['XMRig', 'Minergate', 'Coinhive'],
            'RAT': ['AsyncRAT', 'QuasarRAT', 'RemcosRAT'],
            'WORM': ['Conficker', 'Sasser', 'Blaster'],
            'BOTNET': ['Mirai', 'Emotet', 'TrickBot'],
            'ROOTKIT': ['TDL4', 'Alureon', 'Rustock'],
            'SPYWARE': ['DarkComet', 'BlackShades', 'njRAT'],
            'ADWARE': ['Fireball', 'Roaming Mantis'],
            'TROJAN': ['Zeus', 'SpyEye', 'Carberp'],
            'DROPPER': ['Geodo', 'Dridex'],
            'KEYLOGGER': ['Ardamax', 'Reflexion', 'KidLogger']
        }
        
        type_families = families.get(threat_type, ['Unknown'])
        
        # Простой эвристический выбор
        for family in type_families:
            if family.lower() in strings_found:
                return family
        
        return type_families[0] if type_families else 'Unknown'
