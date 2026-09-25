import csv
import datetime
import os

from aenum import Enum
import cfbd
from dotenv import load_dotenv

from io import int_input

load_dotenv()


def cfbd_data_to_str(x) -> str:
    """Consistent string conversions for data returned by cfbd"""
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    if isinstance(x, Enum):
        return str(x.value)
    if x is None:
        return ""
    return str(x)


if __name__ == "__main__":
    year = int_input("Proceeding will use the API\nYear: ", 2024)
    configuration = cfbd.Configuration(access_token=os.getenv("CFBD_API_KEY"))

    with cfbd.ApiClient(configuration) as api_client:
        games_api = cfbd.GamesApi(api_client)
        response = games_api.get_games(year=YEAR, season_type="both")
        with open(f"{year}.csv", "w") as file:
            file_csv = csv.writer(file, dialect="unix")
            file_csv.writerow(
                [
                    "Week",
                    "SeasonType",
                    "StartDate",
                    "Completed",
                    "HomeId",
                    "HomeTeam",
                    "HomeClassification",
                    "HomeConference",
                    "HomePoints",
                    "AwayId",
                    "AwayTeam",
                    "AwayClassification",
                    "AwayConference",
                    "AwayPoints",
                ]
            )
            for game in response:
                row = [
                    game.week,
                    game.season_type,
                    game.start_date,
                    game.completed,
                    game.home_id,
                    game.home_team,
                    game.home_classification,
                    game.home_conference,
                    game.home_points,
                    game.away_id,
                    game.away_team,
                    game.away_classification,
                    game.away_conference,
                    game.away_points,
                ]
                row = [cfbd_data_to_str(x) for x in row]
                file_csv.writerow(row)
