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

db = get_db_connection()

def back(app_instance):
    app_instance.master.destroy()  # Close the current window
    # Launch the doctor signup page
    subprocess.run(['python', 'doctor.py', app_instance.username])

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
    return decrypted_data.decode('utf-8')

class DoctorProfileApp:
    def __init__(self, master, username):
        self.master = master
        self.master.title("Doctor Profile")
        self.master.geometry("800x600+350+200")
        self.username = username  # Store username for later use

        # Load doctor's information
        self.doctor_data = self.get_doctor_data(username)

        # Create UI elements
        self.create_ui()
        self.display_image()

    def get_doctor_data(self, username):
        pipeline = [{"$match": {"username": username}}, {"$project": {"_id": 1}}]
        doctor_result = list(db['doctor_details'].aggregate(pipeline))

        if doctor_result:
            doctor_id = doctor_result[0]['_id']
            key_pipeline = [{"$match": {"_id": doctor_id}}, {"$project": {"key": 1}}]
            key_result = list(db['keys'].aggregate(key_pipeline))

            if key_result:
                encoded_key = key_result[0]['key']
                keybytes = encoded_key

                doctor_data = db['doctor_details'].find_one({"_id": doctor_id})

                if doctor_data:
                    return {
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
                        "timing": doctor_data.get('timing', []),  # Get the existing timing array
                    }
        return None

    def update_doctor_data(self):
        print("inside update data")
        # Gather updated data from entry fields
        pipeline = [{"$match": {"username": self.username}}, {"$project": {"_id": 1, "ph_no": 1}}]
        doctor_result = list(db['doctor_details'].aggregate(pipeline))
        
        if doctor_result:
            patient_id = doctor_result[0]['_id']
            key_pipeline = [{"$match": {"_id": patient_id}}, {"$project": {"key": 1}}]
            key_result = list(db['keys'].aggregate(key_pipeline))

            if key_result:
                encoded_key = key_result[0]['key']
                keybytes = encoded_key
                print()
                print(keybytes)

        # Gather current values
        current_data = self.doctor_data.copy()
        
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

        if self.contact_no_entry.get():
            updated_data["ph_no"] = encrypt_data(self.contact_no_entry.get(), keybytes)
        else:
            print(current_data["contact_no"])
            updated_data["ph_no"] = encrypt_data(current_data["contact_no"],keybytes)  # Keep the original value if empty

        if self.email_entry.get():
            updated_data["email"] = encrypt_data(self.email_entry.get(), keybytes)
        else:
            updated_data["email"] = encrypt_data(current_data["email"],keybytes)  # Keep the original value if empty

        if self.address_entry.get():
            updated_data["address"] = encrypt_data(self.address_entry.get(), keybytes)
        else:
            updated_data["address"] = encrypt_data(current_data["address"],keybytes)  # Keep the original value if empty

        updated_data["medical_lisc_no"] = encrypt_data(current_data['medical_license_no'],keybytes)

        if self.specialization_entry.get():
            updated_data["specialization"] = self.specialization_entry.get()
        else:
            updated_data["specialization"] = current_data["specialization"]  # Keep the original value if empty

        if self.qualification_entry.get():
            updated_data["qualification"] = self.qualification_entry.get()
        else:
            updated_data["qualification"] = current_data["qualification"]  # Keep the original value if empty

        if self.available_days_entry.get():
            updated_data["available_days"] = self.available_days_entry.get()
        else:
            updated_data["available_days"] = current_data["available_days"] # Keep the original value if empty

        
        # Log the updated data for debugging
        print("Updated Data:", updated_data)

        # Perform the update operation
        result = db['doctor_details'].update_one({"username": self.username}, {"$set": updated_data})

        if result.modified_count > 0:
            print("Doctor data updated successfully.")
        else:
            print("No changes were made to the patient data.")

        '''
        print("Updated Data:", updated_data)

        # Now, update the database with the new data
        db = get_db_connection()

        # Perform the update operation
        result = db['doctor_details'].update_one({"username": self.username}, {"$set": updated_data})

        if result.modified_count > 0:
            print("Doctor data updated successfully.")
        else:
            print("No changes were made to the doctor data.")'''

    def insert_timing(self):
        # Gather timing data from entry fields
        new_timing = self.new_timing_entry.get().strip()
        if new_timing:
            # Update the database by appending new timing
            db = get_db_connection()
            result = db['doctor_details'].update_one({"username": self.username}, {"$push": {"timing": new_timing}})

            if result.modified_count > 0:
                print("New timing added successfully.")
            else:
                print("Failed to add new timing.")

    def update_timing(self, index):
        # Gather updated timing data from entry fields
        new_timing = self.update_timing_entry.get().strip()
        if new_timing:
            # Update the database by updating the timing at the specified index
            db = get_db_connection()
            result = db['doctor_details'].update_one({"username": self.username}, {"$set": {f"timing.{index - 1}": new_timing}})  # Use index - 1 for 0-based

            if result.modified_count > 0:
                print(f"Timing at index {index} updated successfully.")
            else:
                print("Failed to update timing.")

    def updateImg(self):
        print(f"Updating image for {self.username} in {'doctor_details'}...")
        update_image_from_external(self.username, 'doctor_details')
        self.display_image()

    def display_image(self):
        # Create a frame for the image
        image_frame = ctk.CTkFrame(self.master, fg_color="#2E2E2E")
        image_frame.place(relx=0.6, rely=0.15, relwidth=0.30, relheight=0.5)

        # Clear previous image label if it exists
        for widget in image_frame.winfo_children():
            widget.destroy()

        # Retrieve and display the image
        img = retrieve_image(self.username, 'doctor_details')  # Pass correct collection name
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
        if not self.doctor_data:
            error_label = ctk.CTkLabel(self.master, text="No doctor data found.", text_color="#FF0000", font=("Arial", 16))
            error_label.place(relx=0.35, rely=0.5)
            return

        print("Doctor Data:", self.doctor_data)

        # Create a scrollable frame
        scrollable_frame = CTkScrollableFrame(self.master)
        scrollable_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.85)

        # Frame for doctor's information
        info_frame = ctk.CTkFrame(scrollable_frame, fg_color="#2E2E2E")
        info_frame.pack(fill="both", expand=True)

        # Display doctor's information in entry fields
        labels = [
            "Name: ", "Date of Birth: ", "Gender: ", "Contact Number: ",
            "Email: ", "Permanent Address: ", "Medical License No: ",
            "Specialization: ", "Qualification: ", "Available Days: ", "Timing: "
        ]

        keys = [
            "name", "dob", "gender", "contact_no",
            "email", "address", "medical_license_no",
            "specialization", "qualification", "available_days", "timing"
        ]

        # Store entry references for updates
        self.name_entry = None
        self.dob_entry = None
        self.gender_entry = None
        self.contact_no_entry = None
        self.email_entry = None
        self.address_entry = None
        self.medical_license_no_entry = None
        self.specialization_entry = None
        self.qualification_entry = None
        self.available_days_entry = None
        self.timing_entry = None  # Add a reference for the timing entry
        self.new_timing_entry = None  # New timing entry field
        self.update_timing_entry = None  # Update timing entry field
        self.update_timing_index_entry = None  # Entry for timing index

        for idx, label in enumerate(labels):
            l = ctk.CTkLabel(info_frame, text=label, text_color="#E0E0E0", font=("Arial", 16))
            l.grid(row=idx, column=0, padx=10, pady=5, sticky="w")

            key = keys[idx]
            value = self.doctor_data.get(key, "N/A")

            # Debugging: Print out the key and its corresponding value
            print(f"Key: {key}, Value: {value}")

            if key != "gender":  # Gender will be displayed as a label, not an entry
                entry = ctk.CTkEntry(info_frame, placeholder_text=value)  # Use placeholder_text instead of text
                entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
                setattr(self, f"{key}_entry", entry)  # Store reference to entry
            else:
                gender_label = ctk.CTkLabel(info_frame, text=value, text_color="#FFFFFF", font=("Arial", 16))
                gender_label.grid(row=idx, column=1, padx=10, pady=5, sticky="w")

        # New Timing Entry
        l_new_timing = ctk.CTkLabel(info_frame, text="Add New Timing: ", text_color="#E0E0E0", font=("Arial", 16))
        l_new_timing.grid(row=len(labels), column=0, padx=10, pady=5, sticky="w")
        self.new_timing_entry = ctk.CTkEntry(info_frame, placeholder_text="e.g., 9 AM - 12 PM")
        self.new_timing_entry.grid(row=len(labels), column=1, padx=10, pady=5, sticky="w")

        insert_button = CTkButton(info_frame, text="Insert Timing", command=self.insert_timing)
        insert_button.grid(row=len(labels) + 1, columnspan=2, pady=10)

        # Update Timing Entry
        l_update_timing_index = ctk.CTkLabel(info_frame, text="Timing Index: ", text_color="#E0E0E0", font=("Arial", 16))
        l_update_timing_index.grid(row=len(labels) + 2, column=0, padx=10, pady=5, sticky="w")
        self.update_timing_index_entry = ctk.CTkEntry(info_frame, placeholder_text="Index (1-based)")
        self.update_timing_index_entry.grid(row=len(labels) + 2, column=1, padx=10, pady=5, sticky="w")

        l_update_timing = ctk.CTkLabel(info_frame, text="Update Timing: ", text_color="#E0E0E0", font=("Arial", 16))
        l_update_timing.grid(row=len(labels) + 3, column=0, padx=10, pady=5, sticky="w")
        self.update_timing_entry = ctk.CTkEntry(info_frame, placeholder_text="New Timing")
        self.update_timing_entry.grid(row=len(labels) + 3, column=1, padx=10, pady=5, sticky="w")

        update_button = CTkButton(info_frame, text="Update Timing", command=lambda: self.update_timing(int(self.update_timing_index_entry.get())))
        update_button.grid(row=len(labels) + 4, columnspan=2, pady=10)

        # Update Button
        update_button = CTkButton(self.master, text="Update", command=self.update_doctor_data)
        update_button.place(relx=0.55, rely=0.92)

        # Back Button
        back_button = CTkButton(self.master, text="Back", command=lambda: back(self))
        back_button.place(relx=0.75, rely=0.92)

        UpdateImage_button = CTkButton(self.master, text="Update Image", command=self.updateImg)
        UpdateImage_button.place(relx=0.67, rely=0.65)

