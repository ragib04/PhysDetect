import cv2

def resize_put(frame, text, tupxy, font, scale, color, thickness):
    lines = [text[i:i + 30] for i in range(0, len(text), 30)]
    (x, y) = tupxy
    for line in lines:
        cv2.putText(frame, line, (x, y), font, scale, color, thickness)
        y += 30


def check():
    print("Check for:\n"
          "1. Squat\n"
          "2. Quit")

    while True:
        pos_name = input().lower()
        if pos_name in ["squat", "quit"]:
            return pos_name
        print("Re-enter what to check for")


def check_pos(pos_name, angles, frame):

    if pos_name != "squat":
        return

    hip_angle = angles['L-Hip'][0]
    knee_angle = angles['L-Knee'][0]

    # -------------------------
    # Standing Position
    # -------------------------
    if hip_angle > 160 and knee_angle > 160:
        resize_put(frame,
                   "Start Squat: Bend hips and knees",
                   (30, 50),
                   cv2.FONT_HERSHEY_SIMPLEX,
                   0.7,
                   (0, 0, 255),
                   2)

    # -------------------------
    # Correct Squat Depth
    # -------------------------
    elif 70 <= hip_angle <= 100 and 70 <= knee_angle <= 100:
        cv2.putText(frame,
                    "Good Squat!",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    2)

    # -------------------------
    # Too Deep
    # -------------------------
    elif hip_angle < 60:
        cv2.putText(frame,
                    "Too Deep - Come Up Slightly",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2)

    # -------------------------
    # Not Deep Enough
    # -------------------------
    elif knee_angle > 120:
        cv2.putText(frame,
                    "Go Lower",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2)