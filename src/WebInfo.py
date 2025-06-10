from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time


class WebInfo (object):
    
    def __init__(self, name=None, ivs=None):
        if type(name) != str and name != None:
            raise RuntimeError("Input name must be a string.")
        if type(ivs) != list and ivs != None:
            raise RuntimeError("Input IVs must be a list.")
        if ivs != None and len(ivs) != 3:
            raise RuntimeError("Must provide three IV fields.")
        
        try:
            # Initialize webdriver
            self.chrome_options = Options()
            #self.chrome_options.add_argument("--headless=new")
            self.chrome_options.add_argument("--disable-usb-discovery")
            self.chrome_options.add_argument("--disable-device-discovery-notifications")
            self.chrome_options.add_experimental_option("prefs", {
                "download.prompt_for_download": False,  # Auto-download files
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "profile.managed_default_content_settings.images": 2,  # 2 = block images
                "profile.managed_default_content_settings.media_stream": 2,  # block media streams (mic/cam)
                "profile.managed_default_content_settings.plugins": 2,  # block plugins (like flash)
                "profile.managed_default_content_settings.javascript": 1,  # 1 = allow JS (usually want on)
            })
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            self.pokemon_name = name
            if ivs != None:
                self.attack_iv = ivs[0]
                self.defense_iv = ivs[1]
                self.stamina_iv = ivs[2]
            else:
                self.attack_iv = None
                self.defense_iv = None
                self.stamina_iv = None
            self.ranks = {}

        except Exception as e:
            print(f"Unexpected error: {e}")

        finally:
            if 'self.driver' in locals():
                self.driver.quit()  # Ensures cleanup even if an error occurs


    def fetch_ivs(self):
        try:        
            self.driver.set_page_load_timeout(10)
            self.driver.get("https://goiv.app/")

        except Exception as e:
            print(f"Error loading page: {e}")
            return

        if self.enter_pokemon_name():
            self.enter_pokemon_ivs()
            self.collect_iv_rankings()
            return True
        else:
            return False
    

    def enter_pokemon_name(self):
        
        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/section/main/section[1]/label[1]/input'))
        )

        search_input.click() # focus the input box
        search_input.send_keys(self.pokemon_name)

        try:
            element = self.driver.find_element(By.XPATH, f"//*[text()='{self.pokemon_name}']")
        except NoSuchElementException:
            element = None

        return element != None
    
    def enter_pokemon_ivs(self):

        attack_select = self.driver.find_element(By.XPATH, '//*[@id="__next"]/section/main/section[1]/div[1]/label[1]/select')
        attack_select.click()
        attack_select.send_keys(self.attack_iv)

        defense_select = self.driver.find_element(By.XPATH, '//*[@id="__next"]/section/main/section[1]/div[1]/label[2]/select')
        defense_select.click()
        defense_select.send_keys(self.defense_iv)

        stamina_select = self.driver.find_element(By.XPATH, '//*[@id="__next"]/section/main/section[1]/div[1]/label[3]/select')
        stamina_select.click()
        stamina_select.send_keys(self.stamina_iv)

        body = self.driver.find_element(By.TAG_NAME, "body")
        body.click()


    def collect_iv_rankings(self):
        # Every pokemon should always have a rank
        great_league_top_row = self.driver.find_element(By.XPATH, 
            '//*[@id="__next"]/section/main/section[2]/div[1]/div/section/table/tbody/tr[1]/td[1]')
        self.ranks['Great League'] = great_league_top_row.text

        ultra_league_top_row = self.driver.find_element(By.XPATH, 
            '//*[@id="__next"]/section/main/section[2]/div[2]/div/section/table/tbody/tr[1]/td[1]')
        self.ranks['Ultra League'] = ultra_league_top_row.text

        master_league_top_row = self.driver.find_element(By.XPATH, 
            '//*[@id="__next"]/section/main/section[2]/div[3]/div/section/table/tbody/tr[1]/td[1]')
        self.ranks['Master League'] = master_league_top_row.text

        #print(self.great_league_rank, self.ultra_league_rank, self.master_league_rank)


    def stringify_ivs(self):
        return self.attack_iv + ", " + self.defense_iv + ", " + self.stamina_iv