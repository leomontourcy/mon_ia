import json
import math
import os
import random
import shutil
import threading
import uuid
from datetime import datetime

import cv2
import moviepy.editor as mp
import moviepy.video.fx.all as vfx
import numpy as np
from flask import (
    Flask,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from werkzeug.security import check_password_hash, generate_password_hash

try:
    import librosa

    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️  librosa non installé : l'analyse musicale IA sera désactivée.")

# ─── Configuration ───────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object("config.Config")

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
PROJECTS_FILE = os.path.join(BASE_DIR, "projects.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Suivi de progression en mémoire (project_id -> dict)
montage_progress = {}


# ─── Base de données et Modèles ──────────────────────────────────
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    language = db.Column(db.String(10), default='fr')
    theme = db.Column(db.String(20), default='dark')

    def __init__(self, username, password, language='fr', theme='dark', **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.password = password
        self.language = language
        self.theme = theme


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Utilitaires Projets ─────────────────────────────────────────
def load_projects(user_id=None):
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            all_projects = json.load(f)

            uid = user_id
            if not uid:
                try:
                    if current_user.is_authenticated:
                        uid = current_user.id
                except Exception:
                    pass

            if uid:
                return [p for p in all_projects if p.get("user_id") == uid]
            return []
    return []


def save_projects(projects, user_id=None):
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            all_projects = json.load(f)
    else:
        all_projects = []

    uid = user_id
    if not uid:
        try:
            if current_user.is_authenticated:
                uid = current_user.id
        except Exception:
            pass

    if uid:
        other_users_projects = [p for p in all_projects if p.get("user_id") != uid]
        all_projects = other_users_projects + projects

    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_projects, f, indent=2, ensure_ascii=False)


# ─── Moteur de Montage Vidéo ────────────────────────────────────
def create_cinematic_title(text, background_clip, size=(720, 1280), duration=2.5):
    try:
        frame = background_clip.get_frame(0)
        img = Image.fromarray(frame).convert("RGB")
    except Exception:
        img = Image.new("RGB", size, color=(20, 20, 20))

    img = img.resize(size)
    img = img.filter(ImageFilter.GaussianBlur(radius=15))
    enhancer = Image.eval(img, lambda p: p * 0.4)
    img = enhancer

    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Avenir.ttc", 100)
    except Exception:
        font = ImageFont.load_default()

    try:
        bbox = d.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
    except Exception:
        w, h = 600, 150

    x = (size[0] - w) / 2
    y = (size[1] - h) / 2

    d.text((x + 5, y + 5), text, font=font, fill=(0, 0, 0))
    d.text((x, y), text, font=font, fill=(255, 255, 255))

    if not hasattr(Image, "ANTIALIAS"):
        Image.ANTIALIAS = getattr(
            Image,
            "LANCZOS",
            (
                getattr(Image, "Resampling", None).LANCZOS
                if hasattr(Image, "Resampling")
                else None
            ),
        )

    clip = mp.ImageClip(np.array(img)).set_duration(duration)
    clip = clip.fadein(0.5)
    return clip


# ─── Analyse Musicale IA ─────────────────────────────────────────
def analyze_music(music_path, num_clips, style):
    """
    Analyse la musique pour :
    1. Détecter le tempo et les positions des beats
    2. Trouver la section la plus énergique (drop/refrain)
    3. Calculer la durée de chaque clip en fonction du rythme
    """
    if not LIBROSA_AVAILABLE:
        return None

    try:
        y, sr = librosa.load(music_path, sr=22050)

        # Détecter le tempo (BPM) et les positions des beats
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        tempo = (
            float(np.atleast_1d(tempo)[0])
            if hasattr(tempo, "__iter__")
            else float(tempo)
        )
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        if len(beat_times) < 4:
            return None  # Pas assez de beats détectés

        # Nombre de beats par clip selon le style
        if style == "Dynamique (Coupures rapides)":
            beats_per_clip = 1
        elif style == "Chill (Plans longs + Fondus)":
            beats_per_clip = 4
        else:
            beats_per_clip = 2

        total_beats_needed = num_clips * beats_per_clip

        # Réduire si pas assez de beats
        while total_beats_needed > len(beat_times) - 1 and beats_per_clip > 1:
            beats_per_clip -= 1
            total_beats_needed = num_clips * beats_per_clip

        # Si toujours pas assez, limiter le nombre de clips
        if total_beats_needed > len(beat_times) - 1:
            total_beats_needed = len(beat_times) - 1

        # Calculer l'énergie RMS sur toute la piste
        rms = librosa.feature.rms(y=y)[0]

        # Trouver la section la plus énergique (fenêtre glissante sur les beats)
        best_energy = -1
        best_start_idx = 0

        search_range = max(1, len(beat_times) - total_beats_needed)
        for i in range(search_range):
            start_time = beat_times[i]
            end_idx = min(i + total_beats_needed, len(beat_times) - 1)
            end_time = beat_times[end_idx]

            start_frame = librosa.time_to_frames(start_time, sr=sr)
            end_frame = librosa.time_to_frames(end_time, sr=sr)

            start_frame = min(start_frame, len(rms) - 1)
            end_frame = min(end_frame, len(rms))

            if end_frame > start_frame:
                energy = float(np.sum(rms[start_frame:end_frame]))
                if energy > best_energy:
                    best_energy = energy
                    best_start_idx = i

        # Calculer les durées de clip à partir des intervalles entre beats
        clip_durations = []
        avg_beat_dur = 60.0 / tempo  # durée moyenne d'un beat

        for c in range(num_clips):
            start_beat = best_start_idx + c * beats_per_clip
            end_beat = start_beat + beats_per_clip

            if end_beat < len(beat_times):
                duration = float(beat_times[end_beat] - beat_times[start_beat])
            else:
                duration = avg_beat_dur * beats_per_clip

            clip_durations.append(max(0.4, min(duration, 8.0)))  # entre 0.4s et 8s

        best_start_time = float(beat_times[best_start_idx])
        total_duration = sum(clip_durations)

        return {
            "tempo": tempo,
            "best_start": best_start_time,
            "total_duration": total_duration,
            "clip_durations": clip_durations,
            "beats_per_clip": beats_per_clip,
        }

    except Exception as e:
        print(f"Erreur analyse musicale : {e}")
        return None


def get_best_video_segment(video_path, target_duration):
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps < 1:
            fps = 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        if duration <= target_duration + 1.0:
            return 0.0

        best_start_time = 0.0
        best_variance = -1

        for start_sec in range(0, int(duration - target_duration)):
            cap.set(cv2.CAP_PROP_POS_MSEC, start_sec * 1000)
            ret, frame = cap.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if var > best_variance:
                best_variance = var
                best_start_time = start_sec

        cap.release()
        return float(best_start_time)
    except Exception as e:
        print("Erreur IA extraction:", e)
        return 0.0


def process_montage(
    project_id,
    user_id,
    files_list,
    title,
    style,
    shuffle_order,
    music_path,
    mute_original,
    format_out="9:16",
    filter_out="aucun",
    use_intro=True,
    use_effects=True,
    use_ai_extract=True,
):
    """Traitement du montage dans un thread séparé avec mise à jour de la progression."""
    try:
        montage_progress[project_id] = {
            "status": "⏳ Analyse et tri des médias...",
            "percent": 5,
            "done": False,
            "error": None,
            "output": None,
        }

        clips = []

        # Durées par défaut (utilisées si pas de musique ou si librosa échoue)
        if style == "Dynamique (Coupures rapides)":
            default_clip_duration = 1.2
            transition_time = 0.0
        elif style == "Chill (Plans longs + Fondus)":
            default_clip_duration = 3.5
            transition_time = 0.5
        else:
            default_clip_duration = 2.0
            transition_time = 0.25

        valid_extensions = [
            ".mp4",
            ".mov",
            ".avi",
            ".mkv",
            ".webm",
            ".jpg",
            ".jpeg",
            ".png",
        ]
        valid_files = [
            p for p in files_list if os.path.splitext(p)[1].lower() in valid_extensions
        ]

        if not valid_files:
            montage_progress[project_id] = {
                "status": "❌ Aucun média valide trouvé.",
                "percent": 0,
                "done": True,
                "error": "no_files",
                "output": None,
            }
            return

        if shuffle_order:
            random.shuffle(valid_files)

        if len(valid_files) > 25:
            valid_files = valid_files[:25]

        # ── Analyse musicale IA ──
        music_analysis = None
        if music_path and os.path.exists(music_path) and LIBROSA_AVAILABLE:
            montage_progress[project_id] = {
                "status": "🧠 L'IA analyse le rythme de ta musique...",
                "percent": 8,
                "done": False,
                "error": None,
                "output": None,
            }
            music_analysis = analyze_music(music_path, len(valid_files), style)
            if music_analysis:
                print(f"🎵 Tempo détecté : {music_analysis['tempo']:.0f} BPM")
                print(
                    f"🔥 Meilleur moment trouvé à {music_analysis['best_start']:.1f}s"
                )
                print(f"🥁 {music_analysis['beats_per_clip']} beat(s) par clip")

        if format_out == "16:9":
            target_w, target_h = 1280, 720
        else:
            target_w, target_h = 720, 1280

        raw_clips = []

        if not hasattr(Image, "ANTIALIAS"):
            Image.ANTIALIAS = getattr(
                Image,
                "LANCZOS",
                (
                    getattr(Image, "Resampling", None).LANCZOS
                    if hasattr(Image, "Resampling")
                    else None
                ),
            )

        for i, path in enumerate(valid_files):
            percent = 12 + int((i / len(valid_files)) * 50)
            montage_progress[project_id] = {
                "status": f"⚙️ Traitement du fichier {i + 1}/{len(valid_files)}...",
                "percent": percent,
                "done": False,
                "error": None,
                "output": None,
            }

            # Durée du clip : synchronisée sur les beats si possible
            if music_analysis and i < len(music_analysis["clip_durations"]):
                clip_duration = music_analysis["clip_durations"][i]
            else:
                clip_duration = default_clip_duration

            try:
                current_ext = os.path.splitext(path)[1].lower()
                if current_ext in [".jpg", ".jpeg", ".png"]:
                    subclip = mp.ImageClip(path).set_duration(clip_duration)
                else:
                    video = mp.VideoFileClip(path)
                    if video.duration is None or video.duration < clip_duration:
                        # Si la vidéo est trop courte, utiliser ce qu'on a
                        if video.duration and video.duration > 0.3:
                            subclip = video.subclip(0, video.duration)
                            subclip = subclip.set_duration(
                                min(video.duration, clip_duration)
                            )
                        else:
                            continue
                    else:
                        if use_ai_extract:
                            start = get_best_video_segment(path, clip_duration)
                        else:
                            safe_margin = min(1.0, video.duration * 0.1)
                            max_start = max(
                                0, video.duration - clip_duration - safe_margin
                            )
                            start = random.uniform(safe_margin, max_start)
                        end = start + clip_duration
                        subclip = video.subclip(start, end)

                    if mute_original:
                        subclip = subclip.without_audio()

                w, h = subclip.size
                ratio_src = w / h
                ratio_tgt = target_w / target_h
                if ratio_src > ratio_tgt:
                    new_w = int(h * ratio_tgt)
                    subclip_resized = subclip.crop(x_center=w / 2, width=new_w).resize(
                        (target_w, target_h)
                    )
                else:
                    new_h = int(w / ratio_tgt)
                    subclip_resized = subclip.crop(y_center=h / 2, height=new_h).resize(
                        (target_w, target_h)
                    )

                if filter_out == "cinematic":
                    subclip_resized = subclip_resized.fx(vfx.colorx, 1.2)
                elif filter_out == "vintage":
                    subclip_resized = subclip_resized.fx(vfx.colorx, 0.8)
                elif filter_out == "bw":
                    subclip_resized = subclip_resized.fx(vfx.blackwhite)

                if use_effects and i > 0 and style == "Dynamique (Coupures rapides)":
                    # Flash blanc sur les coupures rapides
                    subclip_resized = subclip_resized.fadein(
                        0.15, initial_color=[255, 255, 255]
                    )

                raw_clips.append(subclip_resized)
            except Exception as e:
                print(f"Fichier ignoré : {e}")
                continue

        if not raw_clips:
            montage_progress[project_id] = {
                "status": "❌ Aucun média valide n'a pu être utilisé.",
                "percent": 0,
                "done": True,
                "error": "no_valid_clips",
                "output": None,
            }
            return

        title_exists = bool(title and title.strip() and use_intro)
        if title_exists:
            montage_progress[project_id]["status"] = "🎬 Création de l'écran titre..."
            montage_progress[project_id]["percent"] = 68
            title_clip = create_cinematic_title(
                title.strip(), raw_clips[0], size=(target_w, target_h), duration=2.5
            )
            clips.append(title_clip)

        for i, c in enumerate(raw_clips):
            is_first = i == 0 and not title_exists
            if transition_time > 0 and not is_first:
                c = c.crossfadein(transition_time)
            clips.append(c)

        montage_progress[project_id] = {
            "status": f"🎬 Assemblage de {len(clips)} plans...",
            "percent": 75,
            "done": False,
            "error": None,
            "output": None,
        }

        if transition_time > 0:
            final_video = mp.concatenate_videoclips(
                clips, padding=-transition_time, method="compose"
            )
        else:
            final_video = mp.concatenate_videoclips(clips, method="compose")

        # ── Ajout intelligent de la musique ──
        if music_path and os.path.exists(music_path):
            montage_progress[project_id][
                "status"
            ] = "🎵 Mixage intelligent de la musique..."
            montage_progress[project_id]["percent"] = 82
            try:
                music = mp.AudioFileClip(music_path)

                if music_analysis:
                    # Utiliser le meilleur passage trouvé par l'IA
                    best_start = music_analysis["best_start"]
                    needed_duration = final_video.duration

                    if best_start + needed_duration <= music.duration:
                        # Le meilleur passage rentre en entier
                        music = music.subclip(best_start, best_start + needed_duration)
                    else:
                        # Le meilleur passage dépasse la fin : on boucle
                        remaining = music.duration - best_start
                        first_part = music.subclip(best_start, music.duration)
                        if remaining < needed_duration:
                            loops_needed = math.ceil(
                                (needed_duration - remaining) / music.duration
                            )
                            extra = mp.concatenate_audioclips([music] * loops_needed)
                            music = mp.concatenate_audioclips([first_part, extra])
                        else:
                            music = first_part
                        music = music.subclip(0, needed_duration)
                else:
                    # Pas d'analyse : comportement classique (depuis le début)
                    if music.duration < final_video.duration:
                        loops = math.ceil(final_video.duration / music.duration)
                        music = mp.concatenate_audioclips([music] * loops)
                    music = music.subclip(0, final_video.duration)

                if not mute_original:
                    music = music.volumex(0.3)
                if final_video.audio is not None and not mute_original:
                    final_audio = mp.CompositeAudioClip([final_video.audio, music])
                else:
                    final_audio = music
                final_video = final_video.set_audio(final_audio)
            except Exception as e:
                print("Erreur musique:", e)

        final_video = final_video.fadeout(1.0)

        output_filename = f"montage_{project_id}.mp4"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        montage_progress[project_id] = {
            "status": "⚙️ Rendu final HD (patience ça va être magnifique)...",
            "percent": 88,
            "done": False,
            "error": None,
            "output": None,
        }

        final_video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=30,
            bitrate="10000k",
            preset="medium",
            verbose=False,
            logger=None,
        )

        montage_progress[project_id] = {
            "status": "✅ Chef-d'œuvre terminé ! 🌴",
            "percent": 100,
            "done": True,
            "error": None,
            "output": output_filename,
        }

        # Mettre à jour le projet dans l'historique
        projects = load_projects(user_id=user_id)
        for p in projects:
            if p["id"] == project_id:
                p["status"] = "completed"
                p["output_file"] = output_filename
                break
        save_projects(projects, user_id=user_id)

    except Exception as e:
        montage_progress[project_id] = {
            "status": f"❌ Erreur : {str(e)}",
            "percent": 0,
            "done": True,
            "error": str(e),
            "output": None,
        }


# ─── Routes Flask ────────────────────────────────────────────────


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("index"))
        flash("Nom d'utilisateur ou mot de passe incorrect.", "error")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if User.query.filter_by(username=username).first():
            flash("Ce nom d'utilisateur existe déjà.", "error")
        else:
            new_user = User(
                username=username,
                password=generate_password_hash(password, method="pbkdf2:sha256"),
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    response = make_response(
        render_template("index.html", username=current_user.username, user_language=current_user.language, user_theme=current_user.theme)
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/api/projects")
@login_required
def get_projects():
    return jsonify(load_projects())


@app.route("/api/upload", methods=["POST"])
@login_required
def upload_files():
    project_id = request.form.get("project_id", str(uuid.uuid4()))
    file_type = request.form.get("type", "media")  # 'media' ou 'music'

    project_dir = os.path.join(UPLOAD_FOLDER, project_id)
    os.makedirs(project_dir, exist_ok=True)

    saved = []
    for f in request.files.getlist("files"):
        if file_type == "music":
            filename = "_music_" + f.filename
        else:
            filename = f.filename
        path = os.path.join(project_dir, filename)
        f.save(path)
        saved.append({"name": filename, "type": file_type})

    return jsonify({"project_id": project_id, "files": saved, "count": len(saved)})


@app.route("/api/upload/<project_id>/<filename>", methods=["DELETE"])
@login_required
def delete_file(project_id, filename):
    if ".." in filename or "/" in filename or "\\" in filename:
        return jsonify({"error": "Nom de fichier invalide"}), 400

    project_dir = os.path.join(UPLOAD_FOLDER, project_id)
    path = os.path.join(project_dir, filename)
    if os.path.exists(path):
        os.remove(path)
        return jsonify({"success": True})
    return jsonify({"error": "Fichier introuvable"}), 404


@app.route("/api/start-montage", methods=["POST"])
@login_required
def start_montage():
    data = request.json
    project_id = data["project_id"]

    # ── Analyse du prompt IA (Simulation NLP par mots-clés) ──
    prompt = data.get("prompt", "").lower()

    style = data.get("style", "Normal (Équilibré)")
    format_out = data.get("format", "9:16")
    filter_out = data.get("filter", "aucun")
    use_intro = data.get("intro", True)
    use_effects = data.get("effects", True)
    use_ai_extract = data.get("aiExtract", True)
    mute = data.get("mute", False)

    if prompt:
        # Filtres
        if "noir et blanc" in prompt or "black and white" in prompt or "n&b" in prompt:
            filter_out = "bw"
        elif (
            "vintage" in prompt
            or "retro" in prompt
            or "vhs" in prompt
            or "vieux" in prompt
        ):
            filter_out = "vintage"
        elif "cinémat" in prompt or "sombre" in prompt or "contraste" in prompt:
            filter_out = "cinematic"
        elif "sans filtre" in prompt or "original" in prompt:
            filter_out = "aucun"

        # Style (Dynamisme)
        if (
            "dynamique" in prompt
            or "rapide" in prompt
            or "vif" in prompt
            or "nerveux" in prompt
        ):
            style = "Dynamique (Coupures rapides)"
            use_effects = True
        elif (
            "lent" in prompt
            or "chill" in prompt
            or "doucement" in prompt
            or "calme" in prompt
        ):
            style = "Chill (Plans longs + Fondus)"
            use_effects = False

        # Intro
        if (
            "pas de texte" in prompt
            or "sans texte" in prompt
            or "sans titre" in prompt
            or "enlève le" in prompt
            or "retire le" in prompt
        ):
            use_intro = False
        elif (
            "avec texte" in prompt
            or "avec titre" in prompt
            or "ajoute un texte" in prompt
        ):
            use_intro = True

        # Format
        if (
            "horizontal" in prompt
            or "youtube" in prompt
            or "16:9" in prompt
            or "paysage" in prompt
        ):
            format_out = "16:9"
        elif (
            "vertical" in prompt
            or "tiktok" in prompt
            or "reel" in prompt
            or "short" in prompt
            or "9:16" in prompt
            or "portrait" in prompt
        ):
            format_out = "9:16"

        # Son
        if "coupe le son" in prompt or "sans son" in prompt or "mute" in prompt:
            mute = True

    project_dir = os.path.join(UPLOAD_FOLDER, project_id)
    if not os.path.exists(project_dir):
        return jsonify({"error": "Aucun fichier uploadé"}), 400

    all_files = os.listdir(project_dir)
    media_files = [
        os.path.join(project_dir, f)
        for f in all_files
        if not f.startswith("_music_") and not f.startswith(".")
    ]
    music_files = [
        os.path.join(project_dir, f) for f in all_files if f.startswith("_music_")
    ]
    music_path = music_files[0] if music_files else None

    # Créer l'entrée dans l'historique
    projects = load_projects()
    project_name = data.get("title", "").strip() or "Sans titre"
    project = {
        "id": project_id,
        "user_id": current_user.id,
        "name": project_name,
        "style": style,
        "date": datetime.now().isoformat(),
        "status": "processing",
        "output_file": None,
        "file_count": len(media_files),
    }
    projects.insert(0, project)
    save_projects(projects)

    # Lancer le traitement en arrière-plan
    thread = threading.Thread(
        target=process_montage,
        args=(
            project_id,
            current_user.id,
            media_files,
            data.get("title", ""),
            style,
            data.get("shuffle", True),
            music_path,
            mute,
            format_out,
            filter_out,
            use_intro,
            use_effects,
            use_ai_extract,
        ),
        daemon=True,
    )
    thread.start()

    return jsonify({"project_id": project_id, "status": "started"})


@app.route("/api/progress/<project_id>")
@login_required
def get_progress(project_id):
    if project_id in montage_progress:
        return jsonify(montage_progress[project_id])
    return jsonify(
        {
            "status": "En attente...",
            "percent": 0,
            "done": False,
            "error": None,
            "output": None,
        }
    )


@app.route("/api/project/<project_id>", methods=["DELETE"])
def delete_project(project_id):
    projects = load_projects()
    projects = [p for p in projects if p["id"] != project_id]
    save_projects(projects)

    project_dir = os.path.join(UPLOAD_FOLDER, project_id)
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)

    output_file = os.path.join(OUTPUT_FOLDER, f"montage_{project_id}.mp4")
    if os.path.exists(output_file):
        os.remove(output_file)

    return jsonify({"success": True})


@app.route("/outputs/<filename>")
@login_required
def serve_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, mimetype="video/mp4")


# ─── Lancement ───────────────────────────────────────────────────

@app.route("/api/save-settings", methods=["POST"])
@login_required
def save_settings():
    data = request.json
    if not data:
        return jsonify({"error": "No data"}), 400
    
    if 'language' in data:
        current_user.language = data['language']
    if 'theme' in data:
        current_user.theme = data['theme']
        
    db.session.commit()
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7860, debug=False, threaded=True)
