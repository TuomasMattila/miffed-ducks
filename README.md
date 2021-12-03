# miffed-ducks
A Wee Bit Miffed Ducks: A game where you shoot ducks at objects.
Elementary programming 2021 course project.

![Alt text](sprites/duck.png "Duck")

Author: Tuomas Mattila

Uses sweeperlib (author: Mika Oja, University of Oulu).

The game includes two game modes: normal levels and randomly generated
levels. In both game modes, the goal is to destroy the wooden boxes.

![Alt text](sprites/target.png "Target")

## Normal levels:
- 2 levels.
- Pre-defined amount of ducks.
- Player may reset a level anytime.
- Player wins after passing both levels.

## Randomized levels:
- Unlimited amount of levels.
- The first level has two boxes: one target and one obstacle.
- After passing a level, the amount of boxes increases by two.
- Half of the boxers are targets, other half obstacles.
- Player has the same amount of ducks as there are boxes, however, the
  maximum number of ducks is limited to 20.
- Only the first level can be reset.
- If the player fails to destroy all of the targets in a level the game
  is over and the amount of passed levels is displayed.

## Controls:
### General:
- F: Toggle fullscreen on/off
- Q: Quit the game
- M: Menu
### In menu:
- P: Play levels
- R: Play random levels
### In game:
- R: Restart level (only normal levels and the first random level)
- ←/→ or mouse drag: Set angle
- ↑/↓ or mouse drag: Set Force
- Space or mouse release: Launch
