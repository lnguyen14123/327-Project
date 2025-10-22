# 327-Project

## Files

- Assets: the graphical assets for the game. Currently, just a background.
- Testing: files that aren't part of the game, but show stuff that we'll need to add
- Utils: scripts to aid in development
- Milestone 2: Files needed for Milestone 2 (**Look in here, Dr. Ponce :]**)
- Bullet: a bullet class for the player to shoot other players with (curently unimplemented)
- Button: a button class that the player can click.
- Main: run this one
- Chat Pubsub: the publish-subscribe logic for handling chat and collisions
- Client: main loop for running the game as a client
- Host: main loop for running the game as a host
- Main Menu: the starting menu of the game, where the player chooses whether they want to start the game as a client or a host
- Main: entry point file (run this one :)
- Player: Class for the Player, containing keyboard input handling, movement specifics, etc


## How to run

### Method 1 (For testing chat locally)
1. Open 2 Terminals
2. In one terminal, run `python main.py` and click the white (host) button
3. In another terminal, run `python main.py` and click the green (connect) button

You should get two windows and you should see two players (squares)

### Method 2 (For testing >2 players locally)
1. Run `./utils/simload.sh x`, where x is the number of windows to open
2. On one window, click the white (host) button
3. Click the green (connect) button on all others

### Method 3 (For testing remotely)
1. On the host machine, run `ipconfig` (Windows) or `ip a` (Linux) to get the host IP
2. On the client machine, change the HOST_IP constant in client.py to the host machine's IP
3. Press the white (host) button on the host machine, and the green (connect) button on the client machine

**Note**: Currently, one of the threads handles chat input on both host and client, using the input() function so chat can run in the terminal. Eventually, it will be put in-game instead of the terminal, but currently, you need to press enter so the thread to stop hanging and the program fully exits (This is seemingly only a problem on Linux).
