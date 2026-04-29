#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLEAN FILE TEST - Легитимный Python скрипт
Это тестовый файл для проверки отсутствия ложных срабатываний
"""

import json
import logging
import argparse
from typing import Dict, List

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Легитимный класс для обработки данных"""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        logger.info("DataProcessor initialized")
    
    def _load_config(self, path: str) -> Dict:
        """Загрузка конфигурации из JSON"""
        with open(path, 'r') as f:
            return json.loads(f.read())
    
    def process(self, data: List) -> List:
        """Обработка данных"""
        result = []
        for item in data:
            processed = self._transform(item)
            result.append(processed)
        return result
    
    def _transform(self, item: Dict) -> Dict:
        """Трансформация элемента"""
        return {k: v.upper() if isinstance(v, str) else v for k, v in item.items()}


def main():
    """Точка входа приложения"""
    parser = argparse.ArgumentParser(description='Data Processor')
    parser.add_argument('--config', type=str, required=True, help='Config file path')
    parser.add_argument('--input', type=str, help='Input file path')
    args = parser.parse_args()
    
    processor = DataProcessor(args.config)
    logger.info("Processing started")
    
    # Пример обработки
    sample_data = [{'name': 'test', 'value': 123}]
    result = processor.process(sample_data)
    
    print(json.dumps(result, indent=2))
    logger.info("Processing completed")


if __name__ == '__main__':
    main()
