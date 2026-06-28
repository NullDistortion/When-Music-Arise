import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, ttk
import styles

class MusicDownloaderUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Music Downloader - Ultimate")
        
        self.current_theme_name = "Windows Classic"
        self.mode = "Moderna"
        self.internal_log = []
        
        self.root.geometry("700x350") 
        
        self.setup_base_ui()
        self.setup_dynamic_ui()
        self.apply_theme(self.current_theme_name)

    def setup_base_ui(self):
        self.frame_main = tk.Frame(self.root)
        self.frame_main.pack(expand=True, fill="both", padx=15, pady=15)

        self.header_frame = tk.Frame(self.frame_main)
        self.header_frame.pack(fill="x", pady=(0, 10))
        
        self.lbl_title = tk.Label(self.header_frame, text="MUSIC DOWNLOADER", font=("Tahoma", 16, "bold"))
        self.lbl_title.pack(side="left")

        self.btn_config = tk.Button(self.header_frame, text="⚙️ Config", command=self.controller.abrir_configuracion, cursor="hand2")
        self.btn_config.pack(side="right", padx=5)
        self.btn_edit = tk.Button(self.header_frame, text="🎨 Editar", command=self.controller.abrir_editor_temas, cursor="hand2")
        self.btn_edit.pack(side="right", padx=5)
        self.btn_mode = tk.Button(self.header_frame, text="👁️ Vista: Moderna", command=self.toggle_mode, cursor="hand2", width=18)
        self.btn_mode.pack(side="right", padx=5)

        self.combo_temas = ttk.Combobox(self.header_frame, values=list(styles.THEMES.keys()), state="readonly", width=15)
        self.combo_temas.current(0)
        self.combo_temas.pack(side="right", padx=5)
        self.combo_temas.bind("<<ComboboxSelected>>", self._on_theme_change)

        self.platform_frame = tk.Frame(self.frame_main)
        self.platform_frame.pack(fill="x", pady=(5, 5))
        self.lbl_plat = tk.Label(self.platform_frame, text="Plataforma:", font=("Segoe UI", 9, "bold"))
        self.lbl_plat.pack(side="left", padx=(0, 10))
        
        self.combo_platform = ttk.Combobox(self.platform_frame, values=["YouTube / YT Music", "SoundCloud", "Spotify (Playlist/Track)"], state="readonly", width=25)
        self.combo_platform.current(0)
        self.combo_platform.pack(side="left")

        self.lbl_url = tk.Label(self.frame_main, text="Link / Enlace:")
        self.lbl_url.pack(anchor="w", pady=(10, 0))
        self.entry_url = tk.Entry(self.frame_main, width=70, font=("Segoe UI", 10))
        self.entry_url.pack(fill="x", pady=(5, 15))
        
        self.path_frame = tk.Frame(self.frame_main)
        self.path_frame.pack(fill="x", pady=5)
        self.lbl_path_title = tk.Label(self.path_frame, text="Guardar en:", font=("Tahoma", 9, "bold"))
        self.lbl_path_title.pack(side="left")
        self.lbl_path_val = tk.Label(self.path_frame, text="...", fg="blue")
        self.lbl_path_val.pack(side="left", padx=10)

        self.action_frame = tk.Frame(self.frame_main)
        self.action_frame.pack(fill="x", pady=10)
        self.btn_action = tk.Button(self.action_frame, text="INICIAR DESCARGA", command=self.controller.iniciar_proceso, height=2, font=("Segoe UI", 11, "bold"), cursor="hand2")
        self.btn_action.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_cancel = tk.Button(self.action_frame, text="CANCELAR", command=self.controller.cancelar_proceso, height=2, font=("Segoe UI", 11, "bold"), bg="#ff4444", fg="white", state=tk.DISABLED, cursor="hand2")
        self.btn_cancel.pack(side="right", fill="x", expand=True, padx=(5, 0))

        self.dynamic_frame = tk.Frame(self.frame_main)
        self.dynamic_frame.pack(fill="both", expand=True)

        self.var_notify = tk.StringVar(value="popup")
        self.frame_notify = tk.Frame(self.frame_main)
        self.frame_notify.pack(fill="x", pady=(15, 0))
        self.lbl_notify = tk.Label(self.frame_notify, text="Al finalizar:")
        self.lbl_notify.pack(side="left", padx=(0, 10))
        self.rb_popup = tk.Radiobutton(self.frame_notify, text="Ventana Pop-up", variable=self.var_notify, value="popup", cursor="hand2")
        self.rb_popup.pack(side="left", padx=5)
        self.rb_sound = tk.Radiobutton(self.frame_notify, text="Sonido", variable=self.var_notify, value="sound", cursor="hand2")
        self.rb_sound.pack(side="left", padx=5)

    def setup_dynamic_ui(self):
        for widget in self.dynamic_frame.winfo_children(): widget.destroy()

        if self.mode == "Tradicional":
            self.root.geometry("700x600")
            self.txt_log = scrolledtext.ScrolledText(self.dynamic_frame, height=12)
            self.txt_log.tag_config("error", foreground="red")
            self.txt_log.pack(fill="both", expand=True)
            self.txt_log.insert(tk.END, "".join(self.internal_log))
            self.txt_log.config(state=tk.DISABLED)
            
        elif self.mode == "Moderna":
            self.root.geometry("700x350") 
            
            self.lbl_status = tk.Label(self.dynamic_frame, text="Esperando...", font=("Segoe UI", 12))
            self.lbl_status.pack(pady=(20, 10))
            
            self.progress = ttk.Progressbar(self.dynamic_frame, orient="horizontal", length=400, mode="determinate", maximum=100)
            self.progress.pack(fill="x", padx=50, pady=10)
            
            self.lbl_detail = tk.Label(self.dynamic_frame, text="", fg="gray")
            self.lbl_detail.pack(pady=5)

    def toggle_mode(self):
        self.mode = "Moderna" if self.mode == "Tradicional" else "Tradicional"
        self.btn_mode.config(text=f"👁️ Vista: {self.mode}")
        self.setup_dynamic_ui()
        self.apply_theme(self.current_theme_name)

    def start_loading(self):
        if self.mode == "Moderna":
            self.root.geometry("700x500") 
            if hasattr(self, 'progress'): 
                self.progress["value"] = 0 # Reinicia la barra a 0
            if hasattr(self, 'lbl_status'): self.lbl_status.config(text="Iniciando...")

    def stop_loading(self):
        if self.mode == "Moderna":
            if hasattr(self, 'progress'): 
                self.progress["value"] = 100 # Llena la barra al 100%
            if hasattr(self, 'lbl_status'): self.lbl_status.config(text="Finalizado")

    def _on_theme_change(self, event):
        self.current_theme_name = self.combo_temas.get()
        self.apply_theme(self.current_theme_name)

    def apply_theme(self, theme_name):
        t = styles.THEMES[theme_name]
        for widget in [self.root, self.frame_main, self.header_frame, self.path_frame, self.frame_notify, self.action_frame, self.dynamic_frame, self.platform_frame]:
            widget.config(bg=t["bg"])
        
        labels = [self.lbl_title, self.lbl_url, self.lbl_path_title, self.lbl_path_val, self.lbl_notify, self.lbl_plat]
        if self.mode == "Moderna": labels.extend([self.lbl_status, self.lbl_detail])
        for lbl in labels:
            try: lbl.config(bg=t["bg"], fg=t["fg"])
            except: pass
            if "font" in t and lbl == self.lbl_title: lbl.config(fg=t.get("accent", t["fg"]))

        rb_style = {"bg": t["bg"], "fg": t["fg"], "selectcolor": t["bg"], "activebackground": t["bg"], "activeforeground": t["fg"]}
        self.rb_popup.config(**rb_style)
        self.rb_sound.config(**rb_style)

        for btn in [self.btn_action, self.btn_config, self.btn_edit, self.btn_mode]:
            btn.config(bg=t["btn_bg"], fg=t["btn_fg"], relief=t["relief"], activebackground=t["accent"], activeforeground=t["btn_fg"])
        
        self.entry_url.config(bg=t["text_bg"], fg=t["text_fg"], insertbackground=t["text_fg"])
        if hasattr(self, 'txt_log'): self.txt_log.config(bg=t["text_bg"], fg=t["text_fg"], insertbackground=t["text_fg"])

    def log(self, text, is_error=False):
        self.internal_log.append(text + "\n")
        
        if self.mode == "Tradicional" and hasattr(self, 'txt_log'):
            self.txt_log.config(state=tk.NORMAL)
            self.txt_log.insert(tk.END, text + "\n", "error" if is_error else "normal")
            self.txt_log.see(tk.END)
            self.txt_log.config(state=tk.DISABLED)
            
        elif self.mode == "Moderna":
            clean = text
            
            # --- LÓGICA DE BARRA DE PROGRESO REAL ---
            if "[download]" in text and "%" in text:
                try:
                    partes = text.split('%')[0].split()
                    porcentaje_str = partes[-1]
                    porcentaje_float = float(porcentaje_str)
                    
                    if hasattr(self, 'progress'):
                        self.progress["value"] = porcentaje_float
                        self.root.update_idletasks() 
                        
                    clean = f"Descargando: {porcentaje_str}%"
                except:
                    clean = "Descargando..."
            # ----------------------------------------
            
            if hasattr(self, 'lbl_detail'): 
                self.lbl_detail.config(text=clean, fg="red" if is_error else "gray")

    def bloquear_controles(self, bloquear=True):
        state = tk.DISABLED if bloquear else tk.NORMAL
        self.btn_action.config(state=state)
        self.btn_cancel.config(state=tk.NORMAL if bloquear else tk.DISABLED)
        self.entry_url.config(state=state)
        self.combo_platform.config(state="disabled" if bloquear else "readonly")