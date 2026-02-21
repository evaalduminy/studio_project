# /main.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import time

# استيراد الـ Controllers لكل تبويب
from photo_editor.photo_controller import PhotoController
from audio_editor.audio_controller import AudioController
from compression_tool.compression_controller import CompressionController

class MainApplication:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("استوديو المحتوى الاحترافي ")
        self.root.geometry("1200x800")
        
        self.setup_ui()
        # ربط دالة الإغلاق الآمن
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        self.tab_view = ctk.CTkTabview(self.root)
        self.tab_view.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- تبويب محرر الصور ---
        self.photo_tab = self.tab_view.add("📷 محرر الصور")
        self.photo_controller = PhotoController(self.photo_tab)
        
        # --- تبويب محرر الصوت ---
        self.audio_tab = self.tab_view.add("🎵 محرر الصوت")
        self.audio_controller = AudioController(self.audio_tab)

        # --- تبويب أداة الضغط ---
        # لاحظ أننا نمرر التبويب نفسه كـ "أب" للـ View داخل الـ Controller
        self.compression_tab_parent = self.tab_view.add("🗜️ أداة الضغط")
        self.compression_controller = CompressionController(self.compression_tab_parent)

    def on_closing(self):
        """
        دالة يتم استدعاؤها عند محاولة إغلاق التطبيق.
        تتحقق من وجود تغييرات غير محفوظة.
        """
        # إيقاف تشغيل الصوت إذا كان يعمل
        if self.audio_controller.is_playing:
            self.audio_controller.stop_playback()
            self.root.update_idletasks()
            time.sleep(0.1)

        # التحقق من محرر الصور
        if self.photo_controller.model.unsaved_changes:
            if not messagebox.askyesno("محرر الصور", "لديك تعديلات في محرر الصور غير محفوظة. هل تريد الخروج على أي حال؟", icon='warning'):
                return # إلغاء عملية الخروج

        # التحقق من محرر الصوت
        if self.audio_controller.model.unsaved_changes:
            if not messagebox.askyesno("محرر الصوت", "لديك تعديلات في محرر الصوت غير محفوظة. هل تريد الخروج على أي حال؟", icon='warning'):
                return # إلغاء عملية الخروج
        
        # إذا وافق المستخدم على كل شيء، يتم تدمير النافذة
        self.root.destroy()

    def run(self):
        """تشغيل الحلقة الرئيسية للتطبيق."""
        self.root.mainloop()

if __name__ == "__main__":
    # تأكد من تثبيت كل المكتبات المطلوبة
    # pip install customtkinter Pillow soundfile sounddevice numpy
    app = MainApplication()
    app.run()
