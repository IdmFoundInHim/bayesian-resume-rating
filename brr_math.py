import datetime
import os
import typing

import numpy as np
import scipy.integrate as integrate
import scipy.optimize as optimize

from data import BIG_TEN_TEAMS, B1G_2024_FOOTBALL

prob_err_tracker = 0.0


def calc_win_probability(
    win_team: tuple[float, float], lose_team: tuple[float, float], parity: float
) -> float:
    integral = integrate.quad(
        lambda x: np.exp(-np.square(x) / 2) / np.sqrt(2 * np.pi),
        -np.inf,
        (win_team[0] - lose_team[0])
        / np.sqrt(
            2 * np.square(parity) + np.square(win_team[1]) + np.square(lose_team[1])
        ),
    )
    global prob_err_tracker
    prob_err_tracker = max(prob_err_tracker, integral[1])
    return integral[0]


def calc_parity(
    season: list[tuple[str, str]], ratings: dict[str, tuple[float, float]]
) -> float:
    def difficulty_of_fit(y: float, parity: float, winner: str, loser: str) -> float:
        DENOMINATOR = np.sqrt(2 * np.pi)
        sigma = np.sqrt(np.square(ratings[loser][1]) + np.square(ratings[winner][1]))
        exponent = -np.square(y - ratings[loser][0] + ratings[winner][0]) / (2 * sigma)
        cumulative = integrate.quad(
            lambda x: np.exp(-np.square(x) / 2) / DENOMINATOR,
            -np.inf,
            y / (parity * np.sqrt(2)),
        )[0]
        return np.exp(exponent) / sigma / DENOMINATOR * np.square(cumulative)

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

    result = optimize.minimize_scalar(curve, (0.05, 50))
    # Bracket found using calc_parity([('B', 'A')], {'A': (0, 1), 'B': (0, 1)})
    # Lower chosen with low value that still yields accurate (big) result
    # Without bracket, the value is between 1e9 and 1e10
    # Really, any parity over 50 is useless; this could be brought down
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

    out = {}
    for team in current_ratings:
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
        out[team] = (rating, np.sqrt(variance_numerator[0] / denominator[0]))
        print(
            f"{team}: {tuple(map(lambda x: float(typing.cast(np.float64, x)), out[team]))}"
        )
    return out


def iter_ratings(
    season: list[tuple[str, str]],
    convergence: float = 1e-3,
    parity: float = 1.0,
    ratings: dict[str, tuple[float, float]] | None = None,
):
    if ratings is None:
        ratings = {team: (0, 1) for game in season for team in game}
    with open(f"run_{datetime.datetime.now().isoformat()}.py", "w") as f:
        iteration_done = 0
        while (
            not iteration_done
            or any(
                map(
                    lambda t: abs(ratings[t][0] - prev_ratings[t][0]) > convergence,
                    ratings,
                )
            )
            or abs(parity - prev_parity) > convergence
        ):
            prev_ratings = ratings
            prev_parity = parity
            ratings = next_ratings(season, parity, ratings)
            parity = calc_parity(season, ratings)
            iteration_done += 1
            f.write(
                f"iteration{str(iteration_done)} = {repr((season, ratings, parity))}\n"
            )
            f.flush()
    return ratings, parity, abs(parity - prev_parity)


iter_ratings(B1G_2024_FOOTBALL, 0, np.float64(1.1352629751334307), {'Michigan State': (-0.446612402986514, np.float64(0.6299927515437171)), 'Maryland': (-1.145752407337535, np.float64(0.6560008000574526)), 'Indiana': (1.0486045161890327, np.float64(0.6663171269574972)), 'UCLA': (-0.3024910390763602, np.float64(0.6175605633998039)), 'Illinois': (0.5333498057597115, np.float64(0.6352441927480652)), 'Nebraska': (-0.5692673780887006, np.float64(0.6197395119129336)), 'Michigan': (0.3398603488036836, np.float64(0.6094885577217435)), 'USC': (-0.2566979098331808, np.float64(0.602197031510324)), 'Washington': (0.014896931866371083, np.float64(0.6150295122638711)), 'Northwestern': (-0.9510799312136184, np.float64(0.6441960230806807)), 'Iowa': (0.2915162374777082, np.float64(0.6074020811127141)), 'Minnesota': (0.17221361055241285, np.float64(0.6059659583987067)), 'Rutgers': (-0.3486533757724495, np.float64(0.5895486017493541)), 'Purdue': (-1.6106565483431774, np.float64(0.7045829292687711)), 'Wisconsin': (-0.5758237941606764, np.float64(0.6280676128026477)), 'Ohio State': (0.6541515171169094, np.float64(0.631618504783186)), 'Penn State': (1.587488098951568, np.float64(0.700217552846073)), 'Oregon': (1.5891412586153664, np.float64(0.7006615939895392))})
