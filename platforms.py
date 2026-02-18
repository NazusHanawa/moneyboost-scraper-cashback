import requests
import re

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from utils import MockResponse

class Platform:
    NAME = "platform_name"
    
    @classmethod
    def scrap_cashback(cls, url):
        soup = cls._get_soup(url)
        if not soup:
            return None
        
        description = cls._get_description(soup)
        cashback_values = None
        if description:
            cashback_values = cls._get_all_values(description)
        
        if cashback_values:
            global_value = min(cashback_values)
            max_value = max(cashback_values)
        else:
            global_value = cls._get_global_value(soup)
            max_value = global_value
        
        if global_value == None:
            return None
        
        cashback = {
            "global_value": global_value,
            "max_value": max_value,
            "description": description
        }
        return cashback
    
    @classmethod
    def _get_soup(cls, url):
        response = cls._get_response(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        return soup
    
    @classmethod
    def _get_response(cls, url):
        return cls._get_basic_response(url)
    
    @classmethod
    def _get_basic_response(cls, url):
        headers = cls._get_headers()
        response = requests.get(url, headers=headers, timeout=10)
        return response
        
    @classmethod
    def _get_js_response(cls, url):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                
                    context = browser.new_context(
                        user_agent = cls._get_headers()["User-Agent"]
                    )
                    
                    page = context.new_page()
                    try:
                        page.goto(url, wait_until="load", timeout=5000)
                    except Exception as e:
                        pass
                    
                    content = page.inner_html("body") 
                    
                    page.close()
                    context.close()
                finally:
                    browser.close()
            
            return MockResponse(content)
        except Exception as e:
            print(f"Playwright erro ({cls.NAME}): {e}")
            return None
        
    @classmethod
    def _get_headers(cls):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        return headers
        
    @classmethod
    def _get_global_value(cls, soup):        
        selector = cls._get_global_value_selector()
        container = soup.select_one(selector)
        if not container:
            return None
        
        value_str = container.get_text(strip=True)
        values = cls._get_all_values(value_str)
        if not values:
            return 0
        
        return max(values)

    @classmethod
    def _get_description(cls, soup):
        selector = cls._get_description_selector()
        element = soup.select_one(selector)
        if not element or len(element) < 2:
            return None
        
        description = element.text.replace("\n", " ").strip()
        return description
    
    @classmethod
    def _get_all_values(cls, text):                
        text_normalized = text.replace('\xa0', ' ').replace(' ', '')
        matches = re.findall(r"(\d+(?:[.,]\d+)?)%", text_normalized)
    
        if not matches:
            return None

        values = [float(v.replace(',', '.')) for v in matches]
        
        return values
    
    @classmethod
    def _get_global_value_selector(cls):
        pass
        
    @classmethod
    def _get_description_selector(cls):
        pass

class Meliuz(Platform):
    NAME = "Meliuz"
    
    @classmethod
    def _get_global_value_selector(cls):
        return "body > div.container > main > div.hero-sec > div.hero-sec__redirect-btn > button > span"
    
    @classmethod
    def _get_description_selector(cls):
        return "body > div.container > main > div.hero-sec > nav > ul"

class Cuponomia(Platform):
    NAME = "Cuponomia"
    
    @classmethod
    def _get_global_value_selector(cls):
        return "#middle > div.store_header.js-storeHeader.container > div.store_header__logo.js-storeLogo"
    
    @classmethod
    def _get_description_selector(cls):
        return "#middle > div.store_header.js-storeHeader.container > div.cashback_segmentation > div"

    
class InterShop(Platform):
    NAME = "Inter Shop"
    
    @classmethod
    def _get_global_value_selector(cls):
        return "#__next > div.sc-bc01fd02-0.dvlkhZ > main > div > div > div:nth-child(2) > div.sc-fcf37f6b-0.hXNZkk > div.sc-5b99e04-3.gOqLxR > h1"
    
    @classmethod
    def _get_description_selector(cls):
        return "#__next > div.sc-bc01fd02-0.dvlkhZ > main > div > div > div:nth-child(2) > div.sc-fcf37f6b-0.fJpdTU > div.PromotionsListExtendedstyles__PromotionsListExtended-sc-8lmt3y-0.fYhhPv.sc-5b99e04-12.jfXeBs"
    
    @classmethod
    def _get_description(cls, soup):
        selector = cls._get_description_selector()
        container = soup.select_one(selector)
        if not container:
            return None

        elements = container.select("h3, [data-testid='description']")
        description = " ".join([element.get_text(strip=True) for element in elements])
        return description

class Zoom(Platform):
    NAME = "Zoom"
    
    @classmethod
    def _get_global_value_selector(cls):
        return "body > main > div.Template_FullContainer__SoAKR > div > div > aside > div > div > div.PartnerBrand_PartnerBrand__1AXmN > div.PartnerBrand_Header__gXloa > div > div > p.Text_Text__ARJdp.Text_MobileHeadingXs__Gvbn0"
    
    @classmethod
    def _get_description_selector(cls):
        return "body > main > div.Template_FullContainer__SoAKR > div > div > aside > div > div > div.PartnerBrand_PartnerBrand__1AXmN > div.CashbackSummary_CashbackSummary__bp5Bt > details > dl"

class MyCashBack(Platform):
    NAME = "MyCashBack"
    
    @classmethod
    def _get_global_value_selector(cls):
        return "#retailerPage > div:nth-child(1) > div.container.p-0.bg-white.elevated > div.row.m-0.ret-header-first-row > div.py-3.col-12.col-md-4.retailer-header-logo-cont.d-flex.justify-content-center.align-items-center.flex-column.h-100 > h3"
    
    @classmethod
    def _get_description_selector(cls):
        return "#retailerPage > div:nth-child(1) > div.ret > div > div > div.col-md-4.col-12 > div"

    @classmethod
    def _get_description(cls, soup):
        selector = cls._get_description_selector()
        element = soup.select_one(selector)
        if not element:
            return None

        lines = []

        for text in element.stripped_strings:
            clean_text = text.replace('\xa0', ' ').strip()
            
            if not clean_text:
                continue
            if clean_text.startswith('*'):
                continue
                
            lines.append(clean_text)
            
        description = " ".join(lines).strip()
        
        return description if len(description) > 2 else None

class Letyshops(Platform):
    NAME = "Letyshops"
    
    @classmethod
    def _get_global_value_selector(cls):
        return "#app > div.min-h-screen.flex.flex-col.justify-between > div.flex-1 > div:nth-child(3) > div > div.col-span-1 > div > div.b-shop-teaser.max-w-full > div.b-shop-teaser__shop-info > div.b-shop-teaser__cash-value > div.b-shop-teaser__cash-value-row"
    
    @classmethod
    def _get_description_selector(cls):
        return "#b-shop-content > div.pb-6 > div:nth-child(4)"
    
class Opera(Platform):
    NAME = "Opera"
    
    @classmethod
    def _get_global_value_selector(cls):
        return "span.undefined.hover-line__element"
    
    @classmethod
    def _get_description_selector(cls):
        return "#category-section > div"

    @classmethod
    def _get_response(cls, url):    
        return cls._get_js_response(url)

    @classmethod
    def _get_description(cls, soup):
        selector = cls._get_description_selector()
        container = soup.select_one(selector)
        if not container:
            return None

        elements = container.select("div.font-weight--bold, a")
        description = " ".join([element.get_text(strip=True) for element in elements])
        return description

class Megabonus(Platform):
    NAME = "Megabonus"
    
    @classmethod
    def _get_global_value_selector(cls):
        return "#shopApp > div.shop-page > div.row-section.row-section--shop.big-screen.shop-content-area > section.main-panel > div.shop-card > div > div > div > p.percents"
    
    @classmethod
    def _get_description_selector(cls):
        return "#shopApp > div.shop-page > div.row-section.row-section--shop.big-screen.shop-content-area > section.content-panel > div.left-main-panel > div.cashback-cards > div.cashback-category.bordered-card"

platforms_list = [
    Meliuz,
    Cuponomia,
    InterShop,
    Zoom,
    MyCashBack,
    Letyshops,
    Opera,
    Megabonus
]

if __name__ == "__main__":
    urls = [
        "https://www.mycashback.com.br/retailer/shein",
    ]
    for url in urls:
        result = MyCashBack.scrap_cashback(url)
        print(f"\n{url} {result}")