import http.client
from urllib.parse import urlencode
import json

class APIFootball:
    
    requests_left = 0
    
    def __init__(
        self, API_KEY:str, 
        HOST:str="v3.football.api-sports.io", 
        verbose_level:int=0,
        plan_calls_check:bool = True
        ):
        self.API_KEY = API_KEY
        self.HOST = HOST
        self.verbose_level = verbose_level
        self.plan_calls_check = plan_calls_check
        self.requests_left = self.getRequestsLeft()
        print(f"Requests left: {self.requests_left}. WARNING: from here the program will infer the requests left by discounting this variable. If you use multiple api instances please refresh the requests left ever X time")
        
    def log(self,msg:str):
        if self.verbose_level > 0:
            print(msg)
        
    def getHeaders(self)->dict:
        return {
            'x-rapidapi-host': self.HOST,
            'x-rapidapi-key': self.API_KEY
        }
        
    def makeRequest(self, endpoint:str, query_params:dict={}, call_api_cost:int=1)->dict:
        
        self.requests_left -= call_api_cost
            
        if self.plan_calls_check and call_api_cost:
            
            self.log(f"You have {self.requests_left} requests left")
            if self.requests_left < call_api_cost:
                self.log("YOU ARE AT LIMIT OF PLAN, CAN'T REQUEST NOTHING")
                return {}
        
        
        conn = http.client.HTTPSConnection(self.HOST)
        
        endpoint: str = f"/{endpoint}"
        if len(query_params) > 0:
            endpoint += f"/?{urlencode(query_params)}"
            
        self.log(f"Calling endpoint {endpoint}")
                
        conn.request("GET", endpoint, headers=self.getHeaders())
        res = conn.getresponse()
        data = res.read()
        result_utf8 = data.decode("utf-8")
        
        json_response: dict = {}
        if result_utf8 != "":
            json_response = json.loads(result_utf8)
        return json_response
        
        
    def getStatus(self)->dict:
        """
        Get account status.
        Call api cost: 0
        """
        return self.makeRequest("status", call_api_cost=0)
    
    def getRequestsLeft(self, safe_threshold:int = 1)->int:
        """
        Save threshold is a extra margin limit to avoid exceed plan
        Call api cost: 0
        """
        
        status: dict = self.getStatus()
        self.log(f"Status: {status}")
        response: dict = status["response"]
        requests: dict = response["requests"]
        return requests["limit_day"] - requests["current"] - safe_threshold

    def getCountries(self, query_params:dict={})->dict:
        """
        params: {"name": "Albania", "code": "AL"}, use one of them or nothing to get all
        Recommended Calls : 1 call per day.
        """
        return self.makeRequest("countries", query_params)
        
    def getLeagues(self, query_params:dict={})->dict:
        """
        Call api cost: 1
        params: * https://www.api-football.com/documentation-v3#operation/get-leagues.
            params sample: {"code": "EC"},{"type": "cup"}
        Recommended Calls : 1 call per hour.
        """
        return self.makeRequest("leagues", query_params)
        
    def getTeamsInformation(self, query_params:dict={})->dict:
        """
        Call api cost: 1
        params: * https://www.api-football.com/documentation-v3#operation/get-teams.
            params sample: {"country": "Ecuador"}, {"league": 11, "season": 2022}
        Recommended Calls : 1 call per day.
        """
        # some teams are national, other aren't
        return self.makeRequest("teams", query_params)
    
    def getTeamsStatistics(self, query_params:dict={})->dict:
        """
        Call api cost: 1
        params: * https://www.api-football.com/documentation-v3#operation/get-teams-statistics
            params sample: {"country": "Ecuador"}, {"season": 2022, "league": 34, "team": 2382}
        Recommended Calls : 1 call per day for the teams who have at least one fixture during the day otherwise 1 call per week.
        """
        return self.makeRequest("teams/statistics", query_params)
    
    def getTeamsSeasons(self, team_id:int)->dict:
        """
        Call api cost: 1
        params: team_id
            params sample: 2382
        Recommended Calls : 1 call per day.
        """
        return self.makeRequest("teams/seasons", {"team": team_id})
    
    def getFixtures(self, query_params:dict={})->dict:
        """
        Call api cost: 1
        doc: https://www.api-football.com/documentation-v3#operation/get-fixtures
        params: *
            params sample: {"season": 2022, "league": 34} (world cup conmebol sudamerica clasification, matches)
        Update Frequency : This endpoint is updated every 15 seconds.
        Recommended Calls : 1 call per minute for the leagues, teams, fixtures who have at least one fixture in progress otherwise 1 call per day.
        """
        return self.makeRequest("fixtures", query_params)
    
    def getFixtureStats(self, query_params:dict={})->dict:
        """
        Call api cost: 1
        doc: https://www.api-football.com/documentation-v3#operation/get-fixtures-statistics
        params: *
            params sample: {"fixture": 293580}
        Update Frequency : This endpoint is updated every minute.
        Recommended Calls : 1 call every minute for the teams or fixtures who have at least one fixture in progress otherwise 1 call per day.
        """
        return self.makeRequest("fixtures/statistics", query_params)
    
    def getFixtureEvents(self, query_params:dict={})->dict:
        """
        Call api cost: 1
        doc: https://www.api-football.com/documentation-v3#operation/get-fixtures-events
        params: *
            params sample: {"fixture": 293580}
        Update Frequency : This endpoint is updated every 15 seconds.
        Recommended Calls : 1 call per minute for the fixtures in progress otherwise 1 call per day.
        You can also retrieve all the events of the fixtures in progress thanks to the endpoint fixtures?live=all
        """
        return self.makeRequest("fixtures/events", query_params)
    
    def getFixtureLineups(self, query_params:dict={})->dict:
        """
        Call api cost: 1
        Lineups are available between 20 and 40 minutes before the fixture when the competition covers this feature. You can check this with the endpoint leagues and the coverage field.
        
        doc: https://www.api-football.com/documentation-v3#operation/get-fixtures-lineups
        params: *
            params sample: {"fixture": 293580}
        Update Frequency : This endpoint is updated every 15 seconds.
        Update Frequency : This endpoint is updated every 15 minutes.

        Recommended Calls : 1 call every 15 minutes for the fixtures in progress otherwise 1 call per day.
        """
        return self.makeRequest("fixtures/lineups", query_params)
    
    def getFixturePlayerStatistics(self, query_params:dict={})->dict:
        """
        Call api cost: 1
        doc: https://www.api-football.com/documentation-v3#operation/get-fixtures-players
        params: *
            params sample: {"fixture": 293580}
        Update Frequency : This endpoint is updated every minute.
        Recommended Calls : 1 call every minute for the fixtures in progress otherwise 1 call per day.
        """
        return self.makeRequest("fixtures/players", query_params)
    
    
    def getPlayerStatistics(self, query_params:dict={})->dict:
        """
        Call api cost: 1
        doc: https://www.api-football.com/documentation-v3#operation/get-players
        params: *
            params sample: {"season": 2022, "team": 2382, "league": 34}
        Update Frequency : This endpoint is updated several times a week.
        Recommended Calls : 1 call per day.
        """
        return self.makeRequest("players", query_params)
    
    def getOdds(self, query_params:dict={})->dict:
        """
        Call api cost: 1
        This endpoint uses a pagination system, you can navigate between the different pages thanks to the page parameter.
        Pagination : 10 results per page.
        We provide pre-match odds between 1 and 14 days before the fixture.
        We keep a 7-days history (The availability of odds may vary according to the leagues, seasons, fixtures and bookmakers)
        
        doc: https://www.api-football.com/documentation-v3#operation/get-odds
        params: *
            params sample: {"season": 2022, "league": 34}, {"fixture": 293580}
        Update Frequency : This endpoint is updated every day.
        Recommended Calls : 1 call per day.
        """
        return self.makeRequest("odds", query_params)
    
    
    def getBookmakers(self, query_params:dict={})->dict:
        """
        Call api cost: 1
        doc: https://www.api-football.com/documentation-v3#operation/get-bookmakers
        params: *
            params sample: {}
        Update Frequency : This endpoint is updated several times a week.
        Recommended Calls : 1 call per day.
        """
        return self.makeRequest("odds/bookmakers", query_params)
    
    
    def getBets(self, query_params:dict={})->dict:
        """
        Call api cost: 1
        doc: https://www.api-football.com/documentation-v3#operation/get-bets
        params: *
            params sample: {}, {"search": "under"}
        Update Frequency : This endpoint is updated several times a week.
        Recommended Calls : 1 call per day.
        """
        return self.makeRequest("odds/bets", query_params)
    
    
    # TODO: map other endpoints of API
