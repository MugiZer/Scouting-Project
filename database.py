import psycopg2
from psycopg2.extras import RealDictCursor
from c import organize_player_data, get_player_ids, get_player_stats
from models import Statistics

#establish connection with database and start session
def start_session():

    global conn, cr

    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="hamza158",
        dbname="postgres",
        port="5432"
    )

    cr = conn.cursor()
    conn.autocommit = True

    cr.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'mountakhab'")

    exists = cr.fetchone()
    if not exists:
        cr.execute("CREATE DATABASE mountakhab")
        conn.commit()
    
    # Connect to the mountakhab database
    conn.close()
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="hamza158",
        dbname="mountakhab",
        port="5432"
    )
    cr = conn.cursor()
    conn.autocommit = True


# Create table dynamically
def initialize_db():
    global conn, cr
    # Drop table to ensure schema update
    cr.execute("DROP TABLE IF EXISTS players")
    
    create_query = "CREATE TABLE players (name VARCHAR(255), league_name VARCHAR(255), team_name VARCHAR(255), season_year VARCHAR(255), "
    
    # Get fields from model
    schema = Statistics.model_json_schema()
    props = schema['properties']
    
    columns = []
    
    for key, value in props.items():
        # SIMPLE FIX: If it looks like a number in the Pydantic definition, make it a number in SQL
        val_str = str(value).lower()
        if 'integer' in val_str:
            sql_type = "INT"
        elif 'number' in val_str:
            sql_type = "FLOAT"
        elif 'boolean' in val_str:
            sql_type = "BOOLEAN"
        else:
            sql_type = "VARCHAR(255)"
            
        columns.append(f"{key} {sql_type}")
        
        # Add per 90 rule
        is_numeric = sql_type in ["INT", "FLOAT"]
        is_excluded = False
        
        # 1. Percentages and conversions
        if "Percentage" in key or "Conversion" in key:
            is_excluded = True
        # 2. Ratings
        if "Rating" in key and key != "totalRating":
            is_excluded = True
        # 3. Time/meta
        if key in ["minutesPlayed", "matchesStarted", "appearances", "id", "totwAppearances"]:
            is_excluded = True
            
        if is_numeric and not is_excluded:
            columns.append(f"{key}_per_90 FLOAT")

    create_query += ", ".join(columns)
    create_query += ", player_position VARCHAR(255), UNIQUE (name, league_name, season_year, player_position))"
    
    cr.execute(create_query)
    # conn.commit() # autocommit is True


async def upsert_data(name, league, stats_dict, player_position):
    
    season_year = "25/26"
    # Dictionary keys are columns
    # We need to add name, league, season_year to the dict to map easily
    stats_dict['name'] = name
    stats_dict['league_name'] = league
    stats_dict['season_year'] = season_year
    stats_dict['player_position'] = player_position
    # team_name is already in stats_dict from c.py
    
    #list of all the keys (the name of the statistics)
    columns = list(stats_dict.keys())

    #list of all the values (the value of the statistics)
    values = [stats_dict[c] for c in columns]
    
    #list of placeholders (%s)
    placeholders = ["%s"] * len(columns)
        
    #join the columns and placeholders with commas
    cols_str = ", ".join(columns)
    vals_str = ", ".join(placeholders)
    
    # Construct ON CONFLICT UPDATE clause
    # We want to update all columns except the unique key
    update_set = []
    for col in columns:
        if col not in ['name', 'league_name', 'season_year', 'player_position']:
            update_set.append(f"{col} = EXCLUDED.{col}")
        
    update_str = ", ".join(update_set)
    
    query = f"""INSERT INTO players ({cols_str}) VALUES ({vals_str})
                ON CONFLICT (name, league_name, season_year, player_position)
                DO UPDATE SET {update_str}"""
    
    try:
        cr.execute(query, values)
    except Exception as e:
        print(f"Error inserting {name}: {e}")

#summarize all the stats in one season by adding all stats across all leagues for each player
async def summarize_all_stats():
    
    #get all the distinct player names
    cr.execute("SELECT DISTINCT name FROM players WHERE season_year = '25/26'")
    
    players = cr.fetchall()
    
    #get all the column names
    cr.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'players'")
    
    columns = cr.fetchall()
    
    # Identfy columns to SUM (only numbers, ignore text like 'team_name')
    ignore_list = ['name', 'league_name', 'season_year', 'player_position', 'team_name', 'rating', 'id', 'type']
    all_columns = [row[0] for row in columns if row[0] not in ignore_list and not row[0].endswith('_per_90')]
    
    #get all the column names that end with _per_90
    per_90_columns = [row[0] for row in columns if not row[0] in ['name', 'league_name', 'season_year', 'player_position'] and row[0].endswith('_per_90')]

    # 1. Sum all the stats for each player and insert/update the 'All Leagues' row
    sum_clause = ", ".join([f"SUM({col})" for col in all_columns])
    update_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in all_columns])
        
    cr.execute(f"""INSERT INTO players (name, league_name, season_year, player_position, {', '.join(all_columns)}) 
                    SELECT name, 'All Leagues', '25/26', player_position, {sum_clause} 
                    FROM players
                    WHERE league_name != 'All Leagues'
                    GROUP BY name, season_year, player_position
                    ON CONFLICT (name, league_name, season_year, player_position) 
                    DO UPDATE SET {update_clause}""")

    # 2. Build a list of SQL "instructions" for every per-90 column
    sql_set_instructions = []
    for p90_col in per_90_columns:
        # Get the raw stat name (e.g. goals)
        base_stat = p90_col.replace('_per_90', '')
        # Create the math formula (Safe division with NULLIF)
        instruction = f"{p90_col} = ({base_stat}::float / NULLIF(minutesPlayed, 0)) * 90"
        sql_set_instructions.append(instruction)

    master_set_string = ", ".join(sql_set_instructions)

    # 3. RUN THE UPDATE FOR EVERY ROW (including the new All Leagues rows)
    cr.execute(f"""
        UPDATE players 
        SET {master_set_string}
        WHERE season_year = '25/26'
    """)

#define function to select all the stats for a specific player matching input list with the stat names
async def select_player_stats(player, league, stats_data, player_position):
    # 1. SQL injection check: Ensure we actually have stats to select
    if not stats_data:
        return {}
    
    # 2. Force lowercase to match Postgres default storage
    columns_str = ", ".join([c.lower() for c in stats_data])
    
    # 3. Create a cursor that returns dictionaries
    dict_cr = conn.cursor(cursor_factory=RealDictCursor)
    
    query = f"SELECT {columns_str} FROM players WHERE name = %s AND league_name = %s AND season_year = %s AND player_position = %s"
    params = (player, league, '25/26', player_position)
    
    dict_cr.execute(query, params)
    result = dict_cr.fetchone() # unique constraint means only 1 row exists
    dict_cr.close()
    
    return result if result else {}
    
