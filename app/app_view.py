# /app/app_view.py
import customtkinter as ctk
import tkinter as tk

class AppView:
    """
    فئة العرض الرئيسية للتطبيق.
    مسؤولة عن إنشاء الهيكل الأساسي للواجهة (النافذة والتبويبات).
    """
    def __init__(self, root):
        self.root = root
        self.root.title("استوديو المحتوى المتكامل")
        self.root.geometry("1200x800")

        # إنشاء عنصر التبويبات الرئيسي
        self.tab_view = ctk.CTkTabview(self.root)
        self.tab_view.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # إنشاء التبويبات الفارغة التي سيتم ملؤها لاحقاً
        self.photo_tab = self.tab_view.add("📷 محرر الصور")
        self.audio_tab = self.tab_view.add("🎵 محرر الصوت")
        self.compression_tab = self.tab_view.add("🗜️ أداة الضغط")
