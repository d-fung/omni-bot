import requests
from bs4 import BeautifulSoup
from .helper_functions import generate_response_list

def get_injuries(sport, team=None):
    url = f'https://www.espn.com/{sport}/injuries'
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }   
    response = requests.get(url, headers=headers)
    print(response)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

    all_teams_data = []

    # find all team blocks
    team_blocks = soup.find_all("div", class_="ResponsiveTable Table__league-injuries")

    for team_block in team_blocks:
        # extract the team name
        team_name = team_block.find("span", class_="injuries__teamName").text.strip()
        
        # locate the table body within this team block
        table_body = team_block.find("tbody", class_="Table__TBODY")
        rows = table_body.find_all("tr", class_="Table__TR")
        
        # extract data for each player
        players_data = []
        for row in rows:
            name = row.find("td", class_="col-name").text.strip()
            position = row.find("td", class_="col-pos").text.strip()
            return_date = row.find("td", class_="col-date").text.strip()
            status = row.find("td", class_="col-stat").text.strip()
            comment = row.find("td", class_="col-desc").text.strip()
            
            players_data.append({
                "Name": name,
                "Position": position,
                "Return Date": return_date,
                "Status": status,
                "Comment": comment
            })
        
        # add the team and its players to the list
        all_teams_data.append({
            "Team": team_name,
            "Players": players_data
        })

    outputs = []
    if team == None:
        for t in all_teams_data:
            current_output = ''
            current_output += f"**{t['Team']}**\n"
            for player in t['Players']:
                if player['Status'] == 'Day-To-Day' or player['Status'] == 'Questionable':
                    symbol = '\U0001F7E1' # large yellow circle
                else:
                    symbol = '\U0001F534' # large red circle

                current_output += f"{symbol} _{player['Name']} - {player['Return Date']}_\n"
            current_output += '\n'
            outputs.append(current_output)

    return generate_response_list(outputs)