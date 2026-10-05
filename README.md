# Tic-tac-toe

A terminal tic-tac-toe game in Python where you play against the computer.
The computer uses full minimax search (with alpha-beta pruning and
depth-aware scoring), so it is unbeatable: it never loses, takes the fastest
win available, and delays any loss as long as possible.

Requires Python 3 and the [rich](https://github.com/Textualize/rich) library
for the terminal UI. Install it with:

```sh
pip install -r requirements.txt
```

## Play

```sh
python3 tictactoe.py
```

You choose whether to go first (you are X if you go first, O otherwise; X
always moves first). The board is drawn as a grid, and each empty cell shows
its number (1-9):

```
┏━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃       ┃       ┃       ┃
┃   1   ┃   2   ┃   3   ┃
┃       ┃       ┃       ┃
┣━━━━━━━╋━━━━━━━╋━━━━━━━┫
┃       ┃       ┃       ┃
┃   4   ┃   5   ┃   6   ┃
┃       ┃       ┃       ┃
┣━━━━━━━╋━━━━━━━╋━━━━━━━┫
┃       ┃       ┃       ┃
┃   7   ┃   8   ┃   9   ┃
┃       ┃       ┃       ┃
┗━━━━━━━┻━━━━━━━┻━━━━━━━┛
```

Colors: X is bold cyan, O is bold magenta, and the guide numbers in empty
cells are dim grey. The computer's most recent move is shown in reverse video,
and when someone wins, the three winning cells are highlighted on a green
background. Error messages are red, and the result is green (win), red (loss)
or yellow (draw). When output is not a terminal (for example when piped),
rich leaves out the colors.

Enter a cell number to move. Invalid input (non-numbers, out-of-range numbers,
occupied cells) re-prompts you. After each game you can play again (y/n).
Press Ctrl+C or Ctrl+D to quit at any time.

Input comes from stdin, so the game can be scripted:

```sh
printf 'y\n5\n2\n4\n9\n7\nn\n' | python3 tictactoe.py
```

## Tests

```sh
python3 -m unittest -v
```

The tests cover winner detection, input parsing, board rendering (grid lines,
glyphs and cell styles), the AI taking immediate wins
and blocking immediate losses, and an exhaustive search over every possible
human move sequence (with the AI playing first and second) checking that the
AI never loses.
