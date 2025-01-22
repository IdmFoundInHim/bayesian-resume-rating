from collections.abc import Callable
from datetime import datetime, timedelta, timezone

import csv

type Row = tuple[int, bool, datetime, str, str, str, str, str, str]
type Key = Callable[[int, bool, datetime, str, str, str, str, str, str], Row]


def csv2list(key: Key) -> Callable[[str], list[tuple[str, str]]]:
    def f(csvfile: str) -> list[tuple[str, str]]:
        results = []
        with open(csvfile, "r") as file:
            reader = csv.reader(file)
            next(reader)
            for (
                week,
                before_playoff,
                time,
                game_completed,
                home_id,
                home_team,
                home_conference,
                home_division,
                home_points,
                away_id,
                away_team,
                away_conference,
                away_division,
                away_points,
            ) in reader:
                if game_completed.lower() == "true":
                    home = str(home_id)
                    home = (
                        home_team[:40]
                        + " " * (40 - len(home_team))
                        + home[:10]
                        + " " * (10 - len(home))
                    )
                    away = str(away_id)
                    away = (
                        away_team[:40]
                        + " " * (40 - len(away_team))
                        + away[:10]
                        + " " * (10 - len(away))
                    )
                    _, _, _, home, _, _, away, _, _ = key(
                        int(week),
                        before_playoff == "regular",
                        datetime.fromisoformat(time),
                        home,
                        home_conference,
                        home_division,
                        away,
                        away_conference,
                        away_division,
                    )
                    if home:
                        if int(home_points) > int(away_points):
                            results.append((home, away))
                        else:
                            results.append((away, home))
        return results

    return f


@csv2list
def all_games(*args):
    return args


def add_division_filter(
    division_name: str, /, include_others: bool = True, squash_others: bool = True
) -> Callable[[Key], Key]:
    def decorator(key: Key) -> Key:
        def final_function(
            _0: int,
            _1: bool,
            _2: datetime,
            home: str,
            home_conference: str,
            home_division: str,
            away: str,
            away_conference: str,
            away_division: str,
        ) -> Row:
            if home_division != division_name:
                if away_division != division_name or not include_others:
                    home = ""
                elif squash_others:
                    home = (
                        home_division.upper()
                        + " " * (40 - len(home_division))
                        + "0         "
                    )
                home_conference = home_division.upper()
            elif away_division != division_name:
                if not include_others:
                    home = ""
                elif squash_others:
                    away = (
                        away_division.upper()
                        + " " * (40 - len(away_division))
                        + "0         "
                    )
                away_conference = away_division.upper()
            return key(
                _0,
                _1,
                _2,
                home,
                home_conference,
                home_division,
                away,
                away_conference,
                away_division,
            )

        return final_function

    return decorator


def add_conference_filter(
    conference_name: str, /, include_others: bool = False, squash_others: bool = False
) -> Callable[[Key], Key]:
    def decorator(key: Key) -> Key:
        def final_function(
            _0: int,
            _1: bool,
            _2: datetime,
            home: str,
            home_conference: str,
            home_division: str,
            away: str,
            away_conference: str,
            away_division: str,
        ) -> Row:
            if home_conference != conference_name:
                if away_conference != conference_name or not include_others:
                    home = ""
                elif squash_others:
                    home = (
                        home_conference.upper()
                        + " " * (40 - len(home_conference))
                        + "0         "
                    )
                home_division = home_conference.upper()
            elif away_conference != conference_name:
                if not include_others:
                    home = ""
                elif squash_others:
                    away = (
                        away_conference.upper()
                        + " " * (40 - len(away_conference))
                        + "0         "
                    )
                away_division = away_conference.upper()
            return key(
                _0,
                _1,
                _2,
                home,
                home_conference,
                home_division,
                away,
                away_conference,
                away_division,
            )

        return final_function

    return decorator


def previous_monday(dt: datetime) -> datetime:
    dt = dt - timedelta(hours=5)
    dt = dt - timedelta(days=dt.weekday())
    return dt.replace(hour=5, minute=0, second=0, microsecond=0)


def add_week_filter(
    last_week: int, csv_file: str | None = None
) -> Callable[[Key], Key]:
    include_postseason = False
    if csv_file is not None:
        with open(csv_file, "r") as file:
            reader = csv.reader(file)
            next(reader)
            reg_season_end_week = 0
            reg_season_end_date = datetime.max.replace(tzinfo=timezone.utc)
            for row in reader:
                if row[1] == "postseason":
                    reg_season_end_date = min(
                        datetime.fromisoformat(row[2]), reg_season_end_date
                    )
                else:
                    reg_season_end_week = max(int(row[0]), reg_season_end_week)
            reg_season_end_date = previous_monday(reg_season_end_date)
        if last_week > reg_season_end_week:
            include_postseason = True

    def decorator(key: Key) -> Key:
        def final_function(
            week: int,
            before_playoffs: bool,
            start_time: datetime,
            home: str,
            _4: str,
            _5: str,
            _6: str,
            _7: str,
            _8: str,
        ) -> Row:
            if not before_playoffs:
                week = (start_time - reg_season_end_date) / timedelta(
                    weeks=1
                ) + reg_season_end_week
            if week > last_week:
                home = ""
            return key(week, before_playoffs, start_time, home, _4, _5, _6, _7, _8)

        return final_function

    return decorator


@csv2list
@add_division_filter("fbs")
def fbs_nonconference(
    _0: int,
    _1: bool,
    _2: datetime,
    home: str,
    home_conference: str,
    _5: str,
    away: str,
    away_conference: str,
    _8: str,
) -> Row:
    if home_conference == away_conference:
        home = ""
    return _0, _1, _2, home, home_conference, _5, away, away_conference, _8


@csv2list
@add_division_filter("fbs")
def fbs(*args):
    return args


@csv2list
@add_division_filter("fbs", include_others=False)
def fbs_pure(*args):
    return args


@csv2list
@add_conference_filter("Big Ten")
def big_ten(*args):
    return args
