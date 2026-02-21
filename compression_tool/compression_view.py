# /compression_tool/compression_view.py
import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

class CompressionView:
    """
    فئة الـ View لأداة الضغط.
    مسؤولة عن إنشاء كل التبويبات والعناصر الرسومية.
    """
    def __init__(self, parent):
        # تم تغيير Notebook إلى CTkTabview ليتوافق مع التصميم
        self.notebook = ctk.CTkTabview(parent)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.setup_compression_tab()
        self.setup_image_compression_tab()
        self.setup_audio_compression_tab()
        self.setup_history_tab()

    def setup_compression_tab(self):
        tab = self.notebook.add("ضغط الملفات")
        
        file_frame = ctk.CTkFrame(tab)
        file_frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(file_frame, text="الملفات والمجلدات المضافة").pack()
        
        self.file_listbox = tk.Listbox(file_frame, height=8, selectmode=tk.EXTENDED, bg="#2b2b2b", fg="white", borderwidth=0, highlightthickness=0)
        self.file_listbox.pack(pady=5, padx=5, fill="both", expand=True)
        
        btn_frame = ctk.CTkFrame(file_frame)
        btn_frame.pack(pady=5)
        self.add_files_btn = ctk.CTkButton(btn_frame, text="إضافة ملفات")
        self.add_files_btn.pack(side="left", padx=5)
        self.add_folder_btn = ctk.CTkButton(btn_frame, text="إضافة مجلد")
        self.add_folder_btn.pack(side="left", padx=5)
        self.remove_btn = ctk.CTkButton(btn_frame, text="إزالة المحدد")
        self.remove_btn.pack(side="left", padx=5)
        self.clear_btn = ctk.CTkButton(btn_frame, text="مسح الكل")
        self.clear_btn.pack(side="left", padx=5)
        
        settings_frame = ctk.CTkFrame(tab)
        settings_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(settings_frame, text="مستوى الضغط:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.compression_level = ctk.CTkComboBox(settings_frame, values=["عادي", "عالي", "أقصى ضغط"])
        self.compression_level.set("عالي")
        self.compression_level.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(settings_frame, text="كلمة مرور:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.password = ctk.CTkEntry(settings_frame, show="*")
        self.password.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        exec_frame = ctk.CTkFrame(tab)
        exec_frame.pack(pady=10, padx=10, fill="x")
        
        self.compress_btn = ctk.CTkButton(exec_frame, text="بدء الضغط")
        self.compress_btn.pack(side="left", padx=10)
        self.cancel_btn = ctk.CTkButton(exec_frame, text="إلغاء", state="disabled")
        self.cancel_btn.pack(side="left", padx=10)
        
        self.progress = ctk.CTkProgressBar(exec_frame)
        self.progress.pack(side="left", fill="x", expand=True, padx=10)
        self.progress.set(0)
        
        self.status_label = ctk.CTkLabel(tab, text="جاهز")
        self.status_label.pack(pady=5)
        self.size_info_label = ctk.CTkLabel(tab, text="الحجم: 0 MB | الملفات: 0")
        self.size_info_label.pack(pady=5)

    def setup_image_compression_tab(self):
        tab = self.notebook.add("ضغط الصور")
        
        image_frame = ctk.CTkFrame(tab)
        image_frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(image_frame, text="الصور المضافة").pack()
        
        self.image_listbox = tk.Listbox(image_frame, height=8, selectmode=tk.EXTENDED, bg="#2b2b2b", fg="white", borderwidth=0, highlightthickness=0)
        self.image_listbox.pack(pady=5, padx=5, fill="both", expand=True)
        
        btn_frame = ctk.CTkFrame(image_frame)
        btn_frame.pack(pady=5)
        self.add_images_btn = ctk.CTkButton(btn_frame, text="إضافة صور")
        self.add_images_btn.pack(side="left", padx=5)
        self.remove_image_btn = ctk.CTkButton(btn_frame, text="إزالة المحدد")
        self.remove_image_btn.pack(side="left", padx=5)
        self.clear_images_btn = ctk.CTkButton(btn_frame, text="مسح الكل")
        self.clear_images_btn.pack(side="left", padx=5)
        
        settings_frame = ctk.CTkFrame(tab)
        settings_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(settings_frame, text="جودة الصور (0-100):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.image_quality_slider = ctk.CTkSlider(settings_frame, from_=0, to=100)
        self.image_quality_slider.set(85)
        self.image_quality_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(settings_frame, text="تنسيق الإخراج:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.image_format = ctk.CTkComboBox(settings_frame, values=["JPG", "PNG", "WEBP", "نفس التنسيق الأصلي"])
        self.image_format.set("JPG")
        self.image_format.grid(row=1, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(settings_frame, text="تغيير الحجم (%):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.image_resize_slider = ctk.CTkSlider(settings_frame, from_=10, to=100)
        self.image_resize_slider.set(100)
        self.image_resize_slider.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        self.compress_images_btn = ctk.CTkButton(tab, text="بدء ضغط الصور")
        self.compress_images_btn.pack(pady=15)
        self.image_info_label = ctk.CTkLabel(tab, text="الصور: 0 | الحجم: 0 MB")
        self.image_info_label.pack(pady=5)

    def setup_audio_compression_tab(self):
        tab = self.notebook.add("ضغط الصوت")
        
        audio_frame = ctk.CTkFrame(tab)
        audio_frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(audio_frame, text="ملفات الصوت المضافة").pack()
        
        self.audio_listbox = tk.Listbox(audio_frame, height=8, selectmode=tk.EXTENDED, bg="#2b2b2b", fg="white", borderwidth=0, highlightthickness=0)
        self.audio_listbox.pack(pady=5, padx=5, fill="both", expand=True)
        
        btn_frame = ctk.CTkFrame(audio_frame)
        btn_frame.pack(pady=5)
        self.add_audio_btn = ctk.CTkButton(btn_frame, text="إضافة ملفات صوت")
        self.add_audio_btn.pack(side="left", padx=5)
        self.remove_audio_btn = ctk.CTkButton(btn_frame, text="إزالة المحدد")
        self.remove_audio_btn.pack(side="left", padx=5)
        self.clear_audio_btn = ctk.CTkButton(btn_frame, text="مسح الكل")
        self.clear_audio_btn.pack(side="left", padx=5)
        
        settings_frame = ctk.CTkFrame(tab)
        settings_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(settings_frame, text="جودة الصوت:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.audio_quality = ctk.CTkComboBox(settings_frame, values=["عالية (غير مضغوط)", "متوسطة", "منخفضة"])
        self.audio_quality.set("متوسطة")
        self.audio_quality.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(settings_frame, text="معدل العينة:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.sample_rate = ctk.CTkComboBox(settings_frame, values=["44100 Hz", "22050 Hz", "11025 Hz"])
        self.sample_rate.set("44100 Hz")
        self.sample_rate.grid(row=1, column=1, padx=5, pady=5)
        
        self.compress_audio_btn = ctk.CTkButton(tab, text="بدء ضغط الصوت")
        self.compress_audio_btn.pack(pady=15)
        self.audio_info_label = ctk.CTkLabel(tab, text="الملفات: 0 | الحجم: 0 MB")
        self.audio_info_label.pack(pady=5)

    def setup_history_tab(self):
        tab = self.notebook.add("سجل العمليات")
        
        self.history_text = scrolledtext.ScrolledText(tab, height=20, width=70, bg="#2b2b2b", fg="white")
        self.history_text.pack(pady=10, padx=10, fill="both", expand=True)
        self.history_text.config(state=tk.DISABLED)
        
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(pady=5)
        self.clear_history_btn = ctk.CTkButton(btn_frame, text="مسح السجل")
        self.clear_history_btn.pack(side="left", padx=5)
        self.export_history_btn = ctk.CTkButton(btn_frame, text="تصدير السجل")
        self.export_history_btn.pack(side="left", padx=5)
