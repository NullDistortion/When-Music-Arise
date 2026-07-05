import copy

THEMES_BASE = {
    "Windows Classic": {
        "fg_color": "#d4d0c8", "text_color": "#000000", "button_color": "#d4d0c8",
        "button_hover": "#b8b4a9", "accent": "#000080", "text_bg": "#ffffff",
        "font": ("Tahoma", 12), "corner_radius": 0, "border_width": 2
    },
    "Light": {
        "fg_color": "#f0f0f0", "text_color": "#333333", "button_color": "#e1e1e1",
        "button_hover": "#d1d1d1", "accent": "#0078d7", "text_bg": "#ffffff",
        "font": ("Segoe UI", 12), "corner_radius": 4, "border_width": 1
    },
    "Dracula": {
        "fg_color": "#282a36", "text_color": "#f8f8f2", "button_color": "#6272a4",
        "button_hover": "#4d5b84", "accent": "#ff79c6", "text_bg": "#44475a",
        "font": ("Consolas", 12), "corner_radius": 6, "border_width": 0
    },
    "Punk": {
        "fg_color": "#110000", "text_color": "#FF0000", "button_color": "#330000",
        "button_hover": "#550000", "accent": "#FFFF00", "text_bg": "#220000",
        "font": ("Impact", 14), "corner_radius": 0, "border_width": 3
    },
    "Tecno Caotico": {
        "fg_color": "#050510", "text_color": "#00FF41", "button_color": "#202020",
        "button_hover": "#303030", "accent": "#D000FF", "text_bg": "#000000",
        "font": ("Courier New", 12, "bold"), "corner_radius": 0, "border_width": 1
    },
    "Kwaii": {
        "fg_color": "#FFF0F5", "text_color": "#FF1493", "button_color": "#FFC0CB",
        "button_hover": "#ffb0bd", "accent": "#FFB6C1", "text_bg": "#FFFFFF",
        "font": ("Comic Sans MS", 12), "corner_radius": 15, "border_width": 0
    },
    "RC": {
        "fg_color": "#FF4646", "text_color": "#FFFFFF", "button_color": "#00C3FF",
        "button_hover": "#7fd9f5", "accent": "#00FFFF", "text_bg": "#F0FFFF",
        "font": ("Arial", 12, "bold"), "corner_radius": 8, "border_width": 2
    }
}

PROVEEDOR_TEMAS = copy.deepcopy(THEMES_BASE)