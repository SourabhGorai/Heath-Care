import subprocess
import customtkinter as ctk
from pymongo import MongoClient
from db_connection import get_db_connection
import sys

# Get the database connection
db = get_db_connection()
appointments_collection = db['appointment_management']

# doc_usrn = sys.argv[1]  # Username passed from the previous page
doc_usrn = "sourabh_gorai"

# Function to fetch completed appointments for the doctor
def fetch_completed_appointments(doctor_usrn):
    return list(appointments_collection.find({"doctor_username": doctor_usrn, "done": True}))

# Function to display the completed appointments
def display_completed_appointments():
    appointments = fetch_completed_appointments(doc_usrn)
    
    # Create the table headers, including the new "Illness" column
    headers = ["SL No.", "Name", "Date", "Time", "Doctor Username", "Illness", "View Details"]
    for col, header in enumerate(headers):
        header_label = ctk.CTkLabel(appointments_frame, text=header, font=ctk.CTkFont(size=14, weight="bold"))
        header_label.grid(row=0, column=col, padx=5, pady=5)

    # Populate the table with appointment data, including the "Illness" field
    for index, appointment in enumerate(appointments):
        sl_no = index + 1
        ctk.CTkLabel(appointments_frame, text=str(sl_no)).grid(row=index + 1, column=0, padx=5, pady=5)
        ctk.CTkLabel(appointments_frame, text=appointment["patient_name"]).grid(row=index + 1, column=1, padx=5, pady=5)
        ctk.CTkLabel(appointments_frame, text=appointment["date"]).grid(row=index + 1, column=2, padx=5, pady=5)
        ctk.CTkLabel(appointments_frame, text=appointment["appointment_time"]).grid(row=index + 1, column=3, padx=5, pady=5)
        ctk.CTkLabel(appointments_frame, text=appointment["doctor_username"]).grid(row=index + 1, column=4, padx=5, pady=5)

        # Display the illness (sickness) from the appointment record
        illness = appointment.get("illness", "N/A")  # Use "N/A" if sickness is not available
        ctk.CTkLabel(appointments_frame, text=illness).grid(row=index + 1, column=5, padx=5, pady=5)

        view_details_button = ctk.CTkButton(appointments_frame, text="View Details", 
                                            command=lambda username=appointment["patient_username"]: view_details(username))
        view_details_button.grid(row=index + 1, column=6, padx=5, pady=5)

# Function to handle view details action
def view_details(username):
    # Call another script to view detailed information about the appointment
    subprocess.run(['python', 'viewDetails_toDoctor.py', username])
    print(f"Viewing details for: {username}")

# Initialize the main application
app = ctk.CTk()
app.geometry("750x500+400+250")
app.title("Completed Appointments")

# Create a frame to hold the appointment table
appointments_frame = ctk.CTkFrame(app)
appointments_frame.pack(pady=20, padx=20)

# Display completed appointments
display_completed_appointments()

# Back button to return to the previous page
back_button = ctk.CTkButton(app, text="Back", command=lambda:(app.destroy(), subprocess.run(['python', 'doctor.py',doc_usrn])))
back_button.pack(pady=10)

# Start the application
app.mainloop()
