# relevant packages & modules
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
from tqdm import tqdm  # from tqdm.notebook
import os
from IPython.display import clear_output
import undetected_chromedriver as uc

import sys
# appending custom lib
path_lib = "/home/magody/programming/python/data_science/lib/scrapping"
sys.path.append(path_lib)

from ScrappingSelenium import ScrapperBase  # type: ignore

import pandas as pd            


class ScrapperAnimeFLV(ScrapperBase):
    
    driver = None
    
    logged_in = False
    restarting = False
    
    cache = dict()
    
    stop = False
    
    def __init__(self, base_url, start=True, headless=False):
        super().__init__(base_url, start=True, headless=False)
        
    def wait(self, t):
        time.sleep(t)
        
    def check_requisites(self):
        
        if not self.logged_in:
            print("Please login first")
            return False        
        return True
    
    
    def prewarming(self, time_wait=2):
        element_add = self.driver.find_element(By.XPATH, '//div[contains(@style,"fixed")]')
        element_add_id = element_add.get_attribute("id")
        # print(element_add_id)
        self.driver.execute_script(f"document.getElementById('{element_add_id}').style.setProperty('display', 'none', 'important')");
        self.driver.find_element(By.CSS_SELECTOR, "div[class='AFixed']").click()
        self.driver.find_element(By.CSS_SELECTOR, "div[class='AFixed']").click()
        self.wait(time_wait)
        
        handles = self.driver.window_handles
        if len(handles) > 0:
            self.driver.switch_to.window(handles[1])
            self.driver.close()
            self.driver.switch_to.window(handles[0])
    
    def login(self, username, password):
        
        
        self.driver.find_element(By.CSS_SELECTOR, "div[class='AFixed']").click()
        self.wait(2)
        self.driver.find_element(By.CSS_SELECTOR, "div[class='Login']").click()
        self.wait(2)
        web_element_username = self.driver.find_element(By.CSS_SELECTOR, "input[name='email']")
        web_element_username.clear()
        web_element_username.send_keys(username)

        web_element_password = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        web_element_password.clear()
        web_element_password.send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.wait(3)
        self.driver.get("https://www3.animeflv.net/browse")
        self.logged_in = True
        print("Logged in!")
        
    def obtain_urls_items(self, url_begin="https://www3.animeflv.net/browse?page=1", early_stop=-1):
        
        if not self.check_requisites():
            return []
        
        queue = [url_begin]

        urls = []

        while len(queue) > 0:
            
            if early_stop != -1 :
                if len(urls) > early_stop:
                    break
                
            url_page = queue.pop()

            self.driver.get(url_page)
            self.wait(1)
            
            items_cards = self.driver.find_elements(By.XPATH, "//ul[contains(@class,'ListAnimes')]/li/article/a")
            for card in items_cards:
                urls.append(card.get_attribute("href"))

            try:
                element_next = self.driver.find_element(By.XPATH, "//ul[@class='pagination']/li[last()]")
                if element_next.get_attribute("class") != "disabled":
                    url_next = element_next.find_element(By.XPATH, "./a").get_attribute("href")
                    queue.append(url_next)
            except:
                print("Error at parsing next of", url_page)

        return urls


    def scrape_items(self, timers: dict(),
                     url_begin="https://www3.animeflv.net/browse?page=1", 
                     urls=None,
                     header=["title","title_alternative1","title_alternative2","rating","votes","type_serie","cover","state","followers","categories","related","episodes","description","reactions_like","reactions_funny","reactions_love","reactions_surprise","reactions_angry","reactions_sad","reactions_total"], early_stop=-1):
        
        df = pd.DataFrame(columns=header)
        
        if not self.check_requisites():
            return df
        
        try:
            urls_items = urls
            if urls is None:
                print("URLs CAN'T BE NONE")
                return df
                
            self.init_cache_items(df, urls_items)

            timer_load_page = timers.get("timer_load_page", 2)
            timer_load_disqus = timers.get("timer_load_disqus",1)
            timer_load_reactions = timers.get("timer_load_reactions",1)
            
            print(f"Beginning with {len(urls_items)}")
            for url in tqdm(urls_items):
                
                # initial
                self.driver.get(url)
                self.wait(timer_load_page)
                
                    
                title = self.extract_first(self.driver.find_elements(By.CSS_SELECTOR, "h1.Title"),default=url)
                title_alternatives = self.driver.find_elements(By.CSS_SELECTOR, "span.TxtAlt")
                title_alternatives_len = len(title_alternatives)
                title_alternative1 = "none"
                title_alternative2 = "none"

                if title_alternatives_len > 2:
                    title_alternative1 = title_alternatives[-2].text
                    title_alternative2 = title_alternatives[-1].text
                else:
                    index_alternative = 0
                    if title_alternatives_len > index_alternative:
                        title_alternative1 = title_alternatives[index_alternative].text
                        index_alternative += 1            
                    if title_alternatives_len > index_alternative:
                        title_alternative2 = title_alternatives[index_alternative].text
                        index_alternative += 1
                try:
                    rating = self.extract_first(self.driver.find_elements(By.CSS_SELECTOR, "span#votes_prmd"), mapping=float, default=0)
                    votes = self.extract_first(self.driver.find_elements(By.CSS_SELECTOR, "span#votes_nmbr"), mapping=int, default=0)
                    type_serie = self.extract_first(self.driver.find_elements(By.CSS_SELECTOR, "span.Type"))
                    cover = self.driver.find_elements(By.XPATH, "//div[@class='AnimeCover']/div/figure/img")
                    cover = "none" if len(cover) == 0 else cover[0].get_attribute("src")

                    state = self.extract_first(self.driver.find_elements(By.XPATH, '//p[contains(@class,"AnmStts")]/span'))
                    followers = self.extract_first(self.driver.find_elements(By.XPATH, '//div[contains(@class,"Title")]/span'), mapping=int, default=0)

                    categories = self.parse_multiple(self.driver.find_elements(By.XPATH, '//nav[contains(@class,"Nvgnrs")]/a'))

                    description = self.extract_first(self.driver.find_elements(By.XPATH, '//div[contains(@class,"Description")]/p')).replace("\n", "")
                    related = self.parse_multiple(self.driver.find_elements(By.XPATH, '//ul[@class="ListAnmRel"]/li'))

                    episodes = float(self.extract_first(self.driver.find_elements(By.XPATH, '//ul[@id="episodeList"]/li/a/p'), default="Episodio 0").split(" ")[1])

                
                except Exception as error1:
                    print("Error with basic parsing")
                    self.set_cache_url_error(url, error1)
                    continue
                
                holder_error = "Error in iframe"
                switched = False
                try:
                    errors_maximum = 10
                    errors_actual = 0
                    done = False
                    
                    
                    while not done and errors_actual < errors_maximum:
                        
                        try:
                            result = self.driver.execute_script('var element = document.querySelector("#disqus_thread"); if(element){element.scrollIntoView();return 1;}else{return 0}')
                    
                            if result == int(0):
                                state = "404 not found"
                                reactions_like = 0
                                reactions_funny = 0
                                reactions_love = 0
                                reactions_surprise = 0
                                reactions_angry = 0
                                reactions_sad = 0
                            else:
                                self.wait(timer_load_disqus)
                                frame_disqus = self.driver.find_elements(By.XPATH, '//div[@id="disqus_thread"]/iframe')[0]
                                self.driver.switch_to.frame(frame_disqus)
                                switched = True
                                reactions = self.driver.find_elements(By.XPATH, "//div[contains(@class,'reaction-item__enabled')]")
                                reactions[0].click()
                                
                                self.wait(timer_load_reactions)
                                # refresh in case no voted
                                reactions = self.driver.find_elements(By.XPATH, "//div[contains(@class,'reaction-item__enabled')]")
                                

                                def get_reactions_number(web_element_reaction):
                                    s = web_element_reaction.find_element(By.XPATH, ".//div[@class='reaction-item__votes']").text
                                    n = 0
                                    if len(s) > 0:
                                        n = int(s.strip())
                                    
                                    return n

                                reactions_like = get_reactions_number(reactions[0]) - 1
                                reactions_funny = get_reactions_number(reactions[1])
                                reactions_love = get_reactions_number(reactions[2])
                                reactions_surprise = get_reactions_number(reactions[3])
                                reactions_angry = get_reactions_number(reactions[4])
                                reactions_sad = get_reactions_number(reactions[5])
                                
                            done = True
                        except Exception as hold:
                            errors_actual += 1
                            holder_error = hold
                            print(f"Discuss error counter. {errors_actual} Will retry this...", end=". ")
                            if switched:
                                self.driver.switch_to.parent_frame()
                                switched = False
                          
                    if not done:
                        raise Exception()
                          
                    
                except:
                    print("Error with iframe parsing")
                    self.set_cache_url_error(url, holder_error)
                    continue
                """
                print(title, title_alternative1, title_alternative2)
                print(rating,votes,type_serie)
                print(cover, state, followers)
                print(categories)
                print(related, episodes)
                """

                item_dict = {
                    "title": title,
                    "title_alternative1": title_alternative1,
                    "title_alternative2": title_alternative2,
                    "rating": rating,
                    "votes": votes,
                    "type_serie": type_serie,
                    "cover": cover,
                    "state": state,
                    "followers": followers,
                    "categories": categories,
                    "related": related,
                    "episodes": episodes,
                    "description": description,
                    "reactions_like": reactions_like,
                    "reactions_funny": reactions_funny,
                    "reactions_love": reactions_love,
                    "reactions_surprise": reactions_surprise,
                    "reactions_angry": reactions_angry,
                    "reactions_sad": reactions_sad,
                    "reactions_total": reactions_like+reactions_funny+reactions_love+reactions_surprise+reactions_angry+reactions_sad,
                }
                
                self.update_cache(item_dict)
                
                if self.stop:
                    return self.cache["df"], False
                
            print("Finished!")
            return self.cache["df"], True
        except Exception as error:
            print("General Error:", error)
            return self.cache["df"], False


    def close(self):
        print("CLOSING OBJECT...")
        if self.driver:
            self.driver.close()
            
    def __del__(self):
        print("DESTRUCTING OBJECT")
        if not self.restarting:
            self.close()