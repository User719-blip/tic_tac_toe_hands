import cv2
import mediapipe as mp
import time
import pygame as p

# Initialize MediaPipe hands and drawing utilities
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Function to count fingers based on landmarks
def count_fingers(hand_landmarks, hand_label):
    tips_ids = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    if hand_label == "Left":
        if hand_landmarks.landmark[tips_ids[0]].x < hand_landmarks.landmark[tips_ids[0] - 1].x:
            fingers.append(1)
        else:
            fingers.append(0)
    else:
        if hand_landmarks.landmark[tips_ids[0]].x > hand_landmarks.landmark[tips_ids[0] - 1].x:
            fingers.append(1)
        else:
            fingers.append(0)

    # Other fingers
    for id in range(1, 5):
        if hand_landmarks.landmark[tips_ids[id]].y < hand_landmarks.landmark[tips_ids[id] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers.count(1)

# Initialize webcam
cap = cv2.VideoCapture(0)

# Initialize Pygame
p.init()

# Define game classes and functions
class Square(p.sprite.Sprite):
    def __init__(self, x_id, y_id, number):
        super().__init__()
        self.width = 120
        self.height = 120
        self.x = (x_id - 1) * self.width + self.width // 2
        self.y = (y_id - 1) * self.height + self.height // 2
        self.content = ''
        self.number = number
        self.image = blank_image
        self.image = p.transform.scale(self.image, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def update(self):
        self.rect.center = (self.x, self.y)

    def set_content(self, player):
        if self.content == '' and not won:
            self.content = player
            board[self.number] = player

            if player == 'X':
                self.image = x_image
            else:
                self.image = o_image
            self.image = p.transform.scale(self.image, (self.width, self.height))
            checkWinner(self.content)

def checkWinner(player):
    global background, won, startX, startY, endX, endY

    for line in winners:
        if board[line[0]] == player and board[line[1]] == player and board[line[2]] == player:
            won = True
            getPos(line[0], line[2])
            break

    if won:
        Update()
        drawLine(startX, startY, endX, endY)
        square_group.empty()
        background = p.image.load(player + '_Wins.png')
        background = p.transform.scale(background, (WIDTH, HEIGHT))

def getPos(n1, n2):
    global startX, startY, endX, endY

    for sq in squares:
        if sq.number == n1:
            startX = sq.x
            startY = sq.y
        elif sq.number == n2:
            endX = sq.x
            endY = sq.y

def drawLine(x1, y1, x2, y2):
    p.draw.line(win, (0, 0, 0), (x1, y1), (x2, y2), 15)
    p.display.update()
    time.sleep(2)

def Update():
    win.blit(background, (0, 0))
    square_group.draw(win)
    square_group.update()
    p.display.update()

def get_square_by_position(posx, posy):
    """Maps (posx, posy) grid coordinates to the square number"""
    mapping = {
        (1, 1): 1, (1, 2): 2, (1, 3): 3,
        (2, 1): 4, (2, 2): 5, (2, 3): 6,
        (3, 1): 7, (3, 2): 8, (3, 3): 9
    }
    return mapping.get((posx, posy))

# Initialize game variables
WIDTH = 360
HEIGHT = 360

win = p.display.set_mode((WIDTH, HEIGHT))
p.display.set_caption('Tic Tac Toe')
clock = p.time.Clock()

# Load images
blank_image = p.image.load('Blank.png')
x_image = p.image.load('X.png')
o_image = p.image.load('O.png')
background = p.image.load('Background.png')

background = p.transform.scale(background, (WIDTH, HEIGHT))

won = False

square_group = p.sprite.Group()
squares = []

winners = [
    [1, 2, 3], [4, 5, 6], [7, 8, 9],  # Rows
    [1, 4, 7], [2, 5, 8], [3, 6, 9],  # Columns
    [1, 5, 9], [3, 5, 7]              # Diagonals
]
board = ['' for _ in range(10)]  # Index 0 unused

startX = startY = endX = endY = 0

# Create squares
num = 1
for y in range(1, 4):
    for x in range(1, 4):
        sq = Square(x, y, num)
        square_group.add(sq)
        squares.append(sq)
        num += 1

turn = 'X'
run = True
move_made = False
prev_fingers = (-1, -1)  # To store previous finger counts

with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5, max_num_hands=2) as hands:
    while run:
        clock.tick(30)  # Limit to 30 FPS

        # Handle Pygame events
        for event in p.event.get():
            if event.type == p.QUIT:
                run = False

        # Read frame from webcam
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        fingers_left = fingers_right = 0

        if result.multi_hand_landmarks and result.multi_handedness:
            for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                hand_label = handedness.classification[0].label
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                fingers = count_fingers(hand_landmarks, hand_label)
                if hand_label == "Left":
                    fingers_left = fingers
                else:
                    fingers_right = fingers

        # Display finger counts on the frame
        cv2.putText(frame, f'Left Hand: {fingers_left} fingers', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Right Hand: {fingers_right} fingers', (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Show the OpenCV frame
        cv2.imshow('Hand Tracking and Finger Count', frame)

        # Map finger counts to positions (1-3)
        posx = min(max(fingers_left, 1), 3)
        posy = min(max(fingers_right, 1), 3)

        # Check if finger counts have changed and a move hasn't been made yet
        if (fingers_left, fingers_right) != prev_fingers and not move_made:
            square_number = get_square_by_position(posx, posy)
            if square_number is not None and board[square_number] == '':
                square = squares[square_number - 1]
                square.set_content(turn)

                # Switch turns
                turn = 'O' if turn == 'X' else 'X'
                move_made = True  # Prevent multiple moves for the same finger count

        # Reset move_made when finger counts change
        if (fingers_left, fingers_right) != prev_fingers:
            move_made = False

        prev_fingers = (fingers_left, fingers_right)

        # Update the Pygame display
        Update()

        # Check if the game has been won
        if won:
            print(f"Player {turn} wins!")
            run = False

        # Break the loop if 'q' is pressed in OpenCV window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            run = False

# Release resources
cap.release()
cv2.destroyAllWindows()
p.quit()
