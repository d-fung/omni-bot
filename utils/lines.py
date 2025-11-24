import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from helper_functions import decimal_to_american, format_handicap, format_with_decimal, generate_response_list

load_dotenv()
API_KEY = os.getenv('X-RAPIDAPI-KEY')
API_HOST = os.getenv('X-RAPIDAPI-HOST')

headers = {
	"x-rapidapi-key": API_KEY,
	"x-rapidapi-host": API_HOST
}

# ['sport_id', 'league_id']
sports_map = {
    'nfl': ['7', '889'],
    'mlb': ['9', '246'],
    'nba': ['3', '487']
}

def get_lines(sport):
    # sport_id: 7 is american football, league_ids: 889 for NFL
    # sport_id: 3 is basketball, league_ids: 487 for NBA

    url = "https://pinnacle-odds.p.rapidapi.com/kit/v1/markets"
    querystring = {
        "sport_id":sports_map[sport][0],
                   "is_have_odds":"true",
                   "league_ids":sports_map[sport][1]
                   }
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    outputs = []

    for event in data['events']:

        if event['resulting_unit'] == 'Hits + Runs + Errors':
            continue

        current_match = ''
        dt_obj = datetime.strptime(event['starts'], "%Y-%m-%dT%H:%M:%S")
        #dt_obj = dt_obj - timedelta(hours=4)
        if event['event_type'] == 'live':
            current_match += f"\U0001F7E2 **_LIVE_**\n"
        current_match += f"**Home:** _{event['home']}_\n"
        current_match += f"**Away:** _{event['away']}_\n"
        current_match += f"**Time:** <t:{int(dt_obj.timestamp())}>\n"

        game_data = event['periods']['num_0']

        # skip if no data, usually for live events
        if not game_data.get('money_line'):
            continue
        
        if game_data.get('money_line'):
            home_ml = game_data['money_line'].get('home')
            away_ml = game_data['money_line'].get('away')
            current_match += f"**ML - Home:** _{decimal_to_american(home_ml)}_, **Away**: _{decimal_to_american(away_ml)}_\n"

        if game_data.get('spreads'):
            first_spread_key = list(game_data['spreads'].keys())[0]
            spread_info = game_data['spreads'][first_spread_key]
            
            # Format the handicap for home and away (away is opposite of home)
            home_handicap = spread_info['hdp']
            away_handicap = -home_handicap
            
            home_spread = decimal_to_american(spread_info['home'])
            away_spread = decimal_to_american(spread_info['away'])
            
            current_match += f"**Spread - Home:** _{format_handicap(home_handicap)} {home_spread}_, **Away:** _{format_handicap(away_handicap)} {away_spread}_\n"

        if game_data.get('totals'):
            first_total_key = list(game_data['totals'].keys())[0]
            total_info = game_data['totals'][first_total_key]
            points = format_with_decimal(total_info['points'])
            over_odds = decimal_to_american(total_info['over'])
            under_odds = decimal_to_american(total_info['under'])
            current_match += f"**Total Points:** _o{points} {over_odds}, u{points} {under_odds}_\n"
        
        current_match += '\n'
        outputs.append(current_match)

    return generate_response_list(outputs)
