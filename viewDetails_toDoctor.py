# import sys
# from pymongo import MongoClient
# from db_connection import get_db_connection
# import customtkinter as ctk
# from cryptography.fernet import Fernet

# def decrypt_data(encrypted_data, fernet_key):
#     """Decrypt the provided data using the Fernet cipher."""
#     cipher_suite = Fernet(fernet_key)
#     decrypted_data = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
#     print(decrypted_data.decode('utf-8'))
#     return decrypted_data.decode('utf-8')

# # Function to get patient details by username
# def fetch_patient_details(username):
#     # Get database connection
#     db = get_db_connection()  # Adjust if your function requires parameters
#     patient_collection = db['patient_details']
    
#     # Search for patient by username
#     patient_details = patient_collection.find_one({"username": username})
#     # patient_details = list(patient_collection.aggregate([
#     # {"$match": {"username": username}},
#     # {"$limit": 1}]))

#     if patient_details is None:
#         print(f"No patient found with username: {username}")
#         return None
    
#     # Ensure patient details have required fields
#     patient_id = patient_details.get('_id')
#     if patient_id is None:
#         print("Patient ID not found.")
#         return None

#     # Retrieve the encryption key using the patient's ID
#     key_pipeline = [{"$match": {"_id": patient_id}}, {"$project": {"key": 1}}]
#     key_result = list(db['keys'].aggregate(key_pipeline))

#     if key_result:
#         encoded_key = key_result[0]['key']
#         keybytes = encoded_key
#         print(keybytes)
        
#         return {
#             "name": decrypt_data(patient_details['name'], keybytes),
#             "dob": decrypt_data(patient_details['dob'], keybytes),
#             "contact_no": decrypt_data(patient_details['ph_no'], keybytes),
#             "gender": patient_details.get('gender', 'N/A'),  # Default to 'N/A' if not found
#             "blood_group": decrypt_data(patient_details['blood_G'],keybytes),  # Assuming you have this field
#             "allergy": decrypt_data(patient_details['allergy'],keybytes),  # Assuming you have this field
#             "chronic_disease": decrypt_data(patient_details['chro_disease'],keybytes),  # Assuming you have this field
#             "previous_surgeries": decrypt_data(patient_details['prev_surgeries'],keybytes),  # Assuming you have this field
#         }
    
#     return None

# # Function to display patient details in a Tkinter window
# def display_patient_details(patient):
#     app = ctk.CTk()
#     app.geometry("400x500+650+250")
#     app.title(f"Profile of {patient['name']}")

#     # Font and color customization
#     label_font_bold = ctk.CTkFont(size=16, weight="bold")  # Bold font
#     label_font_normal = ctk.CTkFont(size=14)
#     label_color = "#00008B"  # Dark blue color

#     # Create labels for each piece of patient information
#     ctk.CTkLabel(app, text="Patient Information", font=label_font_bold, text_color="#00FF00").pack(pady=10)
#     ctk.CTkLabel(app, text="Name: " + patient['name'], font=label_font_bold, text_color="#FF8000").pack(pady=10)
#     ctk.CTkLabel(app, text="Date of Birth: " + patient['dob'], font=label_font_bold, text_color="#FF8000").pack(pady=5)
#     ctk.CTkLabel(app, text="Gender: " + patient['gender'], font=label_font_bold, text_color="#FF8000").pack(pady=5)
#     ctk.CTkLabel(app, text="Blood Group: " + patient['blood_group'], font=label_font_bold, text_color="#FF8000").pack(pady=10)
#     ctk.CTkLabel(app, text="Allergy: " + patient['allergy'], font=label_font_bold, text_color="#FF8000").pack(pady=5)
#     ctk.CTkLabel(app, text="Chronic Disease: " + patient['chronic_disease'], font=label_font_bold, text_color="#FF8000").pack(pady=5)
#     ctk.CTkLabel(app, text="Previous Surgeries: " + patient['previous_surgeries'], font=label_font_bold, text_color="#FF8000").pack(pady=5)
#     ctk.CTkLabel(app, text="Contact Number: " + patient['contact_no'], font=label_font_bold, text_color="#FF8000").pack(pady=10)

#     app.mainloop()

# # Main execution
# if __name__ == "__main__":
#     username = "patientA123"  # You can change this to fetch dynamically later
#     # username = sys.argv[1]  # You can change this to fetch dynamically later
#     patient_details = fetch_patient_details(username)
    
#     if patient_details:
#         display_patient_details(patient_details)
#     else:
#         print(f"No patient found with username: {username}")


import sys
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

