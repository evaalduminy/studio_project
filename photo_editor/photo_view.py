# /photo_editor/photo_view.py

import customtkinter as ctk
import tkinter as tk
from PIL import ImageTk, ImageFilter, Image

class PhotoView:
    """
    فئة الـ View لمحرر الصور.
    مسؤولة عن إنشاء وتحديث جميع عناصر الواجهة الرسومية.
    لا تحتوي على أي منطق عمل، فقط تعرض ما يُطلب منها.
    """
    def __init__(self, parent):
        self.parent = parent
        
        # --- الإطارات الرئيسية ---
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.control_panel = ctk.CTkFrame(self.main_frame, width=300)
        self.control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.control_panel.pack_propagate(False)

        self.display_frame = ctk.CTkFrame(self.main_frame)
        self.display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # --- منطقة العرض ---
        self.canvas = tk.Canvas(self.display_frame, bg="#2B2B2B", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.photo_tk = None # للحفاظ على مرجع للصورة المعروضة
        
        # متغيرات لحفظ أبعاد الصورة الأصلية عند العرض
        self.original_image_width = 1
        self.original_image_height = 1
        
        # --- أشرطة الأدوات (مخفية مبدئياً) ---
        self.setup_toolbars()
        
        # --- لوحة التحكم ---
        self.setup_control_panel()

    def setup_control_panel(self):
        """إنشاء كل عناصر لوحة التحكم الجانبية."""
        # --- إدارة الملفات والتاريخ ---
        file_frame = ctk.CTkFrame(self.control_panel)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        ctk.CTkLabel(file_frame, text="إدارة الملفات", font=("Arial", 14, "bold")).pack(pady=5)
        
        file_buttons_frame = ctk.CTkFrame(file_frame)
        file_buttons_frame.pack(fill=tk.X)
        file_buttons_frame.grid_columnconfigure((0,1), weight=1)
        self.open_button = ctk.CTkButton(file_buttons_frame, text="📂 فتح")
        self.open_button.grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=2)
        self.save_button = ctk.CTkButton(file_buttons_frame, text="💾 حفظ")
        self.save_button.grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        self.save_as_button = ctk.CTkButton(file_buttons_frame, text="💾 حفظ باسم")
        self.save_as_button.grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        history_buttons_frame = ctk.CTkFrame(file_frame)
        history_buttons_frame.pack(fill=tk.X, pady=5)
        history_buttons_frame.grid_columnconfigure((0,1), weight=1)
        self.undo_button = ctk.CTkButton(history_buttons_frame, text="↪️ تراجع", state="disabled")
        self.undo_button.grid(row=0, column=0, sticky="ew", padx=2)
        self.redo_button = ctk.CTkButton(history_buttons_frame, text="↩️ إعادة", state="disabled")
        self.redo_button.grid(row=0, column=1, sticky="ew", padx=2)

        # --- التبويبات ---
        tab_view = ctk.CTkTabview(self.control_panel)
        tab_view.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.layers_tab = tab_view.add("الطبقات")
        self.adjustments_tab = tab_view.add("تعديلات")
        self.filters_tab = tab_view.add("الفلاتر")
        self.tools_tab = tab_view.add("الأدوات")

        self.create_layers_tab(self.layers_tab)
        self.create_adjustments_tab(self.adjustments_tab)
        self.create_filters_tab(self.filters_tab)
        self.create_tools_tab(self.tools_tab)

    def setup_toolbars(self):
        """إنشاء أشرطة الأدوات العلوية للرسم والقص."""
        # شريط أدوات الرسم
        self.brush_toolbar = ctk.CTkFrame(self.display_frame, height=50)
        ctk.CTkLabel(self.brush_toolbar, text="حجم الفرشاة:").pack(side=tk.LEFT, padx=(10,0))
        self.brush_size_slider = ctk.CTkSlider(self.brush_toolbar, from_=1, to=100)
        self.brush_size_slider.pack(side=tk.LEFT, padx=5)
        self.brush_color_button = ctk.CTkButton(self.brush_toolbar, text="لون الفرشاة")
        self.brush_color_button.pack(side=tk.LEFT, padx=5)
        self.exit_draw_mode_button = ctk.CTkButton(self.brush_toolbar, text="الخروج من وضع الرسم")
        self.exit_draw_mode_button.pack(side=tk.RIGHT, padx=10)
        
        # شريط أدوات القص
        self.crop_toolbar = ctk.CTkFrame(self.display_frame, height=50)
        self.apply_crop_button = ctk.CTkButton(self.crop_toolbar, text="تطبيق القص")
        self.apply_crop_button.pack(pady=10)

    def create_layers_tab(self, tab):
        """إنشاء واجهة تبويب الطبقات."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        self.layers_listbox = tk.Listbox(tab, bg="#2b2b2b", fg="white", height=8, exportselection=False, borderwidth=0, highlightthickness=0)
        self.layers_listbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        self.add_layer_button = ctk.CTkButton(tab, text="إضافة طبقة صورة")
        self.add_layer_button.grid(row=1, column=0, sticky="ew", padx=(5,2), pady=5)
        self.add_text_button = ctk.CTkButton(tab, text="إضافة طبقة نص")
        self.add_text_button.grid(row=1, column=1, sticky="ew", padx=(2,5), pady=5)
        
        self.remove_layer_button = ctk.CTkButton(tab, text="حذف الطبقة المحددة")
        self.remove_layer_button.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        opacity_frame = ctk.CTkFrame(tab)
        opacity_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(opacity_frame, text="الشفافية:").pack(side=tk.LEFT, padx=5)
        self.opacity_slider = ctk.CTkSlider(opacity_frame, from_=0.0, to=1.0)
        self.opacity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def create_adjustments_tab(self, tab):
        """إنشاء واجهة تبويب التعديلات."""
        tab.grid_columnconfigure(0, weight=1)
        
        self.adjustment_sliders = {}
        
        adjustments = [
            ("السطوع", "brightness", 0.1, 2.0, 1.0),
            ("التباين", "contrast", 0.1, 2.0, 1.0),
            ("تشبع الألوان", "saturation", 0.0, 2.0, 1.0),
            ("الحدة", "sharpness", 0.0, 3.0, 1.0),
            ("العتبة (Threshold)", "threshold", 0, 255, 128)
        ]
        
        row_counter = 0
        for name, key, from_, to, default in adjustments:
            ctk.CTkLabel(tab, text=name).grid(row=row_counter, column=0, sticky="w", padx=10, pady=(10,0))
            row_counter += 1
            slider = ctk.CTkSlider(tab, from_=from_, to=to)
            slider.set(default)
            slider.grid(row=row_counter, column=0, sticky="ew", padx=10, pady=(0,10))
            row_counter += 1
            self.adjustment_sliders[key] = slider

        buttons_frame = ctk.CTkFrame(tab)
        buttons_frame.grid(row=row_counter, column=0, sticky="ew", padx=10, pady=20)
        buttons_frame.grid_columnconfigure((0,1), weight=1)
        self.apply_adj_button = ctk.CTkButton(buttons_frame, text="تطبيق التعديلات")
        self.apply_adj_button.grid(row=0, column=0, padx=2, sticky="ew")
        self.cancel_adj_button = ctk.CTkButton(buttons_frame, text="إلغاء المعاينة")
        self.cancel_adj_button.grid(row=0, column=1, padx=2, sticky="ew")

    def create_filters_tab(self, tab):
        """إنشاء واجهة تبويب الفلاتر."""
        tab.grid_columnconfigure(0, weight=1)
        self.filter_buttons = {}
        filters = [
            ("ضبابي (Blur)", ImageFilter.BLUR), 
            ("حاد (Sharpen)", ImageFilter.SHARPEN), 
            ("بحث عن الحواف", ImageFilter.FIND_EDGES), 
            ("نقش (Emboss)", ImageFilter.EMBOSS), 
            ("تحديد الخطوط", ImageFilter.CONTOUR)
        ]
        for i, (name, filter_type) in enumerate(filters):
            btn = ctk.CTkButton(tab, text=name)
            btn.grid(row=i, column=0, sticky="ew", padx=10, pady=4)
            self.filter_buttons[name] = filter_type

    def create_tools_tab(self, tab):
        """إنشاء واجهة تبويب الأدوات."""
        tab.grid_columnconfigure(0, weight=1)
        
        drawing_frame = ctk.CTkFrame(tab)
        drawing_frame.pack(fill=tk.X, padx=10, pady=10)
        ctk.CTkLabel(drawing_frame, text="الرسم (Drawing)", font=("Arial", 12, "bold")).pack()
        self.brush_button = ctk.CTkButton(drawing_frame, text="🖌️ فرشاة الرسم")
        self.brush_button.pack(fill=tk.X, pady=4)
        
        transform_frame = ctk.CTkFrame(tab)
        transform_frame.pack(fill=tk.X, padx=10, pady=10)
        ctk.CTkLabel(transform_frame, text="التحويل (Transform)", font=("Arial", 12, "bold")).pack()
        
        self.crop_button = ctk.CTkButton(transform_frame, text="✂️ قص الصورة")
        self.crop_button.pack(fill=tk.X, pady=4)
        
        rotate_frame = ctk.CTkFrame(transform_frame)
        rotate_frame.pack(fill=tk.X, pady=4)
        rotate_frame.grid_columnconfigure((0,1), weight=1)
        self.rotate_right_button = ctk.CTkButton(rotate_frame, text="↪️ 90°")
        self.rotate_right_button.grid(row=0, column=0, padx=2, sticky="ew")
        self.rotate_left_button = ctk.CTkButton(rotate_frame, text="↩️ 90°")
        self.rotate_left_button.grid(row=0, column=1, padx=2, sticky="ew")
        
        flip_frame = ctk.CTkFrame(transform_frame)
        flip_frame.pack(fill=tk.X, pady=4)
        flip_frame.grid_columnconfigure((0,1), weight=1)
        self.flip_horizontal_button = ctk.CTkButton(flip_frame, text="↔️ قلب أفقي")
        self.flip_horizontal_button.grid(row=0, column=0, padx=2, sticky="ew")
        self.flip_vertical_button = ctk.CTkButton(flip_frame, text="↕️ قلب عمودي")
        self.flip_vertical_button.grid(row=0, column=1, padx=2, sticky="ew")

        batch_frame = ctk.CTkFrame(tab)
        batch_frame.pack(fill=tk.X, padx=10, pady=20)
        ctk.CTkLabel(batch_frame, text="المعالجة المجمعة", font=("Arial", 12, "bold")).pack()
        self.batch_button = ctk.CTkButton(batch_frame, text="إضافة شعار لعدة صور")
        self.batch_button.pack(fill=tk.X, pady=4)

    # --- دوال تحديث الواجهة ---
    def display_image(self, pil_image):
        """عرض صورة على الكانفاس."""
        self.canvas.delete("all")
        if not pil_image: return
        
        # حفظ أبعاد الصورة الأصلية لاستخدامها في التحويلات
        self.original_image_width = pil_image.width
        self.original_image_height = pil_image.height
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1: return

        ratio = min(canvas_width / pil_image.width, canvas_height / pil_image.height)
        display_width = int(pil_image.width * ratio)
        display_height = int(pil_image.height * ratio)
        
        display_image = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        
        self.photo_tk = ImageTk.PhotoImage(display_image)
        self.canvas.create_image(canvas_width / 2, canvas_height / 2, image=self.photo_tk, anchor=tk.CENTER)

    def update_layers_list(self, layers, active_layer_index):
        """تحديث قائمة الطبقات في الواجهة."""
        self.layers_listbox.delete(0, tk.END)
        for i, layer in enumerate(layers):
            prefix = "▶ " if i == active_layer_index else "  "
            visibility = "👁" if layer['visible'] else "🚫"
            self.layers_listbox.insert(tk.END, f"{prefix}{visibility} {layer['name']}")
        if active_layer_index is not None and active_layer_index < len(layers):
            self.opacity_slider.set(layers[active_layer_index]['opacity'])

    def update_history_buttons(self, can_undo, can_redo):
        """تحديث حالة أزرار التراجع والإعادة."""
        self.undo_button.configure(state="normal" if can_undo else "disabled")
        self.redo_button.configure(state="normal" if can_redo else "disabled")

    def reset_adjustment_sliders(self):
        """إعادة تعيين قيم شرائط التمرير إلى الوضع الافتراضي."""
        self.adjustment_sliders['brightness'].set(1.0)
        self.adjustment_sliders['contrast'].set(1.0)
        self.adjustment_sliders['saturation'].set(1.0)
        self.adjustment_sliders['sharpness'].set(1.0)
        self.adjustment_sliders['threshold'].set(128)

    def show_brush_toolbar(self, show: bool):
        """إظهار أو إخفاء شريط أدوات الفرشاة."""
        if show:
            self.brush_toolbar.place(relx=0, rely=0, relwidth=1, anchor="nw")
        else:
            self.brush_toolbar.place_forget()

    def update_brush_color_button(self, hex_color):
        """تحديث لون زر الفرشاة ليعكس اللون المختار."""
        self.brush_color_button.configure(fg_color=hex_color)
        r, g, b = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        text_color = "#000000" if (r*0.299 + g*0.587 + b*0.114) > 186 else "#FFFFFF"
        self.brush_color_button.configure(text_color=text_color)

    # --- دوال التحكم في واجهة القص ---
    def show_crop_controls(self, show: bool):
        """إظهار أو إخفاء عناصر التحكم في القص."""
        if show:
            self.crop_toolbar.place(relx=0.5, rely=1.0, anchor="s", y=-10)
        else:
            self.crop_toolbar.place_forget()
            self.canvas.delete("crop_rect")

    def start_crop_rect(self, x, y):
        """إنشاء مستطيل القص عند بدء السحب."""
        self.canvas.delete("crop_rect")
        self.crop_start_x = x
        self.crop_start_y = y
        self.crop_rect = self.canvas.create_rectangle(x, y, x, y, outline="cyan", width=2, dash=(4, 4), tags="crop_rect")

    def update_crop_rect(self, x, y):
        """تحديث أبعاد مستطيل القص أثناء السحب."""
        if hasattr(self, 'crop_rect'):
            self.canvas.coords(self.crop_rect, self.crop_start_x, self.crop_start_y, x, y)

    def get_image_crop_box(self):
        """
        تحويل إحداثيات مستطيل القص من الكانفاس إلى إحداثيات الصورة الأصلية.
        """
        if not hasattr(self, 'crop_rect') or not self.photo_tk:
            return None

        x1, y1, x2, y2 = self.canvas.coords(self.crop_rect)
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        display_width = self.photo_tk.width()
        display_height = self.photo_tk.height()
        
        ratio = display_width / self.original_image_width
        
        offset_x = (canvas_width - display_width) / 2
        offset_y = (canvas_height - display_height) / 2

        img_x1 = (x1 - offset_x) / ratio
        img_y1 = (y1 - offset_y) / ratio
        img_x2 = (x2 - offset_x) / ratio
        img_y2 = (y2 - offset_y) / ratio

        return (int(min(img_x1, img_x2)), int(min(img_y1, img_y2)), 
                int(max(img_x1, img_x2)), int(max(img_y1, img_y2)))

     
        
    def create_tools_tab(self, tab):
        """إنشاء واجهة تبويب الأدوات."""
        tab.grid_columnconfigure(0, weight=1)
        
        drawing_frame = ctk.CTkFrame(tab)
        drawing_frame.pack(fill=tk.X, padx=10, pady=10)
        ctk.CTkLabel(drawing_frame, text="الرسم (Drawing)", font=("Arial", 12, "bold")).pack()
        self.brush_button = ctk.CTkButton(drawing_frame, text="🖌️ فرشاة الرسم")
        self.brush_button.pack(fill=tk.X, pady=4)
        
        transform_frame = ctk.CTkFrame(tab)
        transform_frame.pack(fill=tk.X, padx=10, pady=10)
        ctk.CTkLabel(transform_frame, text="التحويل (Transform)", font=("Arial", 12, "bold")).pack()
        
        self.crop_button = ctk.CTkButton(transform_frame, text="✂️ قص الصورة")
        self.crop_button.pack(fill=tk.X, pady=4)
        
        rotate_frame = ctk.CTkFrame(transform_frame)
        rotate_frame.pack(fill=tk.X, pady=4)
        rotate_frame.grid_columnconfigure((0,1), weight=1)
        self.rotate_right_button = ctk.CTkButton(rotate_frame, text="↪️ 90°")
        self.rotate_right_button.grid(row=0, column=0, padx=2, sticky="ew")
        self.rotate_left_button = ctk.CTkButton(rotate_frame, text="↩️ 90°")
        self.rotate_left_button.grid(row=0, column=1, padx=2, sticky="ew")
        
        flip_frame = ctk.CTkFrame(transform_frame)
        flip_frame.pack(fill=tk.X, pady=4)
        flip_frame.grid_columnconfigure((0,1), weight=1)
        self.flip_horizontal_button = ctk.CTkButton(flip_frame, text="↔️ قلب أفقي")
        self.flip_horizontal_button.grid(row=0, column=0, padx=2, sticky="ew")
        self.flip_vertical_button = ctk.CTkButton(flip_frame, text="↕️ قلب عمودي")
        self.flip_vertical_button.grid(row=0, column=1, padx=2, sticky="ew")

        batch_frame = ctk.CTkFrame(tab)
        batch_frame.pack(fill=tk.X, padx=10, pady=20)
        ctk.CTkLabel(batch_frame, text="المعالجة المجمعة", font=("Arial", 12, "bold")).pack()
        self.batch_button = ctk.CTkButton(batch_frame, text="إضافة شعار لعدة صور")
        self.batch_button.pack(fill=tk.X, pady=4)

    # --- دوال تحديث الواجهة ---
    def display_image(self, pil_image):
        """عرض صورة على الكانفاس."""
        self.canvas.delete("all")
        if not pil_image: 
            self.photo_tk = None
            return
        
        # حفظ أبعاد الصورة الأصلية لاستخدامها في التحويلات
        self.original_image_width = pil_image.width
        self.original_image_height = pil_image.height
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1: return

        ratio = min(canvas_width / pil_image.width, canvas_height / pil_image.height)
        display_width = int(pil_image.width * ratio)
        display_height = int(pil_image.height * ratio)
        
        display_image = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        
        self.photo_tk = ImageTk.PhotoImage(display_image)
        self.canvas.create_image(canvas_width / 2, canvas_height / 2, image=self.photo_tk, anchor=tk.CENTER)

    def update_layers_list(self, layers, active_layer_index):
        """تحديث قائمة الطبقات في الواجهة."""
        self.layers_listbox.delete(0, tk.END)
        for i, layer in enumerate(layers):
            prefix = "▶ " if i == active_layer_index else "  "
            visibility = "👁" if layer['visible'] else "🚫"
            self.layers_listbox.insert(tk.END, f"{prefix}{visibility} {layer['name']}")
        if active_layer_index is not None and active_layer_index < len(layers):
            self.layers_listbox.selection_set(active_layer_index)
            self.opacity_slider.set(layers[active_layer_index]['opacity'])

    def update_history_buttons(self, can_undo, can_redo):
        """تحديث حالة أزرار التراجع والإعادة."""
        self.undo_button.configure(state="normal" if can_undo else "disabled")
        self.redo_button.configure(state="normal" if can_redo else "disabled")

    def reset_adjustment_sliders(self):
        """إعادة تعيين قيم شرائط التمرير إلى الوضع الافتراضي."""
        self.adjustment_sliders['brightness'].set(1.0)
        self.adjustment_sliders['contrast'].set(1.0)
        self.adjustment_sliders['saturation'].set(1.0)
        self.adjustment_sliders['sharpness'].set(1.0)
        self.adjustment_sliders['threshold'].set(128)

    def show_brush_toolbar(self, show: bool):
        """إظهار أو إخفاء شريط أدوات الفرشاة."""
        if show:
            self.brush_toolbar.place(relx=0, rely=0, relwidth=1, anchor="nw")
        else:
            self.brush_toolbar.place_forget()

    def update_brush_color_button(self, hex_color):
        """تحديث لون زر الفرشاة ليعكس اللون المختار."""
        self.brush_color_button.configure(fg_color=hex_color)
        r, g, b = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        text_color = "#000000" if (r*0.299 + g*0.587 + b*0.114) > 186 else "#FFFFFF"
        self.brush_color_button.configure(text_color=text_color)

    # --- دوال التحكم في واجهة القص ---
    def show_crop_controls(self, show: bool):
        """إظهار أو إخفاء عناصر التحكم في القص."""
        if show:
            self.crop_toolbar.place(relx=0.5, rely=1.0, anchor="s", y=-10)
        else:
            self.crop_toolbar.place_forget()
            self.canvas.delete("crop_rect")

    def start_crop_rect(self, x, y):
        """إنشاء مستطيل القص عند بدء السحب."""
        self.canvas.delete("crop_rect")
        self.crop_start_x = x
        self.crop_start_y = y
        self.crop_rect = self.canvas.create_rectangle(x, y, x, y, outline="cyan", width=2, dash=(4, 4), tags="crop_rect")

    def update_crop_rect(self, x, y):
        """تحديث أبعاد مستطيل القص أثناء السحب."""
        if hasattr(self, 'crop_rect'):
            self.canvas.coords(self.crop_rect, self.crop_start_x, self.crop_start_y, x, y)

    def get_image_crop_box(self):
        """
        تحويل إحداثيات مستطيل القص من الكانفاس إلى إحداثيات الصورة الأصلية.
        """
        if not hasattr(self, 'crop_rect') or not self.photo_tk:
            return None

        x1, y1, x2, y2 = self.canvas.coords(self.crop_rect)
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        display_width = self.photo_tk.width()
        display_height = self.photo_tk.height()
        
        if self.original_image_width == 0: return None
        ratio = display_width / self.original_image_width
        
        offset_x = (canvas_width - display_width) / 2
        offset_y = (canvas_height - display_height) / 2

        img_x1 = (x1 - offset_x) / ratio
        img_y1 = (y1 - offset_y) / ratio
        img_x2 = (x2 - offset_x) / ratio
        img_y2 = (y2 - offset_y) / ratio

        return (int(min(img_x1, img_x2)), int(min(img_y1, img_y2)), 
                int(max(img_x1, img_x2)), int(max(img_y1, img_y2)))

    def canvas_to_image_coords(self, canvas_x, canvas_y):
   
   
    # 1. التحقق من وجود صورة معروضة
    if not self.photo_tk: 
        return None

    # 2. الحصول على أبعاد الكانفاس والصورة المعروضة عليه
    canvas_width = self.canvas.winfo_width()
    canvas_height = self.canvas.winfo_height()
    display_width = self.photo_tk.width()
    display_height = self.photo_tk.height()
    
    # 3. حماية من القسمة على صفر (إذا لم يتم تحميل صورة بعد)
    if self.original_image_width == 0: 
        return None
        
    # 4. حساب نسبة التصغير/التكبير التي تم تطبيقها على الصورة لتناسب الكانفاس
    ratio = display_width / self.original_image_width
    
    # 5. حساب المسافة الفارغة (الهوامش) حول الصورة داخل الكانفاس
    offset_x = (canvas_width - display_width) / 2
    offset_y = (canvas_height - display_height) / 2

    # 6. التحقق مما إذا كانت نقرة الفأرة داخل حدود الصورة المعروضة (وليس في الهوامش)
    if not (offset_x <= canvas_x < offset_x + display_width and offset_y <= canvas_y < offset_y + display_height):
        return None

    # 7. المعادلة العكسية: تحويل إحداثيات الكانفاس إلى إحداثيات الصورة الأصلية
    #    - نطرح الهامش للوصول إلى إحداثيات النقطة بالنسبة للصورة المعروضة
    #    - نقسم على نسبة التكبير/التصغير للعودة إلى الإحداثيات في الصورة الأصلية
    image_x = int((canvas_x - offset_x) / ratio)
    image_y = int((canvas_y - offset_y) / ratio)
    
    # 8. إرجاع الإحداثيات المحسوبة كنقطة (tuple)
    return (image_x, image_y)

        # /photo_editor/photo_view.py

# ... (كل الكود السابق حتى نهاية دالة canvas_to_image_coords) ...

# =================================================================
# |          هذا هو الكود الناقص الذي يجب إضافته                   |
# =================================================================

class TextDialog(ctk.CTkToplevel):
    """نافذة منبثقة لإدخال النص وخصائصه."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("إضافة نص")
        self.geometry("400x300")
        
        self.result = None # لتخزين نتيجة الحوار

        self.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self, text="النص:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.text_entry = ctk.CTkEntry(self, width=250)
        self.text_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self, text="حجم الخط:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.size_entry = ctk.CTkEntry(self)
        self.size_entry.insert(0, "48")
        self.size_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self, text="اللون:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.color_button = ctk.CTkButton(self, text="اختر لون", command=self.choose_color)
        self.color_button.configure(fg_color="#000000", text_color="#FFFFFF")
        self.color_button.color = (0, 0, 0, 255) # أسود افتراضي
        self.color_button.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        add_button = ctk.CTkButton(self, text="إضافة", command=self.on_add)
        add_button.grid(row=3, column=0, columnspan=2, padx=10, pady=20)

        # جعل النافذة منبثقة بشكل صحيح
        self.transient(parent)
        self.grab_set()

    def choose_color(self):
        """فتح نافذة اختيار اللون."""
        from tkinter import colorchooser
        # تمرير النافذة الحالية (self) كأب لنافذة اختيار الألوان
        color_code = colorchooser.askcolor(parent=self, title="اختر لون النص")
         
        if color_code and color_code[0]:
            rgb, hex_color = color_code[0], color_code[1]
            self.color_button.configure(fg_color=hex_color)
            text_color = "#000000" if (rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) > 186 else "#FFFFFF"
            self.color_button.configure(text_color=text_color)
            self.color_button.color = (int(rgb[0]), int(rgb[1]), int(rgb[2]), 255)

    def on_add(self):
        """عند الضغط على زر إضافة."""
        from tkinter import messagebox
        text = self.text_entry.get()
        size_str = self.size_entry.get()
        if not text or not size_str.isdigit():
            # تمرير النافذة الحالية (self) كأب لرسالة الخطأ
            messagebox.showerror("خطأ", "الرجاء إدخال نص وحجم خط صحيح.", parent=self)
            return
        
        self.result = {
            "text": text,
            "size": int(size_str),
            "color": self.color_button.color
        }
        self.destroy()