if __name__ == "__main__":
    root = ctk.CTk()
    username = "admin21"  # Replace this with the actual username passed from the previous page
    # username = sys.argv[1]  # Replace this with the actual username passed from the previous page
    app = DoctorProfileApp(root, username)
    root.mainloop()


# import subprocess
# import tkinter as tk
# from PIL import ImageTk
# import customtkinter as ctk
# from customtkinter import CTkButton, CTkScrollableFrame
# from db_connection import get_db_connection
# from cryptography.fernet import Fernet
# import sys
# from fetch_image import retrieve_image
# from updateImage import update_image_from_external

# db = get_db_connection()

# def back(app_instance):
#     app_instance.master.destroy()  # Close the current window
#     # Launch the doctor signup page
#     subprocess.run(['python', 'doctor.py', app_instance.username])

# def encrypt_data(data, fernet_key):
#     """Encrypt the provided data using the Fernet cipher."""
#     cipher_suite = Fernet(fernet_key)
#     if not isinstance(data, bytes):
#         data = data.encode('utf-8')
#     encrypted_data = cipher_suite.encrypt(data)
#     return encrypted_data.decode('utf-8')

# def decrypt_data(encrypted_data, fernet_key):
#     """Decrypt the provided data using the Fernet cipher."""
#     cipher_suite = Fernet(fernet_key)
#     decrypted_data = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
#     return decrypted_data.decode('utf-8')

