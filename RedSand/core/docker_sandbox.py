#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedSand Docker Sandbox - Безопасное выполнение файлов в Docker контейнере
Изолирует запуск executables от основной системы
"""

import os
import sys
import time
import json
import subprocess
import threading
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime


class DockerSandbox:
    """
    Запускает подозрительные файлы в изолированном Docker контейнере.
    Предотвращает заражение основной системы.
    """
    
    def __init__(self, container_name: str = "redsand_sandbox", timeout: int = 60):
        self.container_name = container_name
        self.timeout = timeout
        self.container_id: Optional[str] = None
        self.is_running = False
        self.events_log: List[Dict[str, Any]] = []
        self.temp_dir: Optional[str] = None
        
    def _log_event(self, event_type: str, message: str, severity: int = 5):
        """Логирование событий"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'message': message,
            'severity': severity
        }
        self.events_log.append(event)
        print(f"[DockerSandbox] {event_type}: {message}")
    
    def is_docker_available(self) -> bool:
        """Проверка доступности Docker"""
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            self._log_event('ERROR', f'Docker недоступен: {e}', 9)
            return False
    
    def create_container(self, file_path: str) -> bool:
        """
        Создает изолированный контейнер для анализа файла.
        Файл копируется в контейнер, но не имеет доступа к хост-системе.
        """
        if not self.is_docker_available():
            self._log_event('ERROR', 'Docker не установлен или недоступен', 10)
            return False
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            self._log_event('ERROR', f'Файл не найден: {file_path}', 9)
            return False
        
        # Создаем временную директорию для изоляции
        self.temp_dir = tempfile.mkdtemp(prefix='redsand_sandbox_')
        self._log_event('INFO', f'Создана временная директория: {self.temp_dir}', 2)
        
        # Копируем файл во временную директорию
        file_name = os.path.basename(file_path)
        sandbox_file_path = os.path.join(self.temp_dir, file_name)
        shutil.copy2(file_path, sandbox_file_path)
        self._log_event('INFO', f'Файл скопирован в песочницу: {sandbox_file_path}', 2)
        
        try:
            # Создаем контейнер с ограничениями:
            # --rm: автоматическое удаление после завершения
            # --network none: полный запрет сети
            # --read-only: файловая система только для чтения
            # --tmpfs /tmp: временная файловая система для записи
            # --cap-drop ALL: отключаем все capabilities
            # --security-opt seccomp=unconfined: строгий seccomp профиль
            # --pids-limit 50: ограничение на количество процессов
            # --memory 512m: ограничение памяти
            # --cpu-quota 50000: ограничение CPU
            
            docker_cmd = [
                'docker', 'run', '--rm',
                '--name', self.container_name,
                '--network', 'none',  # Полная изоляция сети
                '--read-only',  # Root FS только для чтения
                '--tmpfs', '/tmp:rw,noexec,nosuid,size=100m',  # Временная FS
                '--tmpfs', '/app:rw,noexec,nosuid,size=100m',  # Директория приложения
                '--cap-drop', 'ALL',  # Отключаем все привилегии
                '--security-opt', 'no-new-privileges:true',
                '--pids-limit', '50',  # Максимум процессов
                '--memory', '512m',  # Ограничение памяти
                '--cpus', '0.5',  # Ограничение CPU
                '-v', f'{self.temp_dir}:/app:ro',  # Монтируем файл только для чтения
                '-w', '/app',  # Рабочая директория
                'ubuntu:22.04',  # Базовый образ
                'timeout', str(self.timeout),  # Таймаут выполнения
                '/bin/bash', '-c',  # Команда для выполнения
                f'chmod +x /app/{file_name} && /app/{file_name} || true'
            ]
            
            self._log_event('INFO', f'Запуск контейнера: {" ".join(docker_cmd)}', 3)
            
            # Запускаем контейнер
            process = subprocess.Popen(
                docker_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            self.is_running = True
            self._log_event('CONTAINER_STARTED', f'Контейнер запущен с PID {process.pid}', 4)
            
            # Ждем завершения с таймаутом
            try:
                stdout, stderr = process.communicate(timeout=self.timeout + 10)
                
                # Логируем вывод
                if stdout:
                    self._log_event('STDOUT', stdout[:500], 3)  # Первые 500 символов
                if stderr:
                    self._log_event('STDERR', stderr[:500], 5)  # Первые 500 символов
                
                self._log_event('CONTAINER_STOPPED', f'Контейнер завершен с кодом {process.returncode}', 4)
                return True
                
            except subprocess.TimeoutExpired:
                self._log_event('TIMEOUT', f'Превышен таймаут {self.timeout}с', 8)
                process.kill()
                return False
                
        except Exception as e:
            self._log_event('ERROR', f'Ошибка создания контейнера: {e}', 9)
            self.cleanup()
            return False
    
    def analyze_with_wine(self, file_path: str) -> bool:
        """
        Альтернативный метод: запуск Windows EXE через Wine в Docker.
        Для анализа Windows executables на Linux системах.
        """
        if not self.is_docker_available():
            return False
        
        if not os.path.exists(file_path):
            return False
        
        # Создаем временную директорию
        self.temp_dir = tempfile.mkdtemp(prefix='redsand_wine_')
        file_name = os.path.basename(file_path)
        sandbox_file_path = os.path.join(self.temp_dir, file_name)
        shutil.copy2(file_path, sandbox_file_path)
        
        try:
            # Используем образ с Wine для запуска Windows приложений
            docker_cmd = [
                'docker', 'run', '--rm',
                '--name', f'{self.container_name}_wine',
                '--network', 'none',
                '--read-only',
                '--tmpfs', '/tmp:rw,noexec,nosuid,size=100m',
                '--tmpfs', '/app:rw,noexec,nosuid,size=100m',
                '--cap-drop', 'ALL',
                '--security-opt', 'no-new-privileges:true',
                '--pids-limit', '50',
                '--memory', '512m',
                '--cpus', '0.5',
                '-v', f'{self.temp_dir}:/app:ro',
                '-w', '/app',
                'scottyhardy/docker-wine:latest',  # Образ с Wine
                'timeout', str(self.timeout),
                'wine', f'/app/{file_name}'
            ]
            
            self._log_event('INFO', 'Запуск через Wine в Docker', 3)
            
            process = subprocess.Popen(
                docker_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            self.is_running = True
            
            try:
                stdout, stderr = process.communicate(timeout=self.timeout + 10)
                
                if stdout:
                    self._log_event('WINE_OUTPUT', stdout[:500], 3)
                if stderr:
                    self._log_event('WINE_ERROR', stderr[:500], 5)
                
                return True
            except subprocess.TimeoutExpired:
                self._log_event('TIMEOUT', 'Превышен таймаут Wine', 8)
                process.kill()
                return False
                
        except Exception as e:
            self._log_event('ERROR', f'Ошибка Wine: {e}', 9)
            self.cleanup()
            return False
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self._log_event('CLEANUP', f'Удалена временная директория: {self.temp_dir}', 2)
            except Exception as e:
                self._log_event('ERROR', f'Ошибка очистки: {e}', 7)
            self.temp_dir = None
        
        # Принудительная остановка контейнера если еще работает
        if self.is_running:
            try:
                subprocess.run(
                    ['docker', 'stop', self.container_name],
                    capture_output=True,
                    timeout=10
                )
                self._log_event('CONTAINER_STOPPED', 'Контейнер остановлен принудительно', 4)
            except Exception:
                pass
            self.is_running = False
    
    def get_events_log(self) -> List[Dict[str, Any]]:
        """Возвращает лог событий"""
        return self.events_log
    
    def run_analysis(self, file_path: str, use_wine: bool = False) -> Dict[str, Any]:
        """
        Полный цикл анализа файла в Docker песочнице.
        Возвращает результаты анализа.
        """
        result = {
            'success': False,
            'method': 'docker_wine' if use_wine else 'docker_native',
            'file_path': file_path,
            'events': [],
            'error': None,
            'isolated': True
        }
        
        try:
            if use_wine or file_path.lower().endswith('.exe'):
                success = self.analyze_with_wine(file_path)
            else:
                success = self.create_container(file_path)
            
            result['success'] = success
            result['events'] = self.get_events_log()
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
        
        finally:
            self.cleanup()
        
        return result


def analyze_in_docker(file_path: str, timeout: int = 60, use_wine: bool = False) -> Dict[str, Any]:
    """
    Удобная функция для быстрого анализа файла в Docker.
    
    Args:
        file_path: Путь к файлу для анализа
        timeout: Таймаут выполнения в секундах
        use_wine: Использовать Wine для Windows executables
    
    Returns:
        Словарь с результатами анализа
    """
    sandbox = DockerSandbox(timeout=timeout)
    return sandbox.run_analysis(file_path, use_wine=use_wine)


if __name__ == '__main__':
    # Тестирование модуля
    print("RedSand Docker Sandbox Module")
    print("=" * 50)
    
    # Проверка Docker
    sandbox = DockerSandbox()
    if sandbox.is_docker_available():
        print("[+] Docker доступен")
    else:
        print("[-] Docker недоступен")
        print("    Установите Docker: https://docs.docker.com/get-docker/")
        print("    Или используйте режим без Docker (менее безопасно)")
    
    # Пример использования:
    # result = analyze_in_docker('/path/to/suspicious.exe', timeout=30)
    # print(json.dumps(result, indent=2, ensure_ascii=False))
