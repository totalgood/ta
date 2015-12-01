TA (Text Adventure)
===================

This is a text adventure game that uses Python's builtin `cmd` and `textwrap` modules to interact with the user on the command line. It uses the builtin `json` module to read a json file where you can define the "Finite State Machine" that is the world you explore within the game. A 9-yr-old girl named "Ella" and her cousins created and debugged the json file `the-magic-mission.json` that creates the world you inhabit in this game. This is the default world you load with the command `python story.py`.

The `story.py` engine that parses the json file and provides the game interface is a barely-improved fork of ["Text Adventure Demo"](https://github.com/asweigart/textadventuredemo) by [Al Sweigart](mailto:al@inventwithpython.com). [His tutorial](http://inventwithpython.com/blog/2014/12/04/making-a-text-adventure-game-with-the-cmd-and-textwrap-modules) explains all the elements of the game engine, if you want to learn more.

