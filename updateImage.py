# import gridfs
# from pymongo import MongoClient
# from PIL import Image
# import io
# from bson import ObjectId
# from db_connection import get_db_connection  # Assuming this is a module to connect to MongoDB
# import tkinter as tk
# from tkinter import filedialog, messagebox

# def retrieve_image(username, collection_name):
#     """
#     Retrieve the profile picture of a user from MongoDB.

#     Parameters:
#         username (str): The username of the user whose profile picture is being retrieved.
#         collection_name (str): The name of the MongoDB collection.

#     Returns:
#         PIL.Image: The retrieved image as a PIL Image object, or None if not found.
#     """
#     try:
#         # Connect to MongoDB
#         db = get_db_connection()
#         details_collection = db[collection_name]

#         # Get the user's details from the specified collection
#         details = details_collection.find_one({"username": username})
#         if not details or 'profile_picture' not in details:
#             print("Image not found or profile picture not set.")
#             return None

#         # Retrieve the image's ObjectId from the user's details
#         image_id = details['profile_picture']

#         # If image_id is a string, convert it to ObjectId
#         if isinstance(image_id, str):
#             image_id = ObjectId(image_id)

#         # Use GridFS to access the image file from GridFS
#         fs = gridfs.GridFS(db)
#         image_data = fs.get(image_id).read()

#         # Load the image data into a PIL Image
#         image = Image.open(io.BytesIO(image_data))

#         return image

#     except Exception as e:
#         print(f"Error retrieving image: {e}")
#         return None

# def update_image(username, collection_name, image_path):
#     """
#     Update the profile picture for a specific user in the specified MongoDB collection.

#     Parameters:
#         username (str): The username of the user whose image needs to be updated.
#         collection_name (str): The name of the MongoDB collection.
#         image_path (str): The path of the new image to be uploaded.

#     Returns:
#         bool: True if the image was updated successfully, False otherwise.
#     """
#     # Connect to MongoDB
#     db = get_db_connection()

#     # Load the new image from the selected path
#     try:
#         new_image = Image.open(image_path)
#     except Exception as e:
#         print(f"Error opening image file: {e}")
#         return False
    
#     # Convert the new image to binary for storage
#     img_byte_arr = io.BytesIO()
#     new_image.save(img_byte_arr, format='PNG')  # Save as PNG or any other format
#     img_byte_arr.seek(0)
#     image_data = img_byte_arr.read()

#     # Store the new image in GridFS
#     fs = gridfs.GridFS(db)
#     image_id = fs.put(image_data, filename=f"{username}_profile_picture")

#     # Update the database with the new image's ObjectId
#     result = db[collection_name].update_one(
#         {"username": username},
#         {"$set": {"profile_picture": image_id}}  # Assuming the field to store image ObjectId is 'profile_picture'
#     )

#     if result.modified_count > 0:
#         print("Image updated successfully.")
#         return True
#     else:
#         print("No changes made to the image.")
#         return False

# def choose_image_and_update(username, collection_name):
#     """
#     Open a file dialog to choose an image and update the profile picture.

#     Parameters:
#         username (str): The username of the user whose image needs to be updated.
#         collection_name (str): The name of the MongoDB collection.
#     """
#     image_path = filedialog.askopenfilename(title="Select an Image", 
#                                              filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
    
#     if image_path:
#         if update_image(username, collection_name, image_path):
#             messagebox.showinfo("Success", "Profile picture updated successfully!")
#         else:
#             messagebox.showerror("Error", "Failed to update profile picture.")

# def create_gui(username, collection_name):
#     """
#     Create a simple GUI with a button to update the profile picture.

#     Parameters:
#         username (str): The username of the user.
#         collection_name (str): The name of the MongoDB collection.
#     """
#     root = tk.Tk()
#     root.title("Update Profile Picture")
    
#     label = tk.Label(root, text="Click the button to update your profile picture.")
#     label.pack(pady=20)

#     update_button = tk.Button(root, text="Choose Image", command=lambda: choose_image_and_update(username, collection_name))
#     update_button.pack(pady=10)

#     root.mainloop()

# # Example usage:
# # create_gui("admin321", "doctor_details")


import sys
import gridfs
from pymongo import MongoClient
from PIL import Image
import io
from bson import ObjectId
from db_connection import get_db_connection  # Make sure this module is correctly implemented
import tkinter as tk
from tkinter import filedialog, messagebox

