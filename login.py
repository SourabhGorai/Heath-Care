import subprocess
from customtkinter import CTk, CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkComboBox, CTkImage
from PIL import Image
from db_connection import get_db_connection
import os


def checkLogin():
    username_entered = username_entry.get()
    password_entered = password_entry.get()
    role_selected = role_combo.get()

    # Get the database connection
    db = get_db_connection()  # Correctly call the function
    collection = db['User_login']  # Access the collection

    # Search for the user in the collection
    user = collection.find({"username": username_entered, "password": password_entered, "role": role_selected})

    if user:
        print("User found")
        if (role_selected == "Doctor"):
            app.destroy()  # Close the login window
            subprocess.run(['python', 'doctor.py', username_entered])
        elif (role_selected == "Patient"):
            app.destroy()  # Close the login window
            subprocess.run(['python', 'patient_dashboard.py', username_entered])
        # elif (role_selected == "Administrator"):
        #     app.destroy()  # Close the login window
        #     os.system('python administrator.py')

    else:
        # Create a label to display error message
        error_label = CTkLabel(master=frame, text="Entered Information is not correct",
                               text_color="#601E88", anchor="w", justify="left", font=("Arial Bold", 14))
        error_label.pack(anchor="w", pady=(21, 0), padx=(25, 0))


def checkSignup():
    role_selected = signUp_role_combo.get()

    if(role_selected == "Doctor"):
        app.destroy()
        subprocess.run(['python','doctor_SignUp.py'])
    elif(role_selected == "Patient"):
        app.destroy()
        subprocess.run(['python','patent_Signup.py'])



app = CTk()
app.geometry("600x480+500+200")
app.resizable(0, 0)

# Load images
side_img_data = Image.open(
    "D:\\01Old\\Python\\PBL\\Sem V\\images\\side-img.png")
email_icon_data = Image.open("D:\\01Old\\Python\\PBL\\Sem V\\images\\usrn.png")
password_icon_data = Image.open(
    "D:\\01Old\\Python\\PBL\\Sem V\\images\\password-icon.png")
role_icon_data = Image.open("D:\\01Old\\Python\\PBL\\Sem V\\images\\role.png")

# Create CTkImages
side_img = CTkImage(dark_image=side_img_data,light_image=side_img_data, size=(300, 480))
email_icon = CTkImage(dark_image=email_icon_data,
                      light_image=email_icon_data, size=(20, 20))
password_icon = CTkImage(dark_image=password_icon_data,
                         light_image=password_icon_data, size=(17, 17))
role_icon = CTkImage(dark_image=role_icon_data,
                     light_image=role_icon_data, size=(17, 17))

# Side image label
CTkLabel(master=app, text="", image=side_img).pack(expand=True, side="left")

# Frame for login elements
frame = CTkFrame(master=app, width=300, height=480, fg_color="#ffffff")
frame.pack_propagate(0)
frame.pack(expand=True, side="right")

# Welcome labels
CTkLabel(master=frame, text="Welcome Back!", text_color="#601E88", anchor="w",
         justify="left", font=("Arial Bold", 24)).pack(anchor="w", pady=(30, 5), padx=(25, 0))
CTkLabel(master=frame, text="Sign in to your account", text_color="#7E7E7E",
         anchor="w", justify="left", font=("Arial Bold", 12)).pack(anchor="w", padx=(25, 0))

# Username entry
CTkLabel(master=frame, text="  Username:", text_color="#601E88", anchor="w", justify="left", font=(
    "Arial Bold", 14), image=email_icon, compound="left").pack(anchor="w", pady=(30, 0), padx=(25, 0))
username_entry = CTkEntry(master=frame, width=225, fg_color="#EEEEEE",
                          border_color="#601E88", border_width=1, text_color="#000000")
username_entry.pack(anchor="w", padx=(25, 0))

# Password entry
CTkLabel(master=frame, text="  Password:", text_color="#601E88", anchor="w", justify="left", font=(
    "Arial Bold", 14), image=password_icon, compound="left").pack(anchor="w", pady=(21, 0), padx=(25, 0))
password_entry = CTkEntry(master=frame, width=225, fg_color="#EEEEEE",
                          border_color="#601E88", border_width=1, text_color="#000000", show="*")
password_entry.pack(anchor="w", padx=(25, 0))

# Role entry
CTkLabel(master=frame, text="  Role:", text_color="#601E88", anchor="w", justify="left", font=(
    "Arial Bold", 14), image=role_icon, compound="left").pack(anchor="w", pady=(21, 0), padx=(25, 0))

roles = [ "Doctor", "Patient"]
role_combo = CTkComboBox(master=frame, values=roles, width=225, fg_color="#EEEEEE",
                         border_color="#601E88", border_width=1, text_color="#000000")
role_combo.pack(anchor="w", padx=(25, 0))

# Login button
CTkButton(master=frame, text="Login", fg_color="#601E88", hover_color="#E44982", font=("Arial Bold", 12),
          text_color="#ffffff", width=225, command=checkLogin).pack(anchor="w", pady=(20, 0), padx=(25, 0))

signUp_roles = ["Doctor", "Patient"]
signUp_role_combo = CTkComboBox(master=frame, values=signUp_roles, width=225, fg_color="#EEEEEE",
                         border_color="#601E88", border_width=1, text_color="#000000")
signUp_role_combo.pack(anchor="w", padx=(25, 0), pady=(15,0))

signup_button = CTkButton(master=frame, text="Signup", fg_color="#601E88", hover_color="#E44982", font=("Arial Bold", 12),
          text_color="#ffffff", width=225, command=checkSignup).pack(anchor="w", pady=(20, 0), padx=(25, 0))

app.mainloop()