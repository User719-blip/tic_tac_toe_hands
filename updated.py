import cv2
import mediapipe as mp
import time
import pygame as p
import sys

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
        background = p.image.load(player + ' Wins.png')
        background = p.transform.scale(background, (WIDTH, HEIGHT))
        Update()
        print(f"Player {player} wins!")
        time.sleep(3)  # Display the win screen for 3 seconds
        terminate_game()

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

def terminate_game():
    """Terminates the game gracefully"""
    cap.release()
    cv2.destroyAllWindows()
    p.quit()
    sys.exit()

def check_tie():
    """Checks if the game is a tie"""
    if all(board[i] != '' for i in range(1, 10)) and not won:
        print("The game is a tie!")
        background = p.image.load('Tie Game.png')  # Ensure you have a Tie.png image
        background = p.transform.scale(background, (WIDTH, HEIGHT))
        Update()
        time.sleep(3)  # Display the tie screen for 3 seconds
        terminate_game()

# Initialize game variables
WIDTH = 360
HEIGHT = 360

win = p.display.set_mode((WIDTH, HEIGHT))
p.display.set_caption('Tic Tac Toe')
clock = p.time.Clock()

# Load images
try:
    blank_image = p.image.load('Blank.png')
    x_image = p.image.load('X.png')
    o_image = p.image.load('O.png')
    background = p.image.load('Background.png')
except p.error as e:
    print(f"Error loading images: {e}")
    terminate_game()

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
last_move_time = time.time()      # Initialize to current time
delay_seconds = 5       # 5-second delay between moves

# Debounce parameters
debounce_time = 0.3  # seconds
finger_change_time = None
is_stable = False

with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5, max_num_hands=2) as hands:
    first_frame = True  # Flag to check if it's the first frame
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
        hands_detected = False  # Flag to check if any hands are detected

        if result.multi_hand_landmarks and result.multi_handedness:
            hands_detected = True
            for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                hand_label = handedness.classification[0].label
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                fingers = count_fingers(hand_landmarks, hand_label)
                if hand_label == "Left":
                    fingers_left = fingers
                else:
                    fingers_right = fingers

        else:
            # No hands detected
            hands_detected = False

        # Display finger counts on the frame
        cv2.putText(frame, f'Left Hand: {fingers_left} fingers', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Right Hand: {fingers_right} fingers', (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Show the OpenCV frame
        cv2.imshow('Hand Tracking and Finger Count', frame)

        # Map finger counts to positions (1-3)
        posx = min(max(fingers_left, 1), 3) if hands_detected else 0  # 0 indicates no hand
        posy = min(max(fingers_right, 1), 3) if hands_detected else 0  # 0 indicates no hand

        current_time = time.time()

        if first_frame:
            # Initialize prev_fingers to current counts to prevent immediate move
            if hands_detected:
                prev_fingers = (fingers_left, fingers_right)
            else:
                prev_fingers = (0, 0)
            last_move_time = current_time
            first_frame = False
            continue  # Skip the rest of the loop for the first frame

        # Debouncing Logic Starts Here
        if hands_detected:
            if (fingers_left, fingers_right) != prev_fingers:
                finger_change_time = current_time
                is_stable = False
            else:
                if finger_change_time is not None:
                    if (current_time - finger_change_time) >= debounce_time:
                        is_stable = True
        else:
            # No hands detected; reset debouncing variables
            finger_change_time = None
            is_stable = False

        # If finger counts are stable and a move hasn't been made yet
        if is_stable and not move_made and not won:
            square_number = get_square_by_position(posx, posy)
            if square_number is not None and board[square_number] == '':
                square = squares[square_number - 1]
                square.set_content(turn)

                # Update the display after the move
                Update()

                # Update last move time and reset move_made
                last_move_time = current_time
                move_made = True

                # Switch turns
                turn = 'O' if turn == 'X' else 'X'

                # Check for a tie after the move
                check_tie()

                # Reset stability flag
                is_stable = False
                finger_change_time = None

        # Reset move_made when finger counts change
        if hands_detected and (fingers_left, fingers_right) != prev_fingers:
            move_made = False

        # Update previous finger counts only if hands are detected
        if hands_detected:
            prev_fingers = (fingers_left, fingers_right)
        else:
            prev_fingers = (0, 0)

        # Update the Pygame display
        Update()

        # Check if the game has been won
        if won:
            # Wait for 3 seconds to show the win screen before terminating
            time.sleep(3)
            run = False

        # Break the loop if 'q' is pressed in OpenCV window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            run = False

# Terminate the game gracefully
terminate_game()