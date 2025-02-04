import cv2
import os

# Load the pre-trained face detection model (Haar Cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def crop_all(folder_location):
    output_folder = r'C:\Users\AHMED MALIK\Desktop\New folder\CroppedYale\cropped'  # Make sure the folder path uses 'r' for raw strings in Windows
    os.makedirs(output_folder, exist_ok=True)  # Create output folder if it doesn't exist
    
    # Iterate over all the files in the specified folder
    for filename in os.listdir(folder_location):
        file_path = os.path.join(folder_location, filename)
        
        # Read the image
        image = cv2.imread(file_path)
        if image is None:
            print(f"Failed to load image: {filename}")
            continue
        
        # Convert the image to grayscale for faster face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the grayscale image
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50)
        )
        
        if len(faces) == 0:
            print(f"No faces detected in image: {filename}")
        else:
            for idx, (x, y, w, h) in enumerate(faces):
                # Crop the face from the original image
                face = image[y:y+h, x:x+w]
                
                # Create a unique filename for each cropped face
                base_name = os.path.splitext(filename)[0]
                image_path = os.path.join(output_folder, f"{base_name}_face_{idx + 1}.jpg")
                
                # Save the cropped face
                cv2.imwrite(image_path, face)
                
    
    cv2.destroyAllWindows()

# Specify the folder with images and run the function
crop_all(r'C:\Users\AHMED MALIK\Desktop\New folder\CroppedYale\to_be_cropped')
