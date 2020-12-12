from threading import Thread
from collections import deque
import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')


class webcam:
    """
    A class that will detect face and eyes
    """
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.flag = True

    def detect_face(self):
        while True:
            ret, frame = self.cap.read()
            frame = cv2.add(frame, np.array([30.0]))
            face_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detected = False
            face_rectangle = face_cascade.detectMultiScale(face_img, scaleFactor=1.4, minNeighbors=5)
            for (x, y, w, h) in face_rectangle:
                cv2.rectangle(face_img, (x, y), (x + w, y + h), (255, 255, 255), 5)
                detected = True
                face = face_img[y:y + h, x:x + w]  # cropping the face rectangle
                eyes_rectangle = eye_cascade.detectMultiScale(face)  # detection for eyes in the face
                for (xx, yy, ww, hh) in eyes_rectangle:
                    cv2.rectangle(face_img, (xx + x, y + yy), (x + xx + ww, y + yy + hh), (255, 0, 0),
                                  2)  # drawing rectangle over the detected eyes

            cv2.imshow('face detect', face_img)
            cv2.waitKey(1)
            self.flag = detected

    def start(self):
        Thread(target=self.detect_face, args=()).start()
        return self

    def __del__(self):
        self.cap.release()


class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, src=0):
        self.movie = cv2.VideoCapture(src)
        self.fps = self.movie.get(cv2.CAP_PROP_FPS)
        self.grabbed = deque()
        self.frame = deque()
        g, f = self.movie.read()
        self.grabbed.append(g)
        self.frame.append(f)
        self.stopped = False

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            g, f = self.movie.read()
            if not g:
                break
            else:
                self.frame.append(f)
                self.grabbed.append(g)

    def get_frame(self):
        if len(self.grabbed) != 0:
            g = self.grabbed.popleft()
            f = self.frame.popleft()
            return g, f
        return False, None

    def stop(self):
        self.stopped = True

    def __del__(self):
        self.movie.release()


def PlayVideo(source):
    """
    Dedicated thread for grabbing video frames with VideoGet object.
    Main thread shows video frames.
    """
    play = True
    video_getter = VideoGet(source).start()
    wb = webcam().start()

    while True:
        usr = cv2.waitKey(int(1000/video_getter.fps))
        if usr == 32:  # if the user presses the "space"
            play = not play
        if usr == 27 or video_getter.stopped:
            video_getter.stop()
            break
        # if (cv2.waitKey(int(1000 / video_getter.fps)) == ord("q")) or video_getter.stopped:
        #    video_getter.stop()
        #    break

        if play and wb.flag:
            grabbed, frame = video_getter.get_frame()
            if frame is None:
                break
            cv2.imshow("Video", frame)

    del video_getter
    cv2.destroyAllWindows()


path = '/home/devil/Downloads/vv.mp4'
PlayVideo(path)
