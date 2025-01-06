import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import warnings
import time
import csv
import os
import re


warnings.filterwarnings("ignore")

driver = webdriver.Chrome()

# Explicitly wait for the dropdown button to be clickable
wait = WebDriverWait(driver, 120)


def getFilterValues(html_content, class_to_find):
    filter_html = (
        html_content.find("section", class_="pageFilter col-12")
        .find("div", class_=class_to_find)
        .find_all("li")
    )
    filter_values = []

    for val in filter_html:
        filter_values.append(val.text)

    return filter_values


all_players_df = pd.read_csv("PlayersPerSeason.csv", encoding="utf-8")
print(all_players_df.shape)

player_stats = {
    "Defender": {
        "Defence": [
            "Clean sheets","Goals Conceded","Tackles","Tackle success %","Last man tackles",
            "Blocked shots","Interceptions","Clearances","Headed Clearance","Clearances off line",
            "Recoveries","Duels won","Duels lost","Successful 50/50s","Aerial battles won","Aerial battles lost",
            "Own goals","Errors leading to goal"
        ],
        "Team Play": [
            "Assists","Passes","Passes per match","Big Chances Created","Crosses","Cross accuracy %",
            "Through balls","Accurate long balls"
        ],
        "Discipline": [
            "Yellow cards", "Red cards", "Fouls", "Offsides"
        ],
        "Attack": [
            "Goals","Headed goals", "Goals with right foot", "Goals with left foot", "Hit woodwork"
        ],
    },
    "Forward": {
        "Attack": [
            "Goals", "Goals per match", "Headed goals", "Goals with right foot", "Goals with left foot",
            "Penalties scored", "Freekicks scored", "Shots", "Shots on target", "Shooting accuracy %",
            "Hit woodwork", "Big chances missed"
        ],
        "Team Play": [
            "Assists", "Passes", "Passes per match", "Big Chances Created", "Crosses"
        ],
        "Discipline": [
            "Yellow cards", "Red cards", "Fouls", "Offsides"
        ],
        "Defence": [
            "Tackles", "Blocked shots", "Interceptions", "Clearances", "Headed Clearance"
        ],
    },
    "Goalkeeper": {
        "Goalkeeping": [
            "Saves", "Penalties Saved", "Punches", "High Claims", "Catches",
            "Sweeper clearances", "Throw outs",  "Goal Kicks"
        ],
        "Defence": [
            "Clean sheets", "Goals Conceded", "Errors leading to goal", "Own goals"
        ],
        "Discipline": [
            "Yellow cards", "Red cards", "Fouls"
            ],
        "Team Play": [
            "Goals", "Assists", "Passes", "Passes per match", "Accurate long balls"
        ],
    },
    "Midfielder": {
        "Attack": [
            "Goals", "Goals per match", "Headed goals", "Goals with right foot", "Goals with left foot",
            "Penalties scored", "Freekicks scored", "Shots", "Shots on target", "Shooting accuracy %",
            "Hit woodwork", "Big chances missed",
        ],
        "Team Play": [
            "Assists",  "Passes", "Passes per match", "Big Chances Created", "Crosses",
            "Cross accuracy %", "Through balls", "Accurate long balls",
        ],
        "Discipline": [
            "Yellow cards", "Red cards", "Fouls", "Offsides"
        ],
        "Defence": [
            "Tackles", "Tackle success %", "Blocked shots", "Interceptions",
            "Clearances", "Headed Clearance", "Recoveries", "Duels won", "Duels lost",
            "Successful 50/50s", "Aerial battles won", "Aerial battles lost", "Errors leading to goal",
        ],
    },
}


all_stats = [
    "Appearances","Wins","Losses","Last man tackles","Freekicks scored","Yellow cards","Fouls",
    "Shots on target","Sweeper clearances","Assists","Tackle success %","Duels won","Goals with left foot",
    "Accurate long balls","Shots","Penalties Saved","Crosses","Goals with right foot","Shooting accuracy %",
    "Passes","Catches","Passes per match","Headed Clearance","Throw outs","Tackles","Big Chances Created",
    "Hit woodwork","High Claims","Goals per match","Offsides","Goal Kicks","Big chances missed","Blocked shots",
    "Penalties scored","Clean sheets","Own goals","Successful 50/50s","Recoveries","Clearances off line","Goals",
    "Interceptions","Aerial battles won","Cross accuracy %","Punches","Clearances","Errors leading to goal","Duels lost",
    "Aerial battles lost","Goals Conceded","Through balls","Saves","Headed goals","Red cards"
]


