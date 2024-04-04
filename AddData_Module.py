import os
import firebase_admin
import json
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://studentsattendance-7cd66-default-rtdb.firebaseio.com/"
})
ref = db.reference('Students')

home_dir = os.path.expanduser('~')
dir_and_file = 'AttendanceSystem_asset/data.json'
json_file_path = os.path.join(home_dir, dir_and_file)
with open(json_file_path, 'r') as file:
    data = json.load(file)

print("Uploading to Database...")
for key, value in data.items():
    ref.child(key).set(value)
print("Upload Complete")
