#!/usr/bin/env python3

import sys

if len(sys.argv) > 1 and sys.argv[1] in ("--web", "-w", "--generate", "-g"):
    from generate import run
    run()
else:
    from app_earn.cli import run
    run()
