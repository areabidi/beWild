#POST request: The client sends data (like a form with an uploaded file) to the server
#GET request: The client (user’s browser) asks the server for a page or data.


from flask import Flask, render_template, request, redirect
import requests
from werkzeug.utils import secure_filename
import os
# Create Flask app instance
app = Flask(__name__)

# Configure folder to save uploaded images temporarily
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create the upload folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Your Roboflow API key and model ID
API_KEY = "DTV3jifVK7fHJGNBQsHO"
MODEL_ID = "edible-and-inedible-berries/21"

# Define the main route for both GET (show page) and POST (upload image)
@app.route('/', methods=['GET', 'POST'])
def index():
    result = "Please upload a picture of a berry" #None  # Initialize result message
    if request.method == 'POST': 
             # If form is submitted
              # Check if 'image' is in the form submission
            # Check if 'image' file part is present in request
            #our HTML form didn't include the file input correctly.
            #The name="image" attribute is missing from your <input> tag. or JavaScript code messed with the form before sending.
            if 'image' not in request.files:
              result = "⚠️ No image uploaded. Please select a file."
              return render_template("index.html", result=result)
           # return redirect(request.url)  # Redirect if no file part
        
            file = request.files['image']  # Get the uploaded file

        # If user submitted form without selecting a file
         # Check if a file was actually selected
            if file.filename == '':
                result = "⚠️ No file selected. Please choose an image."
                return render_template("index.html", result=result)
            #return redirect(request.url)  # Redirect back to form
             # Optional: Save or process image here...

            #result = "✅ Image uploaded successfully!"
            #return render_template("index.html", result=result)
            # ✅ If everything is okay, continue processing the image:

            # Sanitize the filename to avoid security issues
            filename = secure_filename(file.filename)
            # Create full path for saving the file
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Save the file locally
            file.save(filepath)

            # Open the saved image file in binary read mode to send to API
            with open(filepath, "rb") as img_file:
                # Call Roboflow API with POST request, passing API key and image
                response = requests.post(
                    f"https://detect.roboflow.com/{MODEL_ID}",
                    params={"api_key": API_KEY},
                    files={"file": img_file}
                )

            # Parse JSON response from API
            data = response.json()
            print(data)

            # Extract predictions list (detected berries)
            predictions = data.get("predictions", [])

            if predictions:  # If there are detected berries
                # List of classes considered edible
                edible_classes = ["Strawberry", "Blueberry", "Raspberry", "Blackberry"]
                # Extract class names from detected predictions
                detected_classes = [p["class"] for p in predictions]
                # Check if any detected class is edible
                edible_detected = any(cls in edible_classes for cls in detected_classes)

                # Set result message based on detection
                if edible_detected:
                    result = "Edible berry detected!"
                else:
                    result = "Non-edible or toxic berry detected!"
            else:
                # No berries detected at all
                result = "No berries detected in the image."

            # Render the HTML template, passing the result message
            return render_template('index.html', result=result)
     # <-- This is the fix: add a return for GET requests
    return render_template('index.html', result=result)   

# Run the app if this file is executed directly
if __name__ == '__main__':
    app.run(debug=True)