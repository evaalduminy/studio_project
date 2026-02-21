# /photo_editor/photo_model.py

# --- الاستيرادات ---
import os
import copy
import threading
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps

class PhotoModel:
    """
    فئة الـ Model لمحرر الصور.
    مسؤولة عن كل عمليات معالجة بيانات الصور وحالتها (الطبقات، التاريخ، ...).
    لا تحتوي على أي كود متعلق بالواجهة.
    """
    def __init__(self):
        # --- حالة النموذج ---
        self.image_path = None
        self.layers = []
        self.history = []
        self.history_index = -1
        self.brush_size = 10
        self.brush_color = (255, 0, 0, 255)
        self.unsaved_changes = False

    # --- دوال تحميل وحفظ ---
    def load_image(self, file_path):
        """تحميل صورة من مسار وتعيينها كطبقة أساسية."""
        self.image_path = file_path
        image = Image.open(file_path)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        self.layers = [{
            'name': 'الطبقة الأساسية',
            'image': image,
            'opacity': 1.0,
            'visible': True,
            'x': 0, 'y': 0,
            'is_draw_layer': False
        }]
        self.reset_history()
        self.unsaved_changes = False

    def save_image(self, path):
        """دمج كل الطبقات وحفظ الصورة النهائية في مسار معين."""
        final_image = self.get_composited_image()
        if not final_image: return

        if ".jpg" in path.lower() or ".jpeg" in path.lower():
            final_image.convert("RGB").save(path)
        else:
            final_image.save(path)
        self.image_path = path
        self.unsaved_changes = False

    # --- دوال الطبقات ---
    def add_image_layer(self, file_path):
        """إضافة صورة جديدة كطبقة منفصلة."""
        layer_image = Image.open(file_path)
        if layer_image.mode != 'RGBA':
            layer_image = layer_image.convert('RGBA')
        
        layer_info = {
            'name': os.path.basename(file_path), 'image': layer_image, 
            'opacity': 1.0, 'visible': True, 'x': 0, 'y': 0, 'is_draw_layer': False
        }
        self.layers.append(layer_info)
        self.add_to_history()

    def add_text_layer(self, text, size, color):
        """إنشاء صورة من نص وإضافتها كطبقة جديدة."""
        try:
            font = ImageFont.truetype("arial.ttf", size)
        except IOError:
            font = ImageFont.load_default()
        
        bbox = font.getbbox(text)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        text_image = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_image)
        draw.text((-bbox[0], -bbox[1]), text, font=font, fill=color)
        
        layer_info = {
            'name': f'نص: "{text[:10]}..."', 'image': text_image,
            'opacity': 1.0, 'visible': True, 'x': 0, 'y': 0, 'is_draw_layer': False
        }
        self.layers.append(layer_info)
        self.add_to_history()

    def add_draw_layer(self):
        """إضافة طبقة شفافة مخصصة للرسم."""
        if not self.layers: return -1
        base_size = self.layers[0]['image'].size
        draw_layer_image = Image.new("RGBA", base_size, (0, 0, 0, 0))
        layer_info = {
            'name': 'طبقة رسم', 'image': draw_layer_image,
            'opacity': 1.0, 'visible': True, 'x': 0, 'y': 0, 'is_draw_layer': True
        }
        self.layers.append(layer_info)
        self.add_to_history()
        return len(self.layers) - 1

    def remove_layer(self, layer_index):
        """حذف طبقة معينة (لا يمكن حذف الطبقة الأساسية)."""
        if layer_index > 0 and layer_index < len(self.layers):
            del self.layers[layer_index]
            self.add_to_history()
            return True
        return False

    # --- دوال معالجة الصور ---
    def apply_filter(self, layer_index, filter_type):
        """تطبيق فلتر على طبقة معينة."""
        if 0 <= layer_index < len(self.layers):
            self.layers[layer_index]['image'] = self.layers[layer_index]['image'].filter(filter_type)
            self.add_to_history()

    def apply_adjustments(self, layer_index, brightness, contrast, saturation, sharpness):
        """تطبيق التعديلات (سطوع، تباين...) على طبقة."""
        if not (0 <= layer_index < len(self.layers)): return
        
        image = self.layers[layer_index]['image']
        enhancer = ImageEnhance.Brightness(image); image = enhancer.enhance(brightness)
        enhancer = ImageEnhance.Contrast(image); image = enhancer.enhance(contrast)
        enhancer = ImageEnhance.Color(image); image = enhancer.enhance(saturation)
        enhancer = ImageEnhance.Sharpness(image); image = enhancer.enhance(sharpness)
        
        self.layers[layer_index]['image'] = image
        self.add_to_history()

    def apply_transform(self, operation):
        """تطبيق عمليات التدوير والقلب على كل الطبقات."""
        if not self.layers: return

        base_size = self.layers[0]['image'].size
        new_base_size = base_size
        if operation in ['rotate_left', 'rotate_right']:
            new_base_size = (base_size[1], base_size[0])

        for layer in self.layers:
            img = layer['image']
            x, y = layer['x'], layer['y']
            
            if operation == 'rotate_left':
                img = img.rotate(90, expand=True)
                layer['x'], layer['y'] = y, new_base_size[1] - (x + layer['image'].size[0])
            elif operation == 'rotate_right':
                img = img.rotate(-90, expand=True)
                layer['x'], layer['y'] = new_base_size[0] - (y + layer['image'].size[1]), x
            elif operation == 'flip_horizontal':
                img = ImageOps.mirror(img)
                layer['x'] = new_base_size[0] - (x + img.width)
            elif operation == 'flip_vertical':
                img = ImageOps.flip(img)
                layer['y'] = new_base_size[1] - (y + img.height)
            
            layer['image'] = img
        
        self.add_to_history()

    def apply_threshold(self, layer_index, value):
        """تطبيق فلتر العتبة على طبقة معينة."""
        if not (0 <= layer_index < len(self.layers)): return
        
        layer = self.layers[layer_index]
        grayscale_img = layer['image'].convert("L")
        threshold_img = grayscale_img.point(lambda p: 255 if p > value else 0, '1')
        layer['image'] = threshold_img.convert("RGBA")
        self.add_to_history()

    def apply_crop(self, crop_box):
        """قص كل الطبقات بناءً على مربع التحديد."""
        if not self.layers or crop_box[0] >= crop_box[2] or crop_box[1] >= crop_box[3]:
            return

        for layer in self.layers:
            layer['image'] = layer['image'].crop(crop_box)
            layer['x'] -= crop_box[0]
            layer['y'] -= crop_box[1]
        
        self.add_to_history()

    def draw_on_layer(self, layer_index, last_point, current_point):
        """الرسم على طبقة معينة."""
        if not (0 <= layer_index < len(self.layers)): return
        
        draw_layer = self.layers[layer_index]['image']
        draw = ImageDraw.Draw(draw_layer)
        
        if last_point:
            draw.line([last_point, current_point], fill=self.brush_color, width=self.brush_size)
        else:
            radius = self.brush_size / 2
            bbox = (current_point[0] - radius, current_point[1] - radius, 
                    current_point[0] + radius, current_point[1] + radius)
            draw.ellipse(bbox, fill=self.brush_color)
        self.add_to_history() # حفظ الرسم في التاريخ

    # --- دوال الحصول على الحالة ---
    def get_composited_image(self):
        """دمج كل الطبقات المرئية في صورة واحدة للعرض أو الحفظ."""
        if not self.layers: return None
        
        base_size = self.layers[0]['image'].size
        composite = Image.new('RGBA', base_size, (0, 0, 0, 0))
        
        for layer in self.layers:
            if layer['visible']:
                img_to_paste = layer['image'].copy()
                if layer['opacity'] < 1.0:
                    alpha = img_to_paste.split()[3]
                    alpha = ImageEnhance.Brightness(alpha).enhance(layer['opacity'])
                    img_to_paste.putalpha(alpha)
                composite.paste(img_to_paste, (layer['x'], layer['y']), img_to_paste)
        return composite

    # --- دوال إدارة التاريخ ---
    def add_to_history(self):
        """إضافة الحالة الحالية للطبقات إلى قائمة التاريخ."""
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        self.history.append(copy.deepcopy(self.layers))
        self.history_index += 1
        self.unsaved_changes = True

    def reset_history(self):
        """إعادة تعيين قائمة التاريخ عند فتح صورة جديدة."""
        self.history = []
        self.history_index = -1
        self.add_to_history()

    def undo(self):
        """العودة إلى الحالة السابقة في التاريخ."""
        if self.history_index > 0:
            self.history_index -= 1
            self.layers = copy.deepcopy(self.history[self.history_index])
            return True
        return False

    def redo(self):
        """التقدم إلى الحالة التالية في التاريخ."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.layers = copy.deepcopy(self.history[self.history_index])
            return True
        return False

    # --- دالة المعالجة الدفعية ---
    def process_batch_watermark(self, source_folder, watermark_path, save_folder, position, progress_callback):
        """منطق إضافة شعار مائي لمجموعة من الصور."""
        def worker():
            try:
                watermark = Image.open(watermark_path).convert('RGBA')
                image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
                image_files = [f for f in os.listdir(source_folder) if f.lower().endswith(image_extensions)]
                
                if not image_files:
                    progress_callback(1.0, "لا توجد صور في المجلد المحدد.", True)
                    return

                total_images = len(image_files)
                for i, filename in enumerate(image_files):
                    progress_callback((i) / total_images, f"جاري معالجة: {filename}", False)
                    
                    image_path = os.path.join(source_folder, filename)
                    with Image.open(image_path).convert('RGBA') as image:
                        wm_width = int(image.size[0] * 0.15)
                        wm_ratio = wm_width / watermark.size[0]
                        wm_height = int(watermark.size[1] * wm_ratio)
                        wm_resized = watermark.resize((wm_width, wm_height), Image.Resampling.LANCZOS)
                        
                        margin = 20
                        positions = {
                            "top_left": (margin, margin),
                            "top_right": (image.size[0] - wm_width - margin, margin),
                            "bottom_left": (margin, image.size[1] - wm_height - margin),
                            "bottom_right": (image.size[0] - wm_width - margin, image.size[1] - wm_height - margin)
                        }
                        pos = positions.get(position, "bottom_right")
                        
                        image.paste(wm_resized, pos, wm_resized)
                        
                        save_path = os.path.join(save_folder, f"marked_{filename}")
                        final_image = image.convert('RGB') if save_path.lower().endswith('.jpg') else image
                        final_image.save(save_path)
                
                progress_callback(1.0, f"اكتملت المعالجة بنجاح لـ {total_images} صورة.", True)
            except Exception as e:
                progress_callback(1.0, f"حدث خطأ فادح: {e}", True)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
