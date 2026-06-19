WARM_PASTEL = {
    "bg":          "#FFF8F0",
    "card":        "#FFE8D6",
    "card_hover":  "#FFDDC4",
    "border":      "#E8D5C4",
    "accent":      "#FF7B6B",
    "accent_hover":"#E86555",
    "success":     "#7BCBA5",
    "warning":     "#FFD166",
    "error":       "#FF6B6B",
    "info":        "#C4A1FF",
    "text":        "#2D3436",
    "text_muted":  "#8E8E93",
    "text_faint":  "#C0B8B0",
    "text_on_accent":"#2D3436",
    "esp_skin":    "#FFD4B8",
    "esp_eye":     "#2D3436",
}

# Dark variant — same accent hue, inverted surfaces. Toggled at runtime
# via the "View → Dark mode" menu / Ctrl+Shift+D shortcut.
DARK_PASTEL = {
    "bg":          "#1A1B26",
    "card":        "#24253A",
    "card_hover":  "#2E3050",
    "border":      "#3A3B55",
    "accent":      "#FF8B7B",
    "accent_hover":"#FFA599",
    "success":     "#9FE6C5",
    "warning":     "#FFE08A",
    "error":       "#FF8B8B",
    "info":        "#D4B5FF",
    "text":        "#E6E6F0",
    "text_muted":  "#9B9BB5",
    "text_faint":  "#5A5B75",
    "text_on_accent":"#1A1B26",
    "esp_skin":    "#3D3E5C",
    "esp_eye":     "#E6E6F0",
}

# Internal plain-dict references (used by the proxy + set_theme)
_LIGHT = WARM_PASTEL
_DARK  = DARK_PASTEL
_ACTIVE = _LIGHT


class _PaletteProxy:
    """Dynamic proxy that always reads from _ACTIVE.

    This lets every module do `from palette import WARM_PASTEL as C`
    and have C['card'] return the *current* active palette's color,
    even after set_theme() swaps _ACTIVE at runtime.

    Without this, C would be a fixed reference to the light palette
    dict and inline styles like f"background: {C['card']};" would
    be baked with light colors forever.
    """

    def __getitem__(self, key):
        return _ACTIVE[key]

    def __contains__(self, key):
        return key in _ACTIVE

    def get(self, key, default=None):
        return _ACTIVE.get(key, default)

    def keys(self):
        return _ACTIVE.keys()

    def values(self):
        return _ACTIVE.values()

    def items(self):
        return _ACTIVE.items()

    def __iter__(self):
        return iter(_ACTIVE)

    def __len__(self):
        return len(_ACTIVE)


# Replace WARM_PASTEL with the proxy so all `from palette import
# WARM_PASTEL as C` imports get the dynamic proxy, not the static dict.
# DARK_PASTEL stays a plain dict so `current_theme()` can do identity
# comparison.
WARM_PASTEL = _PaletteProxy()


def set_theme(name: str) -> None:
    """Switch the active palette. Call MainWindow._apply_theme() afterwards
    to rebuild all inline styles with the new colors."""
    global _ACTIVE
    _ACTIVE = _DARK if name == "dark" else _LIGHT


def current_theme() -> str:
    return "dark" if _ACTIVE is _DARK else "light"


