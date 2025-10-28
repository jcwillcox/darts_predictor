#this python script contains utility functions for the darts predictor defined in predictor.ipynb
import requests
from bs4 import BeautifulSoup
import random
import json
import pandas as pd


#this part saves all the player data in a json using a nested dictionary- player name k
def get_all_stats():
    url = "https://dartsorakel.com/api/stats/player?dateFrom=2024-10-13&dateTo=2025-10-13&rankKey=25&organStat=All&tourns=&minMatches=200&tourCardYear=&showStatsBreakdown=0&_=1760381904166" 
    data = requests.get(url).json()
    players = {}
    for player in data['data']:
        name = player['player_name']
        key = player['player_key']
        players[name] = key

    tableaustats = {}
    for key, value in players.items():
        tableaustats[key] = {}
        link = "https://dartsorakel.com/player/stats/" + str(value)
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.find('table', id='playerStatsTable')
        for row in table.tbody.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) == 2:
                    # Get the stat name and value
                    stat_name = cells[0].get_text(strip=True)
                    stat_value = cells[1].get_text(strip=True)
                    if isinstance(stat_value, str) and stat_value.endswith('%'):
                        try:
                            num = float(stat_value.strip('%'))
                            tableaustats[key][stat_name] = num / 100
                        except ValueError:
                            tableaustats[key][stat_name] = stat_value  # if conversion fails, keep original
                    else:
                        tableaustats[key][stat_name] = stat_value
        if float(tableaustats[key]["Averages"]) < 77.61:
            break
    with open("tableau_stats.json", 'w') as json_file:
        json.dump(tableaustats, json_file, indent=4)


def get_match_stats(P1, P2):
    #use beautiful soup to extract the relevant stats from the website
    url = "https://dartsorakel.com/api/stats/player?dateFrom=2024-10-13&dateTo=2025-10-13&rankKey=25&organStat=All&tourns=&minMatches=200&tourCardYear=&showStatsBreakdown=0&_=1760381904166" 
    data = requests.get(url).json()
    players = {}
    for player in data['data']:
        name = player['player_name']
        key = player['player_key']
        players[name] = key

    if P1 in players and P2 in players:
        firstlink = "https://dartsorakel.com/player/stats/" +  str(players[P1])
        secondlink = "https://dartsorakel.com/player/stats/" +  str(players[P2])
        page1 = requests.get(firstlink)
        page2 = requests.get(secondlink)
        soup1 = BeautifulSoup(page1.content, 'html.parser')
        soup2 = BeautifulSoup(page2.content, 'html.parser')
        table1 = soup1.find('table', id='playerStatsTable')
        table2 = soup2.find('table', id='playerStatsTable')

        # Initialize a dictionary to store stats
        stats1 = {}
        stats2 = {}

        # Loop through all rows in the tbody
        for row in table1.tbody.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) == 2:
                # Get the stat name and value
                stat_name = cells[0].get_text(strip=True)
                stat_value = cells[1].get_text(strip=True)
                if isinstance(stat_value, str) and stat_value.endswith('%'):
                    try:
                        num = float(stat_value.strip('%'))
                        stats1[stat_name] = num / 100
                    except ValueError:
                        stats1[stat_name] = stat_value  # if conversion fails, keep original
                else:
                    stats1[stat_name] = stat_value

        for row in table2.tbody.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) == 2:
                # Get the stat name and value
                stat_name = cells[0].get_text(strip=True)
                stat_value = cells[1].get_text(strip=True)
                if isinstance(stat_value, str) and stat_value.endswith('%'):
                    try:
                        num = float(stat_value.strip('%'))
                        stats2[stat_name] = num / 100
                    except ValueError:
                        stats2[stat_name] = stat_value  # if conversion fails, keep original
                else:
                    stats2[stat_name] = stat_value
        
        return stats1, stats2
        
    else:
        return None, None
    
def get_win_prob(stats1, stats2):
    #obtains cumulative stats of each player finishing in a certain visit
    third_p1 = (stats1['Treble 20 Hit Pcnt'] ** 7) * stats1['Treble 19 Hit Pcnt'] * stats1['Checkout Pcnt 3rd Dart']
    third_p2 = (stats2['Treble 20 Hit Pcnt'] ** 7) * stats2['Treble 19 Hit Pcnt'] * stats2['Checkout Pcnt 3rd Dart']
    fourth_p1 = stats1['Pcnt 12 Darter When Possible']
    fourth_p2 = stats2['Pcnt 12 Darter When Possible']
    fifth_p1 = stats1['Pcnt 15 Darter When Possible']
    fifth_p2 = stats2['Pcnt 15 Darter When Possible']
    sixth_p1 = stats1['Pcnt 18 Darter When Possible']
    sixth_p2 = stats2['Pcnt 18 Darter When Possible']
    seventh_p1 = sixth_p1 + ((1 - sixth_p1) * stats1['Checkout Pcnt 1 Darter'])
    seventh_p2 = sixth_p2 + ((1 - sixth_p2) * stats2['Checkout Pcnt 1 Darter'])
    eigth_p1 = seventh_p1 + ((1 - seventh_p1) * stats1['Checkout Pcnt 1 Darter'])
    eigth_p2 = seventh_p2 + ((1 - seventh_p2) * stats2['Checkout Pcnt 1 Darter'])
    ninth_p1 = eigth_p1 + ((1 - eigth_p1) * stats1['Checkout Pcnt 1 Darter'])
    ninth_p2 = eigth_p2 + ((1 - eigth_p2) * stats2['Checkout Pcnt 1 Darter'])
    tenplus_p1 = 1
    tenplus_p2 = 1
    p1_cumulative_probs = [third_p1, fourth_p1, fifth_p1, sixth_p1, seventh_p1, eigth_p1, ninth_p1, tenplus_p1]
    p2_cumulative_probs = [third_p2, fourth_p2, fifth_p2, sixth_p2, seventh_p2, eigth_p2, ninth_p2, tenplus_p2]

    return p1_cumulative_probs, p2_cumulative_probs

