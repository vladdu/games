# Board games

Terminal board games in Python: tic-tac-toe and Connect Four. Play against
the computer, against another person at the same terminal, or watch the
computer play itself.

Every game's computer uses the same depth-limited alpha-beta search with
depth-aware scoring: it takes the fastest win available and delays any loss as
long as possible. In tic-tac-toe it searches to the end of the game, so it is
unbeatable; in Connect Four it looks 6 moves ahead. You can make it weaker (or
stronger) with `--depth`.

Requires Python 3.10+ and the [rich](https://github.com/Textualize/rich)
library for the terminal UI. The project is managed with
[uv](https://docs.astral.sh/uv/); set it up (a virtualenv with rich, the
package and its scripts, and ruff) with:

```sh
uv sync
```

## Play

```sh
uv run games
```

(`uv run python -m games` does the same.) This starts with a menu of the Game types:

```
Choose a game:
  1. Tic-tac-toe
  2. Connect Four

Game (1-2):
```

Type a number to pick one; anything else is refused and you are asked again,
and Ctrl+C or Ctrl+D quits. "Play again" after each game plays the same Game
type. To skip the menu, name the Game type with `--game`:

```sh
uv run games --game tictactoe
uv run games --game connect-four
```

An unknown name is an error that lists the valid names.
`uv run tictactoe` is a shortcut that starts tic-tac-toe directly; it
takes the same flags except `--game`. Run `uv run games --help` (or `-h`)
for a short summary of how to play.

### Players and Difficulty

By default you play the computer, and each game asks "Do you want to go
first?". To choose who plays each Side instead, use `--first` and `--second`
(each `human` or `computer`); the prompt is then skipped, and "Play again"
keeps the same Players:

```sh
uv run games --game connect-four --first human --second human   # hot-seat
uv run games --game tictactoe --first computer --second computer # watch
uv run games --first computer        # you play second against the computer
```

Giving only one of the two flags puts the other kind of Player on the other
Side. With one human the messages address you ("You win!"); otherwise the
opening line names each Side's Player (for example "Red: human, Yellow:
human" or "X: computer (full depth), O: computer (depth 3)"), the move prompt names the Side to move, and the end
message names the winner ("Red wins!").

`--depth N` sets the computer's Difficulty: how many moves ahead it looks
(1 or more). Without it, each Game type uses its own default: tic-tac-toe
searches to the end of the game (unbeatable), Connect Four looks 6 moves
ahead. At any limited depth the tic-tac-toe computer can be beaten. Large
depths make Connect Four slow (depth 7 already takes a few seconds a move).
The flags also apply after the menu.

The code lives in the `games` package. `games/framework.py` holds what every
Game type shares: the Game type interface, the Game loop, Game events, the
human and computer Players, the terminal Player I/O and the Session.
`games/tictactoe.py` and `games/connectfour.py` each hold one Game type: its
rules, board rendering and the heuristic score the shared search uses.
`games/registry.py` lists the Game types by name, `games/cli.py` is the
command line, and `games/__main__.py` is the entry point. Adding a Game type
takes only its module and an entry in the registry: the menu and `--help`
are built from the registry.

## Tic-tac-toe

Against the computer you choose whether to go first (you are X if you go
first, O otherwise; X always moves first). The board is drawn as a grid, and each empty cell shows
its number (1-9), laid out like a numeric keypad:

```
┏━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃       ┃       ┃       ┃
┃   7   ┃   8   ┃   9   ┃
┃       ┃       ┃       ┃
┣━━━━━━━╋━━━━━━━╋━━━━━━━┫
┃       ┃       ┃       ┃
┃   4   ┃   5   ┃   6   ┃
┃       ┃       ┃       ┃
┣━━━━━━━╋━━━━━━━╋━━━━━━━┫
┃       ┃       ┃       ┃
┃   1   ┃   2   ┃   3   ┃
┃       ┃       ┃       ┃
┗━━━━━━━┻━━━━━━━┻━━━━━━━┛
```

Colors: X is bold cyan, O is bold magenta, and the guide numbers in empty
cells are dim grey. The most recent move is shown in reverse video,
and when someone wins, the three winning cells are highlighted on a green
background. Error messages are red, and the result is green (win), red (loss)
or yellow (draw). When output is not a terminal (for example when piped),
rich leaves out the colors.

Enter a cell number to move. Invalid input (non-numbers, out-of-range numbers,
occupied cells) re-prompts you. After each game you can play again (y/n).
Press Ctrl+C or Ctrl+D to quit at any time.

Input comes from stdin, so the game can be scripted:

```sh
printf '1\ny\n5\n8\n4\n3\n1\nn\n' | uv run games
```

## Connect Four

Connect Four is played on a 7×6 board. Red always moves first; against the
computer you choose whether to go first (you are Red if you do, Yellow otherwise). Type a column
number from 1 to 7 to drop a disc: it falls to the lowest empty row of that
column. Four in a row horizontally, vertically or diagonally wins, and a full
board without one is a draw. Input that isn't a number, a column outside
1-7, and a full column are refused, and you are asked again.

The board uses the same heavy-lined grid, with the column numbers above it:

```
┏━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┓
┃ 1 ┃ 2 ┃ 3 ┃ 4 ┃ 5 ┃ 6 ┃ 7 ┃
┣━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━┫
┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃
┣━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━┫
...
┣━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━┫
┃ Y ┃   ┃   ┃ R ┃ R ┃   ┃   ┃
┗━━━┻━━━┻━━━┻━━━┻━━━┻━━━┻━━━┛
```

Red discs (R) are bold red and Yellow discs (Y) bold yellow. The most recent
move is shown in reverse video, and the winning four get a green background.

The computer is beatable: it uses a depth-limited alpha-beta search (6 moves
ahead) that scores unfinished positions by their open windows of four. It
takes a win when it has one, blocks yours, and answers in well under a
second. Ties between equally good columns are broken in a fixed order (centre
first), so it always plays the same way in the same position.

## Tests

```sh
uv run python -m unittest -v
uv run ruff check .
```

Ruff is configured in `pyproject.toml`.

The tic-tac-toe tests cover winner detection, input parsing, board rendering (grid lines,
glyphs and cell styles), the AI taking immediate wins
and blocking immediate losses, and an exhaustive search over every possible
human move sequence (with the AI playing first and second) checking that the
AI never loses.

Whole games are tested in-process: the game talks to the human only through a
small Player I/O interface, so the tests play it with a scripted adapter and
check the Game events (moves, rejected moves and the result). Every Game type
plays through the one Game loop in `games/framework.py`, and
`tests/test_game_types.py` is a shared suite every registered Game type must
pass (random playouts end with a result, legal moves are accepted, rejected
moves are refused with a reason, typed moves parse back to the same move).
The tests live in `tests/`. A golden-transcript test pipes a scripted session
through the real program (both the `tictactoe` script and
`python3 -m games --game tictactoe`) and compares its output with
`golden_transcript.txt`; if you change the terminal output on purpose,
regenerate that file with the input listed in the test. The startup menu has
its own golden transcript, `golden_menu_transcript.txt` (tests in
`tests/test_menu.py`): the menu with some refused choices, then the same
tic-tac-toe session.
The Connect Four tests (`tests/test_connectfour.py`) cover the rules, whole
Games played with a scripted Player I/O (including refused moves), the
computer taking a win and blocking one from set-up positions, the board
rendering (column header, colors and highlights), and the command line
(`--game`, `--help` and an unknown Game type).
`tests/test_players.py` covers choosing Players and Difficulty: hot-seat and
computer-vs-computer Games played in-process, the intro and end messages for
each pairing of Players, and the `--first`, `--second` and `--depth` flags
(including invalid values and `--help`) run through the real program.
Domain terms are defined in [GLOSSARY.md](GLOSSARY.md).