# class DoctorProfileApp:
#     def __init__(self, master, username):
#         self.master = master
#         self.master.title("Doctor Profile")
#         self.master.geometry("800x600+350+200")
#         self.username = username  # Store username for later use

#         # Load doctor's information
#         self.doctor_data = self.get_doctor_data(username)

#         # Create UI elements
#         self.create_ui()
#         self.display_image()

#     def get_doctor_data(self, username):
#         pipeline = [{"$match": {"username": username}}, {"$project": {"_id": 1}}]
#         doctor_result = list(db['doctor_details'].aggregate(pipeline))

#         if doctor_result:
#             doctor_id = doctor_result[0]['_id']
#             key_pipeline = [{"$match": {"_id": doctor_id}}, {"$project": {"key": 1}}]
#             key_result = list(db['keys'].aggregate(key_pipeline))

#             if key_result:
#                 encoded_key = key_result[0]['key']
#                 keybytes = encoded_key

#                 doctor_data = db['doctor_details'].find_one({"_id": doctor_id})

#                 if doctor_data:
#                     return {
#                         "name": decrypt_data(doctor_data['name'], keybytes),
#                         "dob": decrypt_data(doctor_data['dob'], keybytes),
#                         "gender": doctor_data['gender'],
#                         "contact_no": decrypt_data(doctor_data['ph_no'], keybytes),
#                         "email": decrypt_data(doctor_data['email'], keybytes),
#                         "address": decrypt_data(doctor_data['address'], keybytes),
#                         "medical_license_no": decrypt_data(doctor_data['medical_lisc_no'], keybytes),
#                         "specialization": doctor_data['specialization'],
#                         "qualification": doctor_data['qualification'],
#                         "available_days": doctor_data['available_days'],
#                         "timing": doctor_data.get('timing', []),  # Get the existing timing array
#                     }
#         return None

