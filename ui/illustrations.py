from __future__ import annotations
from palette import WARM_PASTEL as C

def _c(name: str, fallback: str = "#DDD") -> str:
    return C.get(name, fallback)

def espy_glasses(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q70 -5 85 -10" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="86" cy="-10" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="48" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="92" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="50" cy="63" r="2" fill="white"/>
  <circle cx="94" cy="63" r="2" fill="white"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <path d="M55 83 Q70 95 85 83" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_happy(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q70 -5 88 -10" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="89" cy="-10" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="48" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="92" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="50" cy="63" r="2" fill="white"/>
  <circle cx="94" cy="63" r="2" fill="white"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <path d="M50 83 Q70 102 90 83" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_wink(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q70 -5 90 -8" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="91" cy="-8" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="48" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="50" cy="63" r="2" fill="white"/>
  <line x1="87" y1="65" x2="97" y2="65" stroke="{_c('esp_eye')}" stroke-width="2.5" stroke-linecap="round"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <path d="M55 83 Q70 95 85 83" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_surprise(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q70 -5 86 -12" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="87" cy="-12" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="48" cy="65" r="7" fill="{_c('esp_eye')}"/>
  <circle cx="92" cy="65" r="7" fill="{_c('esp_eye')}"/>
  <circle cx="50" cy="63" r="2.5" fill="white"/>
  <circle cx="94" cy="63" r="2.5" fill="white"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <ellipse cx="70" cy="90" rx="8" ry="6" fill="none" stroke="{_c('accent')}" stroke-width="2"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_sad(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q70 0 80 5" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="81" cy="5" r="5" fill="{_c('accent')}" opacity="0.6"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2" opacity="0.7"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2" opacity="0.7"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2" opacity="0.7"/>
  <ellipse cx="48" cy="68" rx="5" ry="4" fill="{_c('esp_eye')}" opacity="0.6"/>
  <ellipse cx="92" cy="68" rx="5" ry="4" fill="{_c('esp_eye')}" opacity="0.6"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.3"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.3"/>
  <path d="M55 92 Q70 82 85 92" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.7"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_searching(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q60 -2 50 -5" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="49" cy="-6" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="44" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="46" cy="63" r="2" fill="white"/>
  <circle cx="88" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="90" cy="63" r="2" fill="white"/>
  <line x1="80" y1="58" x2="98" y2="58" stroke="{_c('accent')}" stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>
  <line x1="80" y1="65" x2="98" y2="65" stroke="{_c('accent')}" stroke-width="1.5" stroke-linecap="round" opacity="0.7"/>
  <line x1="80" y1="72" x2="98" y2="72" stroke="{_c('accent')}" stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <path d="M55 83 Q70 95 85 83" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_focused(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q72 -5 88 -8" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="89" cy="-8" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="36" y1="50" x2="48" y2="53" stroke="{_c('accent')}" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="92" y1="53" x2="104" y2="50" stroke="{_c('accent')}" stroke-width="2.5" stroke-linecap="round"/>
  <ellipse cx="48" cy="65" rx="5" ry="3.5" fill="{_c('esp_eye')}"/>
  <ellipse cx="92" cy="65" rx="5" ry="3.5" fill="{_c('esp_eye')}"/>
  <circle cx="50" cy="64" r="1.5" fill="white"/>
  <circle cx="94" cy="64" r="1.5" fill="white"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <line x1="58" y1="85" x2="82" y2="85" stroke="{_c('accent')}" stroke-width="2.5" stroke-linecap="round"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_sweat(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q70 -5 86 -12" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="87" cy="-12" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="48" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="50" cy="63" r="2" fill="white"/>
  <line x1="87" y1="65" x2="97" y2="65" stroke="{_c('esp_eye')}" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M108 42 Q112 48 108 52 Q104 48 108 42Z" fill="{_c('info')}" opacity="0.7"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <path d="M55 83 Q70 95 85 83" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_excited(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q72 -8 92 -12" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="93" cy="-12" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <text x="48" y="69" font-size="14" fill="{_c('warning')}" text-anchor="middle">★</text>
  <text x="92" y="69" font-size="14" fill="{_c('warning')}" text-anchor="middle">★</text>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.8"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.8"/>
  <path d="M50 83 Q70 108 90 83" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <ellipse cx="70" cy="90" rx="8" ry="5" fill="{_c('accent')}" opacity="0.15"/>
  <text x="20" y="42" font-size="12" fill="{_c('warning')}" opacity="0.6">✦</text>
  <text x="112" y="50" font-size="10" fill="{_c('warning')}" opacity="0.6">✦</text>
  <text x="16" y="50" font-size="8" fill="{_c('warning')}" opacity="0.4">✦</text>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_peek(size: int = 80) -> str:
    s2 = size
    return f"""<svg width="{s2}" height="{s2}" viewBox="0 0 80 100">
  <path d="M40 5 Q40 -2 50 -4" stroke="{_c('accent')}" stroke-width="2" fill="none" stroke-linecap="round"/>
  <circle cx="51" cy="-4" r="3" fill="{_c('accent')}"/>
  <rect x="5" y="20" width="70" height="44" rx="18" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="1.5"/>
  <circle cx="28" cy="42" r="10" fill="none" stroke="{_c('accent')}" stroke-width="2"/>
  <circle cx="52" cy="42" r="10" fill="none" stroke="{_c('accent')}" stroke-width="2"/>
  <line x1="38" y1="42" x2="42" y2="42" stroke="{_c('accent')}" stroke-width="2"/>
  <circle cx="28" cy="42" r="3.5" fill="{_c('esp_eye')}"/>
  <circle cx="52" cy="42" r="3.5" fill="{_c('esp_eye')}"/>
  <circle cx="29" cy="41" r="1.5" fill="white"/>
  <circle cx="53" cy="41" r="1.5" fill="white"/>
  <ellipse cx="16" cy="52" rx="6" ry="3" fill="#FFB5B5" opacity="0.5"/>
  <ellipse cx="64" cy="52" rx="6" ry="3" fill="#FFB5B5" opacity="0.5"/>
  <path d="M35 55 Q40 62 45 55" stroke="{_c('accent')}" stroke-width="2" fill="none" stroke-linecap="round"/>
</svg>"""

def espy_listening(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q70 -5 85 -10" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="86" cy="-10" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="48" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="92" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="50" cy="63" r="2" fill="white"/>
  <circle cx="94" cy="63" r="2" fill="white"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <path d="M55 83 Q70 95 85 83" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <path d="M115 55 Q125 50 128 42" stroke="{_c('accent')}" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.5"/>
  <path d="M120 65 Q132 60 135 50" stroke="{_c('accent')}" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.3"/>
</svg>"""

def usb_illustration(size: int = 160) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 160 160">
  <rect x="60" y="20" width="40" height="20" rx="4" fill="#888" stroke="#666" stroke-width="1.5"/>
  <rect x="55" y="40" width="50" height="30" rx="6" fill="#AAA" stroke="#888" stroke-width="1.5"/>
  <rect x="65" y="70" width="30" height="40" rx="4" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="1.5"/>
  <rect x="55" y="110" width="50" height="30" rx="8" fill="white" stroke="{_c('accent')}" stroke-width="2"/>
  <line x1="70" y1="118" x2="70" y2="132" stroke="{_c('accent')}" stroke-width="2"/>
  <line x1="80" y1="118" x2="80" y2="132" stroke="{_c('accent')}" stroke-width="2"/>
  <line x1="90" y1="118" x2="90" y2="132" stroke="{_c('accent')}" stroke-width="2"/>
  <text x="40" y="155" font-size="11" fill="{_c('text_muted')}" text-anchor="middle">USB</text>
</svg>"""

def plug_illustration(size: int = 240) -> str:
    """Composite SVG: laptop port on left, ESP32 board on right, USB cable between.
    Shows the physical connection at realistic proportions."""
    s = size
    vw, vh = 300, 180
    # Colors
    laptop_body = "#4A4A4A"
    laptop_screen = "#2D2D2D"
    usb_plug = "#888"
    usb_cable = "#555"
    pcb_blue = "#1E3A5F"
    pcb_gold = "#FFD700"
    glow = _c('accent')
    return f"""<svg width="{s}" height="{int(s * vh / vw)}" viewBox="0 0 {vw} {vh}">
  <defs>
    <linearGradient id="cable_grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{usb_cable}"/>
      <stop offset="100%" stop-color="{usb_cable}"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Laptop body (left) -->
  <rect x="10" y="50" width="70" height="45" rx="6" fill="{laptop_body}" stroke="#333" stroke-width="1.5"/>
  <rect x="15" y="55" width="60" height="25" rx="3" fill="{laptop_screen}"/>
  <rect x="35" y="82" width="20" height="4" rx="2" fill="{laptop_body}" stroke="#555" stroke-width="0.5"/>
  <!-- USB port on laptop -->
  <rect x="78" y="68" width="8" height="10" rx="1.5" fill="{usb_plug}" stroke="#666" stroke-width="0.8"/>

  <!-- USB cable -->
  <path d="M86 73 Q105 73 110 68 Q120 60 140 68 Q155 73 170 73" stroke="{usb_cable}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <!-- USB connector (plug end) -->
  <rect x="168" y="66" width="14" height="16" rx="2.5" fill="{usb_plug}" stroke="#666" stroke-width="1"/>
  <rect x="170" y="69" width="10" height="10" rx="1" fill="#444"/>

  <!-- ESP32 Dev Board (right) -->
  <rect x="195" y="35" width="95" height="68" rx="4" fill="{pcb_blue}" stroke="#0D2137" stroke-width="1.5"/>
  <!-- Pin headers -->
  <rect x="195" y="35" width="18" height="68" rx="2" fill="#0D2137" opacity="0.25"/>
  <rect x="272" y="35" width="18" height="68" rx="2" fill="#0D2137" opacity="0.25"/>
  <!-- Chip package -->
  <rect x="218" y="50" width="60" height="38" rx="3" fill="#2A5A8A" stroke="#1E3A5F" stroke-width="1"/>
  <rect x="225" y="55" width="46" height="28" rx="4" fill="#C0C0C0" stroke="#888" stroke-width="1"/>
  <text x="248" y="73" font-size="7" fill="#333" text-anchor="middle" font-family="monospace">ESP32</text>
  <!-- USB port on board -->
  <rect x="248" y="90" width="14" height="8" rx="2" fill="#666" stroke="#555" stroke-width="0.8"/>
  <!-- LED -->
  <circle cx="230" cy="48" r="2" fill="{pcb_gold}"/>
  <circle cx="266" cy="48" r="2" fill="{pcb_gold}"/>

  <!-- Connection glow dot -->
  <circle cx="175" cy="74" r="4" fill="{glow}" opacity="0.6" filter="url(#glow)">
    <animate attributeName="opacity" values="0.3;0.8;0.3" dur="2s" repeatCount="indefinite"/>
  </circle>

  <text x="50" y="130" font-size="9" fill="{_c('text_muted')}" text-anchor="middle">Your Computer</text>
  <text x="242" y="130" font-size="9" fill="{_c('text_muted')}" text-anchor="middle">ESP32 Board</text>
</svg>"""

def wifi_illustration(size: int = 100) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 100 100">
  <path d="M12 45 Q50 15 88 45" stroke="{_c('accent')}" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M25 58 Q50 35 75 58" stroke="{_c('accent')}" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M38 71 Q50 55 62 71" stroke="{_c('accent')}" stroke-width="4" fill="none" stroke-linecap="round"/>
  <circle cx="50" cy="85" r="6" fill="{_c('accent')}"/>
</svg>"""

def chip_icon(size: int = 24) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24">
  <rect x="3" y="3" width="18" height="18" rx="3" fill="none" stroke="{_c('text_muted')}" stroke-width="2"/>
  <rect x="7" y="7" width="10" height="10" rx="2" fill="none" stroke="{_c('text_muted')}" stroke-width="1.5"/>
  <circle cx="12" cy="12" r="2" fill="{_c('accent')}" opacity="0.6"/>
  <line x1="12" y1="3" x2="12" y2="7" stroke="{_c('text_muted')}" stroke-width="1.5"/>
  <line x1="12" y1="17" x2="12" y2="21" stroke="{_c('text_muted')}" stroke-width="1.5"/>
</svg>"""

def book_icon(size: int = 24) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24">
  <rect x="4" y="2" width="16" height="20" rx="2" fill="none" stroke="{_c('text_muted')}" stroke-width="2"/>
  <line x1="12" y1="2" x2="12" y2="22" stroke="{_c('text_muted')}" stroke-width="2"/>
  <line x1="4" y1="8" x2="12" y2="8" stroke="{_c('text_muted')}" stroke-width="1.5"/>
  <line x1="4" y1="12" x2="12" y2="12" stroke="{_c('text_muted')}" stroke-width="1.5"/>
  <line x1="4" y1="16" x2="10" y2="16" stroke="{_c('text_muted')}" stroke-width="1.5"/>
</svg>"""

def drop_zone_illustration(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 180 180">
  <rect x="15" y="30" width="150" height="120" rx="20" fill="none" stroke="{_c('border')}" stroke-width="3" stroke-dasharray="8 6"/>
  <path d="M90 55 L90 100 M70 80 L90 100 L110 80" stroke="{_c('accent')}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="55" y="105" width="70" height="8" rx="4" fill="{_c('border')}"/>
  <text x="90" y="140" font-size="13" fill="{_c('text_muted')}" text-anchor="middle">.ino</text>
</svg>"""

def onboarding_flow_svg(width: int = 360, height: int = 380) -> str:
    """Single SVG showing the 4-step Espy lifecycle.
    Vertical timeline with icons and short plain-English labels."""
    c = _c('accent')
    s = _c('success')
    m = _c('text_muted')
    t = _c('text')
    sk = _c('esp_skin')
    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .step-num {{ font: bold 14px sans-serif; fill: white; }}
    .step-title {{ font: bold 16px sans-serif; fill: {t}; }}
    .step-desc {{ font: 13px sans-serif; fill: {m}; }}
    .connective {{ font: 11px sans-serif; fill: {m}; }}
  </style>

  <!-- Step 1: Plug USB -->
  <rect x="40" y="10" width="28" height="28" rx="14" fill="{c}"/>
  <text x="54" y="30" text-anchor="middle" class="step-num">1</text>
  <text x="80" y="28" class="step-title">Plug in via USB</text>
  <text x="80" y="46" class="step-desc">Connect your ESP32 to this computer once.</text>
  <!-- USB icon -->
  <rect x="60" y="58" width="28" height="12" rx="2" fill="#AAA" stroke="#888" stroke-width="1"/>
  <rect x="70" y="70" width="8" height="10" rx="1.5" fill="#888"/>
  <rect x="80" y="58" width="16" height="12" rx="2" fill="{sk}" stroke="{m}" stroke-width="0.8"/>

  <!-- Arrow down -->
  <line x1="54" y1="82" x2="54" y2="105" stroke="{c}" stroke-width="2" stroke-dasharray="4 3"/>
  <polygon points="54,105 50,97 58,97" fill="{c}"/>

  <!-- Step 2: Connect Wi-Fi -->
  <rect x="40" y="110" width="28" height="28" rx="14" fill="{c}"/>
  <text x="54" y="130" text-anchor="middle" class="step-num">2</text>
  <text x="80" y="128" class="step-title">Connect to Wi-Fi</text>
  <text x="80" y="146" class="step-desc">Your ESP32 joins your home network.</text>
  <!-- Wi-Fi icon -->
  <path d="M55 160 Q70 148 85 160" stroke="{c}" stroke-width="2" fill="none" stroke-linecap="round"/>
  <path d="M60 167 Q70 158 80 167" stroke="{c}" stroke-width="2" fill="none" stroke-linecap="round"/>
  <circle cx="70" cy="176" r="3" fill="{c}"/>

  <!-- Arrow down -->
  <line x1="54" y1="182" x2="54" y2="205" stroke="{c}" stroke-width="2" stroke-dasharray="4 3"/>
  <polygon points="54,205 50,197 58,197" fill="{c}"/>

  <!-- Step 3: Drop .ino -->
  <rect x="40" y="210" width="28" height="28" rx="14" fill="{c}"/>
  <text x="54" y="230" text-anchor="middle" class="step-num">3</text>
  <text x="80" y="228" class="step-title">Drop your code</text>
  <text x="80" y="246" class="step-desc">Drag any .ino file onto Espy.</text>
  <!-- Drop icon -->
  <rect x="58" y="258" width="24" height="20" rx="4" fill="none" stroke="{c}" stroke-width="1.5" stroke-dasharray="3 2"/>
  <path d="M70 260 L70 272 M64 267 L70 272 L76 267" stroke="{c}" stroke-width="2" fill="none" stroke-linecap="round"/>
  <text x="70" y="280" font-size="7" fill="{m}" text-anchor="middle">.ino</text>

  <!-- Arrow down -->
  <line x1="54" y1="285" x2="54" y2="308" stroke="{c}" stroke-width="2" stroke-dasharray="4 3"/>
  <polygon points="54,308 50,300 58,300" fill="{c}"/>

  <!-- Step 4: Done! -->
  <rect x="40" y="315" width="28" height="28" rx="14" fill="{s}"/>
  <path d="M48 329 L53 334 L62 323" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="80" y="333" class="step-title" fill="{s}">Done! No cables needed</text>
  <text x="80" y="351" class="step-desc">Future updates happen over Wi-Fi automatically.</text>
  <!-- Star -->
  <text x="62" y="368" font-size="14" fill="{c}" text-anchor="middle">✦</text>
  <text x="160" y="370" font-size="11" fill="{c}" text-anchor="middle">✦</text>
</svg>"""

def step_illustrations(size: int = 180) -> list[str]:
    s = size
    return [
        f"""<svg width="{s}" height="{s}" viewBox="0 0 180 140">
  <rect x="50" y="20" width="80" height="40" rx="8" fill="white" stroke="{_c('accent')}" stroke-width="2"/>
  <rect x="60" y="60" width="60" height="30" rx="6" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="1.5"/>
  <line x1="90" y1="90" x2="90" y2="115" stroke="{_c('border')}" stroke-width="2"/>
  <rect x="60" y="110" width="60" height="18" rx="5" fill="white" stroke="{_c('accent')}" stroke-width="1.5"/>
  <text x="90" y="130" font-size="12" fill="{_c('text_muted')}" text-anchor="middle">USB cable</text>
  <circle cx="170" cy="25" r="12" fill="{_c('success')}" opacity="0.2"/>
  <text x="170" y="29" font-size="14" fill="{_c('success')}" text-anchor="middle" font-weight="bold">1</text>
</svg>""",
        f"""<svg width="{s}" height="{s}" viewBox="0 0 180 140">
  <path d="M20 55 Q50 20 80 55" stroke="{_c('accent')}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M45 65 Q65 40 85 65" stroke="{_c('accent')}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <circle cx="65" cy="80" r="5" fill="{_c('accent')}"/>
  <rect x="110" y="50" width="40" height="50" rx="10" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="1.5"/>
  <circle cx="118" cy="62" r="2" fill="{_c('esp_eye')}"/>
  <circle cx="132" cy="62" r="2" fill="{_c('esp_eye')}"/>
  <circle cx="170" cy="25" r="12" fill="{_c('success')}" opacity="0.2"/>
  <text x="170" y="29" font-size="14" fill="{_c('success')}" text-anchor="middle" font-weight="bold">2</text>
</svg>""",
        f"""<svg width="{s}" height="{s}" viewBox="0 0 180 140">
  <rect x="25" y="30" width="130" height="80" rx="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5" stroke-dasharray="6 5"/>
  <path d="M90 50 L90 80 M75 65 L90 80 L105 65" stroke="{_c('accent')}" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="55" y="85" width="70" height="6" rx="3" fill="{_c('border')}"/>
  <text x="90" y="112" font-size="12" fill="{_c('text_muted')}" text-anchor="middle">.ino file</text>
  <circle cx="170" cy="25" r="12" fill="{_c('success')}" opacity="0.2"/>
  <text x="170" y="29" font-size="14" fill="{_c('success')}" text-anchor="middle" font-weight="bold">3</text>
</svg>""",
    ]

def espy_svg_tag(size: int = 24) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24">
  <circle cx="12" cy="10" r="6" fill="{_c('esp_skin')}" stroke="{_c('accent')}" stroke-width="1.5"/>
  <circle cx="10" cy="9" r="1.5" fill="{_c('esp_eye')}"/>
  <circle cx="14" cy="9" r="1.5" fill="{_c('esp_eye')}"/>
  <path d="M8 12 Q12 15 16 12" stroke="{_c('accent')}" stroke-width="1.2" fill="none" stroke-linecap="round"/>
  <rect x="8" y="16" width="8" height="4" rx="2" fill="{_c('border')}"/>
</svg>"""

def espy_icon_24(size: int = 24) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24">
  <circle cx="12" cy="8" r="5" fill="{_c('esp_skin')}" stroke="{_c('accent')}" stroke-width="1.2"/>
  <circle cx="10.5" cy="7.5" r="1.2" fill="{_c('esp_eye')}"/>
  <circle cx="13.5" cy="7.5" r="1.2" fill="{_c('esp_eye')}"/>
  <path d="M9 10.5 Q12 12.5 15 10.5" stroke="{_c('accent')}" stroke-width="1" fill="none" stroke-linecap="round"/>
  <rect x="9" y="13" width="6" height="3" rx="1.5" fill="{_c('border')}"/>
</svg>"""

def board_esp32_devkit(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.72)}" viewBox="0 0 220 158">
  <!-- PCB: classic blue, 53mm × 28mm style -->
  <rect x="10" y="18" width="200" height="122" rx="4" fill="#1E3A5F" stroke="#0D2137" stroke-width="1.5"/>
  <!-- Left pin header (15 pins) -->
  <rect x="10" y="22" width="18" height="114" rx="2" fill="#0D2137" opacity="0.35"/>
  <g fill="#C0A030" opacity="0.6">
    <rect x="14" y="26" width="10" height="4" rx="1.5"/>
    <rect x="14" y="33" width="10" height="4" rx="1.5"/>
    <rect x="14" y="40" width="10" height="4" rx="1.5"/>
    <rect x="14" y="47" width="10" height="4" rx="1.5"/>
    <rect x="14" y="54" width="10" height="4" rx="1.5"/>
    <rect x="14" y="61" width="10" height="4" rx="1.5"/>
    <rect x="14" y="68" width="10" height="4" rx="1.5"/>
    <rect x="14" y="75" width="10" height="4" rx="1.5"/>
    <rect x="14" y="82" width="10" height="4" rx="1.5"/>
    <rect x="14" y="89" width="10" height="4" rx="1.5"/>
    <rect x="14" y="96" width="10" height="4" rx="1.5"/>
    <rect x="14" y="103" width="10" height="4" rx="1.5"/>
    <rect x="14" y="110" width="10" height="4" rx="1.5"/>
    <rect x="14" y="117" width="10" height="4" rx="1.5"/>
    <rect x="14" y="124" width="10" height="4" rx="1.5"/>
  </g>
  <!-- Right pin header (15 pins) -->
  <rect x="192" y="22" width="18" height="114" rx="2" fill="#0D2137" opacity="0.35"/>
  <g fill="#C0A030" opacity="0.6">
    <rect x="196" y="26" width="10" height="4" rx="1.5"/><rect x="196" y="33" width="10" height="4" rx="1.5"/>
    <rect x="196" y="40" width="10" height="4" rx="1.5"/><rect x="196" y="47" width="10" height="4" rx="1.5"/>
    <rect x="196" y="54" width="10" height="4" rx="1.5"/><rect x="196" y="61" width="10" height="4" rx="1.5"/>
    <rect x="196" y="68" width="10" height="4" rx="1.5"/><rect x="196" y="75" width="10" height="4" rx="1.5"/>
    <rect x="196" y="82" width="10" height="4" rx="1.5"/><rect x="196" y="89" width="10" height="4" rx="1.5"/>
    <rect x="196" y="96" width="10" height="4" rx="1.5"/><rect x="196" y="103" width="10" height="4" rx="1.5"/>
    <rect x="196" y="110" width="10" height="4" rx="1.5"/><rect x="196" y="117" width="10" height="4" rx="1.5"/>
    <rect x="196" y="124" width="10" height="4" rx="1.5"/>
  </g>
  <!-- ESP32 module / chip area -->
  <rect x="42" y="48" width="136" height="62" rx="3" fill="#2A5A8A" stroke="#1E3A5F" stroke-width="1"/>
  <!-- Metal shield can -->
  <rect x="55" y="52" width="110" height="54" rx="4" fill="#C0C0C0" stroke="#999" stroke-width="1"/>
  <!-- Chip label -->
  <text x="110" y="85" font-size="8" fill="#333" text-anchor="middle" font-family="monospace">ESP32-WROOM-32</text>
  <!-- Gold LED indicators -->
  <circle cx="48" cy="44" r="2.5" fill="#FFD700" stroke="#CC9900" stroke-width="0.5"/>
  <circle cx="168" cy="44" r="2.5" fill="#FF4444" opacity="0.8"/>
  <!-- USB micro-B port -->
  <rect x="95" y="130" width="30" height="12" rx="2" fill="#666" stroke="#555" stroke-width="1"/>
  <rect x="100" y="130" width="20" height="12" rx="1.5" fill="#444"/>
  <!-- EN / RST button -->
  <circle cx="175" cy="132" r="4" fill="#888" stroke="#666" stroke-width="0.8"/>
  <circle cx="50" cy="132" r="4" fill="#888" stroke="#666" stroke-width="0.8"/>
  <!-- Antenna area -->
  <rect x="155" y="18" width="40" height="8" rx="1" fill="#0D2137" opacity="0.15"/>
  <path d="M175 18 L175 10" stroke="#FFD700" stroke-width="0.5" opacity="0.4"/>
  <text x="110" y="151" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">ESP32 Dev Module</text>
</svg>"""


def board_nodemcu(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.8)}" viewBox="0 0 200 160">
  <!-- PCB: green, breadboard-friendly -->
  <rect x="15" y="15" width="170" height="130" rx="10" fill="#0D5C2E" stroke="#083D1E" stroke-width="1.5"/>
  <!-- Left pin header -->
  <rect x="15" y="15" width="22" height="130" rx="3" fill="#083D1E" opacity="0.3"/>
  <g fill="#C0A030" opacity="0.55">
    <rect x="19" y="19" width="14" height="4" rx="1.5"/><rect x="19" y="27" width="14" height="4" rx="1.5"/>
    <rect x="19" y="35" width="14" height="4" rx="1.5"/><rect x="19" y="43" width="14" height="4" rx="1.5"/>
    <rect x="19" y="51" width="14" height="4" rx="1.5"/><rect x="19" y="59" width="14" height="4" rx="1.5"/>
    <rect x="19" y="67" width="14" height="4" rx="1.5"/><rect x="19" y="75" width="14" height="4" rx="1.5"/>
    <rect x="19" y="83" width="14" height="4" rx="1.5"/><rect x="19" y="91" width="14" height="4" rx="1.5"/>
    <rect x="19" y="99" width="14" height="4" rx="1.5"/><rect x="19" y="107" width="14" height="4" rx="1.5"/>
    <rect x="19" y="115" width="14" height="4" rx="1.5"/><rect x="19" y="123" width="14" height="4" rx="1.5"/>
    <rect x="19" y="131" width="14" height="4" rx="1.5"/>
  </g>
  <!-- Right pin header -->
  <rect x="163" y="15" width="22" height="130" rx="3" fill="#083D1E" opacity="0.3"/>
  <g fill="#C0A030" opacity="0.55">
    <rect x="167" y="19" width="14" height="4" rx="1.5"/><rect x="167" y="27" width="14" height="4" rx="1.5"/>
    <rect x="167" y="35" width="14" height="4" rx="1.5"/><rect x="167" y="43" width="14" height="4" rx="1.5"/>
    <rect x="167" y="51" width="14" height="4" rx="1.5"/><rect x="167" y="59" width="14" height="4" rx="1.5"/>
    <rect x="167" y="67" width="14" height="4" rx="1.5"/><rect x="167" y="75" width="14" height="4" rx="1.5"/>
    <rect x="167" y="83" width="14" height="4" rx="1.5"/><rect x="167" y="91" width="14" height="4" rx="1.5"/>
    <rect x="167" y="99" width="14" height="4" rx="1.5"/><rect x="167" y="107" width="14" height="4" rx="1.5"/>
    <rect x="167" y="115" width="14" height="4" rx="1.5"/><rect x="167" y="123" width="14" height="4" rx="1.5"/>
    <rect x="167" y="131" width="14" height="4" rx="1.5"/>
  </g>
  <!-- Module area -->
  <rect x="55" y="55" width="90" height="50" rx="3" fill="#1A8C4A" stroke="#0D5C2E" stroke-width="1"/>
  <rect x="65" y="58" width="70" height="44" rx="3" fill="#D0D0D0" stroke="#999" stroke-width="1"/>
  <text x="100" y="85" font-size="8" fill="#333" text-anchor="middle" font-family="monospace">ESP32</text>
  <!-- USB micro-B port on top edge -->
  <rect x="78" y="8" width="44" height="12" rx="2" fill="#666" stroke="#555" stroke-width="1"/>
  <rect x="86" y="8" width="28" height="12" rx="1.5" fill="#444"/>
  <!-- LED -->
  <circle cx="65" cy="48" r="2" fill="#FFD700"/>
  <circle cx="135" cy="48" r="2" fill="#FF4444" opacity="0.7"/>
  <!-- RST button -->
  <circle cx="145" cy="115" r="5" fill="#888" stroke="#666" stroke-width="0.8"/>
  <text x="100" y="153" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">NodeMCU-32S</text>
</svg>"""



def board_esp32s3(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.75)}" viewBox="0 0 200 150">
  <rect x="10" y="10" width="180" height="100" rx="6" fill="#3A1B4A" stroke="#241030" stroke-width="2"/>
  <rect x="10" y="10" width="25" height="100" rx="6" fill="#241030" opacity="0.2"/>
  <rect x="165" y="10" width="25" height="100" rx="6" fill="#241030" opacity="0.2"/>
  <rect x="45" y="30" width="110" height="60" rx="4" fill="#5C2D7A" stroke="#3A1B4A" stroke-width="1.5"/>
  <rect x="60" y="35" width="80" height="50" rx="5" fill="#D0D0D0" stroke="#999" stroke-width="1.5"/>
  <text x="100" y="65" font-size="10" fill="#333" text-anchor="middle" font-family="monospace">S3</text>
  <circle cx="78" cy="27" r="2.5" fill="#FFD700"/>
  <circle cx="122" cy="27" r="2.5" fill="#FFD700"/>
  <rect x="18" y="25" width="12" height="70" rx="3" fill="#888" opacity="0.3"/>
  <rect x="170" y="25" width="12" height="70" rx="3" fill="#888" opacity="0.3"/>
  <rect x="85" y="100" width="32" height="12" rx="3" fill="#666" stroke="#555" stroke-width="1"/>
  <rect x="88" y="100" width="26" height="12" rx="2" fill="#444"/>
  <rect x="155" y="95" width="20" height="18" rx="3" fill="#888" stroke="#666" stroke-width="1"/>
  <rect x="158" y="98" width="14" height="12" rx="2" fill="#666"/>
  <rect x="25" y="95" width="20" height="18" rx="3" fill="#888" stroke="#666" stroke-width="1"/>
  <text x="100" y="128" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">ESP32-S3 DevKitC</text>
</svg>"""


def board_esp32c3(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.7)}" viewBox="0 0 200 140">
  <rect x="15" y="15" width="170" height="90" rx="8" fill="#1A4A3A" stroke="#0D3025" stroke-width="2"/>
  <rect x="15" y="15" width="20" height="90" rx="8" fill="#0D3025" opacity="0.2"/>
  <rect x="165" y="15" width="20" height="90" rx="8" fill="#0D3025" opacity="0.2"/>
  <rect x="50" y="30" width="100" height="50" rx="4" fill="#2D6B55" stroke="#1A4A3A" stroke-width="1.5"/>
  <rect x="65" y="35" width="70" height="40" rx="5" fill="#D0D0D0" stroke="#999" stroke-width="1.5"/>
  <text x="100" y="60" font-size="9" fill="#333" text-anchor="middle" font-family="monospace">C3</text>
  <circle cx="80" cy="28" r="2" fill="#FFD700"/>
  <circle cx="120" cy="28" r="2" fill="#FFD700"/>
  <rect x="22" y="30" width="12" height="60" rx="2" fill="#888" opacity="0.3"/>
  <rect x="166" y="30" width="12" height="60" rx="2" fill="#888" opacity="0.3"/>
  <rect x="85" y="95" width="30" height="10" rx="3" fill="#666" stroke="#555" stroke-width="1"/>
  <text x="100" y="118" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">ESP32-C3</text>
</svg>"""


def board_esp32s2(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.72)}" viewBox="0 0 200 145">
  <rect x="10" y="15" width="180" height="95" rx="4" fill="#4A1A1A" stroke="#300D0D" stroke-width="2"/>
  <rect x="10" y="15" width="22" height="95" rx="4" fill="#300D0D" opacity="0.2"/>
  <rect x="168" y="15" width="22" height="95" rx="4" fill="#300D0D" opacity="0.2"/>
  <rect x="42" y="35" width="116" height="55" rx="4" fill="#6B2D2D" stroke="#4A1A1A" stroke-width="1.5"/>
  <rect x="57" y="40" width="86" height="45" rx="5" fill="#D0D0D0" stroke="#999" stroke-width="1.5"/>
  <text x="100" y="67" font-size="10" fill="#333" text-anchor="middle" font-family="monospace">S2</text>
  <circle cx="76" cy="33" r="2.5" fill="#FFD700"/>
  <circle cx="124" cy="33" r="2.5" fill="#FFD700"/>
  <rect x="16" y="30" width="12" height="65" rx="2" fill="#888" opacity="0.3"/>
  <rect x="172" y="30" width="12" height="65" rx="2" fill="#888" opacity="0.3"/>
  <rect x="85" y="100" width="30" height="12" rx="3" fill="#666" stroke="#555" stroke-width="1"/>
  <rect x="90" y="100" width="20" height="12" rx="2" fill="#444"/>
  <rect x="40" y="12" width="12" height="8" rx="2" fill="#888"/>
  <rect x="148" y="12" width="12" height="8" rx="2" fill="#888"/>
  <text x="100" y="122" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">ESP32-S2 Saola</text>
</svg>"""


def board_esp32c6(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.7)}" viewBox="0 0 200 140">
  <!-- PCB: deep navy, RISC-V C6 -->
  <rect x="15" y="12" width="170" height="95" rx="6" fill="#1A1A4A" stroke="#0D0D30" stroke-width="1.5"/>
  <!-- Left pin header -->
  <rect x="15" y="12" width="18" height="95" rx="3" fill="#0D0D30" opacity="0.3"/>
  <g fill="#C0A030" opacity="0.5">
    <rect x="18" y="16" width="12" height="4" rx="1.5"/><rect x="18" y="24" width="12" height="4" rx="1.5"/>
    <rect x="18" y="32" width="12" height="4" rx="1.5"/><rect x="18" y="40" width="12" height="4" rx="1.5"/>
    <rect x="18" y="48" width="12" height="4" rx="1.5"/><rect x="18" y="56" width="12" height="4" rx="1.5"/>
    <rect x="18" y="64" width="12" height="4" rx="1.5"/><rect x="18" y="72" width="12" height="4" rx="1.5"/>
    <rect x="18" y="80" width="12" height="4" rx="1.5"/><rect x="18" y="88" width="12" height="4" rx="1.5"/>
  </g>
  <!-- Right pin header -->
  <rect x="167" y="12" width="18" height="95" rx="3" fill="#0D0D30" opacity="0.3"/>
  <g fill="#C0A030" opacity="0.5">
    <rect x="170" y="16" width="12" height="4" rx="1.5"/><rect x="170" y="24" width="12" height="4" rx="1.5"/>
    <rect x="170" y="32" width="12" height="4" rx="1.5"/><rect x="170" y="40" width="12" height="4" rx="1.5"/>
    <rect x="170" y="48" width="12" height="4" rx="1.5"/><rect x="170" y="56" width="12" height="4" rx="1.5"/>
    <rect x="170" y="64" width="12" height="4" rx="1.5"/><rect x="170" y="72" width="12" height="4" rx="1.5"/>
    <rect x="170" y="80" width="12" height="4" rx="1.5"/><rect x="170" y="88" width="12" height="4" rx="1.5"/>
  </g>
  <!-- Chip -->
  <rect x="50" y="30" width="100" height="50" rx="3" fill="#2D2D6B" stroke="#1A1A4A" stroke-width="1"/>
  <rect x="58" y="34" width="84" height="42" rx="3" fill="#D0D0D0" stroke="#999" stroke-width="1"/>
  <text x="100" y="60" font-size="8" fill="#333" text-anchor="middle" font-family="monospace">ESP32-C6</text>
  <!-- USB-C port (bottom edge) -->
  <rect x="82" y="98" width="36" height="14" rx="4" fill="#666" stroke="#555" stroke-width="1"/>
  <rect x="88" y="100" width="24" height="10" rx="2" fill="#444"/>
  <!-- LED -->
  <circle cx="55" cy="26" r="2" fill="#FFD700"/>
  <circle cx="145" cy="26" r="2" fill="#FF4444" opacity="0.7"/>
  <text x="100" y="125" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">ESP32-C6</text>
</svg>"""


def board_esp32h2(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.65)}" viewBox="0 0 200 130">
  <!-- PCB: dark forest green, Zigbee/Thread H2 -->
  <rect x="18" y="12" width="164" height="86" rx="6" fill="#2A4A2A" stroke="#1A301A" stroke-width="1.5"/>
  <!-- Left pin header (compact) -->
  <rect x="18" y="12" width="16" height="86" rx="3" fill="#1A301A" opacity="0.3"/>
  <g fill="#C0A030" opacity="0.5">
    <rect x="21" y="16" width="10" height="4" rx="1.5"/><rect x="21" y="24" width="10" height="4" rx="1.5"/>
    <rect x="21" y="32" width="10" height="4" rx="1.5"/><rect x="21" y="40" width="10" height="4" rx="1.5"/>
    <rect x="21" y="48" width="10" height="4" rx="1.5"/><rect x="21" y="56" width="10" height="4" rx="1.5"/>
    <rect x="21" y="64" width="10" height="4" rx="1.5"/><rect x="21" y="72" width="10" height="4" rx="1.5"/>
    <rect x="21" y="80" width="10" height="4" rx="1.5"/>
  </g>
  <!-- Right pin header -->
  <rect x="166" y="12" width="16" height="86" rx="3" fill="#1A301A" opacity="0.3"/>
  <g fill="#C0A030" opacity="0.5">
    <rect x="169" y="16" width="10" height="4" rx="1.5"/><rect x="169" y="24" width="10" height="4" rx="1.5"/>
    <rect x="169" y="32" width="10" height="4" rx="1.5"/><rect x="169" y="40" width="10" height="4" rx="1.5"/>
    <rect x="169" y="48" width="10" height="4" rx="1.5"/><rect x="169" y="56" width="10" height="4" rx="1.5"/>
    <rect x="169" y="64" width="10" height="4" rx="1.5"/><rect x="169" y="72" width="10" height="4" rx="1.5"/>
    <rect x="169" y="80" width="10" height="4" rx="1.5"/>
  </g>
  <!-- Chip -->
  <rect x="55" y="28" width="90" height="48" rx="3" fill="#3D6B3D" stroke="#2A4A2A" stroke-width="1"/>
  <rect x="63" y="32" width="74" height="40" rx="3" fill="#D0D0D0" stroke="#999" stroke-width="1"/>
  <text x="100" y="57" font-size="8" fill="#333" text-anchor="middle" font-family="monospace">ESP32-H2</text>
  <!-- USB-C port -->
  <rect x="80" y="90" width="40" height="12" rx="4" fill="#666" stroke="#555" stroke-width="1"/>
  <rect x="86" y="92" width="28" height="8" rx="2" fill="#444"/>
  <!-- LED -->
  <circle cx="60" cy="24" r="2" fill="#FFD700"/>
  <circle cx="140" cy="24" r="2" fill="#FF4444" opacity="0.7"/>
  <!-- Antenna area -->
  <rect x="148" y="80" width="24" height="6" rx="1" fill="#1A301A" opacity="0.15"/>
  <text x="100" y="118" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">ESP32-H2</text>
</svg>"""


BOARD_ILLUSTRATIONS = {
    "ESP32 Dev Module": board_esp32_devkit,
    "NodeMCU-32S": board_nodemcu,
    "ESP32-S3 DevKitC": board_esp32s3,
    "ESP32-C3 DevKit": board_esp32c3,
    "ESP32-S2 Saola": board_esp32s2,
    "ESP32-C6 Dev Module": board_esp32c6,
    "ESP32-H2 Dev Module": board_esp32h2,
}

ESPY_MOODS = {
    "idle": espy_glasses,
    "happy": espy_happy,
    "wink": espy_wink,
    "surprise": espy_surprise,
    "sad": espy_sad,
    "searching": espy_searching,
    "focused": espy_focused,
    "sweat": espy_sweat,
    "excited": espy_excited,
    "peek": espy_peek,
    "listening": espy_listening,
}
