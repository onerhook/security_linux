#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Threat Classifier - Классификатор угроз
Определение типа вредоносного ПО по поведению и статическим признакам
Поддержка 12 типов угроз с привязкой к MITRE ATT&CK
"""

class ThreatClassifier:
    def __init__(self):
        self.threat_types = {
            'RANSOMWARE': {
                'keywords': ['encrypt', 'decrypt', 'bitcoin', 'ransom', '.locked', '.crypto'],
                'behaviors': ['file_modification', 'mass_file_rename', 'registry_persistence'],
                'mitre_tactics': ['TA0040 - Impact', 'T1486 - Data Encrypted for Impact'],
                'risk_base': 95
            },
            'STEALER': {
                'keywords': ['password', 'cookie', 'credential', 'wallet', 'browser'],
                'behaviors': ['file_access', 'browser_data_access', 'network_exfiltration'],
                'mitre_tactics': ['TA0009 - Collection', 'T1555 - Credentials from Password Stores'],
                'risk_base': 90
            },
            'MINER': {
                'keywords': ['pool', 'mining', 'cryptonight', 'stratum', 'hashrate'],
                'behaviors': ['high_cpu_usage', 'network_connection', 'process_injection'],
                'mitre_tactics': ['TA0004 - Privilege Escalation', 'T1496 - Resource Hijacking'],
                'risk_base': 75
            },
            'RAT': {
                'keywords': ['remote', 'desktop', 'control', 'backdoor', 'c2'],
                'behaviors': ['network_listening', 'process_creation', 'keylogging'],
                'mitre_tactics': ['TA0011 - Command and Control', 'T1059 - Command and Scripting Interpreter'],
                'risk_base': 92
            },
            'WORM': {
                'keywords': ['spread', 'replicate', 'usb', 'network_share'],
                'behaviors': ['network_scan', 'file_copy', 'autorun_creation'],
                'mitre_tactics': ['TA0008 - Lateral Movement', 'T1091 - Spread via Removable Media'],
                'risk_base': 80
            },
            'BOTNET': {
                'keywords': ['bot', 'ddos', 'flood', 'zombie', 'irc'],
                'behaviors': ['network_connection', 'process_persistence', 'command_execution'],
                'mitre_tactics': ['TA0011 - Command and Control', 'T1071 - Application Layer Protocol'],
                'risk_base': 88
            },
            'ROOTKIT': {
                'keywords': ['kernel', 'driver', 'hide', 'hook', 'ssdt'],
                'behaviors': ['driver_load', 'process_hiding', 'file_hiding'],
                'mitre_tactics': ['TA0005 - Defense Evasion', 'T1014 - Rootkit'],
                'risk_base': 98
            },
            'SPYWARE': {
                'keywords': ['spy', 'monitor', 'screenshot', 'clipboard', 'webcam'],
                'behaviors': ['screen_capture', 'clipboard_monitor', 'keylogging'],
                'mitre_tactics': ['TA0009 - Collection', 'T1113 - Screen Capture'],
                'risk_base': 85
            },
            'ADWARE': {
                'keywords': ['ad', 'popup', 'banner', 'redirect', 'promotion'],
                'behaviors': ['browser_modification', 'popup_creation', 'registry_modification'],
                'mitre_tactics': ['TA0002 - Execution', 'T1547 - Boot or Logon Autostart Execution'],
                'risk_base': 45
            },
            'TROJAN': {
                'keywords': ['trojan', 'payload', 'dropper', 'downloader'],
                'behaviors': ['file_download', 'process_injection', 'persistence'],
                'mitre_tactics': ['TA0002 - Execution', 'T1204 - User Execution'],
                'risk_base': 82
            },
            'DROPPER': {
                'keywords': ['drop', 'install', 'stage', 'payload'],
                'behaviors': ['file_download', 'file_write', 'process_execution'],
                'mitre_tactics': ['TA0002 - Execution', 'T1105 - Ingress Tool Transfer'],
                'risk_base': 78
            },
            'KEYLOGGER': {
                'keywords': ['keylog', 'keystroke', 'input', 'keyboard', 'hook'],
                'behaviors': ['keyboard_hook', 'input_capture', 'file_write'],
                'mitre_tactics': ['TA0009 - Collection', 'T1056.001 - Input Capture: Keylogging'],
                'risk_base': 87
            }
        }

    def classify_static(self, static_results):
        """Классификация на основе статического анализа"""
        scores = {}

        strings_found = static_results.get('strings', [])
        pe_info = static_results.get('pe_info', {})

        all_text = ' '.join(strings_found).lower()
        if pe_info:
            all_text += ' ' + str(pe_info).lower()

        for threat_type, config in self.threat_types.items():
            score = 0

            # Поиск ключевых слов
            for keyword in config['keywords']:
                if keyword.lower() in all_text:
                    score += 15

            scores[threat_type] = min(score, 100)

        # Возвращаем тип с максимальным скором
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'UNKNOWN'

    def classify(self, static_results, dynamic_events):
        """Полная классификация угрозы"""
        threat_scores = {}

        # Статический анализ
        static_type = self.classify_static(static_results)

        # Динамический анализ
        behaviors_detected = self._analyze_behaviors(dynamic_events)

        # Получаем уровень угрозы из статического анализатора
        static_threat_level = static_results.get('threat_level', 'CLEAN')

        for threat_type, config in self.threat_types.items():
            score = 0  # Начинаем с 0 для чистых файлов

            # Если статический анализ показал CLEAN - даем минимальный скор
            if static_threat_level == 'CLEAN':
                score = config['risk_base'] * 0.1  # 10% от базового риска
            elif static_threat_level == 'SUSPICIOUS':
                score = config['risk_base'] * 0.3  # 30% от базового риска
            else:  # MALICIOUS
                score = config['risk_base'] * 0.5  # 50% от базового риска

            # Статические совпадения (только если найдены реальные индикаторы)
            if static_type == threat_type and static_threat_level != 'CLEAN':
                score += 20

            # Поведенческие совпадения
            for behavior in behaviors_detected:
                if behavior in config['behaviors']:
                    score += 15

            # Ключевые слова в событиях (только специфичные)
            events_text = str(dynamic_events).lower()
            for keyword in config['keywords'][:3]:  # Только первые 3 ключевых слова
                if keyword.lower() in events_text:
                    score += 5

            threat_scores[threat_type] = min(int(score), 100)

        # Определяем основной тип
        primary_threat = max(threat_scores, key=threat_scores.get)
        risk_score = threat_scores[primary_threat]

        # Если все скоры низкие (< 20), считаем файл чистым
        if max(threat_scores.values()) < 20:
            primary_threat = 'CLEAN'
            risk_score = min(threat_scores.values())

        # Формируем результат
        result = {
            'type': primary_threat,
            'family': self._determine_family(primary_threat, static_results),
            'risk_score': risk_score,
            'confidence': 'HIGH' if risk_score > 70 else 'MEDIUM' if risk_score > 40 else 'LOW',
            'mitre_tactics': self.threat_types.get(primary_threat, {}).get('mitre_tactics', ['Unknown']),
            'all_scores': threat_scores,
            'behaviors_detected': behaviors_detected
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
