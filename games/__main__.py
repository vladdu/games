"""Entry point: ``python3 -m games [--game NAME] [--first KIND]
[--second KIND] [--depth N]``. Without ``--game`` a startup menu asks which
Game type to play."""

import sys

from games import cli

sys.exit(cli.main(None, "python3 -m games"))
