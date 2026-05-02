Gauge 

# ─────────────────────────────────────────────
# CHART 2: GAUGE – Preis im Marktvergleich
# ─────────────────────────────────────────────

def erstelle_gauge_chart(preis_pro_m2, quartier):
    """
    Zeigt ob der geschätzte Preis für das gewählte
    Quartier günstig, durchschnittlich oder teuer ist.
    """
    basispreis  = BASISPREIS_PRO_QUARTIER.get(quartier, 11000)
    min_preis   = min(BASISPREIS_PRO_QUARTIER.values())   # günstigstes Quartier
    max_preis   = max(BASISPREIS_PRO_QUARTIER.values())   # teuerstes Quartier

    fig = go.Figure(go.Indicator(
        mode  = "gauge+number+delta",
        value = preis_pro_m2,
        delta = {
            "reference": basispreis,
            "increasing": {"color": "#16a34a"},
            "decreasing": {"color": "#dc2626"},
            "suffix": " CHF/m²"
        },
        number = {"suffix": " CHF/m²", "font": {"size": 28}},
        title  = {"text": f"Preis im Vergleich zum Quartier-Durchschnitt ({quartier})",
                  "font": {"size": 14}},
        gauge  = {
            "axis": {
                "range":     [min_preis * 0.8, max_preis * 1.1],
                "ticksuffix": " CHF",
                "tickfont":   {"size": 11},
            },
            "bar":       {"color": "#2563eb"},
            "steps": [
                {"range": [min_preis * 0.8, min_preis * 1.1], "color": "#dcfce7"},
                {"range": [min_preis * 1.1, max_preis * 0.9], "color": "#fef9c3"},
                {"range": [max_preis * 0.9, max_preis * 1.1], "color": "#fee2e2"},
            ],
            "threshold": {
                "line":  {"color": "#1D9E75", "width": 3},
                "value": basispreis,
            },
        }
    ))

    fig.update_layout(
        plot_bgcolor  = "white",
        paper_bgcolor = "white",
        height        = 300,
        margin        = dict(t=80, b=20, l=40, r=40),
    )
    return fig