def win_pct_to_moneyline(win_pct):
    p = win_pct / 100  # convert % to decimal
    decimal_odds = 1 / p
    
    if decimal_odds >= 2:
        moneyline = (decimal_odds - 1) * 100
    else:
        moneyline = -100 / (decimal_odds - 1)
    
    return round(decimal_odds, 3), round(moneyline)
    
def leg(probs1, probs2, name1, name2): #inputs- player probabilities used to calculate visits, player names
    # this function returns the name of the player who won the leg
    #note- player 1 throws first
    p1_performance = random.random()
    p2_performance = random.random()
    p1_visits = 0
    for i, p in enumerate(probs1):
        if p1_performance <= p:
            p1_visits = i + 3  # visits are 3-indexed
            break
    p2_visits = 0
    for i, p in enumerate(probs2):
        if p2_performance <= p:
            p2_visits = i + 3  # visits are 3-indexed
            break
    if p1_visits <= p2_visits:
        return name1
    else:
        return name2

def simulator(name1, name2, sets1, sets2, sets_to_win, legs_to_win, games):
    #run the get match stats function with the name parameters, 
    stats1, stats2 = get_match_stats(name1, name2)
    if stats1 is None or stats2 is None:
        outcome = "Error- no stats retrieved. One or both players not found in database. Check spelling"
        return outcome, {}, 0, 0

    p1probs, p2probs = get_win_prob(stats1, stats2)
    #need to still convert odds, output charts/distributions
    #first being true= player 1 throws first that leg
    p1wins = 0
    p2wins = 0
    results = {} # enumerate game possibilities for returning results
    if sets_to_win > 1: #set play
        for i in range(sets_to_win): # if sets to win is 3, range is 0,1,2
            results[(sets_to_win, i)] = 0
        for j in range(sets_to_win - 1, -1, -1):
            results[(j, sets_to_win)] = 0
    else: #leg play
        for i in range(legs_to_win): # if sets to win is 3, range is 0,1,2
            results[(legs_to_win, i)] = 0
        for j in range(legs_to_win -1, -1, -1):
            results[(j, legs_to_win)] = 0
    gamefirst = True
    legs1 = 0
    legs2 = 0
    for game in range(games): # simulate the matches
        setfirst = gamefirst
        p1sets = sets1
        p2sets = sets2
        while p1sets < sets_to_win and p2sets < sets_to_win: # loop until game is finished
            first = setfirst
            legs1 = 0
            legs2 = 0
            while legs1 < legs_to_win and legs2 < legs_to_win: # loop until set is finished
                if first:
                    leg_winner_name = leg(p1probs, p2probs, name1, name2)
                else:
                    leg_winner_name = leg(p2probs, p1probs, name2, name1)
                if leg_winner_name == name1: #increment legs score for the leg winner
                    legs1 = legs1 + 1
                else:
                    legs2 = legs2 + 1
                first = not first #switch who goes first next leg
            if legs1 == legs_to_win: #increment sets for the set winner
                p1sets = p1sets + 1
            else:
                p2sets = p2sets + 1
            setfirst = not setfirst
        if p1sets == sets_to_win: #increment wins for the winner
            p1wins = p1wins + 1
        else:
            p2wins = p2wins + 1
        gamefirst = not gamefirst # flip who starts 1st each game
        if sets_to_win > 1:
            results[(p1sets, p2sets)] += 1 #add to results
        else:
            results[(legs1, legs2)] += 1

    winpct1 = float(p1wins)/games * 100
    winpct2 = float(p2wins)/games * 100
    results_dist = {}
    for key, value in results.items():
        outcomepct = value/games * 100
        print(str(key) + " pct, odds, ml: " + str(round(outcomepct, 3)) + ", " + str(win_pct_to_moneyline(outcomepct)))
        newresult = str(key).strip("(").strip(")").replace(", ", "-").strip(" ")
        results_dist[str(newresult)] = value/games*100
    outcome = "Simulation Complete\n"
    #print(name1 + " wins = " + str(winpct1) + "percent")
    #print(name2 + " wins = " + str(winpct2) + "percent")
    #print("Decimal odds & moneyline for " + name1 + " = " + str(win_pct_to_moneyline(winpct1)))
    #print("Decimal odds & moneyline for " + name2 + " = " + str(win_pct_to_moneyline(winpct2)))
    #with open("results_distribution.json", 'w') as json_file:
        #json.dump(results_dist, json_file, indent=4)
        #convert the json to a csv
    #df = pd.DataFrame(list(results_dist.items()), columns=['Outcome', 'Percentage'])
    #df.to_csv('results_distribution.csv', index=False)
    return outcome, results, winpct1, winpct2
