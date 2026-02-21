# /audio_editor/audio_model.py
import soundfile as sf
import numpy as np
import os


class AudioModel:
    """
    فئة الـ Model لمحرر الصوت.
    مسؤولة عن كل عمليات معالجة بيانات الصوت وحالتها.
    """
    def __init__(self):
        self.audio_path = None
        self.audio_data = None
        self.sample_rate = None
        self.duration = 0
        self.clipboard_data = None
        self.unsaved_changes = False

    def load_audio(self, file_path):
        """تحميل ملف صوتي من مسار."""
        try:
            self.audio_path = file_path
            self.audio_data, self.sample_rate = sf.read(file_path, always_2d=True)
            # تحويل إلى mono إذا كان stereo
            if self.audio_data.ndim > 1:
                self.audio_data = np.mean(self.audio_data, axis=1)
            self.duration = len(self.audio_data) / self.sample_rate
            self.unsaved_changes = False
            return True, "تم تحميل الملف."
        except Exception as e:
            return False, f"فشل تحميل الملف: {e}"

    def save_audio(self, file_path):
        """حفظ بيانات الصوت الحالية في ملف."""
        if self.audio_data is None:
            return False, "لا يوجد صوت للحفظ."
        try:
            sf.write(file_path, self.audio_data, self.sample_rate)
            self.unsaved_changes = False
            return True, "تم حفظ الملف."
        except Exception as e:
            return False, f"فشل الحفظ: {e}"

    def get_selection_samples(self, start_sec, end_sec):
        """تحويل أزمنة التحديد إلى مؤشرات العينات."""
        start_sample = int(start_sec * self.sample_rate)
        end_sample = int(end_sec * self.sample_rate)
        return start_sample, end_sample

    def cut_audio(self, start_sec, end_sec):
        """قص جزء من الصوت وحفظه في الحافظة."""
        start_sample, end_sample = self.get_selection_samples(start_sec, end_sec)
        if start_sample == end_sample: return False
        
        self.clipboard_data = self.audio_data[start_sample:end_sample].copy()
        self.audio_data = np.delete(self.audio_data, np.arange(start_sample, end_sample))
        self.duration = len(self.audio_data) / self.sample_rate
        self.unsaved_changes = True
        return True

    def copy_audio(self, start_sec, end_sec):
        """نسخ جزء من الصوت إلى الحافظة."""
        start_sample, end_sample = self.get_selection_samples(start_sec, end_sec)
        if start_sample == end_sample: return False
        
        self.clipboard_data = self.audio_data[start_sample:end_sample].copy()
        return True

    def paste_audio(self, position_sec):
        """لصق الصوت من الحافظة في موضع معين."""
        if self.clipboard_data is None: return False
        
        insert_sample = int(position_sec * self.sample_rate)
        self.audio_data = np.insert(self.audio_data, insert_sample, self.clipboard_data)
        self.duration = len(self.audio_data) / self.sample_rate
        self.unsaved_changes = True
        return True

    def apply_effect(self, effect_name, start_sec, end_sec):
        """تطبيق تأثير على جزء محدد أو على كامل الصوت."""
        start_sample, end_sample = self.get_selection_samples(start_sec, end_sec)
        
        is_full_track = start_sample == end_sample
        target_audio = self.audio_data if is_full_track else self.audio_data[start_sample:end_sample]

        processed_audio = None
        if effect_name == 'amplify':
            processed_audio = target_audio * 1.5
        elif effect_name == 'noise_gate':
            threshold = 0.02
            processed_audio = np.where(np.abs(target_audio) < threshold, 0, target_audio)
        elif effect_name == 'reverb':
            delay_samples = int(self.sample_rate * 0.2)
            decay = 0.5
            reverb_part = np.zeros_like(target_audio)
            reverb_part[delay_samples:] = target_audio[:-delay_samples] * decay
            processed_audio = target_audio + reverb_part
        elif effect_name == 'reverse':
            processed_audio = target_audio[::-1]

        if processed_audio is not None:
            # تطبيع الصوت لمنع التقطيع (Clipping)
            max_val = np.max(np.abs(processed_audio))
            if max_val > 0:
                processed_audio = processed_audio / max_val
            
            if is_full_track:
                self.audio_data = processed_audio
            else:
                self.audio_data[start_sample:end_sample] = processed_audio
            
            self.unsaved_changes = True
            return True
        return False
