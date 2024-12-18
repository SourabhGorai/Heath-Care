import base64
import os
import subprocess
import tkinter as tk
import customtkinter as ctk
from customtkinter import CTkButton
from db_connection import get_db_connection
from cryptography.fernet import Fernet
import sys
from fetch_image import retrieve_image  # Import the function to fetch image
from PIL import ImageTk

def back(app_instance):
    app_instance.master.destroy()  # Close the current window
    # Launch the doctor signup page
    subprocess.run(['python', 'doctor.py', username])

def decrypt_data(encrypted_data, fernet_key):
    """Decrypt the provided data using the Fernet cipher."""
    cipher_suite = Fernet(fernet_key)
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
    return decrypted_data.decode('utf-8')

class DoctorProfileApp:
    def __init__(self, master, username):
        self.master = master
        self.master.title("Doctor Profile")
        self.master.geometry("800x500+350+200")

        # Load doctor's information
        self.doctor_data = self.get_doctor_data(username)

        # Create UI elements
        self.create_ui()

    def get_doctor_data(self, username):
        db = get_db_connection()

        # Find the doctor's ID using their username
        pipeline = [{"$match": {"username": username}},
                    {"$project": {"_id": 1}}]
        doctor_result = list(db['doctor_details'].aggregate(pipeline))

        if doctor_result:
            doctor_id = doctor_result[0]['_id']  # Extract the doctor ID
            
            # Retrieve the encryption key using the doctor's ID
            key_pipeline = [{"$match": {"_id": doctor_id}},
                            {"$project": {"key": 1}}]
            key_result = list(db['keys'].aggregate(key_pipeline))

            if key_result:
                encoded_key = key_result[0]['key']
                keybytes = encoded_key

                # Retrieve doctor data
                doctor_data = db['doctor_details'].find_one({"_id": doctor_id})

                if doctor_data:
                    # Decrypt the data
                    doctor_info = {
                        "name": decrypt_data(doctor_data['name'], keybytes),
                        "dob": decrypt_data(doctor_data['dob'], keybytes),
                        "gender": doctor_data['gender'],
                        "contact_no": decrypt_data(doctor_data['ph_no'], keybytes),
                        "email": decrypt_data(doctor_data['email'], keybytes),
                        "address": decrypt_data(doctor_data['address'], keybytes),
                        "medical_license_no": decrypt_data(doctor_data['medical_lisc_no'], keybytes),
                        "specialization": doctor_data['specialization'],
                        "qualification": doctor_data['qualification'],
                        "available_days": doctor_data['available_days'],
                        "profile_picture": doctor_data.get('profile_picture'),  # Get image ID
                    }

                    return doctor_info
        return None

    def create_ui(self):
        if not self.doctor_data:
            error_label = ctk.CTkLabel(
                self.master, text="No doctor data found.", text_color="#FF0000", font=("Arial", 16))
            error_label.place(relx=0.35, rely=0.5)
            return

        # Frame for doctor's information
        info_frame = ctk.CTkFrame(self.master, fg_color="#2E2E2E")
        info_frame.place(relx=0.05, rely=0.05, relwidth=0.5, relheight=0.9)

        # Display doctor's information
        labels = [
            "Name: ", "Date of Birth: ", "Gender: ", "Contact Number: ",
            "Email: ", "Permanent Address: ", "Medical License No: ",
            "Specialization: ", "Qualification: ", "Available Days: "
        ]

        keys = [
            "name", "dob", "gender", "contact_no",
            "email", "address", "medical_license_no",
            "specialization", "qualification", "available_days"
        ]

        for idx, label in enumerate(labels):
            l = ctk.CTkLabel(info_frame, text=label,
                             text_color="#E0E0E0", font=("Arial", 16))
            l.grid(row=idx, column=0, padx=10, pady=5, sticky="w")

            key = keys[idx]
            value = self.doctor_data.get(key, "N/A")
            v = ctk.CTkLabel(info_frame, text=value,
                             text_color="#FFFFFF", font=("Arial", 16))
            v.grid(row=idx, column=1, padx=10, pady=5, sticky="w")

        # Fetch the image if available
        image_id = self.doctor_data.get('profile_picture')
        if image_id:
            self.display_image(image_id)

        # Back Button
        back_button = CTkButton(self.master, text="Back",
                                command=lambda: back(self))
        back_button.place(relx=0.75, rely=0.88)

    def display_image(self, image_id):
        # Create a frame for the image
        image_frame = ctk.CTkFrame(self.master, fg_color="#2E2E2E")
        image_frame.place(relx=0.6, rely=0.05, relwidth=0.35, relheight=0.9)

        # Retrieve and display the image
        img = retrieve_image(username, 'doctor_details')  # Pass correct collection name
        if img:
            img = img.resize((350, 350))  # Resize image for the display
            img_tk = ImageTk.PhotoImage(img)
            img_label = ctk.CTkLabel(image_frame, image=img_tk)
            img_label.image = img_tk  # Keep a reference to avoid garbage collection
            img_label.pack(pady=10)

if __name__ == "__main__":
    root = ctk.CTk()
    # username = "sourabh_gorai"
    username = sys.argv[1]
    app = DoctorProfileApp(root, username)
    root.mainloop()
