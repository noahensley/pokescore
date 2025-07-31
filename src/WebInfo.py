from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from WebUtils import silent_driver_startup


class WebInfo (object):
    
    def __init__(self, name=None, ivs=None):
        if type(name) != str and name != None:
            raise RuntimeError("Input name must be a string.")
        if type(ivs) != list and ivs != None:
            raise RuntimeError("Input IVs must be a list.")
        if ivs != None and len(ivs) != 3:
            raise RuntimeError("Must provide three IV fields.")
        
        print("[WebInfo] Initializing...")
        try:
            self.chrome_options = Options()
            self.chrome_options.add_argument("--headless=chrome")
            self.chrome_options.add_argument("--disable-extensions")   
            self.chrome_options.add_experimental_option("prefs", {
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            })
            
            self.driver = None
            silent_driver_startup(self.chrome_options, self.driver)       
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
            print("[WebInfo] ERROR")
            raise RuntimeError(f"Unable to initialize WebInfo: {e}")

        finally:
            if 'self.driver' in locals():
                self.driver.quit()  # Ensures cleanup even if an error occurs

        print("[WebInfo] DONE")


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
        Select(attack_select).select_by_visible_text(str(self.attack_iv))

        defense_select = self.driver.find_element(By.XPATH, '//*[@id="__next"]/section/main/section[1]/div[1]/label[2]/select')
        Select(defense_select).select_by_visible_text(str(self.defense_iv))

        stamina_select = self.driver.find_element(By.XPATH, '//*[@id="__next"]/section/main/section[1]/div[1]/label[3]/select')
        Select(stamina_select).select_by_visible_text(str(self.stamina_iv))

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


    def stringify_ivs(self):
        return self.attack_iv + ", " + self.defense_iv + ", " + self.stamina_iv