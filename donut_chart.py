# ─────────────────────────────────────────────
# CHART 1: DONUT – Zusammensetzung des Preises
# ─────────────────────────────────────────────
def erstelle_donut_chart(faktoren):
    """
    Zeigt den relativen Einfluss jedes Faktors
    als Anteil am Gesamtpreis (in Prozent).
    """
    # Nur Faktoren ohne Basispreis und nur wenn sie vom Standard (1.0) abweichen
    labels = []
    anteile = []

    faktor_map = {
        "Zimmerzahl":  faktoren["Zimmerzahl"],
        "Zustand":     faktoren["Zustand"],
        "Stockwerk":   faktoren["Stockwerk"],
        "Baujahr":     faktoren["Baujahr"],
        "Ausstattung": faktoren["Ausstattung"],
    }

    # Basispreis als grössten Anteil setzen
    gesamt = faktoren["Basispreis (Quartier)"]
    basis_anteil = 100.0

    # Anteil jedes Faktors berechnen (Abweichung von 1.0 in Prozent)
    faktor_anteile = {}
    for name, wert in faktor_map.items():
        abweichung = abs((wert - 1.0) * 100)
        if abweichung > 0.1:  # nur relevante Faktoren anzeigen
            faktor_anteile[name] = round(abweichung, 1)
            basis_anteil -= abweichung

    labels = ["Lage (Quartier)"] + list(faktor_anteile.keys())
    werte  = [round(max(basis_anteil, 50), 1)] + list(faktor_anteile.values())
    farben = ["#378ADD", "#1D9E75", "#EF9F27", "#D85A30", "#7F77DD", "#5DCAA5"]

    fig = go.Figure(go.Pie(
        labels    = labels,
        values    = werte,
        hole      = 0.6,
        marker    = dict(colors=farben[:len(labels)]),
        textinfo  = "label+percent",
        hovertemplate = "<b>%{label}</b><br>Einfluss: %{value:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        title       = "Zusammensetzung des Preises – Einfluss der Faktoren",
        showlegend  = False,
        plot_bgcolor  = "white",
        paper_bgcolor = "white",
        margin = dict(t=60, b=20, l=20, r=20),
        annotations = [dict(
            text      = "Einfluss",
            x=0.5, y=0.5,
            font_size = 14,
            showarrow = False,
            font_color= "#6c757d"
        )]
    )
    return fig
