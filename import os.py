import os

# 1. Création du dossier du projet
dossier = "Mon_IA_Video"
os.makedirs(dossier, exist_ok=True)

# 2. Contenu du fichier requirements.txt
requirements_content = """gradio==4.19.2
moviepy==1.0.3
openai-whisper==20231117
openai==1.12.0
"""

# 3. Contenu du fichier app.py
app_content = '''import gradio as gr
import moviepy.editor as mp
import whisper
import os
from openai import OpenAI

# 1. Charger le modèle d'écoute (Whisper)
print("Chargement du modèle Whisper (cela peut prendre un instant la première fois)...")
whisper_model = whisper.load_model("base") 

def analyze_and_edit_video(video_path, openai_key):
    try:
        # ---- ETAPE A : ANALYSE DE LA VIDEO ----
        yield None, "⏳ Étape 1 : Extraction de l'audio de la vidéo..."
        video = mp.VideoFileClip(video_path)
        audio_path = "temp_audio.wav"
        video.audio.write_audiofile(audio_path, verbose=False, logger=None)
        
        yield None, "🧠 Étape 2 : L'IA écoute et transcrit la vidéo (Whisper)..."
        result = whisper_model.transcribe(audio_path)
        transcript = result["text"]
        
        # ---- ETAPE B : DECISION DU MEILLEUR MOMENT (ChatGPT) ----
        yield None, f"🤖 Étape 3 : Analyse du texte par ChatGPT...\\nTexte trouvé : {transcript[:100]}..."
        
        if not openai_key:
            yield None, "⚠️ Pas de clé API OpenAI. Je coupe les 15 premières secondes par défaut."
            start_time = 0
            end_time = min(15, video.duration)
        else:
            client = OpenAI(api_key=openai_key)
            prompt = """
            Voici la transcription d'une vidéo : "{transcript}"
            Trouve le passage le plus captivant pour un TikTok de 10 à 15 secondes maximum.
            Réponds UNIQUEMENT avec le timestamp de début et de fin en secondes, séparés par une virgule.
            Exemple de réponse attendue : 12,27
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            
            timestamps = response.choices[0].message.content.strip().split(',')
            start_time = float(timestamps[0])
            end_time = float(timestamps[1])
            
        # ---- ETAPE C : LE MONTAGE VIDEO ----
        yield None, f"🎬 Étape 4 : Découpage de la vidéo de {start_time}s à {end_time}s..."
        
        clip = video.subclip(start_time, end_time)
        
        w, h = clip.size
        target_ratio = 9 / 16
        target_width = int(h * target_ratio)
        x_center = w / 2
        
        clip_resized = clip.crop(
            x1=x_center - target_width/2, 
            y1=0, 
            x2=x_center + target_width/2, 
            y2=h
        )
        
        yield None, "⚙️ Étape 5 : Rendu final de la vidéo TikTok..."
        output_path = "mon_tiktok_final.mp4"
        clip_resized.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        
        os.remove(audio_path)
        
        yield output_path, "✅ Terminé ! Ton TikTok est prêt."

    except Exception as e:
        yield None, f"❌ Une erreur s'est produite : {str(e)}"

# ---- INTERFACE WEB (Gradio) ----
with gr.Blocks(theme=gr.themes.Soft()) as interface:
    gr.Markdown("# 🎬 IA Video Creator (Style TikTok)")
    gr.Markdown("Upload une vidéo longue, l'IA va trouver le meilleur moment, couper et recadrer la vidéo au format vertical TikTok.")
    
    with gr.Row():
        with gr.Column():
            input_video = gr.Video(label="Glisse ta vidéo ici (mp4)")
            api_key = gr.Textbox(label="Clé API OpenAI (Optionnel pour tester)", type="password")
            start_btn = gr.Button("✂️ Générer mon TikTok", variant="primary")
        
        with gr.Column():
            output_video = gr.Video(label="Résultat Final")
            status_text = gr.Textbox(label="Statut en direct", lines=5)

    start_btn.click(
        fn=analyze_and_edit_video,
        inputs=[input_video, api_key],
        outputs=[output_video, status_text]
    )

if __name__ == "__main__":
    interface.launch()
'''

# 4. Écriture des fichiers sur le disque
chemin_requirements = os.path.join(dossier, "requirements.txt")
with open(chemin_requirements, "w", encoding="utf-8") as f:
    f.write(requirements_content)

chemin_app = os.path.join(dossier, "app.py")
with open(chemin_app, "w", encoding="utf-8") as f:
    f.write(app_content)

print(f"✅ Succès ! Le dossier '{dossier}' a été créé sur ton ordinateur.")
print(f"👉 Tu peux maintenant aller dans ce dossier et lancer les commandes d'installation.")