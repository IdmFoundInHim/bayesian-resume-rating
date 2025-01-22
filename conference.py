from statistics import mean

from ratings import int_input, fbs_with_fcs

CONVERGENCE_DIGITS = 4
_CONVERGENCE = 10.0**-CONVERGENCE_DIGITS
LAST_UPDATED = 2025  # One year added
CONFERENCES = {  # dict[conference, dict[team, (year_joined, year_left)]]
    "ACC": {
        "Boston College": range(2005, LAST_UPDATED),
        "Clemson": range(1953, LAST_UPDATED),
        "Duke": range(1953, LAST_UPDATED),
        "Florida State": range(1991, LAST_UPDATED),
        "Georgia Tech": range(1979, LAST_UPDATED),
        "Louisville": range(2014, LAST_UPDATED),
        "Miami": range(2004, LAST_UPDATED),
        "North Carolina": range(1953, LAST_UPDATED),
        "NC State": range(1953, LAST_UPDATED),
        "Pittsburgh": range(2013, LAST_UPDATED),
        "Syracuse": range(2013, LAST_UPDATED),
        "Virginia": range(1953, LAST_UPDATED),
        "Virginia Tech": range(2004, LAST_UPDATED),
        "Wake Forest": range(1953, LAST_UPDATED),
    },
    "Big 12": {
        "Arizona": range(2024, LAST_UPDATED),
        "Arizona State": range(2024, LAST_UPDATED),
        "Baylor": range(1996, LAST_UPDATED),
        "BYU": range(2023, LAST_UPDATED),
        "Cincinnati": range(2023, LAST_UPDATED),
        "Colorado": list(range(1996, 2012)) + list(range(2024, LAST_UPDATED)),
        "Houston": range(2023, LAST_UPDATED),
        "Iowa State": range(1996, LAST_UPDATED),
        "Kansas": range(1996, LAST_UPDATED),
        "Kansas State": range(1996, LAST_UPDATED),
        "Missouri": range(1996, 2012),
        "Nebraska": range(1996, 2011),
        "Oklahoma": range(1996, 2024),
        "Oklahoma State": range(1996, LAST_UPDATED),
        "TCU": range(2012, LAST_UPDATED),
        "Texas": range(1996, 2024),
        "Texas A&M": range(1996, 2012),
        "Texas Tech": range(1996, LAST_UPDATED),
        "UCF": range(2023, LAST_UPDATED),
        "Utah": range(2024, LAST_UPDATED),
        "West Virginia": range(2012, LAST_UPDATED),
    },
    "Big Ten": {
        "Illinois": range(1896, LAST_UPDATED),
        "Indiana": range(1899, LAST_UPDATED),
        "Iowa": range(1899, LAST_UPDATED),
        "Maryland": range(2014, LAST_UPDATED),
        "Michigan": range(1917, LAST_UPDATED),
        "Michigan State": range(1950, LAST_UPDATED),
        "Minnesota": range(1896, LAST_UPDATED),
        "Nebraska": range(2011, LAST_UPDATED),
        "Northwestern": range(1896, LAST_UPDATED),
        "Ohio State": range(1912, LAST_UPDATED),
        "Oregon": range(2024, LAST_UPDATED),
        "Penn State": range(1990, LAST_UPDATED),
        "Purdue": range(1896, LAST_UPDATED),
        "Rutgers": range(2014, LAST_UPDATED),
        "UCLA": range(2024, LAST_UPDATED),
        "USC": range(2024, LAST_UPDATED),
        "Washington": range(2024, LAST_UPDATED),
        "Wisconsin": range(1896, LAST_UPDATED),
    },
    "Pac-12": {
        "Arizona": range(1978, 2024),
        "Arizona State": range(1978, 2024),
        "Boise State": range(2026, LAST_UPDATED),
        "California": range(1915, 2024),
        "Colorado": range(2011, 2024),
        "Colorado State": range(2026, LAST_UPDATED),
        "Fresno State": range(2026, LAST_UPDATED),
        "Oregon": range(1915, 2024),
        "Oregon State": range(1915, LAST_UPDATED),
        "San Diego State": range(2026, LAST_UPDATED),
        "Stanford": range(1915, 2024),
        "UCLA": range(1928, 2024),
        "USC": range(1922, 2024),
        "Utah": range(2011, 2024),
        "Utah State": range(2026, LAST_UPDATED),
        "Washington": range(1915, 2024),
        "Washington State": range(1917, LAST_UPDATED),
    },
    "SEC": {
        "Alabama": range(1933, LAST_UPDATED),
        "Arkansas": range(1992, LAST_UPDATED),
        "Auburn": range(1933, LAST_UPDATED),
        "Florida": range(1933, LAST_UPDATED),
        "Georgia": range(1933, LAST_UPDATED),
        "Kentucky": range(1933, LAST_UPDATED),
        "LSU": range(1933, LAST_UPDATED),
        "Mississippi State": range(1933, LAST_UPDATED),
        "Missouri": range(2012, LAST_UPDATED),
        "Ole Miss": range(1933, LAST_UPDATED),
        "South Carolina": range(1992, LAST_UPDATED),
        "Tennessee": range(1933, LAST_UPDATED),
        "Texas A&M": range(2012, LAST_UPDATED),
        "Vanderbilt": range(1933, LAST_UPDATED),
    },
    "American Athletic": {
        "Army": range(2024, LAST_UPDATED),
        "Charlotte": range(2023, LAST_UPDATED),
        "UConn": range(2013, 2021),
        "Cincinnati": range(2013, 2023),
        "East Carolina": range(2014, LAST_UPDATED),
        "Florida Atlantic": range(2023, LAST_UPDATED),
        "Houston": range(2013, 2023),
        "Louisville": range(2013, 2014),
        "Memphis": range(2013, LAST_UPDATED),
        "Navy": range(2015, LAST_UPDATED),
        "North Texas": range(2023, LAST_UPDATED),
        "Rice": range(2023, LAST_UPDATED),
        "Rutgers": range(2013, 2014),
        "SMU": range(2013, 2024),
        "South Florida": range(2013, LAST_UPDATED),
        "Temple": range(2013, LAST_UPDATED),
        "Tulane": range(2014, LAST_UPDATED),
        "Tulsa": range(2014, LAST_UPDATED),
        "UAB": range(2023, LAST_UPDATED),
        "UCF": range(2013, 2023),
        "UTSA": range(2023, LAST_UPDATED),
    },
    "Conference USA": {
        "Army": range(1998, 2005),
        "Charlotte": range(2015, 2023),
        "Cincinnati": range(1996, 2005),
        "Delaware": range(2025, LAST_UPDATED),
        "East Carolina": range(1997, 2014),
        "Florida International": range(2013, LAST_UPDATED),
        "Houston": range(1996, 2013),
        "Jacksonville State": range(2023, LAST_UPDATED),
        "Kennesaw State": range(2024, LAST_UPDATED),
        "Liberty": range(2023, LAST_UPDATED),
        "Louisiana Tech": range(2013, LAST_UPDATED),
        "Louisville": range(1996, 2005),
        "Marshall": range(2005, 2022),
        "Memphis": range(1996, 2013),
        "Middle Tennessee": range(2013, LAST_UPDATED),
        "Missouri State": range(2025, LAST_UPDATED),
        "New Mexico State": range(2023, LAST_UPDATED),
        "North Texas": range(2013, 2023),
        "Old Dominion": range(2014, 2022),
        "Sam Houston": range(2023, LAST_UPDATED),
        "Rice": range(2005, 2013),
        "SMU": range(2005, 2013),
        "Southern Miss": range(1995, 2022),
        "TCU": range(2001, 2005),
        "Tulane": range(1996, 2014),
        "Tulsa": range(2005, 2014),
        "UAB": list(range(1995, 2015)) + list(range(2017, 2023)),
        "UCF": range(2005, 2013),
        "South Florida": range(2003, 2005),
        "UTEP": range(2005, LAST_UPDATED),
        "UTSA": range(2013, 2023),
        "Western Kentucky": range(2014, LAST_UPDATED),
    },
    "Mid-American": {
        "Akron": range(1992, LAST_UPDATED),
        "Ball State": range(1973, LAST_UPDATED),
        "Bowling Green": range(1952, LAST_UPDATED),
        "Buffalo": range(1999, LAST_UPDATED),
        "Central Michigan": range(1975, LAST_UPDATED),
        "Eastern Michigan": range(1972, LAST_UPDATED),
        "Kent State": range(1951, LAST_UPDATED),
        "Marshall": range(1997, 2005),
        "Massachusetts": list(range(2012, 2015)) + list(range(2025, LAST_UPDATED)),
        "Miami (OH)": range(1947, LAST_UPDATED),
        "Northern Illinois": range(1997, 2026),
        "Ohio": range(1946, LAST_UPDATED),
        "Temple": range(2007, 2012),
        "Toledo": range(1950, LAST_UPDATED),
        "UCF": range(2002, 2005),
        "Western Michigan": range(1947, LAST_UPDATED),
    },
    "Mountain West": {
        "Air Force": range(1999, LAST_UPDATED),
        "Boise State": range(2011, 2026),
        "BYU": range(1999, 2011),
        "Colorado State": range(1999, 2026),
        "Fresno State": range(2012, 2026),
        "Hawai'i": range(2012, LAST_UPDATED),
        "Nevada": range(2012, LAST_UPDATED),
        "New Mexico": range(1999, LAST_UPDATED),
        "Northern Illinois": range(2026, LAST_UPDATED),
        "San Diego State": range(1999, 2026),
        "San José State": range(2013, LAST_UPDATED),
        "TCU": range(2005, 2012),
        "UNLV": range(1999, LAST_UPDATED),
        "Utah": range(1999, 2011),
        "Utah State": range(2013, 2026),
        "Wyoming": range(1999, LAST_UPDATED),
    },
    "Sun Belt": {
        "App State": range(2014, LAST_UPDATED),
        "Arkansas State": range(2001, LAST_UPDATED),
        "Coastal Carolina": range(2017, LAST_UPDATED),
        "Florida Atlantic": range(2005, 2013),
        "Florida International": range(2005, 2013),
        "Georgia Southern": range(2014, LAST_UPDATED),
        "Georgia State": range(2013, LAST_UPDATED),
        "James Madison": range(2022, LAST_UPDATED),
        "Louisiana": range(2001, LAST_UPDATED),
        "UL Monroe": range(2001, LAST_UPDATED),
        "Marshall": range(2022, LAST_UPDATED),
        "MTSU": range(2001, 2013),
        "New Mexico State": range(2001, 2005),
        "North Texas": range(2000, 2013),
        "Old Dominion": range(2022, LAST_UPDATED),
        "South Alabama": range(2012, LAST_UPDATED),
        "Southern Miss": range(2022, LAST_UPDATED),
        "Texas State": range(2013, LAST_UPDATED),
        "Troy": range(2004, LAST_UPDATED),
        "Western Kentucky": range(2009, 2014),
    },
}

if __name__ == "__main__":
    year = int_input("Year: ", 2023)
    week = int_input("Week: ", 17)  # 2023 had 17 weeks
    team_ratings = {
        k[:40].strip(): v[0]
        for k, v in fbs_with_fcs(year, week, _CONVERGENCE)[2].items()
    }
    year = min(year, LAST_UPDATED)
    current_conference_members = {
        conference: [
            team
            for team in CONFERENCES[conference]
            if year in CONFERENCES[conference][team]
        ]
        for conference in CONFERENCES
    }
    average_ratings = {
        conference: mean(
            team_ratings[team]
            for team in current_conference_members[conference]
            if team in team_ratings
        )
        for conference in current_conference_members
    }
    unofficial = False
    for conference in sorted(average_ratings, key=average_ratings.get, reverse=True):
        print(
            f"{conference}{((unofficial := True) and '*') if 8 > len(current_conference_members[conference]) else ''}: {average_ratings[conference]:.{CONVERGENCE_DIGITS}f}"
        )
    if unofficial:
        print("\n*Conference did not meet FBS 8-team minimum")
