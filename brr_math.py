import typing

import numpy as np
import scipy.integrate as integrate
import scipy.optimize as optimize
import scipy.special as special


def calc_win_probability(
    win_team: tuple[float, float], lose_team: tuple[float, float], parity: float
) -> float:
    delta = win_team[0] - lose_team[0]
    sigma = np.sqrt(
        np.square(parity) + np.square(win_team[1]) + np.square(lose_team[1])
    )
    return special.erf(delta / (np.sqrt(2) * sigma)) / 2 + 0.5


def calc_parity(
    season: list[tuple[str, str]], ratings: dict[str, tuple[float, float]]
) -> float:
    def difficulty_of_fit(y: float, parity: float, winner: str, loser: str) -> float:
        sigma = np.sqrt(np.square(ratings[loser][1]) + np.square(ratings[winner][1]))
        exponent = -np.square(y - ratings[loser][0] + ratings[winner][0]) / (2 * sigma)
        cumulative = special.erf(y / (2 * parity)) / 2 + 0.5
        return np.exp(exponent) / sigma / np.sqrt(2 * np.pi) * np.square(cumulative)

    def curve(p: float) -> float:
        return sum(
            integrate.quad(
                lambda y: difficulty_of_fit(y, p, winner, loser),
                -np.inf,
                np.inf,
                limit=1000,
            )[0]
            for winner, loser in season
        )

    result = optimize.minimize_scalar(curve, (0.5, 5))
    # Bracket found using calc_parity([('B', 'A')], {'A': (0, 1), 'B': (0, 1)}) was (.05, 1e10)
    print(result)
    return result.x


# calc_parity([('B', 'A')], {'A': (0, 1), 'B': (0, 1)})
# calc_parity(
#    B1G_2024_FOOTBALL,
#    {
#        t: ((len([g for g in B1G_2024_FOOTBALL if g[0] == t]) - 6) / 10, 1)
#        for t in BIG_TEN_TEAMS
#    },
# )


# The initial prior is that every team is a standard normal distribution
def next_ratings(
    season: list[tuple[str, str]],
    parity: float,
    current_ratings: dict[str, tuple[float, float]],
    teams: list[str] | None = None,
) -> dict[str, tuple[float, float]]:
    def season_probability(team: str, rating: float) -> float:
        games = []
        for game in filter(lambda x: team in x, season):
            if game[0] == team:
                winner = (rating, 0)
                loser = current_ratings[game[1]]
            else:
                winner = current_ratings[game[0]]
                loser = (rating, 0)
            games.append(calc_win_probability(winner, loser, parity))
        return typing.cast(float, np.prod(games))

    ratings = current_ratings.copy()
    for team in teams or current_ratings:
        numerator = integrate.quad(
            lambda x: x
            * np.exp(-np.square(x) / 2)
            / np.sqrt(2 * np.pi)
            * season_probability(team, x),
            -np.inf,
            np.inf,
        )
        denominator = integrate.quad(
            lambda x: np.exp(-np.square(x) / 2)
            / np.sqrt(2 * np.pi)
            * season_probability(team, x),
            -np.inf,
            np.inf,
        )
        rating = numerator[0] / denominator[0]
        variance_numerator = integrate.quad(
            lambda x: np.square(rating - x)
            * np.exp(-np.square(x) / 2)
            / np.sqrt(2 * np.pi)
            * season_probability(team, x),
            -np.inf,
            np.inf,
        )
        ratings[team] = (rating, np.sqrt(variance_numerator[0] / denominator[0]))
        print(
            f"{team}: {tuple(map(lambda x: float(typing.cast(np.float64, x)), ratings[team]))}"
        )
    return ratings


def iter_ratings(
    season: list[tuple[str, str]],
    convergence: float = 1e-3,
    parity: float = 1.0,
    ratings: dict[str, tuple[float, float]] | None = None,
    teams: list[str] | None = None,
) -> tuple[float, float, dict[str, tuple[float, float]]]:
    if ratings is None:
        ratings = {team: (0.0, 1.0) for game in season for team in game}
    while True:
        prev_ratings = ratings
        prev_parity = parity
        ratings = next_ratings(season, parity, ratings, teams)
        parity = calc_parity(season, ratings)
        if (
            all(
                map(
                    lambda t: abs(ratings[t][0] - prev_ratings[t][0]) < convergence,
                    ratings,
                )
            )
            or abs(parity - prev_parity) > convergence
        ):
            return convergence, parity, ratings
