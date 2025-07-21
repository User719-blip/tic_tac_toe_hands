# 🖐️ Hand-Controlled Tic Tac Toe Game

This interactive Tic Tac Toe game lets two players compete using just their hands! By showing different numbers of fingers on each hand,
you can place your moves on the board without ever touching a keyboard or mouse.

---

## 🛠️ Prerequisites

Before running the game, make sure you have the following installed:

### Python Dependencies

Install these using `pip`:
```bash
pip install opencv-python mediapipe pygame
```

### Image Assets
- allready provided

## Installation 

Clone repo 
```
git clone https://github.com/User719-blip/tic_tac_toe_hands
```
then create the python virtual env

## 🎮 How to Play Using Hand Gestures

The game allows players to select Tic Tac Toe squares by showing **1 to 3 fingers** on each hand.

### 🧠 Control Mapping

- **Left Hand → Column Selection**
  - 1 finger = Column 1 (left)
  - 2 fingers = Column 2 (middle)
  - 3 fingers = Column 3 (right)

- **Right Hand → Row Selection**
  - 1 finger = Row 1 (top)
  - 2 fingers = Row 2 (middle)
  - 3 fingers = Row 3 (bottom)

**For example:**  
✌️ Left Hand (2 fingers) + 🤟 Right Hand (3 fingers) → Selects **cell (Column 2, Row 3)**

### 🕒 Stability Detection

To confirm a move:
1. Hold your finger count steady for **0.3 seconds**.
2. The system detects stable hand gestures.
3. If the selected cell is empty, the move is placed.

### 🔄 Turn-Based Play

- Players alternate between **'X'** and **'O'**.
- You don’t need to press anything—just show your fingers!

### 🛑 Ending the Game

- A win or tie ends the game automatically with a display message.
- To exit manually, press **Q** in the webcam preview window or close the display.

---

## ✋ Helpful Tips

- Make sure your fingers are well-lit and clearly visible.
- Avoid rapid movements—hold your pose until the move registers.
- If no hands are detected, the game waits until gestures reappear.





 
