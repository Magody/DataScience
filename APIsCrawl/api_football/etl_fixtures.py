import os
import sys
# appending custom lib
path_lib = "/home/magody/programming/python/data_science/lib"
sys.path.append(path_lib)

from utils_json import loadJSON
from MongoDatabase import MongoDatabase

class ETLSeasonLeague:
    
    def __init__(self, connectionDB:MongoDatabase) -> None:
        self.connectionDB = connectionDB
        
    def extract(self, sources:list, extra: dict)->dict:    
        data: dict = {"json": []}
        
        path_base_season_league = extra["json"]
        
        for source in sources:
            
            if source.endswith(".json"):
                fixtures_json = loadJSON(source)
                
                for fixture_resp in fixtures_json:
                    # print(fixture_resp)
                    fixture = fixture_resp["fixture"]
                    fixture_league = fixture_resp["league"]
                    fixture_teams = fixture_resp["teams"]
                    
                    home_id = fixture_teams["home"]["id"]
                    away_id = fixture_teams["away"]["id"]
                    
                    path_base_season_league_fixture = f"{path_base_season_league}fixtures_detail/{fixture['id']}/"
                                
                    if not os.path.isdir(path_base_season_league_fixture):
                        print(f"{path_base_season_league_fixture} doesn't exists. Forcing continue, probably is a lack of requests to api.")        
                        continue
                                
                    statistics = loadJSON(f"{path_base_season_league_fixture}statistics.json")
                    home_statistics = {}
                    away_statistics = {}
                    if len(statistics) == 2:
                        statistics0 = statistics[0]
                        statistics1 = statistics[1]
                        
                        if statistics0["team"]["id"] == home_id:
                            home_statistics = statistics0["statistics"]
                            away_statistics = statistics1["statistics"]
                        else:
                            home_statistics = statistics1["statistics"]
                            away_statistics = statistics0["statistics"]
                    
                        
                    lineups = loadJSON(f"{path_base_season_league_fixture}lineups.json")
                    home_lineups = {}
                    away_lineups = {}
                    if len(lineups) == 2:
                        lineups0 = lineups[0]
                        lineups1 = lineups[1]
                        
                        if lineups0["team"]["id"] == home_id:
                            del lineups0["team"]
                            del lineups1["team"]
                            home_lineups = lineups0
                            away_lineups = lineups1
                        else:
                            del lineups0["team"]
                            del lineups1["team"]
                            home_lineups = lineups1
                            away_lineups = lineups0
                    
                    statistics_players = loadJSON(f"{path_base_season_league_fixture}statistics_players.json")
                    home_statistics_players = {}
                    away_statistics_players = {}
                    if len(statistics) == 2:
                        statistics_players0 = statistics_players[0]
                        statistics_players1 = statistics_players[1]
                        
                        if statistics_players0["team"]["id"] == home_id:
                            home_statistics_players = statistics_players0["players"]
                            away_statistics_players = statistics_players1["players"]
                        else:
                            home_statistics_players = statistics_players1["players"]
                            away_statistics_players = statistics_players0["players"]
                    
                    events = loadJSON(f"{path_base_season_league_fixture}events.json")
                    
                    data["json"].append({
                        "id": fixture["id"],
                        "team_home": fixture_teams["home"],
                        "team_away": fixture_teams["away"],
                        "league_id": fixture_league["id"],
                        "season_id": fixture_league["season"],
                        "referee": fixture["referee"],
                        "venue_id": fixture["venue"]["id"],
                        "timezone": fixture["timezone"],
                        "datetime": fixture["date"],
                        "timestamp": fixture["timestamp"],
                        "periods": fixture["periods"],
                        "status": fixture["status"],
                        "goals": fixture_resp["goals"],
                        "score": fixture_resp["score"],
                        "home_statistics": home_statistics,
                        "away_statistics": away_statistics,
                        "home_lineups": home_lineups,
                        "away_lineups": away_lineups,
                        "home_statistics_players": home_statistics_players,
                        "away_statistics_players": away_statistics_players,
                        "events": events
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
                if not self.connectionDB.db.fixtures.count_documents({ key_unique: identifier }, limit = 1):
                    self.connectionDB.insertDocument("fixtures", data)
                    count_loaded += 1
                else:
                    print(f"{key_unique} {identifier} already exists")
            except:
                print(f"Invalid key {key_unique}")
        count_total += 1
                
        return {"count_loaded": count_loaded, "count_total": count_total}
    
    def etl(self, sources:list, extra:dict, key_unique:str)->dict:
        
        extracted:dict = self.extract(sources, extra)
        transformed:list = self.transform(extracted)
        loaded:dict = self.load(transformed, key_unique)
        return loaded

def main():
    """
    OS ENV:
    - PATH_DATA_API_FOOTBALL
    Container running:
    $ docker run -p 27040:27017 -v /home/magody/programming/python/data_science/containers_data/mongodb:/data/db --name mongodb_datascience -it mongo
    
    
    source load_mongo_dev_vars.sh 
    python etl_fixtures.py <season> <league> <optional:key_unique>
    python etl_fixtures.py 2022 34 id
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

    sources:list = [
        f"{path_base_season_league}fixtures_info.json"
    ]
    extra:dict = {"json": path_base_season_league}

    ENV_MODE = os.environ.get("MODE", "production")
    ENV_MONGODB_USER = os.environ.get("MONGODB_USER")
    ENV_MONGODB_PASS = os.environ.get("MONGODB_PASS")
    ENV_MONGODB_HOST = os.environ.get("MONGODB_HOST")
    ENV_MONGODB_PORT = os.environ.get("MONGODB_PORT")
    ENV_MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE")
    mongoDB = MongoDatabase(ENV_MONGODB_DATABASE, f"mongodb://{ENV_MONGODB_USER}:{ENV_MONGODB_PASS}@{ENV_MONGODB_HOST}:{ENV_MONGODB_PORT}/{ENV_MONGODB_DATABASE}?retryWrites=true&w=majority")

    etl = ETLSeasonLeague(mongoDB)
    print(etl.etl(sources, extra, key_unique))

main()