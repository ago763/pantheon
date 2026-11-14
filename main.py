"""Entrada do jogo. Execute: python main.py."""

import os
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
if '--self-test' in sys.argv:
    os.environ['SDL_VIDEODRIVER']='dummy'

from goetia.app import Game


if __name__ == "__main__":
    if '--self-test' in sys.argv:
        from goetia.package_check import run
        index=sys.argv.index('--self-test')
        report=sys.argv[index+1] if index+1<len(sys.argv) else 'pantheon-self-test.json'
        sys.exit(run(report))
    else:
        Game().run()
