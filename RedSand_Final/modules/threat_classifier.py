#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Threat Classifier - Классификатор угроз
Определение типа вируса и подробное описание поведения
Поддержка 12+ типов угроз с привязкой к MITRE ATT&CK
"""

import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class ThreatType(Enum):
    RANSOMWARE = "Ransomware"
    STEALER = "Stealer"
    MINER = "Miner"
    RAT = "Remote Access Trojan"
    WORM = "Worm"
    BOTNET = "Botnet"
    ROOTKIT = "Rootkit"
    SPYWARE = "Spyware"
    ADWARE = "Adware"
    TROJAN = "Trojan"
    DROPPER = "Dropper"
    KEYLOGGER = "Keylogger"
    BACKDOOR = "Backdoor"
    UNKNOWN = "Unknown"

class ThreatClassifier:
    def __init__(self):
        # Сигнатуры для каждого типа угроз
        self.threat_signatures = {
            ThreatType.RANSOMWARE: {
                "keywords": ["encrypt", "decrypt", "ransom", "bitcoin", "wallet", ".encrypted", ".locked"],
                "behaviors": ["file_encryption", "mass_file_rename", "ransom_note_creation"],
                "registry": ["HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"],
                "mitre_techniques": ["T1486", "T1490", "T1489"]
            },
            ThreatType.STEALER: {
                "keywords": ["password", "cookie", "credential", "browser", "wallet", "autoit"],
                "behaviors": ["browser_data_access", "credential_extraction", "data_exfiltration"],
                "registry": ["HKCU\\Software\\Classes\\CLSID"],
                "mitre_techniques": ["T1555", "T1503", "T1539"]
            },
            ThreatType.MINER: {
                "keywords": ["miner", "pool", "hashrate", "coin", "bitcoin", "monero", "stratum"],
                "behaviors": ["high_cpu_usage", "gpu_mining", "pool_connection"],
                "registry": [],
                "mitre_techniques": ["T1496"]
            },
            ThreatType.RAT: {
                "keywords": ["remote", "access", "control", "webcam", "screenshot", "keylog"],
                "behaviors": ["remote_command_execution", "screen_capture", "keylogging", "webcam_access"],
                "registry": ["HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"],
                "mitre_techniques": ["T1219", "T1125", "T1113"]
            },
            ThreatType.WORM: {
                "keywords": ["worm", "spread", "replicate", "network", "share"],
                "behaviors": ["network_scanning", "self_replication", "usb_propagation"],
                "registry": ["HKLM\\SYSTEM\\CurrentControlSet\\Services"],
                "mitre_techniques": ["T1083", "T1091"]
            },
            ThreatType.BOTNET: {
                "keywords": ["bot", "ddos", "c2", "beacon", "zombie", "flood"],
                "behaviors": ["c2_communication", "ddos_capability", "bot_commands"],
                "registry": [],
                "mitre_techniques": ["T1071", "T1498", "T1095"]
            },
            ThreatType.ROOTKIT: {
                "keywords": ["rootkit", "hide", "hook", "kernel", "driver", "sys"],
                "behaviors": ["process_hiding", "file_hiding", "kernel_hooking"],
                "registry": ["HKLM\\SYSTEM\\CurrentControlSet\\Drivers"],
                "mitre_techniques": ["T1014", "T1562.006"]
            },
            ThreatType.SPYWARE: {
                "keywords": ["spy", "monitor", "track", "surveillance"],
                "behaviors": ["activity_monitoring", "data_collection", "stealth_mode"],
                "registry": [],
                "mitre_techniques": ["T1056", "T1123"]
            },
            ThreatType.ADWARE: {
                "keywords": ["ad", "popup", "banner", "redirect"],
                "behaviors": ["popup_creation", "browser_redirect", "ad_injection"],
                "registry": ["HKCU\\Software\\Microsoft\\Internet Explorer"],
                "mitre_techniques": ["T1564.003"]
            },
            ThreatType.TROJAN: {
                "keywords": ["trojan", "backdoor", "payload", "dropper"],
                "behaviors": ["payload_delivery", "system_modification", "persistence"],
                "registry": ["HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"],
                "mitre_techniques": ["T1059", "T1204"]
            },
            ThreatType.DROPPER: {
                "keywords": ["drop", "inject", "stage", "loader"],
                "behaviors": ["payload_extraction", "memory_injection", "secondary_download"],
                "registry": [],
                "mitre_techniques": ["T1204.002", "T1059"]
            },
            ThreatType.KEYLOGGER: {
                "keywords": ["keylog", "keystroke", "input", "keyboard"],
                "behaviors": ["keyboard_hooking", "input_capture", "keystroke_logging"],
                "registry": ["HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"],
                "mitre_techniques": ["T1056.001"]
            },
            ThreatType.BACKDOOR: {
                "keywords": ["backdoor", "shell", "reverse", "bind"],
                "behaviors": ["reverse_shell", "command_execution", "persistence"],
                "registry": ["HKLM\\SYSTEM\\CurrentControlSet\\Services"],
                "mitre_techniques": ["T1059", "T1571"]
            }
        }
        
        # Описания типов угроз
        self.threat_descriptions = {
            ThreatType.RANSOMWARE: "Шифрует файлы пользователя и требует выкуп за расшифровку. Критически опасен для данных.",
            ThreatType.STEALER: "Крадет конфиденциальные данные: пароли, cookies, криптокошельки. Высокий риск утечки.",
            ThreatType.MINER: "Использует ресурсы системы для майнинга криптовалюты. Замедляет работу компьютера.",
            ThreatType.RAT: "Предоставляет злоумышленнику полный удаленный доступ к системе. Крайне опасен.",
            ThreatType.WORM: "Самовоспроизводится и распространяется по сети. Может перегружать инфраструктуру.",
            ThreatType.BOTNET: "Включает устройство в сеть ботов для DDoS-атак и рассылки спама.",
            ThreatType.ROOTKIT: "Маскирует свое присутствие в системе на глубоком уровне. Сложно обнаруживается.",
            ThreatType.SPYWARE: "Тайно собирает информацию о действиях пользователя. Нарушает приватность.",
            ThreatType.ADWARE: "Показывает навязчивую рекламу, перенаправляет браузер. Раздражает, но не критичен.",
            ThreatType.TROJAN: "Маскируется под легитимное ПО для доставки вредоносной нагрузки. Опасен.",
            ThreatType.DROPPER: "Загружает и устанавливает другие вредоносные программы. Вторичная угроза.",
            ThreatType.KEYLOGGER: "Перехватывает нажатия клавиш для кражи паролей и другой информации.",
            ThreatType.BACKDOOR: "Создает скрытый вход в систему для обхода аутентификации. Высокий риск."
        }
    
    def classify(self, static_results: Dict, dynamic_results: Dict) -> Dict:
        """Классификация угрозы на основе статического и динамического анализа"""
        
        threat_scores = {}
        detected_threats = []
        
        # Анализ статических признаков
        static_keywords = self._extract_static_keywords(static_results)
        
        # Анализ динамического поведения
        dynamic_behaviors = self._extract_dynamic_behaviors(dynamic_results)
        
        # Оценка каждого типа угрозы
        for threat_type, signatures in self.threat_signatures.items():
            score = 0
            matched_indicators = []
            
            # Проверка ключевых слов
            keyword_matches = set(static_keywords) & set(signatures["keywords"])
            if keyword_matches:
                score += len(keyword_matches) * 15
                matched_indicators.extend([f"keyword:{k}" for k in keyword_matches])
            
            # Проверка поведения
            behavior_matches = set(dynamic_behaviors) & set(signatures["behaviors"])
            if behavior_matches:
                score += len(behavior_matches) * 25
                matched_indicators.extend([f"behavior:{b}" for b in behavior_matches])
            
            # Нормализация scores
            score = min(score, 100)
            
            if score > 30:  # Порог обнаружения
                threat_scores[threat_type.value] = {
                    "score": score,
                    "indicators": matched_indicators,
                    "description": self.threat_descriptions[threat_type],
                    "mitre_techniques": signatures["mitre_techniques"]
                }
                detected_threats.append((threat_type, score))
        
        # Определение основного типа угрозы
        if detected_threats:
            detected_threats.sort(key=lambda x: x[1], reverse=True)
            primary_threat = detected_threats[0]
            
            result = {
                "type": primary_threat[0].value,
                "risk_score": primary_threat[1],
                "all_detected": [t[0].value for t in detected_threats],
                "details": threat_scores[primary_threat[0].value],
                "confidence": self._calculate_confidence(detected_threats),
                "recommendation": self._get_recommendation(primary_threat[0])
            }
        else:
            result = {
                "type": ThreatType.UNKNOWN.value,
                "risk_score": 0,
                "all_detected": [],
                "details": {},
                "confidence": "low",
                "recommendation": "Угрозы не обнаружены. Рекомендуется дополнительный анализ."
            }
        
        return result
    
    def _extract_static_keywords(self, static_results: Dict) -> List[str]:
        """Извлечение ключевых слов из статического анализа"""
        keywords = []
        
        # Из строк файла
        strings = static_results.get("strings", [])
        for s in strings:
            keywords.extend([kw for kw in self._get_all_keywords() if kw.lower() in s.lower()])
        
        # Из PE информации
        pe_info = static_results.get("pe_info", {})
        if pe_info:
            keywords.extend([kw for kw in self._get_all_keywords() 
                           if kw.lower() in str(pe_info).lower()])
        
        return list(set(keywords))
    
    def _extract_dynamic_behaviors(self, dynamic_results: Dict) -> List[str]:
        """Извлечение поведенческих признаков из динамического анализа"""
        behaviors = []
        
        # Из операций с файлами
        file_ops = dynamic_results.get("file_operations", [])
        if any("encrypt" in str(op).lower() for op in file_ops):
            behaviors.append("file_encryption")
        
        # Из сетевых операций
        net_ops = dynamic_results.get("network_operations", [])
        if net_ops:
            behaviors.append("c2_communication")
        
        # Из флагов поведения
        flags = dynamic_results.get("behavior_flags", [])
        behaviors.extend(flags)
        
        return list(set(behaviors))
    
    def _get_all_keywords(self) -> List[str]:
        """Получение всех ключевых слов для классификации"""
        all_keywords = []
        for signatures in self.threat_signatures.values():
            all_keywords.extend(signatures["keywords"])
        return list(set(all_keywords))
    
    def _calculate_confidence(self, detected_threats: List) -> str:
        """Расчет уверенности классификации"""
        if not detected_threats:
            return "none"
        
        top_score = detected_threats[0][1]
        
        if top_score >= 80:
            return "high"
        elif top_score >= 50:
            return "medium"
        else:
            return "low"
    
    def _get_recommendation(self, threat_type: ThreatType) -> str:
        """Получение рекомендаций по обработке угрозы"""
        recommendations = {
            ThreatType.RANSOMWARE: "НЕМЕДЛЕННО изолировать систему! Не платить выкуп. Восстановить файлы из бэкапа.",
            ThreatType.STEALER: "Сменить все пароли на другом устройстве. Проверить банковские счета.",
            ThreatType.MINER: "Удалить вредоносное ПО. Проверить автозагрузку. Мониторить нагрузку на CPU/GPU.",
            ThreatType.RAT: "Отключить от сети! Полная переустановка системы. Сменить все учетные данные.",
            ThreatType.WORM: "Изолировать зараженные системы. Обновить антивирусные базы. Проверить сеть.",
            ThreatType.BOTNET: "Блокировать C&C серверы. Переустановить систему. Уведомить провайдера.",
            ThreatType.ROOTKIT: "Требуется специализированное удаление. Рассмотреть переустановку ОС.",
            ThreatType.SPYWARE: "Удалить вредоносное ПО. Проверить настройки приватности.",
            ThreatType.ADWARE: "Удалить через Панель управления. Очистить браузеры.",
            ThreatType.TROJAN: "Удалить файл. Проверить систему на наличие других угроз.",
            ThreatType.DROPPER: "Найти и удалить полезную нагрузку. Проверить сетевые подключения.",
            ThreatType.KEYLOGGER: "Сменить пароли на другом устройстве. Проверить автозагрузку.",
            ThreatType.BACKDOOR: "Немедленно отключить от сети! Полная переустановка системы."
        }
        
        return recommendations.get(threat_type, "Провести дополнительный анализ.")
    
    def get_mitre_mapping(self, threat_type: str) -> List[str]:
        """Получение техник MITRE ATT&CK для типа угрозы"""
        for tt, signatures in self.threat_signatures.items():
            if tt.value == threat_type:
                return signatures["mitre_techniques"]
        return []
