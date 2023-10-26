
#import fire
import cv2
import time
import pandas
from datetime import datetime, timedelta
import random
import os
from dataclasses import dataclass


MP3 = 1
VOICE = 2

@dataclass
class Sound:
    type: int
    name: str

    def play(self):
        if self.type == MP3:
            os.system(f'afplay "{self.name}"')
        else:      
            os.system(f"say --voice=Alva {self.name}")
            
SOUNDS = [
    #Sound(MP3, "Ingen-hemma.m4a")

    Sound(MP3, "woman_scream.mp3"),
    Sound(MP3, "Maja jag kommer ata upp er.m4a"),
    Sound(MP3, "Maja-skriker.m4a"),
    Sound(MP3, "Mala har finns det spoken.m4a"),
    Sound(MP3, "Melvin ater upp dig.m4a"),
    Sound(MP3, "Melvin ha ha ha.m4a"),
    Sound(MP3, "Melvin nu kommer jag och ater upp er.m4a"),
    Sound(MP3, "Stefan ater upp er.m4a"),

    Sound(MP3, "Stefan hahaha.m4a"),
    Sound(MP3, "Stefan har far man bara gronsaker.m4a"),
    Sound(MP3, "Stefan har finns det bara ackligt godis.m4a"),

    #Sound(MP3, "Stefan godiset är slut.m4a"),
]

def play_sound():
    sound = random.choice(SOUNDS)
    sound.play()

    
def main():
    # Assigning our static_back to None
    static_back = None

    # List when any moving object appear
    motion_list = [ None, None ]

    # Time of movement
    time = []

    # Initializing DataFrame, one column is start
    # time and other column is end time
    df = pandas.DataFrame(columns = ["Start", "End"])

    # Capturing video
    video = cv2.VideoCapture(0)

    # Infinite while loop to treat stack of image as video
    while True:
        # Reading frame(image) from video
        check, frame = video.read()

        # Initializing motion = 0(no motion)
        motion = 0

        # Converting color image to gray_scale image
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Converting gray scale image to GaussianBlur
        # so that change can be find easily
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # In first iteration we assign the value
        # of static_back to our first frame
        if static_back is None or (datetime.now() - static_taken) > timedelta(minutes=3):
            static_back = gray
            static_taken = datetime.now()
            print("new static back")
            continue

        # Difference between static background
        # and current frame(which is GaussianBlur)
        diff_frame = cv2.absdiff(static_back, gray)

        # If change in between static background and
        # current frame is greater than 30 it will show white color(255)
        thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
        thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)

        # Finding contour of moving object
        cnts,_ = cv2.findContours(thresh_frame.copy(),
                                        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in cnts:
            area = cv2.contourArea(contour)
            #if area > 8000:
            #print(f"Area {area}")
            if area < 9000:
                continue
            motion = 1

            (x, y, w, h) = cv2.boundingRect(contour)
            # making green rectangle around the moving object
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        # Appending status of motion
        motion_list.append(motion)

        motion_list = motion_list[-2:]

        # Appending Start time of motion
        if motion_list[-1] == 1 and motion_list[-2] == 0:
                time.append(datetime.now())
                play_sound()
                print("Start of motion")

        # Appending End time of motion
        if motion_list[-1] == 0 and motion_list[-2] == 1:
                time.append(datetime.now())
                #play_sound()
                print("end of motion")

        continue
        
        # Displaying image in gray_scale
        cv2.imshow("Gray Frame", gray)

        # Displaying the difference in currentframe to
        # the staticframe(very first_frame)
        cv2.imshow("Difference Frame", diff_frame)

        # Displaying the black and white image in which if
        # intensity difference greater than 30 it will appear white
        cv2.imshow("Threshold Frame", thresh_frame)

        # Displaying color frame with contour of motion of object
        cv2.imshow("Color Frame", frame)

        key = cv2.waitKey(1)
        # if q entered whole process will stop
        if key == ord('q'):
            # if something is movingthen it append the end time of movement
            if motion == 1:
                time.append(datetime.now())
            break

    # Appending time of motion in DataFrame
    for i in range(0, len(time), 2):
        df = df.append({"Start":time[i], "End":time[i + 1]}, ignore_index = True)

    # Creating a CSV file in which time of movements will be saved
    df.to_csv("Time_of_movements.csv")

    video.release()

    # Destroying all the windows
    cv2.destroyAllWindows()

    
if __name__ == '__main__':
    #play_sound()
    main()
