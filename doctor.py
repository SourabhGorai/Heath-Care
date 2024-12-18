# import os
# import subprocess
# import customtkinter as ctk
# import sys

# # Initialize the window
# app = ctk.CTk()
# app.geometry("600x400+500+300")
# app.title("Doctor Dashboard")

# # username = sys.argv[1]
# username = "admin321"
# print(username)

# # Variable to track availability
# is_available = False

# # Function to show the Doctor Profile Page
# def show_doctor_profile():
#     app.destroy()  # Close the login window
#     subprocess.run(['python', 'doc_Profile.py', username])

# # Function to manage appointments
# def manage_appointments():
#     app.destroy()  # Close the login window
#     subprocess.run(['python', 'appoint_management.py', username])

# # Function to view medical records
# def view_medical_records():
#     app.destroy()  # Close the login window
#     subprocess.run(['python', 'doc_prevRecords.py', username])

# # Function to manage doctor profile
# def manage_doctor_profile():
#     app.destroy()  # Close the login window
#     subprocess.run(['python', 'manage_docProf.py', username])

# # Function to toggle availability
# def toggle_availability():
#     global is_available
#     is_available = not is_available
#     availability_status_label.configure(text="Available Today: " + ("Yes" if is_available else "No"))

# # Title label
# title_label = ctk.CTkLabel(app, text="Doctor Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
# title_label.pack(pady=20)

# # Availability toggle button
# availability_toggle = ctk.CTkButton(app, text="Toggle Availability", command=toggle_availability)
# availability_toggle.pack(pady=10)

# # Label to display availability status
# availability_status_label = ctk.CTkLabel(app, text="Available Today: No", font=ctk.CTkFont(size=14))
# availability_status_label.pack(pady=10)

# # Buttons for different sections
# doctor_profile_btn = ctk.CTkButton(app, text="View Doctor Profile", command=show_doctor_profile)
# doctor_profile_btn.pack(pady=10)

# appointments_btn = ctk.CTkButton(app, text="Appointment Management", command=manage_appointments)
# appointments_btn.pack(pady=10)

# medical_records_btn = ctk.CTkButton(app, text="View Medical Records", command=view_medical_records)
# medical_records_btn.pack(pady=10)

# profile_management_btn = ctk.CTkButton(app, text="Manage Doctor Profile", command=manage_doctor_profile)
# profile_management_btn.pack(pady=10)

# # Label to display the current section's content
# doctor_label = ctk.CTkLabel(app, text="", font=ctk.CTkFont(size=14))
# doctor_label.pack(pady=20)

# # Start the application
# app.mainloop()


import os
import subprocess
import customtkinter as ctk
import sys
from pymongo import MongoClient
from datetime import datetime
from db_connection import get_db_connection
from cryptography.fernet import Fernet

# Initialize the window
app = ctk.CTk()
app.geometry("600x450+500+300")
app.title("Doctor Dashboard")

db = get_db_connection()
availability_collection = db['doc_availability_records']

def decrypt_data(encrypted_data, fernet_key):
    """Decrypt the provided data using the Fernet cipher."""
    cipher_suite = Fernet(fernet_key)  # Use Fernet instead of Telnet
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
    print(decrypted_data.decode('utf-8'))
    return decrypted_data.decode('utf-8')

def getDocName():
    # Fetch doctor data using aggregation
    doctor_data = list(db['doctor_details'].aggregate([{"$match": {"username": username}},{"$project": {"_id": 1, "name": 1}} ]))
    
    print("Doctor Data Retrieved:", doctor_data)  # Debugging line to print the doctor data
        
    if doctor_data:  # If the list is not empty
        # Access the first (and expected only) document in the list
        doctor = doctor_data[0]
        # Separate ID and Name
        doctor_id = doctor['_id']  # Get the doctor's ID
        doctor_name = doctor['name']
        
    # Fetch the encryption key based on the doctor ID
    key_pipeline = [{"$match": {"_id": doctor_id}}, {"$project": {"key": 1}}]
    key_result = list(db['keys'].aggregate(key_pipeline))
        
    if key_result:
        encoded_key = key_result[0]['key']  # Retrieve the encryption key
        keybytes = encoded_key
        
        # Decrypt the doctor's name
        decrypted_name = decrypt_data(doctor_name, keybytes)  # Pass the correct variable
        
        print("doc_name : "+decrypted_name)
        return decrypted_name
    else:
        print("Key not found for the doctor.")
        return None

