import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
import json
import pandas as pd
from utils import simulator, win_pct_to_moneyline
st.title("Darts Match Outcome Simulator")
st.write("This app simulates the outcome distribution of a darts match between two players based on their statistics.")
with st.form("simulation_form"):
    name1 = st.text_input("Player 1 Name", "")
    name2 = st.text_input("Player 2 Name", "")
    sets1 = st.number_input("Current Sets Player 1", min_value=0, value=0)
    sets2 = st.number_input("Current Sets Player 2", min_value=0, value=0)
    sets = st.number_input("Sets To Win", min_value=1, value=1)
    legs = st.number_input("Legs To Win A Set", min_value=1, value=1)
    simulations = st.number_input("Number of Simulations", min_value=0, max_value=100000, value=100000)
    code = st.text_input("Password to have this match auto-log itself to the database", "")
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

    #integrate google sheet
    if code.upper() == "MVG":
        st.success("password correct")