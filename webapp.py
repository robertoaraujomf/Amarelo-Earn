#!/usr/bin/env python3
"""DEPRECADO: use 'python generate.py' para gerar uma página HTML estática.

Antigo servidor Flask foi substituído pelo gerador de página estática
que não precisa de localhost.
"""

import sys
from pathlib import Path

print("=" * 62)
print("  AVISO: webapp.py foi substituído!")
print("=" * 62)
print()
print("  Este projeto não precisa mais de um servidor web (localhost).")
print()
print("  Para gerar a página HTML estática:")
print(f"    python {Path(__file__).parent / 'generate.py'}")
print()
print("  ou execute o analisador no terminal:")
print(f"    python {Path(__file__).parent / 'main.py'}")
print()
print("  Após gerar o HTML, abra o arquivo index.html no navegador.")
print("=" * 62)
sys.exit(1)
