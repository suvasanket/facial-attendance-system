import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://studentsattendance-7cd66-default-rtdb.firebaseio.com/",
    'storageBucket':"studentsattendance-7cd66.appspot.com"
})


# Importing student images
home_dir = os.path.expanduser('~')
faces_path = 'AttendanceSystem_asset/Images'
folderPath = os.path.join(home_dir, faces_path)

# folderPath = 'Images'
pathList = os.listdir(folderPath)
imgList = []
studentIds = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])

    uploadTo = f'Images/{path}'
    uploadFrom = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(uploadTo)
    blob.upload_from_filename(uploadFrom)

print("Image Uploaded to Database")

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


print("Encoding...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")