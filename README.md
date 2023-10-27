# Tic-Tac-Toe
GUI Tic Tac Toe game implemented in PyQt6 with AI players and animation and GUI customization

![2023-10-28_011616](https://github.com/Estrangeling/Tic-Tac-Toe/assets/78679218/78370d9d-e453-41cd-864c-d53931123119)
![2023-10-28_011643](https://github.com/Estrangeling/Tic-Tac-Toe/assets/78679218/d4509253-194e-4566-988c-cde4eb5e1820)
![2023-10-28_011630](https://github.com/Estrangeling/Tic-Tac-Toe/assets/78679218/accd00ab-b7e2-4c2b-82a0-ce913020486c)
![2023-10-28_011146](https://github.com/Estrangeling/Tic-Tac-Toe/assets/78679218/b96aae58-ed56-478a-ac6e-21d1b1ea0ee0)
![2023-10-28_011510](https://github.com/Estrangeling/Tic-Tac-Toe/assets/78679218/e94aede0-29f4-4e5a-afab-da2463025d50)
![2023-10-28_011337](https://github.com/Estrangeling/Tic-Tac-Toe/assets/78679218/81c1916a-b1a3-47b8-bc55-c65f2833027b)



Features: six AI players with varying level of skills, each can be played against, or you can let them fight each other.

The AIs are Novice AI, Adept AI, Master AI, Master AI+, Super AI, and Super AI+. 

Novice AI starts out choosing moves completely randomly, and it gradually improves as it plays the game. It remembers every state and every move that lead to the state, and will adjust the weights of the options according to the outcome of the game, 
so that the actions that lead to a win is more likely to be chosen when the same state is encountered, and moves that lead to a tie are also given increased weights, albeit slightly less than that lead to wins. Mistakes that cause a loss will be less likely to be repeated.

Adept AI chooses the moves completely randomly, but only when there aren't two of the same pieces in the same line and the third place is vacant. In this case, it will always choose the empty spot to fill the gap, either to win the game or to prevent the other player from winning.

Master AI uses a tree structure that was systematically created to include all 8533 possible board states (without considering rotations and reflections) reachable via gameplay, and the structure encodes the information about all possible states that can follow 
the next state that is reached by the next move, for all possible moves that are legal given the state. Each move and state is given a score based on how many win states, loss states and tie states that can follow the state or the state reached by making the move.

Master AI, in addition to always fill the vacant spot when there are two of the same piece on a line and the third spot is empty, will randomly choose a move based on the score of the next state that follows from the move, moves that lead to more win states are more likely to be chosen
than moves that lead to more loss states. If there are no moves that lead to wins, it then chooses a move that leads to more tie states. If it can only lose, then it just chooses completely randomly.

In practice, Master AI will always choose a good enough move and it doesn't make beginner mistakes, it is a force to be reckoned with.

Master AI+, in addition to using the same strategy and tree structure as Master AI, will choose a move that leads to more win states and also less tie states, the number of tie states is subtracted from the number of win states, the minimum win score is 0, which means Master AI+ will choose a move that leads to less ties.

Super AI also fills the gap, and it also uses the same tree structure, but instead of choosing randomly, it will always choose the best move given the same board state without failure. Super AI+ also chooses moves that leads to more wins and less ties.

Super AI+ is exactly impossible to beat if it moves first.

The playing pieces representing the players can be customized, in addition to the standard X and O shapes, there are 24 shapes in total to choose from to use as playing pieces, and you can also choose the colors of the playing pieces, you can choose from all 16777216 RGB colors,
the colors are chosen either by using a dedicated dialog window, which is shown when the associated button is clicked, and lets you see the color you chose, or by using the textbox that is specifically designed for this purpose, using the textbox is faster, but you won't have a preview.

And there are 27 blend modes to choose from to apply the color to the image and compose the final playing piece.

And there is a dedicated window to let you customize almost all components of the GUI, you can customize the background color, gradient, text color and border styles of the widgets, for each status a widget can be in. There is also an option to test your luck, a button that once clicked, will randomly change the color and border styles of every available settings chosen,
to get a completely different theme. The theme is almost certainly ugly, and it is designed to be so, because it is designed to choose things completely randomly, to be able to generate all possible themes. So that if you click the randomize button enough times, you might see a satisfactory theme that is almost guaranteed to be unique.

Of course if you don't like the new theme you can just revert it, or parts of it. There is also an option to restore all settings to default.

And there is some animation here, I don't know if it fits, and seemingly the animation is unnecessary and purposeless, but I just thought it would be funny to implement. If you press the run button, many widgets will periodically change states, the interval between changes is exactly 125 milliseconds, or one eighth of a second, many widgets will randomly change their styles and text and/or image every 0.125 seconds. And the animation will go on forever until it is manually paused or stopped, or your devices loses power.

Instructions on how to play:

First you need to download the entire repository (obviously), then you need to run `analyze_tic_tac_toe_states.py` once to generate the necessary data files needed for the AI players. Then you can just run the game anytime by running `main.py`.

I wrote every line of code entirely by myself without anyone else's help, and all artworks are created by me. You aren't authorized to plagiarize, you shouldn't falsely claim to be the project's author. You will be sued if I found out you steal the credit of my work. Be warned.
