#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network Emulator - Эмулятор сети
Безопасная эмуляция DNS и HTTP для перехвата запросов вредоносного ПО
"""

import socket
import threading
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class NetworkEmulator:
    def __init__(self, dns_port: int = 53, http_port: int = 80):
        self.dns_port = dns_port
        self.http_port = http_port
        self.dns_server = None
        self.http_server = None
        self.running = False
        self.captured_requests: List[Dict] = []
        
        # Фейковые ответы
        self.fake_dns_responses = {
            "*": "127.0.0.1",  # Все домены резолвятся в localhost
            "google.com": "127.0.0.1",
            "microsoft.com": "127.0.0.1"
        }
        
        self.fake_http_response = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body>Fake Server</body></html>"
    
    def start(self):
        """Запуск эмуляторов"""
        self.running = True
        
        # Запуск DNS эмулятора (только если есть права)
        try:
            self.dns_thread = threading.Thread(target=self._run_dns_emulator, daemon=True)
            self.dns_thread.start()
            logger.info("✅ DNS эмулятор запущен")
        except Exception as e:
            logger.warning(f"⚠️  Не удалось запустить DNS эмулятор: {e}")
        
        # Запуск HTTP эмулятора
        try:
            self.http_thread = threading.Thread(target=self._run_http_emulator, daemon=True)
            self.http_thread.start()
            logger.info("✅ HTTP эмулятор запущен")
        except Exception as e:
            logger.warning(f"⚠️  Не удалось запустить HTTP эмулятор: {e}")
    
    def stop(self):
        """Остановка эмуляторов"""
        self.running = False
        
        if self.dns_server:
            try:
                self.dns_server.close()
            except:
                pass
        
        if self.http_server:
            try:
                self.http_server.close()
            except:
                pass
        
        logger.info("🛑 Эмуляторы остановлены")
    
    def _run_dns_emulator(self):
        """DNS эмулятор (UDP порт 53)"""
        try:
            self.dns_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.dns_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.dns_server.bind(('0.0.0.0', self.dns_port))
            self.dns_server.settimeout(1.0)
            
            logger.info(f"🌐 DNS эмулятор слушает на порту {self.dns_port}")
            
            while self.running:
                try:
                    data, addr = self.dns_server.recvfrom(512)
                    self._handle_dns_request(data, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"Ошибка DNS: {e}")
                    
        except PermissionError:
            logger.warning("Нет прав для запуска DNS на порту 53")
        except Exception as e:
            logger.error(f"Ошибка запуска DNS эмулятора: {e}")
    
    def _handle_dns_request(self, data: bytes, addr):
        """Обработка DNS запроса"""
        try:
            # Парсинг DNS запроса (упрощенный)
            domain = self._parse_dns_query(data)
            
            if domain:
                logger.info(f"🔍 DNS запрос: {domain} от {addr}")
                
                # Сохранение запроса
                self.captured_requests.append({
                    "type": "DNS",
                    "domain": domain,
                    "source": addr,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Отправка фейкового ответа
            response = self._create_fake_dns_response(data)
            self.dns_server.sendto(response, addr)
            
        except Exception as e:
            logger.error(f"Ошибка обработки DNS: {e}")
    
    def _parse_dns_query(self, data: bytes) -> Optional[str]:
        """Парсинг домена из DNS запроса"""
        try:
            # Пропускаем заголовок (12 байт)
            offset = 12
            
            if len(data) <= offset:
                return None
            
            labels = []
            while True:
                length = data[offset]
                if length == 0:
                    break
                offset += 1
                label = data[offset:offset+length].decode('utf-8', errors='ignore')
                labels.append(label)
                offset += length
            
            return '.'.join(labels) if labels else None
            
        except Exception:
            return None
    
    def _create_fake_dns_response(self, query: bytes) -> bytes:
        """Создание фейкового DNS ответа"""
        # Копируем ID и флаги
        response = bytearray(query[:2])
        response.append(0x81)  # Флаги ответа
        response.append(0x80)
        response.extend(query[4:6])  # Количество вопросов
        response.extend(query[6:8])  # Количество ответов
        response.extend(b'\x00\x00')  # Авторитетные записи
        response.extend(b'\x00\x00')  # Дополнительные записи
        
        # Добавляем ответ
        response.extend(b'\xc0\x0c')  # Указатель на домен
        response.extend(b'\x00\x01')  # Тип A
        response.extend(b'\x00\x01')  # Класс IN
        response.extend(b'\x00\x00\x00\x3c')  # TTL
        response.extend(b'\x00\x04')  # Длина данных
        response.extend(bytes([127, 0, 0, 1]))  # IP 127.0.0.1
        
        return bytes(response)
    
    def _run_http_emulator(self):
        """HTTP эмулятор"""
        try:
            self.http_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.http_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.http_server.bind(('0.0.0.0', self.http_port))
            self.http_server.listen(5)
            self.http_server.settimeout(1.0)
            
            logger.info(f"🌐 HTTP эмулятор слушает на порту {self.http_port}")
            
            while self.running:
                try:
                    client, addr = self.http_server.accept()
                    self._handle_http_request(client, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"Ошибка HTTP: {e}")
                    
        except Exception as e:
            logger.error(f"Ошибка запуска HTTP эмулятора: {e}")
    
    def _handle_http_request(self, client: socket.socket, addr):
        """Обработка HTTP запроса"""
        try:
            request = client.recv(4096).decode('utf-8', errors='ignore')
            
            if request:
                lines = request.split('\r\n')
                method_path = lines[0] if lines else ""
                
                logger.info(f"🌍 HTTP запрос: {method_path} от {addr}")
                
                # Сохранение запроса
                self.captured_requests.append({
                    "type": "HTTP",
                    "request": method_path,
                    "source": addr,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Отправка фейкового ответа
            client.sendall(self.fake_http_response)
            
        except Exception as e:
            logger.error(f"Ошибка обработки HTTP: {e}")
        finally:
            client.close()
    
    def get_captured_requests(self) -> List[Dict]:
        """Получение перехваченных запросов"""
        return self.captured_requests.copy()
    
    def get_statistics(self) -> Dict:
        """Получение статистики"""
        dns_count = sum(1 for r in self.captured_requests if r["type"] == "DNS")
        http_count = sum(1 for r in self.captured_requests if r["type"] == "HTTP")
        
        return {
            "total_requests": len(self.captured_requests),
            "dns_requests": dns_count,
            "http_requests": http_count,
            "running": self.running
        }