#     def update_doctor_data(self):
#         # Gather updated data from entry fields
#         pipeline = [{"$match": {"username": self.username}}, {"$project": {"_id": 1, "ph_no": 1}}]
#         doctor_result = list(db['doctor_details'].aggregate(pipeline))
        
#         if doctor_result:
#             doctor_id = doctor_result[0]['_id']
#             key_pipeline = [{"$match": {"_id": doctor_id}}, {"$project": {"key": 1}}]
#             key_result = list(db['keys'].aggregate(key_pipeline))

#             if key_result:
#                 encoded_key = key_result[0]['key']
#                 keybytes = encoded_key

#         # Gather current values
#         current_data = self.doctor_data.copy()
#         updated_data = {}

#         # Update each field if a new value is provided
#         if self.name_entry.get():
#             updated_data["name"] = encrypt_data(self.name_entry.get(), keybytes)
#         else:
#             updated_data["name"] = encrypt_data(current_data["name"], keybytes)

#         if self.dob_entry.get():
#             updated_data["dob"] = encrypt_data(self.dob_entry.get(), keybytes)
#         else:
#             updated_data["dob"] = encrypt_data(current_data["dob"], keybytes)

#         updated_data["gender"] = current_data['gender']

#         if self.contact_no_entry.get():
#             updated_data["ph_no"] = encrypt_data(self.contact_no_entry.get(), keybytes)
#         else:
#             updated_data["ph_no"] = encrypt_data(current_data["contact_no"], keybytes)

#         if self.email_entry.get():
#             updated_data["email"] = encrypt_data(self.email_entry.get(), keybytes)
#         else:
#             updated_data["email"] = encrypt_data(current_data["email"], keybytes)

#         if self.address_entry.get():
#             updated_data["address"] = encrypt_data(self.address_entry.get(), keybytes)
#         else:
#             updated_data["address"] = encrypt_data(current_data["address"], keybytes)

#         updated_data["medical_lisc_no"] = current_data['medical_license_no']

#         if self.specialization_entry.get():
#             updated_data["specialization"] = self.specialization_entry.get()
#         else:
#             updated_data["specialization"] = current_data["specialization"]

#         if self.qualification_entry.get():
#             updated_data["qualification"] = self.qualification_entry.get()
#         else:
#             updated_data["qualification"] = current_data["qualification"]

#         if self.available_days_entry.get():
#             updated_data["available_days"] = self.available_days_entry.get()
#         else:
#             updated_data["available_days"] = current_data["available_days"]

#         # Perform the update operation
#         result = db['doctor_details'].update_one({"username": self.username}, {"$set": updated_data})

#         if result.modified_count > 0:
#             print("Doctor data updated successfully.")
#         else:
#             print("No changes were made.")

#     def insert_timing(self):
#         # Add new timing to the doctor’s record
#         new_timing = self.new_timing_entry.get().strip()
#         if new_timing:
#             result = db['doctor_details'].update_one({"username": self.username}, {"$push": {"timing": new_timing}})
#             if result.modified_count > 0:
#                 print("New timing added successfully.")
#             else:
#                 print("Failed to add new timing.")

#     def update_timing(self, index):
#         # Update specific timing based on index
#         new_timing = self.update_timing_entry.get().strip()
#         if new_timing:
#             result = db['doctor_details'].update_one({"username": self.username}, {"$set": {f"timing.{index - 1}": new_timing}})
#             if result.modified_count > 0:
#                 print(f"Timing at index {index} updated successfully.")
#             else:
#                 print("Failed to update timing.")

#     def updateImg(self):
#         # Update doctor's image
#         print(f"Updating image for {self.username}...")
#         update_image_from_external(self.username, 'doctor_details')
#         self.display_image()

#     def display_image(self):
#         # Create a frame for displaying the image
#         image_frame = ctk.CTkFrame(self.master, fg_color="#2E2E2E")
#         image_frame.place(relx=0.6, rely=0.15, relwidth=0.30, relheight=0.5)

#         for widget in image_frame.winfo_children():
#             widget.destroy()

#         img = retrieve_image(self.username, 'doctor_details')
#         if img:
#             img = img.resize((350, 350))
#             img_tk = ImageTk.PhotoImage(img)
#             img_label = ctk.CTkLabel(image_frame, image=img_tk)
#             img_label.image = img_tk  # Keep a reference to avoid garbage collection
#             img_label.pack(pady=10)
#         else:
#             no_image_label = ctk.CTkLabel(image_frame, text="No Image Found", text_color="#FF0000", font=("Arial", 16))
#             no_image_label.pack(pady=10)

