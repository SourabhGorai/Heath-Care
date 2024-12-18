# import gridfs
# from pymongo import MongoClient
# from PIL import Image
# import io
# from db_connection import get_db_connection  # Assuming this is a module to connect to MongoDB

# # Function to retrieve image using profile picture ObjectId from doctor details
# def retrieve_image(doctor_usrn,coll_name):
#     try:
#         # Connect to MongoDB
#         db = get_db_connection()  # Adjust if your function requires parameters
#         doctor_details_collection = db[coll_name]

#         # Get the doctor's details from 'doctor_details' collection
#         doctor_details = doctor_details_collection.find_one({"username": doctor_usrn})
#         if not doctor_details or 'profile_picture' not in doctor_details:
#             print("Doctor not found or profile picture not set.")
#             return None

#         # Retrieve the image's ObjectId from the doctor's details
#         image_id = doctor_details['profile_picture']

#         # Use GridFS to access the image file from GridFS
#         fs = gridfs.GridFS(db)
#         image_data = fs.get(image_id).read()

#         # Load the image data into a PIL Image
#         image = Image.open(io.BytesIO(image_data))

#         return image

#     except Exception as e:
#         print(f"Error retrieving image: {e}")
#         return None


import gridfs
from pymongo import MongoClient
from PIL import Image
import io
from bson import ObjectId  # Import ObjectId for BSON handling
from db_connection import get_db_connection  # Assuming this is a module to connect to MongoDB

# Function to retrieve image using profile picture ObjectId from doctor details
def retrieve_image(usrn, coll_name): 
    # print(usrn)
    # print(coll_name)
    try:
        # Connect to MongoDB
        db = get_db_connection()  # Adjust if your function requires parameters
        details_collection = db[coll_name] 

        # Get the doctor's details from 'doctor_details' collection
        details = details_collection.find_one({"username": usrn})
        if not details or 'profile_picture' not in details:
            print("Image not found or profile picture not set.")
            return None

        # Retrieve the image's ObjectId from the doctor's details
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

# if __name__ == "__main__":
#     image = retrieve_image("patientB456", "patient_details")
#     if image:
#         image.show()  # This will display the image using the default image viewer
#     else:
#         print("No image retrieved.")
