# ChineseChess-GUI
This is a minimal GUI version of the Chinese Chess, I implemented it only via `tkinter` library.

# How to run it
Just download the `cchess.py` python file and run it, then the GUI will apear and you can play Chinese chess with AI opponent!

![image](https://github.com/user-attachments/assets/c0ae5f69-b1f9-453b-8f84-ee7c7f1ff036)

# About the implementation
The algorithm of AI opponent to find a best move is [Minimax](https://en.wikipedia.org/wiki/Minimax) in game theory.

The depth of Minimax search tree determines how clever the AI opponent will be. In the GUI, I provide a button `Difficulty` for you to adjust the smartness of AI opponent. 

Also you can decide whether you go first or AI go first via a check button.

If you try to move a piece in the wrong way, a warning information will appear in the bottom of GUI and your move will be invalid.
