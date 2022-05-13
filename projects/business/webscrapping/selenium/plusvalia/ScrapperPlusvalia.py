# relevant packages & modules
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import requests
import urllib.request
import json
from tqdm import tqdm
# from tqdm.notebook import tqdm_notebook as tqdm
import undetected_chromedriver.v2 as uc


# Have powerfull bot protection, so we need undetected_chrome
class ScrapperPlusvalia:
    
    driver = None

    
    logged_in = False
    
    def __init__(self):
        
        self.driver = uc.Chrome(version_main=95)
        self.root = "https://www.plusvalia.com/inmuebles-ordenado-por-fechaonline-descendente"
        self.base = f"{self.root}-pagina-"
        self.driver.get(f"{self.base}1.html")

    def wait(self, t):
        time.sleep(t)
        
    def check_requisites(self):     
        return True
    
    def collect_urls(self,page_from,page_to,waiting_time=2)->list:
        
        if not self.check_requisites():
            return []

        urls = []
        repeated = []


        

        with open("urls.txt","a") as f:

            for page_i in tqdm(range(page_from, page_to+1)):

                url = f"{self.base}{page_i}.html"
                self.driver.get(url)
                
                chunk = self.driver.find_elements(By.XPATH, '//div[contains(@class,"list-card-container")]/div')
                
                for c in chunk:
                    if str(c.get_attribute("class")) != "ads-container":

                        url_item = str(c.get_attribute("data-to-posting"))
                        if url_item is None:
                            pass
                        else:
                            if url_item not in urls:
                                urls.append(url_item)
                            else:
                                repeated.append(f"Repeated inmuebles-ordenado-por-fechaonline-descendente-{page_i}.html:{url_item}")

                if len(urls) > 0:
                    f.write("\n".join(map(lambda s: f"https://www.plusvalia.com{s}", urls)))
                    urls = []

                current_url = self.driver.current_url


                if current_url == f"{self.root}.html":
                    page = 1
                else:
                    page = int(re.match(r"^https\:\/\/www\.plusvalia\.com\/[A-z\-]*(\d+)\.html$", current_url).groups()[0])

                if page == page_to:
                    break
                
                # next = self.driver.find_elements(By.CSS_SELECTOR, 'li.pag-go-next > a')[0]
                # next.click()
                self.wait(waiting_time)

        return urls, repeated
    
    def close(self):
        if self.driver:
            self.driver.close()
            
    def __del__(self):
        print("Closing...")
        self.close()