from flask import Flask, render_template
from app_earn.scraper import fetch_all_results, extract_draws, split_by_position
from app_earn.analyzer import compute_position_frequencies, get_top_n
from app_earn.generator import generate_games

app = Flask(__name__)

CACHE = {}

pos_names = ["1ª Posição", "2ª Posição", "3ª Posição", "4ª Posição", "5ª Posição", "6ª Posição"]


def load_data():
    if CACHE:
        return CACHE

    data = fetch_all_results()
    draws = extract_draws(data)
    positions = split_by_position(draws)
    pos_freq = compute_position_frequencies(positions)
    games = generate_games(pos_freq)

    pos_top5 = []
    for idx in range(6):
        top5 = get_top_n(pos_freq[idx], 5)
        pos_top5.append([{"rank": r, "num": num, "count": count} for r, (num, count) in enumerate(top5, 1)])

    games_data = []
    labels = [
        "1º mais freq. de cada posição",
        "2º mais freq. de cada posição",
        "3º mais freq. de cada posição",
        "4º mais freq. de cada posição",
        "5º mais freq. de cada posição",
        "6º mais freq. de cada posição",
    ]
    for i, (game, label) in enumerate(zip(games, labels), 1):
        games_data.append({"id": i, "label": label, "numbers": sorted(game)})

    CACHE["total_draws"] = len(draws)
    CACHE["first_date"] = data[-1]["data"]
    CACHE["last_date"] = data[0]["data"]
    CACHE["last_concurso"] = data[0]["concurso"]
    CACHE["total_contests"] = len(data)
    CACHE["pos_top5"] = pos_top5
    CACHE["games"] = games_data

    return CACHE


@app.route("/")
def index():
    cache = load_data()
    return render_template(
        "index.html",
        total_contests=cache["total_contests"],
        total_draws=cache["total_draws"],
        first_date=cache["first_date"],
        last_date=cache["last_date"],
        last_concurso=cache["last_concurso"],
        pos_top5=cache["pos_top5"],
        games=cache["games"],
        pos_names=pos_names,
    )


@app.route("/refresh")
def refresh():
    CACHE.clear()
    return index()


if __name__ == "__main__":
    import socket
    hostname = socket.gethostname()
    print("Carregando dados da Mega-Sena...")
    load_data()
    print(f"Servidor rodando em http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
