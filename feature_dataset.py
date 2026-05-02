# CHART 1: DONUT  Zusammensetzung des Preises
# feature_donut_chart
# Zeigt wie stark jeder Faktor den geschätzten Preis beeinflusst.
# Jeder Faktor ist ein Multiplikator: 1.0 = kein Einfluss,
# z.B. 1.05 = +5% auf den Preis, 0.95 = -5% auf den Preis


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
    # Beispiel: Baujahr = 0.95 → abs((0.95 - 1.0) * 100) = 5%

    faktor_anteile = {}
    for name, wert in faktor_map.items():
        abweichung = abs((wert - 1.0) * 100) #
        if abweichung > 0.1:  # nur relevante Faktoren anzeigen, die mehr als 0.1% Einfluss haben
            faktor_anteile[name] = round(abweichung, 1)
            basis_anteil -= abweichung 


    labels = ["Lage (Quartier)"] + list(faktor_anteile.keys()) # Lage als erster Faktor, da sie den Baispreis bestimmt, danach die anderen Faktoren
    werte  = [round(max(basis_anteil, 50), 1)] + list(faktor_anteile.values()) # Basisanteil auf mindestens 50% setzen, damit er sichtbar bleibt, auch wenn viele Faktoren Einfluss haben
    farben = ["#378ADD", "#1D9E75", "#EF9F27", "#D85A30", "#7F77DD", "#5DCAA5"] #Farbpalette für die Segmente


    fig = go.Figure(go.Pie( # Pie für Kreisdiagramm, mit hole=0.6 wird es zum Donut-Chart
        labels    = labels, # Beschriftungen für die Segmente (Faktoren)
        values    = werte, # Werte als Prozentanteile für die Darstellung im Donut-Chart
        hole      = 0.6, # 0.6 = 60% Loch in der Mitte → Donut-Chart
        marker    = dict(colors=farben[:len(labels)]),
        textinfo  = "label+percent", 
        hovertemplate = "<b>%{label}</b><br>Einfluss: %{value:.1f}%<extra></extra>", # benutzerdefinierte Hover-Info: zeigt den Faktor und seinen Einfluss in Prozent, ohne zusätzlichen Text (extra)
    ))


    fig.update_layout(
        title       = "Zusammensetzung des Preises --> Einfluss der Faktoren", # Titel über dem Chart
        showlegend  = False, # keine Legende, da die Labels direkt im Chart angezeigt werden
        plot_bgcolor  = "white", # Hintergrundfarbe des Chart-Bereichs 
        paper_bgcolor = "white", # Hintergrundfarbe der gesamten Grafik / Figure
        margin = dict(t=60, b=20, l=20, r=20), # etwas mehr Platz oben für den Titel (Abstände in Pixeln, top bottom left right)
        annotations = [dict( 
            text      = "Einfluss", # Text in der Mitte des Donuts
            x=0.5, y=0.5, # Text in der Mitte des Donuts
            font_size = 14, # etwas kleinerer Text in der Mitte
            showarrow = False, # kein Pfeil in der Mitte, nur text
            font_color= "#6c757d" # grau für den Text in der Mitte
        )]
    )
    # Figure zurückgeben → wird in Streamlit mit st.plotly_chart(fig) angezeigt
    return fig

# Zeile 40 noch nicht zufrieden, da der Basisanteil ein bisschen zu dominant sein könnte, wenn viele Faktoren Einfluss haben. Daher setze ich den Basisanteil auf mindestens 50%, damit er immer sichtbar bleibt, auch wenn viele Faktoren Einfluss haben. So bleibt die Visualisierung ausgewogen und der Basispreis ist immer erkennbar, auch wenn viele Faktoren den Preis beeinflussen.

# ACHTUNG: abs() entfernt das Vorzeichen – der Chart zeigt nur die GRÖSSE
# des Einflusses, nicht ob er den Preis erhöht oder senkt.
# Baujahr 1970 (Multiplikator 0.95) erscheint als "5%" – gleich wie
# ein preiserhöhender Faktor mit 1.05.