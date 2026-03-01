import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose

def detect_view(frame, landmarks, frame_width, frame_height):

    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]

    # Convert to pixel coordinates
    ls_x = left_shoulder.x * frame_width
    rs_x = right_shoulder.x * frame_width

    nose_y = nose.y * frame_height
    ankle_y = max(left_ankle.y, right_ankle.y) * frame_height

    # Shoulder width in pixels
    shoulder_width = abs(ls_x - rs_x)

    # Full body height in pixels
    body_height = abs(ankle_y - nose_y)

    if body_height == 0:
        return None

    # Ratio (VERY IMPORTANT)
    ratio = shoulder_width / body_height

    # -------------------------
    # STABLE RANGES (Test These)
    # -------------------------

    if ratio > 0.22:
        view = "FRONT VIEW"
        color = (255, 0, 0)

    elif ratio < 0.13:
        view = "SIDE VIEW"
        color = (0, 255, 255)

    else:
        view = "TURN PROPERLY"
        color = (0, 165, 255)

    cv2.putText(frame, view,
                (30, 400),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color,
                3)

    return view