This is an AR based version of Hit-A-Mole game which you must have 
played at some point of time.

# Set-up
The set-up consists of a linear array of ArUco markers placed on some 
flat surface. A camera is placed so as to observe all these ArUco 
markers. The camera is placed either vertically above the markers or at 
some small angle. The screen is placed in front of the ArUco array where
the player can see his actions.

# Game
Just like in Hit-A-Mole, a mole appears through one of the holes, in this
game, on the screen a 3D image of a Monkey will be projected above one
of the ArUco markers chosen randomly. The player has to place his/her 
hand on that same ArUco marker, as if hitting the Monkey. As soon as the 
player misses a pre-set number of Monkeys, the game ends.

# Logic
The game is a finite state machine with three states as follows:  
1. Idle state
2. Start state
3. End state

IDLE STATE--(Keyboard Interrupt)-->START STATE--(x monkeys missed)-->END

END STATE--(Keyboard Interrupt)-->IDLE STATE

**Idle state:** The game is just displaying the Monkey over one of the 
ArUco markers chosen randomly.

**Start state:** The game displays monkey at a random position, and 
monitors if the monkey has been hit before it changes it's position after
a pre-set amount of time. The game keeps the count of the monkeys missed,
monkeys hit and the penalty of hitting wrong ArUco id. Once the player has
missed the pre-set number of monkeys, the game ends.

**End state:** The score card of the player is displayed.


