# admin2 key = <cryptography.fernet.Fernet object at 0x0000020D5F615B90>
# admin3 key = b'-1tDB2U7aCJYnuJYFfroHuW14bKQJKPbAM1ALo8ZahM='


import tkinter
from tkinter import filedialog
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkImage, CTkButton, CTkRadioButton
from PIL import Image
import os
from db_connection import get_db_connection
import gridfs
from pymongo import errors
from cryptography.fernet import Fernet
import base64
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
        self.top.geometry("300x150+730+500")


def back():
    app.destroy()  # Close the login window
    os.system('python login.py')

# ******************ENCRYPTION**************

key = Fernet.generate_key()
cipher_suite = Fernet(key)
print(key)

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
    mln_data = entry7.get()
    spec_data = entry8.get()
    experience_data = entry9.get()
    qualific_data = entry10.get()
    username_data = entry11.get()
    password_data = entry12.get()
    secQ_data = entry13.get()
    secA_Data = entry14.get()
    available_days_data = entry15.get()

    # Check for empty fields
    mandatory_fields = [
        name_data, dob_data, gender_data, contact_no_data,
        email_data, paddress_data, mln_data, spec_data,
        experience_data, qualific_data,
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
        encrypted_mln = encrypt_data(mln_data)
        encrypted_password = encrypt_data(password_data)  # Encrypt password
        encrypted_secQ = encrypt_data(secQ_data)  # Encrypt security question
        encrypted_secA = encrypt_data(secA_Data)

        # Get the database connection
        db = get_db_connection()
        fs = gridfs.GridFS(db)  # Create a GridFS instance to store the image

        # Generate custom ID using name and medical license number
        custom_id = f"{name_data.replace(' ', '_')}_{mln_data}"

        # Document to insert
        document = {
            "_id": custom_id,  # Custom ID
            "name": encrypted_name,
            "dob": encrypted_dob,
            "gender": gender_data,
            "ph_no": encrypted_contact,
            "email": encrypted_email,
            "address": encrypted_address,
            "medical_lisc_no": encrypted_mln,
            "specialization": spec_data,
            "experience": experience_data,
            "qualification": qualific_data,
            "username": username_data,
            "password": encrypted_password,
            "security_ques": encrypted_secQ,
            "security_ans" : encrypted_secA,
            "available_days": available_days_data
        }

        document2 = {
        "_id": custom_id,  # or use another identifier if needed
        "key": Binary(key)  # Store the key as a base64 string
        }
        insert_result2 = db['keys'].insert_one(document2)
        if insert_result2:
            print("Inserion of key successfull")
            # If an image was uploaded, save it in GridFS
            if img_path:
                with open(img_path, "rb") as image_file:
                    image_id = fs.put(image_file, filename=os.path.basename(img_path))
                    document["profile_picture"] = image_id  # Save the reference to the image in the document

            # Insert the document into the collection
            insert_result = db['doctor_details'].insert_one(document)
            print("Inserted document ID:", insert_result.inserted_id)
        else:
            print("Keys not inserted")

        msg_box = CustomMessageBox(app, "Information", "Sign Up Successful", 25)
        db['User_login'].insert_one({"username":username_data,"password":password_data,"roll":"Doctor"})
        # Handle close event if necessary
        msg_box.top.protocol("WM_DELETE_WINDOW", lambda: self.close_app())

        app.wait_window(msg_box.top)

        app.destroy()  # Close the window
        os.system('python login.py')

    except errors.ConnectionFailure:
        print("Failed to connect to MongoDB")
    except errors.DuplicateKeyError:
        print("Duplicate key error: document already exists")
    except Exception as e:
        print("An error occurred:", e)


def upload_image():
    global img_path
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
    
    if file_path:
        uploaded_image = Image.open(file_path)
        ctk_image = CTkImage(dark_image=uploaded_image, size=(100, 100))  # Adjust size as needed
        image_label.configure(image=ctk_image)
        image_label.image = ctk_image  # Keep a reference
        img_path = file_path


# Ensure MongoDB indexing
def ensure_indexing():
    try:
        db = get_db_connection()
        db['doctor_details'].create_index([("username", 1)], unique=True)  # Ensure index on username
    except Exception as e:
        print("Error creating index:", e)


# Call ensure_indexing function during initialization
ensure_indexing()

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
canvas.place(x=200, y=70)

# Scrollbar for the canvas
y_scroll = tkinter.Scrollbar(bg_label, orient='vertical', command=canvas.yview)
y_scroll.place(x=1027, y=70, height=552)

canvas.configure(yscrollcommand=y_scroll.set)
scrollable_frame = tkinter.Frame(canvas, bg="#2E2E2E")
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# ******************ENTRY FIELDS************************

l3 = CTkLabel(master=scrollable_frame, text="Sign UP", font=('Century Gothic', 20))
l3.grid(row=0, column=0, columnspan=2, pady=(15, 10))

# # Name label and entry
name_label = CTkLabel(master=scrollable_frame, text="Name: ", text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
name_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

entry1 = CTkEntry(master=scrollable_frame, width=220, placeholder_text="Full Name")
entry1.grid(row=1, column=1, padx=10, pady=5, sticky="w")

# DOB label and entry
dob_label = CTkLabel(master=scrollable_frame, text="Date of Birth: ", text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
dob_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

entry2 = CTkEntry(master=scrollable_frame, width=220, placeholder_text="DD/MM/YYYY")
entry2.grid(row=2, column=1, padx=10, pady=5, sticky="w")

# Gender label and entry
gender_label = CTkLabel(master=scrollable_frame, text="Gender: ", text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
gender_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

# *****************************

gender_var = tkinter.StringVar()
gender_options = ["Male", "Female", "Others"]

entry3 = ctk.CTkOptionMenu(scrollable_frame, variable=gender_var, values=gender_options)
entry3.grid(row=3, column=1, padx=10, pady=5)

# *******************************

# Phone number label and entry
phno_label = CTkLabel(master=scrollable_frame, text="Ph Number: ", text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
phno_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

entry4 = CTkEntry(master=scrollable_frame, width=220, placeholder_text="Phone Number")
entry4.grid(row=4, column=1, padx=10, pady=5, sticky="w")

# Email label and entry
email_label = CTkLabel(master=scrollable_frame, text="Email Address: ", text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
email_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")

entry5 = CTkEntry(master=scrollable_frame, width=220, placeholder_text="Email Address")
entry5.grid(row=5, column=1, padx=10, pady=5, sticky="w")

# Permanent Address label and entry
permAdd_label = CTkLabel(master=scrollable_frame, text="Permanent Address: ", text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
permAdd_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")

entry6 = CTkEntry(master=scrollable_frame, width=220, placeholder_text="Permanent Address")
entry6.grid(row=6, column=1, padx=10, pady=5, sticky="w")

# Medical License label and entry
MedicLisc_no_label = CTkLabel(master=scrollable_frame, text="Medical License No: ", text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
MedicLisc_no_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")

entry7 = CTkEntry(master=scrollable_frame, width=220, placeholder_text="Medical License No")
entry7.grid(row=7, column=1, padx=10, pady=5, sticky="w")

# Specialization label and entry
special_label = CTkLabel(master=scrollable_frame, text="Specialization: ", text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
special_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")

entry8 = CTkEntry(master=scrollable_frame, width=220, placeholder_text="Specialization")
entry8.grid(row=8, column=1, padx=10, pady=5, sticky="w")

# Experience label and entry
experience_label = CTkLabel(master=scrollable_frame, text="Experience: ", text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
experience_label.grid(row=9, column=0, padx=10, pady=5, sticky="w")

entry9 = CTkEntry(master=scrollable_frame, width=220, placeholder_text="Experience")
entry9.grid(row=9, column=1, padx=10, pady=5, sticky="w")

# Qualification label and entry
Qualification_label = CTkLabel(master=scrollable_frame, text="Qualification: ", text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
Qualification_label.grid(row=10, column=0, padx=10, pady=5, sticky="w")

entry10 = CTkEntry(master=scrollable_frame, width=220, placeholder_text="Qualification")
entry10.grid(row=10, column=1, padx=10, pady=5, sticky="w")

# Username label and entry
Username_label = CTkLabel(master=scrollable_frame, text="Username: ", text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
Username_label.grid(row=11, column=0, padx=10, pady=5, sticky="w")

entry11 = CTkEntry(master=scrollable_frame, width=220, placeholder_text="Username")
entry11.grid(row=11, column=1, padx=10, pady=5, sticky="w")

password_label = CTkLabel(master=scrollable_frame, text="Password :", text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
password_label.grid(row=12, column=0, padx=10, pady=5, sticky="w")

entry12 = CTkEntry(master=scrollable_frame, width=220, placeholder_text="Password")
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

# Username label and entry
available_days_label = CTkLabel(master=scrollable_frame, text="Available Days: ", text_color="#7E7E7E", anchor="w", font=("Arial Bold", 18))
available_days_label.grid(row=15, column=0, padx=10, pady=5, sticky="w")

entry15 = CTkEntry(master=scrollable_frame, width=220, placeholder_text="Available Days")
entry15.grid(row=15, column=1, padx=10, pady=5, sticky="w")

# Image upload button and label
upload_button = CTkButton(master=scrollable_frame, text="Upload Image", command=upload_image)
upload_button.grid(row=16, column=0, columnspan=2, padx=10, pady=5)

image_label = CTkLabel(master=scrollable_frame, text="")  # Label to display uploaded image
image_label.grid(row=17, column=0, columnspan=2, padx=10, pady=5)

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




