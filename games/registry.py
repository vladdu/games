"""The Game type registry: every Game type the program can play, by the
name used on the command line. To add a Game type, write its module and add
its ``GAME_TYPE`` here."""

from games import connectfour, tictactoe

GAME_TYPES = {
    game_type.name: game_type
    for game_type in (tictactoe.GAME_TYPE, connectfour.GAME_TYPE)
}
