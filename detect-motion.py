import cv2
import datetime
import random
import subprocess
import logging

time_format = "%H:%M:%S"
formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt=time_format
)

# Create a logger and set the custom formatter
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
log = logging.getLogger("detect-motion")


def play_sound():
    sound = random.choice(
        [
            # "Ingen-hemma.mp3)
            "woman_scream.mp3",
            "Maja jag kommer ata upp er.mp3",
            "Maja-skriker.mp3",
            "Mala har finns det spoken.mp3",
            "Melvin ater upp dig.mp3",
            "Melvin ha ha ha.mp3",
            "Melvin nu kommer jag och ater upp er.mp3",
            "Stefan ater upp er.mp3",
            "Stefan hahaha.mp3",
            "Stefan har far man bara gronsaker.mp3",
            "Stefan har finns det bara ackligt godis.mp3",
            # "Stefan godiset är slut.mp3",
        ]
    )
    log.info(f"Playing {sound}")
    subprocess.run(["mpg123", sound], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def frame_changes(refresh_background_interval=datetime.timedelta(minutes=2)):
    video = cv2.VideoCapture(0)
    background = None
    background_refreshed = None
    try:
        while True:
            check, frame = video.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if (
                background is None
                or (datetime.datetime.now() - background_refreshed)
                > refresh_background_interval
            ):
                background = gray
                background_refreshed = datetime.datetime.now()
                continue

            diff_frame = cv2.absdiff(background, gray)
            yield diff_frame
    except KeyboardInterrupt:
        return
    finally:
        log.info("Shutting down")
        video.release()


def find_contours(diff_frame):
    # enhance diff
    threshold_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
    dialated_frame = cv2.dilate(threshold_frame, None, iterations=2)

    contours, _ = cv2.findContours(
        dialated_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    for contour in contours:
        yield contour


def has_movement(diff_frame, minimum_area):
    for contour in find_contours(diff_frame):
        area = cv2.contourArea(contour)
        if area > 9000:
            return True

    return False


def main():
    log.info("Starting up")
    is_moving = False
    for diff_frame in frame_changes():
        if has_movement(diff_frame, minimum_area=9000):
            if not is_moving:
                log.info("Detected motion")
                play_sound()
            is_moving = True
        else:
            if is_moving:
                log.info("No more motion")
            is_moving = False


if __name__ == "__main__":
    # play_sound()
    main()
