import cv2
import mediapipe as mp
import numpy as np
import csv
import time
from datetime import datetime

import postures as ps
import view_detection as vd

# -------------------------------
# MediaPipe setup
# -------------------------------
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

def calc_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    cosine = np.clip(cosine, -1.0, 1.0)
    return np.degrees(np.arccos(cosine))

# -------------------------------
# Choose posture
# -------------------------------
pos_name = ps.check()
if pos_name == "quit":
    exit()

# -------------------------------
# CSV Setup
# -------------------------------
csv_filename = "angles.csv"
csv_file = open(csv_filename, "w", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)

csv_writer.writerow([
    "Timestamp",
    "L_Elbow", "R_Elbow",
    "L_Shoulder", "R_Shoulder",
    "L_Hip", "R_Hip",
    "L_Knee", "R_Knee"
])

last_saved_time = time.time() * 1000

# -------------------------------
# Webcam
# -------------------------------
cap = cv2.VideoCapture(0)

with mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as pose:

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)

        if results.pose_landmarks:

            lm = results.pose_landmarks.landmark

            def p(idx):
                return [lm[idx].x * w, lm[idx].y * h]

            # Landmarks
            L_SH = p(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
            R_SH = p(mp_pose.PoseLandmark.RIGHT_SHOULDER.value)
            L_EL = p(mp_pose.PoseLandmark.LEFT_ELBOW.value)
            R_EL = p(mp_pose.PoseLandmark.RIGHT_ELBOW.value)
            L_WR = p(mp_pose.PoseLandmark.LEFT_WRIST.value)
            R_WR = p(mp_pose.PoseLandmark.RIGHT_WRIST.value)
            L_HIP = p(mp_pose.PoseLandmark.LEFT_HIP.value)
            R_HIP = p(mp_pose.PoseLandmark.RIGHT_HIP.value)
            L_KNEE = p(mp_pose.PoseLandmark.LEFT_KNEE.value)
            R_KNEE = p(mp_pose.PoseLandmark.RIGHT_KNEE.value)
            L_ANKLE = p(mp_pose.PoseLandmark.LEFT_ANKLE.value)
            R_ANKLE = p(mp_pose.PoseLandmark.RIGHT_ANKLE.value)

            # Angle dictionary
            angles = {
                "L-Elbow": (calc_angle(L_SH, L_EL, L_WR), L_EL),
                "R-Elbow": (calc_angle(R_SH, R_EL, R_WR), R_EL),
                "L-Shoulder": (calc_angle(L_HIP, L_SH, L_EL), L_SH),
                "R-Shoulder": (calc_angle(R_HIP, R_SH, R_EL), R_SH),
                "L-Hip": (calc_angle(L_SH, L_HIP, L_KNEE), L_HIP),
                "R-Hip": (calc_angle(R_SH, R_HIP, R_KNEE), R_HIP),
                "L-Knee": (calc_angle(L_HIP, L_KNEE, L_ANKLE), L_KNEE),
                "R-Knee": (calc_angle(R_HIP, R_KNEE, R_ANKLE), R_KNEE),
            }

            # Display angles
            for name, (angle, pos) in angles.items():
                cv2.putText(frame, f"{name}: {int(angle)}",
                            (int(pos[0]) + 10, int(pos[1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2)

            # ✅ View detection (UPDATED CALL)
            vd.detect_view(frame, lm, w, h)

            # Posture feedback
            ps.check_pos(pos_name, angles, frame)

            # Save to CSV every 1 second
            current_time = time.time() * 1000
            if current_time - last_saved_time >= 1000:
                csv_writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    int(angles["L-Elbow"][0]),
                    int(angles["R-Elbow"][0]),
                    int(angles["L-Shoulder"][0]),
                    int(angles["R-Shoulder"][0]),
                    int(angles["L-Hip"][0]),
                    int(angles["R-Hip"][0]),
                    int(angles["L-Knee"][0]),
                    int(angles["R-Knee"][0]),
                ])
                last_saved_time = current_time

            mp_draw.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

        cv2.imshow("Full Body Angle Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
csv_file.close()
print("CSV saved successfully.")