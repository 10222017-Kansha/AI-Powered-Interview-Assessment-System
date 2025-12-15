import streamlit as st
import json
import os
import base64
from pathlib import Path
from backend import generate_final_assessment_report
from backend import parse_input_json, process_videos_pipeline
from backend import transcript
from backend import evaluate_transcripts

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

bg_image_file = "background.png"
spinner_image_file = "jam_pasir.png"

st.set_page_config(page_title="AI Interview Assessor", page_icon="🤖", layout="wide")

bg_image_b64 = img_to_bytes(bg_image_file) if os.path.exists(bg_image_file) else ""
spinner_image_b64 = img_to_bytes(spinner_image_file) if os.path.exists(spinner_image_file) else ""

st.markdown(f"""
<style>
    .stApp {{
        background-image: url("data:image/png;base64,{bg_image_b64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    .stButton > button {{
        background-color: #2e4073; color: white; border-radius: 8px;
        padding: 12px 24px; font-size: 18px; font-weight: bold; border: none; width: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.3s;
    }}
    .stButton > button:hover {{ background-color: #1e2b4d; transform: translateY(-2px); }}
    [data-testid="stFileUploader"] {{
        background-color: rgba(255, 255, 255, 0.9); border-radius: 15px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    h1, h2, h3, p {{ font-family: 'Segoe UI', sans-serif; color: #2e4073; }}
    @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
    .loading-spinner {{
        display: block; margin-left: auto; margin-right: auto; width: 80px;
        animation: spin 2s linear infinite;
    }}
    .loading-text {{ text-align: center; color: #2e4073; font-size: 18px; margin-top: 15px; font-weight: 500; }}
</style>
""", unsafe_allow_html=True)

# Main UI
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<h3 style='text-align: center;'>KELOMPOK A25-C351 | Dicoding</h3>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>AI Powered Interview System</h1>", unsafe_allow_html=True)
    st.markdown("""
    <style>
    div.stButton > button {
        color: #000000;              
        background-color: #FFFFFF; 
        border: 2px solid black;
        padding: 10px 24px;
        border-radius: 5px;
    }
    
    
    div.stButton > button:hover {
        background-color: #FFFFFF; 
        color: #000000;
    }

    
    div.stButton {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Silahkan unggah file berformat .json di sini", type=['json'])

    if uploaded_file is None:
        st.info("Silakan unggah file JSON terlebih dahulu sebelum memulai analisis.")
    else:
        if uploaded_file.name != "payload.json":
            st.error("Nama file harus 'payload.json'. Silakan unggah file yang benar.")
        else:
            try:
                input_data = json.load(uploaded_file)
                # Panggil fungsi backend
                print(input_data)
                links = parse_input_json(input_data)
                
                if not links:
                    st.error("File JSON tidak mengandung link video Google Drive.")
                else:
                    if 'done' not in st.session_state: st.session_state['done'] = False

                    if not st.session_state['done']:
                        start_btn = st.button("Mulai analisis")
                        
                        if start_btn:
                            loading_placeholder = st.empty()
                            loading_placeholder.markdown(f"""
                                <div style="margin-top: 20px; margin-bottom: 20px;">
                                    <img src="data:image/png;base64,{spinner_image_b64}" class="loading-spinner">
                                    <div class="loading-text">File sedang dianalisis...</div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            try:
                                audio_paths, video_paths = process_videos_pipeline(links)

                                # Transcripting the audio
                                print("\nTranscripting")
                                audio_transcriptions = transcript(audio_paths)

                                # Scoring the interview answer
                                print("\nScoring")
                                scores, reasons = evaluate_transcripts(audio_transcriptions, 'assesment_metric.json')

                                # Final output in .json format
                                print("\nWriting final report")
                                final_report = generate_final_assessment_report(
                                        input_payload=input_data,
                                        video_paths_dict=links,
                                        transcriptions_list=audio_transcriptions,
                                        scores_list=scores,     
                                        reasons_list=reasons,     
                                    )
                                
                                st.session_state['result'] = final_report
                                st.session_state['done'] = True
                                
                            except Exception as e:
                                st.error(f"Terjadi kesalahan sistem: {str(e)}")
                            
                            loading_placeholder.empty()

            except json.JSONDecodeError:
                st.error("File yang diunggah tidak berformat JSON.")

    if st.session_state.get('done'):
        st.success("Analisis Selesai!")
        json_str = json.dumps(st.session_state['result'], indent=2)
        st.download_button(
            label="Download hasil analisis",
            data=json_str,
            file_name="final_assessment_report.json",
            mime="application/json"
        )
