# C.H.E.S.S.
(Computing Homographies Every Stinkin' Second)
## Technical details
### Package Dependencies
#### Python libraries used:
* `OpenCV` 3.4.2
* `python-chess`
* `numpy`

You can download our Anaconda environment [here](www.google.com).
Python 3.7 was used in development.

### Usage
* Set working directory to `CHESS/main`.
* Set script path to `CHESS/main/main.py`
* Run `main.py` (if in PyCharm and script path is set, click `Run` button).

### Notes
* By default, C.H.E.S.S. will run with a pre-recorded video. This can be changed in the `ccv` object instantiation in `main.py`. Changing the `webcam` parameter from `False` to `True` accomplishes this.
* The `chess_icons` parameter in the `ccv` object instantiation can also be changed to the path of a chesspiece template.
  * Default: `chess_icons="../assets/chess_pieces.png"`
  * Alternate: `chess_icons="../assets/chess_pieces_alt.png"`

## Project Goals and Requirements

### Objective
We aim to create an augmented reality game of chess with no physical chess pieces; pieces are displayed on a video feed from a camera that is observing the board. Pieces shall be moved virtually by the user. For the initial implementation, the user will move a piece by clicking on the square of the piece it wishes to move and then clicking on the desired location for said pieces. As moves are made, the corresponding pieces are moved on screen. We plan to display the chess pieces as 2D pieces on the chessboard.

### Stretch Goals
  * The user can click and drag a piece instead of just clicking source and destination points. Specifically, moving the chess piece as the mouse is moving onscreen.
  * The user can use a set of ArUco markers to select and move a piece instead of using mouse input. For example, one ArUco marker can be placed on a square to select which piece the user wants to move; a second ArUco marker can be placed to select which square the user wants to move the piece to; a third marker can be placed to finalize the move.
  * The user can use a pinching hand gesture to select and move a piece instead of using mouse input.
  * Use 3D chess pieces.

### Approach
To approach the problem, we will use `cv2.findChessboardCorners()` to read the chessboard. This will give us each corner of the board, with which we can subdivide into each square. Since the chessboard is square (n × n), the previous function will not return the pose of the chessboard. To remedy this, we will use an ArUco marker to form a reference orientation of the board. <br />
We will need to track the location of each chess piece. To do this, we will have an array stored in our program that contains information about the position of each chess piece. This will be used for the game logic in addition to the Computer Vision techniques. We will then use this information in conjunction with intrensic and extrensic parameters to perform a homography transformation of the chess piece onto the board.

### Timeline
  * One-page proposal: 10/27/2021
  * Progress Report: 11/22/2021
  * Presentation (in-class): 12/03/2021
  * Project Report and Video: 12/13/2021
