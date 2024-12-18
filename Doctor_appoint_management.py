import subprocess
import customtkinter as ctk
from pymongo import MongoClient
from db_connection import get_db_connection
import sys

# Call the get_db_connection function to get the database connection
db = get_db_connection()
appointments_collection = db['appointment_management']

doc_usrn = sys.argv[1]
# doc_usrn = "sourabh_gorai"

# Function to fetch appointments where 'done' is false
def fetch_appointments():
    return list(appointments_collection.find({"done": False, "doctor_username": doc_usrn}))

# Function to update the appointment to done and set sickness for a specific username
def update_appointment_to_done(appointment_id, username, sickness):
    appointments_collection.update_one(
        {"_id": appointment_id, "patient_username": username},
        {"$set": {"done": True, "sickness": sickness}}
    )

# Fetch appointments and extract usernames
appointments = fetch_appointments()
usernames = [appointment["patient_username"] for appointment in appointments]
print(usernames)

# Initialize the application
app = ctk.CTk()
app.geometry("850x400+360+270")  # Adjust width for the new column
app.title("Appointment Management")

# Function to mark an appointment as done
def mark_as_done(index, appointment_id, username):
    sickness = sickness_entries[index].get()  # Get sickness from entry field
    # Update the appointment in the database
    update_appointment_to_done(appointment_id, username, sickness)

    # Update the button and label for the corresponding appointment
    done_button = done_buttons[index]
    done_button.configure(text="Done", command=lambda: None)  # Change button to plain text
    done_button.grid_forget()  # Remove the button from the layout
    done_label = ctk.CTkLabel(appointments_frame, text="Done", font=ctk.CTkFont(size=12))
    done_label.grid(row=index + 1, column=6, padx=5, pady=5)  # Place label in the same grid position

# Create a frame for the appointments
appointments_frame = ctk.CTkFrame(app)
appointments_frame.pack(pady=20, padx=20)

# Create headers for the table
headers = ["SL No.", "Name", "Date", "Time", "Sickness", "View Details", "Done"]
for col, header in enumerate(headers):
    header_label = ctk.CTkLabel(appointments_frame, text=header, font=ctk.CTkFont(size=14, weight="bold"))
    header_label.grid(row=0, column=col, padx=5, pady=5)

# List to hold the "Done" buttons and sickness entries
done_buttons = []
sickness_entries = []

# Fetch and create rows for each appointment
appointments = fetch_appointments()
for index, appointment in enumerate(appointments):
    sl_no = index + 1
    ctk.CTkLabel(appointments_frame, text=str(sl_no)).grid(row=index + 1, column=0, padx=5, pady=5)
    ctk.CTkLabel(appointments_frame, text=appointment["patient_name"]).grid(row=index + 1, column=1, padx=5, pady=5)
    ctk.CTkLabel(appointments_frame, text=appointment["date"]).grid(row=index + 1, column=2, padx=5, pady=5)
    ctk.CTkLabel(appointments_frame, text=appointment["appointment_time"]).grid(row=index + 1, column=3, padx=5, pady=5)

    # Add entry field for sickness
    sickness_entry = ctk.CTkEntry(appointments_frame, width=150)  # Adjust width as needed
    sickness_entry.grid(row=index + 1, column=4, padx=5, pady=5)
    sickness_entries.append(sickness_entry)  # Store entry reference

    view_details_button = ctk.CTkButton(appointments_frame, text="View Details", 
                                         command=lambda username=appointment["patient_username"]: view_details(username))
    view_details_button.grid(row=index + 1, column=5, padx=5, pady=5)

    done_button = ctk.CTkButton(appointments_frame, text="Done", 
                                 command=lambda index=index, appointment_id=appointment["_id"], username=appointment["patient_username"]: mark_as_done(index, appointment_id, username))
    done_button.grid(row=index + 1, column=6, padx=5, pady=5)

    # Append button to the list for later reference
    done_buttons.append(done_button)

# Function to handle view details action
def view_details(username):
    # Call doc_Profile.py with the username as an argument
    subprocess.run(['python', 'viewDetails_toDoctor.py', username])
    print(username)

# Add the Back button functionality
def go_back():
    app.destroy()  # Close the current window
    subprocess.run(['python', 'doctor.py', doc_usrn])  # Open doctor.py

