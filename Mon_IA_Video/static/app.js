// ── I18n & Theme ──────────────────────────────────
        const translations = {
            fr: {
                new_project: "Nouveau Projet",
                recent: "Récents",
                logout: "Quitter",
                hero_title: "Crée ton prochain",
                hero_title_2: "chef-d'œuvre",
                hero_subtitle: "Glisse tes vidéos et photos pour créer un montage cinématique en un clic.",
                add_media: "Ajouter des vidéos et photos",
                generate: "Générer ✨",
                montage_title: "Titre du montage",
                style: "Style",
                format: "Format de sortie",
                filter: "Filtre Cinématique",
                shuffle: "🔀 Mélanger",
                mute: "🔇 Couper le son",
                intro: "📝 Titre d'intro",
                effects: "✨ Effets (Flash/Zoom)",
                ai_extract: "🤖 Extraction IA",
                ai_prompt: "🪄 Instructions IA Spécifiques (Optionnel)",
                add_music: "Ajouter une musique de fond",
                start_montage: "✨ Lancer la création du chef-d'œuvre",
                pending_files: "Fichiers en attente",
                settings: "Paramètres du compte",
                language: "Langue",
                theme: "Thème"
            },
            en: {
                new_project: "New Project",
                recent: "Recent",
                logout: "Logout",
                hero_title: "Create your next",
                hero_title_2: "masterpiece",
                hero_subtitle: "Drag your videos and photos to create a cinematic montage in one click.",
                add_media: "Add videos and photos",
                generate: "Generate ✨",
                montage_title: "Montage Title",
                style: "Style",
                format: "Output Format",
                filter: "Cinematic Filter",
                shuffle: "🔀 Shuffle",
                mute: "🔇 Mute audio",
                intro: "📝 Intro Title",
                effects: "✨ Effects (Flash/Zoom)",
                ai_extract: "🤖 AI Extraction",
                ai_prompt: "🪄 Specific AI Instructions (Optional)",
                add_music: "Add background music",
                start_montage: "✨ Start creating masterpiece",
                pending_files: "Pending files",
                settings: "Account Settings",
                language: "Language",
                theme: "Theme"
            },
            es: {
                new_project: "Nuevo Proyecto",
                recent: "Recientes",
                logout: "Salir",
                hero_title: "Crea tu próxima",
                hero_title_2: "obra maestra",
                hero_subtitle: "Arrastra tus videos y fotos para crear un montaje cinematográfico con un clic.",
                add_media: "Añadir videos y fotos",
                generate: "Generar ✨",
                montage_title: "Título del montaje",
                style: "Estilo",
                format: "Formato de salida",
                filter: "Filtro Cinematográfico",
                shuffle: "🔀 Aleatorio",
                mute: "🔇 Silenciar",
                intro: "📝 Título de intro",
                effects: "✨ Efectos (Flash/Zoom)",
                ai_extract: "🤖 Extracción IA",
                ai_prompt: "🪄 Instrucciones IA (Opcional)",
                add_music: "Añadir música de fondo",
                start_montage: "✨ Iniciar la creación",
                pending_files: "Archivos pendientes",
                settings: "Configuración de la cuenta",
                language: "Idioma",
                theme: "Tema"
            },
            zh: {
                new_project: "新项目",
                recent: "最近",
                logout: "退出",
                hero_title: "创作你的下一个",
                hero_title_2: "杰作",
                hero_subtitle: "拖放您的视频和照片，一键创建电影蒙太奇。",
                add_media: "添加视频和照片",
                generate: "生成 ✨",
                montage_title: "蒙太奇标题",
                style: "风格",
                format: "输出格式",
                filter: "电影滤镜",
                shuffle: "🔀 随机播放",
                mute: "🔇 静音",
                intro: "📝 片头标题",
                effects: "✨ 特效 (闪光/缩放)",
                ai_extract: "🤖 AI 提取",
                ai_prompt: "🪄 特定 AI 指令 (可选)",
                add_music: "添加背景音乐",
                start_montage: "✨ 开始创作杰作",
                pending_files: "待处理文件",
                settings: "帐户设置",
                language: "语言",
                theme: "主题"
            },
            de: {
                new_project: "Neues Projekt",
                recent: "Kürzlich",
                logout: "Abmelden",
                hero_title: "Erstelle dein nächstes",
                hero_title_2: "Meisterwerk",
                hero_subtitle: "Zieh deine Videos und Fotos hierher, um mit einem Klick eine filmische Montage zu erstellen.",
                add_media: "Videos und Fotos hinzufügen",
                generate: "Erstellen ✨",
                montage_title: "Titel der Montage",
                style: "Stil",
                format: "Ausgabeformat",
                filter: "Filmischer Filter",
                shuffle: "🔀 Mischen",
                mute: "🔇 Stummschalten",
                intro: "📝 Intro-Titel",
                effects: "✨ Effekte (Blitz/Zoom)",
                ai_extract: "🤖 KI-Extraktion",
                ai_prompt: "🪄 Spezifische KI-Anweisungen (Optional)",
                add_music: "Hintergrundmusik hinzufügen",
                start_montage: "✨ Meisterwerk erstellen",
                pending_files: "Ausstehende Dateien",
                settings: "Kontoeinstellungen",
                language: "Sprache",
                theme: "Design"
            }
        };

        function applyLanguage(lang) {
            document.documentElement.lang = lang;
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (translations[lang] && translations[lang][key]) {
                    el.textContent = translations[lang][key];
                }
            });
            
            // Placeholder translations
            if (lang === 'en') {
                if ($('titleInput')) $('titleInput').placeholder = "Ex: Montreal Vacation 🍁";
                if ($('aiPromptInput')) $('aiPromptInput').placeholder = "Ex: I want a dynamic black and white style without title...";
            } else {
                if ($('titleInput')) $('titleInput').placeholder = "Ex: Vacances Montréal 🍁";
                if ($('aiPromptInput')) $('aiPromptInput').placeholder = "Ex: Je veux un style dynamique en noir et blanc sans titre...";
            }
        }

        function changeLanguage(lang) {
            localStorage.setItem('leoai_lang', lang);
            fetch('/api/save-settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ language: lang })
            });
            applyLanguage(lang);
        }

        function changeTheme(theme) {
            localStorage.setItem('leoai_theme', theme);
            fetch('/api/save-settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ theme: theme })
            });
            document.documentElement.setAttribute('data-theme', theme);
        }

                function toggleSidebar() {
            document.body.classList.toggle('sidebar-collapsed');
        }

        function openSettings() {
            $('settingsModal').classList.add('active');
        }

        function closeSettings() {
            $('settingsModal').classList.remove('active');
        }

        // Init language and theme
        const savedLang = window.USER_LANGUAGE || localStorage.getItem('leoai_lang') || 'fr';
        const savedTheme = window.USER_THEME || localStorage.getItem('leoai_theme') || 'dark';
        window.addEventListener('DOMContentLoaded', () => {
            $('langSelect').value = savedLang;
            $('themeSelect').value = savedTheme;
            changeLanguage(savedLang);
            changeTheme(savedTheme);
        });

        // Close modal on click outside
        window.addEventListener('click', e => {
            if (e.target === $('settingsModal')) closeSettings();
        });

        // ── État ──────────────────────────────────────────
        let currentProjectId = null;
        let uploadedFileCount = 0;
        let currentFiles = [];
        let pollingInterval = null;

        // ── Éléments DOM ──────────────────────────────────
        const $  = id => document.getElementById(id);
        const landingView    = $('landingView');
        const processingView = $('processingView');
        const resultView     = $('resultView');

        // ── Vues ──────────────────────────────────────────
        function showView(view) {
            [landingView, processingView, resultView].forEach(v => v.classList.add('hidden'));
            view.classList.remove('hidden');
        }

        // ── Initialisation ────────────────────────────────
        window.addEventListener('DOMContentLoaded', () => {
            loadProjects();
            setupDragDrop();
            setupFileInputs();
        });

        // ── Projets ──────────────────────────────────────
        async function loadProjects() {
            try {
                const res = await fetch('/api/projects');
                const projects = await res.json();
                renderProjectList(projects);
            } catch(e) { console.error('Erreur chargement projets:', e); }
        }

        function renderProjectList(projects) {
            const list = $('projectList');
            list.innerHTML = '';
            if (projects.length === 0) {
                list.innerHTML = '<div style="padding:12px;font-size:0.8em;color:var(--text-muted);text-align:center;">Aucun projet pour le moment</div>';
                return;
            }
            projects.forEach(p => {
                const item = document.createElement('div');
                item.className = 'project-item' + (p.id === currentProjectId ? ' active' : '');
                const icon = p.status === 'completed' ? '🎬' : '⏳';
                const date = formatDate(p.date);
                item.innerHTML = `
                    <span class="project-item-icon">${icon}</span>
                    <div class="project-item-info">
                        <div class="project-item-name">${escapeHtml(p.name)}</div>
                        <div class="project-item-date">${date} · ${p.file_count} fichier${p.file_count > 1 ? 's' : ''}</div>
                    </div>
                    <button class="project-item-delete" onclick="event.stopPropagation(); deleteProject('${p.id}')" title="Supprimer">🗑</button>
                `;
                item.addEventListener('click', () => openProject(p));
                list.appendChild(item);
            });
        }

        function formatDate(isoStr) {
            const d = new Date(isoStr);
            const now = new Date();
            const diff = Math.floor((now - d) / 1000);
            if (diff < 60) return "À l'instant";
            if (diff < 3600) return `Il y a ${Math.floor(diff/60)} min`;
            if (diff < 86400) return `Il y a ${Math.floor(diff/3600)}h`;
            return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
        }

        function escapeHtml(str) {
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }

        function openProject(project) {
            currentProjectId = project.id;
            loadProjects();
            if (project.status === 'completed' && project.output_file) {
                showResult(project.output_file);
            } else if (project.status === 'processing') {
                showView(processingView);
                startPolling(project.id);
            }
        }

        async function deleteProject(id) {
            try {
                await fetch('/api/project/' + id, { method: 'DELETE' });
                if (currentProjectId === id) {
                    currentProjectId = null;
                    resetToLanding();
                }
                loadProjects();
            } catch(e) { console.error('Erreur suppression:', e); }
        }

        // ── Landing / Reset ──────────────────────────────
        function resetToLanding() {
            currentProjectId = null;
            uploadedFileCount = 0;
            currentFiles = [];
            if (pollingInterval) { clearInterval(pollingInterval); pollingInterval = null; }

            $('uploadLabel').textContent = 'Ajouter des vidéos et photos';
            $('fileCountBadge').style.display = 'none';
            $('genBtn').disabled = true;
            $('optionsPanel').classList.add('hidden');
            $('titleInput').value = '';
            $('musicLabel').textContent = 'Ajouter une musique de fond';
            $('mediaInput').value = '';
            $('musicInput').value = '';

            renderFileList();

            showView(landingView);
            loadProjects();
        }

        // ── Upload fichiers ──────────────────────────────
        function setupFileInputs() {
            $('mediaInput').addEventListener('change', (e) => {
                if (e.target.files.length > 0) uploadMediaFiles(e.target.files);
            });
            $('musicInput').addEventListener('change', (e) => {
                if (e.target.files.length > 0) uploadMusicFile(e.target.files[0]);
            });
        }

        async function uploadMediaFiles(files) {
            if (!currentProjectId) currentProjectId = crypto.randomUUID ? crypto.randomUUID() : generateUUID();

            const formData = new FormData();
            formData.append('project_id', currentProjectId);
            formData.append('type', 'media');
            for (const f of files) formData.append('files', f);

            try {
                const res = await fetch('/api/upload', { method: 'POST', body: formData });
                const data = await res.json();
                
                data.files.forEach(f => {
                    if (f.type === 'media') currentFiles.push(f.name);
                });
                
                uploadedFileCount = currentFiles.length;
                $('uploadLabel').textContent = `${uploadedFileCount} fichier${uploadedFileCount > 1 ? 's' : ''} prêt${uploadedFileCount > 1 ? 's' : ''}`;
                $('fileCountBadge').style.display = 'inline';
                $('fileCountBadge').textContent = uploadedFileCount;
                $('genBtn').disabled = uploadedFileCount === 0;
                
                renderFileList();
            } catch(e) {
                console.error('Erreur upload:', e);
                alert('Erreur lors de l\'upload des fichiers');
            }
        }

        function renderFileList() {
            const container = $('fileListContainer');
            const list = $('fileList');
            if (currentFiles.length === 0) {
                container.style.display = 'none';
                list.innerHTML = '';
                return;
            }
            container.style.display = 'block';
            list.innerHTML = '';
            currentFiles.forEach(filename => {
                const div = document.createElement('div');
                div.className = 'file-list-item';
                div.innerHTML = `
                    <span class="file-item-name">${escapeHtml(filename)}</span>
                    <button class="file-item-delete" onclick="deleteFile('${escapeHtml(filename)}')">❌</button>
                `;
                list.appendChild(div);
            });
        }

        async function deleteFile(filename) {
            if (!currentProjectId) return;
            try {
                const res = await fetch(`/api/upload/${currentProjectId}/${encodeURIComponent(filename)}`, { method: 'DELETE' });
                if (res.ok) {
                    currentFiles = currentFiles.filter(f => f !== filename);
                    uploadedFileCount = currentFiles.length;
                    
                    if (uploadedFileCount > 0) {
                        $('uploadLabel').textContent = `${uploadedFileCount} fichier${uploadedFileCount > 1 ? 's' : ''} prêt${uploadedFileCount > 1 ? 's' : ''}`;
                        $('fileCountBadge').textContent = uploadedFileCount;
                    } else {
                        $('uploadLabel').textContent = 'Ajouter des vidéos et photos';
                        $('fileCountBadge').style.display = 'none';
                        $('genBtn').disabled = true;
                        $('optionsPanel').classList.add('hidden');
                    }
                    
                    renderFileList();
                } else {
                    alert("Impossible de supprimer le fichier.");
                }
            } catch(e) {
                console.error("Erreur suppression fichier", e);
            }
        }

        async function uploadMusicFile(file) {
            if (!currentProjectId) currentProjectId = crypto.randomUUID ? crypto.randomUUID() : generateUUID();

            const formData = new FormData();
            formData.append('project_id', currentProjectId);
            formData.append('type', 'music');
            formData.append('files', file);

            try {
                await fetch('/api/upload', { method: 'POST', body: formData });
                $('musicLabel').textContent = '🎵 ' + file.name;
                $('musicLabel').classList.add('music-name');
            } catch(e) {
                console.error('Erreur upload musique:', e);
            }
        }

        function generateUUID() {
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
                const r = Math.random() * 16 | 0;
                return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
        }

        // ── Options Panel ────────────────────────────────
        function showOptions() {
            $('optionsPanel').classList.remove('hidden');
            $('optionsPanel').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        // ── Lancement Montage ────────────────────────────
        async function startMontage(customPrompt = null) {
            if (!currentProjectId) {
                alert("Erreur : Aucun projet actif.");
                return;
            }

            let promptText = "";
            if (typeof customPrompt === 'string') {
                promptText = customPrompt;
            } else if (document.getElementById('aiPromptInput')) {
                promptText = document.getElementById('aiPromptInput').value;
            }

            try {
                const payload = {
                    project_id: currentProjectId,
                    title: $('titleInput') ? $('titleInput').value : '',
                    style: $('styleInput') ? $('styleInput').value : 'Normal (Équilibré)',
                    format: $('formatInput') ? $('formatInput').value : '9:16',
                    filter: $('filterInput') ? $('filterInput').value : 'aucun',
                    shuffle: $('shuffleInput') ? $('shuffleInput').checked : true,
                    mute: $('muteInput') ? $('muteInput').checked : false,
                    intro: $('introInput') ? $('introInput').checked : true,
                    effects: $('effectsInput') ? $('effectsInput').checked : true,
                    aiExtract: $('aiExtractInput') ? $('aiExtractInput').checked : true,
                    prompt: promptText
                };

                showView(processingView);
                $('progressFill').style.width = '0%';
                $('progressPercent').textContent = '0%';
                $('processingStatus').textContent = 'Démarrage...';

                await fetch('/api/start-montage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                startPolling(currentProjectId);
                loadProjects();
            } catch(e) {
                console.error('Erreur démarrage:', e);
                alert('Erreur inattendue lors du démarrage. Voir la console.');
            }
        }


        
        function reGenerateWithPrompt() {
            const prompt = $('rePromptInput').value;
            if (!prompt.trim()) {
                alert("Veuillez entrer une instruction pour l'IA !");
                return;
            }
            startMontage(prompt);
        }

        // ── Polling Progression ──────────────────────────
        function startPolling(projectId) {
            if (pollingInterval) clearInterval(pollingInterval);

            pollingInterval = setInterval(async () => {
                try {
                    const res = await fetch('/api/progress/' + projectId);
                    const data = await res.json();

                    $('processingStatus').textContent = data.status || 'En cours...';
                    $('progressFill').style.width = (data.percent || 0) + '%';
                    $('progressPercent').textContent = (data.percent || 0) + '%';

                    if (data.done) {
                        clearInterval(pollingInterval);
                        pollingInterval = null;

                        if (data.output) {
                            showResult(data.output);
                        } else if (data.error) {
                            alert('Erreur : ' + data.status);
                            resetToLanding();
                        }
                        loadProjects();
                    }
                } catch(e) { console.error('Erreur polling:', e); }
            }, 600);
        }

        // ── Affichage Résultat ───────────────────────────
        function showResult(outputFilename) {
            const url = '/outputs/' + outputFilename;
            $('resultVideo').src = url;
            $('downloadBtn').href = url;
            showView(resultView);
        }

        // ── Drag & Drop ──────────────────────────────────
        function setupDragDrop() {
            let dragCounter = 0;

            document.addEventListener('dragenter', (e) => {
                e.preventDefault();
                dragCounter++;
                $('dropOverlay').classList.add('active');
            });

            document.addEventListener('dragleave', (e) => {
                e.preventDefault();
                dragCounter--;
                if (dragCounter <= 0) {
                    dragCounter = 0;
                    $('dropOverlay').classList.remove('active');
                }
            });

            document.addEventListener('dragover', (e) => e.preventDefault());

            document.addEventListener('drop', (e) => {
                e.preventDefault();
                dragCounter = 0;
                $('dropOverlay').classList.remove('active');

                if (e.dataTransfer.files.length > 0) {
                    // Si on est pas sur le landing, y retourner
                    if (landingView.classList.contains('hidden')) {
                        // On ne reset pas tout, juste montrer le landing
                    }
                    showView(landingView);
                    uploadMediaFiles(e.dataTransfer.files);
                }
            });
        }