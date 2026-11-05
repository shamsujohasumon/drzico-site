# Inline SVG icon set: one stroke style (1.75px, round caps) across the site.
# Next.js: each key becomes a small <Icon name="..."/> component.

def svg(inner, cls="", label=None):
    aria = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true" focusable="false"'
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
            f'stroke-linecap="round" stroke-linejoin="round" {aria}>{inner}</svg>')

P = {
    # services
    "spine": '<rect x="8" y="2.5" width="8" height="3.2" rx="1.2"/><rect x="8" y="8" width="8" height="3.2" rx="1.2"/><rect x="8" y="13.5" width="8" height="3.2" rx="1.2"/><rect x="8" y="19" width="8" height="2.8" rx="1.2"/><path d="M5 4.1h3M16 4.1h3M5 9.6h3M16 9.6h3M5 15.1h3M16 15.1h3"/>',
    "disc": '<rect x="5" y="3" width="14" height="6" rx="2"/><rect x="5" y="15" width="14" height="6" rx="2"/><path d="M5 12h9.5"/><path d="M14.5 10.4c2.4 0 4 .7 4 1.6s-1.6 1.6-4 1.6"/>',
    "brain": '<path d="M9.5 4A2.5 2.5 0 0 0 7 6.3a2.8 2.8 0 0 0-2.4 4 2.8 2.8 0 0 0 .4 4.9A2.7 2.7 0 0 0 9 18.4 2.5 2.5 0 0 0 12 19.5V5.3A2.5 2.5 0 0 0 9.5 4Z"/><path d="M14.5 4A2.5 2.5 0 0 1 17 6.3a2.8 2.8 0 0 1 2.4 4 2.8 2.8 0 0 1-.4 4.9 2.7 2.7 0 0 1-4 3.2A2.5 2.5 0 0 1 12 19.5"/><path d="M8.5 9.5c1 0 1.8.6 2 1.5M15.5 9.5c-1 0-1.8.6-2 1.5M9 14.2c.8.2 1.5.7 1.8 1.4"/>',
    "drop": '<path d="M12 3.2S6.2 9.4 6.2 14a5.8 5.8 0 0 0 11.6 0C17.8 9.4 12 3.2 12 3.2Z"/><path d="M9.3 14.6a2.8 2.8 0 0 0 2.4 2.5"/>',
    "vessel": '<path d="M3.5 20.5c3.3-3.2 5.6-6.4 6.8-10.2"/><path d="M10.3 10.3c1.2-3.1 3.2-5.3 6.4-6.8"/><path d="M10.3 10.3c1.7 1.2 3.1 2.6 4 4.4"/><circle cx="16.6" cy="16.6" r="2.6"/>',
    "spinetumor": '<rect x="6" y="2.5" width="7" height="3.2" rx="1.2"/><rect x="6" y="8" width="7" height="3.2" rx="1.2"/><rect x="6" y="13.5" width="7" height="3.2" rx="1.2"/><rect x="6" y="19" width="7" height="2.8" rx="1.2"/><circle cx="17.5" cy="12" r="3"/><path d="M13 12h1.5"/>',
    "tb": '<rect x="8" y="2.5" width="8" height="3.2" rx="1.2"/><rect x="8" y="19" width="8" height="2.8" rx="1.2"/><path d="M8.6 8.4 15.4 16M15.4 8.4 8.6 16"/><circle cx="12" cy="12.2" r="5.2"/>',
    "head": '<path d="M8.5 21v-3.2A7 7 0 1 1 18 11.5l1.6 3.3h-2.1v3.4h-3.1V21"/><path d="M11 7.5v4M9 9.5h4"/>',
    "bolt": '<path d="M8.5 21v-3.2A7 7 0 1 1 18 11.5l1.6 3.3h-2.1v3.4h-3.1V21"/><path d="M12.6 5.8 10.4 9.6h2.8l-2.3 4"/>',
    # ui
    "phone": '<path d="M5 3.5h3.2l1.6 4.2-2.1 1.3a10.6 10.6 0 0 0 5.3 5.3l1.3-2.1 4.2 1.6V17a2.5 2.5 0 0 1-2.7 2.5A14.5 14.5 0 0 1 2.5 6.2 2.5 2.5 0 0 1 5 3.5Z"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/><path d="M8 14h2M12 14h2M8 17h2"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "pin": '<path d="M12 21s-6.5-5.7-6.5-11a6.5 6.5 0 0 1 13 0C18.5 15.3 12 21 12 21Z"/><circle cx="12" cy="10" r="2.4"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "alert": '<path d="M12 3.5 2.8 19.5h18.4L12 3.5Z"/><path d="M12 10v4.2M12 17.2v.1"/>',
    "check": '<path d="M4.5 12.5 9.5 17.5 19.5 6.5"/>',
    "shield": '<path d="M12 3 5 6v5.5c0 4.4 3 8 7 9.5 4-1.5 7-5.1 7-9.5V6l-7-3Z"/><path d="m9 12 2.2 2.2L15.5 10"/>',
    "up": '<path d="M12 19V5M6 11l6-6 6 6"/>',
    "cap": '<path d="M2.5 9 12 4.5 21.5 9 12 13.5 2.5 9Z"/><path d="M6.5 11v4.5c1.4 1.4 3.4 2 5.5 2s4.1-.6 5.5-2V11"/>',
    "scope": '<circle cx="12" cy="12" r="3.5"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3"/><circle cx="12" cy="12" r="8"/>',
    "users": '<circle cx="9" cy="8" r="3.2"/><path d="M3.5 19.5a5.5 5.5 0 0 1 11 0"/><path d="M16 5.2a3.2 3.2 0 0 1 0 6.1M17.5 14.2a5.5 5.5 0 0 1 3 5.3"/>',
    "image": '<rect x="3.5" y="4.5" width="17" height="15" rx="2.5"/><circle cx="9" cy="10" r="1.8"/><path d="m20.5 16-5-5-8.5 8.5"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6l1.4 1.4M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/>',
    "moon": '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5Z"/>',
    "play": '<path d="M8 5.5v13l10.5-6.5L8 5.5Z" fill="currentColor"/>',
    "file": '<path d="M7 3h7l5 5v12.5a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5V3.5A.5.5 0 0 1 7 3Z"/><path d="M14 3v5h5M9.5 13h5M9.5 16.5h5"/>',
}

def icon(name, cls="", label=None):
    return svg(P[name], cls, label)

# Large line drawing used in the portrait placeholder (not a person: a sagittal brain and spine outline)
PORTRAIT_ART = ('<svg viewBox="0 0 200 240" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true">'
    '<path d="M60 70c0-30 26-50 58-48 30 2 52 24 50 54-1 18-12 30-26 36l-6 3"/>'
    '<path d="M60 70c-10 6-14 18-10 30 4 12 16 20 30 20h26"/>'
    '<path d="M84 44c10 4 14 14 10 24M120 36c-4 10 0 22 12 26M146 64c-10 2-16 10-14 20M98 92c8-6 20-6 26 2"/>'
    '<path d="M116 124c2 10 2 20 0 30"/>'
    '<rect x="104" y="156" width="26" height="12" rx="4"/><rect x="104" y="174" width="26" height="12" rx="4"/>'
    '<rect x="104" y="192" width="26" height="12" rx="4"/><rect x="104" y="210" width="26" height="12" rx="4"/>'
    '</svg>')
