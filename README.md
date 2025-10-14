# 327-Project

## Files

- Assets: the graphical assets for the game. Currently, just a background.
- Testing: files that aren't part of the game, but show stuff that we'll need to add
- Bullet: a bullet class for the player to shoot. This bullet colliding with another player will trigger an RPC on that player's computer
  - I'm pretty sure this is HORRIBLE design, but he wants RPC implemented so
- Button: a button class that the player can press.
- Main: run this one

in one terminal do python main.py and click the white button
in another terminal do python main.py and click the green button

you should get two windows and you should see two players (squares)

use wasd for player movement

currently, one of the threads handles chat input on both host and client, using the input() function so chat can run in the terminal. Eventually, it will be put in-game, but currently, you need to press enter so the thread to stop hanging and the program fully exits. 
