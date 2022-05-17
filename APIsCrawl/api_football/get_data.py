import os
import sys
import time
from models.APIFootball import APIFootball

# appending custom lib
path_lib = "/home/magody/programming/python/data_science/lib"
sys.path.append(path_lib)

from utils_json import saveJSON, loadJSON # type: ignore

API_KEY = os.environ["KEY_API_FOOTBALL"]
path_data_base = os.environ["PATH_DATA_API_FOOTBALL"]

class ExtractSeasonLeague:

    def __init__(self, api:APIFootball, season:int, league:int, path_data_base:str, verbose_level:int=1) -> None:
        self.api = api
        self.season = season
        self.league = league
        self.verbose_level = verbose_level
        
        if path_data_base.endswith("/"):
            path_data_base = path_data_base[:-1]
        
        self.path_season_league = f"{path_data_base}/season/{season}/league/{league}/"

        if not os.path.isdir(self.path_season_league):
            os.mkdir(self.path_season_league)
            os.mkdir(f"{self.path_season_league}fixtures_details")
            os.mkdir(f"{self.path_season_league}team_stats")
            

        self.path_season_league_teams_info = f"{self.path_season_league}teams_info.json"
        self.path_season_league_fixtures_info = f"{self.path_season_league}fixtures_info.json"

    def log(self, msg:str)->None:
        if self.verbose_level > 0:
            print(msg)

    def checkApiCalls(self, API_COST):
        return self.api.requests_left >= API_COST

    def extractTeamsInfo(self)->list:
        
        API_COST = 1
        teams_info:list = []
        if not self.checkApiCalls(API_COST):
            self.log(f"Not enough left request to continue. Needed: {API_COST}")
            return teams_info
        
        
        if os.path.isfile(self.path_season_league_teams_info):
            self.log("Already exists a file with team info. Loading...")
            teams_info = loadJSON(self.path_season_league_teams_info)
            if len(teams_info) == 0:
                self.log("WARNING: teams info with ZERO data")
                
        else:
            # API CALL: 1
            self.teams_info = self.api.getTeamsInformation({"season":self.season, "league":self.league})["response"]
            saveJSON(self.path_season_league_teams_info, teams_info)

        return teams_info
    
    def extractTeamsStatistics(self)->dict:
        
        teams_info:dict = self.extractTeamsInfo()
    
        teams_statistics_all: dict = {}
        
        API_COST = len(teams_info)
        if not self.checkApiCalls(API_COST):
            self.log(f"Not enough left request to continue. Needed: {API_COST}")
            return teams_statistics_all
        

        for team in teams_info:
            team_id = team["team"]["id"]
            
            path_team_statistic = f"{self.path_season_league}/team_stats/{team_id}.json"

            if os.path.isfile(path_team_statistic):
                self.log(f"Already exist file for team {team_id}. {path_team_statistic}")
                team_statistics = loadJSON(path_team_statistic)
            else:
                # os.mkdir(path_team_statistic)
                team_statistics = self.api.getTeamsStatistics({"season":self.season, "league":self.league, "team":team_id})
                saveJSON(path_team_statistic, team_statistics["response"])
            teams_statistics_all[team_id] = team_statistics
                
               
        return teams_statistics_all

    def extractFixturesStatistics(self, start_index:int = 1, end_index:int = -1, time_wait:int = 61)->dict:

        all_results:dict = {}

        fixtures_season_league = None
        if os.path.isfile(self.path_season_league_fixtures_info):
            fixtures_season_league = loadJSON(self.path_season_league_fixtures_info)
        else:
            # API CALLS: 1
            API_COST = 1
            if not self.checkApiCalls(API_COST):
                self.log(f"Not enough left request to continue. Needed: {API_COST}")
                return {}
        
            fixtures_season_league = self.api.getFixtures({"season":self.season, "league":self.league})["response"]
            saveJSON(self.path_season_league_fixtures_info, fixtures_season_league)

        all_results["fixtures_season_league"] = fixtures_season_league
        all_results["fixtures"] = {}
        
        self.log(f"Total fixtures: {len(fixtures_season_league)}")
        
        if end_index == -1:
            end_index:int = len(fixtures_season_league)
        

        for i in range(start_index, end_index + 1):
            fixture_id = fixtures_season_league[i]["fixture"]["id"] # in 4 for 2022 - 34
            
            self.log(f"Processing: {i} index. Fixture: {fixture_id}")
            if self.api.requests_left <= 5:
                self.log(f"PENDING START FROM index {i} to {len(fixtures_season_league)}")
                break
            path_fixture = f"{self.path_season_league}/fixtures_detail/{fixture_id}/"

            if os.path.isdir(path_fixture):
                self.log("Already exist dir of fixtures")
                fixture_statistics = loadJSON(f"{path_fixture}statistics.json")
                fixture_events = loadJSON(f"{path_fixture}events.json")
                fixture_lineups = loadJSON(f"{path_fixture}lineups.json")
                fixture_statistics_players = loadJSON(f"{path_fixture}statistics_players.json")                
            else:
                # 4 API Calls
                os.mkdir(path_fixture)
                fixture_statistics = self.api.getFixtureStats({"fixture": fixture_id})
                saveJSON(f"{path_fixture}statistics.json", fixture_statistics["response"])
                
                fixture_events = self.api.getFixtureEvents({"fixture": fixture_id})
                saveJSON(f"{path_fixture}events.json", fixture_events["response"])
                
                fixture_lineups = self.api.getFixtureLineups({"fixture": fixture_id})
                saveJSON(f"{path_fixture}lineups.json", fixture_lineups["response"])
                
                fixture_statistics_players = self.api.getFixturePlayerStatistics({"fixture": fixture_id})
                saveJSON(f"{path_fixture}statistics_players.json", fixture_statistics_players["response"])
            
            if len(fixture_statistics) == 0 or len(fixture_statistics) == 0 or len(fixture_statistics) == 0 or len(fixture_statistics) == 0:
                self.log(f"WARNING: Fixture {fixture_id} is empty. Problems with API calls?")
            
            all_results["fixtures"][fixture_id] = dict()
            all_results["fixtures"][fixture_id]["fixture_statistics"] = fixture_statistics
            all_results["fixtures"][fixture_id]["fixture_events"] = fixture_events
            all_results["fixtures"][fixture_id]["fixture_lineups"] = fixture_lineups
            all_results["fixtures"][fixture_id]["fixture_statistics_players"] = fixture_statistics_players
            
            if i < end_index:
                time.sleep(time_wait)
        
        return all_results


