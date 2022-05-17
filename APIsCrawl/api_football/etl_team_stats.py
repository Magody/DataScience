
import os
import sys
# appending custom lib
path_lib = "/home/magody/programming/python/data_science/lib"
sys.path.append(path_lib)

from utils_json import loadJSON
from MongoDatabase import MongoDatabase



class ETLTeamSeasonLeagueStatistics:
    
    def __init__(self, connectionDB:MongoDatabase, season_id:int, league_id:int) -> None:
        self.connectionDB = connectionDB
        self.season_id = season_id
        self.league_id = league_id
        
    def extract(self, sources:list)->dict:    
        data: dict = {"json": []}
                
        for source in sources:
            
            if source.endswith(".json"):
                team_stats = loadJSON(source)
                
                data["json"].append({
                    "team_id": team_stats["team"]["id"],
                    "team_name": team_stats["team"]["name"],
                    "league_id": team_stats["league"]["id"],
                    "league_name": team_stats["league"]["name"],
                    "season_id": team_stats["league"]["season"],
                    "fixtures_summary": team_stats["fixtures"],
                    "goals_summary": team_stats["goals"],
                    "biggest": team_stats["biggest"],
                    "clean_sheet": team_stats["clean_sheet"],
                    "failed_to_score": team_stats["failed_to_score"],
                    "penalty": team_stats["penalty"],
                    "lineups": team_stats["lineups"],
                    "cards": team_stats["cards"],
                })
                
        return data
    
    
    def transform(self, data:dict)->list:
        return data["json"]
            
    
    def load(self, data_transformed:list, key_unique:str = "id")->None:
        
        count_total = 0
        count_loaded = 0
        for data in data_transformed:
            try:
                identifier = data[key_unique]
                print(f"Loading {identifier}")
                if not self.connectionDB.db.team_statistics.count_documents({ key_unique: identifier, "season_id": self.season_id, "league_id": self.league_id }, limit = 1):
                    self.connectionDB.insertDocument("team_statistics", data)
                    count_loaded += 1
                else:
                    print(f"{key_unique} {identifier} already exists")
            except:
                print(f"Not found {key_unique} in {data.keys()}")
            count_total += 1
                
        return {"count_loaded": count_loaded, "count_total": count_total}
    
    def etl(self, sources:list, key_unique:str)->dict:
        
        extracted:dict = self.extract(sources)
        print(f"Extracted len: {len(extracted)}")
        transformed:list = self.transform(extracted)
        print(f"Transformed len: {len(transformed)}")
        loaded:dict = self.load(transformed, key_unique)
        return loaded

def main():
    """
    OS ENV:
    - PATH_DATA_API_FOOTBALL
    Container running:
    $ docker run -p 27040:27017 -v /home/magody/programming/python/data_science/containers_data/mongodb:/data/db --name mongodb_datascience -it mongo
    
    
    source load_mongo_dev_vars.sh 
    python etl_team_stats.py <season> <league> <optional:key_unique>
    python etl_team_stats.py 2022 34 team_id
    """
    args:list = sys.argv
    
    key_unique:str = "id"
    if len(args) >= 4:
        # print("Not enought args")
        # sys.exit(0)
        key_unique:str = args[3]

    season:int = int(args[1])
    league:int = int(args[2])
    
    path_data_base = os.environ.get("PATH_DATA_API_FOOTBALL", None)
    if path_data_base is None:
        print("SET PATH_DATA_API_FOOTBALL ENV")
        sys.exit(0)
    if path_data_base.endswith("/"):
        path_data_base = path_data_base[:-1]
    
    path_base_season_league = f"{path_data_base}/season/{season}/league/{league}/"
    path_base_season_league_team_stats = f"{path_base_season_league}team_stats/"
    team_files:list = os.listdir(path_base_season_league_team_stats)

    sources:list = []
    for file in team_files:
        sources.append(f"{path_base_season_league_team_stats}{file}")

    # print(sources)
    ENV_MODE = os.environ.get("MODE", "production")
    ENV_MONGODB_USER = os.environ.get("MONGODB_USER")
    ENV_MONGODB_PASS = os.environ.get("MONGODB_PASS")
    ENV_MONGODB_HOST = os.environ.get("MONGODB_HOST")
    ENV_MONGODB_PORT = os.environ.get("MONGODB_PORT")
    ENV_MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE")
    mongoDB = MongoDatabase(ENV_MONGODB_DATABASE, f"mongodb://{ENV_MONGODB_USER}:{ENV_MONGODB_PASS}@{ENV_MONGODB_HOST}:{ENV_MONGODB_PORT}/{ENV_MONGODB_DATABASE}?retryWrites=true&w=majority")

    etl = ETLTeamSeasonLeagueStatistics(mongoDB, season, league)
    print(etl.etl(sources, key_unique))

main()