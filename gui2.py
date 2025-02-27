import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import os
import shutil
import cv2


class YOLOv5Predictor:
    def __init__(self, yolov5_dir):
        self.yolov5_dir = yolov5_dir

    def predict(self, image_path, output_path):
        # Construct the command to run detect.py
        command = [
            'python', 'detect.py',
            '--weights', "runs/train/exp5/weights/best.pt",  # 使用权重路径
            '--source', image_path,  # 输入源路径，可以是图片、视频、或者摄像头
            '--project', output_path
        ]
        # Run the command
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running YOLOv5 detection: {result.stderr}")
            return False
        else:
            output_files = os.listdir(output_path)
            if output_files:
                return True
        return True


class App:
    def __init__(self, root, yolov5_predictor):
        self.root = root
        self.yolov5_predictor = yolov5_predictor
        self.root.title("YOLOv5 火灾烟雾检测系统")

        # 设置窗口大小
        self.root.geometry("1000x600")

        # 标题标签
        self.title_label = tk.Label(root, text="火灾烟雾检测系统", font=("Arial", 20), pady=20)
        self.title_label.pack(fill=tk.X, pady=10)

        # 创建一个框架，分为左右两部分
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧功能栏
        self.left_frame = tk.Frame(self.main_frame, width=200, bg='lightgray')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_frame.pack_propagate(False)  # 防止frame根据内容大小调整

        # 右侧显示区域
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 显示图片/视频的标签
        self.display_label = tk.Label(self.right_frame, bg='white')
        self.display_label.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)




        # 左侧按钮
        self.select_image_frame = tk.Frame(self.left_frame, bg='lightgray')  # 创建一个新的 Frame 用于按钮
        self.select_image_frame.pack(fill=tk.X, pady=70)
        self.select_image_button = tk.Button(self.left_frame, text="上传图片", command=self.select_image)
        self.select_image_button.pack(fill=tk.X, padx=20, pady=10)

        self.select_video_button = tk.Button(self.left_frame, text="上传视频", command=self.select_video)
        self.select_video_button.pack(fill=tk.X, padx=20, pady=10)

        self.start_camera_button = tk.Button(self.left_frame, text="开启摄像头", command=self.start_camera)
        self.start_camera_button.pack(fill=tk.X, padx=20, pady=10)

        self.stop_camera_button = tk.Button(self.left_frame, text="关闭摄像头", command=self.stop_camera, state=tk.DISABLED)
        self.stop_camera_button.pack(fill=tk.X, padx=20, pady=10)

        self.start_detection_button = tk.Button(self.left_frame, text="开始检测", command=self.start_detection,
                                                state=tk.DISABLED)
        self.start_detection_button.pack(fill=tk.X, padx=20, pady=10)

        self.stop_detection_button = tk.Button(self.left_frame, text="停止检测", command=self.stop_detection,
                                               state=tk.DISABLED)
        self.stop_detection_button.pack(fill=tk.X, padx=20, pady=10)

        # 管理状态的变量
        self.image_path = None
        self.video_path = None
        self.cap = None
        self.video_playing = False
        self.detection_running = False

    def select_image(self):
        # 选择图片
        self.image_path = filedialog.askopenfilename(filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.bmp")])
        if self.image_path:
            self.update_image_display()
            self.start_detection_button.config(state=tk.NORMAL)

    def select_video(self):
        # 选择视频
        self.video_path = filedialog.askopenfilename(filetypes=[("视频文件", "*.mp4;*.avi;*.mov")])
        if self.video_path:
            self.update_video_display(self.video_path)
            self.start_detection_button.config(state=tk.NORMAL)

    def update_image_display(self):
        # 更新显示区域为图片
        if self.image_path:
            image = Image.open(self.image_path)
            image.thumbnail((800, 600))  # 调整图片大小
            photo = ImageTk.PhotoImage(image)

            self.display_label.config(image=photo)
            self.display_label.image = photo

    def update_video_display(self, video_path):
        # 更新显示区域为视频
        if not self.video_playing:
            self.cap = cv2.VideoCapture(video_path)
            self.video_playing = True
            self.play_video()

    def play_video(self):
        # 播放视频
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_image = Image.fromarray(frame_rgb)
                frame_image = frame_image.resize((800, 600))  # 调整视频帧大小
                photo = ImageTk.PhotoImage(frame_image)

                self.display_label.config(image=photo)
                self.display_label.image = photo
                self.display_label.after(10, self.play_video)
            else:
                self.stop_video()

    def stop_video(self):
        # 停止视频播放
        if self.cap:
            self.cap.release()
            self.video_playing = False

    def start_camera(self):
        # 开启摄像头
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("错误", "无法打开摄像头。")
            return
        self.stop_camera_button.config(state=tk.NORMAL)
        self.start_camera_button.config(state=tk.DISABLED)
        self.start_detection_button.config(state=tk.NORMAL)
        self.capture_camera_frame()

    def stop_camera(self):
        # 关闭摄像头
        if self.cap:
            self.cap.release()
            self.cap = None
        self.stop_camera_button.config(state=tk.DISABLED)
        self.start_camera_button.config(state=tk.NORMAL)
        self.start_detection_button.config(state=tk.DISABLED)

    def capture_camera_frame(self):
        # 捕捉摄像头画面
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                # 在每帧上进行检测
                self.detect_and_update(frame)
                # 每隔10ms捕捉一次
                self.display_label.after(10, self.capture_camera_frame)
            else:
                self.stop_camera()

    def detect_and_update(self, frame):
        # 对帧进行检测并更新显示
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_pil = image_pil.resize((800, 600))  # 调整图像大小

        # 临时保存帧以便检测
        temp_path = "temp_frame.jpg"
        image_pil.save(temp_path)

        # 使用 YOLOv5 进行检测
        success = self.yolov5_predictor.predict(temp_path, "temp_yolov5_output")
        if success:
            # 重新加载并显示预测后的图像
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_image = Image.fromarray(frame_rgb)
            frame_image = frame_image.resize((800, 600))
            photo = ImageTk.PhotoImage(frame_image)

            self.display_label.config(image=photo)
            self.display_label.image = photo

        os.remove(temp_path)  # 删除临时文件

    def display_results(self, temp_dir):
        # 创建一个Tkinter窗口来显示图像
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        temp_dir = temp_dir + '/exp'
        # 假设检测后的图像文件名存储在temp_dir中，可以根据实际情况调整
        image_files = [f for f in os.listdir(temp_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        video_files = [f for f in os.listdir(temp_dir) if f.endswith(('.mp4', '.mov'))]
        if not image_files and not video_files:
            messagebox.showwarning("警告", "未找到检测后的图像文件。")
            return
        if(image_files):
            # 显示第一张图像（或者可以选择其他方式显示所有图像）
            image_path = os.path.join(temp_dir, image_files[0])
            image = cv2.imread(image_path)
            cv2.imshow("Detect Result", image)

            # 等待用户按键关闭窗口
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        if(video_files):
            video_path = os.path.join(temp_dir, video_files[0])
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                exit()
            # 逐帧读取视频
            while True:
                ret, frame = cap.read()
                if not ret:
                    # 视频读取完毕
                    break
                # 为了演示，我们仅仅显示原始帧
                cv2.imshow('Video Frame', frame)
                # 按下 'q' 键退出循环
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
            # 释放视频捕获对象并关闭所有窗口
            cap.release()
            cv2.destroyAllWindows()

    def start_detection(self):
        # 开始检测
        if self.image_path:
            # 图片检测
            self.predict_image(self.image_path)
        elif self.video_path:
            # 视频检测
            self.predict_image(self.video_path)
        elif self.cap:
            # 摄像头检测
            self.capture_camera_frame()

    def stop_detection(self):
        # 停止检测
        if self.cap:
            self.cap.release()
            self.cap = None
        self.stop_camera_button.config(state=tk.DISABLED)
        self.start_camera_button.config(state=tk.NORMAL)
        self.start_detection_button.config(state=tk.DISABLED)

    def predict_image(self, source):
        # 图片/视频/摄像头检测方法（保持不变）
        if source:
            temp_dir = "temp_yolov5_output"
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)
            success = self.yolov5_predictor.predict(source, temp_dir)
            if success:
                messagebox.showinfo("成功", "检测完成！")
                # 可选的：显示检测结果或处理输出文件
                self.display_results(temp_dir)
            else:
                messagebox.showerror("错误", "检测失败。")
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    yolov5_dir = "yolov5-master"  # 替换为你的 YOLOv5 目录路径
    yolov5_predictor = YOLOv5Predictor(yolov5_dir)

    root = tk.Tk()
    app = App(root, yolov5_predictor)

    root.mainloop()