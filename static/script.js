const video = document.getElementById('camera-feed');
const canvas = document.getElementById('snapshotCanvas');
const context = canvas.getContext('2d');
const toggleCameraButton = document.getElementById('toggle-camera');
const snapshotButton = document.getElementById('snapshot-button');
const attendanceButton = document.getElementById('xyz');

let stream;

toggleCameraButton.addEventListener('click', async () => {
    if (!stream) {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            video.style.visibility = 'visible';
            snapshotButton.disabled = false;
            toggleCameraButton.textContent = 'Close Camera';
        } catch (error) {
            console.error('Error accessing camera: ', error);
        }
    } else {
        stream.getTracks().forEach(track => track.stop());
        video.style.visibility = 'hidden';
        toggleCameraButton.textContent = 'Open Camera';
        snapshotButton.disabled = true;
        stream = null;
    }
});

snapshotButton.addEventListener('click', () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/png');
    uploadSnapshot(imageData);
});

function uploadSnapshot(imageData) {
    console.log("Uploading snapshot..."); 

    fetch('/upload_snapshot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageData })
    })
    .then(response => {
        if (!response.ok) {
            console.error('Response not OK:', response);  
            throw new Error('Failed to upload snapshot.');
        }
        return response.json();  
    })
    .then(data => {
        if (data.redirect_url) {
            console.log('Redirecting to:', data.redirect_url); 
            
            window.location.href = data.redirect_url;
        } else {
            console.error('Error in response data:', data); 
            alert('Error: Unable to process the image.');
        }
    })
    .catch(error => {
        console.error('Error uploading snapshot:', error); 
        alert('Error: ' + error.message);
    });
}



document.getElementById('upload-form').addEventListener('submit', function (event) {
    event.preventDefault();
    const formData = new FormData(this);

    const uploadButton = document.getElementById('upload-button');
    uploadButton.disabled = true;
    uploadButton.textContent = 'Uploading...';

    fetch('/upload_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        } else {
            console.error('Server error:', data.error); 
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error uploading snapshot:', error);
        alert('Error: ' + error.message);
    });
    
});





// attendanceButton.addEventListener('click', () => {
//     console.log("Button clicked");
//     const predicted_class_name = "{{ predicted_class_name }}";
//     console.log("Predicted class name:", predicted_class_name);

//     // Check if face is detected and predicted class name is valid
//     if (!predicted_class_name || predicted_class_name === 'Unknown' || predicted_class_name.includes('No face detected')) {
//         alert('Cannot mark attendance for an unknown person or no face detected.');
//         return;
//     }

//     // Send the name to the server to mark attendance
//     fetch('/mark_attendance', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ name: predicted_class_name })
//     })
//     .then(response => response.json())
//     .then(data => {
//         console.log(data);
//         if (data.message) {
//             alert(data.message);  // Show success message from server
//         } else {
//             alert('Error: ' + (data.error || 'Could not mark attendance.'));
//         }
//     })
//     .catch(error => {
//         console.error('Error marking attendance:', error);
//         alert('Error: Unable to mark attendance.');
//     });
// });

function markAttendance() {
    const predicted_class_name = document.getElementById('predicted_class_name').value;
    console.log('Predicted Class Name:', predicted_class_name);

    if (!predicted_class_name || predicted_class_name === 'Unknown' || predicted_class_name.includes('No face detected')) {
        alert('Cannot mark attendance for an unknown person or no face detected.');
        return;
    }

    fetch('/mark_attendance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: predicted_class_name,
            status: "marked",
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Attendance marked successfully!");
        } else {
            alert("Error: " + (data.message || "Could not mark attendance."));
        }
    })
    .catch(error => {
        alert("Error marking attendance: " + error);
    });
}

