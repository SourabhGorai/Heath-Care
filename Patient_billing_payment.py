import sys
import customtkinter as ctk
from pymongo import MongoClient
from cryptography.fernet import Fernet
from tkinter import Scrollbar, messagebox
from db_connection import get_db_connection
import subprocess  # To open another Python script

db = get_db_connection()

# Setup Fernet encryption key function
def get_fernet_key(doc_id):
    key_pipeline = [{"$match": {"_id": doc_id}}, {"$project": {"key": 1}}]
    key_result = list(db['keys'].aggregate(key_pipeline))

    if key_result:
        encoded_key = key_result[0]['key']
        keybytes = encoded_key
        return keybytes
    return None

def decrypt_data(encrypted_data, fernet_key):
    """Decrypt the provided data using the Fernet cipher."""
    cipher_suite = Fernet(fernet_key)
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
    return decrypted_data.decode('utf-8')

# CustomTkinter Scrollable Frame
class AppointmentManager(ctk.CTk):
    def __init__(self, username):
        super().__init__()
        self.title("Appointment Management")
        self.geometry("1050x600+150+90")

        # Main frame that contains all widgets
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(main_frame, width=900, height=400)
        scrollable_frame.pack(fill="both", expand=True, pady=10)

        # Add a title label
        ctk.CTkLabel(main_frame, text="Patient Appointments", font=("Arial", 20, "bold")).pack(pady=10)

        # Fetch appointments for the logged-in patient
        self.fetch_appointments(username, scrollable_frame)

        # Frame for the back button
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=10)

        # Add a back button
        back_button = ctk.CTkButton(button_frame, text="Back", command=self.open_patient_dashboard)
        back_button.pack(pady=10)

    def fetch_appointments(self, patient_username, frame):
        # Aggregation to match patient username
        pipeline = [
            {"$match": {"patient_username": patient_username}}
        ]
        appointments = db['appointment_management'].aggregate(pipeline)

        # Table Header Styling
        headers = ["Doctor", "Date", "Time", "Status", "Illness", "Billing"]
        header_bg = "#4a4a4a"  # Dark background for header
        header_fg = "#ffffff"  # White text for header
        for idx, header in enumerate(headers):
            ctk.CTkLabel(master=frame, text=header, width=150, font=("Arial", 12, "bold"),
                        fg_color=header_bg, text_color=header_fg, corner_radius=5).grid(row=0, column=idx, padx=5, pady=5)

        # Check if any appointments are found
        i = 1  # For row index in the table
        for appointment in appointments:
            patient_name = appointment['patient_name']
            doctor_usrn = appointment['doctor_username']
            date = appointment['date']
            time = appointment['appointment_time']
            done_status = appointment['done']
            illness = appointment['illness']

            # Fetch doctor details
            doctor_pipeline = [{"$match": {"username": doctor_usrn}}, {"$project": {"_id": 1, "name": 1}}]
            doctor_results = list(db['doctor_details'].aggregate(doctor_pipeline))

            if doctor_results:
                doc_id = doctor_results[0]['_id']
                doc_name = doctor_results[0]['name']

                # Fetch Fernet key
                fernet_key = get_fernet_key(doc_id)

                # Decrypt doctor's name
                doctor_name = decrypt_data(doc_name, fernet_key)

                # Determine appointment status
                status = "Done" if done_status else "Pending"

                # Handle billing status
                billing_status = appointment.get('billing_status', 'Pending')  # Default to 'Pending' if not found

                # Row coloring for alternating rows
                row_bg = "#e6f2ff" if i % 2 == 0 else "#f9f9f9"
                text_color = "#000000"  # Default text color for normal data
                status_color = "#007bff" if status == "Done" else "#ff0000"  # Blue for "Done", Red for "Pending"
                illness_color = "#007bff" if illness != "N/A" else "#ff0000"  # Blue for "Done", Red for "Pending"

                # Add labels to the frame (decorate them)
                ctk.CTkLabel(master=frame, text=doctor_name, width=150, fg_color=row_bg,
                            text_color=text_color, corner_radius=3).grid(row=i, column=0, padx=5, pady=5)
                ctk.CTkLabel(master=frame, text=date, width=150, fg_color=row_bg,
                            text_color=text_color, corner_radius=3).grid(row=i, column=1, padx=5, pady=5)
                ctk.CTkLabel(master=frame, text=time, width=150, fg_color=row_bg,
                            text_color=text_color, corner_radius=3).grid(row=i, column=2, padx=5, pady=5)
                ctk.CTkLabel(master=frame, text=status, width=150, fg_color=row_bg,
                            text_color=status_color, corner_radius=3).grid(row=i, column=3, padx=5, pady=5)
                ctk.CTkLabel(master=frame, text=illness, width=150, fg_color=row_bg,
                            text_color=illness_color, corner_radius=3).grid(row=i, column=4, padx=5, pady=5)

                # Handle billing status
                if billing_status == 'Paid':
                    billing_label = ctk.CTkLabel(master=frame, text=billing_status, width=150,
                                                fg_color=row_bg, text_color=text_color, corner_radius=3)
                else:  # For pending billing, add a button to pay
                    billing_label = ctk.CTkButton(master=frame, text="Pay", command=lambda: self.pay_billing(appointment['_id']),
                                                    fg_color=row_bg, text_color=text_color, corner_radius=3)

                billing_label.grid(row=i, column=5, padx=5, pady=5)

                # Increment row index for next appointment
                i += 1


    def pay_for_appointment(self, appointment_id):
        """Function to handle payment logic (you can edit this to implement payment logic)."""
        # Implement your payment logic here
        messagebox.showinfo("Payment", f"Payment functionality for appointment {appointment_id} will be implemented here.")
        # You could open a payment window or redirect the user accordingly.

    def open_patient_dashboard(self):
        """Opens the patient dashboard when the back button is clicked."""
        self.destroy()  # Close the current window
        subprocess.run(["python", "patient_dashboard.py", username])  # Open patient_dashboard.py


# Run the app
if __name__ == "__main__":
    # username = "sanmarg123"  # Replace with actual patient username
    username = sys.argv[1]  # Replace with actual patient username
    app = AppointmentManager(username)
    app.mainloop()
