# /compression_tool/compression_controller.py
from .compression_model import CompressionModel
from .compression_view import CompressionView
from tkinter import filedialog, messagebox, tk
import threading
import os
from datetime import datetime

class CompressionController:
    def __init__(self, parent):
        self.model = CompressionModel()
        self.view = CompressionView(parent)
        self.compression_thread = None
        self.result_queue = [] # طريقة بسيطة للحصول على نتيجة الخيط
        
        self.bind_commands()
        self.add_to_history("تم تشغيل أداة الضغط.")

    def bind_commands(self):
        # ربط تبويب الضغط العام
        self.view.add_files_btn.configure(command=self.add_general_files)
        self.view.add_folder_btn.configure(command=self.add_folder)
        self.view.remove_btn.configure(command=lambda: self.remove_selected(self.view.file_listbox, self.update_general_info))
        self.view.clear_btn.configure(command=lambda: self.clear_list(self.view.file_listbox, self.update_general_info))
        self.view.compress_btn.configure(command=self.start_general_compression)
        self.view.cancel_btn.configure(command=self.cancel_compression)
        
        # ربط تبويب ضغط الصور
        self.view.add_images_btn.configure(command=self.add_images)
        self.view.remove_image_btn.configure(command=lambda: self.remove_selected(self.view.image_listbox, self.update_image_info))
        self.view.clear_images_btn.configure(command=lambda: self.clear_list(self.view.image_listbox, self.update_image_info))
        self.view.compress_images_btn.configure(command=self.start_image_compression)
        
        # ربط تبويب ضغط الصوت
        self.view.add_audio_btn.configure(command=self.add_audio_files)
        self.view.remove_audio_btn.configure(command=lambda: self.remove_selected(self.view.audio_listbox, self.update_audio_info))
        self.view.clear_audio_btn.configure(command=lambda: self.clear_list(self.view.audio_listbox, self.update_audio_info))
        self.view.compress_audio_btn.configure(command=self.start_audio_compression)
        
        # ربط تبويب السجل
        self.view.clear_history_btn.configure(command=self.clear_history)
        self.view.export_history_btn.configure(command=self.export_history)

    # --- دوال إدارة القوائم ---
    def add_general_files(self):
        files = filedialog.askopenfilenames(title="اختر ملفات للضغط")
        for f in files: self.view.file_listbox.insert(tk.END, f)
        self.update_general_info()

    def add_images(self):
        files = filedialog.askopenfilenames(title="اختر صور للضغط", filetypes=[("الصور", "*.jpg *.jpeg *.png *.bmp *.gif *.webp")])
        for f in files: self.view.image_listbox.insert(tk.END, f)
        self.update_image_info()

    def add_audio_files(self):
        files = filedialog.askopenfilenames(title="اختر ملفات صوت للضغط", filetypes=[("الصوت", "*.wav")])
        for f in files: self.view.audio_listbox.insert(tk.END, f)
        self.update_audio_info()

    def add_folder(self):
        folder = filedialog.askdirectory(title="اختر مجلد للضغط")
        if folder:
            for root, _, files in os.walk(folder):
                for file in files:
                    self.view.file_listbox.insert(tk.END, os.path.join(root, file))
            self.update_general_info()

    def remove_selected(self, listbox, update_callback):
        for i in reversed(listbox.curselection()):
            listbox.delete(i)
        update_callback()

    def clear_list(self, listbox, update_callback):
        listbox.delete(0, tk.END)
        update_callback()

    # --- دوال تحديث المعلومات ---
    def update_general_info(self):
        files = self.view.file_listbox.get(0, tk.END)
        size = sum(os.path.getsize(f) for f in files if os.path.isfile(f))
        self.view.size_info_label.configure(text=f"الحجم: {size / (1024*1024):.2f} MB | الملفات: {len(files)}")

    def update_image_info(self):
        files = self.view.image_listbox.get(0, tk.END)
        size = sum(os.path.getsize(f) for f in files if os.path.isfile(f))
        self.view.image_info_label.configure(text=f"الصور: {len(files)} | الحجم: {size / (1024*1024):.2f} MB")

    def update_audio_info(self):
        files = self.view.audio_listbox.get(0, tk.END)
        size = sum(os.path.getsize(f) for f in files if os.path.isfile(f))
        self.view.audio_info_label.configure(text=f"الملفات: {len(files)} | الحجم: {size / (1024*1024):.2f} MB")

    # --- دوال بدء العمليات ---
    def _run_in_thread(self, target_func, args):
        self.prepare_for_compression()
        
        # دالة обгортка لتشغيل دالة الـ Model وحفظ نتيجتها
        def thread_wrapper():
            result = target_func(*args)
            self.result_queue.append(result)

        self.compression_thread = threading.Thread(target=thread_wrapper, daemon=True)
        self.compression_thread.start()
        self.check_thread()

    def start_general_compression(self):
        files = self.view.file_listbox.get(0, tk.END)
        if not files: return messagebox.showerror("خطأ", "لم يتم اختيار أي ملفات.")
        output_path = filedialog.asksaveasfilename(defaultextension=".zip", initialfile="archive.zip")
        if not output_path: return
        args = (files, output_path, self.view.compression_level.get(), self.view.password.get(), self.progress_callback)
        self._run_in_thread(self.model.compress_general_files, args)

    def start_image_compression(self):
        files = self.view.image_listbox.get(0, tk.END)
        if not files: return messagebox.showerror("خطأ", "لم يتم اختيار أي صور.")
        output_dir = filedialog.askdirectory(title="اختر مجلد لحفظ الصور")
        if not output_dir: return
        args = (files, output_dir, int(self.view.image_quality_slider.get()), self.view.image_format.get(), 
                self.view.image_resize_slider.get() / 100.0, self.progress_callback)
        self._run_in_thread(self.model.compress_images, args)

    def start_audio_compression(self):
        files = self.view.audio_listbox.get(0, tk.END)
        if not files: return messagebox.showerror("خطأ", "لم يتم اختيار أي ملفات صوت.")
        output_dir = filedialog.askdirectory(title="اختر مجلد لحفظ الصوتيات")
        if not output_dir: return
        quality_map = {"عالية (غير مضغوط)": 1.0, "متوسطة": 0.5, "منخفضة": 0.25}
        quality = quality_map.get(self.view.audio_quality.get())
        rate = int(self.view.sample_rate.get().split(" ")[0])
        args = (files, output_dir, quality, rate, self.progress_callback)
        self._run_in_thread(self.model.compress_audio, args)

    # --- دوال التحكم في سير العملية ---
    def prepare_for_compression(self):
        self.model.is_compressing = True
        self.view.compress_btn.configure(state="disabled")
        self.view.compress_images_btn.configure(state="disabled")
        self.view.compress_audio_btn.configure(state="disabled")
        self.view.cancel_btn.configure(state="normal")
        self.view.status_label.configure(text="جاري التحضير...")
        self.view.progress.set(0)
        self.result_queue.clear()

    def cancel_compression(self):
        self.model.is_compressing = False
        self.add_to_history("تم طلب إلغاء العملية.")

    def progress_callback(self, percentage, status):
        self.view.progress.set(percentage / 100)
        self.view.status_label.configure(text=status)

    def check_thread(self):
        if self.compression_thread.is_alive():
            self.view.parent.after(100, self.check_thread)
        else:
            self.complete_compression()

    def complete_compression(self):
        self.view.compress_btn.configure(state="normal")
        self.view.compress_images_btn.configure(state="normal")
        self.view.compress_audio_btn.configure(state="normal")
        self.view.cancel_btn.configure(state="disabled")
        self.view.status_label.configure(text="انتهت العملية.")
        self.view.progress.set(1)
        
        if self.result_queue:
            success, message = self.result_queue[0]
            if success:
                messagebox.showinfo("نجاح", message)
            else:
                messagebox.showerror("فشل أو إلغاء", message)
            self.add_to_history(message)

    # --- دوال السجل ---
    def add_to_history(self, message):
        self.view.history_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.view.history_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.view.history_text.see(tk.END)
        self.view.history_text.config(state=tk.DISABLED)

    # /compression_tool/compression_controller.py
# ... (كل الكود الذي كتبناه في الرد السابق) ...

    def clear_history(self):
        if messagebox.askyesno("تأكيد", "هل تريد مسح السجل؟"):
            self.view.history_text.config(state=tk.NORMAL)
            self.view.history_text.delete('1.0', tk.END)
            self.view.history_text.config(state=tk.DISABLED)
            self.add_to_history("تم مسح السجل.")

    def export_history(self):
        """
        يفتح مربع حوار لحفظ محتويات السجل في ملف نصي.
        """
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="compression_log.txt",
            title="تصدير السجل"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.view.history_text.get('1.0', tk.END))
                messagebox.showinfo("نجاح", "تم تصدير السجل بنجاح!")
                self.add_to_history(f"تم تصدير السجل إلى: {path}")
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل تصدير السجل: {e}")


    
