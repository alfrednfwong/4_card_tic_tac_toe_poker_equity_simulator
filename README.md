# 4 card tic tac toe poker equity simulator

This is an equity calculator for the poker variant 4 Card Tic-tac-toe.

Each player has 4 hole cards. The board will form a 3x3 square, and players can make a final hand with any of their two hole cards plus any 3 cards on the board that forms a straight line, vertical, horizontal or diagonal.

On the flop the 4 corners of the board will be dealt, and on the turn, the 4 sides, with the river being the center card alone.

As a reference, check [this](http://gamerules.org/rules/tic-tac-toe-card-game/) out, except that in our variant each player is dealt 4 hole cards and must play 2 of them. 

As inputs, the simulator takes the number of players in the hand, hole cards and board cards (* for any card also accepted),  as inputs. Monte carlo simulation is then done to compute the pot equity (poker parlance, basically meaning the probability of winning, with ties being equally split between tied players) of each player.
