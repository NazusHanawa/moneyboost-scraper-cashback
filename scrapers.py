
from utils import timer

class CashbackScraper:
    def __init__(self, partnerships, platforms, cashbacks=None):
        self.partnerships = partnerships
        self.platforms = {"platform_name": "PlatformClass"}
        
        self.old_cashbacks = {}
        if cashbacks:
            self.old_cashbacks = cashbacks
        
        self.set_platforms(platforms)
    
    @timer
    def get_new_cashbacks(self):
        cashbacks = self.scrap_all_cashbacks()
        
        new_cashbacks = {}
        for partnership_id, cashback in cashbacks.items():
            if cashback == None:
                continue
            
            old_cashback = self.old_cashbacks.get(partnership_id)
            if old_cashback:
                if cashback:
                    same_global_value = old_cashback["global_value"] == cashback["global_value"]
                    same_max_value = old_cashback["max_value"] == cashback["max_value"]
                    if same_global_value and same_max_value:
                        continue

            new_cashbacks[partnership_id] = cashback.copy()
            
        self.old_cashbacks = cashbacks
        return new_cashbacks
        
    @timer
    def scrap_all_cashbacks(self):
        cashbacks = {}
        
        for partnership_id, partnership in self.partnerships.items():            
            cashback = self.scrap_cashback(partnership)
            if cashback:
                cashback["partnership_id"] = partnership_id
            cashbacks[partnership_id] = cashback
            
        return cashbacks
    
    def scrap_cashback(self, partnership):
        platform_name = partnership["platform_name"]
        
        if not partnership["partnership_url"]:
            return None

        platform = self._get_platform(platform_name)
        if not platform:
            return None
        
        cashback = platform.scrap_cashback(partnership["partnership_url"])
        return cashback
    
    def set_platforms(self, platforms): 
        self.platforms = {}
        for platform in platforms:
            platform_name = platform.NAME.lower()
            self.platforms[platform_name] = platform
    
    def _get_platform(self, store_name):
        store_name = store_name.lower()
        
        platform = self.platforms.get(store_name)
        if not platform:
            return None
        
        return platform
    
    
        
        
        
    
            

