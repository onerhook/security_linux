import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import re


class PromoMonitor:
    """Мониторинг промокодов и акций на различных сайтах"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_promos = set()  # Для отслеживания новых промокодов
        
    async def start(self):
        """Инициализация сессии"""
        self.session = aiohttp.ClientSession()
        
    async def stop(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
            
    async def check_promocodus(self) -> List[Dict[str, str]]:
        """Проверка промокодов на Promocodus.ru"""
        promos = []
        try:
            async with self.session.get("https://promocodus.ru/category/promokody-case-battle/") as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Ищем последние промокоды
                    articles = soup.find_all('article', class_='post')[:5]
                    
                    for article in articles:
                        title_elem = article.find('h2', class_='entry-title')
                        if title_elem:
                            title = title_elem.text.strip()
                            link_elem = article.find('a', href=True)
                            link = link_elem['href'] if link_elem else ""
                            
                            # Извлекаем сам промокод из заголовка или контента
                            promo_code = self._extract_promo_code(title)
                            
                            if promo_code:
                                promos.append({
                                    'source': 'Promocodus',
                                    'title': title,
                                    'code': promo_code,
                                    'link': link
                                })
        except Exception as e:
            print(f"Ошибка при проверке Promocodus: {e}")
        
        return promos
    
    async def check_casebattle_promo(self) -> List[Dict[str, str]]:
        """Проверка акций на CaseBattle"""
        promos = []
        try:
            async with self.session.get("https://casebattle.io/") as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Ищем баннеры с акциями
                    banners = soup.find_all('div', class_=re.compile(r'promo|banner|action', re.I))[:5]
                    
                    for banner in banners:
                        title_elem = banner.find(['h1', 'h2', 'h3', 'p'])
                        if title_elem:
                            title = title_elem.text.strip()
                            if title and len(title) > 5:  # Фильтр от пустых заголовков
                                promos.append({
                                    'source': 'CaseBattle',
                                    'title': title,
                                    'code': '',
                                    'link': 'https://casebattle.io/'
                                })
        except Exception as e:
            print(f"Ошибка при проверке CaseBattle: {e}")
        
        return promos
    
    async def check_steam_promo(self) -> List[Dict[str, str]]:
        """Проверка промо-акций Steam"""
        promos = []
        try:
            # Специальные предложения Steam
            async with self.session.get(
                "https://store.steampowered.com/specials",
                headers={'User-Agent': 'Mozilla/5.0'}
            ) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Ищем крупные акции
                    specials = soup.find_all('div', class_='special_offer')[:3]
                    
                    for special in specials:
                        title_elem = special.find('h4')
                        discount_elem = special.find('div', class_='discount_pct')
                        
                        if title_elem and discount_elem:
                            title = title_elem.text.strip()
                            discount = discount_elem.text.strip()
                            
                            promos.append({
                                'source': 'Steam Special',
                                'title': f"{title} - {discount}",
                                'code': '',
                                'link': 'https://store.steampowered.com/specials'
                            })
        except Exception as e:
            print(f"Ошибка при проверке Steam Promo: {e}")
        
        return promos
    
    def _extract_promo_code(self, text: str) -> str:
        """Извлечение промокода из текста"""
        # Паттерны для поиска промокодов
        patterns = [
            r'[A-Z0-9]{4,12}',  # Заглавные буквы и цифры 4-12 символов
            r'CASE[A-Z0-9]+',   # Коды начинающиеся с CASE
            r'BATTLE[A-Z0-9]+', # Коды начинающиеся с BATTLE
            r'FREE[A-Z0-9]+',   # Коды начинающиеся с FREE
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return ""
    
    async def get_new_promos(self) -> List[Dict[str, str]]:
        """Получение новых промокодов со всех источников"""
        all_promos = []
        
        # Проверяем все источники
        promocodus = await self.check_promocodus()
        casebattle = await self.check_casebattle_promo()
        steam = await self.check_steam_promo()
        
        all_promos.extend(promocodus)
        all_promos.extend(casebattle)
        all_promos.extend(steam)
        
        # Фильтруем только новые промокоды
        new_promos = []
        for promo in all_promos:
            promo_key = f"{promo['source']}:{promo['code'] or promo['title']}"
            if promo_key not in self.last_promos:
                self.last_promos.add(promo_key)
                new_promos.append(promo)
        
        # Ограничиваем размер множества
        if len(self.last_promos) > 100:
            self.last_promos = set(list(self.last_promos)[-50:])
        
        return new_promos


class SteamExtendedClient:
    """Расширенный клиент для Steam с дополнительными функциями"""
    
    def __init__(self, username: str, password: str, region: str = "KZ"):
        self.username = username
        self.password = password
        self.region = region
        self.authenticated = False
        
    async def get_inventory(self, app_id: int = 730) -> List[Dict[str, Any]]:
        """Получение инвентаря Steam (CS:GO по умолчанию)"""
        inventory = []
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://steamcommunity.com/id/{self.username}/inventory/json/{app_id}/2/"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success'):
                            inventory = data.get('rgInventory', [])
        except Exception as e:
            print(f"Ошибка получения инвентаря: {e}")
        
        return inventory
    
    async def get_trade_offers(self) -> List[Dict[str, Any]]:
        """Получение активных трейд-офферов"""
        offers = []
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://steamcommunity.com/id/{self.username}/tradeoffers/"
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'lxml')
                        
                        # Парсинг активных офферов
                        offer_elements = soup.find_all('div', class_='tradeoffer')
                        for offer in offer_elements:
                            offers.append({
                                'status': 'active',
                                'details': str(offer)[:200]  # Краткая информация
                            })
        except Exception as e:
            print(f"Ошибка получения трейд-офферов: {e}")
        
        return offers
    
    async def get_market_listings(self, search_query: str = "") -> List[Dict[str, Any]]:
        """Получение списков товаров на торговом рынке"""
        listings = []
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://steamcommunity.com/market/search/render/"
                params = {
                    'query': search_query,
                    'start': 0,
                    'count': 25,
                    'search_descriptions': 1,
                    'country': 'KZ',
                    'language': 'russian',
                    'currency': 398  # KZT
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        listings = data.get('results', [])
        except Exception as e:
            print(f"Ошибка получения рыночных списков: {e}")
        
        return listings
    
    async def get_account_level(self) -> int:
        """Получение уровня Steam аккаунта"""
        level = 0
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://steamcommunity.com/id/{self.username}/"
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'lxml')
                        
                        level_elem = soup.find('span', class_='friendPlayerLevelNum')
                        if level_elem:
                            level = int(level_elem.text.strip())
        except Exception as e:
            print(f"Ошибка получения уровня аккаунта: {e}")
        
        return level
