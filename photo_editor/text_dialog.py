# /photo_editor/text_dialog.py
import customtkinter as ctk
from tkinter import colorchooser, messagebox

class TextDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # --- الحل: حفظ الأب الحقيقي ---
        # هذا يضمن أن أي نافذة منبثقة جديدة ستظهر فوق النافذة الرئيسية
        self.main_parent = parent 
        
        self.title("إضافة نص")
        self.geometry("400x300")
        self.result = None
        
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
        self.color_button.configure(fg_color="#000000")
        self.color_button.color = (0, 0, 0, 255)
        self.color_button.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        add_button = ctk.CTkButton(self, text="إضافة", command=self.on_add)
        add_button.grid(row=3, column=0, columnspan=2, padx=10, pady=20)
        
        # هاتان الدالتان تضمنان أن هذه النافذة تبقى فوق النافذة الرئيسية
        self.transient(parent)
        self.grab_set()

    def choose_color(self):
        """
        يفتح نافذة اختيار اللون.
        الحل: استخدام self.main_parent كـ "أب" لضمان ظهورها في المقدمة.
        """
        color_code = colorchooser.askcolor(parent=self.main_parent, title="اختر لون النص")
        if color_code and color_code[0]:
            rgb, hex_color = color_code[0], color_code[1]
            self.color_button.configure(fg_color=hex_color)
            
            # حساب لون النص المناسب (أسود أو أبيض)
            text_color = "#000000" if (rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) > 186 else "#FFFFFF"
            self.color_button.configure(text_color=text_color)
            
            self.color_button.color = (int(rgb[0]), int(rgb[1]), int(rgb[2]), 255)

    def on_add(self):
        """
        يتم استدعاؤها عند الضغط على زر "إضافة".
        تتحقق من المدخلات وتجهز النتيجة.
        """
        text = self.text_entry.get()
        size_str = self.size_entry.get()
        
        if not text or not size_str.isdigit() or int(size_str) <= 0:
            # الحل: استخدام self.main_parent كـ "أب" لرسالة الخطأ
            messagebox.showerror("خطأ في الإدخال", "الرجاء إدخال نص وحجم خط صحيح (رقم أكبر من صفر).", parent=self.main_parent)
            return
        
        self.result = {
            "text": text,
            "size": int(size_str),
            "color": self.color_button.color
        }
        self.destroy()