def retrieve_image(username, collection_name):
    """
    Retrieve the profile picture of a user from MongoDB.

    Parameters:
        username (str): The username of the user whose profile picture is being retrieved.
        collection_name (str): The name of the MongoDB collection.

    Returns:
        PIL.Image: The retrieved image as a PIL Image object, or None if not found.
    """
    try:
        # Connect to MongoDB
        db = get_db_connection()
        details_collection = db[collection_name]

        # Get the user's details from the specified collection
        details = details_collection.find_one({"username": username})
        if not details or 'profile_picture' not in details:
            print("Image not found or profile picture not set.")
            return None

        # Retrieve the image's ObjectId from the user's details
        image_id = details['profile_picture']

        # If image_id is a string, convert it to ObjectId
        if isinstance(image_id, str):
            image_id = ObjectId(image_id)

        # Use GridFS to access the image file from GridFS
        fs = gridfs.GridFS(db)
        image_data = fs.get(image_id).read()

        # Load the image data into a PIL Image
        image = Image.open(io.BytesIO(image_data))

        return image

    except Exception as e:
        print(f"Error retrieving image: {e}")
        return None

def update_image(username, collection_name, image_path):
    """
    Update the profile picture for a specific user in the specified MongoDB collection.

    Parameters:
        username (str): The username of the user whose image needs to be updated.
        collection_name (str): The name of the MongoDB collection.
        image_path (str): The path of the new image to be uploaded.

    Returns:
        bool: True if the image was updated successfully, False otherwise.
    """
    # Connect to MongoDB
    db = get_db_connection()

    # Load the new image from the selected path
    try:
        new_image = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image file: {e}")
        return False
    
    # Convert the new image to binary for storage
    img_byte_arr = io.BytesIO()
    new_image.save(img_byte_arr, format='PNG')  # Save as PNG or any other format
    img_byte_arr.seek(0)
    image_data = img_byte_arr.read()

    # Store the new image in GridFS
    fs = gridfs.GridFS(db)
    image_id = fs.put(image_data, filename=f"{username}_profile_picture")

    # Update the database with the new image's ObjectId
    result = db[collection_name].update_one(
        {"username": username},
        {"$set": {"profile_picture": image_id}}  # Assuming the field to store image ObjectId is 'profile_picture'
    )

    if result.modified_count > 0:
        print("Image updated successfully.")
        return True
    else:
        print("No changes made to the image.")
        return False

def choose_image_and_update(username, collection_name):
    """
    Open a file dialog to choose an image and update the profile picture.

    Parameters:
        username (str): The username of the user whose image needs to be updated.
        collection_name (str): The name of the MongoDB collection.
    """
    image_path = filedialog.askopenfilename(title="Select an Image", 
                                             filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
    
    if image_path:
        if update_image(username, collection_name, image_path):
            messagebox.showinfo("Success", "Profile picture updated successfully!")
        else:
            messagebox.showerror("Error", "Failed to update profile picture.")

class DoctorProfileApp:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.create_ui()

    def create_ui(self):
        self.master.title("Doctor Profile")
        
        # Create a label for the username
        username_label = tk.Label(self.master, text=f"Logged in as: {self.username}")
        username_label.pack(pady=10)

        # Create an Update Image Button
        update_image_button = tk.Button(self.master, text="Update Image", command=self.update_image)
        update_image_button.pack(pady=10)

        # Load and display the current profile image if available
        self.display_current_image()

    def display_current_image(self):
        """Load and display the current profile picture."""
        image = retrieve_image(self.username, "doctor_details")
        if image:
            # Convert the image to a PhotoImage and display it
            image.thumbnail((100, 100))  # Resize for display purposes
            self.current_image = ImageTk.PhotoImage(image)
            image_label = tk.Label(self.master, image=self.current_image)
            image_label.pack(pady=10)
        else:
            print("No current image to display.")

    def update_image(self):
        choose_image_and_update(self.username, "doctor_details")

# External function to update image
def update_image_from_external(username, collection_name):
    """
    Function to update the image for a given user without launching the GUI.

    Parameters:
        username (str): The username of the user whose image needs to be updated.
        collection_name (str): The name of the MongoDB collection.
    """
    image_path = filedialog.askopenfilename(title="Select an Image", 
                                             filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
    
    if image_path:
        if update_image(username, collection_name, image_path):
            print("Profile picture updated successfully!")
        else:
            print("Failed to update profile picture.")

if __name__ == "__main__":
    root = tk.Tk()
    username = sys.argv[1]  # Replace with the actual username from your logic
    # username = "admin321"  # Replace with the actual username from your logic
    app = DoctorProfileApp(root, username)
    root.mainloop()