class BatchProcessingWindow(ctk.CTkToplevel):
    """
    فئة تمثل نافذة المعالجة الدفعية.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("المعالجة الدفعية")
        self.geometry("500x450")
        
        self.setup_ui()

        # جعل النافذة منبثقة بشكل صحيح
        self.transient(parent)
        self.grab_set()

    def setup_ui(self):
        """إنشاء كل عناصر الواجهة داخل النافذة المنبثقة."""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # --- اختيار مجلد الصور ---
        ctk.CTkLabel(main_frame, text="مجلد الصور المصدر:").pack(anchor="w", pady=(10, 0))
        folder_frame = ctk.CTkFrame(main_frame)
        folder_frame.pack(fill=tk.X, pady=5)
        self.folder_path_var = tk.StringVar()
        folder_entry = ctk.CTkEntry(folder_frame, textvariable=self.folder_path_var)
        folder_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self.select_folder_button = ctk.CTkButton(folder_frame, text="اختيار", width=70)
        self.select_folder_button.pack(side=tk.LEFT)

        # --- اختيار صورة الشعار ---
        ctk.CTkLabel(main_frame, text="صورة الشعار (Watermark):").pack(anchor="w", pady=(10, 0))
        watermark_frame = ctk.CTkFrame(main_frame)
        watermark_frame.pack(fill=tk.X, pady=5)
        self.watermark_path_var = tk.StringVar()
        watermark_entry = ctk.CTkEntry(watermark_frame, textvariable=self.watermark_path_var)
        watermark_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self.select_watermark_button = ctk.CTkButton(watermark_frame, text="اختيار", width=70)
        self.select_watermark_button.pack(side=tk.LEFT)

        # --- اختيار موضع الشعار ---
        ctk.CTkLabel(main_frame, text="موضع الشعار:").pack(anchor="w", pady=(10, 0))
        self.position_var = tk.StringVar(value="bottom_right")
        positions_frame = ctk.CTkFrame(main_frame)
        positions_frame.pack(fill=tk.X, pady=5)
        positions = [("أعلى اليسار", "top_left"), ("أعلى اليمين", "top_right"), 
                     ("أسفل اليسار", "bottom_left"), ("أسفل اليمين", "bottom_right")]
        for i, (text, value) in enumerate(positions):
            ctk.CTkRadioButton(positions_frame, text=text, variable=self.position_var, value=value).pack(side="left", padx=10, pady=5, expand=True)

        # --- اختيار مجلد الحفظ ---
        ctk.CTkLabel(main_frame, text="مجلد الحفظ (الوجهة):").pack(anchor="w", pady=(10, 0))
        save_frame = ctk.CTkFrame(main_frame)
        save_frame.pack(fill=tk.X, pady=5)
        self.save_path_var = tk.StringVar()
        save_entry = ctk.CTkEntry(save_frame, textvariable=self.save_path_var)
        save_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self.select_save_folder_button = ctk.CTkButton(save_frame, text="اختيار", width=70)
        self.select_save_folder_button.pack(side=tk.LEFT)

        # --- شريط التقدم والحالة ---
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(pady=20, fill=tk.X)
        self.progress_bar.set(0)
        self.progress_label = ctk.CTkLabel(main_frame, text="في انتظار البدء...")
        self.progress_label.pack()

        # --- زر البدء ---
        self.start_button = ctk.CTkButton(main_frame, text="بدء المعالجة")
        self.start_button.pack(pady=10)
