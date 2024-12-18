from msilib import Binary
import tkinter
from tkinter import filedialog
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkImage, CTkButton
from PIL import Image
import os
from db_connection import get_db_connection
import gridfs
from pymongo import errors
from cryptography.fernet import Fernet
import base64
import uuid
from bson import Binary

# Initialize variables
img_path = None  # To store image file path


class CustomMessageBox:
    def __init__(self, master, title, message, text_size):
        self.top = ctk.CTkToplevel(master)
        self.top.title(title)

        # Set the message box to be modal
        self.top.grab_set()  # Make this window modal

        # Create a label to display the message
        self.label = ctk.CTkLabel(
            self.top, text=message, text_color="#E0E0E0", font=("Arial", text_size, "bold"))
        self.label.pack(padx=20, pady=20)

        # Create an OK button to close the message box
        self.ok_button = ctk.CTkButton(
            self.top, text="OK", command=self.top.destroy)
        self.ok_button.pack(pady=(0, 20))

        # Center the window
        # Adjust size and position as needed
        self.top.geometry("300x150+730+500")


def back():
    app.destroy()  # Close the login window
    os.system('python login.py')


# ******************ENCRIPTION**************

key = Fernet.generate_key()
cipher_suite = Fernet(key)

def encrypt_data(data):
    """Encrypt the provided data using the Fernet cipher."""
    if not isinstance(data, bytes):
        data = data.encode('utf-8')
    encrypted_data = cipher_suite.encrypt(data)
    return encrypted_data.decode('utf-8')

def decrypt_data(encrypted_data):
    """Decrypt the provided data using the Fernet cipher."""
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
    return decrypted_data.decode('utf-8')

# ************************************************

    
def signup():
    name_data = entry1.get()
    dob_data = entry2.get()
    gender_data = entry3.get()
    contact_no_data = entry4.get()
    email_data = entry5.get()
    paddress_data = entry6.get()
    bg_data = entry7.get()
    allergy_data = entry8.get()
    chronic_disease_data = entry9.get()
    prevSurgeries_data = entry10.get()
    username_data = entry11.get()
    password_data = entry12.get()
    secQ_data = entry13.get()
    secA_data = entry14.get()

    # Check for empty fields
    mandatory_fields = [
        name_data, dob_data, gender_data, contact_no_data,
        email_data, paddress_data, bg_data, allergy_data,
        chronic_disease_data, prevSurgeries_data,
        username_data, password_data, secQ_data
    ]

    if any(not field.strip() for field in mandatory_fields):
        msg_box = CustomMessageBox(app, "Error", "Please fill in all mandatory fields.", 12)
        app.wait_window(msg_box.top)
        return  # Exit the function if fields are empty

    try:

        # Encrypt sensitive data
        encrypted_name = encrypt_data(name_data)
        encrypted_dob = encrypt_data(dob_data)
        encrypted_contact = encrypt_data(contact_no_data)
        encrypted_email = encrypt_data(email_data)
        encrypted_address = encrypt_data(paddress_data)
        encrypted_bloodG = encrypt_data(bg_data)
        encrypted_allergy = encrypt_data(allergy_data)
        encrypted_CDisease = encrypt_data(chronic_disease_data)
        encrypted_prevSurgery = encrypt_data(prevSurgeries_data)
        encrypted_password = encrypt_data(password_data)  # Encrypt password
        encrypted_secQ = encrypt_data(secQ_data)  # Encrypt password
        encrypted_secA = encrypt_data(secA_data)

        # Get the database connection
        db = get_db_connection()
        fs = gridfs.GridFS(db)  # Create a GridFS instance to store the image

        custom_id = str(uuid.uuid4())

        # Document to insert
        document = {
            "_id": custom_id,
            "name": encrypted_name,
            "dob": encrypted_dob,
            "gender": gender_data,
            "ph_no": encrypted_contact,
            "email": encrypted_email,
            "address": encrypted_address,
            "blood_G": encrypted_bloodG,
            "allergy": encrypted_allergy,
            "chro_disease": encrypted_CDisease,
            "prev_surgeries": encrypted_prevSurgery,
            "username": username_data,
            "password": encrypted_password,
            "security_ques": encrypted_secQ,
            "security_ans": encrypted_secA
        }
        
        document2 = {
        "_id": custom_id,  # or use another identifier if needed
        "key": Binary(key)  # Store the key as a base64 string
        }
        insert_result2 = db['keys'].insert_one(document2)

        if insert_result2:
            # If an image was uploaded, save it in GridFS
            if img_path:
                with open(img_path, "rb") as image_file:
                    image_id = fs.put(
                        image_file, filename=os.path.basename(img_path))
                    # Save the reference to the image in the document
                    document["profile_picture"] = image_id

            # Insert the document into the collection
            insert_result = db['patient_details'].insert_one(document)
            print("Inserted document ID:", insert_result.inserted_id)

        else:
            print("Insertion of key is failed")

        msg_box = CustomMessageBox(app, "Information", "Sign Up Successful", 25)
        # Handle close event if necessary

        db['User_login'].insert_one({"username":username_data,"password":password_data,"roll":"Patient"})

        msg_box.top.protocol("WM_DELETE_WINDOW", lambda: self.close_app())

        # Wait for the message box to be closed before continuing
        app.wait_window(msg_box.top)

        app.destroy()  # Close the login window
        os.system('python login.py')

    except errors.ConnectionFailure:
        print("Failed to connect to MongoDB")
    except errors.DuplicateKeyError:
        print("Duplicate key error: document already exists")
    except Exception as e:
        print("An error occurred:", e)

