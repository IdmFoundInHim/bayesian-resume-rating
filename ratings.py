import json
from collections.abc import Callable
from typing import TypeVar

from brr_math import iter_ratings, calc_parity
from data import csv2list, add_division_filter, add_week_filter, TEAM_NAME_LENGTH

CONVERGENCE_DIGITS = 6
_CONVERGENCE = 10.0**-CONVERGENCE_DIGITS


def int_input(prompt: str, default: int) -> int:
    i = input(prompt)
    return int(i) if i.isdigit() else default


T = TypeVar("T", bound=Callable)


def variadic_call(func: T) -> T:
    def wrapper(*args, **kwargs):
        for kw in kwargs.copy():
            if kwargs[kw] is None:
                del kwargs[kw]
        return func(*args, **kwargs)

    return wrapper


def cache_ratings(games_func: Callable[[str], list[tuple[str, str]]]):
    def final_function(
        games_file: str,
        cache_key: str,
        convergence: float | None = None,
        parity: float | None = None,
        ratings: dict[str, tuple[float, float]] = None,
        teams: list[str] | None = None,
    ) -> tuple[float, float, dict[str, tuple[float, float]]]:
        with open("RatingsCache.json", "r+") as cache_file:
            cache: dict[str, tuple[float, float, dict[str, tuple[float, float]]]] = (
                json.load(cache_file)
            )
            games = games_func(games_file)
            if parity is None:
                if ratings:
                    parity = calc_parity(games, ratings)
                elif cache_key in cache and cache[cache_key][0] > convergence:
                    parity, ratings = cache[cache_key][1:]
            if cache_key not in cache or parity is not None:
                cache[cache_key] = variadic_call(iter_ratings)(
                    games,
                    convergence=convergence,
                    parity=parity,
                    ratings=ratings,
                    teams=teams,
                )
                try:
                    cache_file.seek(0)
                    json.dump(cache, cache_file)
                except Exception as e:
                    print()
                    print(cache)
                    print("CACHE WARNING")
                    print(e)
                    print()
                    breakpoint()
        return cache[cache_key]

    return final_function


def fbs_with_fcs(year_selected: int, week_selected: int, convergence: float = 1e-3):
    file = f"{year_selected}.csv"

    @cache_ratings
    @csv2list
    @add_week_filter(week_selected, file)
    @add_division_filter("fbs")
    def fbs_squashed(*args):
        return args

    @cache_ratings
    @csv2list
    @add_week_filter(week_selected, file)
    @add_division_filter("fcs")
    def fcs_squashed(*args):
        return args

    @cache_ratings
    @csv2list
    @add_week_filter(week_selected, file)
    @add_division_filter("fbs", squash_others=False)
    def fbs_full(*args):
        return args

    tag = f"{year_selected}w{week_selected:02}"
    squashed = fbs_squashed(file, tag + "fbsq", convergence=convergence)[2]
    mu, sigma = squashed.pop("FCS                                     0         ")
    fcs_in_fbs = {
        k: (v[0] * sigma + mu, v[1] * sigma + sigma)
        for k, v in fcs_squashed(file, tag + "fcsq", convergence=convergence)[2].items()
    }
    del fcs_in_fbs["FBS                                     0         "]
    return fbs_full(
        file,
        tag + "fbs",
        convergence=convergence,
        ratings={team: (0.0, 1.0) for team in squashed} | fcs_in_fbs,
        teams=list(squashed),
    )


def print_ratings(ratings: dict[str, tuple[float, float]]):
    for k, v in sorted(
        ratings.items(),
        key=lambda x: x[1][0],
        reverse=True,
    ):
        print(f"{k}: {v[0]:.{CONVERGENCE_DIGITS}f},  σ = {v[1]:.2f}")


def get_fbs_ratings(year: int, week: int) -> dict[str, tuple[float, float]]:
    with open("RatingsCache.json", "r") as cache_file:
        cache = json.load(cache_file)
        if (cache_key := f"{year}w{week:02}fbs") in cache:
            out = cache[cache_key][2]
        else:
            out = fbs_with_fcs(year, week, _CONVERGENCE)[2]
    return {k[:TEAM_NAME_LENGTH].strip(): v for k, v in out.items()}


if __name__ == "__main__":
    year = int_input("Year: ", 2024)
    week = int_input("Week: ", 21)
    print_ratings(get_fbs_ratings(year, week))