username = sys.argv[1]
# username = "sourabh_gorai"
doctor_name = getDocName()  # Retrieve the doctor's name
print(doctor_name)

# Variable to track availability
is_available = False

# Function to update availability in MongoDB
def update_availability():
    global is_available
    
    today_date = datetime.now().strftime("%Y-%m-%d")  # Get today's date
    print(f"Today Date: {today_date}")  # Debugging: Print today's date

    # Use aggregation to find the record
    record = list(availability_collection.aggregate([
        {"$match": {"date": today_date}},
        {"$limit": 1}
    ]))

    print(f"Record Found: {record}")  # Debugging: Print the found record
    
    if is_available:
        if record:
            # Add the doctor to the existing array
            print("Updating existing record...")  # Debugging
            availability_collection.update_one(
                {"date": today_date},
                {"$addToSet": {"available_docs": doctor_name}}
            )
        else:
            # Create a new record for today
            print("Creating new record...")  # Debugging
            availability_collection.insert_one({
                "date": today_date,
                "available_docs": [doctor_name]
            })
    else:
        if record:
            print("Removing doctor from the availability...")  # Debugging
            # Remove the doctor from the array
            availability_collection.update_one(
                {"date": today_date},
                {"$pull": {"available_docs": doctor_name}}
            )
        else:
            print("No existing record to update.")  # Debugging

# Function to toggle availability
def toggle_availability():
    global is_available
    is_available = not is_available
    availability_status_label.configure(text="Available Today: " + ("Yes" if is_available else "No"))
    
    print(f"Toggling availability to: {is_available}")  # Debugging
    update_availability()  # Update MongoDB whenever the availability changes

# Function to go back to the previous screen or main menu
def logout():
    app.destroy()  # Close the current window
    # Replace 'main_menu.py' with the actual name of your main menu file or previous screen file
    subprocess.run(['python', 'login.py'])

# Function to show the Doctor Profile Page
def show_doctor_profile():
    app.destroy()  # Close the login window
    subprocess.run(['python', 'doc_Profile.py', username])

# Function to manage appointments
def manage_appointments():
    app.destroy()  # Close the login window
    subprocess.run(['python', 'Doctor_appoint_management.py', username])

# Function to view medical records
def view_medical_records():
    app.destroy()  # Close the login window
    subprocess.run(['python', 'doc_prevRecords.py', username])

# Function to manage doctor profile
def manage_doctor_profile():
    app.destroy()  # Close the login window
    subprocess.run(['python', 'manage_docProf.py', username])

# Title label
title_label = ctk.CTkLabel(app, text="Doctor Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
title_label.pack(pady=20)

# Availability toggle button
availability_toggle = ctk.CTkButton(app, text="Toggle Availability", command=toggle_availability)
availability_toggle.pack(pady=10)

# Label to display availability status
availability_status_label = ctk.CTkLabel(app, text="Available Today: No", font=ctk.CTkFont(size=14))
availability_status_label.pack(pady=10)

# Buttons for different sections
doctor_profile_btn = ctk.CTkButton(app, text="View Doctor Profile", command=show_doctor_profile)
doctor_profile_btn.pack(pady=10)

appointments_btn = ctk.CTkButton(app, text="Appointment Management", command=manage_appointments)
appointments_btn.pack(pady=10)

medical_records_btn = ctk.CTkButton(app, text="View Medical Records", command=view_medical_records)
medical_records_btn.pack(pady=10)

profile_management_btn = ctk.CTkButton(app, text="Manage Doctor Profile", command=manage_doctor_profile)
profile_management_btn.pack(pady=10)

# Back button
logout_button = ctk.CTkButton(app, text="Logout", command=logout)
logout_button.pack(pady=10)

# Label to display the current section's content
doctor_label = ctk.CTkLabel(app, text="", font=ctk.CTkFont(size=14))
doctor_label.pack(pady=20)

# Start the application
app.mainloop()

