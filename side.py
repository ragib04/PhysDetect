import cv2
import mediapipe as mp
import numpy as np
import time
import csv
from collections import deque
from datetime import datetime

# -------- Mediapipe setup --------
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# -------- Angle calculation function --------
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180:
        angle = 360 - angle
    return angle

# -------- Moving average buffers --------
buffers = {
    "shoulder": deque(maxlen=10),
    "elbow": deque(maxlen=10),
    "hip": deque(maxlen=10),
    "knee": deque(maxlen=10)
}

def smooth(buffer, angle):
    buffer.append(angle)
    return np.mean(buffer)

# -------- CSV setup --------
csv_filename = "left_elbow_flexion.csv"
csv_file = open(csv_filename, "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Timestamp", "Left Shoulder", "Left Elbow", "Left Hip", "Left Knee"])

# -------- Video capture --------
cap = cv2.VideoCapture(0)
last_saved_time = time.time()

# 🔥 ONLY MODEL IMPROVED HERE
with mp_pose.Pose(
        model_complexity=2,              # Highest accuracy
        smooth_landmarks=True,           # Built-in smoothing
        enable_segmentation=False,
        min_detection_confidence=0.85,   # Stronger detection
        min_tracking_confidence=0.85     # Stronger tracking
    ) as pose:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Default angles
        shoulder_angle = 0
        elbow_angle = 0
        hip_angle = 0
        knee_angle = 0

        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark

            # Left landmarks
            left_shoulder = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            left_elbow = [lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                          lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            left_wrist = [lm[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                          lm[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            left_hip = [lm[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        lm[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_knee = [lm[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                         lm[mp_pose.PoseLandmark.LEFT_KNEE.value].y]

            # ---- Calculate & smooth angles ----
            shoulder_angle = smooth(buffers["shoulder"], calculate_angle(left_hip, left_shoulder, left_elbow))
            elbow_angle = smooth(buffers["elbow"], calculate_angle(left_shoulder, left_elbow, left_wrist))
            hip_angle = smooth(buffers["hip"], calculate_angle(left_shoulder, left_hip, left_knee))
            knee_angle = smooth(buffers["knee"], calculate_angle(left_hip, left_knee, left_knee))

            # Display angles
            cv2.putText(image,f'Shoulder:{int(shoulder_angle)}',
                        tuple(np.multiply(left_shoulder,[w,h]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)

            cv2.putText(image,f'Elbow:{int(elbow_angle)}',
                        tuple(np.multiply(left_elbow,[w,h]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)

            cv2.putText(image,f'Hip:{int(hip_angle)}',
                        tuple(np.multiply(left_hip,[w,h]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)

            cv2.putText(image,f'Knee:{int(knee_angle)}',
                        tuple(np.multiply(left_knee,[w,h]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)

        # -------- Feedback Section --------
        if not results.pose_landmarks:
            status_text = "NO POSTURE DETECTED"
            color = (0,0,255)

        else:
            if elbow_angle == 0:
                status_text = "NO POSTURE DETECTED"
                color = (0,0,255)

            elif elbow_angle > 130:
                status_text = "BEND MORE (Flex Arm)"
                color = (0,0,255)

            elif elbow_angle < 40:
                status_text = "EXTEND MORE"
                color = (0,0,255)

            else:
                status_text = "CORRECT FLEXION"
                color = (0,255,0)

        cv2.putText(image,status_text,(50,50),
                    cv2.FONT_HERSHEY_SIMPLEX,1,color,3)

        # -------- Save angles per second --------
        current_time = time.time()
        if current_time - last_saved_time >= 1:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            csv_writer.writerow([
                timestamp,
                round(shoulder_angle,2),
                round(elbow_angle,2),
                round(hip_angle,2),
                round(knee_angle,2)
            ])
            csv_file.flush()
            last_saved_time = current_time

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.imshow("Left Elbow Flexion Tracker", image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
csv_file.close()
cv2.destroyAllWindows()
print(f"CSV saved as {csv_filename}")