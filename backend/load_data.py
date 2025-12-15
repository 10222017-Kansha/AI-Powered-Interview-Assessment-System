import gdown
import os
import gdown
import subprocess
import re

# drive_regex = re.compile(
#     r"https?://drive\.google\.com/file/d/[a-zA-Z0-9_-]+"
# )


# def extract_interview_links(payload: dict):
#     interviews = (
#         payload.get("data", {})
#         .get("reviewChecklists", {})
#         .get("interviews", [])
#     )

#     results_dict = {
#         item["positionId"]: item["recordedVideoUrl"]
#         for item in interviews
#         if item.get("isVideoExist") and item.get("recordedVideoUrl")
#     }

#     return results_dict


# def get_drive_id(url):
#     # Retrieving the file ID from google drive URL
#     return url.split('/d/')[1].split('/')[0]


# def download_video_no_audio(links_dict):
#     output_dir = "videos_without_audio"
#     os.makedirs(output_dir, exist_ok=True)
#     print("=== Downloading Videos Without Audio ===")
#     video_paths = []

#     for key, url in links_dict.items():
#         print(f"\n=== Processing Video ID: {key} ===")
        
#         file_id = get_drive_id(url)
#         temp_filename = f"temp_raw_{key}.mp4"
#         final_filename = os.path.join(output_dir, f"video_{key}_mute.mp4")
        
#         # Downloading video
#         print("Downloading...")
#         gdown.download(id=file_id, output=temp_filename, quiet=False, fuzzy=True)
        
#         if not os.path.exists(temp_filename):
#             print(f"Gagal mengunduh file {key}")
#             continue

#         # Deleting audio from videos
#         print(f"Deleting audio...")
#         cmd = [
#             'ffmpeg', 
#             '-y', 
#             '-i', temp_filename, 
#             '-c', 'copy', 
#             '-an', 
#             final_filename
#         ]
        
#         try:
#             subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
#             # Saving video path into list
#             absolute_path = os.path.abspath(final_filename)
#             video_paths.append(absolute_path)
            
#         except subprocess.CalledProcessError:
#             print(f"Error memproses video {key}.")
            
#         except FileNotFoundError:
#             print("Error: FFmpeg tidak ditemukan.")
        
#         if os.path.exists(temp_filename):
#             os.remove(temp_filename)
            
#     return video_paths

# def download_and_extract_audio(links_dict):
#     output_dir = "audios_only"
#     os.makedirs(output_dir, exist_ok=True)
#     print("=== Downloading Audio Only ===")
#     audio_paths = []

#     for key, url in links_dict.items():
#         print(f"\n--- Processing ID: {key} ---")
        
#         file_id = get_drive_id(url)
#         temp_filename = f"temp_video_{key}.mp4"
#         final_filename = os.path.join(output_dir, f"audio_{key}.mp3")
#         gdown.download(id=file_id, output=temp_filename, quiet=False, fuzzy=True)
        
#         if not os.path.exists(temp_filename):
#             print(f"Gagal mengunduh file {key}")
#             continue

#         # Extract the audio
#         cmd = [
#             'ffmpeg', 
#             '-y', 
#             '-i', temp_filename, 
#             '-vn', 
#             '-acodec', 'libmp3lame', 
#             '-ab', '192k', 
#             final_filename
#         ]
        
#         try:
#             subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
#             print(f"Sukses: {final_filename}")
#             # Saving audio path into list
#             absolute_path = os.path.abspath(final_filename)
#             audio_paths.append(absolute_path)
            
#         except subprocess.CalledProcessError:
#             print(f"Error konversi audio {key}.")
        
#         if os.path.exists(temp_filename):
#             os.remove(temp_filename)
            
#     return audio_paths

def parse_input_json(json_data):
    video_links = {}
    try:
        interviews = json_data['data']['reviewChecklists']['interviews']
        for item in interviews:
            vid_url = item.get('recordedVideoUrl', '')
            pos_id = item.get('positionId')
            if vid_url and ("drive.google.com" in vid_url or "youtube" in vid_url):
                video_links[pos_id] = vid_url
    except Exception:
        return {}
    return video_links

def process_videos_pipeline(links_dict):
    output_audio_dir = "temp_audios"
    output_video_dir = "temp_videos_mute"
    os.makedirs(output_audio_dir, exist_ok=True)
    os.makedirs(output_video_dir, exist_ok=True)
    
    audio_paths = []
    video_paths = []
    sorted_ids = sorted(links_dict.keys())
    
    for key in sorted_ids:
        url = links_dict[key]
        try:
            if "drive.google.com" in url:
                file_id = url.split('/d/')[1].split('/')[0]
                temp_mp4 = f"temp_raw_{key}.mp4"
                gdown.download(id=file_id, output=temp_mp4, quiet=True, fuzzy=True)
            else:
                audio_paths.append(None); video_paths.append(None)
                continue

            if os.path.exists(temp_mp4):
                # Extract Audio
                audio_out = os.path.join(output_audio_dir, f"audio_{key}.mp3")
                subprocess.run(['ffmpeg', '-y', '-i', temp_mp4, '-vn', '-acodec', 'libmp3lame', '-ab', '192k', audio_out], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                audio_paths.append(os.path.abspath(audio_out))
                
                # Mute Video
                video_out = os.path.join(output_video_dir, f"video_{key}_mute.mp4")
                subprocess.run(['ffmpeg', '-y', '-i', temp_mp4, '-c', 'copy', '-an', video_out], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                video_paths.append(os.path.abspath(video_out))
                
                os.remove(temp_mp4)
            else:
                audio_paths.append(None); video_paths.append(None)
        except Exception:
            audio_paths.append(None); video_paths.append(None)

    return audio_paths, video_paths