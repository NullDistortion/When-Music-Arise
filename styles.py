import copy

# Original
THEMES_BASE = {
    "Windows Classic": {
        "bg": "#d4d0c8", "fg": "#000000", "accent": "#000080",
        "text_bg": "#ffffff", "text_fg": "#000000", "btn_bg": "#d4d0c8",
        "btn_fg": "#000000", "relief": "raised", "font": ("Tahoma", 9)
    },
    "Light": {
        "bg": "#f0f0f0", "fg": "#333333", "accent": "#0078d7",
        "text_bg": "#ffffff", "text_fg": "#000000", "btn_bg": "#e1e1e1",
        "btn_fg": "#000000", "relief": "groove", "font": ("Segoe UI", 9)
    },
    "Dracula": {
        "bg": "#282a36", "fg": "#f8f8f2", "accent": "#ff79c6",
        "text_bg": "#44475a", "text_fg": "#8be9fd", "btn_bg": "#6272a4",
        "btn_fg": "#f8f8f2", "relief": "flat", "font": ("Consolas", 9)
    },
    "Punk": {
        "bg": "#110000", "fg": "#FF0000", "accent": "#FFFF00",
        "text_bg": "#220000", "text_fg": "#FF0000", "btn_bg": "#330000",
        "btn_fg": "#FFFF00", "relief": "ridge", "font": ("Impact", 10)
    },
    "Tecno Caotico": {
        "bg": "#050510", "fg": "#00FF41", "accent": "#D000FF",
        "text_bg": "#000000", "text_fg": "#00FF41", "btn_bg": "#202020",
        "btn_fg": "#D000FF", "relief": "solid", "font": ("Courier New", 9, "bold")
    },
    "Kwaii": {
        "bg": "#FFF0F5", "fg": "#FF69B4", "accent": "#FFB6C1",
        "text_bg": "#FFFFFF", "text_fg": "#FF1493", "btn_bg": "#FFC0CB",
        "btn_fg": "#FFFFFF", "relief": "flat", "font": ("Comic Sans MS", 9)
    },
    "RC": {
        "bg": "#D90000", "fg": "#00FFFF", "accent": "#00C3FF",
        "text_bg": "#F0FFFF", "text_fg": "#000000", "btn_bg": "#00C3FF",
        "btn_fg": "#FFFFFF", "relief": "raised", "font": ("Arial", 9, "bold")
    }
}

#copias
THEMES = copy.deepcopy(THEMES_BASE)