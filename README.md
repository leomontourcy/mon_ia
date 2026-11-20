<p align="center">
  <img src="logo_ai.png" alt="Logo LEOai" width="120" />
</p>

<h1 align="center">LEOai — Montage vidéo automatique</h1>

<p align="center">
  Application web qui transforme une série de vidéos et de photos en un montage rythmé, synchronisé sur la musique.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-Socket.IO-000000?logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/OpenCV-librosa-5C3EE8?logo=opencv&logoColor=white" alt="OpenCV" />
  <img src="https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white" alt="Docker" />
</p>

---

## Fonctionnalités

**Montage**
- Import par glisser-déposer de vidéos (`mp4`, `mov`, `avi`, `mkv`, `webm`) et de photos (`jpg`, `png`), avec une musique de fond optionnelle.
- **Synchronisation sur le rythme** : `librosa` détecte le tempo et les beats, repère le passage le plus énergique du morceau (énergie RMS) et cale la durée de chaque plan sur les beats.
- **Choix automatique du meilleur extrait** de chaque vidéo : `OpenCV` mesure la netteté de l'image (variance du Laplacien) pour éviter les passages flous.
- Formats vertical **9:16** (TikTok, Reels) ou horizontal **16:9** (YouTube), recadrage centré automatique.
- Trois styles (Dynamique, Équilibré, Chill), filtres (cinématique, vintage, noir et blanc), écran titre, fondus et flashs.
- **Instructions en langage naturel** : « je veux un style dynamique en noir et blanc sans titre » est traduit en réglages (analyse par mots-clés).
- Progression du rendu en temps réel via **Socket.IO**, historique des projets par utilisateur.
- Interface disponible en 5 langues (FR, EN, ES, DE, ZH), thème clair ou sombre.

**Sécurité**
- Authentification avec mots de passe hachés (PBKDF2) et **double authentification TOTP obligatoire** (QR code compatible Google Authenticator, Authy…).
- Protection **CSRF** (Flask-WTF), en-têtes de sécurité et **CSP** (Flask-Talisman), **limitation de débit** sur la connexion, l'inscription et l'upload (Flask-Limiter).
- Contrôle d'accès sur chaque ressource : un utilisateur ne peut ni lire, ni modifier, ni télécharger les projets d'un autre.
- Noms de fichiers assainis, extensions filtrées, identifiants de projet validés (UUID), taille d'upload limitée.
- Cookies `HttpOnly`, `Secure` et `SameSite`, clé secrète obligatoire au démarrage.

## Stack technique

| Couche | Technologies |
| --- | --- |
| Back-end | Python, Flask, Flask-SocketIO, Flask-Login, SQLAlchemy (SQLite) |
| Traitement | MoviePy, FFmpeg, OpenCV, librosa, NumPy, Pillow |
| Front-end | HTML, CSS, JavaScript |
| Déploiement | Docker, Docker Compose, Gunicorn |

## Lancer le projet

### Avec Docker (recommandé)

```bash
git clone https://github.com/leomontourcy/mon_ia.git
cd mon_ia/Mon_IA_Video
cp .env.example .env
# Renseigner SECRET_KEY dans .env :
python -c "import secrets; print(secrets.token_hex(32))"
docker compose up --build
```

L'application est disponible sur <http://localhost:7860>.

> En local sans HTTPS, ajouter `SESSION_COOKIE_SECURE=false` dans `.env` pour que la session fonctionne depuis une autre machine que `localhost`.

### En local (Python 3.10+)

FFmpeg doit être installé (`brew install ffmpeg` ou `sudo apt install ffmpeg`).

```bash
cd mon_ia/Mon_IA_Video
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # puis renseigner SECRET_KEY
python app.py
```

## Structure

```
Mon_IA_Video/
├── app.py              # Routes Flask, authentification, moteur de montage
├── config.py           # Configuration (variables d'environnement)
├── templates/          # Pages : accueil, connexion, inscription, 2FA
├── static/             # JavaScript et CSS du front-end
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Pistes d'amélioration

- File de tâches (Celery ou RQ) pour sortir le rendu vidéo du processus web.
- Stockage de l'historique des projets en base de données plutôt qu'en JSON.
- Tests automatisés (pytest) et intégration continue.

## Auteur

**Léo Montourcy**, étudiant en BUT Informatique à l'IUT Paul Sabatier (Toulouse).
[Portfolio](https://leomontourcy.github.io/portfolio/) · [LinkedIn](https://www.linkedin.com/in/l%C3%A9o-montourcy-5b7381437/)
