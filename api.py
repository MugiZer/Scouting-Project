import asyncio 
from sofascore_wrapper.api import SofascoreAPI
from sofascore_wrapper.search import Search
from sofascore_wrapper.player import Player
from sofascore_wrapper.team import Team
from sofascore_wrapper.league import League

api = SofascoreAPI()

#class structuring how each object constituting each player is defined as
class _Player:
    def __init__(self,api,player_name):
        self.player_name = player_name
        self.api = api
        self.search = Search(self.api, player_name)

    async def get_player_data(self):
        whole_unit = await self.search.search_all()
        player_id = whole_unit["results"][0]["entity"]["id"]
        player = Player(self.api, player_id)
        player_data = await player.get_player()
        return player_data
    
    async def get_player_id(self, dictionary):
        player_id = dictionary["results"][0]["entity"]["id"]
        return player_id

class _Players:
    def __init__(self,api,list_of_players):
        self.api = api
        self.list_of_players = list_of_players


async def synthesize_players_data(list_of_players):
    all_players = {}
    for p in list_of_players:
        player = _Player(api,p)
        data = await player.get_player_data()
        all_players[p] = data
    return all_players
    






    


    








