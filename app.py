from flask import Flask, render_template, request, jsonify, redirect, url_for
import base64
import os
import cv2
import numpy as np
import warnings
import logging
import pickle
import face_recognition
import datetime
import pandas as pd


# Suppress warnings
warnings.filterwarnings("ignore")
logging.getLogger('tensorflow').disabled = True  # Disable TensorFlow logging

with open('encoded_faces.pkl','rb') as f:
    encoded_known_faces,person_faces= pickle.load(f)




def predict_image(img_path):
        
        img = face_recognition.load_image_file(img_path)
        encoded_unknown_img=face_recognition.face_encodings(img)

        if len(encoded_unknown_img) == 0:
            return "No face detected\nTry Again!",95
        matches= face_recognition.compare_faces(encoded_known_faces,encoded_unknown_img[0])
        face_distance= face_recognition.face_distance(encoded_known_faces,encoded_unknown_img[0])
        
        best_match= face_distance.argmin()
        
        if not matches[best_match]:  
              
              return "Unknown", 95


        predicted_class_name= person_faces[best_match]
        x= face_distance[best_match]
        prediction= (1-x)*100

        if prediction<=60:

            return "Unknown", 95
        
     
         
                        
        return predicted_class_name, prediction

time_now = datetime.datetime.now()
print(time_now)
x=str(time_now).split()
date= x[0]
time=x[1][0:8]
print(date)
print(time)

def crop_face(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Image not found at path: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return "No face detected. Please try again."

    for (x, y, w, h) in faces:
        cropped_face = img[y:y+h, x:x+w]
        break

    cropped_image_path = image_path.replace('.jpg', '_cropped_face.jpg')
    cv2.imwrite(cropped_image_path, cropped_face)

    return cropped_image_path
 




                                                 
app = Flask(__name__)
logging.basicConfig(level=logging.ERROR)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMPLATES_AUTO_RELOAD'] = True
existing_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.startswith('snapshot') and f.endswith('.png')]
no_images = len(existing_files)  


@app.route('/')
def home():
    return render_template('index.html')


from flask import jsonify

@app.route('/upload_snapshot', methods=['POST'])
def upload_snapshot():
    global no_images

    try:
        data = request.json
        if 'image' in data:
            image_data = data['image']
            header, encoded = image_data.split(',', 1)
            filename = f"snapshot{no_images}.jpg"
            no_images += 1 

            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
                final_image = base64.b64decode(encoded)
                f.write(final_image)
             

            predicted_class_name,prediction = predict_image(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return jsonify({'redirect_url': url_for('result', predicted_class_name=predicted_class_name,prediction= prediction,date=date,time=time)})

        return jsonify({'error': 'No image data provided'}), 400

    except Exception as e:
        logging.error(f"Error in upload_snapshot: {str(e)}")  
        return jsonify({'error': str(e)}), 500 



@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' in request.files:
        file = request.files['image']  # Get the uploaded file
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename)) 
        
      
        predicted_class_name,prediction = predict_image(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

        return jsonify({'redirect_url': url_for('result', predicted_class_name=predicted_class_name,prediction= prediction,date=date,time=time)})
    
    return jsonify({'error': 'No file data provided'}), 400


@app.route('/result')
def result():
    predicted_class_name = request.args.get('predicted_class_name') 
    prediction = float(request.args.get('prediction'))
    date=request.args.get('date')
    time=request.args.get('time')

    return render_template('result.html', predicted_class_name=predicted_class_name,prediction=prediction,date=date,time=time)




import os

def manage_attendance(predicted_student_name=None):
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    today_date = str(datetime.datetime.now()).split()[0]

    students = ['Ahmed', 'Hamza', 'Adeel', 'Muzamil']

    attendance_dict = {
        "Name": students,
        "Date": [today_date] * len(students),
        "Attendance": ["Absent"] * len(students)
    }

    # Check if file exists
    if not os.path.exists('student_attendance.csv'):
        print("File does not exist, creating new file.")
        df_existing = pd.DataFrame(columns=["Name", "Date", "Attendance"])
    else:
        try:
            df_existing = pd.read_csv('student_attendance.csv')
        except Exception as e:
            print(f"Error reading CSV: {e}")
            df_existing = pd.DataFrame(columns=["Name", "Date", "Attendance"])

    # Add default attendance if no record for today exists
    if not ((df_existing['Date'] == today_date).any()):
        df_today = pd.DataFrame(attendance_dict)
        df_existing = pd.concat([df_existing, df_today], ignore_index=True)
        df_existing.to_csv('student_attendance.csv', mode='w', index=False)
        print("Default attendance for today added.")

    # Update attendance if a student name is provided
    if predicted_student_name:
        if predicted_student_name not in df_existing['Name'].values:
            print(f"{predicted_student_name} not found in the list of students.")
            return
        df_existing.loc[
            (df_existing['Name'] == predicted_student_name) & (df_existing['Date'] == today_date), 'Attendance'
        ] = 'Present'

    # Save changes to the CSV file (overwrite)
    df_existing.to_csv('student_attendance.csv', mode='w', index=False)
    print(f"Attendance data saved. File updated.")




@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Name not provided'}), 400

        predicted_class_name = data['name']
        if not predicted_class_name:
            return jsonify({'error': 'Predicted class name is empty'}), 400

        manage_attendance(predicted_student_name=predicted_class_name)
        return jsonify({"success": True, "message": f"Attendance for {predicted_class_name} has been marked."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)