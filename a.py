import asyncio
import sys
import logging

# MUST be at the very top to affect the entire process
if sys.platform == "win32":
    # ProactorEventLoop is required for subprocesses (needed by Playwright)
    if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from typing import List
from fastapi import FastAPI, Query
from c import organize_player_data, get_player_ids, get_player_stats
from api import synthesize_players_data
from database import upsert_data, start_session, summarize_all_stats, initialize_db
from fastapi.responses import JSONResponse
from logger_utils import log_error

app = FastAPI()

# Run DB initialization when the server starts
@app.on_event("startup")
async def startup_event():
    start_session()
    initialize_db()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/players")
async def input_players(player_names: List[str] = Query(..., description="Player name")):
    try:
        # 1. Fetch data
        uncurated_players = await synthesize_players_data(player_names)
        gen = await organize_player_data(uncurated_players, get_player_ids, get_player_stats)

        scouted_results = []
        re_use_keys = []
        errors = []

        from c import which_stats_to_show

        # 2. Write to DB
        async for player, league_name, stats_data, player_position in gen:
            re_use_keys.append((player, league_name, player_position))
            try:
                await upsert_data(player, league_name, stats_data, player_position)
            except Exception as e:
                log_error(f"DB Write Error for {player}")
                errors.append(f"Write error: {player}")

        # 3. Summary logic (Best Effort)
        try:
            await summarize_all_stats()
        except Exception as e:
            log_error("Summary logic failed")
            errors.append("Summary error")

        # 4. Read from DB (Include All Leagues)
        # Unique players to avoid duplicate 'All Leagues' if a player has multiple rows
        unique_players = list(set([(p, pos) for p, l, pos in re_use_keys]))
        
        # Add All Leagues to the fetch list
        fetch_list = re_use_keys + [(p, 'All Leagues', pos) for p, pos in unique_players]

        for player, league_name, player_position in fetch_list:
            try:
                async for p_name, p_league, p_stats, p_pos in which_stats_to_show(player, league_name, {}, player_position):
                    scouted_results.append({
                        "name": p_name,
                        "league": p_league,
                        "position": p_pos,
                        "stats": p_stats
                    })
            except Exception as e:
                log_error(f"DB Read Error for {player}")
                errors.append(f"Read error: {player}")

        response = {"scouted_players": scouted_results}
        if errors:
            response["errors"] = errors

        return response

    except Exception as e:
        log_error("Fatal Error in /players endpoint")
        return JSONResponse(
            status_code=500,
            content={"message": str(e), "type": type(e).__name__}
        )
