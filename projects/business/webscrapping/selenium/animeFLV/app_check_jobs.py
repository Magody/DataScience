import os
import sys
# appending custom lib
path_lib = "/home/magody/programming/python/data_science/lib/scrapping"
sys.path.append(path_lib)

from ScrappingSelenium import check_jobs_complete  # type: ignore

path_jobs = os.path.join("jobs")

check_jobs_complete(path_jobs)