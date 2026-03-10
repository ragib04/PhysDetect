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


def check_pos(pos_name, angles, frame, view):
    if pos_name == "squat":
        if view == "SIDE VIEW":
            if angles['R-Hip'][0] > 150 and angles['R-Knee'][0] > 150:
                resize_put(frame, f"Move your hips back slowly keeping your chest up and bend your knees", (30,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
        else:
            if angles['R-Hip'][0] < 45:
                resize_put(frame, f"Move your back up", (30,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
            elif angles['R-Hip'][0] > 80:
                cv2.putText(frame, f"Move your back down", (30,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
            if angles['R-Knee'][0] < 70:
                cv2.putText(frame, f"Move your knee up", (30,200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
            elif angles['R-Knee'][0] > 95:
                cv2.putText(frame, f"Move your knee down", (30,200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
