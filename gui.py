import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import os
import shutil


class YOLOv5Predictor:
    def __init__(self, yolov5_dir):
        self.yolov5_dir = yolov5_dir

    def predict(self, image_path, output_path):
        # Construct the command to run detect.py
        command = [
            'python', 'detect.py',
            '--weights', "runs/train/exp5/weights/best.pt",
            '--source', image_path
        ]
        # Run the command
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running YOLOv5 detection: {result.stderr}")
            return False
        return True


class App:
    def __init__(self, root, yolov5_predictor):
        self.root = root
        self.yolov5_predictor = yolov5_predictor
        self.root.title("YOLOv5 Image Predictor")

        self.label = tk.Label(root, text="Select an image to predict:")
        self.label.pack(pady=10)

        self.image_path = None
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

        self.select_button = tk.Button(root, text="Select Image", command=self.select_image)
        self.select_button.pack(pady=10)

        self.predict_button = tk.Button(root, text="Predict", command=self.predict_image, state=tk.DISABLED)
        self.predict_button.pack(pady=10)

    def select_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if self.image_path:
            self.update_image_display()
            self.predict_button.config(state=tk.NORMAL)


    def update_image_display(self):
        if self.image_path:
            image = Image.open(self.image_path)
            image.thumbnail((300, 300))  # Resize image to fit in the label
            photo = ImageTk.PhotoImage(image)

            # Clear previous image
            for widget in self.image_label.winfo_children():
                widget.destroy()

            self.image_label.config(image=photo)
            self.image_label.image = photo  # Keep a reference to prevent garbage collection

    def predict_image(self):
        if self.image_path:
            temp_dir = "temp_yolov5_output"
            success = self.yolov5_predictor.predict(self.image_path, temp_dir)
            if success:
                messagebox.showinfo("Success", "Prediction completed successfully!")
                # Optionally, you can show the results or process the output files here
            else:
                messagebox.showerror("Error", "Failed to run YOLOv5 detection.")

            # Clean up temporary directory
            # shutil.rmtree(temp_dir)

    def show_predicted_image(image):
        # 将PIL图像转换为Tkinter可以显示的格式
        photo = ImageTk.PhotoImage(image)
        # 更新Canvas上的图片
        label.config(image=photo)
        label.image = photo

if __name__ == "__main__":
    yolov5_dir = "path/to/your/yolov5/directory"  # Replace with the path to your YOLOv5 directory
    yolov5_predictor = YOLOv5Predictor(yolov5_dir)

    root = tk.Tk()
    app = App(root, yolov5_predictor)

    label = tk.Label(root)
    label.pack(fill=tk.BOTH, expand=True)
    root.mainloop()