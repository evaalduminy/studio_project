# /audio_editor/audio_controller.py
from .audio_model import AudioModel
from .audio_view import AudioView
from tkinter import filedialog, messagebox
import sounddevice as sd
import threading
import time
import os

class AudioController:
    """
    فئة الـ Controller لمحرر الصوت.
    تربط بين الواجهة والمنطق وتدير حالة التشغيل.
    """
    def __init__(self, parent):
        self.model = AudioModel()
        self.view = AudioView(parent)
        
        # --- متغيرات حالة التشغيل ---
        self.is_playing = False
        self.current_position_sec = 0
        self.playback_thread = None
        self.ui_update_thread = None
        
        # --- متغيرات التحديد ---
        self.selection_start_pixel = None
        self.selection_end_pixel = None
        
        self.bind_commands()

    def bind_commands(self):
        """ربط كل الأوامر والأحداث."""
        # الأزرار الرئيسية
        self.view.open_button.configure(command=self.open_audio)
        self.view.save_button.configure(command=self.save_audio)
        self.view.play_button.configure(command=self.toggle_playback)
        
        # أزرار التحرير
        self.view.cut_button.configure(command=self.cut_selection)
        self.view.copy_button.configure(command=self.copy_selection)
        self.view.paste_button.configure(command=self.paste_selection)
        
        # أزرار التأثيرات
        self.view.amplify_button.configure(command=lambda: self.apply_effect('amplify'))
        self.view.noise_gate_button.configure(command=lambda: self.apply_effect('noise_gate'))
        self.view.reverb_button.configure(command=lambda: self.apply_effect('reverb'))
        self.view.reverse_button.configure(command=lambda: self.apply_effect('reverse'))
        
        # أحداث الكانفاس
        self.view.waveform_canvas.bind("<Configure>", lambda e: self.update_view())
        self.view.waveform_canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.view.waveform_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.view.waveform_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

    def update_view(self):
        """تحديث الواجهة بالكامل بناءً على حالة النموذج."""
        self.view.draw_waveform(self.model.audio_data)
        self.view.draw_selection(self.selection_start_pixel, self.selection_end_pixel)
        self.view.draw_playhead(self.seconds_to_pixels(self.current_position_sec))
        self.update_time_labels()

    def open_audio(self):
        if self.model.unsaved_changes:
            if not messagebox.askyesno("تأكيد", "لديك تعديلات غير محفوظة. هل تريد المتابعة؟"):
                return
        path = filedialog.askopenfilename(title="اختر ملف صوتي", filetypes=[("ملفات الصوت", "*.wav *.mp3 *.flac")])
        if path:
            success, msg = self.model.load_audio(path)
            if success:
                self.current_position_sec = 0
                self.view.file_label.configure(text=os.path.basename(path))
                self.update_view()
            else:
                messagebox.showerror("خطأ", msg)

    def save_audio(self):
        if self.model.audio_data is None: return
        path = filedialog.asksaveasfilename(title="حفظ الملف الصوتي", defaultextension=".wav", filetypes=[("WAV", "*.wav")])
        if path:
            success, msg = self.model.save_audio(path)
            if success:
                messagebox.showinfo("نجاح", msg)
            else:
                messagebox.showerror("خطأ", msg)

    # --- دوال التحرير ---
    def get_selection_times(self):
        """الحصول على أزمنة البداية والنهاية للتحديد."""
        if self.selection_start_pixel is None or self.selection_end_pixel is None:
            return 0, 0
        start_sec = self.pixels_to_seconds(min(self.selection_start_pixel, self.selection_end_pixel))
        end_sec = self.pixels_to_seconds(max(self.selection_start_pixel, self.selection_end_pixel))
        return start_sec, end_sec

    def cut_selection(self):
        start_sec, end_sec = self.get_selection_times()
        if self.model.cut_audio(start_sec, end_sec):
            self.update_view()
        else:
            messagebox.showwarning("تحذير", "الرجاء تحديد جزء من الموجة أولاً.")

    def copy_selection(self):
        start_sec, end_sec = self.get_selection_times()
        if self.model.copy_audio(start_sec, end_sec):
            messagebox.showinfo("نجاح", "تم نسخ الجزء المحدد.")
        else:
            messagebox.showwarning("تحذير", "الرجاء تحديد جزء من الموجة أولاً.")

    def paste_selection(self):
        if self.model.paste_audio(self.current_position_sec):
            self.update_view()
        else:
            messagebox.showwarning("تحذير", "الحافظة فارغة.")

    def apply_effect(self, effect_name):
        start_sec, end_sec = self.get_selection_times()
        if start_sec == end_sec:
            if not messagebox.askyesno("تأكيد", "لم يتم تحديد أي جزء. هل تريد تطبيق التأثير على الملف بأكمله؟"):
                return
        
        if self.model.apply_effect(effect_name, start_sec, end_sec):
            self.update_view()
            messagebox.showinfo("نجاح", "تم تطبيق التأثير.")

    # --- دوال التحكم بالتشغيل ---
    def toggle_playback(self):
        if self.model.audio_data is None: return
        if self.is_playing:
            self.stop_playback()
        else:
            self.start_playback()

    def start_playback(self):
        if self.is_playing: return
        self.is_playing = True
        self.view.play_button.configure(text="⏹️ إيقاف")
        self.playback_thread = threading.Thread(target=self._audio_playback_worker, daemon=True)
        self.playback_thread.start()
        self.ui_update_thread = threading.Thread(target=self._ui_update_worker, daemon=True)
        self.ui_update_thread.start()

    def stop_playback(self):
        self.is_playing = False
        sd.stop()
        self.view.play_button.configure(text="▶ تشغيل")

    def _audio_playback_worker(self):
        start_sample = int(self.current_position_sec * self.model.sample_rate)
        try:
            sd.play(self.model.audio_data[start_sample:], self.model.sample_rate, blocking=True)
        except Exception as e:
            print(f"Playback error: {e}")
        self.view.parent.after(0, self.stop_playback_from_thread)

    def _ui_update_worker(self):
        start_time = time.time()
        initial_position = self.current_position_sec
        while self.is_playing:
            elapsed = time.time() - start_time
            self.current_position_sec = initial_position + elapsed
            if self.current_position_sec >= self.model.duration:
                self.current_position_sec = self.model.duration
                self.is_playing = False
            
            self.update_time_labels()
            self.view.draw_playhead(self.seconds_to_pixels(self.current_position_sec))
            time.sleep(0.05)
        self.view.parent.after(0, self.stop_playback_from_thread)

    def stop_playback_from_thread(self):
        if self.current_position_sec >= self.model.duration - 0.1:
            self.current_position_sec = 0
        self.stop_playback()
        self.update_time_labels()
        self.view.draw_playhead(self.seconds_to_pixels(self.current_position_sec))

    # --- دوال أحداث الكانفاس ---
    def on_canvas_press(self, event):
        self.selection_start_pixel = event.x
        self.selection_end_pixel = event.x
        self.view.draw_selection(self.selection_start_pixel, self.selection_end_pixel)

    def on_canvas_drag(self, event):
        self.selection_end_pixel = event.x
        self.view.draw_selection(self.selection_start_pixel, self.selection_end_pixel)

    def on_canvas_release(self, event):
        if self.selection_start_pixel == self.selection_end_pixel:
            self.current_position_sec = self.pixels_to_seconds(event.x)
            self.selection_start_pixel = None
            self.selection_end_pixel = None
            self.update_view()

    # --- دوال مساعدة ---
    def pixels_to_seconds(self, pixels):
        width = self.view.waveform_canvas.winfo_width()
        return (pixels / width) * self.model.duration if self.model.duration > 0 else 0

    def seconds_to_pixels(self, seconds):
        width = self.view.waveform_canvas.winfo_width()
        return (seconds / self.model.duration) * width if self.model.duration > 0 else 0

    def format_time(self, seconds):
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_time_labels(self):
        current_str = self.format_time(self.current_position_sec)
        duration_str = self.format_time(self.model.duration)
        self.view.update_time_label(current_str, duration_str)
        progress = self.current_position_sec / self.model.duration if self.model.duration > 0 else 0
        self.view.update_progress_bar(progress)
