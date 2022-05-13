import sys
import os
import json

from ScrapperAnimeFLV import ScrapperAnimeFLV
# appending custom lib
path_lib = "/home/magody/programming/python/data_science/lib/scrapping"
sys.path.append(path_lib)

from ScrappingSelenium import SeleniumApp  # type: ignore


args = sys.argv
if len(args) <= 1:
    print("Insert job_name argument")

job_name = args[1]

timers = {
            "timer_load_page": 2,
            "timer_load_disqus": 2,
            "timer_load_reactions": 1
        }
    

f = open(".env.json", "r")
env = json.load(f)
f.close()

scrapper = ScrapperAnimeFLV("https://www.animeflv.net/")

selenium_app = SeleniumApp(scrapper, os.path.join("jobs"))
selenium_app.run(env["username_animeflv"], env["password_animeflv"])
del env["password_animeflv"]

selenium_app.work(timers, job_name)
