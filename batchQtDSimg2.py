#!/usr/bin/env python
# Creates an image using DreamStudio's text-to-image
# Robert Schauer 25-Apr-2023
# With assistance from ChatGPT

import requests
import json
import os
import base64
from qtpy import QtWidgets, QtGui, QtCore
from qtpy.QtWidgets import QSpinBox

class TextToImageApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("Batch DreamStudio Image Generator")

        # Set window dimensions
        self.setGeometry(100, 100, 900, 1200)

        self.engine_id = "stable-diffusion-512-v2-1"
        self.api_host = os.getenv("API_HOST", "https://api.stability.ai")

        # Read the API key from api_key.txt
        with open("api_key.txt", "r") as f:
            self.api_key = f.readline().strip()

        # Create UI elements
        self.filename_label = QtWidgets.QLabel("No file selected.")
        self.filename_label.setAlignment(QtCore.Qt.AlignCenter)
        self.filename_label.setMinimumHeight(50)

        self.file_list_widget = QtWidgets.QListWidget()
        self.file_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.file_list_widget.setFixedHeight(200)  # Set fixed height

        self.browse_button = QtWidgets.QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)

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
        self.engine_id_dropdown.addItems([
            "stable-diffusion-v1",
            "stable-diffusion-v1-5",
            "stable-diffusion-512-v2-0",
            "stable-diffusion-768-v2-0",
            "stable-diffusion-512-v2-1",
            "stable-diffusion-768-v2-1",
            "stable-diffusion-xl-beta-v2-2-2",
            "stable-inpainting-v1-0",
            "stable-inpainting-512-v2-0"
        ])

        self.output_dir_label = QtWidgets.QLabel("Output directory:")
        self.output_dir_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.output_dir_textbox = QtWidgets.QLineEdit()
        self.output_dir_textbox.setText(os.getcwd())

        self.output_dir_button = QtWidgets.QPushButton("Select")
        self.output_dir_button.clicked.connect(self.select_output_dir)

        self.generate_button = QtWidgets.QPushButton("Generate")

        self.image_scroll_area = QtWidgets.QScrollArea()
        self.image_scroll_area.setWidgetResizable(True)
        self.image_scroll_area_widget = QtWidgets.QWidget()
        self.image_scroll_area_layout = QtWidgets.QVBoxLayout(self.image_scroll_area_widget)
        self.image_scroll_area.setWidget(self.image_scroll_area_widget)

        self.status_label = QtWidgets.QLabel()
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)

        # Add a numbering scheme checkbox
        self.numbering_checkbox = QtWidgets.QCheckBox("Enable numbering scheme")
        self.numbering_checkbox.setChecked(True)

        # Add a new label and spin box for specifying the number of iterations
        self.iterations_label = QtWidgets.QLabel("Number of iterations:")
        self.iterations_spin_box = QSpinBox()
        self.iterations_spin_box.setMinimum(1)
        self.iterations_spin_box.setMaximum(9999)
        self.iterations_spin_box.setValue(1)

        # Add a new label and spin box for specifying cfg_scale
        self.cfg_scale_label = QtWidgets.QLabel("cfg_scale:")
        self.cfg_scale_spin_box = QSpinBox()
        self.cfg_scale_spin_box.setMinimum(1)
        self.cfg_scale_spin_box.setMaximum(35)
        self.cfg_scale_spin_box.setValue(7)

        # Connect button to function that generates the image
        self.generate_button.clicked.connect(self.generate_image)

        # Set layout
        input_layout = QtWidgets.QGridLayout()
        input_layout.addWidget(self.browse_button, 0, 0)
        input_layout.addWidget(self.filename_label, 0, 1)
        input_layout.addWidget(self.style_preset_label, 1, 0)
        input_layout.addWidget(self.style_preset_dropdown, 1, 1)
        input_layout.addWidget(self.engine_id_label, 2, 0)
        input_layout.addWidget(self.engine_id_dropdown, 2, 1)
        input_layout.addWidget(self.numbering_checkbox, 3, 0)  # Add numbering scheme checkbox
        input_layout.addWidget(self.iterations_label, 4, 0)
        input_layout.addWidget(self.iterations_spin_box, 4, 1)
        input_layout.addWidget(self.cfg_scale_label, 5, 0)  # Add cfg_scale label
        input_layout.addWidget(self.cfg_scale_spin_box, 5, 1)  # Add cfg_scale spin box

        # Set the default value for the style_preset_dropdown
        default_style_preset = "enhance"
        default_style_preset_index = self.style_preset_dropdown.findText(default_style_preset)
        if default_style_preset_index != -1:
            self.style_preset_dropdown.setCurrentIndex(default_style_preset_index)

        # Set the default value for the engine_id_dropdown
        default_engine_id = "stable-diffusion-512-v2-1"
        default_engine_id_index = self.engine_id_dropdown.findText(default_engine_id)
        if default_engine_id_index != -1:
            self.engine_id_dropdown.setCurrentIndex(default_engine_id_index)

        output_layout = QtWidgets.QHBoxLayout()
        output_layout.addWidget(self.output_dir_label)
        output_layout.addWidget(self.output_dir_textbox)
        output_layout.addWidget(self.output_dir_button)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.generate_button)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.file_list_widget)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.image_scroll_area)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)
        
        # Center the window on the screen
        self.center_on_screen()
        
    def center_on_screen(self):
        screen_geometry = QtWidgets.QApplication.desktop().screenGeometry()
        window_geometry = self.frameGeometry()
        center = screen_geometry.center()
        window_geometry.moveCenter(center)
        self.move(window_geometry.topLeft())

    def browse_file(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setNameFilter("Text files (*.txt)")
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if file_dialog.exec_():
            filename = file_dialog.selectedFiles()[0]
            self.filename_label.setText(filename)
            self.file_list_widget.clear()
            with open(filename, 'r') as f:
                for line in f:
                    self.file_list_widget.addItem(line.strip())

    def select_output_dir(self):
        dir_dialog = QtWidgets.QFileDialog(self)
        dir_dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        if dir_dialog.exec_():
            self.output_dir_textbox.setText(dir_dialog.selectedFiles()[0])

    def generate_image(self):
        # Get the prompt list, style_preset, and engine_id from the user
        filename = self.filename_label.text()
        style_preset = self.style_preset_dropdown.currentText()
        engine_id = self.engine_id_dropdown.currentText()

        # Set the default width and height based on the engine_id
        if '768' in engine_id:
            width = 768
            height = 768
        else:
            width = 512
            height = 512

        # Read the contents of the file into a list of prompts
        prompt_list = []
        with open(filename, 'r') as f:
            for line in f:
                prompt = line.strip()
                prompt_filename = prompt.replace(" ", "_") + ".png"
                prompt_list.append({
                    "text": prompt,
                    "filename": prompt_filename,
                    "width": width,
                    "height": height,
                })

        output_dir = self.output_dir_textbox.text()

        # Get the number of iterations from the spin box
        iterations = self.iterations_spin_box.value()

        # Get the cfg_scale from the spin box
        cfg_scale = self.cfg_scale_spin_box.value()
        
        # Initialize the numbering counter
        numbering_counter = 1

        # Iterate through the prompt list the specified number of times
        for _ in range(iterations):
            # Make the API request for each prompt
            for prompt in prompt_list:
                self.status_label.setText(f"Generating image for prompt '{prompt['text']}'...")

                QtWidgets.QApplication.processEvents()

                response = requests.post(
                    f"{self.api_host}/v1/generation/{engine_id}/text-to-image",
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "text_prompts": [prompt],
                        "cfg_scale": cfg_scale,
                        "clip_guidance_preset": "FAST_BLUE",
                        "samples": 1,
                        "style_preset": style_preset,
                        "width": width,
                        "height": height,
                    },
                )

                if response.status_code != 200:
                    raise Exception("Non-200 response: " + str(response.text))

                data = response.json()

                # Save the resulting image to a file
                image_data = base64.b64decode(data["artifacts"][0]["base64"])
                output_path = os.path.join(output_dir, prompt['filename'])

                # Check if the numbering scheme is enabled
                if self.numbering_checkbox.isChecked():
                    # Prepend the sequential number to the filename
                    filename_without_ext, ext = os.path.splitext(prompt['filename'])
                    output_path = os.path.join(output_dir, f"{numbering_counter:04}_{filename_without_ext}{ext}")

                    # Increment the numbering counter
                    numbering_counter += 1

                # Check if the file already exists, and append a sequential number if it does
                i = 1
                while os.path.exists(output_path):
                    filename_without_ext, ext = os.path.splitext(prompt['filename'])
                    output_path = os.path.join(output_dir, f"{filename_without_ext}_{i:03}{ext}")
                    i += 1

                with open(output_path, "wb") as f:
                    f.write(image_data)

                # Display the resulting image
                image_label = QtWidgets.QLabel()
                image = QtGui.QPixmap()
                image.loadFromData(image_data)
                image_label.setPixmap(image)
                self.image_scroll_area_layout.addWidget(image_label)
                self.image_scroll_area_widget.adjustSize()
                QtWidgets.QApplication.processEvents()

                # Scroll to the bottom of the image scroll area
                self.image_scroll_area.verticalScrollBar().setValue(self.image_scroll_area.verticalScrollBar().maximum())

        # Display status message
        self.status_label.setText("Done!")
                
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    text_to_image_app = TextToImageApp()
    text_to_image_app.show()
    app.exec_()
