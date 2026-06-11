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

def stylesheet() -> str:
    c = WARM_PASTEL
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
        background: #FFF0EA;
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
        background: #FFF0F0;
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
        background: white;
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
        background: white;
        border: 1px solid {c['border']};
        border-radius: 10px;
        color: {c['text']};
        selection-background-color: {c['card']};
        selection-color: {c['accent']};
        padding: 6px;
        font-size: 16px;
    }}
    QLineEdit {{
        background: white;
        border: 2px solid {c['border']};
        border-radius: 14px;
        padding: 12px 16px;
        color: {c['text']};
        font-size: 17px;
        min-height: 24px;
    }}
    QLineEdit:focus {{
        border-color: {c['accent']};
        background: #FFF8F5;
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
        background: white;
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
        background: white;
        border-right: 1px solid {c['border']};
    }}
    """
