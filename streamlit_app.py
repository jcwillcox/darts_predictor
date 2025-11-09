import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
import json
import pandas as pd
from utils import simulator, win_pct_to_moneyline
st.title("Darts Match Outcome Simulator")
st.write("Made by James Willcox, this app simulates the outcome distribution of a darts match between two players based on their statistics.")
with st.form("simulation_form"):
    name1 = st.text_input("Player 1 Name", "")
    name2 = st.text_input("Player 2 Name", "")
    sets1 = st.number_input("Current Sets Player 1", min_value=0, value=0)
    sets2 = st.number_input("Current Sets Player 2", min_value=0, value=0)
    sets = st.number_input("Sets To Win", min_value=1, value=1)
    legs = st.number_input("Legs To Win A Set", min_value=1, value=1)
    date = st.date_input("Match Date", value = "today")
    simulations = st.number_input("Number of Simulations", min_value=0, max_value=100000, value=100000)
    st.write("If you would like the results of this simulation to be automatically logged to a Google Sheet, please enter the betting information for the match and the password below.")
    betodds1 = st.number_input("Player 1 Betting Decimal Win Odds:", min_value=1.00, step = 0.01, value = 2.0)
    betodds2 = st.number_input("Player 2 Betting Decimal Win Odds:", min_value=1.00, step = 0.01, value = 2.0)
    betway_odds_series = st.text_input("Exact Score Decimal Odds, in order from most dominant player 1 win to most dominant player 2 win:", "")
    code = st.text_input("Password:", "", type="password", autocomplete="off")
    submitted = st.form_submit_button("Run Simulation")
    if submitted:
        outcome, results, winpct1, winpct2 = simulator(name1, name2, sets1, sets2, sets, legs, simulations)
        if outcome == "Error- no stats retrieved. One or both players not found in database. Check spelling":
            st.error(outcome)
        else:
            st.success(outcome)
        
            for key, value in results.items():
                outcomepct = value/simulations * 100
                st.write(str(key) + " pct, odds, ml: " + str(round(outcomepct, 3)) + "%, " + str(win_pct_to_moneyline(outcomepct)))
            st.write(f"Win Percentage for {name1}: {winpct1:.3f}%")
            st.write(f"Win Percentage for {name2}: {winpct2:.3f}%")
            st.write(f"Decimal odds & moneyline for {name1} = {win_pct_to_moneyline(winpct1)}")
            st.write(f"Decimal odds & moneyline for {name2} = {win_pct_to_moneyline(winpct2)}")

            # If the password is correct, auto log the results to the google sheet of match data
            if code.upper() == st.secrets["app_settings"]["auto_log_password"]:
                import gspread
                from google.oauth2.service_account import Credentials

                # Define scopes for Google Sheets and Drive access
                scope = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]

                # Authenticate using service account info from Streamlit secrets
                creds = Credentials.from_service_account_info(
                    st.secrets["google_service_account"],
                    scopes=scope
                )

                # Authorize gspread client
                client = gspread.authorize(creds)

                # Open the Google Sheet by ID and select worksheets
                spreadsheet_id = st.secrets["spreadsheet_info"]["sheet_id"]
                worksheet_win = client.open_by_key(spreadsheet_id).worksheet("win_data")
                worksheet_exact = client.open_by_key(spreadsheet_id).worksheet("leg_or_set_play")

                
                # Prepare data to be logged here
                # Read the first column (column A)
                column_values = worksheet_win.col_values(1)  # returns list of strings

                # Convert to integers (skip header if there is one)
                numbers = [int(x) for x in column_values if x.isdigit()]

                # Get the max
                max_number = max(numbers)
                betwinpct1 = 1.0 / betodds1
                betwinpct2 = 1.0/ betodds2

                worksheet_win.append_row([max_number + 1, str(date), name1, betwinpct1, winpct1, name2, betwinpct2, winpct2])

                #take the odds string and convert to list of floats
                betway_prob_string = ""
                if betway_odds_series:
                    import re
                    # Split by commas or whitespace
                    odds_list = [float(x) for x in re.split(r'[,\s]+', betway_odds_series.strip()) if x]
                    betway_prob_series = [round(1.0 / odds, 4) for odds in odds_list]
                    for i in range(len(betway_prob_series)):
                        betway_prob_string = betway_prob_string + str(betway_prob_series[i]) + ", "
                
                model_prob_string = ""
                for value in results.values():
                    model_prob_string = model_prob_string + str(round(value / simulations, 4)) + ", "
                
                worksheet_exact.append_row([max_number + 1, 
                                            1 if sets > 1 else 0, 
                                            sets if sets > 1 else legs,
                                            betway_prob_string, model_prob_string ])
                st.success("Password Correct. Results logged to Google Sheet successfully!")

    