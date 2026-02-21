# /photo_editor/batch_window.py
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
from PIL import Image

class BatchWindow(ctk.CTkToplevel):
    """
    نافذة منبثقة لإدارة عملية المعالجة الدفعية (إضافة شعار).
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("المعالجة الدفعية - إضافة شعار")
        self.geometry("550x500")
        self.transient(parent)
        self.grab_set()

        self.setup_ui()

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # --- اختيار مجلد الصور ---
        ctk.CTkLabel(main_frame, text="1. اختر مجلد الصور المصدر:").pack(anchor=tk.W, pady=(10, 0))
        folder_frame = ctk.CTkFrame(main_frame)
        folder_frame.pack(fill=tk.X, pady=5)
        self.folder_path = tk.StringVar()
        folder_entry = ctk.CTkEntry(folder_frame, textvariable=self.folder_path)
        folder_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ctk.CTkButton(folder_frame, text="اختيار...", command=self.select_folder).pack(side=tk.LEFT)
        
        # --- اختيار صورة الشعار ---
        ctk.CTkLabel(main_frame, text="2. اختر صورة الشعار (Watermark):").pack(anchor=tk.W, pady=(10, 0))
        watermark_frame = ctk.CTkFrame(main_frame)
        watermark_frame.pack(fill=tk.X, pady=5)
        self.watermark_path = tk.StringVar()
        watermark_entry = ctk.CTkEntry(watermark_frame, textvariable=self.watermark_path)
        watermark_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ctk.CTkButton(watermark_frame, text="اختيار...", command=self.select_watermark).pack(side=tk.LEFT)
        
        # --- اختيار موضع الشعار ---
        ctk.CTkLabel(main_frame, text="3. اختر موضع الشعار:").pack(anchor=tk.W, pady=(10, 0))
        self.position_var = tk.StringVar(value="bottom_right")
        positions_frame = ctk.CTkFrame(main_frame)
        positions_frame.pack(fill=tk.X, pady=5)
        positions = [("أعلى اليسار", "top_left"), ("أعلى اليمين", "top_right"), ("أسفل اليسار", "bottom_left"), ("أسفل اليمين", "bottom_right")]
        for i, (text, value) in enumerate(positions):
            ctk.CTkRadioButton(positions_frame, text=text, variable=self.position_var, value=value).pack(side=tk.LEFT, padx=10, pady=5, expand=True)
        
        # --- اختيار مجلد الحفظ ---
        ctk.CTkLabel(main_frame, text="4. اختر مجلد لحفظ الصور الجديدة:").pack(anchor=tk.W, pady=(10, 0))
        save_frame = ctk.CTkFrame(main_frame)
        save_frame.pack(fill=tk.X, pady=5)
        self.save_path = tk.StringVar()
        save_entry = ctk.CTkEntry(save_frame, textvariable=self.save_path)
        save_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ctk.CTkButton(save_frame, text="اختيار...", command=self.select_save_folder).pack(side=tk.LEFT)
        
        # --- شريط التقدم والبدء ---
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(pady=20, fill=tk.X)
        self.progress_bar.set(0)
        self.progress_label = ctk.CTkLabel(main_frame, text="في انتظار البدء...")
        self.progress_label.pack()
        
        self.start_button = ctk.CTkButton(main_frame, text="بدء المعالجة", command=self.start_processing)
        self.start_button.pack(pady=10, ipady=10)
        
    def select_folder(self):
        folder = filedialog.askdirectory(title="اختر مجلد الصور")
        if folder: self.folder_path.set(folder)
            
    def select_watermark(self):
        # هذا هو السطر الذي قمنا بإصلاحه سابقاً
        file_path = filedialog.askopenfilename(title="اختر صورة الشعار", filetypes=[("ملفات الصور", "*.png *.jpg *.jpeg *.bmp")])
        if file_path: self.watermark_path.set(file_path)
            
    def select_save_folder(self):
        folder = filedialog.askdirectory(title="اختر مجلد الحفظ")
        if folder: self.save_path.set(folder)
            
    def start_processing(self):
        folder = self.folder_path.get()
        watermark_file = self.watermark_path.get()
        save_folder = self.save_path.get()
        if not all([folder, watermark_file, save_folder]):
            messagebox.showerror("خطأ", "الرجاء ملء جميع الحقول", parent=self)
            return
        
        self.start_button.configure(state="disabled", text="جاري المعالجة...")
        # تشغيل العملية في خيط منفصل لتجنب تجميد الواجهة
        thread = threading.Thread(target=self.process_images_thread, args=(folder, watermark_file, save_folder), daemon=True)
        thread.start()
        
    def process_images_thread(self, folder, watermark_file, save_folder):
        try:
            watermark = Image.open(watermark_file).convert('RGBA')
            image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
            image_files = [f for f in os.listdir(folder) if f.lower().endswith(image_extensions)]
            
            if not image_files:
                messagebox.showwarning("تحذير", "لا توجد صور في المجلد المحدد.", parent=self)
                self.start_button.configure(state="normal", text="بدء المعالجة")
                return

            total_images = len(image_files)
            position_choice = self.position_var.get()
            
            for i, filename in enumerate(image_files):
                self.progress_label.configure(text=f"جاري معالجة: {filename} ({i+1}/{total_images})")
                
                image_path = os.path.join(folder, filename)
                with Image.open(image_path).convert('RGBA') as image:
                    # تغيير حجم الشعار ليكون مناسباً (مثلاً 15% من عرض الصورة)
                    wm_width = int(image.size[0] * 0.15)
                    wm_height = int(watermark.size[1] * (wm_width / watermark.size[0]))
                    wm_resized = watermark.resize((wm_width, wm_height), Image.Resampling.LANCZOS)
                    
                    margin = 20
                    positions = {
                        "top_left": (margin, margin),
                        "top_right": (image.size[0] - wm_width - margin, margin),
                        "bottom_left": (margin, image.size[1] - wm_height - margin),
                        "bottom_right": (image.size[0] - wm_width - margin, image.size[1] - wm_height - margin)
                    }
                    pos = positions.get(position_choice)
                    
                    # لصق الشعار على الصورة
                    image.paste(wm_resized, pos, wm_resized)
                    
                    # حفظ الصورة (مع تحويلها لـ RGB إذا كانت ستحفظ كـ JPG)
                    save_path = os.path.join(save_folder, f"marked_{filename}")
                    final_image = image.convert('RGB') if save_path.lower().endswith('.jpg') else image
                    final_image.save(save_path)

                progress = (i + 1) / total_images
                self.progress_bar.set(progress)
            
            messagebox.showinfo("نجاح", f"تمت معالجة {total_images} صورة بنجاح.", parent=self)
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}", parent=self)
        finally:
            # التأكد من أن تدمير النافذة يحدث في الخيط الرئيسي
            self.after(0, self.destroy)
