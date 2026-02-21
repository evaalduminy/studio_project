# /compression_tool/compression_model.py
import zipfile
import os
import wave
import struct
from PIL import Image

class CompressionModel:
    """
    فئة الـ Model لأداة الضغط.
    مسؤولة عن كل عمليات الضغط الفعلية للملفات والصور والصوت.
    """
    def __init__(self):
        self.is_compressing = True

    def compress_general_files(self, files, output_path, compression_level, password, progress_callback):
        try:
            total_files = len(files)
            compression_map = {"عادي": zipfile.ZIP_STORED, "عالي": zipfile.ZIP_DEFLATED, "أقصى ضغط": zipfile.ZIP_BZIP2}
            compression = compression_map.get(compression_level, zipfile.ZIP_DEFLATED)
            
            original_size = sum(os.path.getsize(f) for f in files if os.path.isfile(f))

            with zipfile.ZipFile(output_path, 'w', compression=compression, allowZip64=True) as zipf:
                if password:
                    zipf.setpassword(password.encode('utf-8'))
                
                for i, file_path in enumerate(files):
                    if not self.is_compressing:
                        raise InterruptedError("تم إلغاء العملية.")
                    
                    file_name = os.path.basename(file_path)
                    progress_callback((i / total_files) * 100, f"جاري ضغط {file_name}...")
                    zipf.write(file_path, file_name)
            
            if not self.is_compressing: return False, "تم إلغاء العملية."

            compressed_size = os.path.getsize(output_path)
            ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            return True, f"تم الضغط بنجاح! نسبة الضغط: {ratio:.1f}%"
        except Exception as e:
            if os.path.exists(output_path): os.remove(output_path)
            return False, f"فشل الضغط: {e}"

    def compress_images(self, files, output_dir, quality, output_format, resize_factor, progress_callback):
        try:
            total_files = len(files)
            for i, file_path in enumerate(files):
                if not self.is_compressing:
                    raise InterruptedError("تم إلغاء العملية.")
                
                file_name = os.path.basename(file_path)
                progress_callback((i / total_files) * 100, f"جاري ضغط {file_name}...")

                with Image.open(file_path) as img:
                    if resize_factor != 1.0:
                        new_size = (int(img.width * resize_factor), int(img.height * resize_factor))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    base_name, old_ext = os.path.splitext(file_name)
                    output_ext = f".{output_format.lower()}" if output_format != "نفس التنسيق الأصلي" else old_ext.lower()
                    output_path = os.path.join(output_dir, f"{base_name}_compressed{output_ext}")
                    
                    if output_ext in ['.jpg', '.jpeg'] and img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    
                    save_params = {'quality': quality}
                    if output_ext == '.webp':
                        save_params['method'] = 6
                    
                    img.save(output_path, **save_params)
            
            if not self.is_compressing: return False, "تم إلغاء العملية."
            return True, f"تم ضغط {total_files} صورة بنجاح."
        except Exception as e:
            return False, f"فشل ضغط الصور: {e}"

    def compress_audio(self, files, output_dir, quality_factor, new_rate, progress_callback):
        try:
            total_files = len(files)
            for i, file_path in enumerate(files):
                if not self.is_compressing:
                    raise InterruptedError("تم إلغاء العملية.")
                
                file_name = os.path.basename(file_path)
                progress_callback((i / total_files) * 100, f"جاري معالجة {file_name}...")

                with wave.open(file_path, 'rb') as wav_in:
                    params = wav_in.getparams()
                    n_channels, samp_width, _, n_frames = params[:4]
                    frames = wav_in.readframes(n_frames)

                    if samp_width > 1 and quality_factor < 1.0:
                        unpacked = struct.iter_unpack(f'<{n_channels}h', frames)
                        packed = b''.join(struct.pack(f'<{n_channels}h', *(int(s * quality_factor) for s in frame)) for frame in unpacked)
                        frames = packed

                    output_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_compressed.wav")
                    with wave.open(output_path, 'wb') as wav_out:
                        wav_out.setparams((n_channels, samp_width, new_rate, len(frames) // (n_channels * samp_width), params[4], params[5]))
                        wav_out.writeframes(frames)
            
            if not self.is_compressing: return False, "تم إلغاء العملية."
            return True, f"تمت معالجة {total_files} ملف صوتي بنجاح."
        except Exception as e:
            return False, f"فشل معالجة الصوت: {e}"
