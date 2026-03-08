import asyncio
from database import start_session, upsert_data
from api import synthesize_players_data
from c import organize_player_data, get_player_ids, get_player_stats
import psycopg2

async def main():
    print("Starting session...")
    try:
        start_session()
    except Exception as e:
        print(f"Error starting session: {e}")
        return

    player_name = "Achraf Hakimi"
    print(f"Fetching data for {player_name}...")
    
    try:
        # Mocking what fastapi endpoint does
        uncurated_players = await synthesize_players_data([player_name])
        
        print("Organizing and upserting...")
        gen = await organize_player_data(uncurated_players, get_player_ids, get_player_stats)
        await upsert_data(gen)
        
        # Verify
        # We need to access the cursor. In database.py 'cr' is global.
        # But we can't import globals easily if they are not exposed properly or if module reloads.
        # Let's just create a new connection to check.
        
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="hamza158",
            dbname="mountakhab",
            port="5432"
        )
        cr = conn.cursor()
        
        cr.execute("SELECT name, minutes_played, goals, goals_per_90 FROM players WHERE name = %s", (player_name,))
        row = cr.fetchone()
        if row:
            print(f"Success! Data found: {row}")
            # Check if per 90 is correct
            minutes = row[1]
            goals = row[2]
            g_90 = row[3]
            if minutes > 0:
                calc_g_90 = (goals / minutes) * 90
                print(f"Calculated: {calc_g_90}, Stored: {g_90}")
        else:
            print("Failure! No data found.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
