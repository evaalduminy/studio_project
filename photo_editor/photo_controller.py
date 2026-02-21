# /photo_editor/photo_controller.py

import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
from .photo_model import PhotoModel
from .photo_view import PhotoView
from .text_dialog import TextDialog
from .batch_dialog import BatchDialog

class PhotoController:
    """
    فئة المتحكم لمحرر الصور.
    تربط بين الواجهة (View) والمنطق (Model).
    """
    def __init__(self, parent_tab):
        self.model = PhotoModel()
        self.view = PhotoView(parent_tab)
        
        # --- متغيرات الحالة ---
        self.active_layer_index = 0
        self.is_drawing = False
        self.is_cropping = False
        self.is_dragging_layer = False
        self.last_draw_point = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.original_layer_x = 0
        self.original_layer_y = 0
        
        self.bind_commands()

    def bind_commands(self):
        """ربط جميع عناصر الواجهة بالدوال المناسبة في المتحكم."""
        # أزرار الملفات
        self.view.open_button.configure(command=self.open_image)
        self.view.save_as_button.configure(command=self.save_as_image)
        
        # أزرار التاريخ
        self.view.undo_button.configure(command=self.undo)
        self.view.redo_button.configure(command=self.redo)

        # أزرار الطبقات
        self.view.add_layer_button.configure(command=self.add_image_layer)
        self.view.add_text_button.configure(command=self.open_text_dialog)
        self.view.remove_layer_button.configure(command=self.remove_layer)
        self.view.layers_listbox.bind('<<ListboxSelect>>', self.on_layer_select)
        self.view.opacity_slider.configure(command=self.update_opacity)

        # أزرار التعديلات
        self.view.apply_adj_button.configure(command=self.apply_adjustments)
        self.view.cancel_adj_button.configure(command=self.cancel_adjustments)
        self.view.apply_threshold_button.configure(command=self.apply_threshold)
        for slider in self.view.adjustment_sliders.values():
            slider.bind("<ButtonPress-1>", self.start_adjustment_preview)
            slider.bind("<ButtonRelease-1>", self.preview_adjustments)

        # أزرار الفلاتر
        for name, filter_type in self.view.filter_buttons.items():
            button = self.find_widget_by_text(self.view.filters_tab, name)
            if button:
                button.configure(command=lambda ft=filter_type: self.apply_filter(ft))

        # أزرار الأدوات
        self.view.brush_button.configure(command=self.toggle_drawing_mode)
        self.view.crop_button.configure(command=self.toggle_crop_mode)
        self.view.rotate_left_button.configure(command=lambda: self.apply_transform('rotate_left'))
        self.view.rotate_right_button.configure(command=lambda: self.apply_transform('rotate_right'))
        self.view.flip_horizontal_button.configure(command=lambda: self.apply_transform('flip_horizontal'))
        self.view.flip_vertical_button.configure(command=lambda: self.apply_transform('flip_vertical'))
        self.view.batch_button.configure(command=self.open_batch_dialog)

        # أدوات الفرشاة
        self.view.brush_size_slider.configure(command=self.update_brush_size)
        self.view.brush_color_button.configure(command=self.choose_brush_color)

        # أحداث الكانفاس
        self.view.canvas.bind("<Configure>", self.on_canvas_resize)
        self.view.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.view.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.view.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

    # --- دوال معالجة أحداث الكانفاس ---
    # <<< تم تصحيح المسافة البادئة هنا >>>
    def on_canvas_press(self, event):
        """يتم استدعاؤها عند الضغط على الكانفاس."""
        if self.is_drawing:
            self.draw_on_canvas(event)
        elif self.is_cropping:
            self.start_crop(event)
        else: # وضع تحريك الطبقات
            self.start_drag_layer(event)

    def on_canvas_drag(self, event):
        """يتم استدعاؤها عند السحب على الكانفاس."""
        if self.is_drawing:
            self.draw_on_canvas(event)
        elif self.is_cropping:
            self.update_crop_rect(event)
        elif self.is_dragging_layer:
            self.drag_layer(event)

    def on_canvas_release(self, event):
        """يتم استدعاؤها عند رفع زر الفأرة عن الكانفاس."""
        if self.is_drawing:
            self.last_draw_point = None
            self.model.add_to_history()
            self.update_history_buttons()
        elif self.is_cropping:
            pass # لا تفعل شيئاً، ننتظر الضغط على زر "تطبيق"
        elif self.is_dragging_layer:
            self.end_drag_layer(event)

    def on_canvas_resize(self, event):
        """يتم استدعاؤها عند تغيير حجم النافذة."""
        self.update_view()

    # --- دوال الملفات والتاريخ ---
    def open_image(self):
        path = filedialog.askopenfilename(title="اختر صورة", filetypes=[("ملفات الصور", "*.jpg *.jpeg *.png *.bmp *.tiff")])
        if path:
            self.model.load_image(path)
            self.active_layer_index = 0
            self.update_view()

    def save_as_image(self):
        if not self.model.layers: return
        path = filedialog.asksaveasfilename(title="حفظ الصورة باسم", defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")])
        if path:
            self.model.save_image(path)
            messagebox.showinfo("نجاح", "تم حفظ الصورة بنجاح.")

    def undo(self):
        if self.model.undo():
            self.update_view()

    def redo(self):
        if self.model.redo():
            self.update_view()

    # --- دوال الطبقات ---
    def add_image_layer(self):
        if not self.model.layers: return
        path = filedialog.askopenfilename(title="اختر صورة للطبقة", filetypes=[("ملفات الصور", "*.jpg *.jpeg *.png *.bmp")])
        if path:
            self.model.add_image_layer(path)
            self.active_layer_index = len(self.model.layers) - 1
            self.update_view()

    def open_text_dialog(self):
        if not self.model.layers: return
        dialog = TextDialog(self.view.winfo_toplevel())
        self.view.wait_window(dialog)
        if dialog.result:
            self.model.add_text_layer(**dialog.result)
            self.active_layer_index = len(self.model.layers) - 1
            self.update_view()

    def remove_layer(self):
        if self.model.remove_layer(self.active_layer_index):
            self.active_layer_index = min(self.active_layer_index, len(self.model.layers) - 1)
            self.update_view()

    def on_layer_select(self, event):
        selection = self.view.layers_listbox.curselection()
        if selection:
            self.active_layer_index = selection[0]
            self.update_view()

    def update_opacity(self, value):
        self.model.layers[self.active_layer_index]['opacity'] = float(value)
        self.update_view()

    # --- دوال التعديلات والفلاتر ---
    def start_adjustment_preview(self, event):
        self.model.start_adjustment_preview(self.active_layer_index)

    def apply_adjustments(self):
        self.model.apply_adjustments(
            self.active_layer_index,
            self.view.adjustment_sliders['brightness'].get(),
            self.view.adjustment_sliders['contrast'].get(),
            self.view.adjustment_sliders['saturation'].get(),
            self.view.adjustment_sliders['sharpness'].get()
        )
        self.view.reset_adjustment_sliders()
        self.update_view()

    def cancel_adjustments(self):
        self.model.cancel_adjustment_preview(self.active_layer_index)
        self.view.reset_adjustment_sliders()
        self.update_view()

    def apply_filter(self, filter_type):
        self.model.apply_filter(self.active_layer_index, filter_type)
        self.update_view()

    def apply_threshold(self):
        value = self.view.threshold_slider.get()
        self.model.apply_threshold(self.active_layer_index, value)
        self.update_view()

    # --- دوال الأدوات ---
    def toggle_drawing_mode(self):
        if not self.model.layers: return
        self.is_drawing = not self.is_drawing
        self.view.show_brush_toolbar(self.is_drawing)
        if self.is_drawing:
            self.active_layer_index = self.model.add_draw_layer()
            self.update_view()

    def update_brush_size(self, value):
        self.model.brush_size = int(value)

    def choose_brush_color(self):
        color_code = colorchooser.askcolor(parent=self.view.winfo_toplevel(), title="اختر لون الفرشاة")
        if color_code and color_code[0]:
            self.model.brush_color = (*color_code[0], 255)
            self.view.update_brush_color_button(color_code[1])

    def draw_on_canvas(self, event):
        coords = self.view.canvas_to_image_coords(event.x, event.y)
        if coords:
            self.model.draw_on_layer(self.active_layer_index, self.last_draw_point, coords)
            self.last_draw_point = coords
            self.update_view()

    def toggle_crop_mode(self):
        if not self.model.layers: return
        self.is_cropping = not self.is_cropping
        self.view.show_crop_controls(self.is_cropping)
        if self.is_cropping:
            self.view.apply_crop_button.configure(command=self.apply_crop)

    def start_crop(self, event):
        self.view.start_crop_rect(event.x, event.y)

    def update_crop_rect(self, event):
        self.view.update_crop_rect(event.x, event.y)

    def apply_crop(self):
        crop_box = self.view.get_image_crop_box()
        if crop_box:
            self.model.apply_crop(crop_box)
            self.update_view()
        self.toggle_crop_mode()

    def apply_transform(self, operation):
        self.model.apply_transform(operation)
        self.update_view()

    def open_batch_dialog(self):
        dialog = BatchDialog(self.view.winfo_toplevel())
        self.view.wait_window(dialog)
        if dialog.result:
            self.model.process_batch_watermark(**dialog.result, progress_callback=dialog.update_progress)

    # --- دوال تحريك الطبقات ---
    def start_drag_layer(self, event):
        if self.active_layer_index > 0: # لا يمكن تحريك الطبقة الأساسية
            self.is_dragging_layer = True
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            layer = self.model.layers[self.active_layer_index]
            self.original_layer_x = layer['x']
            self.original_layer_y = layer['y']

    def drag_layer(self, event):
        if self.is_dragging_layer:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            self.model.layers[self.active_layer_index]['x'] = self.original_layer_x + dx
            self.model.layers[self.active_layer_index]['y'] = self.original_layer_y + dy
            self.update_view()

    def end_drag_layer(self, event):
        if self.is_dragging_layer:
            self.is_dragging_layer = False
            self.model.add_to_history()
            self.update_history_buttons()

    # --- دالة التحديث الرئيسية ---
    def update_view(self):
        """تحديث الواجهة بالكامل بناءً على حالة الـ Model."""
        # عرض الصورة
        composited_image = self.model.get_composited_image()
        self.view.display_image(composited_image)
        
        # تحديث قائمة الطبقات
        self.view.update_layers_list(self.model.layers, self.active_layer_index)
        
        # تحديث أزرار التراجع/الإعادة
        self.update_history_buttons()

    def update_history_buttons(self):
        can_undo = self.model.history_index > 0
        can_redo = self.model.history_index < len(self.model.history) - 1
        self.view.update_history_buttons(can_undo, can_redo)

    def find_widget_by_text(self, parent, text):
        """دالة مساعدة للبحث عن ويدجت بناءً على النص."""
        for child in parent.winfo_children():
            if isinstance(child, ctk.CTkButton) and child.cget("text") == text:
                return child
            found = self.find_widget_by_text(child, text)
            if found:
                return found
        return None
