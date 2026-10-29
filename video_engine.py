import os
import glob
from PIL import Image, ImageDraw, ImageFile
from gtts import gTTS

# Fix for truncated/incomplete image downloads
ImageFile.LOAD_TRUNCATED_IMAGES = True

try:
    from moviepy import (
        ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
    )
except ImportError:
    from moviepy.editor import (
        ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
    )

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 24

def generate_voiceover_audio(text: str, output_path: str):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(output_path)

def prepare_image(image_path: str, target_w=VIDEO_WIDTH, target_h=VIDEO_HEIGHT) -> str:
    processed_path = f"temp_processed_{os.path.basename(image_path)}"
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            target_ratio = target_w / target_h
            img_ratio = img.width / img.height
            
            if img_ratio > target_ratio:
                new_h = target_h
                new_w = int(target_h * img_ratio)
            else:
                new_w = target_w
                new_h = int(target_w / img_ratio)
                
            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            img_cropped = img_resized.crop((left, top, left + target_w, top + target_h))
            img_cropped.save(processed_path)
            return processed_path
    except Exception:
        # Fallback card if the uploaded image file is completely corrupt
        img = Image.new("RGB", (target_w, target_h), color=(30, 41, 59))
        d = ImageDraw.Draw(img)
        d.text((50, target_h // 2), "Property Image", fill=(255, 255, 255))
        img.save(processed_path)
        return processed_path

def build_property_video(property_data: dict, image_paths: list, output_filename: str = "property_promo.mp4") -> str:
    from script_generator import generate_property_script

    if not image_paths:
        raise ValueError("At least 1 property image is required.")

    script_data = generate_property_script(property_data)
    scenes = script_data["scenes"]
    
    audio_path = "temp_voiceover.mp3"
    generate_voiceover_audio(script_data["full_voiceover"], audio_path)
    full_audio = AudioFileClip(audio_path)
    
    total_audio_duration = full_audio.duration
    scene_duration = max(3.5, total_audio_duration / len(scenes))
    
    video_clips = []
    
    for idx, scene in enumerate(scenes):
        img_file = image_paths[idx % len(image_paths)]
        processed_img = prepare_image(img_file)
        
        img_clip = ImageClip(processed_img)
        if hasattr(img_clip, "with_duration"):
            img_clip = img_clip.with_duration(scene_duration)
        else:
            img_clip = img_clip.set_duration(scene_duration)
        
        txt_img = Image.new("RGBA", (VIDEO_WIDTH, 300), (0, 0, 0, 180))
        draw = ImageDraw.Draw(txt_img)
        caption_text = scene["caption"]
        draw.text((30, 30), caption_text, fill=(255, 255, 255))
        
        temp_txt_path = f"temp_txt_{idx}.png"
        txt_img.save(temp_txt_path)
        
        txt_clip = ImageClip(temp_txt_path)
        if hasattr(txt_clip, "with_duration"):
            txt_clip = txt_clip.with_duration(scene_duration).with_position(('center', 'bottom'))
        else:
            txt_clip = txt_clip.set_duration(scene_duration).set_position(('center', 'bottom'))
        
        scene_composite = CompositeVideoClip([img_clip, txt_clip])
        video_clips.append(scene_composite)
        
    final_video = concatenate_videoclips(video_clips, method="compose")
    
    if hasattr(final_video, "with_audio"):
        final_video = final_video.with_audio(full_audio)
    else:
        final_video = final_video.set_audio(full_audio)
    
    os.makedirs("output", exist_ok=True)
    final_output_path = os.path.join("output", output_filename)
    
    final_video.write_videofile(
        final_output_path, 
        fps=FPS, 
        codec="libx264", 
        audio_codec="aac",
        logger=None
    )
    
    for temp_f in glob.glob("temp_*"):
        try:
            os.remove(temp_f)
        except OSError:
            pass
            
    return final_output_path