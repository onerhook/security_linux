#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ML Threat Classifier - Машинное обучение для классификации угроз
Использует ансамбль моделей для точного определения типа вредоносного ПО
Поддержка онлайн-обучения и адаптации к новым угрозам
"""

import os
import json
import hashlib
import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import re

# Попытка импорта sklearn, если недоступен - используем упрощённую версию
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class MLDetectionResult:
    """Результат ML детектирования."""
    threat_type: str
    confidence: float  # 0.0 - 1.0
    probability_distribution: Dict[str, float]
    model_version: str
    features_used: List[str]
    is_ensemble: bool
    individual_predictions: List[Dict[str, Any]]


class MLThreatClassifier:
    """
    Классификатор угроз на основе машинного обучения.
    Использует ансамбль моделей для повышения точности.
    """
    
    MODEL_VERSION = "1.0.0"
    SUPPORTED_THREATS = [
        'RANSOMWARE', 'STEALER', 'MINER', 'RAT', 'WORM',
        'BOTNET', 'ROOTKIT', 'SPYWARE', 'ADWARE', 'TROJAN',
        'DROPPER', 'KEYLOGGER', 'MEMORY_INJECTOR', 'CLEAN'
    ]
    
    def __init__(self, model_path: Optional[str] = None, use_ensemble: bool = True):
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), 'ml_models'
        )
        self.use_ensemble = use_ensemble
        self.models = {}
        self.scaler = None
        self.label_encoder = None
        self.vectorizer = None
        self.is_trained = False
        
        # Веса для ансамбля моделей
        self.model_weights = {
            'random_forest': 0.35,
            'gradient_boost': 0.35,
            'neural_network': 0.30
        }
        
        # Кэш предсказаний
        self.prediction_cache = {}
        self.cache_max_size = 1000
        
        Path(self.model_path).mkdir(parents=True, exist_ok=True)
        
        if SKLEARN_AVAILABLE:
            self._load_or_initialize_models()
        else:
            print("[!] Scikit-learn не установлен. Используем упрощённый классификатор.")
    
    def _load_or_initialize_models(self):
        """Загрузка обученных моделей или инициализация новых."""
        if not SKLEARN_AVAILABLE:
            return
            
        model_file = os.path.join(self.model_path, 'threat_classifier.pkl')
        
        if os.path.exists(model_file):
            try:
                with open(model_file, 'rb') as f:
                    saved_data = pickle.load(f)
                    self.models = saved_data.get('models', {})
                    self.scaler = saved_data.get('scaler')
                    self.label_encoder = saved_data.get('label_encoder')
                    self.vectorizer = saved_data.get('vectorizer')
                    self.is_trained = saved_data.get('is_trained', False)
                print(f"[+] ML модели загружены из {model_file}")
            except Exception as e:
                print(f"[-] Ошибка загрузки ML моделей: {e}. Инициализация новых...")
                self._initialize_models()
        else:
            self._initialize_models()
    
    def _initialize_models(self):
        """Инициализация новых моделей."""
        if not SKLEARN_AVAILABLE:
            return
            
        # Random Forest - хорошая точность и скорость
        self.models['random_forest'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        
        # Gradient Boosting - высокая точность
        self.models['gradient_boost'] = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        # Neural Network - сложные паттерны
        self.models['neural_network'] = MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),
            activation='relu',
            solver='adam',
            alpha=0.001,
            max_iter=500,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1
        )
        
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.95
        )
        
        self.label_encoder.fit(self.SUPPORTED_THREATS)
        print("[+] ML модели инициализированы")
    
    def extract_features(self, file_content: str, file_path: str, 
                        static_results: Dict) -> Tuple[List[float], List[str]]:
        """
        Извлечение признаков из файла для ML модели.
        Возвращает вектор признаков и список названий признаков.
        """
        features = []
        feature_names = []
        
        # 1. Статистические признаки файла
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        features.append(file_size / (10 * 1024 * 1024))  # Нормализация по 10MB
        feature_names.append('file_size_normalized')
        
        # 2. Количество строк кода
        lines = file_content.split('\n')
        features.append(len(lines) / 1000)  # Нормализация
        feature_names.append('line_count_normalized')
        
        # 3. Средняя длина строки
        avg_line_length = sum(len(line) for line in lines) / max(len(lines), 1)
        features.append(avg_line_length / 200)  # Нормализация
        feature_names.append('avg_line_length_normalized')
        
        # 4. Плотность подозрительных ключевых слов
        suspicious_keywords = [
            'encrypt', 'decrypt', 'bitcoin', 'password', 'credential',
            'inject', 'hook', 'remote', 'backdoor', 'shell', 'payload',
            'download', 'execute', 'hide', 'stealth', 'kernel', 'driver'
        ]
        content_lower = file_content.lower()
        keyword_density = sum(
            content_lower.count(kw) for kw in suspicious_keywords
        ) / max(len(content_lower), 1) * 1000
        features.append(keyword_density)
        feature_names.append('suspicious_keyword_density')
        
        # 5. Количество API вызовов
        api_pattern = r'[A-Z][a-z]+[A-Z][a-zA-Z]+'
        api_calls = re.findall(api_pattern, file_content)
        features.append(len(api_calls) / 100)  # Нормализация
        feature_names.append('api_call_count_normalized')
        
        # 6. Уникальные API вызовы
        unique_apis = set(api_calls)
        features.append(len(unique_apis) / 50)  # Нормализация
        feature_names.append('unique_api_count_normalized')
        
        # 7. Наличие сетевых индикаторов
        network_indicators = [
            'http://', 'https://', 'ftp://', 'socket', 'connect',
            'listen', 'bind', 'send', 'recv', 'pool.', 'stratum'
        ]
        network_count = sum(content_lower.count(ind) for ind in network_indicators)
        features.append(network_count / 20)  # Нормализация
        feature_names.append('network_indicator_count_normalized')
        
        # 8. Признаки шифрования
        crypto_patterns = [
            r'CryptEncrypt', r'CryptDecrypt', r'AES', r'RSA',
            r'\.encrypted', r'\.locked', r'\.crypto'
        ]
        crypto_count = sum(
            len(re.findall(pattern, file_content, re.IGNORECASE))
            for pattern in crypto_patterns
        )
        features.append(crypto_count / 10)  # Нормализация
        feature_names.append('crypto_pattern_count_normalized')
        
        # 9. Признаки работы с реестром (Windows)
        registry_patterns = [
            r'RegSetValue', r'RegCreateKey', r'RegDeleteKey',
            r'CurrentVersion\\\\Run', r'SOFTWARE\\\\Microsoft'
        ]
        registry_count = sum(
            len(re.findall(pattern, file_content, re.IGNORECASE))
            for pattern in registry_patterns
        )
        features.append(registry_count / 5)  # Нормализация
        feature_names.append('registry_operation_count_normalized')
        
        # 10. Признаки инъекции кода
        injection_patterns = [
            r'VirtualAllocEx', r'WriteProcessMemory', r'CreateRemoteThread',
            r'NtUnmapViewOfSection', r'process hollow', r'code inject'
        ]
        injection_count = sum(
            len(re.findall(pattern, file_content, re.IGNORECASE))
            for pattern in injection_patterns
        )
        features.append(injection_count / 5)  # Нормализация
        feature_names.append('injection_pattern_count_normalized')
        
        # 11. Risk score от статического анализатора
        risk_score = static_results.get('risk_score', 0) / 100.0
        features.append(risk_score)
        feature_names.append('static_risk_score_normalized')
        
        # 12. Количество обнаруженных сигнатур
        sig_count = len(static_results.get('matched_signatures', []))
        features.append(sig_count / 20)  # Нормализация
        feature_names.append('signature_count_normalized')
        
        # 13. TF-IDF векторизация текста (для текстовых признаков)
        tfidf_features = self._extract_tfidf_features(file_content)
        features.extend(tfidf_features)
        feature_names.extend([f'tfidf_{i}' for i in range(len(tfidf_features))])
        
        return features, feature_names
    
    def _extract_tfidf_features(self, text: str) -> List[float]:
        """Извлечение TF-IDF признаков из текста."""
        if not SKLEARN_AVAILABLE or self.vectorizer is None:
            return [0.0] * 50  # Заглушка
        
        try:
            # Если векторизатор ещё не обучен, возвращаем нули
            if not hasattr(self.vectorizer, 'vocabulary_'):
                return [0.0] * 50
            
            tfidf_matrix = self.vectorizer.transform([text])
            features = tfidf_matrix.toarray()[0]
            
            # Берём первые 50 признаков для единообразия
            if len(features) > 50:
                features = features[:50]
            elif len(features) < 50:
                features = list(features) + [0.0] * (50 - len(features))
            
            return list(features)
        except Exception:
            return [0.0] * 50
    
    def predict(self, file_content: str, file_path: str, 
               static_results: Dict) -> MLDetectionResult:
        """
        Предсказание типа угрозы с использованием ансамбля моделей.
        """
        # Проверка кэша
        cache_key = hashlib.md5(
            f"{file_path}{static_results.get('file_hash', '')}".encode()
        ).hexdigest()
        
        if cache_key in self.prediction_cache and len(self.prediction_cache) < self.cache_max_size:
            return self.prediction_cache[cache_key]
        
        if not SKLEARN_AVAILABLE or not self.is_trained:
            # Fallback на эвристический классификатор
            return self._heuristic_fallback(static_results)
        
        try:
            # Извлечение признаков
            features, feature_names = self.extract_features(
                file_content, file_path, static_results
            )
            
            # Масштабирование признаков
            if self.scaler is not None:
                features_scaled = self.scaler.transform([features])[0]
            else:
                features_scaled = features
            
            # Предсказания от каждой модели
            individual_predictions = []
            weighted_votes = defaultdict(float)
            
            for model_name, model in self.models.items():
                if model is None:
                    continue
                    
                try:
                    prediction = model.predict([features_scaled])[0]
                    probabilities = model.predict_proba([features_scaled])[0]
                    
                    pred_threat = self.label_encoder.inverse_transform([prediction])[0]
                    
                    # Взвешенное голосование
                    for idx, prob in enumerate(probabilities):
                        threat_class = self.label_encoder.inverse_transform([idx])[0]
                        weighted_votes[threat_class] += prob * self.model_weights.get(model_name, 0.33)
                    
                    individual_predictions.append({
                        'model': model_name,
                        'prediction': pred_threat,
                        'confidence': float(max(probabilities)),
                        'probabilities': {
                            self.label_encoder.inverse_transform([i])[0]: float(p)
                            for i, p in enumerate(probabilities)
                        }
                    })
                except Exception as e:
                    print(f"[-] Ошибка предсказания моделью {model_name}: {e}")
                    continue
            
            # Определение итогового класса
            if weighted_votes:
                final_threat = max(weighted_votes, key=weighted_votes.get)
                final_confidence = weighted_votes[final_threat]
                
                # Нормализация вероятностей
                total = sum(weighted_votes.values())
                probability_distribution = {
                    k: v / total if total > 0 else 0
                    for k, v in weighted_votes.items()
                }
            else:
                return self._heuristic_fallback(static_results)
            
            result = MLDetectionResult(
                threat_type=final_threat,
                confidence=float(final_confidence),
                probability_distribution=probability_distribution,
                model_version=self.MODEL_VERSION,
                features_used=feature_names[:20],  # Первые 20 признаков
                is_ensemble=self.use_ensemble,
                individual_predictions=individual_predictions
            )
            
            # Сохранение в кэш
            if len(self.prediction_cache) < self.cache_max_size:
                self.prediction_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            print(f"[-] Ошибка ML предсказания: {e}")
            return self._heuristic_fallback(static_results)
    
    def _heuristic_fallback(self, static_results: Dict) -> MLDetectionResult:
        """Резервный эвристический классификатор."""
        threat_level = static_results.get('threat_level', 'CLEAN')
        
        if threat_level == 'CLEAN':
            threat_type = 'CLEAN'
            confidence = 0.8
        elif threat_level == 'SUSPICIOUS':
            threat_type = 'TROJAN'  # По умолчанию
            confidence = 0.5
        else:
            threat_type = static_results.get('preliminary_threat_type', 'MALWARE')
            confidence = 0.7
        
        return MLDetectionResult(
            threat_type=threat_type,
            confidence=confidence,
            probability_distribution={threat_type: confidence},
            model_version="heuristic_fallback",
            features_used=[],
            is_ensemble=False,
            individual_predictions=[]
        )
    
    def train(self, training_data: List[Dict[str, Any]], 
              test_size: float = 0.2) -> Dict[str, float]:
        """
        Обучение ML моделей на предоставленных данных.
        
        training_data: Список словарей с полями:
            - 'content': текст файла
            - 'file_path': путь к файлу
            - 'threat_type': тип угрозы (метка)
            - 'static_results': результаты статического анализа
        """
        if not SKLEARN_AVAILABLE:
            return {'error': 'Scikit-learn не установлен'}
        
        print(f"[*] Начало обучения на {len(training_data)} примерах...")
        
        # Подготовка данных
        X_features = []
        y_labels = []
        texts = []
        
        for sample in training_data:
            try:
                content = sample.get('content', '')
                file_path = sample.get('file_path', 'unknown')
                threat_type = sample.get('threat_type', 'CLEAN')
                static_results = sample.get('static_results', {})
                
                if threat_type not in self.SUPPORTED_THREATS:
                    continue
                
                features, _ = self.extract_features(content, file_path, static_results)
                X_features.append(features)
                y_labels.append(threat_type)
                texts.append(content)
            except Exception as e:
                print(f"[-] Ошибка обработки образца: {e}")
                continue
        
        if len(X_features) < 10:
            return {'error': 'Недостаточно данных для обучения (минимум 10 образцов)'}
        
        # Разделение на обучающую и тестовую выборки
        X_train, X_test, y_train, y_test = train_test_split(
            X_features, y_labels, test_size=test_size, random_state=42, stratify=y_labels
        )
        
        # Масштабирование признаков
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Кодирование меток
        y_train_encoded = self.label_encoder.transform(y_train)
        y_test_encoded = self.label_encoder.transform(y_test)
        
        # Обучение векторизатора
        self.vectorizer.fit(texts)
        
        # Обучение каждой модели
        metrics = {}
        
        for model_name, model in self.models.items():
            print(f"[*] Обучение модели: {model_name}")
            
            try:
                model.fit(X_train_scaled, y_train_encoded)
                
                # Оценка на тестовой выборке
                y_pred = model.predict(X_test_scaled)
                accuracy = accuracy_score(y_test_encoded, y_pred)
                
                metrics[model_name] = {
                    'accuracy': float(accuracy),
                    'report': classification_report(
                        y_test_encoded, y_pred,
                        target_names=self.label_encoder.classes_,
                        zero_division=0
                    )
                }
                
                print(f"[+] {model_name} обучена. Точность: {accuracy:.4f}")
                
            except Exception as e:
                print(f"[-] Ошибка обучения {model_name}: {e}")
                metrics[model_name] = {'error': str(e)}
        
        self.is_trained = True
        
        # Сохранение моделей
        self._save_models()
        
        return metrics
    
    def _save_models(self):
        """Сохранение обученных моделей."""
        if not SKLEARN_AVAILABLE:
            return
            
        model_file = os.path.join(self.model_path, 'threat_classifier.pkl')
        
        try:
            save_data = {
                'models': self.models,
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'vectorizer': self.vectorizer,
                'is_trained': self.is_trained,
                'version': self.MODEL_VERSION
            }
            
            with open(model_file, 'wb') as f:
                pickle.dump(save_data, f)
            
            print(f"[+] ML модели сохранены в {model_file}")
        except Exception as e:
            print(f"[-] Ошибка сохранения моделей: {e}")
    
    def add_training_sample(self, content: str, file_path: str, 
                           threat_type: str, static_results: Dict):
        """Добавление одного образца для будущего дообучения."""
        training_file = os.path.join(self.model_path, 'training_samples.jsonl')
        
        sample = {
            'content': content[:100000],  # Ограничение размера
            'file_path': file_path,
            'threat_type': threat_type,
            'static_results': static_results,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(training_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"[-] Ошибка добавления образца: {e}")
    
    def load_training_samples(self, max_samples: int = 1000) -> List[Dict[str, Any]]:
        """Загрузка накопленных образцов для переобучения."""
        training_file = os.path.join(self.model_path, 'training_samples.jsonl')
        samples = []
        
        if not os.path.exists(training_file):
            return samples
        
        try:
            with open(training_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if len(samples) >= max_samples:
                        break
                    try:
                        sample = json.loads(line.strip())
                        samples.append(sample)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"[-] Ошибка загрузки образцов: {e}")
        
        return samples
    
    def clear_cache(self):
        """Очистка кэша предсказаний."""
        self.prediction_cache.clear()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Получение информации о моделях."""
        return {
            'version': self.MODEL_VERSION,
            'sklearn_available': SKLEARN_AVAILABLE,
            'is_trained': self.is_trained,
            'use_ensemble': self.use_ensemble,
            'supported_threats': self.SUPPORTED_THREATS,
            'model_weights': self.model_weights,
            'cache_size': len(self.prediction_cache),
            'models_initialized': list(self.models.keys()) if SKLEARN_AVAILABLE else []
        }


# Для совместимости
if __name__ == "__main__":
    # Пример использования
    classifier = MLThreatClassifier()
    print(classifier.get_model_info())
