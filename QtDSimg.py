#!/usr/bin/env python
# Creates an image using DreamStudio's text-to-image
# Robert Schauer 22-Apr-2023
# With assistance from ChatGPT

import requests
import json
import os
import base64
from PyQt5 import QtWidgets, QtGui, QtCore

class TextToImageApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.engine_ids = [
            "stable-diffusion-v1",
            "stable-diffusion-v1-5",
            "stable-diffusion-512-v2-0",
            "stable-diffusion-768-v2-0",
            "stable-diffusion-512-v2-1",
            "stable-diffusion-768-v2-1",
            "stable-diffusion-xl-beta-v2-2-2",
            "stable-inpainting-v1-0",
            "stable-inpainting-512-v2-0"
        ]
        self.api_host = os.getenv("API_HOST", "https://api.stability.ai")

        # Read the API key from api_key.txt
        with open("api_key.txt", "r") as f:
            self.api_key = f.readline().strip()

        # Create UI elements
        self.prompt_label = QtWidgets.QLabel("Enter the prompt:")
        self.prompt_input = QtWidgets.QLineEdit()
        self.style_preset_label = QtWidgets.QLabel("Select a style preset:")
        self.style_preset_dropdown = QtWidgets.QComboBox()
        self.style_preset_dropdown.addItems([
            "3d-model",
            "analog-film",
            "anime",
            "cinematic",
            "comic-book",
            "digital-art",
            "enhance",
            "fantasy-art",
            "isometric",
            "line-art",
            "low-poly",
            "modeling-compound",
            "neon-punk",
            "origami",
            "photographic",
            "pixel-art",
            "tile-texture"
        ])
        self.engine_id_label = QtWidgets.QLabel("Select an engine ID:")
        self.engine_id_dropdown = QtWidgets.QComboBox()
        self.engine_id_dropdown.addItems(self.engine_ids)
        self.filename_label = QtWidgets.QLabel("Enter the filename:")
        self.filename_input = QtWidgets.QLineEdit("out.png")
        self.generate_button = QtWidgets.QPushButton("Generate")
        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setMinimumHeight(500)

        # Connect button to function that generates the image
        self.generate_button.clicked.connect(self.generate_image)

        # Set layout
        input_layout = QtWidgets.QGridLayout()
        input_layout.addWidget(self.prompt_label, 0, 0)
        input_layout.addWidget(self.prompt_input, 0, 1)
        input_layout.addWidget(self.style_preset_label, 2, 0)
        input_layout.addWidget(self.style_preset_dropdown, 2, 1)
        input_layout.addWidget(self.engine_id_label, 3, 0)
        input_layout.addWidget(self.engine_id_dropdown, 3, 1)
        input_layout.addWidget(self.filename_label, 4, 0)
        input_layout.addWidget(self.filename_input, 4, 1)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(input_layout)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        # Set window size
        self.resize(800, 600)

    def generate_image(self):
        # Get the prompt and filename from the user
        prompt = self.prompt_input.text()
        filename = self.filename_input.text()
        style_preset = self.style_preset_dropdown.currentText()
        engine_id = self.engine_id_dropdown.currentText()

        # Make the API request
        if self.api_key is None:
            raise Exception("Missing Stability API key.")

        response = requests.post(
            f"{self.api_host}/v1/generation/{engine_id}/text-to-image",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            },
            json={
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1.0
                    }
                ],
                "cfg_scale": 7,
                "clip_guidance_preset": "FAST_BLUE",
                "samples": 1,
                "style_preset": style_preset,
            },
        )

        if response.status_code != 200:
            raise Exception("Non-200 response: " + str(response.text))

        data = response.json()

        # Save the resulting image to a file
        image_data = base64.b64decode(data["artifacts"][0]["base64"])
        with open(filename, "wb") as f:
            f.write(image_data)

        # Display the resulting image
        image = QtGui.QPixmap()
        image.loadFromData(image_data)
        self.image_label.setPixmap(image.scaled(self.image_label.width(), self.image_label.height(), QtCore.Qt.KeepAspectRatio))

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    text_to_image_app = TextToImageApp()
    text_to_image_app.show()
    app.exec_()
