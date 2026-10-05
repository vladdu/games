# Board games

Terminal board games in Python where you play against the computer:
tic-tac-toe and Connect Four.

Every game's computer uses the same depth-limited alpha-beta search with
depth-aware scoring: it takes the fastest win available and delays any loss as
long as possible. In tic-tac-toe it searches to the end of the game, so it is
unbeatable; in Connect Four it looks 6 moves ahead.

Requires Python 3 and the [rich](https://github.com/Textualize/rich) library
for the terminal UI. Install it with:

```sh
pip install -r requirements.txt
```

## Play

```sh
python3 -m games
```

This starts with a menu of the Game types:

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
python3 -m games --game tictactoe
python3 -m games --game connect-four
```

An unknown name is an error that lists the valid names.
`python3 tictactoe.py` is a shortcut that starts tic-tac-toe directly. Run
`python3 -m games --help` (or `-h`) for a short summary of how to play.

The code lives in the `games` package. `games/framework.py` holds what every
Game type shares: the Game type interface, the Game loop, Game events, the
human and computer Players, the terminal Player I/O and the session.
`games/tictactoe.py` and `games/connectfour.py` each hold one Game type: its
rules, board rendering and (for now) its own computer search.
`games/registry.py` lists the Game types by name, and `games/__main__.py` is
the entry point.

## Tic-tac-toe

You choose whether to go first (you are X if you go first, O otherwise; X
always moves first). The board is drawn as a grid, and each empty cell shows
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
printf '1\ny\n5\n8\n4\n3\n1\nn\n' | python3 -m games
```

## Connect Four

Connect Four is played on a 7×6 board. Red always moves first; you choose
whether to go first (you are Red if you do, Yellow otherwise). Type a column
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
python3 -m unittest -v
```

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
through the real program (both `python3 tictactoe.py` and
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
Domain terms are defined in [GLOSSARY.md](GLOSSARY.md).
