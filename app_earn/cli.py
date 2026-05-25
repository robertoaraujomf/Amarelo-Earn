import sys
import time

from app_earn.scraper import fetch_all_results, extract_draws, split_by_position
from app_earn.analyzer import compute_position_frequencies, get_top_n
from app_earn.generator import generate_games


def run():
    print("=" * 62)
    print("  🏆  AMARELO EARN  -  Mega-Sena Analyzer")
    print("  Analisando todos os resultados da Mega-Sena...")
    print("=" * 62)
    print()

    print("[1/4] Buscando todos os sorteios...")
    t0 = time.time()
    try:
        data = fetch_all_results()
    except Exception as e:
        print(f"  ERRO: {e}")
        sys.exit(1)
    t1 = time.time()
    print(f"  ✔ {len(data)} sorteios encontrados  ({t1 - t0:.1f}s)")
    print(f"  Período: {data[-1]['data']} a {data[0]['data']}")
    print()

    print("[2/4] Extraindo números sorteados...")
    draws = extract_draws(data)
    print(f"  ✔ {len(draws)} sorteios válidos")
    print()

    print("[3/4] Separando por posição...")
    positions = split_by_position(draws)
    pos_freq = compute_position_frequencies(positions)
    print(f"  ✔ 6 arrays criados ({len(positions[0])} números cada)")
    print()

    print("[4/4] ANÁLISE POR POSIÇÃO:")
    print("=" * 62)

    pos_names = ["1ª POSIÇÃO", "2ª POSIÇÃO", "3ª POSIÇÃO", "4ª POSIÇÃO", "5ª POSIÇÃO", "6ª POSIÇÃO"]

    for pos_idx in range(6):
        print()
        print(f"  ─── {pos_names[pos_idx]} ───")
        print()
        top5 = get_top_n(pos_freq[pos_idx], 5)
        for rank, (num, count) in enumerate(top5, 1):
            print(f"    {rank}º  Nº {num:02d}  →  {count}x sorteado nesta posição")

    print()
    print("=" * 62)

    print()
    print("  💡 6 JOGOS SUGERIDOS (1 número de cada posição por jogo):")
    print("  ─────────────────────────────────────────────────────")
    print()

    games = generate_games(pos_freq)

    labels = [
        "1º mais freq. de cada posição",
        "2º mais freq. de cada posição",
        "3º mais freq. de cada posição",
        "4º mais freq. de cada posição",
        "5º mais freq. de cada posição",
        "6º mais freq. de cada posição",
    ]

    for i, (game, label) in enumerate(zip(games, labels), 1):
        nums = " - ".join(f"{n:02d}" for n in game)
        print(f"  JOGO {i}  ({label})")
        print(f"  [{nums}]")
        print()

    print("=" * 62)
    print(f"  Total de sorteios: {len(draws)}")
    print(f"  Último concurso: {data[0]['concurso']} ({data[0]['data']})")
    print("=" * 62)
    print()
    print("  Lembre-se: loteria é jogo de azar.")
    print("  Jogue com responsabilidade!")
    print("=" * 62)