#     def create_ui(self):
#         if not self.doctor_data:
#             error_label = ctk.CTkLabel(self.master, text="No doctor data found.", text_color="#FF0000", font=("Arial", 16))
#             error_label.place(relx=0.35, rely=0.5)
#             return

#         print("Doctor Data:", self.doctor_data)

#         scrollable_frame = CTkScrollableFrame(self.master)
#         scrollable_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.85)

#         info_frame = ctk.CTkFrame(scrollable_frame, fg_color="#2E2E2E")
#         info_frame.pack(fill="both", expand=True)

#         labels = [
#             "Name: ", "Date of Birth: ", "Gender: ", "Contact Number: ",
#             "Email: ", "Permanent Address: ", "Medical License No: ",
#             "Specialization: ", "Qualification: ", "Available Days: ", "Timing: "
#         ]

#         keys = [
#             "name", "dob", "gender", "contact_no",
#             "email", "address", "medical_license_no",
#             "specialization", "qualification", "available_days", "timing"
#         ]

#         self.name_entry = None
#         self.dob_entry = None
#         self.gender_entry = None
#         self.contact_no_entry = None
#         self.email_entry = None
#         self.address_entry = None
#         self.medical_license_no_entry = None
#         self.specialization_entry = None
#         self.qualification_entry = None
#         self.available_days_entry = None
#         self.timing_entry = None

#         # Display Doctor Info Fields
#         for i, label in enumerate(labels):
#             ctk.CTkLabel(info_frame, text=label, anchor="w").grid(row=i, column=0, padx=10, pady=5, sticky="w")
#             entry_var = tk.StringVar(value=self.doctor_data[keys[i]])
#             if keys[i] == "timing":
#                 timings = "\n".join(self.doctor_data['timing'])
#                 timing_label = ctk.CTkLabel(info_frame, text=timings)
#                 timing_label.grid(row=i, column=1, padx=10, pady=5, sticky="w")
#             else:
#                 entry = ctk.CTkEntry(info_frame, textvariable=entry_var)
#                 entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")

#             if keys[i] == "name":
#                 self.name_entry = entry
#             elif keys[i] == "dob":
#                 self.dob_entry = entry
#             elif keys[i] == "gender":
#                 self.gender_entry = entry
#             elif keys[i] == "contact_no":
#                 self.contact_no_entry = entry
#             elif keys[i] == "email":
#                 self.email_entry = entry
#             elif keys[i] == "address":
#                 self.address_entry = entry
#             elif keys[i] == "medical_license_no":
#                 self.medical_license_no_entry = entry
#             elif keys[i] == "specialization":
#                 self.specialization_entry = entry
#             elif keys[i] == "qualification":
#                 self.qualification_entry = entry
#             elif keys[i] == "available_days":
#                 self.available_days_entry = entry

#         # New Timing Entry
#         self.new_timing_entry = ctk.CTkEntry(info_frame, placeholder_text="New Timing (e.g., 9 AM - 12 PM)")
#         self.new_timing_entry.grid(row=len(labels) + 1, column=1, padx=10, pady=5, sticky="w")

#         insert_timing_button = CTkButton(info_frame, text="Add Timing", command=self.insert_timing)
#         insert_timing_button.grid(row=len(labels) + 2, columnspan=2, pady=10)

#         # Update Timing Entry
#         self.update_timing_index_entry = ctk.CTkEntry(info_frame, placeholder_text="Timing Index (1-based)")
#         self.update_timing_index_entry.grid(row=len(labels) + 3, column=0, padx=10, pady=5, sticky="w")

#         self.update_timing_entry = ctk.CTkEntry(info_frame, placeholder_text="New Timing (e.g., 2 PM - 4 PM)")
#         self.update_timing_entry.grid(row=len(labels) + 3, column=1, padx=10, pady=5, sticky="w")

#         update_timing_button = CTkButton(info_frame, text="Update Timing", 
#                                          command=lambda: self.update_timing(int(self.update_timing_index_entry.get())))
#         update_timing_button.grid(row=len(labels) + 4, columnspan=2, pady=10)

#         # Button to Update Doctor Information
#         update_button = CTkButton(info_frame, text="Update Doctor Info", command=self.update_doctor_data)
#         update_button.grid(row=len(labels) + 5, columnspan=2, pady=20)

#         # Back Button to go back to the previous page
#         back_button = CTkButton(self.master, text="Back", command=lambda: back(self))
#         back_button.place(relx=0.05, rely=0.93, relwidth=0.15, relheight=0.05)


# if __name__ == "__main__":
#     # username = sys.argv[1]  # Get the passed username
#     username = "admin1"  # Get the passed username
#     root = tk.Tk()
#     app = DoctorProfileApp(root, username)
#     root.mainloop()
