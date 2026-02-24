import cv2

def resize_put(frame, text, tupxy, font, scale, color, thickness):
    lines = [text[i:i+20] for i in range(0, len(text), 20)]
    (x, y) = tupxy
    for line in lines:
        cv2.putText(frame, line, (x, y), font, scale, color, thickness)
        y += 30
        

def check():
    print("check for:\n"
          "1. Squat\n"
          "2. Quit")
    pos_name = 'none'
    while pos_name == 'none':
        pos_name = input()
        if pos_name in ['squat', 'quit']:
            return pos_name
        else:
            pos_name = 'none'
            print("re-enter what to check for")

def check_pos(pos_name, angles, frame):
    if pos_name == 'squat':
        # check for initial state
        if angles['L-Hip'][0] > 150 and angles['L-Knee'][0] > 150:
            resize_put(frame, f"Move your hips back slowly keeping your chest up and bend your knees", (30,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
        else:
            if angles['L-Hip'][0] < 45 and angles['R-Hip'][0] < 45:
                resize_put(frame, f"Move your back up", (30,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
            elif angles['L-Hip'][0] > 80 and angles['R-Hip'][0] > 80:
                cv2.putText(frame, f"Move your back down", (30,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
            if angles['L-Knee'][0] < 70 and angles['R-Knee'][0] < 70:
                cv2.putText(frame, f"Move your knee up", (30,200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
            elif angles['L-Knee'][0] > 95 and angles['R-Knee'][0] > 95:
                cv2.putText(frame, f"Move your knee down", (30,200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
