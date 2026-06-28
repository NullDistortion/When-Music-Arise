import os
import json
import threading
import subprocess
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import webbrowser
import winsound
import styles
import copy
import sys
import time

# IMPORTACIONES PARA WEB SCRAPING (NO API)
try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False

SETTINGS_FILE = "settings.json"

class MusicController:
    def __init__(self, root):
        self.root = root
        self.view = None
        self.settings = self.cargar_settings()
        self.current_process = None 
        self.stop_event = False     
        self.win_config = None
        self.win_edit = None

    def set_view(self, view):
        self.view = view
        self.view.lbl_path_val.config(text=self.settings.get("download_path", "No seleccionado"))
        last_theme = self.settings.get("last_theme", "Windows Classic")
        if last_theme in styles.THEMES:
            self.view.combo_temas.set(last_theme)
            self.view.apply_theme(last_theme)
        if not self.settings.get("download_path"):
            self.root.after(100, self.configuracion_inicial)

    def cargar_settings(self):
        data = {"download_path": "", "picard_path": "", "last_theme": "Windows Classic", "custom_themes": {}}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data.update(json.load(f))
                if "custom_themes" in data:
                    for t, p in data["custom_themes"].items():
                        if t in styles.THEMES: styles.THEMES[t].update(p)
            except: pass
        return data

    def guardar_settings(self):
        self.settings["last_theme"] = self.view.current_theme_name
        self.settings["custom_themes"] = styles.THEMES
        with open(SETTINGS_FILE, "w") as f: json.dump(self.settings, f, indent=4)

    def configuracion_inicial(self):
        messagebox.showinfo("Bienvenido", "Selecciona carpeta.")
        self.seleccionar_carpeta()
        
    def seleccionar_carpeta(self):
        p = filedialog.askdirectory()
        if p:
            self.settings["download_path"] = p
            self.view.lbl_path_val.config(text=p)
            self.guardar_settings()

    def _focus_window(self, window):
        if window is not None and window.winfo_exists():
            window.lift()
            window.focus_force()
            return True
        return False
            
    def abrir_configuracion(self):
        if self._focus_window(self.win_config): return
        self.win_config = tk.Toplevel(self.root)
        self.win_config.title("Configuración")
        self.win_config.geometry("400x250")
        self._aplicar_estilo_ventana(self.win_config)
        try: self.win_config.iconbitmap(self.root.iconbitmap())
        except: pass

        tk.Label(self.win_config, text="Ruta de Descarga:", bg=self.win_config["bg"], fg=styles.THEMES[self.view.current_theme_name]["fg"]).pack(pady=(10,0))
        tk.Button(self.win_config, text=self.settings.get("download_path", "Seleccionar"), command=self.seleccionar_carpeta).pack(pady=5)
        
        tk.Label(self.win_config, text="Ruta de Picard:", bg=self.win_config["bg"], fg=styles.THEMES[self.view.current_theme_name]["fg"]).pack(pady=(10,0))
        def buscar_picard():
            f = filedialog.askopenfilename(filetypes=[("Exe", "*.exe")])
            if f:
                self.settings["picard_path"] = f
                self.guardar_settings()
        tk.Button(self.win_config, text="Buscar Picard.exe", command=buscar_picard).pack(pady=5)
        tk.Button(self.win_config, text="Descargar Picard Web", command=lambda: webbrowser.open("https://picard.musicbrainz.org/")).pack(pady=10)

    def abrir_editor_temas(self):
        if self._focus_window(self.win_edit): return
        self.win_edit = tk.Toplevel(self.root)
        theme_name = self.view.current_theme_name
        self.win_edit.title(f"Editar: {theme_name}")
        self.win_edit.geometry("300x320")
        self._aplicar_estilo_ventana(self.win_edit)
        try: self.win_edit.iconbitmap(self.root.iconbitmap())
        except: pass
        
        current_theme_data = styles.THEMES[theme_name]

        def pedir_color(clave):
            color = colorchooser.askcolor(title=f"Elegir {clave}", color=current_theme_data[clave])[1]
            if color:
                current_theme_data[clave] = color
                self.view.apply_theme(theme_name)
                self._aplicar_estilo_ventana(self.win_edit)
                self.guardar_settings()

        def restaurar():
            styles.THEMES[theme_name] = copy.deepcopy(styles.THEMES_BASE[theme_name])
            self.view.apply_theme(theme_name)
            self.win_edit.destroy()
            self.guardar_settings()
            messagebox.showinfo("Reset", f"Tema '{theme_name}' restaurado.")

        tk.Label(self.win_edit, text=f"Editando: {theme_name}", bg=self.win_edit["bg"], fg=styles.THEMES[theme_name]["fg"], font=("default", 10, "bold")).pack(pady=10)
        tk.Button(self.win_edit, text="Fondo Principal", command=lambda: pedir_color("bg")).pack(fill="x", pady=2, padx=20)
        tk.Button(self.win_edit, text="Color Texto", command=lambda: pedir_color("fg")).pack(fill="x", pady=2, padx=20)
        tk.Button(self.win_edit, text="Botones (Fondo)", command=lambda: pedir_color("btn_bg")).pack(fill="x", pady=2, padx=20)
        tk.Button(self.win_edit, text="Botones (Texto)", command=lambda: pedir_color("btn_fg")).pack(fill="x", pady=2, padx=20)
        tk.Frame(self.win_edit, height=2, bg="gray").pack(fill="x", pady=15)
        tk.Button(self.win_edit, text="🔄 Restaurar Originales", command=restaurar, bg="#cc0000", fg="white").pack(fill="x", pady=5, padx=20)

    def _aplicar_estilo_ventana(self, window):
        t = styles.THEMES[self.view.current_theme_name]
        window.config(bg=t["bg"])

    def iniciar_proceso(self):
        url = self.view.entry_url.get().strip()
        path = self.settings.get("download_path")
        platform = self.view.combo_platform.get()
        
        if not url: return messagebox.showwarning("!", "Falta el link")
        if not path or not os.path.isdir(path): return messagebox.showwarning("!", "Configura una carpeta válida")

        self.stop_event = False
        self.view.bloquear_controles(True)
        self.view.start_loading()
        self.view.internal_log = []
        
        if "YouTube" in platform:
            threading.Thread(target=self._logica_youtube, args=(url, path)).start()
        elif "SoundCloud" in platform:
            threading.Thread(target=self._logica_soundcloud, args=(url, path)).start()
        elif "Spotify" in platform:
            if not SCRAPING_AVAILABLE:
                self.view.log("❌ ERROR: Librerías 'requests'/'bs4' no instaladas.", True)
                self.view.bloquear_controles(False)
                self.view.stop_loading()
                return
            threading.Thread(target=self._logica_spotify_scraping, args=(url, path)).start()

    def cancelar_proceso(self):
        if messagebox.askyesno("Cancelar", "¿Detener descarga y limpiar?"):
            self.stop_event = True
            self.view.log("🛑 CANCELANDO PROCESO...")
            if self.current_process:
                try:
                    self.current_process.terminate()
                    time.sleep(0.5)
                    self.current_process.kill()
                except: pass

    def _encontrar_tools(self, tool_name):
        base = os.path.dirname(os.path.abspath(sys.argv[0]))
        p1 = os.path.join(base, "bin", tool_name)
        if os.path.exists(p1): return p1
        p2 = os.path.join(base, tool_name)
        if os.path.exists(p2): return p2
        return None

    def _logica_youtube(self, url, final_path):
        self._generic_download_logic(url, final_path, mode="youtube")

    def _logica_soundcloud(self, url, final_path):
        self._generic_download_logic(url, final_path, mode="soundcloud")

    # --- NUEVA LÓGICA DE SCRAPING (SIN CUENTA) ---
    def _logica_spotify_scraping(self, url, final_path):
        self.view.log("🎧 Leyendo Spotify (Modo Anónimo)...")
        
        # Cabecera para parecer un navegador real
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        try:
            if "playlist" in url:
                self.view.log("⚠️ AVISO: El modo anónimo no soporta Playlists enteras.", True)
                self.view.log("💡 Por favor, ingresa links de canciones individuales.", True)
                self.view.stop_loading()
                self.view.bloquear_controles(False)
                return

            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Spotify bloqueó la conexión (Código {response.status_code})")

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscamos los metadatos ocultos en el HTML
            title_tag = soup.find("meta", property="og:title")
            desc_tag = soup.find("meta", property="og:description")
            
            if title_tag and desc_tag:
                track_name = title_tag["content"]
                # La descripción suele ser "ArtistName · Song · 2024"
                artist_name = desc_tag["content"].split("·")[0].strip()
                
                full_name = f"{artist_name} - {track_name}"
                self.view.log(f"✅ Detectado: {full_name}")
                
                # Puente a YouTube
                self.view.log(f"🔎 Buscando en YouTube...")
                search_query = f"ytsearch1:{full_name} audio"
                
                # Reiniciamos barra
                if hasattr(self.view, 'progress'): self.view.progress["value"] = 0
                
                self._generic_download_logic(search_query, final_path, mode="youtube", single_song=True)
                
            else:
                self.view.log("❌ No se pudo leer el nombre de la canción.", True)

        except Exception as e:
            self.view.log(f"❌ Error de lectura: {e}", True)
        
        self.view.stop_loading()
        self.view.bloquear_controles(False)

    def _generic_download_logic(self, url, final_path, mode="youtube", single_song=False):
        temp_folder = os.path.join(final_path, "_Incompletos")
        try:
            os.makedirs(temp_folder, exist_ok=True)
            if not single_song: self.view.log(f"⬇️ Iniciando descarga ({mode})...")

            cookies_path = os.path.join(final_path, "cookies.txt")
            cookies_arg = ["--cookies", cookies_path] if os.path.exists(cookies_path) else []

            if mode == "soundcloud":
                exito = self._ejecutar_descarga_directa(url, temp_folder, cookies_arg)
            else:
                exito = self._intentar_descarga_con_rotacion(url, temp_folder, cookies_arg)

            if not single_song:
                if self.stop_event: return 
                if not exito:
                    self.view.log("❌ ERROR FATAL: La descarga falló.", True)
                    return
                self._procesar_y_limpiar(final_path, temp_folder)

        except Exception as e:
            self.view.log(f"Error: {e}", True)
            if not single_song: self.view.bloquear_controles(False)

    def _procesar_y_limpiar(self, final_path, temp_folder):
        basura = [os.path.join(final_path, "beets_library.blb"), os.path.join(final_path, "beets_log.txt"), os.path.join(temp_folder, "beets_library.blb"), os.path.join(temp_folder, "beets_log.txt"), os.path.join(temp_folder, "temp_config.yaml")]
        
        files = os.listdir(temp_folder)
        mp3s = [f for f in files if f.endswith(".mp3")]
        others = [f for f in files if f.endswith((".mp4", ".m4a", ".webm"))]

        if not mp3s and others:
            self.view.log("⚠️ Falló conversión a MP3. Rescatando originales...", True)
            for f in others: shutil.move(os.path.join(temp_folder, f), os.path.join(final_path, f))
        elif mp3s:
            self.view.log(f"🏷️ Organizando {len(mp3s)} canciones con Beets...")
            cfg_path = self._generar_beets_config(final_path, temp_folder)
            cmd_beet = ["beet", "-c", cfg_path, "import", "-q", "-s", temp_folder]
            
            self.current_process = subprocess.Popen(cmd_beet, shell=True, startupinfo=subprocess.STARTUPINFO())
            self.current_process.wait()
            
            if not self.stop_event:
                self._rescate_archivos(temp_folder, final_path)
                self.view.log("✅ ¡Proceso Completado!")
                self._notificar_fin()

        self.view.stop_loading()
        self.current_process = None
        
        for b in basura:
            if os.path.exists(b):
                try: os.remove(b)
                except: pass
        
        if os.path.exists(temp_folder):
            try:
                if self.stop_event: shutil.rmtree(temp_folder)
                elif not os.listdir(temp_folder): os.rmdir(temp_folder)
            except: pass

        self._guardar_log_archivo()
        self.view.bloquear_controles(False)

    def _ejecutar_descarga_directa(self, url, temp_folder, cookies_arg):
        ytdlp_exe = self._encontrar_tools("yt-dlp.exe")
        ffmpeg_exe = self._encontrar_tools("ffmpeg.exe")
        
        if not ytdlp_exe:
            self.view.log("❌ ERROR: No se encuentra 'yt-dlp.exe' en la carpeta bin.", True)
            return False

        ffmpeg_loc = os.path.dirname(ffmpeg_exe) if ffmpeg_exe else None
        ffmpeg_args = ["--ffmpeg-location", ffmpeg_loc] if ffmpeg_loc else []
        
        output_template = f"{temp_folder}/%(title)s.%(ext)s"
        
        cmd = [ytdlp_exe, url, "-x", "--audio-format", "mp3", "--audio-quality", "0", "-o", output_template, "--no-warnings"] + ffmpeg_args + cookies_arg
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        try:
            self.current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, startupinfo=startupinfo)
            
            while True:
                if self.stop_event: 
                    self.current_process.kill()
                    return False

                line = self.current_process.stdout.readline()
                if not line and self.current_process.poll() is not None: break
                if line:
                    t = line.strip()
                    if "[download]" in t and "%" in t: 
                        self.view.log(t)

            return self.current_process.returncode == 0
        except Exception as e:
            self.view.log(f"❌ Error al ejecutar motor: {e}", True)
            return False

    def _intentar_descarga_con_rotacion(self, url, temp_folder, cookies_arg):
        ffmpeg_exe = self._encontrar_tools("ffmpeg.exe")
        ytdlp_exe = self._encontrar_tools("yt-dlp.exe")
        
        if not ytdlp_exe:
            self.view.log("❌ ERROR: No se encuentra 'yt-dlp.exe'.", True)
            return False

        ffmpeg_loc = os.path.dirname(ffmpeg_exe) if ffmpeg_exe else None
        ffmpeg_args = ["--ffmpeg-location", ffmpeg_loc] if ffmpeg_loc else []

        estrategias = [
            {"nombre": "Android", "args": ["--extractor-args", "youtube:player_client=android", "-f", "bestaudio/best"]},
            {"nombre": "Web", "args": ["--extractor-args", "youtube:player_client=web", "-f", "bestaudio/best"]},
            {"nombre": "iOS", "args": ["--extractor-args", "youtube:player_client=ios", "-f", "best"]},
            {"nombre": "TV", "args": ["--extractor-args", "youtube:player_client=tv", "-f", "bestaudio/best"]}
        ]

        for i, estrategia in enumerate(estrategias):
            if self.stop_event: return False

            self.view.log(f"🔄 Intento {i+1}: Modo {estrategia['nombre']}...")
            output_template = f"{temp_folder}/%(artist&{{}} - |)s%(title)s.%(ext)s"
            
            cmd_dl = [
                ytdlp_exe, url, "-x", "--audio-format", "mp3", "--audio-quality", "0", 
                "-o", output_template, "--replace-in-metadata", "artist", "^NA$", "",
                "--no-playlist" if "list=" not in url else "--yes-playlist", 
                "--ignore-errors", "--no-warnings", "--retries", "3"
            ] + estrategia["args"] + ffmpeg_args + cookies_arg
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            try:
                self.current_process = subprocess.Popen(cmd_dl, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, startupinfo=startupinfo)
                
                error_403 = False
                while True:
                    if self.stop_event: 
                        self.current_process.kill()
                        return False

                    line = self.current_process.stdout.readline()
                    if not line and self.current_process.poll() is not None: break
                    if line:
                        t = line.strip()
                        if "HTTP Error 403" in t or "Requested format is not available" in t:
                            error_403 = True
                            self.view.log(f"⚠️ Falló modo {estrategia['nombre']}.")
                        elif "[download]" in t and "%" in t: 
                            self.view.log(t)
                
                if not error_403 and not self.stop_event:
                    self.view.log(f"✅ Modo {estrategia['nombre']} exitoso.")
                    return True
                    
            except Exception as e:
                self.view.log(f"❌ Error motor: {e}", True)
                return False
        return False

    def _guardar_log_archivo(self):
        try:
            with open("historial_sesion.log", "w", encoding="utf-8") as f:
                f.writelines(self.view.internal_log)
        except: pass

    def _generar_beets_config(self, final_dir, source_dir):
        final_dir_clean = final_dir.replace('\\', '/')
        db_path = os.path.join(source_dir, "beets_library.blb").replace('\\', '/')
        log_path = os.path.join(source_dir, "beets_log.txt").replace('\\', '/')
        cfg_path = os.path.join(source_dir, "temp_config.yaml")
        plugins = "fetchart embedart"
        fpcalc_path = shutil.which("fpcalc")
        if not fpcalc_path:
            base = os.path.dirname(os.path.abspath(sys.argv[0]))
            local_fp = os.path.join(base, "bin", "fpcalc.exe")
            if os.path.exists(local_fp): fpcalc_path = local_fp
        if fpcalc_path: plugins += " chroma"
        
        content = f"""
directory: "{final_dir_clean}"
library: "{db_path}"
paths:
    default: $artist - $title
import:
    move: yes
    write: yes
    copy: no
    quiet: yes
    log: "{log_path}"
match:
    strong_rec_thresh: 0.25
plugins: {plugins}
chroma:
    auto: yes
embedart:
    auto: yes
    maxwidth: 1000
        """
        with open(cfg_path, "w", encoding="utf-8") as f: f.write(content)
        return cfg_path

    def _rescate_archivos(self, temp_folder, final_path):
        if os.path.exists(temp_folder):
            sobras = [f for f in os.listdir(temp_folder) if f.endswith(".mp3")]
            if sobras:
                picard = self.settings.get("picard_path")
                if picard and os.path.exists(picard):
                    subprocess.run([picard, temp_folder])
                for f in os.listdir(temp_folder):
                    if f.endswith(".mp3"):
                        src = os.path.join(temp_folder, f)
                        dst = os.path.join(final_path, f)
                        try:
                            if os.path.exists(dst): os.remove(dst)
                            shutil.move(src, dst)
                        except: pass
    
    def _notificar_fin(self):
        if self.view.var_notify.get() == "sound": winsound.MessageBeep(winsound.MB_OK)
        else: messagebox.showinfo("Finalizado", "¡Música lista!")