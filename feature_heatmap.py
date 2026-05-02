#feature_heatmap_chart

# ─────────────────────────────────────────────
# CHART 3: HEATMAP – Karte Zürich
# ─────────────────────────────────────────────
import folium

def erstelle_heatmap_karte(ausgewaehltes_quartier, quartier_koordinaten, basispreis_pro_quartier):
    """
    Erstellt eine interaktive Karte von Zürich mit
    farbigen Kreisen pro Quartier (grün = günstig, rot = teuer).
    Das ausgewählte Quartier wird speziell markiert.
    """
    # Karte auf Zürich zentrieren
    karte = folium.Map(
        location=[47.3769, 8.5417],
        zoom_start=12,
        tiles="CartoDB positron"   # helles, klares Kartenlayout
    )

    # Preisskala für Farbgebung berechnen
    alle_preise = list(basispreis_pro_quartier.values())
    min_p = min(alle_preise)
    max_p = max(alle_preise)

    def preis_zu_farbe(preis):
        """
        Berechnet eine Farbe auf der Skala grün → gelb → rot
        basierend auf dem Preis relativ zum Min/Max.
        """
        ratio = (preis - min_p) / (max_p - min_p)  # 0 = günstig, 1 = teuer
        if ratio < 0.5:
            # grün → gelb
            r = int(255 * (ratio * 2))
            g = 200
            b = 50
        else:
            # gelb → rot
            r = 220
            g = int(200 * (1 - (ratio - 0.5) * 2))
            b = 50
        return f"#{r:02x}{g:02x}{b:02x}"

    # Kreise für jedes Quartier zeichnen
    for quartier, (lat, lon) in quartier_koordinaten.items():
        preis = basispreis_pro_quartier.get(quartier, 11000)
        farbe = preis_zu_farbe(preis)

        # Ausgewähltes Quartier speziell hervorheben
        ist_ausgewaehlt = (quartier == ausgewaehltes_quartier)
        rand_farbe  = "#1a1a2e" if ist_ausgewaehlt else "#ffffff"
        rand_breite = 3 if ist_ausgewaehlt else 1
        radius      = 600 if ist_ausgewaehlt else 450 #rausnehmen?

        # Kreis mit Tooltip
        folium.CircleMarker(
            location = [lat, lon],
            radius   = 18 if ist_ausgewaehlt else 14,
            color    = rand_farbe,
            weight   = rand_breite,
            fill           = True,
            fill_color     = farbe,
            fill_opacity   = 0.85,
            tooltip = folium.Tooltip(
                f"<b>{quartier}</b><br>"
                f"Basispreis: CHF {preis:,}/m²".replace(",", "'")
                + (" ← Ihre Immobilie" if ist_ausgewaehlt else "")
            )
        ).add_to(karte)

        # Quartier-Name als Label
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(
                html=f'<div style="font-size:9px; font-weight:{"700" if ist_ausgewaehlt else "500"}; '
                     f'color:#1a1a2e; white-space:nowrap; '
                     f'text-shadow: 1px 1px 2px white, -1px -1px 2px white;">'
                     f'{quartier}</div>',
                icon_size=(120, 20),
                icon_anchor=(60, -8),
            )
        ).add_to(karte)

    # Legende hinzufügen
    legende_html = """
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                background: white; padding: 12px 16px; border-radius: 8px;
                border: 1px solid #e2e8f0; font-size: 12px; font-family: sans-serif;">
        <b style="font-size:13px;">Preis pro m²</b><br><br>
        <span style="display:inline-block;width:14px;height:14px;
              background:#00c832;border-radius:50%;margin-right:6px;
              vertical-align:middle;"></span>Günstig (&lt; CHF 10'000)<br>
        <span style="display:inline-block;width:14px;height:14px;
              background:#ffc832;border-radius:50%;margin-right:6px;
              vertical-align:middle;"></span>Mittel (CHF 10'000–14'000)<br>
        <span style="display:inline-block;width:14px;height:14px;
              background:#dc3232;border-radius:50%;margin-right:6px;
              vertical-align:middle;"></span>Teuer (&gt; CHF 14'000)
    </div>
    """
    karte.get_root().html.add_child(folium.Element(legende_html))

    return karte