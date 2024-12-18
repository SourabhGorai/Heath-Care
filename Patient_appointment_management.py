import sys
import customtkinter as ctk
from pymongo import MongoClient
from datetime import datetime
from tkinter import messagebox
import subprocess
from db_connection import get_db_connection

db = get_db_connection()

# CustomTkinter App
class AppointmentManagementApp(ctk.CTk):
    def __init__(self, username):
        super().__init__()
        self.title("Today's Appointments")
        self.geometry("1050x600+160+150")

        # Create scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(self, width=1050, height=430)
        scrollable_frame.pack(padx=20, pady=20)

        # Add a title label
        ctk.CTkLabel(master=self, text="Today's Appointments", font=("Arial", 20, "bold")).pack(pady=10)

        # Fetch today's appointments
        self.fetch_appointments(username, scrollable_frame)

        # Add a Back button
        back_button = ctk.CTkButton(master=self, text="Back to Dashboard", command=self.go_to_dashboard)
        back_button.pack(pady=10)

    def fetch_appointments(self, patient_username, frame):
        # Get the current date in YYYY-MM-DD format
        today = datetime.today().strftime('%Y-%m-%d')

        # Query to match patient username and today's date
        pipeline = [
            {"$match": {"patient_username": patient_username, "date": today}}
        ]
        appointments = list(db['appointment_management'].aggregate(pipeline))

        if not appointments:
            # If no appointments found, show a message
            ctk.CTkLabel(master=frame, text="You don't have any appointments today.",
                         font=("Arial", 16, "bold"), text_color="#ff0000").pack(pady=20)
            return

        # Table Header Styling
        headers = ["Doctor", "Date", "Time", "Status", "Doctor Info", "Cancel Appointment"]
        header_bg = "#4a4a4a"  # Dark background for header
        header_fg = "#ffffff"  # White text for header
        for idx, header in enumerate(headers):
            ctk.CTkLabel(master=frame, text=header, width=150, font=("Arial", 12, "bold"),
                         fg_color=header_bg, text_color=header_fg, corner_radius=5).grid(row=0, column=idx, padx=5, pady=5)

        # Check if any appointments are found
        i = 1  # For row index in the table
        for appointment in appointments:

            doctor_usrn = appointment['doctor_username']
            date = appointment['date']
            time = appointment['appointment_time']
            done_status = appointment['done']
            
            # Determine appointment status
            status = "Done" if done_status else "Pending"

            # Row coloring for alternating rows
            row_bg = "#e6f2ff" if i % 2 == 0 else "#f9f9f9"
            text_color = "#000000"  # Default text color for normal data
            status_color = "#007bff" if status == "Done" else "#ff0000"  # Blue for "Done", Red for "Pending"

            # Add labels to the frame (decorate them)
            ctk.CTkLabel(master=frame, text=doctor_usrn, width=150, fg_color=row_bg,
                         text_color=text_color, corner_radius=3).grid(row=i, column=0, padx=5, pady=5)
            ctk.CTkLabel(master=frame, text=date, width=150, fg_color=row_bg,
                         text_color=text_color, corner_radius=3).grid(row=i, column=1, padx=5, pady=5)
            ctk.CTkLabel(master=frame, text=time, width=150, fg_color=row_bg,
                         text_color=text_color, corner_radius=3).grid(row=i, column=2, padx=5, pady=5)
            ctk.CTkLabel(master=frame, text=status, width=150, fg_color=row_bg,
                         text_color=status_color, corner_radius=3).grid(row=i, column=3, padx=5, pady=5)

            # Add "Doctor Info" button
            info_button = ctk.CTkButton(master=frame, text="View Doc. Info", command=lambda d_usrn=doctor_usrn: self.view_doctor_info(d_usrn))
            info_button.grid(row=i, column=4, padx=5, pady=5)

            # Add "Cancel Appointment" button
            cancel_button = ctk.CTkButton(master=frame, text="Cancel Appointment", command=lambda a_id=appointment['_id']: self.cancel_appointment(a_id))
            cancel_button.grid(row=i, column=5, padx=5, pady=5)

            # Increment row index for next appointment
            i += 1

    def view_doctor_info(self, doctor_username):
        """Function to view doctor information (you can edit this to show details)."""
        self.destroy()
        subprocess.run(['python', 'view_doctorsInfoPatient.py', doctor_username])

    def cancel_appointment(self, appointment_id):
        """Function to cancel the appointment."""
        result = messagebox.askyesno("Cancel Appointment", "Are you sure you want to cancel this appointment?")
        if result:
            try:
                db['appointment_management'].delete_one({"_id": appointment_id})
                messagebox.showinfo("Canceled", "Your appointment has been canceled.")
            except Exception as e:
                messagebox.showinfo("Not Canceled", "Your appointment has not been canceled.")
                print(e)
        else:
            messagebox.showinfo("Canceled", "Appointment cancellation aborted.")

    def go_to_dashboard(self):
        """Function to go back to the patient dashboard."""
        self.destroy()
        subprocess.run(['python', 'patient_dashboard.py', username])

# Run the app
if __name__ == "__main__":
    # username = "sanmarg123"  # Replace with actual patient username
    username = sys.argv[1]  # Replace with actual patient username
    app = AppointmentManagementApp(username)
    app.mainloop()