def main():
    """Gets data from specific season league. Wait time strongly recommended is 61. 
    Indexes are only to restore pending queries. If there is not state to recover begin from 1 to 100000.
    
    OS ENV (load_keys.sh may help):
    - export KEY_API_FOOTBALL="asfdsgsgshs"
    - export PATH_DATA_API_FOOTBALL="/home/magody/programming/python/data_science/data/api_football"
    
    Usage Example:
    python get_data.py <season> <league> <index_begin> <index_end> <time_wait> <verbose_level>
    python get_data.py 2022 34 21 24 61 1
    """
    
    args:list = sys.argv
    if len(args) < 7:
        print("NOT ENOUGH ARGS", args)
        sys.exit(0)

    season = int(args[1])
    league = int(args[2])
    index_begin = int(args[3])
    index_end = int(args[4])
    time_wait = int(args[5])
    verbose_level = int(args[6])

    # os.environ["KEY_API_FOOTBALL"] = "asfaf"
    api = APIFootball(
        API_KEY,
        verbose_level=verbose_level
    )

    extractSeasonLeague:ExtractSeasonLeague = ExtractSeasonLeague(api, season, league, path_data_base)

    teamsStatistics: dict = extractSeasonLeague.extractTeamsStatistics()
    print(f"Teams number: {len(teamsStatistics)}")

    fixtures_played_total: int = 0
    for team_id, team_stats in teamsStatistics.items():
        fixtures_played: int = team_stats["fixtures"]["played"]["total"]
        print(f"Team:{team_id} played: {fixtures_played}")
        fixtures_played_total += fixtures_played
    print(f"Total fixtures for season league: {fixtures_played_total}")
    fixtures:dict = extractSeasonLeague.extractFixturesStatistics(index_begin, index_end, time_wait)
    print(f"Fixtures retrieved: ", len(fixtures["fixtures"]))


main()