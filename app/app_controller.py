# /app/app_controller.py
import customtkinter as ctk
from tkinter import messagebox
import time

# استيراد العرض الرئيسي والمتحكمات الفرعية
from .app_view import AppView
from photo_editor.photo_controller import PhotoController
from audio_editor.audio_controller import AudioController
from compression_tool.compression_controller import CompressionController

class AppController:
    """
    فئة المتحكم الرئيسية للتطبيق.
    مسؤولة عن تجميع كل الوحدات (Modules) معاً وإدارة الأحداث العامة.
    """
    def __init__(self, root):
        self.view = AppView(root)

        # --- تجميع الوحدات ---
        # إنشاء كل متحكم وتمرير التبويب الخاص به إليه
        self.photo_controller = PhotoController(self.view.photo_tab)
        self.audio_controller = AudioController(self.view.audio_tab)
        self.compression_controller = CompressionController(self.view.compression_tab)

        # ربط حدث إغلاق النافذة بالدالة المخصصة
        self.view.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """
        دالة يتم استدعاؤها عند محاولة إغلاق التطبيق.
        تستشير كل متحكم فرعي قبل الإغلاق.
        """
        # إيقاف تشغيل الصوت إذا كان يعمل
        if self.audio_controller.model.is_playing:
            self.audio_controller.stop_playback()
            self.view.root.update_idletasks()
            time.sleep(0.1)

        # التحقق من محرر الصور
        if self.photo_controller.model.unsaved_changes:
            if not messagebox.askyesno("محرر الصور", "لديك تعديلات غير محفوظة. هل تريد الخروج؟", icon='warning'):
                return # إلغاء الإغلاق

        # التحقق من محرر الصوت
        if self.audio_controller.model.unsaved_changes:
            if not messagebox.askyesno("محرر الصوت", "لديك تعديلات غير محفوظة. هل تريد الخروج؟", icon='warning'):
                return # إلغاء الإغلاق
        
        self.view.root.destroy()

    def run(self):
        """تشغيل الحلقة الرئيسية للتطبيق."""
        self.view.root.mainloop()
