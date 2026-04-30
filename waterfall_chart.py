# ─────────────────────────────────────────────────────────────
# CHART 1b: WATERFALL – Zusammensetzung des Preises
# Ersetzt den Donut-Chart. Zeigt wie jeder Faktor den Preis
# erhöht (grün) oder senkt (rot) – mit korrektem Vorzeichen.
# ─────────────────────────────────────────────────────────────
def erstelle_waterfall_chart(faktoren, preis_pro_m2):
    """
    Zeigt den Aufbau des Preises als Wasserfall-Diagramm.
    Jeder Balken zeigt den CHF-Beitrag eines Faktors.
    Grün = preiserhöhend, Rot = preissenkend.

    Parameter:
        faktoren    (dict): Multiplikatoren aus berechne_preis()
        preis_pro_m2 (int): Endpreis pro m² aus berechne_preis()
    """

    basispreis = faktoren["Basispreis (Quartier)"]  # CHF/m² des Quartiers (ohne Korrekturen)

    # Faktoren die den Basispreis anpassen (ohne Lage)
    faktor_map = {
        "Zimmerzahl":  faktoren["Zimmerzahl"],
        "Zustand":     faktoren["Zustand"],
        "Stockwerk":   faktoren["Stockwerk"],
        "Baujahr":     faktoren["Baujahr"],
        "Ausstattung": faktoren["Ausstattung"],
    }

    # ── CHF-Beitrag jedes Faktors berechnen ──
    # Logik: Wie viel CHF/m² kommt durch diesen Faktor dazu oder weg?
    # Basispreis wird schrittweise mit jedem Faktor multipliziert.
    # Der Unterschied zum vorherigen Schritt = Beitrag dieses Faktors.
    #
    # Beispiel:
    #   Basispreis:          12'000
    #   × Zimmer (1.02):     12'240  → +240 CHF/m²
    #   × Zustand (1.10):    13'464  → +1'224 CHF/m²
    #   × Baujahr (0.95):    12'791  → -673 CHF/m²

    namen  = []   # x-Achse: Bezeichnungen
    werte  = []   # y-Achse: CHF-Beitrag pro Faktor
    farben = []   # grün = positiv, rot = negativ

    laufender_preis = basispreis  # startet beim Basispreis

    for name, faktor in faktor_map.items():
        neuer_preis = laufender_preis * faktor          # Preis nach diesem Faktor
        beitrag = round(neuer_preis - laufender_preis)  # Differenz = Einfluss in CHF

        if abs(beitrag) > 10:  # Faktoren unter CHF 10 Einfluss ignorieren
            namen.append(name)
            werte.append(beitrag)
            # Grün wenn Faktor Preis erhöht, Rot wenn er ihn senkt
            farben.append("#1D9E75" if beitrag >= 0 else "#D85A30")
            laufender_preis = neuer_preis  # nächster Faktor startet vom neuen Preis

    # Basispreis und Endpreis als Rahmen dazufügen
    # "inside" = Balken im Waterfall-Chart (relative Änderung)
    # "total"  = absoluter Wert (Basispreis und Endpreis)
    alle_namen  = ["Lage (Quartier)"] + namen           + ["Endpreis"]
    alle_werte  = [basispreis]        + werte           + [preis_pro_m2]
    alle_typen  = ["absolute"]        + ["relative"] * len(namen) + ["total"]
    alle_farben = ["#378ADD"]         + farben          + ["#2563eb"]

    # Waterfall-Chart erstellen
    fig = go.Figure(go.Waterfall(
        orientation = "v",                    # vertikale Balken
        measure     = alle_typen,             # "absolute", "relative" oder "total"
        x           = alle_namen,             # Beschriftung x-Achse
        y           = alle_werte,             # Werte in CHF/m²
        connector   = {"line": {"color": "#e2e8f0", "width": 1}},  # Verbindungslinien zwischen Balken
        text        = [
            f"+{v:,}".replace(",", "'") if v > 0
            else f"{v:,}".replace(",", "'")
            for v in alle_werte
        ],  # Wert direkt auf jedem Balken anzeigen, mit Vorzeichen
        textposition = "outside",             # Text oberhalb/unterhalb des Balkens
        increasing   = {"marker": {"color": "#1D9E75"}},  # grün für positive Balken
        decreasing   = {"marker": {"color": "#D85A30"}},  # rot für negative Balken
        totals       = {"marker": {"color": "#378ADD"}},  # blau für Lage und Endpreis
    ))

    fig.update_layout(
        title         = "Zusammensetzung des Preises – Einfluss der Faktoren (CHF/m²)",
        yaxis_title   = "CHF pro m²",
        plot_bgcolor  = "white",
        paper_bgcolor = "white",
        margin        = dict(t=60, b=20, l=20, r=20),
        showlegend    = False,
    )

    return fig