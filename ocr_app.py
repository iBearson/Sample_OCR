import os
import cv2
import pytesseract
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # Import the ttk module for styled widgets

# Function to extract image ID from file name
def extract_image_id(filename):
    return os.path.splitext(os.path.basename(filename))[0]

# Function to load OCR text from a saved .txt file
def load_ocr_text(image_id, ocr_outputs_dir='dataset/ocr_outputs/'):
    ocr_file_path = os.path.join(ocr_outputs_dir, f"{image_id}.txt")
    if os.path.exists(ocr_file_path):
        with open(ocr_file_path, 'r') as file:
            return file.read()
    else:
        return "No OCR text found."

# Function to load XML annotations
def load_annotations(xml_file):
    annotations = {}
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for image in root.findall(".//image"):
        image_id = image.get("id")
        annotations[image_id] = {}
        for box in image.findall(".//box"):
            label = box.get("label")
            text = box.find("attribute").text.strip() if box.find("attribute") is not None else ""
            annotations[image_id][label] = text
    return annotations

# Tkinter-based prototype
class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR and Annotation Display")
        self.root.geometry("600x450")  # Set the size of the window

        # Styling
        primary_color = "#4a7a8c"  # Blue-green primary color
        
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f3f4f6")  # Light gray background
        self.style.configure("TButton", background=primary_color, foreground="#333333", font=('Helvetica', 10, 'bold'))  # Blue-green buttons with white text
        self.style.configure("TLabel", background="#f3f4f6", foreground="#333333", font=('Helvetica', 10))  # Dark text on light background for labels
        self.style.configure("Treeview", background="#ffffff", foreground="#333333", fieldbackground="#ffffff", font=('Helvetica', 10))  # White background for the treeview with dark text
        self.style.configure("Treeview.Heading", foreground="#333333", background=primary_color, font=('Helvetica', 10, 'bold'))  # Blue-green headings with white text
        
        # Remove hover effect on table header
        self.style.map('Treeview.Heading', relief=[('active', 'flat')])

        # Customize the Treeview Highlight / Border when selected
        self.style.map('Treeview', background=[('selected', primary_color)], foreground=[('selected', '#ffffff')])
        self.style.layout("Treeview.Item", [('Treeitem.padding', {'sticky': 'nswe'})])  # Padding for treeview items
        self.style.configure("Treeview.Item", background="#ffffff", foreground="#333333", font=('Helvetica', 10))

        # Frame for upload button
        self.upload_frame = ttk.Frame(self.root)
        self.upload_frame.pack(padx=10, pady=10, fill='x', expand=True)

        # Upload button
        self.upload_button = ttk.Button(self.upload_frame, text="Upload Image", command=self.upload_action)
        self.upload_button.pack(pady=10, padx=10)

        # Frame for displaying OCR text and annotations
        self.display_frame = ttk.Frame(self.root)
        self.display_frame.pack(padx=10, pady=10, fill='both', expand=True)

    def upload_action(self):
        filename = filedialog.askopenfilename()
        if filename:
            image_id = extract_image_id(filename)
            ocr_text = load_ocr_text(image_id)
            annotations = load_annotations('dataset/annotations.xml')
            self.display_text_and_annotations(image_id, ocr_text, annotations)

    def display_text_and_annotations(self, image_id, ocr_text, annotations):
        # Clear previous display
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        # Display OCR text
        ocr_label = ttk.Label(self.display_frame, text="OCR Text:")
        ocr_label.pack(anchor='nw', pady=(10, 0))
        ocr_text_widget = tk.Text(self.display_frame, height=10, width=75)
        ocr_text_widget.insert(tk.END, ocr_text)
        ocr_text_widget.pack(pady=(0, 10))

        # Display annotations in a table format using Treeview
        if image_id in annotations:
            annotation_label = ttk.Label(self.display_frame, text="Processed:")
            annotation_label.pack(anchor='nw', pady=(10, 0))

            columns = ('Label', 'Text')
            annotation_table = ttk.Treeview(self.display_frame, columns=columns, show='headings')
            annotation_table.heading('Label', text='Label')
            annotation_table.heading('Text', text='Text')
            for label, text in annotations[image_id].items():
                annotation_table.insert('', tk.END, values=(label, text))
            annotation_table.pack(fill='x', expand=True)
        else:
            messagebox.showinfo("No Annotations", "No annotations found for this image.")

if __name__ == "__main__":
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()