# Function to get patient details by username
def fetch_patient_details(username):
    # Get database connection
    db = get_db_connection()  # Adjust if your function requires parameters
    patient_collection = db['patient_details']
    
    # Search for patient by username
    patient_details = list(patient_collection.aggregate([{"$match": {"username": username}},{"$limit": 1}]))
    
    if not patient_details:
        print(f"No patient found with username: {username}")
        return None
    
    # Ensure patient details have required fields
    patient_document = patient_details[0]
    patient_id = patient_document.get('_id')

    if patient_id is None:
        print("Patient ID not found.")
        return None

    # Retrieve the encryption key using the patient's ID
    key_pipeline = [{"$match": {"_id": patient_id}}, {"$project": {"key": 1}}]
    key_result = list(db['keys'].aggregate(key_pipeline))

    if key_result:
        encoded_key = key_result[0]['key']
        keybytes = encoded_key
        
        # Decrypted details
        patient_info = {
            "name": decrypt_data(patient_document['name'], keybytes),
            "dob": decrypt_data(patient_document['dob'], keybytes),
            "contact_no": decrypt_data(patient_document['ph_no'], keybytes),
            "gender": patient_document.get('gender', 'N/A'),
            "blood_group": decrypt_data(patient_document['blood_G'], keybytes),
            "allergy": decrypt_data(patient_document['allergy'], keybytes),
            "chronic_disease": decrypt_data(patient_document['chro_disease'], keybytes),
            "previous_surgeries": decrypt_data(patient_document['prev_surgeries'], keybytes),
        }

        # Fetch the image if available
        image_id = patient_document.get('profile_picture')
        if image_id:
            patient_info['image'] = retrieve_image(username, 'patient_details')  # Pass correct collection name
        else:
            patient_info['image'] = None  # No image found

        return patient_info
    
    return None

# Function to display patient details in a Tkinter window
def display_patient_details(patient):
    app = ctk.CTk()
    app.geometry("800x500+350+250")  # Adjust window size as needed
    app.title(f"Profile of {patient['name']}")

    # Create frames for layout
    left_frame = ctk.CTkFrame(app)
    left_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    right_frame = ctk.CTkFrame(app)
    right_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    # Font and color customization
    label_font_bold = ctk.CTkFont(size=16, weight="bold")  # Bold font
    label_font_normal = ctk.CTkFont(size=14)
    label_color = "#00008B"  # Dark blue color

    # Create labels for each piece of patient information and align them to the left
    ctk.CTkLabel(left_frame, text="                        Patient Information", font=label_font_bold, text_color="#00FF00", anchor='w').pack(pady=10, anchor='w')
    ctk.CTkLabel(left_frame, text="    Name:  " + patient['name'], font=label_font_bold, text_color="#FF8000", anchor='w').pack(pady=10, anchor='w')
    ctk.CTkLabel(left_frame, text="    Date of Birth:  " + patient['dob'], font=label_font_bold, text_color="#FF8000", anchor='w').pack(pady=5, anchor='w')
    ctk.CTkLabel(left_frame, text="    Gender:  " + patient['gender'], font=label_font_bold, text_color="#FF8000", anchor='w').pack(pady=5, anchor='w')
    ctk.CTkLabel(left_frame, text="    Blood Group:  " + patient['blood_group'], font=label_font_bold, text_color="#FF8000", anchor='w').pack(pady=10, anchor='w')
    ctk.CTkLabel(left_frame, text="    Allergy:  " + patient['allergy'], font=label_font_bold, text_color="#FF8000", anchor='w').pack(pady=5, anchor='w')
    ctk.CTkLabel(left_frame, text="    Chronic Disease:  " + patient['chronic_disease'], font=label_font_bold, text_color="#FF8000", anchor='w').pack(pady=5, anchor='w')
    ctk.CTkLabel(left_frame, text="    Previous Surgeries:  " + patient['previous_surgeries'], font=label_font_bold, text_color="#FF8000", anchor='w').pack(pady=5, anchor='w')
    ctk.CTkLabel(left_frame, text="    Contact Number:  " + patient['contact_no'], font=label_font_bold, text_color="#FF8000", anchor='w').pack(pady=10, anchor='w')

    # If an image is available, display it in the right frame
    if patient['image']:
        img = patient['image'].resize((350, 350))  # Resize image for the display
        img_tk = ImageTk.PhotoImage(img)
        img_label = ctk.CTkLabel(right_frame, image=img_tk)
        img_label.image = img_tk  # Keep a reference to avoid garbage collection
        img_label.pack(pady=50)

    app.mainloop()

# Main execution
if __name__ == "__main__":
    # username = "sanmarg123"  # You can change this to fetch dynamically later
    username = sys.argv[1]  # You can change this to fetch dynamically later
    patient_details = fetch_patient_details(username)
    
    if patient_details:
        display_patient_details(patient_details)
    else:
        print(f"No patient found with username: {username}")
