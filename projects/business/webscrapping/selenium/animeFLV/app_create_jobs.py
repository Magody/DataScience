import sys
import os
import json

from ScrapperAnimeFLV import ScrapperAnimeFLV
# appending custom lib
path_lib = "/home/magody/programming/python/data_science/lib/scrapping"
sys.path.append(path_lib)

from ScrappingSelenium import SeleniumApp  # type: ignore


args = sys.argv
if len(args) <= 2:
    print("Insert job_batch_items and job_id_start argument")

job_batch_items = int(args[1])  # every job will have this amount of items
job_id_start = int(args[2])  # usually 1, but if is new scrapping over completed may need to be higher

f = open(".env.json", "r")
env = json.load(f)
f.close()

scrapper = ScrapperAnimeFLV("https://www.animeflv.net/")

selenium_app = SeleniumApp(scrapper, os.path.join("jobs"))
selenium_app.run(env["username_animeflv"], env["password_animeflv"])
del env["password_animeflv"]

selenium_app.create_jobs("https://www3.animeflv.net/browse?page=1", job_id_start, job_batch_items)
