from api import api
from sofascore_wrapper.player import Player
from api import synthesize_players_data
import asyncio
from models import PlayerSeasonsResponse, LeagueStatsResponse

async def get_player_ids(uncurated_players):
    curated_players = {}
    for player in uncurated_players:
        try:
            player_id = uncurated_players[player]["player"]["id"]
            player_position = uncurated_players[player]["player"]["position"]
            curated_players[player] = [player_id, player_position]
        except Exception as e:
            print(e)
            continue
    return curated_players
    
async def yield_instances(curated_players):
    for player in curated_players:
        try:
            player_id = curated_players[player][0]
            player_position = curated_players[player][1]
            player_instance = Player(api, player_id)
            yield player_instance, player_id, player, player_position 
        except Exception as e:
            print(e)
            continue
    
async def get_player_season(instance, player_id):
        seasons = await instance.player_seasons(player_id)
        seasons = PlayerSeasonsResponse(**seasons)
        for tournament in seasons.uniqueTournamentSeasons:
            try:
                for season in tournament.seasons:
                    try:
                        if season.year == "25/26":
                            league_id = tournament.uniqueTournament.id
                            league_name = tournament.uniqueTournament.name
                            season_id = season.id
                            yield league_id, league_name, season_id
                    except Exception as e:
                        print(e)
                        continue
            except Exception as e:
                print(e)
                continue

async def get_player_stats(curated_players):
    async for instance, player_id, player, player_position in yield_instances(curated_players):
        try:
            async for league_id, league_name, season_id in get_player_season(instance, player_id):
                try:
                    stats_response = await instance.league_stats(league_id, season_id)
                    stats_model = LeagueStatsResponse(**stats_response)
                    
                    # Basically just take all of the data from the api response and put it as the value to the key, and key is the name of the stat from the model
                    stats_data = stats_model.statistics.model_dump()
                    
                    # Add team name
                    stats_data["team_name"] = stats_model.team.name
                    
                    minutes = stats_data.get("minutesPlayed")

                    if minutes is None:
                        minutes = 0
                        
                    # Calculate per 90s

                    # We iterate over a static list of keys to avoid modifying dict while iterating if we were doing that, 
                    # but here we just iterate the original data items
                    for key, value in list(stats_data.items()):
                        # Skip non-numeric or None
                        if not isinstance(value, (int, float)) or value is None:
                            continue
                            
                        # Skip fields that don't make sense for per 90

                        # 1. Percentages and conversions
                        if "Percentage" in key or "Conversion" in key:
                            continue

                        # 2. Ratings (averages)
                        if "Rating" in key and key != "totalRating": # totalRating could be accumulative? Usually rating is average. 
                            # 'rating' is average. 'totalRating' might be sum of ratings? Let's check model. 
                            # Safe to assume simple 'rating' is avg.
                            continue
                        # 3. Time/meta stats
                        if key in ["minutesPlayed", "matchesStarted", "appearances", "id", "totwAppearances"]:
                             continue
                        
                        # Calculate
                        if minutes > 0:
                            stats_data[f"{key}_per_90"] = (value / minutes) * 90
                            
                        else:
                            stats_data[f"{key}_per_90"] = 0.0

                    yield player, league_name, stats_data, player_position

                except Exception as e:
                    print(f"Error processing stats for {player}: {e}")
                    continue
        except Exception as e:
            print(f"Error getting player instance for {player}: {e}")
            continue



async def organize_player_data(uncurated_players, gen_1, gen_2):
    curated_players = await gen_1(uncurated_players)
    gen = gen_2(curated_players)
    return gen

#generator yielding the stats to show for each player based on their position
async def which_stats_to_show(player, league_name, stats_data, player_position  ):
    #dictionary of positions and the stats that are relevant to them
    position_stats = {
        "G": ["goalsConceded", "saves", "cleanSheet", "penaltySave", "goalsConceded_per_90", "saves_per_90", "cleanSheet_per_90", "penaltySave_per_90"],
        "D": ["tackles", "interceptions", "blockedShots", "clearances", "aerialDuelsWon", "groundDuelsWon", "possessionWonAttThird", "tackles_per_90", "interceptions_per_90", "blockedShots_per_90", "clearances_per_90", "aerialDuelsWon_per_90", "groundDuelsWon_per_90"],
        "M": ["accuratePasses", "keyPasses", "assists", "successfulDribbles", "tackles", "interceptions", "accuratePasses_per_90", "keyPasses_per_90", "assists_per_90", "successfulDribbles_per_90", "tackles_per_90", "interceptions_per_90"],
        "F": ["goals", "expectedGoals", "assists", "shotsOnTarget", "successfulDribbles", "goals_per_90", "expectedGoals_per_90", "assists_per_90", "shotsOnTarget_per_90", "successfulDribbles_per_90"]
    }

    try:
        from database import select_player_stats
        if player_position in position_stats:
            # list comprehension of all the names of the stats matching the position
            stats_to_show = [stat for stat in position_stats[player_position]]
            stats_to_show = await select_player_stats(player, league_name,stats_to_show, player_position)
            yield player, league_name, stats_to_show, player_position
        else:
            yield player, league_name, {}, player_position
    except Exception as e:
        print(f"Filtering error: {e}")
 
    





