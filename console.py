import json
import os
import tkinter as tk
import subprocess
from tkinter import simpledialog, messagebox

with open('antiSpoof.txt', 'r') as file:
    antiSpoof = [int(num) for line in file for num in line.split()]

with open('coolDown.txt', 'r') as file:
    coolDown = [int(num) for line in file for num in line.split()]

def button6_cmd():
    faceadd_proccess=subprocess.Popen(["python", file_path("AddFace_Module.py")])
    faceadd_proccess.wait()
    messagebox.showinfo("FaceAdded", "Faces Added Successfully")

def button5_cmd():
    datadd_proccess=subprocess.Popen(["python", file_path("AddData_Module.py")])
    datadd_proccess.wait()
    messagebox.showinfo("DataAdded", "Data Added Successfully")

def button4_cmd():
    new_window = tk.Toplevel(root)
    new_window.title("Enter Details")

    # Labels and Entries for each prompt
    labels = ["Roll No.", "Name", "Dept", "Starting Year", "Total Attendance", "Sec", "Year", "Last Attendance Time"]
    entries = []

    for i, label_text in enumerate(labels):
        label = tk.Label(new_window, text=label_text)
        label.grid(row=i, column=0)
        entry = tk.Entry(new_window)
        entry.grid(row=i, column=1)
        entries.append(entry)

    # Submit button to save data
    def submit():
        data = {}
        for i, entry in enumerate(entries):
            if i == 0:
                key = entry.get()
            else:
                data[labels[i].lower()] = entry.get()

        directory = os.path.expanduser("~/AttendanceSystem_asset/")
        if not os.path.exists(directory):
            os.makedirs(directory)
        data_json = os.path.join(directory, 'data.json')

        # Save data to JSON file
        with open(data_json, 'r+') as file:
            try:
                data_dict = json.load(file)
            except json.JSONDecodeError:
                data_dict = {}
            data_dict[key] = data
            file.seek(0)
            json.dump(data_dict, file, indent=4)
            file.truncate()

        messagebox.showinfo("Success", "Data saved successfully.")
        new_window.destroy()

    submit_button = tk.Button(new_window, text="Submit", command=submit)
    submit_button.grid(row=len(labels), column=0, columnspan=2)

def button3_cmd():
    value = simpledialog.askinteger("Time Lag", "Enter a time in Seconds:",parent=root)
    if value is not None:
        coolDown_text1 = f"CoolDown Time: {value}s"
        button3.config(text=coolDown_text1, command=button3_cmd)
        with open('coolDown.txt', 'w') as f:
            f.write(str(value))
        with open('coolDown.txt', 'r') as file:
            coolDown1 = []
            for line in file:
                for num in line.split():
                    coolDown1.append(int(num))

def button2_cmd():
    with open('antiSpoof.txt', 'r') as file:
        num = [int(num) for line in file for num in line.split()]
    print(num)
    if num==[1]:
        button2.config(text="AntiSpoofing: Disabled", command=button2_cmd)
        with open('antiSpoof.txt', 'w') as f:
            f.write("0")
    else:
        button2.config(text="AntiSpoofing: Enabled", command=button2_cmd)
        with open('antiSpoof.txt', 'w') as f:
            f.write("1")

def file_path(file_name):
    file_path = os.path.join('/Users/suvasanketrout/codes/projects/python/FaceReconationAttendance', file_name)
    return file_path

def button1_cmd():
    global process, is_running
    if is_running:
        if process and process.poll() is None:
            process.kill()
        button1.config(text="Start Attendance Recording", command=button1_cmd)
        is_running = False
    else:
        process = subprocess.Popen(["python", file_path("main.py")])
        button1.config(text="Stop Attendance Recording", command=button1_cmd)
        is_running = True

root = tk.Tk()
root.title("Attendance System Console")
root.geometry('400x400')


# Attendance
button1 = tk.Button(root, text="Start Attendance Recording", command=button1_cmd)
button1.pack(side='top', padx=10, pady=40,fill='x')

# AntiSpoofing
if antiSpoof==[1]:
    button2 = tk.Button(root, text="AntiSpoofing: Enabled", command=button2_cmd)
    button2.pack(side='top', padx=10, pady=0,fill='x')
if antiSpoof==[0]:
    button2 = tk.Button(root, text="AntiSpoofing: Disabled", command=button2_cmd)
    button2.pack(side='top', padx=10, pady=0,fill='x')


# Cool Down
coolDown_text="Time Lag: "+str(coolDown[0])+"s"
button3 = tk.Button(root, text=coolDown_text, command=button3_cmd)
button3.pack(side='top', padx=10, pady=0,fill='x')

# Data.json editor
button4 = tk.Button(root, text="data.json editor", command=button4_cmd)
button4.pack(side='top', padx=10, pady=0, fill='x')

# Add Data
button5 = tk.Button(root, text="Add Data", command=button5_cmd)
button5.pack(side='top', padx=10, pady=0, fill='x')

# Add Face
button6 = tk.Button(root, text="Add Face", command=button6_cmd)
button6.pack(side='top', padx=10, pady=0, fill='x')


process = None
is_running = False

root.mainloop()
