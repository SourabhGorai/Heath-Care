

import subprocess
import tkinter as tk
from PIL import ImageTk
import customtkinter as ctk
from customtkinter import CTkButton, CTkScrollableFrame
from db_connection import get_db_connection
from cryptography.fernet import Fernet
import sys
from fetch_image import retrieve_image
from updateImage import update_image_from_external
import base64
from bson import Binary


# Now, update the database with the new data
db = get_db_connection()

def back(app_instance):
    app_instance.master.destroy()  # Close the current window
    # Launch the patient signup page
    subprocess.run(['python', 'patient_dashboard.py', app_instance.username])

def encrypt_data(data,fernet_key):
    """Encrypt the provided data using the Fernet cipher."""
    cipher_suite = Fernet(fernet_key)
    if not isinstance(data, bytes):
        data = data.encode('utf-8')
    encrypted_data = cipher_suite.encrypt(data)
    return encrypted_data.decode('utf-8')

def decrypt_data(encrypted_data, fernet_key):
    """Decrypt the provided data using the Fernet cipher."""
    cipher_suite = Fernet(fernet_key)
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
    print("hello "+decrypted_data.decode('utf-8'))
    return decrypted_data.decode('utf-8')

class patientProfileApp:
    def __init__(self, master, username):
        self.master = master
        self.master.title("Patient Profile")
        self.master.geometry("800x600+350+200")
        self.username = username  # Store username for later use

        # Load patient's information
        self.patient_data = self.get_patient_data(username)

        # Create UI elements
        self.create_ui()
        self.display_image()

    def get_patient_data(self, username):
        # db = get_db_connection()
        pipeline = [{"$match": {"username": username}}, {"$project": {"_id": 1}}]
        patient_result = list(db['patient_details'].aggregate(pipeline))
        # print(patient_result)

        if patient_result:
            patient_id = patient_result[0]['_id']
            key_pipeline = [{"$match": {"_id": patient_id}}, {"$project": {"key": 1}}]
            key_result = list(db['keys'].aggregate(key_pipeline))

            if key_result:
                encoded_key = key_result[0]['key']
                keybytes = encoded_key
                print("decode wala ")
                print(keybytes)

                patient_data = db['patient_details'].find_one({"_id": patient_id})

                if patient_data:
                    return {
                        "name": decrypt_data(patient_data['name'], keybytes),
                        "dob": decrypt_data(patient_data['dob'], keybytes),
                        "gender": patient_data['gender'],
                        "ph_no": decrypt_data(patient_data['ph_no'], keybytes),
                        "email": decrypt_data(patient_data['email'], keybytes),
                        "address": decrypt_data(patient_data['address'], keybytes),
                        "blood_G": decrypt_data(patient_data['blood_G'], keybytes),
                        "allergy": decrypt_data(patient_data['allergy'], keybytes),
                        "chro_disease": decrypt_data(patient_data['chro_disease'], keybytes),
                        "prev_surgeries": decrypt_data(patient_data['prev_surgeries'], keybytes),
                    }
                             
        return None

    # def update_patient_data(self):
    #     print("inside update data")
    #     # Gather updated data from entry fields
    #     pipeline = [{"$match": {"username": username}}, {"$project": {"_id": 1, "ph_no":1}}]
    #     patient_result = list(db['patient_details'].aggregate(pipeline))
    #     if patient_result:
    #         patient_id = patient_result[0]['_id']
    #         key_pipeline = [{"$match": {"_id": patient_id}}, {"$project": {"key": 1}}]
    #         key_result = list(db['keys'].aggregate(key_pipeline))

    #         if key_result:
    #             encoded_key = key_result[0]['key']
    #             keybytes = encoded_key
    #             print()
    #             print(keybytes)

    #     print(self.name_entry.get())
    #     print(self.dob_entry.get())
    #     print(self.ph_no_entry.get())
    #     print(self.email_entry.get())
    #     print(self.address_entry.get())
    #     print(self.blood_G_entry.get())
    #     print(self.allergy_entry.get())
    #     print(self.chro_disease_entry.get())
    #     print(self.prev_surgeries_entry.get())
    
    #     updated_data = {
    #         "name": encrypt_data(self.name_entry.get(),keybytes),
    #         "dob": encrypt_data(self.dob_entry.get(),keybytes),
    #         "gender": self.patient_data['gender'],  # Keep the original gender value, as it's not an entry
    #         "ph_no": encrypt_data(self.ph_no_entry.get(),keybytes),
    #         "email": encrypt_data(self.email_entry.get(),keybytes),
    #         "address": encrypt_data(self.address_entry.get(),keybytes),
    #         "blood_G": encrypt_data(self.blood_G_entry.get(),keybytes),
    #         "allergy": encrypt_data(self.allergy_entry.get(),keybytes),
    #         "chro_disease": encrypt_data(self.chro_disease_entry.get(),keybytes),
    #         "prev_surgeries": encrypt_data(self.prev_surgeries_entry.get(),keybytes)
    #     }
    #     print("none")
        
    #     updated_data = {k: v for k, v in updated_data.items() if v != ""}
    #     # Log the updated data for debugging
    #     print("Updated Data:", updated_data)

        

    #     # Perform the update operation
    #     result = db['patient_details'].update_one({"username": self.username}, {"$set": updated_data})

    #     if result.modified_count > 0:
    #         print("patient data updated successfully.")
    #     else:
    #         print("No changes were made to the patient data.")

    def update_patient_data(self):
        print("inside update data")
        # Gather updated data from entry fields
        pipeline = [{"$match": {"username": self.username}}, {"$project": {"_id": 1, "ph_no": 1}}]
        patient_result = list(db['patient_details'].aggregate(pipeline))
        
        if patient_result:
            patient_id = patient_result[0]['_id']
            key_pipeline = [{"$match": {"_id": patient_id}}, {"$project": {"key": 1}}]
            key_result = list(db['keys'].aggregate(key_pipeline))

            if key_result:
                encoded_key = key_result[0]['key']
                keybytes = encoded_key
                print()
                print(keybytes)

        # Gather current values
        current_data = self.patient_data.copy()
        
        # Prepare updated data
        updated_data = {}
        
        # Check each entry field and update if new value is provided
        if self.name_entry.get():
            updated_data["name"] = encrypt_data(self.name_entry.get(), keybytes)
        else:
            updated_data["name"] = encrypt_data(current_data["name"],keybytes)  # Keep the original value if empty

        if self.dob_entry.get():
            updated_data["dob"] = encrypt_data(self.dob_entry.get(), keybytes)
        else:
            updated_data["dob"] = encrypt_data(current_data["dob"],keybytes)  # Keep the original value if empty

        updated_data["gender"] = current_data['gender']  # Keep the original gender value

        if self.ph_no_entry.get():
            updated_data["ph_no"] = encrypt_data(self.ph_no_entry.get(), keybytes)
        else:
            updated_data["ph_no"] = encrypt_data(current_data["ph_no"],keybytes)  # Keep the original value if empty

        if self.email_entry.get():
            updated_data["email"] = encrypt_data(self.email_entry.get(), keybytes)
        else:
            updated_data["email"] = encrypt_data(current_data["email"],keybytes)  # Keep the original value if empty

        if self.address_entry.get():
            updated_data["address"] = encrypt_data(self.address_entry.get(), keybytes)
        else:
            updated_data["address"] = encrypt_data(current_data["address"],keybytes)  # Keep the original value if empty

        if self.blood_G_entry.get():
            updated_data["blood_G"] = encrypt_data(self.blood_G_entry.get(), keybytes)
        else:
            updated_data["blood_G"] = encrypt_data(current_data["blood_G"],keybytes)  # Keep the original value if empty

        if self.allergy_entry.get():
            updated_data["allergy"] = encrypt_data(self.allergy_entry.get(), keybytes)
        else:
            updated_data["allergy"] = encrypt_data(current_data["allergy"],keybytes)  # Keep the original value if empty

        if self.chro_disease_entry.get():
            updated_data["chro_disease"] = encrypt_data(self.chro_disease_entry.get(), keybytes)
        else:
            updated_data["chro_disease"] = encrypt_data(current_data["chro_disease"],keybytes)  # Keep the original value if empty

        if self.prev_surgeries_entry.get():
            updated_data["prev_surgeries"] = encrypt_data(self.prev_surgeries_entry.get(), keybytes)
        else:
            updated_data["prev_surgeries"] = encrypt_data(current_data["prev_surgeries"],keybytes)  # Keep the original value if empty

        # Log the updated data for debugging
        print("Updated Data:", updated_data)

        # Perform the update operation
        result = db['patient_details'].update_one({"username": self.username}, {"$set": updated_data})

        if result.modified_count > 0:
            print("Patient data updated successfully.")
        else:
            print("No changes were made to the patient data.")




    def updateImg(self):
        print(f"Updating image for {self.username} in {'patient_details'}...")
        update_image_from_external(self.username, 'patient_details')
        self.display_image()

    def display_image(self):
        # Create a frame for the image
        image_frame = ctk.CTkFrame(self.master, fg_color="#2E2E2E")
        image_frame.place(relx=0.6, rely=0.15, relwidth=0.30, relheight=0.5)

        # Clear previous image label if it exists
        for widget in image_frame.winfo_children():
            widget.destroy()

        # Retrieve and display the image
        img = retrieve_image(self.username, 'patient_details')  # Pass correct collection name
        if img:
            img = img.resize((350, 350))  # Resize image for the display
            img_tk = ImageTk.PhotoImage(img)

            img_label = ctk.CTkLabel(image_frame, image=img_tk)
            img_label.image = img_tk  # Keep a reference to avoid garbage collection
            img_label.pack(pady=10)
        else:
            no_image_label = ctk.CTkLabel(image_frame, text="No Image Found", text_color="#FF0000", font=("Arial", 16))
            no_image_label.pack(pady=10)

    def create_ui(self):
        print("Inside UI")
        if not self.patient_data:
            error_label = ctk.CTkLabel(self.master, text="No patient data found.", text_color="#FF0000", font=("Arial", 16))
            error_label.place(relx=0.35, rely=0.5)
            return

        print("patient Data:", self.patient_data)

        # Create a scrollable frame
        scrollable_frame = CTkScrollableFrame(self.master)
        scrollable_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.85)

        # Frame for patient's information
        info_frame = ctk.CTkFrame(scrollable_frame, fg_color="#2E2E2E")
        info_frame.pack(fill="both", expand=True)

        # Display patient's information in entry fields
        labels = [
            "Name: ", "Date of Birth: ", "Gender: ", "Contact Number: ",
            "Email: ", "Permanent Address: ", "Blood Group: ",
            "Allergy: ", "Chronic Disease: ", "Previous Surgeries: "
        ]

        keys = [
            "name", "dob", "gender", "ph_no",
            "email", "address", "blood_G",
            "allergy", "chro_disease", "prev_surgeries"
        ]

        # Store entry references for updates
        self.name_entry = None
        self.dob_entry = None
        self.gender_entry = None
        self.ph_no_entry = None
        self.email_entry = None
        self.address_entry = None
        self.blood_G_entry = None
        self.allergy_entry = None
        self.chro_disease_entry = None
        self.prev_surgeries_entry = None

        print("Entering for loop, UI")

        for idx, label in enumerate(labels):
            l = ctk.CTkLabel(info_frame, text=label, text_color="#E0E0E0", font=("Arial", 16))
            l.grid(row=idx, column=0, padx=10, pady=5, sticky="w")

            key = keys[idx]
            value = self.patient_data.get(key, "N/A")

            # Debugging: Print out the key and its corresponding value
            print(f"Key: {key}, Value: {value}")

            if key != "gender":  # Gender will be displayed as a label, not an entry
                entry = ctk.CTkEntry(info_frame, placeholder_text=value)  # Use placeholder_text instead of text
                entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
                setattr(self, f"{key}_entry", entry)  # Store reference to entry
            else:
                gender_label = ctk.CTkLabel(info_frame, text=value, text_color="#FFFFFF", font=("Arial", 16))
                gender_label.grid(row=idx, column=1, padx=10, pady=5, sticky="w")

        print("out of for loop, UI")
        # Update Button
        update_button = CTkButton(self.master, text="Update", command=self.update_patient_data)
        update_button.place(relx=0.55, rely=0.92)

        # Back Button
        back_button = CTkButton(self.master, text="Back", command=lambda: back(self))
        back_button.place(relx=0.75, rely=0.92)

        UpdateImage_button = CTkButton(self.master, text="Update Image", command=self.updateImg)
        UpdateImage_button.place(relx=0.67, rely=0.65)

if __name__ == "__main__":
    root = ctk.CTk()
    # username = "sanmarg123"  # Replace this with the actual username passed from the previous page
    username = sys.argv[1]  # Replace this with the actual username passed from the previous page
    app = patientProfileApp(root, username)
    root.mainloop()


