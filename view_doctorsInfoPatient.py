
import sys
import subprocess  # Import subprocess to run another Python script
from pymongo import MongoClient
from db_connection import get_db_connection
import customtkinter as ctk
from cryptography.fernet import Fernet
from fetch_image import retrieve_image  # Import the function to fetch image
from PIL import ImageTk


def decrypt_data(encrypted_data, fernet_key):
    """Decrypt the provided data using the Fernet cipher."""
    cipher_suite = Fernet(fernet_key)
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
    return decrypted_data.decode('utf-8')

# Function to get doctor details by username
def fetch_doctor_details(username):
    # Get database connection
    db = get_db_connection()  # Adjust if your function requires parameters
    doctor_collection = db['doctor_details']

    # Search for doctor by username
    doctor_details = list(doctor_collection.aggregate(
        [{"$match": {"username": username}}, {"$limit": 1}]))


    if not doctor_details:
        print(f"No doctor found with username: {username}")
        return None

    # Ensure doctor details have required fields
    doctor_document = doctor_details[0]
    doctor_id = doctor_document.get('_id')

    if doctor_id is None:
        print("Doctor ID not found.")
        return None

    # Retrieve the encryption key using the doctor's ID
    key_pipeline = [{"$match": {"_id": doctor_id}}, {"$project": {"key": 1}}]
    key_result = list(db['keys'].aggregate(key_pipeline))

    if key_result:
        encoded_key = key_result[0]['key']
        keybytes = encoded_key

        # Decrypted details
        doctor_info = {
            "name": decrypt_data(doctor_document['name'], keybytes),
            "gender": doctor_document.get('gender', 'N/A'),
            "specialization": doctor_document['specialization'],
            "experience": doctor_document['experience'],
            "qualification": doctor_document['qualification'],
            # Correctly handle array of timings
            "timing": doctor_document.get('timing', []),
            "available_days": doctor_document.get('available_days', [])  # Fetch available days
        }

        # Fetch the image if available
        image_id = doctor_document.get('profile_picture')
        if image_id:
            doctor_info['image'] = retrieve_image(
                username, 'doctor_details')  # Pass correct collection name
        else:
            doctor_info['image'] = None  # No image found

        return doctor_info

    return None

# Function to display doctor details in a Tkinter window
def display_doctor_details(doctor):
    app = ctk.CTk()
    app.geometry("800x500+350+250")  # Adjust window size as needed
    app.title(f"Profile of Dr. {doctor['name']}")

    # Create frames for layout
    left_frame = ctk.CTkFrame(app)
    left_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    right_frame = ctk.CTkFrame(app)
    right_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    # Font and color customization
    label_font_bold = ctk.CTkFont(size=16, weight="bold")  # Bold font
    label_font_normal = ctk.CTkFont(size=14)
    label_color = "#00008B"  # Dark blue color

    # Create labels for each piece of doctor information and align them to the left
    ctk.CTkLabel(left_frame, text="                        Doctor Information",
                 font=label_font_bold, text_color="#00FF00", anchor='w').pack(pady=10, anchor='w')
    ctk.CTkLabel(left_frame, text="    Name:  " +
                 doctor['name'], font=label_font_bold, text_color="#FF8000", anchor='w').pack(pady=10, anchor='w')
    ctk.CTkLabel(left_frame, text="    Gender:  " +
                 doctor['gender'], font=label_font_bold, text_color="#FF8000", anchor='w').pack(pady=5, anchor='w')
    ctk.CTkLabel(left_frame, text="    Specialization:  " +
                 doctor['specialization'], font=label_font_bold, text_color="#FF8000", anchor='w').pack(pady=10, anchor='w')
    ctk.CTkLabel(left_frame, text="    Experience:  " +
                 doctor['experience'] + " Yrs", font=label_font_bold, text_color="#FF8000", anchor='w').pack(pady=5, anchor='w')
    ctk.CTkLabel(left_frame, text="    Qualification:  " +
                 doctor['qualification'], font=label_font_bold, text_color="#FF8000", anchor='w').pack(pady=5, anchor='w')

    # Display timings
    if doctor['timing']:
        timing_text = "    Timings: " + ', '.join(doctor['timing'])
        ctk.CTkLabel(left_frame, text=timing_text, font=label_font_bold,
                     text_color="#FF8000", anchor='w').pack(pady=5, anchor='w')
    else:
        ctk.CTkLabel(left_frame, text="    Timings: Not Available", font=label_font_bold,
                     text_color="#FF8000", anchor='w').pack(pady=5, anchor='w')

    # Display available days
    if doctor['available_days']:
        available_days_text = "    Available Days: " + ', '.join(doctor['available_days'])
        ctk.CTkLabel(left_frame, text=available_days_text, font=label_font_bold,
                     text_color="#FF8000", anchor='w').pack(pady=5, anchor='w')
    else:
        ctk.CTkLabel(left_frame, text="    Available Days: Not Available", font=label_font_bold,
                     text_color="#FF8000", anchor='w').pack(pady=5, anchor='w')

    # If an image is available, display it in the right frame
    if doctor['image']:
        # Resize image for the display
        img = doctor['image'].resize((350, 350))
        img_tk = ImageTk.PhotoImage(img)
        img_label = ctk.CTkLabel(right_frame, image=img_tk)
        img_label.image = img_tk  # Keep a reference to avoid garbage collection
        img_label.pack(pady=50)

    # Back Button in the left frame
    back_button = ctk.CTkButton(left_frame, text="Back", command=lambda: [app.destroy()])  # Destroy the app and run the new script
    back_button.pack(pady=(50, 20))  # Adjust padding to move the button lower

    app.mainloop()


# Main execution
if __name__ == "__main__":
    username = sys.argv[1]  # You can change this to fetch dynamically later
    # username = "sourabh_gorai"  # You can change this to fetch dynamically later
    doctor_details = fetch_doctor_details(username)

    if doctor_details:
        display_doctor_details(doctor_details)
    else:
        print(f"No doctor found with username: {username}")
