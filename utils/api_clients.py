import aiohttp
from typing import Optional, Dict, Any, List
from steam.client import SteamClient
from steam.enums import EResult
from steam.webauth import WebAuth
import pyotp
import asyncio

class SteamClientHandler:
    """Клиент для работы с Steam API с использованием steamclient (Казахстан регион)"""
    
    def __init__(self, username: str, password: str, region: str = "KZ"):
        self.username = username
        self.password = password
        self.region = region
        self.steam_client = SteamClient()
        self.web_auth = WebAuth()
        self.authenticated = False
        self.shared_secret = None  # Нужно будет добавить из Steam Guard
        
    async def login(self, shared_secret: str = None) -> bool:
        """Авторизация в Steam с поддержкой Steam Guard"""
        try:
            self.shared_secret = shared_secret
            
            # Асинхронный запуск авторизации
            loop = asyncio.get_event_loop()
            
            def _login():
                try:
                    # Попытка входа через WebAuth
                    self.web_auth.login(
                        username=self.username,
                        password=self.password
                    )
                    
                    # Копируем куки в основной клиент
                    for cookie in self.web_auth.session.cookies:
                        self.steam_client._session.cookies.set_cookie(cookie)
                    
                    # Вход в Steam клиент
                    result = self.steam_client.login(self.username, self.password)
                    
                    if result == EResult.OK:
                        return True
                    
                    # Если требуется Steam Guard код
                    if result == EResult.AccountLogonDenied:
                        if self.shared_secret:
                            # Генерируем 2FA код
                            time_code = pyotp.TOTP(self.shared_secret).now()
                            result = self.steam_client.login(
                                self.username, 
                                self.password,
                                auth_code=time_code
                            )
                            return result == EResult.OK
                        else:
                            print("Требуется Steam Guard код. Укажите shared_secret.")
                            return False
                    
                    return False
                except Exception as e:
                    print(f"Ошибка при логине: {e}")
                    return False
            
            return await loop.run_in_executor(None, _login)
            
        except Exception as e:
            print(f"Ошибка авторизации: {e}")
            return False
    
    async def get_wishlist_deals(self) -> List[Dict[str, Any]]:
        """Получение скидок на товары из желаемого"""
        if not self.authenticated:
            # Пробуем войти без shared_secret сначала
            self.authenticated = await self.login()
        
        if not self.authenticated:
            print("Не удалось авторизоваться в Steam")
            return []
        
        try:
            # Получаем wishlist через веб-сессию
            wishlist_url = f"https://store.steampowered.com/wishlist/profiles/{self.username}/rendered/?language=russian&currency=398"
            
            async with aiohttp.ClientSession() as session:
                # Добавляем куки от авторизации
                cookies = {}
                for cookie in self.web_auth.session.cookies:
                    cookies[cookie.name] = cookie.value
                
                async with session.get(wishlist_url, cookies=cookies) as response:
                    if response.status == 200:
                        html = await response.text()
                        # Парсим HTML для получения информации о скидках
                        deals = self._parse_wishlist_html(html)
                        return deals
        except Exception as e:
            print(f"Ошибка получения желаемого: {e}")
        
        return []
    
    def _parse_wishlist_html(self, html: str) -> List[Dict[str, Any]]:
        """Парсинг HTML страницы желаемого"""
        from bs4 import BeautifulSoup
        
        deals = []
        soup = BeautifulSoup(html, 'lxml')
        
        # Ищем элементы wishlist
        wishlist_items = soup.find_all('div', class_='wishlist_row')
        
        for item in wishlist_items:
            try:
                title_elem = item.find('div', class_='title')
                title = title_elem.text.strip() if title_elem else "Unknown"
                
                # Проверяем наличие скидки
                discount_block = item.find('div', class_='discount_block')
                if discount_block and not discount_block.get('class', []).count('discount_block_empty'):
                    discount_pct = discount_block.find('div', class_='discount_pct')
                    final_price = discount_block.find('div', class_='discount_final_price')
                    
                    if discount_pct and final_price:
                        deals.append({
                            'name': title,
                            'discount': discount_pct.text.strip().replace('-', ''),
                            'price': final_price.text.strip(),
                            'original_price': discount_block.find('div', class_='discount_original_price').text.strip() if discount_block.find('div', class_='discount_original_price') else ''
                        })
            except Exception as e:
                continue
        
        return deals
    
    async def close(self):
        """Закрытие сессии"""
        try:
            self.steam_client.logout()
        except:
            pass


class HostVDSClient:
    """Клиент для работы с HostVDS API через панель управления"""
    
    def __init__(self, login: str, password: str, server_id: str = ""):
        self.login = login
        self.password = password
        self.server_id = server_id
        self.base_url = "https://my.hostvds.com"  # Панель управления
        self.session: Optional[aiohttp.ClientSession] = None
        self.authenticated = False
        
    async def login(self) -> bool:
        """Авторизация в панели HostVDS"""
        try:
            self.session = aiohttp.ClientSession()
            
            # POST запрос на авторизацию
            async with self.session.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "email": self.login,
                    "password": self.password
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.authenticated = True
                    self.token = data.get('token', '')
                    return True
        except Exception as e:
            print(f"Ошибка авторизации HostVDS: {e}")
        
        return False
    
    async def get_balance(self) -> Optional[float]:
        """Получение баланса счета"""
        if not self.authenticated:
            if not await self.login():
                return None
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            async with self.session.get(
                f"{self.base_url}/api/user/balance",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return float(data.get('balance', 0))
        except Exception as e:
            print(f"Ошибка получения баланса HostVDS: {e}")
        
        return None
    
    async def get_server_info(self) -> Optional[Dict[str, Any]]:
        """Получение информации о сервере"""
        if not self.authenticated:
            if not await self.login():
                return None
        
        if not self.server_id:
            print("Server ID не указан")
            return None
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            async with self.session.get(
                f"{self.base_url}/api/servers/{self.server_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"Ошибка получения информации о сервере: {e}")
        
        return None
    
    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
