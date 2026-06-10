#!/usr/bin/env python3
"""Generate a self-contained static HTML page with Mega-Sena analysis.
No Flask or web server needed — just open the generated file in a browser.
"""

import json
import os
import sys
import time
import webbrowser
from pathlib import Path

from app_earn.scraper import fetch_all_results, extract_draws, split_by_position
from app_earn.analyzer import compute_position_frequencies
from app_earn.generator import generate_games

OUTPUT = Path(__file__).parent / "index.html"

pos_names = ["1\u00aa Posi\u00e7\u00e3o", "2\u00aa Posi\u00e7\u00e3o", "3\u00aa Posi\u00e7\u00e3o",
             "4\u00aa Posi\u00e7\u00e3o", "5\u00aa Posi\u00e7\u00e3o", "6\u00aa Posi\u00e7\u00e3o"]

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #e0e0e0; min-height: 100vh; padding: 20px;
}
.container { max-width: 1060px; margin: 0 auto; }
.header { text-align: center; padding: 40px 20px 30px; }
.header h1 { font-size: 2.5rem; color: #ffd700; text-shadow: 0 0 20px rgba(255,215,0,0.3); letter-spacing: 2px; }
.header h1 span { display: inline-block; background: #ffd700; color: #1a1a2e; padding: 0 12px; border-radius: 8px; font-weight: 900; }
.header p { color: #aaa; margin-top: 8px; font-size: 0.95rem; }
.stats-bar {
  display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;
  background: rgba(255,215,0,0.08); border: 1px solid rgba(255,215,0,0.2);
  border-radius: 12px; padding: 16px 30px; margin-bottom: 30px;
}
.stats-bar .stat { text-align: center; }
.stats-bar .stat .value { font-size: 1.4rem; font-weight: 700; color: #ffd700; }
.stats-bar .stat .label { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
.section-title {
  font-size: 1.3rem; color: #ffd700; margin-bottom: 20px; padding-bottom: 8px;
  border-bottom: 2px solid rgba(255,215,0,0.2);
  display: flex; align-items: center; gap: 10px;
}
.section-title .badge { background: #ffd700; color: #1a1a2e; font-size: 0.75rem; padding: 2px 10px; border-radius: 20px; font-weight: 700; }
.pos-section { margin-bottom: 30px; }
.pos-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.pos-header h3 { color: #ffd700; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; }
.pos-header .top5-label { font-size: 0.75rem; color: #888; }
.freq-grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 4px; }
.freq-cell {
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);
  border-radius: 6px; padding: 4px 2px; text-align: center; font-size: 0.7rem;
  transition: transform 0.15s, border-color 0.15s; cursor: default; position: relative;
}
.freq-cell:hover { transform: scale(1.2); z-index: 10; border-color: #ffd700; }
.freq-cell .num { font-weight: 700; font-size: 0.8rem; color: #fff; }
.freq-cell .count { font-size: 0.6rem; color: #888; }
.freq-cell.top1 { background: rgba(255,215,0,0.25); border-color: #ffd700; }
.freq-cell.top1 .num, .freq-cell.top1 .count { color: #ffd700; }
.freq-cell.top2 { background: rgba(255,215,0,0.18); border-color: rgba(255,215,0,0.6); }
.freq-cell.top2 .num { color: #ffd700; }
.freq-cell.top3 { background: rgba(255,215,0,0.12); border-color: rgba(255,215,0,0.4); }
.freq-cell.top3 .num { color: #e6c200; }
.freq-cell.top4 { background: rgba(255,215,0,0.08); border-color: rgba(255,215,0,0.25); }
.freq-cell.top4 .num { color: #cca800; }
.freq-cell.top5 { background: rgba(255,215,0,0.05); border-color: rgba(255,215,0,0.15); }
.freq-cell.top5 .num { color: #b39100; }
.games-section { margin-bottom: 40px; }
.games-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.game-card {
  background: rgba(255,215,0,0.06); border: 1px solid rgba(255,215,0,0.2);
  border-radius: 14px; padding: 20px; text-align: center;
  transition: transform 0.2s, border-color 0.2s;
}
.game-card:hover { transform: translateY(-2px); border-color: #ffd700; }
.game-card .game-id { font-size: 1.5rem; font-weight: 900; color: #ffd700; margin-bottom: 4px; }
.game-card .game-label { font-size: 0.7rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }
.game-card .numbers { display: flex; justify-content: center; gap: 6px; flex-wrap: wrap; }
.game-card .numbers .ball {
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, #ffd700, #ffb300);
  color: #1a1a2e; font-weight: 800; font-size: 0.85rem;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 8px rgba(255,215,0,0.3);
}
.footer { text-align: center; padding: 30px; color: #666; font-size: 0.8rem; }
.footer a { color: #ffd700; text-decoration: none; }
.footer a:hover { text-decoration: underline; }
.disclaimer {
  background: rgba(255,215,0,0.06); border: 1px solid rgba(255,215,0,0.1);
  border-radius: 10px; padding: 14px 20px; text-align: center;
  color: #999; font-size: 0.82rem; margin-top: 20px;
}
.legenda {
  display: flex; gap: 16px; flex-wrap: wrap; margin: 16px 0 24px; justify-content: center;
}
.legenda-item { display: flex; align-items: center; gap: 6px; font-size: 0.72rem; color: #999; }
.legenda-item .box { width: 16px; height: 16px; border-radius: 3px; border: 1px solid rgba(255,215,0,0.3); }
.data-geracao { text-align: center; font-size: 0.75rem; color: #555; margin-top: 10px; }
@media (max-width:900px) { .freq-grid { grid-template-columns: repeat(10,1fr); } }
@media (max-width:768px) {
  .freq-grid { grid-template-columns: repeat(8,1fr); }
  .games-grid { grid-template-columns: repeat(2,1fr); }
  .header h1 { font-size: 1.8rem; }
}
@media (max-width:480px) {
  .freq-grid { grid-template-columns: repeat(6,1fr); }
  .games-grid { grid-template-columns: 1fr; }
}
"""


def build_html(total_contests, total_draws, first_date, last_date,
               pos_all, games, last_concurso):
    rows_pos = []
    for idx in range(6):
        top5_items = pos_all[idx][:5]
        top5_str = ", ".join(item["num"] for item in top5_items)

        cells = []
        for item in pos_all[idx]:
            tier = f"top{item['rank']}" if item["rank"] <= 5 else ""
            cells.append(
                f'<div class="freq-cell {tier}" '
                f'title="{item["num"]}: {item["count"]}x ({item["rank"]}\u00ba)">'
                f'<div class="num">{item["num"]}</div>'
                f'<div class="count">{item["count"]}x</div>'
                f"</div>"
            )

        rows_pos.append(f"""
        <div class="pos-section">
            <div class="pos-header">
                <h3>{pos_names[idx]}</h3>
                <span class="top5-label">Top 5: {top5_str}</span>
            </div>
            <div class="freq-grid">
                {''.join(cells)}
            </div>
        </div>""")

    games_cards = []
    for g in games:
        balls = "".join(
            f'<div class="ball">{n:02d}</div>'
            for n in g["numbers"]
        )
        games_cards.append(f"""
        <div class="game-card">
            <div class="game-id">JOGO {g['id']}</div>
            <div class="game-label">{g['label']}</div>
            <div class="numbers">{balls}</div>
        </div>""")

    generated_at = time.strftime("%d/%m/%Y \u00e0s %H:%M")

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Amarelo Earn — Mega-Sena Analyzer</title>
<style>{CSS}</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1><span>AMARELO</span> EARN</h1>
        <p>Analisador estat\u00edstico da Mega-Sena — frequ\u00eancia por posi\u00e7\u00e3o (01 a 60)</p>
    </div>

    <div class="stats-bar">
        <div class="stat">
            <div class="value">{total_contests}</div>
            <div class="label">Sorteios</div>
        </div>
        <div class="stat">
            <div class="value">{total_draws * 6}</div>
            <div class="label">Dezenas Processadas</div>
        </div>
        <div class="stat">
            <div class="value">{first_date} — {last_date}</div>
            <div class="label">Per\u00edodo</div>
        </div>
    </div>

    <div class="section-title">
        💡 Jogos Sugeridos
        <span class="badge">6 combina\u00e7\u00f5es</span>
    </div>

    <div class="games-section">
        <div class="games-grid">
            {''.join(games_cards)}
        </div>
    </div>

    <div class="section-title">
        📊 Frequ\u00eancia Completa por Posi\u00e7\u00e3o
        <span class="badge">60 n\u00fameros</span>
    </div>

    <div class="legenda">
        <div class="legenda-item"><div class="box" style="background:rgba(255,215,0,0.25);border-color:#ffd700;"></div> 1\u00ba</div>
        <div class="legenda-item"><div class="box" style="background:rgba(255,215,0,0.18);border-color:rgba(255,215,0,0.6);"></div> 2\u00ba</div>
        <div class="legenda-item"><div class="box" style="background:rgba(255,215,0,0.12);border-color:rgba(255,215,0,0.4);"></div> 3\u00ba</div>
        <div class="legenda-item"><div class="box" style="background:rgba(255,215,0,0.08);border-color:rgba(255,215,0,0.25);"></div> 4\u00ba</div>
        <div class="legenda-item"><div class="box" style="background:rgba(255,215,0,0.05);border-color:rgba(255,215,0,0.15);"></div> 5\u00ba</div>
        <div class="legenda-item"><div class="box" style="background:rgba(255,255,255,0.04);border-color:rgba(255,255,255,0.06);"></div> 6\u00ba+</div>
    </div>

    {''.join(rows_pos)}

    <div class="data-geracao">
        Gerado em {generated_at} — \u00daltimo concurso: {last_concurso} ({last_date})
    </div>

    <div class="disclaimer">
        ⚠️ Lembre-se: loteria \u00e9 jogo de azar. N\u00e3o existe garantia de ganho.
        Jogue com responsabilidade. Este app \u00e9 apenas uma ferramenta estat\u00edstica.
    </div>

    <div class="footer">
        <p>Amarelo Earn &copy; 2026 — Dados: Caixa Econ\u00f4mica Federal via API p\u00fablica</p>
    </div>
</div>
</body>
</html>"""


def run():
    print("=" * 62)
    print("  🏆  AMARELO EARN  -  Gerador de Página Estática")
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
    print(f"  ✔ 6 arrays criados")
    print()

    print("[4/4] Gerando página HTML...")
    pos_all = []
    for idx in range(6):
        items = []
        max_count = pos_freq[idx][0][1] if pos_freq[idx] else 1
        for rank, (num, count) in enumerate(pos_freq[idx], 1):
            items.append({
                "rank": rank,
                "num": f"{num:02d}",
                "count": count,
                "pct": (count / max_count) * 100,
            })
        pos_all.append(items)

    games_list = generate_games(pos_freq)
    labels = [
        "1º mais freq. de cada posição",
        "2º mais freq. de cada posição",
        "3º mais freq. de cada posição",
        "4º mais freq. de cada posição",
        "5º mais freq. de cada posição",
        "6º mais freq. de cada posição",
    ]
    games_data = [
        {"id": i, "label": label, "numbers": sorted(game)}
        for i, (game, label) in enumerate(zip(games_list, labels), 1)
    ]

    html = build_html(
        total_contests=len(data),
        total_draws=len(draws),
        first_date=data[-1]["data"],
        last_date=data[0]["data"],
        pos_all=pos_all,
        games=games_data,
        last_concurso=data[0]["concurso"],
    )

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"  ✔ Página salva: {OUTPUT}")
    print()

    print("=" * 62)
    print(f"  Arquivo: {OUTPUT}")
    print(f"  Basta abrir o arquivo no navegador (não precisa de servidor)")
    print("=" * 62)
    print()
    print("  Lembre-se: loteria é jogo de azar.")
    print("  Jogue com responsabilidade!")
    print("=" * 62)

    webbrowser.open(OUTPUT.resolve().as_uri())


if __name__ == "__main__":
    run()
