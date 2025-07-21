import cv2
import mediapipe as mp
import time

# Initialize MediaPipe hands and drawing utilities
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Function to count fingers based on landmarks
def count_fingers(hand_landmarks, hand_label):
    # Tip landmarks for fingers: Thumb, Index, Middle, Ring, Pinky
    tips_ids = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb: Check based on hand orientation (left or right)
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

    # For other fingers
    for i in range(1, 5):
        if hand_landmarks.landmark[tips_ids[i]].y < hand_landmarks.landmark[tips_ids[i] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers.count(1)

# Initialize webcam and fps variables
cap = cv2.VideoCapture(0)
pTime = 0  # Previous time to calculate FPS

# Mediapipe Hands object
with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5, max_num_hands=2) as hands:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        frame = cv2.flip(frame, 1)
        # Convert BGR to RGB for Mediapipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        # Store frame dimensions for placing text
        h, w, _ = frame.shape

        # Check if hand landmarks are detected
        if result.multi_hand_landmarks and result.multi_handedness:
            for idx, (hand_landmarks, handedness) in enumerate(zip(result.multi_hand_landmarks, result.multi_handedness)):
                # Get hand label (Left or Right)
                hand_label = handedness.classification[0].label

                # Draw landmarks on the frame
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Count the number of raised fingers
                fingers_count = count_fingers(hand_landmarks, hand_label)

                # Display finger count and hand label on the frame
                cv2.putText(frame, f'Hand {idx + 1} ({hand_label}): {fingers_count} fingers', 
                            (10, 30 + idx * 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Calculate FPS and display it
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(frame, f'FPS: {int(fps)}', (w - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Show the frame
        cv2.imshow('Hand Tracking and Finger Count', frame)

        # Break on 'q' key press
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

# Release resources
cap.release()
cv2.destroyAllWindows()