# Function to upload an image


def upload_image():
    global img_path
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])

    if file_path:
        # Load and display the image
        uploaded_image = Image.open(file_path)
        ctk_image = CTkImage(dark_image=uploaded_image,
                             size=(100, 100))  # Adjust size as needed

        # Update the label with the new image
        image_label.configure(image=ctk_image)
        image_label.image = ctk_image  # Keep a reference to prevent garbage collection

        # Store the file path or image data for uploading to MongoDB later
        img_path = file_path


# Create the tkinter window
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.geometry("800x500+350+200")
app.title("Signup")
app.resizable(False, False)

# Load image and set it as the background
img1 = Image.open("D:\\01Old\\Python\\PBL\\Sem V\\images\\doctor_signup.jpg")
bg_image = CTkImage(dark_image=img1, light_image=img1, size=(800, 500))

# Create label for background image
bg_label = CTkLabel(master=app, text="", image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Create a frame for the form
canvas = tkinter.Canvas(bg_label, width=850, height=550, bg="#2E2E2E")
canvas.place(x=200, y=100)

# Scrollbar for the canvas
y_scroll = tkinter.Scrollbar(bg_label, orient='vertical', command=canvas.yview)
y_scroll.place(x=1027, y=100, height=552)

canvas.configure(yscrollcommand=y_scroll.set)
scrollable_frame = tkinter.Frame(canvas, bg="#2E2E2E")
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# ******************ENTRY FIELDS************************

l3 = CTkLabel(master=bg_label, text="Patient Sign UP", font=(
    'Century Gothic', 20, 'bold'), text_color="#FF9933")
l3.configure(fg_color="transparent")
l3.place(x=330, y=20)

# # Name label and entry
name_label = CTkLabel(master=scrollable_frame, text="Name: ",
                      text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
name_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

entry1 = CTkEntry(master=scrollable_frame, width=220,
                  placeholder_text="Full Name")
entry1.grid(row=1, column=1, padx=10, pady=5, sticky="w")

# DOB label and entry
dob_label = CTkLabel(master=scrollable_frame, text="Date of Birth: ",
                     text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
dob_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

entry2 = CTkEntry(master=scrollable_frame, width=220,
                  placeholder_text="DD/MM/YYYY")
entry2.grid(row=2, column=1, padx=10, pady=5, sticky="w")

# Gender label and entry
gender_label = CTkLabel(master=scrollable_frame, text="Gender: ",
                        text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
gender_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

gender_var = tkinter.StringVar()
gender_options = ["Male", "Female", "Others"]

entry3 = ctk.CTkOptionMenu(scrollable_frame, variable=gender_var, values=gender_options)
entry3.grid(row=3, column=1, padx=10, pady=5)

# Phone number label and entry
phno_label = CTkLabel(master=scrollable_frame, text="Ph Number: ",
                      text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
phno_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

entry4 = CTkEntry(master=scrollable_frame, width=220,
                  placeholder_text="Phone Number")
entry4.grid(row=4, column=1, padx=10, pady=5, sticky="w")

# Email label and entry
email_label = CTkLabel(master=scrollable_frame, text="Email Address: ",
                       text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
email_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")

entry5 = CTkEntry(master=scrollable_frame, width=220,
                  placeholder_text="Email Address")
entry5.grid(row=5, column=1, padx=10, pady=5, sticky="w")

# Permanent Address label and entry
permAdd_label = CTkLabel(master=scrollable_frame, text="Permanent Address: ",
                         text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
permAdd_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")

entry6 = CTkEntry(master=scrollable_frame, width=220,
                  placeholder_text="Permanent Address")
entry6.grid(row=6, column=1, padx=10, pady=5, sticky="w")

# Medical License label and entry
bloodG_label = CTkLabel(master=scrollable_frame, text="Blood Group: ",
                        text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
bloodG_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")

entry7 = CTkEntry(master=scrollable_frame, width=220,
                  placeholder_text="A+, B+, etc.")
entry7.grid(row=7, column=1, padx=10, pady=5, sticky="w")

# Specialization label and entry
Allergies_label = CTkLabel(master=scrollable_frame, text="Allergies: ",
                           text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
Allergies_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")

entry8 = CTkEntry(master=scrollable_frame, width=220,
                  placeholder_text="Allergies")
entry8.grid(row=8, column=1, padx=10, pady=5, sticky="w")

# Experience label and entry
chronic_Diseases_label = CTkLabel(master=scrollable_frame, text="Chronic Diseases: ",
                                  text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
chronic_Diseases_label.grid(row=9, column=0, padx=10, pady=5, sticky="w")

entry9 = CTkEntry(master=scrollable_frame, width=220,
                  placeholder_text="e.g., diabetes, hypertension")
entry9.grid(row=9, column=1, padx=10, pady=5, sticky="w")

# Qualification label and entry
prev_surgeries_label = CTkLabel(master=scrollable_frame, text="Previous Surgeries : ",
                                text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
prev_surgeries_label.grid(row=10, column=0, padx=10, pady=5, sticky="w")

entry10 = CTkEntry(master=scrollable_frame, width=220,
                   placeholder_text="Previous Surgeries ")
entry10.grid(row=10, column=1, padx=10, pady=5, sticky="w")

# Username label and entry
Username_label = CTkLabel(master=scrollable_frame, text="Username: ",
                          text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
Username_label.grid(row=11, column=0, padx=10, pady=5, sticky="w")

entry11 = CTkEntry(master=scrollable_frame, width=220,
                   placeholder_text="Username")
entry11.grid(row=11, column=1, padx=10, pady=5, sticky="w")

password_label = CTkLabel(master=scrollable_frame, text="Password :",
                          text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
password_label.grid(row=12, column=0, padx=10, pady=5, sticky="w")

entry12 = CTkEntry(master=scrollable_frame, width=220,
                   placeholder_text="Password")
entry12.grid(row=12, column=1, padx=10, pady=5, sticky="w")

secQ_var = tkinter.StringVar()
security_questions = [
    "What is your pet's name?",
    "What is your mother's maiden name?",
    "What was your first car?",
    "What city were you born in?"
]

secQ_ques_label = CTkLabel(master=scrollable_frame, text="Security Question: ", text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
secQ_ques_label.grid(row=13, column=0, padx=10, pady=5, sticky="w")

entry13 = ctk.CTkOptionMenu(scrollable_frame, variable=secQ_var, values=security_questions)
entry13.grid(row=13, column=1, padx=10, pady=5)

# Security Answer label and entry
secQ_answer_label = CTkLabel(master=scrollable_frame, text="Security Answer: ", text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
secQ_answer_label.grid(row=14, column=0, padx=10, pady=5, sticky="w")

entry14 = CTkEntry(master=scrollable_frame, width=220, placeholder_text="Secq answer")
entry14.grid(row=14, column=1, padx=10, pady=5, sticky="w")

# Image upload button and label
upload_button = CTkButton(master=scrollable_frame,
                          text="Upload Image", command=upload_image)
upload_button.grid(row=15, column=0, columnspan=2, padx=10, pady=5)

# Label to display uploaded image
image_label = CTkLabel(master=scrollable_frame, text="")
image_label.grid(row=16, column=0, columnspan=2, padx=10, pady=5)

# Submit button to trigger signup
button1 = CTkButton(master=bg_label, text="Signup", fg_color="#601E88", hover_color="#E44982", font=("Arial Bold", 12),
                    text_color="#ffffff", width=150, command=signup)
button1.place(x=550, y=440)

back_button = CTkButton(master=bg_label, text="Back", fg_color="#601E88", hover_color="#E44982", font=("Arial Bold", 12),
                    text_color="#ffffff", width=150, command=back)
back_button.place(x=380, y=440)

# Scroll region update


def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))


scrollable_frame.bind("<Configure>", on_frame_configure)

app.mainloop()
