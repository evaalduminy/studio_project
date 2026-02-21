# /audio_editor/audio_view.py

import customtkinter as ctk
import tkinter as tk
import numpy as np  # <-- تم إضافة الاستيراد المفقود

class AudioView:
    """
    فئة العرض لمحرر الصوت.
    مسؤولة عن بناء كل عناصر الواجهة الرسومية الخاصة بمحرر الصوت.
    """
    def __init__(self, parent):
        self.parent = parent
        
        # --- الإطار الرئيسي ---
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # --- الإطار العلوي (الملف والأزرار الرئيسية) ---
        top_frame = ctk.CTkFrame(main_frame)
        top_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        top_frame.grid_columnconfigure(1, weight=1)

        self.file_label = ctk.CTkLabel(top_frame, text="لم يتم تحميل ملف", font=("Arial", 12))
        self.file_label.grid(row=0, column=0, columnspan=3, pady=5, padx=10, sticky="w")

        controls_frame = ctk.CTkFrame(top_frame)
        controls_frame.grid(row=1, column=0, columnspan=3, pady=5, padx=5, sticky="ew")
        controls_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.open_button = ctk.CTkButton(controls_frame, text="📂 فتح")
        self.open_button.grid(row=0, column=0, padx=2, sticky="ew")
        self.play_button = ctk.CTkButton(controls_frame, text="▶ تشغيل")
        self.play_button.grid(row=0, column=1, padx=2, sticky="ew")
        self.save_button = ctk.CTkButton(controls_frame, text="💾 حفظ")
        self.save_button.grid(row=0, column=2, padx=2, sticky="ew")

        # --- كانفاس رسم الموجة الصوتية ---
        self.waveform_canvas = tk.Canvas(main_frame, bg="#2B2B2B", highlightthickness=0)
        self.waveform_canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # --- الإطار السفلي (شريط التقدم والتبويبات) ---
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        bottom_frame.grid_columnconfigure(0, weight=1)

        progress_frame = ctk.CTkFrame(bottom_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        progress_frame.grid_columnconfigure(0, weight=1)

        self.position_label = ctk.CTkLabel(progress_frame, text="00:00 / 00:00", font=("Arial", 10))
        self.position_label.grid(row=0, column=1, padx=10)
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=10)
        self.progress_bar.set(0)

        # --- تبويبات الأدوات ---
        tab_view = ctk.CTkTabview(bottom_frame)
        tab_view.pack(fill=tk.X, pady=10)
        edit_tab = tab_view.add("أدوات التحرير")
        filters_tab = tab_view.add("الفلاتر والتأثيرات")
        
        self.create_edit_tab(edit_tab)
        self.create_filters_tab(filters_tab)

    def create_edit_tab(self, tab):
        """إنشاء الأزرار داخل تبويب أدوات التحرير."""
        tab.grid_columnconfigure((0, 1, 2), weight=1)
        self.cut_button = ctk.CTkButton(tab, text="✂️ قص")
        self.cut_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.copy_button = ctk.CTkButton(tab, text="📋 نسخ")
        self.copy_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.paste_button = ctk.CTkButton(tab, text="📎 لصق")
        self.paste_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    def create_filters_tab(self, tab):
        """إنشاء الأزرار داخل تبويب الفلاتر والتأثيرات."""
        tab.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.amplify_button = ctk.CTkButton(tab, text="تعزيز الصوت")
        self.amplify_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.noise_gate_button = ctk.CTkButton(tab, text="تخفيض الضوضاء")
        self.noise_gate_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.reverb_button = ctk.CTkButton(tab, text="صدى (Reverb)")
        self.reverb_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.reverse_button = ctk.CTkButton(tab, text="عكس الصوت")
        self.reverse_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    def draw_waveform(self, audio_data):
        """
        رسم الموجة الصوتية على الكانفاس.
        هذه هي النسخة المصححة والآمنة.
        """
        self.waveform_canvas.delete("all")
        
        if audio_data is None or len(audio_data) == 0:
            return
        
        canvas_width = self.waveform_canvas.winfo_width()
        canvas_height = self.waveform_canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            return

        num_samples = len(audio_data)
        step = max(1, num_samples // canvas_width)
        
        try:
            amplitudes = [np.max(np.abs(audio_data[i:i+step])) for i in range(0, num_samples, step)]
            
            if not amplitudes:
                return

            max_amp = max(amplitudes)
            if max_amp == 0: max_amp = 1.0
            
            center_y = canvas_height / 2
            for i, amp in enumerate(amplitudes):
                line_height = (amp / max_amp) * canvas_height
                self.waveform_canvas.create_line(i, center_y - line_height / 2, i, center_y + line_height / 2, fill="#3498db", tags="waveform")
                
        except ValueError as e:
            print(f"خطأ في رسم الموجة: {e}")

    def draw_selection(self, start_pixel, end_pixel):
        """رسم مستطيل التحديد على الموجة الصوتية."""
        self.waveform_canvas.delete("selection")
        if start_pixel is not None and end_pixel is not None:
            start = min(start_pixel, end_pixel)
            end = max(start_pixel, end_pixel)
            self.waveform_canvas.create_rectangle(start, 0, end, self.waveform_canvas.winfo_height(), fill="#1f6aa5", stipple="gray50", outline="", tags="selection")
            self.waveform_canvas.tag_lower("selection", "waveform")

    def draw_playhead(self, x_pos):
        """رسم خط التشغيل (Playhead) عند الموضع الحالي."""
        self.waveform_canvas.delete("playhead")
        self.waveform_canvas.create_line(x_pos, 0, x_pos, self.waveform_canvas.winfo_height(), fill="red", width=2, tags="playhead")

    def format_time(self, seconds):
        """تحويل الثواني إلى صيغة دقائق:ثواني (e.g., 01:23)."""
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_time_labels(self, current_time, duration):
        """تحديث ملصقات الوقت التي تعرض الوقت الحالي والمدة الإجمالية."""
        self.position_label.configure(text=f"{self.format_time(current_time)} / {self.format_time(duration)}")
