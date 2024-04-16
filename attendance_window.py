import os
import pickle
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime
from test import test
import tkinter as tk
from tkinter import messagebox

with open('antiSpoof.txt', 'r') as file:
    antiSpoof = [int(num) for line in file for num in line.split()]
with open('coolDown.txt', 'r') as file:
    coolDown = [int(num) for line in file for num in line.split()]

antiSpoofing=antiSpoof[0]
cooldown_time=coolDown[0]

def start_process():
    # Code to start the process goes here
    print("Process started")

if __name__ == '__main__':
    #### Database Authenticator ####
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(
        cred,
        {
            "databaseURL": "https://studentsattendance-7cd66-default-rtdb.firebaseio.com/",
            "storageBucket": "studentsattendance-7cd66.appspot.com",
        },
    )
    bucket = storage.bucket()

    #### Video Capture ####
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    imgBackground = cv2.imread("Resources/background.png")

    folderModePath = "Resources/Modes"
    modePathList = os.listdir(folderModePath)
    imgModeList = []
    for path in modePathList:
        imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

    # Load the encoding file
    print("FaceModule loading...")
    file = open("EncodeFile.p", "rb")
    encodeListKnownWithIds = pickle.load(file)
    file.close()
    encodeListKnown, studentIds = encodeListKnownWithIds
    print("FaceModule Loaded")

    modeType = 0
    counter = 0
    id = -1
    imgStudent = []

    #### Main loop ####
    while True:
        success, img = cap.read()

        recent_capture = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(recent_capture, cv2.COLOR_BGR2RGB)


        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        imgBackground[162:162 + 480, 55:55 + 640] = img
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        if faceCurFrame:
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)
                if antiSpoofing == 1:
                    live = test(
                        image=recent_capture,
                        model_dir='Silent-Face-Anti-Spoofing/resources/anti_spoof_models',
                        device_id=0
                    )
                    text = "AntiSpoofing Enabled"
                    cv2.putText(imgBackground, text, (10,700), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (128, 128, 128), 1, cv2.LINE_AA)
                    if live == 1:
                        if matches[matchIndex]:
                            y1, x2, y2, x1 = faceLoc
                            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                            id = studentIds[matchIndex]
                            if counter == 0:
                                cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                                cv2.imshow("Face Attendance", imgBackground)
                                cv2.waitKey(1)
                                counter = 1
                                modeType = 1
                else:
                    text = "AntiSpoofing Disabled"
                    cv2.putText(imgBackground, text, (10, 700), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (128, 128, 128), 1,
                                cv2.LINE_AA)
                    if matches[matchIndex]:
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                        imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                        id = studentIds[matchIndex]
                        if counter == 0:
                            cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                            cv2.imshow("Face Attendance", imgBackground)
                            cv2.waitKey(1)
                            counter = 1
                            modeType = 1

            if counter != 0:
                if counter == 1:
                    try:
                        # Get the Data
                        studentInfo = db.reference(f"Students/{id}").get()
                        # Get the Image from the storage
                        blob = bucket.get_blob(f"Images/{id}.png")
                        array = np.frombuffer(blob.download_as_string(), np.uint8)
                        imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                        # Update data of attendance
                        datetimeObject = datetime.strptime(
                            studentInfo["last_attendance_time"], "%Y-%m-%d %H:%M:%S"
                        )
                        secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                    except:
                        messagebox.showerror("Connection Issue","unable to fetch data from database")
                        print("something went wrong")


                    if secondsElapsed > cooldown_time:
                        ref = db.reference(f"Students/{id}")
                        studentInfo["total_attendance"] += 1
                        ref.child("total_attendance").set(studentInfo["total_attendance"])
                        ref.child("last_attendance_time").set(
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[44: 44 + 633, 808: 808 + 414] = imgModeList[
                            modeType
                        ]

                if modeType != 3:
                    if 15 < counter < 25:
                        modeType = 2
                    imgBackground[44: 44 + 633, 808: 808 + 414] = imgModeList[modeType]

                    if counter <= 15:
                        # noinspection PyUnboundLocalVariable
                        cv2.putText(
                            imgBackground,
                            str(studentInfo["total_attendance"]),
                            (861, 125),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (255, 255, 255),
                            1,
                        )
                        cv2.putText(
                            imgBackground,
                            str(studentInfo["dept"]),
                            (1006, 550),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (255, 255, 255),
                            1,
                        )
                        cv2.putText(
                            imgBackground,
                            str(id),
                            (1006, 493),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (255, 255, 255),
                            1,
                        )
                        cv2.putText(
                            imgBackground,
                            str(studentInfo["sec"]),
                            (910, 625),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (255, 255, 255),
                            1,
                        )
                        cv2.putText(
                            imgBackground,
                            str(studentInfo["year"]),
                            (1025, 625),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (255, 255, 255),
                            1,
                        )
                        cv2.putText(
                            imgBackground,
                            str(studentInfo["starting_year"]),
                            (1125, 625),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (255, 255, 255),
                            1,
                        )

                        (w, h), _ = cv2.getTextSize(
                            studentInfo["name"], cv2.FONT_HERSHEY_SIMPLEX, 1, 1
                        )
                        offset = (414 - w) // 2
                        cv2.putText(
                            imgBackground,
                            str(studentInfo["name"]),
                            (808 + offset, 445),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (255, 255, 255),
                            1,
                        )

                        imgBackground[175: 175 + 216, 909: 909 + 216] = imgStudent

                    counter += 1

                    if counter >= 25:
                        counter = 0
                        modeType = 0
                        studentInfo = []
                        imgStudent = []
                        imgBackground[44: 44 + 633, 808: 808 + 414] = imgModeList[
                            modeType
                        ]
        else:
            modeType = 0
            counter = 0
        # cv2.imshow("Webcam", img)
        cv2.imshow("Face Attendance", imgBackground)
        cv2.waitKey(1)