def stylesheet() -> str:
    c = _ACTIVE
    return f"""
    QMainWindow, QWidget {{
        background: {c['bg']};
        color: {c['text']};
        font-family: 'Ubuntu', 'Noto Sans', 'Segoe UI', system-ui, sans-serif;
        font-size: 17px;
    }}
    QFrame#card {{
        background: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 18px;
        padding: 8px;
    }}
    QFrame#dropzone {{
        background: {c['card']};
        border: 3px dashed {c['border']};
        border-radius: 24px;
    }}
    QFrame#dropzone[dragover="true"] {{
        border-color: {c['accent']};
        background: {"#FFF0EA" if c is _LIGHT else "#2E3050"};
    }}
    QPushButton#primary {{
        background: {c['accent']};
        color: {c['text_on_accent']};
        border: none;
        border-radius: 16px;
        padding: 20px 44px;
        font-size: 19px;
        font-weight: 700;
        min-height: 60px;
        min-width: 200px;
    }}
    QPushButton#primary:hover {{
        background: {c['accent_hover']};
    }}
    QPushButton#primary:disabled {{
        background: {c['text_faint']};
        color: {c['text_muted']};
    }}
    QPushButton#secondary {{
        background: transparent;
        color: {c['text_muted']};
        border: 2px solid {c['border']};
        border-radius: 14px;
        padding: 14px 28px;
        font-size: 16px;
        min-height: 48px;
    }}
    QPushButton#secondary:hover {{
        border-color: {c['accent']};
        color: {c['accent']};
    }}
    QPushButton#success {{
        background: {c['success']};
        color: {c['text_on_accent']};
        border: none;
        border-radius: 16px;
        padding: 20px 44px;
        font-size: 19px;
        font-weight: 700;
    }}
    QPushButton#danger {{
        background: transparent;
        color: {c['error']};
        border: 2px solid {c['error']};
        border-radius: 14px;
        padding: 14px 28px;
        font-size: 16px;
    }}
    QPushButton#danger:hover {{
        background: {"#FFF0F0" if c is _LIGHT else "#3A1F1F"};
    }}
    QPushButton#ghost {{
        background: transparent;
        color: {c['text_muted']};
        border: none;
        font-size: 15px;
        padding: 10px 16px;
        min-height: 40px;
    }}
    QPushButton#ghost:hover {{
        color: {c['accent']};
    }}
    QComboBox {{
        background: {"white" if c is _LIGHT else c['card']};
        border: 2px solid {c['border']};
        border-radius: 14px;
        padding: 12px 16px;
        color: {c['text']};
        font-size: 17px;
        min-height: 24px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 32px;
    }}
    QComboBox QAbstractItemView {{
        background: {"white" if c is _LIGHT else c['card']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        color: {c['text']};
        selection-background-color: {c['card']};
        selection-color: {c['accent']};
        padding: 6px;
        font-size: 16px;
    }}
    QLineEdit {{
        background: {"white" if c is _LIGHT else c['card']};
        border: 2px solid {c['border']};
        border-radius: 14px;
        padding: 12px 16px;
        color: {c['text']};
        font-size: 17px;
        min-height: 24px;
    }}
    QLineEdit:focus {{
        border-color: {c['accent']};
        background: {"#FFF8F5" if c is _LIGHT else c['card_hover']};
    }}
    QProgressBar {{
        background: {c['border']};
        border: none;
        border-radius: 10px;
        height: 16px;
        text-align: center;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {c['accent']}, stop:1 {c['info']});
        border-radius: 10px;
    }}
    QScrollBar:vertical {{
        background: {c['bg']};
        width: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background: {c['text_faint']};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QTextEdit {{
        background: {"white" if c is _LIGHT else c['card']};
        border: 2px solid {c['border']};
        border-radius: 14px;
        padding: 12px;
        color: {c['text_muted']};
        font-family: 'Ubuntu Mono', 'Consolas', monospace;
        font-size: 15px;
    }}
    QListWidget {{
        background: transparent;
        border: none;
    }}
    QListWidget::item {{
        padding: 4px;
        margin: 2px;
    }}
    QLabel#step_dot {{
        font-size: 14px;
    }}
    QLabel#section_title {{
        font-size: 14px;
        font-weight: 700;
        color: {c['text_muted']};
        letter-spacing: 0.5px;
        padding: 10px 0 6px 0;
    }}
    QWidget#sidebar {{
        background: {"white" if c is _LIGHT else c['card']};
        border-right: 1px solid {c['border']};
    }}
    QToolTip {{
        background: {c['card']};
        color: {c['text']};
        border: 1px solid {c['border']};
        padding: 6px 8px;
    }}
    """

