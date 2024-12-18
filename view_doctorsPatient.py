import subprocess
import sys
import customtkinter as ctk
from tkinter import messagebox
from pymongo import MongoClient
from db_connection import get_db_connection
from cryptography.fernet import Fernet
from datetime import datetime
# from customtkinter import CTk  # Import CTkMessagebox

patient_username = sys.argv[1]
patient_name = sys.argv[2]

# Call the get_db_connection function to get the database connection
db = get_db_connection()
doctors_collection = db['doctor_details']
keys_collection = db['keys']
availability_collection = db['doc_availability_records']
appointments_collection = db['appointment_management']  # Collection for appointments

# Function to fetch all doctors
def fetch_doctors():
    return list(doctors_collection.find())

# Function to get the Fernet key for a specific username
def get_fernet_key(id):
    key_pipeline = [{"$match": {"_id": id}}, {"$project": {"key": 1}}]
    key_result = list(db['keys'].aggregate(key_pipeline))

    if key_result:
        encoded_key = key_result[0]['key']
        keybytes = encoded_key
        return keybytes
    return None

# Function to decrypt the doctor's name
def decrypt_data(encrypted_data, fernet_key):
    cipher_suite = Fernet(fernet_key)
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
    return decrypted_data.decode('utf-8')

# Function to fetch today's availability for doctors
def fetch_today_availability():
    today_date = datetime.now().date().isoformat()  # Get today's date in 'YYYY-MM-DD' format
    availability_record = availability_collection.find_one({"date": today_date})
    if availability_record:
        return availability_record.get("available_docs", [])
    return []

# Function to save the appointment data
def save_appointment(patient_name, patient_username, doctor_username, appointment_time):
    # Convert appointment_time (datetime.time) to a string
    appointment_time_str = appointment_time.strftime("%H:%M:%S")
    today_date = datetime.today().date().isoformat()
    # Create the appointment data
    appointment_data = {
        "patient_name": patient_name,
        "patient_username": patient_username,
        "doctor_username": doctor_username,
        "timestamp": datetime.now(),
        "date": today_date,
        "appointment_time": appointment_time_str,  # Use the string representation
        "done": False,
        "illness": "N/A"
    }
    
    # Save the appointment to the collection
    appointments_collection.insert_one(appointment_data)

# Initialize the application
app = ctk.CTk()
app.geometry("800x400+360+270")
app.title("Doctor Management")
ctk.set_appearance_mode("dark")  # Set a dark theme for the app
ctk.set_default_color_theme("blue")  # Set the default color theme

# Create a frame for the doctors
doctors_frame = ctk.CTkFrame(app)
doctors_frame.pack(pady=20, padx=20, fill='both', expand=True)

# Add title label
title_label = ctk.CTkLabel(doctors_frame, text="Available Doctors", font=ctk.CTkFont(size=16, weight="bold"))
title_label.grid(row=0, column=0, columnspan=5, pady=(10, 5))

# Create headers for the table
headers = ["Name", "Specialization", "Today's Availability", "More Info", "Take Appointment"]
for col, header in enumerate(headers):
    header_label = ctk.CTkLabel(doctors_frame, text=header, font=ctk.CTkFont(size=14, weight="bold"))
    header_label.grid(row=1, column=col, padx=5, pady=5, sticky="ew")

# Create a scrollable frame for doctors
scrollable_frame = ctk.CTkScrollableFrame(doctors_frame)
scrollable_frame.grid(row=2, column=0, columnspan=len(headers), sticky='nsew')

# Configure the columns to be wider and set uniform weight
for col in range(len(headers)):
    doctors_frame.grid_columnconfigure(col, weight=1)

# Fetch doctors and today's availability
doctors = fetch_doctors()
today_availability = fetch_today_availability()

# Create rows for each doctor
for index, doctor in enumerate(doctors):
    # Get the Fernet key for the doctor's username
    fernet = get_fernet_key(doctor["_id"])
    decrypted_name = decrypt_data(doctor["name"], fernet) if fernet else "N/A"

    # Check if the doctor is available today
    availability_status = "Available" if decrypted_name in today_availability else "Not Available"

    # Create labels for each data cell with sticky alignment
    ctk.CTkLabel(scrollable_frame, text=decrypted_name).grid(row=index, column=0, padx=10, pady=5, sticky="ew")
    ctk.CTkLabel(scrollable_frame, text=doctor["specialization"]).grid(row=index, column=1, padx=32, pady=5, sticky="ew")
    ctk.CTkLabel(scrollable_frame, text=availability_status).grid(row=index, column=2, padx=65, pady=5, sticky="ew")

    # More Info button
    more_info_button = ctk.CTkButton(scrollable_frame, text="More Info",
                                       command=lambda username=doctor["username"]: more_info(username),
                                       width=120)  # Set a fixed width for buttons
    more_info_button.grid(row=index, column=3, padx=0, pady=5, sticky="ew")

    # Take Appointment button
    take_appointment_button = ctk.CTkButton(scrollable_frame, text="Take Appointment",
                                             command=lambda username=doctor["username"], name=decrypted_name: confirm_appointment(username, name),
                                             width=120)  # Set a fixed width for buttons
    take_appointment_button.grid(row=index, column=4, padx=30, pady=5, sticky="ew")

# Function to handle more info action
def more_info(username):
    subprocess.run(['python', 'view_doctorsInfoPatient.py', username])

# Function to confirm the appointment
def confirm_appointment(doctor_username, doctor_name):
    confirmation = messagebox.askyesno("Confirm Appointment", f"Do you want to confirm the appointment with Dr. {doctor_name}?")
    if confirmation:
        # You would typically gather patient info (e.g., username) here, possibly with a popup for confirmation
        # patient_name = "Sanmarg Sandeep Yadav"  # Replace with actual patient name retrieval logic
        # patient_username = "iloveShivani"  # Replace with actual patient username retrieval logic
        appointment_time = datetime.now()  # Replace with user-selected time, if applicable

        # Save the appointment
        save_appointment(patient_name, patient_username, doctor_username, appointment_time)


# Add the Back button functionality
def go_back():
    app.destroy()  # Close the current window
    subprocess.run(['python', 'patient_dashboard.py',patient_username])

# Add a Back button
back_button = ctk.CTkButton(app, text="Back", command=go_back)
back_button.pack(pady=10)

# Start the application
app.mainloop()