# Add a Back button
back_button = ctk.CTkButton(app, text="Back", command=go_back)
back_button.pack(pady=10)  # Adjust the position as needed

# Start the application
app.mainloop()


# import subprocess
# import customtkinter as ctk
# from pymongo import MongoClient
# from db_connection import get_db_connection
# import sys

# # Call the get_db_connection function to get the database connection
# db = get_db_connection()  # Add parentheses to call the function
# appointments_collection = db['appointment_management']

# # doc_usrn = sys.argv[1]
# doc_usrn = "admin321"

# # Function to fetch appointments where 'done' is false
# def fetch_appointments():
#     return list(appointments_collection.find({"done": False, "doctor_usrn": doc_usrn}))

# # Function to update the appointment to done
# def update_appointment_to_done(appointment_id):
#     appointments_collection.update_one({"_id": appointment_id}, {"$set": {"done": True}})

# # Fetch appointments and extract usernames
# appointments = fetch_appointments()
# usernames = [appointment["username"] for appointment in appointments]
# print(usernames)

# # Initialize the application
# app = ctk.CTk()
# app.geometry("600x400+500+300")
# app.title("Appointment Management")

# # Function to mark an appointment as done
# def mark_as_done(index, appointment_id):
#     # Update the appointment in the database
#     update_appointment_to_done(appointment_id)

#     # Update the button and label for the corresponding appointment
#     done_button = done_buttons[index]
#     done_button.configure(text="Done", command=lambda: None)  # Change button to plain text
#     done_button.grid_forget()  # Remove the button from the layout
#     done_label = ctk.CTkLabel(appointments_frame, text="Done", font=ctk.CTkFont(size=12))
#     done_label.grid(row=index + 1, column=5, padx=5, pady=5)  # Place label in the same grid position

# # Create a frame for the appointments
# appointments_frame = ctk.CTkFrame(app)
# appointments_frame.pack(pady=20, padx=20)

# # Create headers for the table
# headers = ["SL No.", "Name", "Date", "Time", "View Details", "Done"]
# for col, header in enumerate(headers):
#     header_label = ctk.CTkLabel(appointments_frame, text=header, font=ctk.CTkFont(size=14, weight="bold"))
#     header_label.grid(row=0, column=col, padx=5, pady=5)

# # List to hold the "Done" buttons
# done_buttons = []

# # Fetch and create rows for each appointment
# appointments = fetch_appointments()
# for index, appointment in enumerate(appointments):
#     sl_no = index + 1
#     ctk.CTkLabel(appointments_frame, text=str(sl_no)).grid(row=index + 1, column=0, padx=5, pady=5)
#     ctk.CTkLabel(appointments_frame, text=appointment["name"]).grid(row=index + 1, column=1, padx=5, pady=5)
#     ctk.CTkLabel(appointments_frame, text=appointment["date"]).grid(row=index + 1, column=2, padx=5, pady=5)
#     ctk.CTkLabel(appointments_frame, text=appointment["time"]).grid(row=index + 1, column=3, padx=5, pady=5)

#     view_details_button = ctk.CTkButton(appointments_frame, text="View Details", 
#                                          command=lambda username=appointment["username"]: view_details(username))
#     view_details_button.grid(row=index + 1, column=4, padx=5, pady=5)

#     done_button = ctk.CTkButton(appointments_frame, text="Done", 
#                                  command=lambda index=index, appointment_id=appointment["_id"]: mark_as_done(index, appointment_id))
#     done_button.grid(row=index + 1, column=5, padx=5, pady=5)

#     # Append button to the list for later reference
#     done_buttons.append(done_button)

# # Function to handle view details action
# def view_details(username):
#     # Call doc_Profile.py with the username as an argument
#     subprocess.run(['python', 'viewDetails_toDoctor.py', username])
#     print(username)

# # Add the Back button functionality
# def go_back():
#     app.destroy()  # Close the current window
#     subprocess.run(['python', 'doctor.py',  doc_usrn])  # Open doctor.py

# # Add a Back button
# back_button = ctk.CTkButton(app, text="Back", command=go_back)
# back_button.pack(pady=10)  # Adjust the position as needed

# # Start the application
# app.mainloop()
