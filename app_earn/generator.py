from typing import List


def generate_games(position_frequencies: List[List[tuple]]) -> List[List[int]]:
    games = []
    used_global = set()

    for game_idx in range(6):
        game = []
        used_in_game = set()

        for pos_idx in range(6):
            ranked = position_frequencies[pos_idx]
            picked = False

            for num, _ in ranked:
                if num not in used_in_game and num not in used_global:
                    game.append(num)
                    used_in_game.add(num)
                    picked = True
                    break

            if not picked:
                for num, _ in ranked:
                    if num not in used_in_game:
                        game.append(num)
                        used_in_game.add(num)
                        break

        used_global.update(game)
        games.append(sorted(game))

    return games
