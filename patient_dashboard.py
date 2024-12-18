import subprocess
import sys
import customtkinter as ctk
from customtkinter import CTkButton
from PIL import ImageTk
from db_connection import get_db_connection
from fetch_image import retrieve_image
from cryptography.fernet import Fernet


class PatientDashboardApp:
    def __init__(self, master, username):
        self.master = master
        self.master.title("Patient Dashboard")
        self.master.geometry("1000x600+200+100")

        # Colors and style
        ctk.set_appearance_mode("dark")
        self.bg_color = "#333333"
        self.button_color = "#4CAF50"
        self.label_color = "#E0E0E0"

        # Connect to database
        self.db = get_db_connection()
        self.patient_collection = self.db['patient_details']

        # Username to search in database
        self.username = username
        self.patient_data = self.fetch_patient_data()
        # print(self.patient_data)

        # Frame for Buttons on the left side
        self.sidebar_frame = ctk.CTkFrame(
            self.master, width=300, height=600, corner_radius=10, fg_color=self.bg_color)
        self.sidebar_frame.place(relx=0, rely=0, relheight=1, relwidth=0.3)

        # Frame for content display on the right side
        self.content_frame = ctk.CTkFrame(
            self.master, fg_color="#2E2E2E", corner_radius=10)
        self.content_frame.place(relx=0.3, rely=0, relheight=1, relwidth=0.8)

        # Sidebar Title
        self.title_label = ctk.CTkLabel(
            self.sidebar_frame, text="Patient Dashboard", text_color=self.label_color, font=("Arial", 20, "bold"))
        self.title_label.pack(pady=20)

        self.display_image()

        # Get the fernet keys
        fernet_key = self.get_fernetKey()

        # Buttons for different sections
        self.create_buttons()

        # Default content (Profile displayed on load)
        self.show_profile(fernet_key)

    def logout(self):
        self.master.destroy()  # Close the current window
        # Launch the previous page (e.g., patient management page)
        subprocess.run(['python', 'login.py'])
        
    def display_image(self):
        # Create a frame for the image
        image_frame = ctk.CTkFrame(self.master, fg_color="#2E2E2E")
        image_frame.place(relx=0.7, rely=0.15, relwidth=0.25, relheight=0.5)

        # Retrieve and display the image
        img = retrieve_image(self.username, 'patient_details')  # Pass correct collection name
        if img:
            img = img.resize((350, 350))  # Resize image for the display
            img_tk = ImageTk.PhotoImage(img)
            img_label = ctk.CTkLabel(image_frame, image=img_tk)
            img_label.image = img_tk  # Keep a reference to avoid garbage collection
            img_label.pack(pady=10)

    def decrypt_data(self, encrypted_data, fernet_key):
        cipher_suite = Fernet(fernet_key)
        decrypted_data = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
        print(decrypted_data.decode('utf-8'))
        return decrypted_data.decode('utf-8')

    def get_fernetKey(self):
        # Find the patient's ID using their username
        pipeline = [{"$match": {"username": self.username}},
                    {"$project": {"_id": 1, "ph_no": 1}}]
        patient_result = list(self.db['patient_details'].aggregate(pipeline))
        print("phone - "+patient_result[0]['ph_no'])
        print(patient_result)
        if patient_result:
            patient_id = patient_result[0]['_id']  # Extract the patient ID

            # Retrieve the encryption key using the patient's ID
            key_pipeline = [{"$match": {"_id": patient_id}},
                            {"$project": {"key": 1}}]
            key_result = list(self.db['keys'].aggregate(key_pipeline))

            if key_result:
                encoded_key = key_result[0]['key']
                keybytes = encoded_key

        print(keybytes)
        return keybytes

    def fetch_patient_data(self):
        # Fetch the patient details from the database based on the username
        result_pipeline = [{"$match": {"username": self.username}},
                          {"$project": {"name": 1, "dob": 1, "gender": 1,
                                         "ph_no": 1, "email": 1, "address": 1, "blood_G": 1, "allergy": 1, "chro_disease": 1, "prev_surgeries": 1}}]
        patient = list(self.patient_collection.aggregate(result_pipeline))
        return patient

    def create_buttons(self):
        # Creating sidebar buttons
        buttons = [
            ("Update Profile", self.update_profile),
            ("View Doctors", self.view_doctors),
            ("Appointment Management", self.show_appointments),
            ("Treatment Records", self.show_treatment_records),
            # ("Messages & Notifications", self.show_messages),
            ("Billing & Payments", self.show_billing),
            ("Logout", self.logout)
        ]

        for btn_text, btn_command in buttons:
            button = ctk.CTkButton(self.sidebar_frame, text=btn_text, command=btn_command,
                                   fg_color=self.button_color, font=("Arial", 16, "bold"))
            button.pack(pady=15, padx=20, fill="x")

    def clear_content(self):
        # Clear current content from the right content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_profile(self, fernet_key):
        self.clear_content()
        
        profile_heading = ctk.CTkLabel(
            self.content_frame, text="Patient Profile", text_color=self.label_color, font=("Arial", 20, "bold"))
        profile_heading.grid(row=0, column=3, columnspan=2,
                             padx=10, pady=20, sticky="w")

        # Check if patient data exists
        if not self.patient_data:
            error_label = ctk.CTkLabel(
                self.content_frame, text="No patient data found.", text_color="red", font=("Arial", 16))
            error_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
            return
        
        # Profile Data to Display
        print("phone no - "+self.patient_data[0]['ph_no'])
        name = self.decrypt_data(self.patient_data[0]['name'], fernet_key)
        profile_data = {
            "Name": name,
            "DOB": self.decrypt_data(self.patient_data[0]['dob'], fernet_key),
            "Gender": self.patient_data[0]['gender'],
            "Phone Number": self.decrypt_data(self.patient_data[0]['ph_no'], fernet_key),  
            "Email": self.decrypt_data(self.patient_data[0]['email'], fernet_key),
            "Address": self.decrypt_data(self.patient_data[0]['address'], fernet_key),
            "Blood Group": self.decrypt_data(self.patient_data[0]['blood_G'], fernet_key),  
            "Allergies": self.decrypt_data(self.patient_data[0]['allergy'], fernet_key),  
            "Chronic Disease": self.decrypt_data(self.patient_data[0]['chro_disease'], fernet_key),  
            "Previous Surgeries": self.decrypt_data(self.patient_data[0]['prev_surgeries'], fernet_key)
        }

        # Display Profile Data
        row_idx = 1
        for label, value in profile_data.items():
            label_widget = ctk.CTkLabel(
                self.content_frame, text=f"{label}:", text_color=self.label_color, font=("Arial", 16))
            value_widget = ctk.CTkLabel(
                self.content_frame, text=value, text_color=self.label_color, font=("Arial", 16))

            # Placing the labels and values using grid for precise positioning
            label_widget.grid(row=row_idx, column=0,
                              padx=10, pady=5, sticky="w")
            value_widget.grid(row=row_idx, column=1,
                              padx=10, pady=5, sticky="w")
            row_idx += 1

    def update_profile(self):
        self.master.destroy()  # Close the current window
        # Launch the doctor signup page
        subprocess.run(['python', 'manage_patient.py', self.username])

    def view_doctors(self):
        self.master.destroy()  # Close the current window
        # Launch the doctor view page with username and name
        name = self.decrypt_data(self.patient_data[0]['name'], self.get_fernetKey())
        subprocess.run(['python', 'view_doctorsPatient.py', self.username, name])
        
    def show_appointments(self):
        self.master.destroy()
        subprocess.run(['python','Patient_appointment_management.py',self.username])

    def show_treatment_records(self):
        self.master.destroy()
        subprocess.run(['python','treatment_recordsPatient.py',self.username])

    def show_messages(self):
        self.clear_content()
        message_heading = ctk.CTkLabel(
            self.content_frame, text="Messages & Notifications", text_color=self.label_color, font=("Arial", 20, "bold"))
        message_heading.pack(pady=20)

        # Sample messages
        message_data = [
            {"From": "Dr. Smith", "Message": "Your appointment is confirmed."},
            {"From": "Reception", "Message": "Your lab results are ready."},
        ]

        for message in message_data:
            message_label = ctk.CTkLabel(
                self.content_frame, text=f"{message['From']}: {message['Message']}",
                text_color=self.label_color, font=("Arial", 16))
            message_label.pack(pady=5)

    def show_billing(self):
        self.master.destroy()
        subprocess.run(['python','Patient_billing_payment.py',self.username])
        


if __name__ == "__main__":
    root = ctk.CTk()
    # username = "sanmarg123"  # Replace with actual username from login
    username = sys.argv[1]  # Replace with actual username from login
    app = PatientDashboardApp(root, username)
    root.mainloop()
