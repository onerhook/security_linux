"""
RedSand - Модуль статического анализа
Анализирует файл до запуска: хеши, строки, PE-заголовки, YARA
"""

import hashlib
import pefile
import yara
import re
from pathlib import Path
from typing import Dict, List, Any


class StaticAnalyzer:
    """Статический анализ образцов"""
    
    def __init__(self, yara_rules_path: str = "rules"):
        self.yara_rules = self._load_yara_rules(yara_rules_path)
        
    def _load_yara_rules(self, path: str) -> Any:
        """Загрузка YARA правил"""
        try:
            rules_path = Path(path)
            if rules_path.exists():
                # Компиляция всех .yar файлов в папке
                rule_files = [str(f) for f in rules_path.glob("*.yar")]
                if rule_files:
                    return yara.compile(filepaths={str(f): str(f) for f in rule_files})
        except Exception as e:
            print(f"[!] Ошибка загрузки YARA правил: {e}")
        return None
    
    def analyze(self, file_path: str) -> Dict[str, Any]:
        """Полный статический анализ файла"""
        result = {
            "file_info": self._get_file_info(file_path),
            "hashes": self._calculate_hashes(file_path),
            "pe_info": self._analyze_pe(file_path),
            "strings": self._extract_strings(file_path),
            "yara_matches": self._scan_yara(file_path)
        }
        return result
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Базовая информация о файле"""
        path = Path(file_path)
        return {
            "name": path.name,
            "size": path.stat().st_size,
            "extension": path.suffix,
            "path": str(path.absolute())
        }
    
    def _calculate_hashes(self, file_path: str) -> Dict[str, str]:
        """Вычисление хешей файла"""
        hashes = {}
        with open(file_path, "rb") as f:
            data = f.read()
            hashes["md5"] = hashlib.md5(data).hexdigest()
            hashes["sha1"] = hashlib.sha1(data).hexdigest()
            hashes["sha256"] = hashlib.sha256(data).hexdigest()
        return hashes
    
    def _analyze_pe(self, file_path: str) -> Dict[str, Any]:
        """Анализ PE-заголовков (только для Windows exe/dll)"""
        pe_info = {"is_pe": False}
        
        try:
            pe = pefile.PE(file_path)
            pe_info["is_pe"] = True
            pe_info["machine"] = pefile.MACHINE_TYPE[pe.FILE_HEADER.Machine].replace("IMAGE_FILE_MACHINE_", "")
            pe_info["subsystem"] = pefile.SUBSYSTEM_TYPE[pe.OPTIONAL_HEADER.Magic].replace("IMAGE_SUBSYSTEM_", "") if hasattr(pe.OPTIONAL_HEADER, 'Magic') else "Unknown"
            
            # Импорты функций
            imports = []
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    for imp in entry.imports:
                        if imp.name:
                            imports.append(imp.name.decode())
            pe_info["imports"] = list(set(imports))[:50]  # Первые 50 уникальных
            
            # Экспорты (для DLL)
            exports = []
            if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
                for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                    if exp.name:
                        exports.append(exp.name.decode())
            pe_info["exports"] = exports[:20]
            
            # Секции
            sections = []
            for section in pe.sections:
                sections.append({
                    "name": section.Name.decode().strip('\x00'),
                    "virtual_size": section.Misc_VirtualSize,
                    "raw_size": section.SizeOfRawData,
                    "entropy": self._calculate_entropy(section.get_data())
                })
            pe_info["sections"] = sections
            
            # Подозрительные флаги
            pe_info["suspicious_flags"] = []
            if any(s['entropy'] > 7.0 for s in sections):
                pe_info["suspicious_flags"].append("Высокая энтропия секций (возможно зашифровано/упаковано)")
            if ".rsrc" in [s['name'] for s in sections]:
                rsrc = next((s for s in sections if s['name'] == '.rsrc'), None)
                if rsrc and rsrc['raw_size'] > 1000000:
                    pe_info["suspicious_flags"].append("Большой размер ресурсов (возможно внедренный payload)")
                    
        except pefile.PEFormatError:
            pe_info["error"] = "Не является корректным PE файлом"
        except Exception as e:
            pe_info["error"] = str(e)
            
        return pe_info
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Расчет энтропии Шеннона"""
        if not data:
            return 0.0
        
        entropy = 0.0
        byte_counts = {}
        for byte in data:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1
        
        data_len = len(data)
        for count in byte_counts.values():
            if count > 0:
                probability = count / data_len
                entropy -= probability * (probability and (probability * 0.69314718056) or 0) / 0.69314718056  # log2
        
        return round(entropy, 2)
    
    def _extract_strings(self, file_path: str, min_length: int = 4) -> Dict[str, List[str]]:
        """Извлечение строк из файла"""
        strings = {"ascii": [], "unicode": []}
        
        try:
            with open(file_path, "rb") as f:
                data = f.read()
                
            # ASCII строки
            ascii_pattern = rb'[\x20-\x7e]{' + str(min_length).encode() + rb',}'
            strings["ascii"] = [s.decode('ascii', errors='ignore') for s in re.findall(ascii_pattern, data)][:100]
            
            # Unicode строки
            unicode_pattern = rb'(?:[\x20-\x7e]\x00){' + str(min_length).encode() + rb',}'
            unicode_matches = re.findall(unicode_pattern, data)
            strings["unicode"] = [s.decode('utf-16-le', errors='ignore')[:100] for s in unicode_matches][:100]
            
        except Exception as e:
            strings["error"] = str(e)
            
        return strings
    
    def _scan_yara(self, file_path: str) -> List[Dict[str, Any]]:
        """Сканирование YARA правилами"""
        matches = []
        
        if self.yara_rules:
            try:
                results = self.yara_rules.match(file_path)
                for match in results:
                    matches.append({
                        "rule_name": match.rule,
                        "namespace": match.namespace,
                        "strings": [{"identifier": s.identifier, "offset": s.offset, "data": s.bytes.decode('utf-8', errors='ignore')} for s in match.strings]
                    })
            except Exception as e:
                matches.append({"error": str(e)})
                
        return matches


if __name__ == "__main__":
    # Тестирование
    import sys
    if len(sys.argv) > 1:
        analyzer = StaticAnalyzer()
        result = analyzer.analyze(sys.argv[1])
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Использование: python static_analyzer.py <файл>")
