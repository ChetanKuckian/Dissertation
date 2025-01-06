import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import warnings
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

warnings.filterwarnings("ignore")

driver = webdriver.Chrome()

web = "https://www.premierleague.com/players"
driver.get(web)

try:

    accept_cookies = driver.find_element(
        By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'
    )
    accept_cookies.click()
    time.sleep(1)
except Exception as e:
    print(e)


# Explicitly wait for the dropdown button to be clickable
wait = WebDriverWait(driver, 120)

try:
    close_advert = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="advertClose"]'))
    )
    close_advert.click()
except Exception as e:
    print(e)


# Wait for the dropdown button and click it
dropdown_button = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="mainContent"]/div[2]/div[1]/div/section/div[1]/div[2]')
    )
)
dropdown_button.click()

# Wait for the options in the dropdown to become visible
desired_option = wait.until(
    EC.visibility_of_element_located(
        (
            By.XPATH,
            '//*[@id="mainContent"]/div[2]/div[1]/div/section/div[1]/div[3]/ul/li[2]',
        )
    )
)

# Click the desired option
desired_option.click()

# Wait to observe the change
time.sleep(1)

html = driver.page_source
soup = bs(html, "html.parser")


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


filter_by_season_values = getFilterValues(soup, "dropDown active")
print(filter_by_season_values)


players = []
position = []
links = []


all_players_df = pd.DataFrame(columns=["Player", "Position", "Link"])


for i in range(0, filter_by_season_values.index("2006/07") + 1):
    print("Season:", filter_by_season_values[i])
    # Wait for the dropdown button and click it
    season_dropdown_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="mainContent"]/div[2]/div[1]/div/section/div[1]/div[2]')
        )
    )
    season_dropdown_button.click()

    time.sleep(1)
    # Wait for the options in the dropdown to become visible
    season_option = wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                '//*[@id="mainContent"]/div[2]/div[1]/div/section/div[1]/div[3]/ul/li[{i}]'.format(
                    i=i + 1
                ),
            )
        )
    )

    # Click the desired option
    season_option.click()

    time.sleep(1)

    html = driver.page_source
    soup = bs(html, "html.parser")

    filter_by_club_values = getFilterValues(soup, "dropDown mobile")
    print(filter_by_club_values)

    for j in range(1, len(filter_by_club_values)):
        print("Club:", filter_by_club_values[j])
        club_dropdown_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="mainContent"]/div[2]/div/div/section/div[2]/div[2]',
                )
            )
        )
        club_dropdown_button.click()
        time.sleep(2)

        club_option = wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="mainContent"]/div[2]/div/div/section/div[2]/div[3]/ul/li[{i}]'.format(
                        i=j + 1
                    ),
                )
            )
        )
        club_option.click()
        time.sleep(1)

        # Scroll to the bottom of the page to load all players
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(3)  # Wait for the page to load

        filtered_html = driver.page_source
        filtered_soup = bs(filtered_html, "html.parser")

        filtered_table = filtered_soup.find("table")
        headers = [x.text for x in filtered_soup.find("thead").find_all("th")]

        for player in filtered_soup.find("tbody").find_all("tr"):
            data = player.find_all("td")
            print(data[0].text)
            players.append(data[0].text)
            position.append(data[1].text)
            links.append(
                data[0]
                .find("a")
                .get("href")
                .replace("/overview", "/stats")
                .replace("//www", "https://www")
            )

    temp_data = pd.DataFrame(columns=["Player", "Position", "Link"])
    temp_data["Player"] = players
    temp_data["Position"] = position
    temp_data["Link"] = links

    all_players_df = pd.concat([all_players_df, temp_data], ignore_index=True)


print(all_players_df.shape)
all_players_df.drop_duplicates(inplace=True)
all_players_df.to_csv("PlayersPerSeason.csv", index=False)
