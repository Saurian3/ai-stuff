#!/usr/bin/env python
# Creates an image using deepai.org's text-to-image
# Robert Schauer 22-Apr-2023
# With assistance from ChatGPT


import sys
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QGraphicsScene, QGraphicsView
from PyQt5.QtGui import QPixmap

class Text2ImgGUI(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the UI
        self.initUI()

    def initUI(self):
        # Set up layout
        main_layout = QVBoxLayout()

        # Image description
        image_desc_layout = QHBoxLayout()
        image_desc_label = QLabel("Image description:")
        self.image_desc_input = QLineEdit()
        image_desc_layout.addWidget(image_desc_label)
        image_desc_layout.addWidget(self.image_desc_input)

        # Negative prompt
        neg_prompt_layout = QHBoxLayout()
        neg_prompt_label = QLabel("Negative prompt:")
        self.neg_prompt_input = QLineEdit()
        neg_prompt_layout.addWidget(neg_prompt_label)
        neg_prompt_layout.addWidget(self.neg_prompt_input)

        # Filename
        filename_layout = QHBoxLayout()
        filename_label = QLabel("Filename:")
        self.filename_input = QLineEdit()
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_file)
        filename_layout.addWidget(filename_label)
        filename_layout.addWidget(self.filename_input)
        filename_layout.addWidget(browse_button)

        # Create image button
        create_image_button = QPushButton("Create Image")
        create_image_button.clicked.connect(self.create_image_button_clicked)

        # Image display
        self.image_scene = QGraphicsScene()
        self.image_view = QGraphicsView(self.image_scene)

        # Add layouts and widgets to main layout
        main_layout.addLayout(image_desc_layout)
        main_layout.addLayout(neg_prompt_layout)
        main_layout.addLayout(filename_layout)
        main_layout.addWidget(create_image_button)
        main_layout.addWidget(self.image_view)

        self.setLayout(main_layout)
        self.resize(800, 600)
        self.setWindowTitle("Text to Image")

    def browse_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.xpm *.jpg)")
        if file_name:
            self.filename_input.setText(file_name)

    def create_image_button_clicked(self):
        # Get input values
        image_description = self.image_desc_input.text()
        negative_prompt = self.neg_prompt_input.text()
        filename = self.filename_input.text()

        # Read API key from file
        try:
            with open("api_key.txt", "r") as api_key_file:
                api_key = api_key_file.read().strip()
        except FileNotFoundError:
            print("Error: api_key.txt not found")
            return

        # Check for required inputs
        if not image_description or not negative_prompt or not filename:
            print("Error: Please provide all required inputs")
            return

        # Call the create_image function
        self.create_image(image_description, negative_prompt, filename, api_key)

        # Display the created image
        self.display_image(filename)

    def create_image(self, image_description, negative_prompt, filename, api_key):
        # Create the request
        request = requests.post("https://api.deepai.org/api/text2img",
                                data={"text": image_description, "negative_prompt": negative_prompt, "grid_size":"1"},
                                headers={'api-key':api_key})

        # Check the response status code
        if request.status_code == 200:
            # Get the image data
            image_url = request.json()["output_url"]

            # Save the image to a file
            with open(filename, "wb") as f:
                f.write(requests.get(image_url).content)

            print("Image created successfully!")
        else:
            print("Error creating image: {}".format(request.status_code))

    def display_image(self, filename):
        # Load the image
        image = QPixmap(filename)

        # Add the image to the scene and display it in the view
        self.image_scene.clear()
        self.image_scene.addPixmap(image)
        self.image_view.setScene(self.image_scene)
        self.image_view.fitInView(self.image_scene.itemsBoundingRect(), mode=Qt.KeepAspectRatio)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = Text2ImgGUI()
    gui.show()
    sys.exit(app.exec_())