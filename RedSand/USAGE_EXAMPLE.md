# RedSand - Примеры использования

## Быстрый старт

### 1. Базовый анализ файла

```bash
python src/orchestrator.py --sample samples/suspicious.exe --output reports/report.json
```

### 2. Полный цикл анализа

```bash
# Шаг 1: Запуск оркестратора
python src/orchestrator.py --sample samples/file.exe --timeout 60 --verbose

# Шаг 2: Углубленный анализ отчета
python src/analyzer.py reports/report.json reports/report_analyzed.json

# Шаг 3: Генерация отчетов во всех форматах
python src/reporter.py reports/report_analyzed.json reports
```

## Интерпретация результатов

### Вердикты

| Вердикт | Описание | Действия |
|---------|----------|----------|
| **SAFE** | Файл безопасен | Можно использовать |
| **SUSPICIOUS** | Подозрительная активность | Требуется дополнительный анализ |
| **MALICIOUS** | Обнаружено вредоносное ПО | Удалить файл, проверить систему |

### Уровни риска

- **LOW (0-39)**: Минимальная угроза
- **MEDIUM (40-69)**: Средняя угроза
- **HIGH (70-100)**: Высокая угроза

## Сценарии использования

### Сценарий 1: Анализ одного файла

```bash
python src/orchestrator.py \
    --sample downloads/potential_malware.exe \
    --output reports/malware_analysis.json \
    --timeout 90 \
    --verbose
```

### Сценарий 2: Пакетный анализ

```bash
#!/bin/bash
for file in samples/*.exe; do
    filename=$(basename "$file" .exe)
    python src/orchestrator.py --sample "$file" --output "reports/${filename}.json"
    python src/analyzer.py "reports/${filename}.json" "reports/${filename}_analyzed.json"
done
```

### Сценарий 3: Автоматизация с проверкой вердикта

```bash
#!/bin/bash
python src/orchestrator.py --sample "$1" --output temp_report.json
python src/analyzer.py temp_report.json analyzed_report.json

verdict=$(python -c "import json; print(json.load(open('analyzed_report.json'))['verdict']['verdict'])")

if [ "$verdict" == "MALICIOUS" ]; then
    echo "⚠️  Файл распознан как вредоносный!"
    rm "$1"
elif [ "$verdict" == "SUSPICIOUS" ]; then
    echo "⚡ Файл подозрительный, требуется ручной анализ"
else
    echo "✅ Файл безопасен"
fi

rm temp_report.json analyzed_report.json
```

## Интеграция с другими инструментами

### Экспорт IOC для блокировки

```python
import json

with open('reports/report_full.json') as f:
    report = json.load(f)

iocs = report['analysis']['iocs']

# Экспорт IP адресов для фаервола
with open('block_ips.txt', 'w') as f:
    for ip in iocs['ip_addresses']:
        f.write(f'{ip}\n')

# Экспорт доменов для DNS фильтра
with open('block_domains.txt', 'w') as f:
    for domain in iocs['domains']:
        f.write(f'{domain}\n')
```

### Интеграция с YARA

```bash
# Создайте правила в rules/custom.yar
python -c "
import yara
rules = yara.compile('rules/custom.yar')
matches = rules.match('samples/suspicious.exe')
for match in matches:
    print(f'Правило: {match.rule}')
"
```

## Советы по использованию

1. **Всегда используйте изолированную среду** - ВМ или контейнер
2. **Настраивайте таймаут** в зависимости от типа файла
3. **Сохраняйте отчеты** для последующего анализа
4. **Обновляйте YARA правила** регулярно
5. **Сравнивайте отчеты** для похожих образцов

## Типичные проблемы и решения

| Проблема | Решение |
|----------|---------|
| Нет событий в отчете | Увеличьте таймаут, проверьте права |
| Ошибка компиляции агента | Установите Visual Studio Build Tools |
| Ложные срабатывания | Настройте пороги в analyzer.py |
