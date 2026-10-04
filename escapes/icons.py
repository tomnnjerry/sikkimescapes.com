"""Line icons (24x24, stroke = currentColor). One per district, one per experience kind, plus UI icons.

Drawn for Sikkim Escapes; render with {% icon "gompa" %} or {% icon "gompa" "icon--lg" %}.
"""

ICONS = {
    # ---- districts
    "gompa":  # East / Gangtok: monastery with sloped golden roof, finial and prayer flag pole
        '<path d="M3 21h18"/><path d="M5 21v-7h14v7"/><path d="M3.5 14L7 9.5h10l3.5 4.5"/><path d="M7.5 9.5L9 7h6l1.5 2.5"/>'
        '<path d="M12 7V3.5"/><path d="M11 4.5h2"/><path d="M10.2 21v-3.2a1.8 1.8 0 0 1 3.6 0V21"/><path d="M7.5 16.5h1.5M15 16.5h1.5"/>',
    "glacier":  # North / Mangan: a high lake under a glacier peak
        '<path d="M2 15l5-8 3 4 3-6 9 10z"/><path d="M10 11l1.4 1.6L13 5"/><path d="M15.5 9.8l1.2 1.7 1.3-.9"/>'
        '<path d="M4 18.5c2.5-1 5-1 8 0s5.5 1 8 0"/><path d="M7 21c1.8-.6 3.6-.6 5 0s3.2.6 5 0"/>',
    "summit":  # West / Gyalshing: Kangchenjunga's five summits with the sun rising behind
        '<path d="M2 20l4.5-7 2 2.5L12 8l3.5 5.5 2-2.5L22 20z"/><path d="M12 8l-1.5 3.5L12 11l1.3 1.5"/>'
        '<path d="M8 5.5a4 4 0 0 1 8 0"/><path d="M12 1.5v1M6.5 3.2l.7.7M17.5 3.2l-.7.7"/>',
    "tealeaf":  # South / Namchi: two leaves and a bud with a terrace line
        '<path d="M12 19c-.4-4.8 1.4-8.6 6.5-11.5.4 5.6-1.8 9.4-6.5 11.5z"/><path d="M12 19c-3.6-1.3-6.3-4.3-6.3-9 3.6 1.3 5.9 3.9 6.3 9z"/>'
        '<path d="M12 19c.3-2.6 1.4-5.2 3.6-7.4M12 19c-.9-2.2-2.2-4.3-4.5-6"/><path d="M12.4 6.6c-.7-1.4-.5-2.7.5-3.6.9 1.1.8 2.3-.5 3.6z"/>'
        '<path d="M3 21.5h18"/>',
    "zigzag":  # Pakyong / Silk Route: the Zuluk loops climbing a slope
        '<path d="M4 21h4l9-3.5-9-3 9-3-9-3 8-3"/><circle cx="16" cy="4.5" r="1.3"/><path d="M2 21h20"/>',
    "rhododendron":  # Soreng / Barsey: a rhododendron truss
        '<circle cx="12" cy="8" r="2.6"/><circle cx="8" cy="10.5" r="2.6"/><circle cx="16" cy="10.5" r="2.6"/><circle cx="10" cy="13.8" r="2.4"/><circle cx="14" cy="13.8" r="2.4"/>'
        '<path d="M12 16.5V21"/><path d="M12 19c-2.5-.2-4.5 1-5.5 2.5M12 19c2.5-.2 4.5 1 5.5 2.5"/>',
    # ---- experience kinds
    "culture": '<path d="M4 21h16"/><path d="M6 21v-9h12v9"/><path d="M3 12l9-7 9 7"/><path d="M10 21v-4h4v4"/><path d="M12 5V2.5"/>',
    "spiritual":  # prayer wheel
        '<rect x="8" y="6" width="8" height="10" rx="1.5"/><path d="M8 9h8M8 13h8"/><path d="M12 6V3M12 16v5"/><path d="M16 11h3.5l1.5 2"/>',
    "nature": '<path d="M2 20l7-11 4 6 3-4 6 9z"/><circle cx="17.5" cy="5.5" r="2"/>',
    "wildlife":  # red panda face
        '<path d="M5 7.5L4 4l4 2M19 7.5L20 4l-4 2"/><path d="M4.5 12c0-4 3.4-6.5 7.5-6.5s7.5 2.5 7.5 6.5-3.4 7-7.5 7-7.5-3-7.5-7z"/>'
        '<path d="M8 10.5c.8-.6 1.6-.6 2.2 0M13.8 10.5c.6-.6 1.4-.6 2.2 0"/><path d="M11 14h2l-1 1z"/><path d="M7.5 13.5c1 .4 1.6 1.4 1.8 2.4M16.5 13.5c-1 .4-1.6 1.4-1.8 2.4"/>',
    "food":  # momo in a bamboo steamer
        '<path d="M3 13h18v3a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3z"/><path d="M3 16h18"/>'
        '<path d="M6.5 13c0-2.2 1.3-3.5 2.7-3.5s2.7 1.3 2.7 3.5M12.1 13c0-2.2 1.3-3.5 2.7-3.5s2.7 1.3 2.7 3.5"/><path d="M9.2 9.5V8.6M14.8 9.5V8.6"/><path d="M9 5c0-1 1-1.5 1-2.5M14 5c0-1 1-1.5 1-2.5"/>',
    "adventure":  # boot print on a trail with a summit flag
        '<path d="M3 20l5-7 3 3 4-6 6 10z"/><path d="M15 10V4l3.5 1.5L15 7"/>',
    "craft":  # choktse table carving / thangka scroll
        '<path d="M6 3h12M6 21h12"/><path d="M7 3v18M17 3v18"/><path d="M10 8c1.2-1.2 2.8-1.2 4 0M9.5 12h5M10 16c1.2 1.2 2.8 1.2 4 0"/>',
    "village":  # homestay house with a smoke curl and a field
        '<path d="M3 21h18"/><path d="M5 21v-8l7-5.5 7 5.5v8"/><path d="M3.5 14l8.5-7 8.5 7"/><path d="M10 21v-4h4v4"/>'
        '<path d="M16.5 7V4"/><path d="M16.5 4c0-1 1-1.3 1-2.2"/>',
    "wellness":  # hot spring
        '<path d="M3 17c2.5 2.5 15.5 2.5 18 0"/><path d="M3 17c0-1.5 3-2.5 9-2.5s9 1 9 2.5"/>'
        '<path d="M8 12c-1-1.2 1-2.3 0-3.5s1-2.3 0-3.5M12 12c-1-1.2 1-2.3 0-3.5s1-2.3 0-3.5M16 12c-1-1.2 1-2.3 0-3.5s1-2.3 0-3.5"/>',
    # ---- UI
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "book": '<path d="M4 4h6a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4z"/><path d="M20 4h-6a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h7z"/>',
    "route": '<circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h6a3 3 0 0 0 0-6h-4a3 3 0 0 1 0-6h6"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 10h8M8 13h5"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "jeep":  # shared jeep: the budget icon
        '<path d="M3 16v-4l2-4h10l3 4h3v4"/><path d="M5 8l-.5 4h13"/><path d="M10 8v4"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M9 17h6M3 16h2M19 16h2"/>',
    "rupee": '<path d="M7 4h10M7 8h10"/><path d="M7 4h3.5a4 4 0 0 1 0 8H7l8 8"/>',
    "permit": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h4"/><circle cx="16.5" cy="16.5" r="1.5"/>',
    "altitude": '<path d="M2 20l6-9 3.5 4.5L15 10l7 10z"/><path d="M19 3v7M17 5l2-2 2 2"/>',
    "flag": '<path d="M4 21V4"/><path d="M4 4c3-1.5 5 1 8 0s5-1.5 8 0v8c-3-1.5-5 1-8 0s-5-1.5-8 0"/>',
    "story": '<path d="M5 4h11l3 3v13H5z"/><path d="M8 9h8M8 12.5h8M8 16h5"/><path d="M16 4v3h3"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/>',
    "whatsapp": '<path d="M4 20l1.3-4A8 8 0 1 1 8 18.7z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 1c-1-.5-1.5-1-2-2l1-1-1-2z"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>',
    "sparkle": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/>',
}


def svg(name, cls=""):
    body = ICONS.get(name) or ICONS["sparkle"]
    return (f'<svg class="icon {cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')
