"""
RedSand - Модуль сетевой эмуляции
Создает безопасную сетевую среду: локальный DNS, эмуляция интернета, перехват трафика
"""

import socket
import threading
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class NetworkEmulator:
    """Эмулятор сетевой среды для безопасного анализа"""
    
    def __init__(self):
        self.dns_server = None
        self.http_server = None
        self.connections_log = []
        self.running = False
        
        # Фейковые ответы для распространенных доменов
        self.fake_dns = {
            "google.com": "142.250.185.46",
            "facebook.com": "157.240.1.35",
            "microsoft.com": "20.112.250.133",
            "amazon.com": "54.239.28.85",
            "github.com": "140.82.121.4",
            "malware-c2.com": "127.0.0.1",  # Перенаправляем вредоносные на localhost
            "evil-server.net": "127.0.0.1",
        }
        
        # Фейковые ответы HTTP
        self.fake_http_responses = {
            "/": "<html><body>Fake Website</body></html>",
            "/api/status": '{"status": "ok"}',
            "/update": "Fake update data",
        }
    
    def start_emulation(self) -> Dict[str, Any]:
        """Запуск сетевой эмуляции"""
        results = {
            "dns_server": self._start_dns_server(),
            "http_server": self._start_http_server(),
            "network_config": self._configure_network()
        }
        self.running = True
        return results
    
    def _start_dns_server(self) -> Dict[str, Any]:
        """Запуск простого DNS сервера"""
        dns_info = {"started": False, "port": 5353}
        
        try:
            # Создаем UDP сокет для DNS (порт 53 требует root, используем 5353)
            self.dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.dns_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.dns_socket.bind(("0.0.0.0", 5353))
            self.dns_socket.settimeout(1)
            
            dns_info["started"] = True
            dns_info["message"] = "DNS сервер запущен на порту 5353"
            
            # Запускаем в отдельном потоке
            dns_thread = threading.Thread(target=self._dns_server_loop, daemon=True)
            dns_thread.start()
            
        except Exception as e:
            dns_info["error"] = str(e)
            
        return dns_info
    
    def _dns_server_loop(self):
        """Основной цикл DNS сервера"""
        while self.running:
            try:
                data, addr = self.dns_socket.recvfrom(512)
                # Простая эмуляция DNS ответа
                domain = self._parse_dns_query(data)
                if domain:
                    response_ip = self.fake_dns.get(domain.lower(), "93.184.216.34")  # example.com
                    self._send_dns_response(data, addr, response_ip)
                    self.connections_log.append({
                        "type": "DNS",
                        "domain": domain,
                        "resolved_ip": response_ip,
                        "timestamp": datetime.now().isoformat()
                    })
            except socket.timeout:
                continue
            except Exception as e:
                break
    
    def _parse_dns_query(self, data: bytes) -> Optional[str]:
        """Парсинг DNS запроса"""
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
                labels.append(data[offset:offset+length].decode('ascii'))
                offset += length
            
            return ".".join(labels)
        except Exception:
            return None
    
    def _send_dns_response(self, query: bytes, addr: tuple, ip: str):
        """Отправка DNS ответа"""
        try:
            # Простой ответ с фиксированным IP
            response = bytearray(query[:2])  # ID запроса
            response.extend(b'\x81\x80')  # Флаги ответа
            response.extend(query[4:6])  # Количество вопросов
            response.extend(query[4:6])  # Количество ответов
            response.extend(b'\x00\x00\x00\x00')  # Авторитетные и дополнительные записи
            response.extend(query[12:])  # Оригинаный вопрос
            response.extend(b'\xc0\x0c')  # Указатель на имя
            response.extend(b'\x00\x01\x00\x01')  # Тип A, класс IN
            response.extend(b'\x00\x00\x00\x3c')  # TTL 60 секунд
            response.extend(b'\x00\x04')  # Длина данных
            response.extend(bytes(map(int, ip.split('.'))))
            
            self.dns_socket.sendto(response, addr)
        except Exception:
            pass
    
    def _start_http_server(self) -> Dict[str, Any]:
        """Запуск простого HTTP сервера"""
        http_info = {"started": False, "port": 8080}
        
        try:
            self.http_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.http_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.http_socket.bind(("0.0.0.0", 8080))
            self.http_socket.listen(5)
            self.http_socket.settimeout(1)
            
            http_info["started"] = True
            http_info["message"] = "HTTP сервер запущен на порту 8080"
            
            # Запускаем в отдельном потоке
            http_thread = threading.Thread(target=self._http_server_loop, daemon=True)
            http_thread.start()
            
        except Exception as e:
            http_info["error"] = str(e)
            
        return http_info
    
    def _http_server_loop(self):
        """Основной цикл HTTP сервера"""
        while self.running:
            try:
                client_socket, addr = self.http_socket.accept()
                request = client_socket.recv(1024).decode('utf-8', errors='ignore')
                
                # Парсим путь запроса
                path = "/"
                if request:
                    lines = request.split('\r\n')
                    if lines:
                        parts = lines[0].split(' ')
                        if len(parts) > 1:
                            path = parts[1]
                
                # Формируем ответ
                response_body = self.fake_http_responses.get(path, "<html><body>404 Not Found</body></html>")
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}"
                
                client_socket.sendall(response.encode())
                client_socket.close()
                
                self.connections_log.append({
                    "type": "HTTP",
                    "path": path,
                    "client": addr[0],
                    "timestamp": datetime.now().isoformat()
                })
                
            except socket.timeout:
                continue
            except Exception as e:
                break
    
    def _configure_network(self) -> Dict[str, Any]:
        """Настройка сетевого окружения"""
        config = {
            "localhost_ip": "127.0.0.1",
            "fake_gateway": "192.168.1.1",
            "fake_subnet": "192.168.1.0/24",
            "blocked_ports": [25, 445, 3389],  # Блокируем опасные порты
            "allowed_outbound": ["80", "443", "53", "8080", "5353"]
        }
        return config
    
    def get_connections_log(self) -> List[Dict[str, Any]]:
        """Получение лога сетевых подключений"""
        return self.connections_log
    
    def stop_emulation(self):
        """Остановка сетевой эмуляции"""
        self.running = False
        
        if hasattr(self, 'dns_socket'):
            try:
                self.dns_socket.close()
            except Exception:
                pass
                
        if hasattr(self, 'http_socket'):
            try:
                self.http_socket.close()
            except Exception:
                pass
    
    def analyze_network_behavior(self) -> Dict[str, Any]:
        """Анализ сетевого поведения образца"""
        analysis = {
            "total_connections": len(self.connections_log),
            "dns_queries": [],
            "http_requests": [],
            "suspicious_domains": [],
            "risk_score": 0
        }
        
        suspicious_tlds = [".ru", ".cn", ".tk", ".top", ".xyz", ".pw"]
        suspicious_keywords = ["malware", "evil", "hack", "c2", "botnet", "trojan"]
        
        for conn in self.connections_log:
            if conn["type"] == "DNS":
                analysis["dns_queries"].append(conn["domain"])
                domain_lower = conn["domain"].lower()
                
                # Проверка на подозрительные домены
                if any(tld in domain_lower for tld in suspicious_tlds):
                    analysis["suspicious_domains"].append(conn["domain"])
                    analysis["risk_score"] += 10
                    
                if any(keyword in domain_lower for keyword in suspicious_keywords):
                    analysis["suspicious_domains"].append(conn["domain"])
                    analysis["risk_score"] += 20
                    
            elif conn["type"] == "HTTP":
                analysis["http_requests"].append(conn["path"])
                if any(keyword in conn["path"].lower() for keyword in suspicious_keywords):
                    analysis["risk_score"] += 15
        
        return analysis


if __name__ == "__main__":
    # Тестирование модуля
    print("[*] Запуск сетевого эмулятора...")
    emulator = NetworkEmulator()
    results = emulator.start_emulation()
    
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Ждем немного для тестирования
    import time
    time.sleep(5)
    
    # Анализ поведения
    analysis = emulator.analyze_network_behavior()
    print("\n[*] Анализ сетевого поведения:")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
    
    emulator.stop_emulation()
    print("\n[*] Сетевой эмулятор остановлен")