def add_to_csv(all_stats, players_data):
    # We'll create a DataFrame where columns represent the stats
    df = pd.DataFrame(columns=["Season", "Player", "Position"] + all_stats)

    # Use pd.concat() to add player data to the DataFrame
    for player in players_data:
        player_df = pd.DataFrame(
            [player]
        )  # Convert the player dictionary into a DataFrame
        df = pd.concat([df, player_df], ignore_index=True)

    for col in df.columns:
        # Check if the column contains string data and is not completely empty
        if df[col].dtype == "object" and df[col].notna().any():
            # Replace '\n' and ',' in columns where applicable, ignoring empty or None entries
            df[col] = df[col].replace({"\n": "", ",": ""}, regex=True)

    print(df)
    file_path = "Player_Stats_Data.csv"

    if not os.path.exists(file_path):
        # If the file doesn't exist, create it by saving the dataframe
        df.to_csv(file_path, index=False, quoting=csv.QUOTE_ALL)
    else:
        # If the file exists, append without writing the header
        df.to_csv(file_path, mode="a", header=False, index=False, quoting=csv.QUOTE_ALL)


for idx, row in all_players_df.iterrows():
    players_data = []
    start = time.time()
    if row["Done"] == "YES":
        continue

    player_name = row["Player"]
    position = row["Position"]
    stat_url = row["Link"]

    print(player_name)

    driver = webdriver.Chrome()

    web = stat_url
    driver.get(web)

    try:
        accept_cookies = driver.find_element(
            By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'
        )
        accept_cookies.click()
    except Exception as e:
        print(e)

    time.sleep(1)
    wait = WebDriverWait(driver, 120)

    try:
        close_advert = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="advertClose"]'))
        )
        close_advert.click()

    except Exception as e:
        print(e)
    time.sleep(1)

    html = driver.page_source
    soup = bs(html, "html.parser")

    filter_by_season_values = getFilterValues(soup, "dropDown mobile")

    if "2006/07" in filter_by_season_values:
        length = filter_by_season_values.index("2006/07") + 1
    else:
        length = len(filter_by_season_values)

    for i in range(1, length):
        # print("Season:",filter_by_season_values[i])
        player_stat = dict()
        player_stat["Player"] = player_name
        player_stat["Position"] = position
        player_stat["Season"] = filter_by_season_values[i]

        # Wait for the dropdown button and click it
        season_dropdown_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="mainContent"]/div[2]/div/div/div/div/section/div[2]/div[2]',
                )
            )
        )
        season_dropdown_button.click()
        time.sleep(1)
        # Wait for the options in the dropdown to become visible
        season_option = wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="mainContent"]/div[2]/div/div/div/div/section/div[2]/div[3]/ul/li[{n}]'.format(
                        n=i + 1
                    ),
                )
            )
        )

        # Click the desired option
        season_option.click()

        time.sleep(1)

        filtered_html = driver.page_source
        filtered_soup = bs(filtered_html, "html.parser")

        player_position = filtered_soup.find("div", class_="player-overview__info")

        overview_stat_list = filtered_soup.find(
            "div", "player-stats__top-stats"
        ).find_all("div", "player-stats__top-stat")
        for div in overview_stat_list:
            temp = re.split("\s{2,}", div.text)
            # print(temp)
            if temp[1] == "Goals":
                continue
            player_stat[temp[1]] = temp[2]

        stat_ul = filtered_soup.find("ul", class_="player-stats__stats-wrapper")
        stat_list = stat_ul.find_all("li")
        for stat in stat_list:
            for div in stat.find_all("div", "player-stats__stat-value"):
                temp = re.split("\s{2,}", div.text)
                # print(temp)
                player_stat[temp[0]] = temp[1]
        # print(player_stat)
        players_data.append(player_stat)
    print("Total Time taken fo the player:", time.time() - start)
    driver.quit()
    add_to_csv(all_stats, players_data)
    all_players_df.iloc[idx, all_players_df.columns.get_loc("Done")] = "YES"
    all_players_df.to_csv("PlayersPerSeason.csv", index=False)
