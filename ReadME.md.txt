# Project Title: Predicting Player Transfer and Valuation in the English Premier League Using Machine Learning

## Overview
This project focuses on collecting player data using web scraping scripts and analyzing it through predictive models for player valuation and transfer predictions.

## Data Collection
- **get_player_list.py**: Collects a list of players.
- **get_player_data.py**: Fetches detailed statistics for each player from the collected list.
  - If the script encounters an error, rerunning it will resume from the last unfinished player.

## Running the Scripts
- Run `get_player_list.py` to collect player data.
- Run `get_player_data.py` to fetch detailed player statistics.


## Data for Prediction Models
To run the Player Valuation Prediction and Player Transfer Prediction Jupyter notebooks:
1. Download the dataset from [Kaggle Player Scores Dataset](https://www.kaggle.com/datasets/davidcariboo/player-scores).
2. Place the downloaded dataset in the `Data/` folder.

## Notebooks
- **Player Valuation Prediction.ipynb**: Predict player valuation based on collected data.
- **Player Transfer Prediction.ipynb**: Predict player transfer likelihood based on collected data.

## Dependencies
Ensure you have the required Python libraries installed. Install them using:
```bash
pip install -r requirements.txt
```

