#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network Emulator - Эмуляция сетевой активности
Локальные DNS и HTTP серверы для безопасного перехвата запросов
"""

import socket
import threading
import time
from datetime import datetime

class NetworkEmulator:
    def __init__(self, dns_port=53, http_port=80):
        self.dns_port = dns_port
        self.http_port = http_port
        self.dns_server = None
        self.http_server = None
        self.running = False
        self.requests_log = []
        
    def start(self):
        """Запуск эмуляции сети"""
        self.running = True
        
        # Запуск DNS сервера
        dns_thread = threading.Thread(target=self._run_dns_server)
        dns_thread.daemon = True
        dns_thread.start()
        
        # Запуск HTTP сервера
        http_thread = threading.Thread(target=self._run_http_server)
        http_thread.daemon = True
        http_thread.start()
        
        time.sleep(1)  # Даем время на запуск
    
    def stop(self):
        """Остановка эмуляции"""
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
    
    def _run_dns_server(self):
        """Простой DNS сервер"""
        try:
            self.dns_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.dns_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.dns_server.bind(('0.0.0.0', self.dns_port))
            self.dns_server.settimeout(1.0)
            
            while self.running:
                try:
                    data, addr = self.dns_server.recvfrom(512)
                    self._log_request('DNS', f"Query from {addr[0]}")
                    
                    # Отвечаем своим IP на любой запрос
                    response = self._create_dns_response(data)
                    if response:
                        self.dns_server.sendto(response, addr)
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    break
                    
        except Exception as e:
            self._log_request('ERROR', f"DNS server error: {str(e)}")
    
    def _run_http_server(self):
        """Простой HTTP сервер"""
        try:
            self.http_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.http_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.http_server.bind(('0.0.0.0', self.http_port))
            self.http_server.listen(5)
            self.http_server.settimeout(1.0)
            
            while self.running:
                try:
                    client, addr = self.http_server.accept()
                    self._log_request('HTTP', f"Connection from {addr[0]}")
                    
                    request = client.recv(1024).decode('utf-8', errors='ignore')
                    
                    # Логируем URL
                    if request:
                        lines = request.split('\n')
                        if lines:
                            method_url = lines[0].split(' ')
                            if len(method_url) >= 2:
                                self._log_request('HTTP', f"{method_url[0]} {method_url[1]}")
                    
                    # Отправляем успешный ответ
                    response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body>OK</body></html>"
                    client.sendall(response.encode())
                    client.close()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    break
                    
        except Exception as e:
            self._log_request('ERROR', f"HTTP server error: {str(e)}")
    
    def _create_dns_response(self, request_data):
        """Создание простого DNS ответа"""
        if len(request_data) < 12:
            return None
        
        # ID запроса
        tx_id = request_data[:2]
        
        # Флаги ответа (стандартный ответ)
        flags = b'\x81\x80'
        
        # Вопросы и ответы
        questions = request_data[4:6]
        answers = b'\x00\x01'  # Один ответ
        
        # TTL (5 минут)
        ttl = b'\x00\x00\x01\x2c'
        
        # Длина данных ответа (4 байта для IPv4)
        rd_length = b'\x00\x04'
        
        # Наш IP (127.0.0.1)
        fake_ip = b'\x7f\x00\x00\x01'
        
        response = tx_id + flags + questions + answers
        response += b'\xc0\x0c'  # Pointer к имени
        response += b'\x00\x01'  # Type A
        response += b'\x00\x01'  # Class IN
        response += ttl
        response += rd_length
        response += fake_ip
        
        return response
    
    def _log_request(self, req_type, message):
        """Логирование запроса"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': req_type,
            'message': message
        }
        self.requests_log.append(entry)
    
    def get_requests_log(self):
        """Получение лога запросов"""
        return self.requests_log
