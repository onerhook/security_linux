# 🔒 RedSand Secure - Руководство по максимальной безопасности

## 📋 Содержание
1. [Обзор архитектуры безопасности](#обзор-архитектуры-безопасности)
2. [Docker Security Hardening](#docker-security-hardening)
3. [Multiprocessing с изоляцией](#multiprocessing-с-изоляцией)
4. [Запуск в production](#запуск-v-production)
5. [Чеклист безопасности](#чеклист-безопасности)
6. [Мониторинг и аудит](#мониторинг-и-аудит)

---

## 🏗️ Обзор архитектуры безопасности

### Многоуровневая защита

```
┌─────────────────────────────────────────────────────────────┐
│                    HOST SYSTEM                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Docker Daemon (Hardened)                 │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │           Container Runtime (runc)              │  │  │
│  │  │  ┌───────────────────────────────────────────┐  │  │  │
│  │  │  │      RedSand Secure Container             │  │  │  │
│  │  │  │  ┌─────────────────────────────────────┐  │  │  │  │
│  │  │  │  │   Application Layer (Python)        │  │  │  │  │
│  │  │  │  │   • Non-root user (UID 10001)       │  │  │  │  │
│  │  │  │  │   • Read-only filesystem            │  │  │  │  │
│  │  │  │  │   • Process isolation               │  │  │  │  │
│  │  │  │  │   • Network disabled                │  │  │  │  │
│  │  │  │  └─────────────────────────────────────┘  │  │  │  │
│  │  │  │  ┌─────────────────────────────────────┐  │  │  │  │
│  │  │  │  │   Security Profiles                 │  │  │  │  │
│  │  │  │  │   • Seccomp (syscall filtering)     │  │  │  │  │
│  │  │  │  │   • AppArmor (MAC)                  │  │  │  │  │
│  │  │  │  │   • Capabilities dropped            │  │  │  │  │
│  │  │  │  └─────────────────────────────────────┘  │  │  │  │
│  │  │  └───────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Уровни защиты

| Уровень | Мера защиты | Описание |
|---------|-------------|----------|
| **L1** | Non-root пользователь | Запуск от UID 10001 без привилегий |
| **L2** | Read-only FS | Корневая ФС только для чтения |
| **L3** | Seccomp профиль | Фильтрация системных вызовов |
| **L4** | AppArmor профиль | Mandatory Access Control |
| **L5** | Drop capabilities | Удаление всех Linux capabilities |
| **L6** | Network isolation | Полная изоляция сети |
| **L7** | Resource limits | Ограничение CPU, памяти, процессов |
| **L8** | Process isolation | Multiprocessing в sandbox |

---

## 🐳 Docker Security Hardening

### 1. Multi-stage Build

**Dockerfile.secure** использует multi-stage build для минимизации attack surface:

```dockerfile
# Stage 1: Builder (только для компиляции)
FROM python:3.11-slim-bookworm AS builder
# ... установка зависимостей ...

# Stage 2: Production (минимальный образ)
FROM python:3.11-slim-bookworm AS production
# ... только необходимые файлы ...
```

**Преимущества:**
- ✅ Нет компиляторов в production
- ✅ Меньший размер образа (~150MB vs ~500MB)
- ✅ Нет dev-зависимостей
- ✅ Меньше уязвимостей

### 2. Seccomp Профиль

**seccomp_profile.json** разрешает только безопасные syscall:

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "syscalls": [
    {
      "names": ["read", "write", "open", "close", ...],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

**Запрещенные опасные syscall:**
- ❌ `ptrace` - отладка процессов
- ❌ `mount` - монтирование ФС
- ❌ `reboot` - перезагрузка системы
- ❌ `kexec_load` - загрузка нового ядра
- ❌ `init_module`, `delete_module` - модули ядра

### 3. AppArmor Профиль

**apparmor_profile** обеспечивает Mandatory Access Control:

```bash
profile redsand-secure flags=(attach_disconnected,mediate_deleted) {
  # Запрет опасных capabilities
  capability !sys_admin,
  capability !sys_ptrace,
  capability !net_raw,
  
  # Запрет доступа к системным директориям
  deny /{dev,proc,sys,run}/** rw,
  
  # Разрешение только необходимых путей
  /app/redsand_secure.py ix,
  /app/logs/** rw,
  /app/samples/** r,
}
```

### 4. Docker Compose Security Options

**docker-compose.yml** включает все меры защиты:

```yaml
services:
  redsand-analyzer:
    # Read-only корневая ФС
    read_only: true
    
    # Временные ФС с noexec,nosuid
    tmpfs:
      - /tmp:size=100M,mode=1777,noexec,nosuid
    
    # Security options
    security_opt:
      - no-new-privileges:true
      - apparmor:docker-default
      - seccomp:./seccomp_profile.json
    
    # Drop всех capabilities
    cap_drop:
      - ALL
    
    # Минимальные capabilities
    cap_add:
      - CHOWN
    
    # Изоляция
    ipc: none
    pid: none
    
    # Resource limits
    cpus: 2.0
    mem_limit: 512m
    pids_limit: 50
    
    # Ulimits
    ulimits:
      nofile:
        soft: 1024
        hard: 1024
      nproc:
        soft: 50
        hard: 50
```

---

## ⚡ Multiprocessing с изоляцией

### Архитектура worker процессов

```
Master Process (UID 10001)
│
├── Worker Process 1 (isolated)
│   ├── StaticAnalyzer
│   ├── ThreatClassifier
│   └── ReportGenerator
│
├── Worker Process 2 (isolated)
│   ├── StaticAnalyzer
│   ├── ThreatClassifier
│   └── ReportGenerator
│
└── Worker Process N (isolated)
    ├── StaticAnalyzer
    ├── ThreatClassifier
    └── ReportGenerator
```

### Безопасный запуск workers

**redsand_secure.py**:

```python
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

class RedSandSecure:
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(mp.cpu_count(), 2)
        
    def analyze_batch_multiprocessing(self, file_paths: List[str]):
        # Каждый worker запускается в изолированном процессе
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(analyze_single_file_worker, args): file_path
                for file_path in file_paths
            }
            
            for future in as_completed(futures):
                result = future.result()
                # Обработка результатов...
```

### Меры безопасности для multiprocessing

1. **Ограниченное количество workers**: Максимум 2 для снижения риска
2. **Изоляция памяти**: Каждый worker имеет свое адресное пространство
3. **Timeout на анализ**: 60 секунд максимум на файл
4. **Catch-all exceptions**: Предотвращение crash master процесса
5. **No shared state**: Workers не имеют общего состояния

---

## 🚀 Запуск в Production

### 1. Подготовка окружения

```bash
# Создание директорий
mkdir -p samples reports quarantine config redis-data

# Установка правильных прав
chmod 750 samples reports quarantine config
chown 10001:10001 reports quarantine

# Генерация случайного пароля для Redis
export REDIS_PASSWORD=$(openssl rand -base64 32)
echo "REDIS_PASSWORD=$REDIS_PASSWORD" > .env
```

### 2. Запуск с максимальными настройками безопасности

```bash
# Вариант A: Docker Compose (рекомендуется)
docker-compose --env-file .env up -d

# Вариант B: Docker run с полным набором опций
docker run -d \
  --name redsand-secure \
  --hostname redsand-sandbox \
  --user 10001:10001 \
  --read-only \
  --tmpfs /tmp:noexec,nosuid,size=100m \
  --tmpfs /app/logs:noexec,nosuid,size=50m \
  --tmpfs /app/reports:noexec,nosuid,size=200m \
  --security-opt no-new-privileges:true \
  --security-opt seccomp=./seccomp_profile.json \
  --security-opt apparmor=./apparmor_profile \
  --cap-drop ALL \
  --cap-add CHOWN \
  --ipc none \
  --pid none \
  --cpus=2.0 \
  --memory=512m \
  --memory-swap=512m \
  --pids-limit=50 \
  --ulimit nofile=1024:1024 \
  --ulimit nproc=50:50 \
  --network none \
  -v $(pwd)/samples:/app/samples:ro \
  -v $(pwd)/reports:/app/reports:rw \
  -v $(pwd)/quarantine:/app/quarantine:rw \
  -v $(pwd)/config:/app/config:ro \
  -e REDSAND_SECURITY_LEVEL=maximum \
  -e SECURE_MODE=true \
  -e NETWORK_ENABLED=false \
  redsand-secure:latest \
  python redsand_secure.py --input /app/samples --workers 2
```

### 3. Проверка безопасности

```bash
# Проверка что контейнер запущен от non-root
docker exec redsand-secure id
# uid=10001(redsand) gid=10001(redsand)

# Проверка read-only ФС
docker exec redsand-secure touch /test 2>&1
# Touch: cannot touch '/test': Read-only file system

# Проверка отсутствия сети
docker exec redsand-secure ping -c1 8.8.8.8 2>&1
# ping: Network is unreachable

# Проверка capabilities
docker exec redsand-secure cat /proc/self/status | grep Cap
# CapEff: 0000000000000000 (все zero!)
```

---

## ✅ Чеклист безопасности

### Pre-deployment

- [ ] Образ собран с `Dockerfile.secure`
- [ ] Seccomp профиль применен
- [ ] AppArmor профиль загружен
- [ ] Пользователь non-root (UID 10001)
- [ ] Read-only корневая ФС
- [ ]Tmpfs с noexec,nosuid

### Runtime

- [ ] Все capabilities dropped
- [ ] Сеть отключена (или internal network)
- [ ] Resource limits установлены
- [ ] Ulimits настроены
- [ ] IPC и PID namespace изолированы
- [ ] No new privileges

### Monitoring

- [ ] Health check активен
- [ ] Логирование включено
- [ ] Аудит syscall активен
- [ ] Alerts настроены

### Post-analysis

- [ ] Samples удалены из /app/samples
- [ ] Отчеты перемещены в secure storage
- [ ] Карантин проверен
- [ ] Логи архивированы

---

## 📊 Мониторинг и аудит

### Docker Events

```bash
# Мониторинг событий контейнера
docker events --filter container=redsand-secure

# Просмотр логов
docker logs --follow redsand-secure

# Проверка использования ресурсов
docker stats redsand-secure
```

### Audit Logging

Включение аудита Python:

```bash
export PYTHONAUDIT=1
python -X audit redsand_secure.py
```

### Prometheus Metrics (опционально)

```yaml
# docker-compose.override.yml для мониторинга
services:
  redsand-analyzer:
    ports:
      - "127.0.0.1:8080:8080"  # Только для метрик!
    
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
```

---

## 🛡️ Дополнительные рекомендации

### 1. Host Hardening

```bash
# Включить user namespace remapping
# /etc/docker/daemon.json
{
  "userns-remap": "default",
  "no-new-privileges": true,
  "live-restore": false
}

# Restart Docker
systemctl restart docker
```

### 2. Network Policies

```bash
# Создать полностью изолированную сеть
docker network create \
  --driver bridge \
  --internal \
  --subnet 172.28.0.0/16 \
  --gateway 172.28.0.1 \
  --opt com.docker.network.bridge.enable_icc=false \
  redsand-isolated
```

### 3. Secret Management

```bash
# Использовать Docker secrets (Swarm mode)
echo "my_secret_password" | docker secret create redis_password -

# В docker-compose.yml
secrets:
  redis_password:
    external: true
```

### 4. Image Scanning

```bash
# Сканирование образа на уязвимости
docker scan redsand-secure:latest

# Или использовать Trivy
trivy image redsand-secure:latest
```

---

## 📞 Экстренные процедуры

### Panic Button - Немедленная остановка

```bash
# Остановить все контейнеры
docker-compose down --timeout 5

# Убить все процессы анализа
docker kill redsand-secure

# Очистить временные файлы
docker volume prune -f

# Проверить хост на аномалии
ps aux | grep python
netstat -tulpn
lsof -i
```

### Восстановление после инцидента

1. Остановить все контейнеры
2. Сохранить логи для анализа
3. Пересоздать контейнеры с чистого образа
4. Проверить хост систему
5. Обновить правила безопасности

---

## 📚 Ресурсы

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [OWASP Container Security](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [NIST Container Security Guide](https://csrc.nist.gov/publications/detail/sp/800-190/final)
- [Seccomp Documentation](https://www.kernel.org/doc/html/latest/userspace-api/seccomp.html)
- [AppArmor Documentation](https://apparmor.net/)

---

**⚠️ WARNING**: Даже с максимальной защитой, анализ вредоносного ПО всегда несет риски. 
Запускайте ТОЛЬКО в изолированной VM или dedicated hardware!
