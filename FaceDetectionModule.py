import cv2
import mediapipe as mp
import time



class faceDetector():
    def __init__(self, minDetectionCon=0.5):

        self.minDetectionCon = minDetectionCon

        self.mpFaceDetection = mp.solutions.face_detection
        self.mpDraw = mp.solutions.drawing_utils
        self.faceDetection = self.mpFaceDetection.FaceDetection(self.minDetectionCon)

    def findFaces(self, img, draw=True):

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.faceDetection.process(imgRGB)
        # print(self.results)
        bboxs = []
        self.scoreList = []
        self.bboxList = []
        score = 0
        i = 0
        if self.results.detections:
            for id, detection in enumerate(self.results.detections):
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, ic = img.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                       int(bboxC.width * iw), int(bboxC.height * ih)
                score = list(detection.score)[0]  
                self.scoreList.append(score)
                bboxs.append([id, bbox, score])
                
                if draw:
                    img = self.fancyDraw(img,bbox)
                    cv2.putText(img, f'ID: {id}', (bbox[0], bbox[1] - 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                    cv2.putText(img, f'{int(detection.score[0] * 100)}%',
                            (bbox[0], bbox[1] - 20), cv2.FONT_HERSHEY_PLAIN,
                            2, (255, 0, 255), 2)
            
            if len(bboxs) != 0:
                print("********************************")
                i = self.scoreList.index(max(self.scoreList))
                bboxs = bboxs[i]
            else:
                print("---------------------------------")
                bboxs = [[0, [], 0]]
            print("Bboxs:", bboxs)
        return img, bboxs

    def fancyDraw(self, img, bbox, l=30, t=5, rt= 1):
        x, y, w, h = bbox
        x1, y1 = x + w, y + h

        cv2.rectangle(img, bbox, (255, 0, 255), rt)
        # Top Left  x,y
        cv2.line(img, (x, y), (x + l, y), (255, 0, 255), t)
        cv2.line(img, (x, y), (x, y+l), (255, 0, 255), t)
        # Top Right  x1,y
        cv2.line(img, (x1, y), (x1 - l, y), (255, 0, 255), t)
        cv2.line(img, (x1, y), (x1, y+l), (255, 0, 255), t)
        # Bottom Left  x,y1
        cv2.line(img, (x, y1), (x + l, y1), (255, 0, 255), t)
        cv2.line(img, (x, y1), (x, y1 - l), (255, 0, 255), t)
        # Bottom Right  x1,y1
        cv2.line(img, (x1, y1), (x1 - l, y1), (255, 0, 255), t)
        cv2.line(img, (x1, y1), (x1, y1 - l), (255, 0, 255), t)
        return img


def main():
    '''me = Tello()
    me.connect()
    print(me.get_battery())
    me.streamoff()
    me.streamon()'''

    cap = cv2.VideoCapture(0)
    pTime = 0
    detector = faceDetector()
    while True:
        success, img = cap.read()
        #img = me.get_frame_read().frame
        img, bboxs = detector.findFaces(img)
        img = cv2.resize(img,(640,480))
        '''if len(bboxs) != 0:
            print(len(bboxs))
            #print(bboxs)
        else:
            print("No Face Detected")'''

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)
        #cv2.putText(img,("Batarya: " + str(me.get_battery())),(350,70),cv2.FONT_HERSHEY_PLAIN,3,(0,255,255),2)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()

