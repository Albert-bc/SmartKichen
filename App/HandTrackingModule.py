import cv2
import mediapipe as mp
import time
import math


class handDetctor():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # change into rgb
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        thumb = True
        if self.results.multi_hand_landmarks:
            if handNo >= len(self.results.multi_hand_landmarks):
                return []
            myHand = self.results.multi_hand_landmarks[handNo]
            thumb_mcp = myHand.landmark[2]
            thumb_pip = myHand.landmark[3]
            thumb_tip = myHand.landmark[4]
            index_mcp = myHand.landmark[5]
            middle_mcp = myHand.landmark[9]

            # calculate 3 key points angle of thumb
            thumb_angle = self.calculate_angle(thumb_mcp, thumb_pip, thumb_tip)
            distance_tip_pip = math.sqrt((thumb_tip.x - thumb_pip.x) ** 2 + (thumb_tip.y - thumb_pip.y) ** 2)
            for id, lm in enumerate(myHand.landmark):
                if id > 4:
                    distance = math.sqrt((thumb_tip.x - lm.x) ** 2 + (thumb_tip.y - lm.y) ** 2)
                    if distance < distance_tip_pip:
                        thumb = False
                        break

            # calculate distance between thunb and other fingers
            dist_thumb_index = math.sqrt((thumb_tip.x - index_mcp.x) ** 2 + (thumb_tip.y - index_mcp.y) ** 2)
            dist_thumb_middle = math.sqrt((thumb_tip.x - middle_mcp.x) ** 2 + (thumb_tip.y - middle_mcp.y) ** 2)

            # justify the status according to the distance and angle
            if thumb_angle < 100 and (dist_thumb_index < 0.1 or dist_thumb_middle < 0.1):
                thumb = False

            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                # get finger key points
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.putText(img, str(int(id)), (cx + 10, cy + 10), cv2.FONT_HERSHEY_PLAIN,
                                1, (0, 0, 255), 2)

        return thumb, lmList

    # return a list which contains the finger status
    def fingerOpenStatus(self, lmList):

        fingerList = []

        id, originx, originy = lmList[0]
        keypoint_list = [[6, 8], [10, 12], [14, 16], [18, 20]]
        for point in keypoint_list:
            id, x1, y1 = lmList[point[0]]
            id, x2, y2 = lmList[point[1]]
            if math.hypot(x2 - originx, y2 - originy) > math.hypot(x1 - originx, y1 - originy):
                fingerList.append(True)
            else:
                fingerList.append(False)

        return fingerList

    def fingerCloseStatus(self, lmList):

        fingerList = []
        id, originx, originy = lmList[0]
        keypoint_list = [[2, 4], [5, 8], [9, 12], [13, 16], [17, 20]]
        for point in keypoint_list:
            id, x1, y1 = lmList[point[0]]
            id, x2, y2 = lmList[point[1]]
            if math.hypot(x2 - originx, y2 - originy) > math.hypot(x1 - originx, y1 - originy):
                fingerList.append(True)
            else:
                fingerList.append(False)

        return fingerList

    def firstUp(self, lmList):
        point = [6, 8]
        id, x1, y1 = lmList[point[0]]
        id, x2, y2 = lmList[point[1]]
        if x1 == x2 and y2 > y1:
            return True
        return (y2 > y1) and abs(y2 - y1) / abs(x2 - x1) > 2

    def firstDown(self, lmList):
        point = [6, 8]
        id, x1, y1 = lmList[point[0]]
        id, x2, y2 = lmList[point[1]]
        if x1 == x2 and y2 < y1:
            return True
        return (y2 < y1) and abs(y2 - y1) / abs(x2 - x1) > 2


    def calculate_angle(self, a, b, c):
        # calculate angle between ab and bc
        ab = [b.x - a.x, b.y - a.y]  # vector ab
        bc = [c.x - b.x, c.y - b.y]  # vector bc
        cos_angle = (ab[0] * bc[0] + ab[1] * bc[1]) / (
                    math.sqrt(ab[0] ** 2 + ab[1] ** 2) * math.sqrt(bc[0] ** 2 + bc[1] ** 2))
        angle = math.acos(max(min(cos_angle, 1.0), -1.0)) * 180 / math.pi
        return angle


def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # FPS
    pTime = 0
    cTime = 0
    detector = handDetctor()
    while True:
        success, img = cap.read()

        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)
        if len(lmList) != 0:
            # print(lmList)
            print(detector.fingerStatus(lmList))

        # fps
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        cv2.imshow("image", img)
        if cv2.waitKey(2) & 0xFF == 27:
            break

    cap.release()


if __name__ == '__main__':
    main()
