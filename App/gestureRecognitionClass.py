import threading
import cv2
import HandTrackingModule as htm


class GestureRecognition(threading.Thread):
    def __init__(self, callback=None):
        threading.Thread.__init__(self)
        self.detector = htm.handDetctor(detectionCon=0.7)
        self.callback = callback
        self.stop_thread = False

    def run(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, 640)  # Width
        cap.set(4, 480)  # Height
        status = []
        position = []
        while True and not self.stop_thread:  # check self.stop_thread in while condition
            success, img = cap.read()
            img = self.detector.findHands(img)
            thumbOpen, lmList = self.detector.findPosition(img, draw=False)

            if len(lmList) != 0:
                firstOpen, secondOpen, thirdOpen, fourthOpen = self.detector.fingerOpenStatus(lmList)
                thumbClosed, firstClosed, secondClosed, thirdClosed, fourthClosed = not thumbOpen, not firstOpen, not secondOpen, not thirdOpen, not fourthOpen

                new_statu = -1
                id, x0, y0 = lmList[0]
                id, x4, y4 = lmList[4]
                if y4 < y0:
                    position.append(1)
                if y4 > y0 and 1 in position:
                    position.clear()
                    if x0 < x4:
                        print("pre")
                        self.callback("LEFT")
                    else:
                        print("next")
                        self.callback("RIGHT")

                if thumbOpen and firstOpen and secondOpen and thirdOpen and fourthOpen:
                    new_statu = 5
                elif not firstOpen and not secondOpen and not thirdOpen and not fourthOpen:
                    new_statu = 0
                elif firstOpen and thumbClosed and secondClosed and thirdClosed and fourthClosed:
                    new_statu = 1
                elif firstOpen and thumbClosed and secondOpen and thirdClosed and fourthClosed:
                    new_statu = 2
                elif firstOpen and thumbClosed and secondOpen and thirdOpen and fourthClosed:
                    new_statu = 3
                elif firstOpen and thumbClosed and secondOpen and thirdOpen and fourthOpen:
                    new_statu = 4
                elif thumbOpen and firstClosed and secondClosed and thirdClosed and fourthOpen:
                    new_statu = 6
                elif thumbOpen and firstOpen and secondOpen and thirdClosed and fourthClosed:
                    new_statu = 7
                elif thumbOpen and firstOpen and secondClosed and thirdClosed and fourthClosed:
                    new_statu = 8
                elif thumbOpen and firstClosed and secondClosed and thirdClosed and fourthClosed:
                    new_statu = 9
                # print(new_statu)
                status.append(new_statu)
                # print(5 in status,len(status))
                if len(status) > 100:
                    status = status[1:]
                    position = position[1:]
                if new_statu == 0 and 5 in status:
                    # print("pause")
                    self.callback("OK")
                    status = []
                elif new_statu == 5 and 0 in status:
                    # print("open")
                    self.callback("OPEN")
                    status = []
                elif firstOpen and thumbClosed and secondClosed and thirdClosed and fourthClosed:
                    if self.detector.firstUp(lmList) and 0 in status:
                        # print("down")
                        self.callback("DOWN")
                        status.clear()
                    if self.detector.firstDown(lmList) and 0 in status:
                        # print("up")
                        self.callback("UP")
                        status.clear()
                elif new_statu == 6 and 0 in status:
                    # print("6")
                    self.callback("6")
                    status.clear()
                elif new_statu == 2 and 0 in status:
                    # print("2")
                    self.callback("2")
                    status.clear()
                elif new_statu == 8 and 0 in status:
                    # print("8")
                    self.callback("8")
                    status.clear()
                elif new_statu == 9 and 0 in status:
                    print("9")
                    self.callback("9")
                    status.clear()
                elif new_statu == 3 and 0 in status:
                    # print("3")
                    self.callback("3")
                    status.clear()

            cv2.imshow("image", img)
            if cv2.waitKey(2) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        self.stop_thread = True

