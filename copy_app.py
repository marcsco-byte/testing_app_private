# =============================================================
# fragebogen.py – Immobilien-Preisschätzer Zürich
# Ausführen im Terminal: streamlit run fragebogen.py
# =============================================================

import streamlit as st #importiert das Framework Streamlit, mit der Abkürzung st
import plotly.graph_objects as go #importiert eine Bibliothek für interaktive Diagramme mit der low-level Variante go
import plotly.express as px #???? raus nehmen, nutzen wir nicht???? Bibliothek für interaktive Diagramme, px als high-level Variante
import folium #importiert interaktive Landkarten
from streamlit_folium import st_folium #Bindeglied, damit die Karte in Streamlit angezeigt werden kann
from feature_dataset import get_daten #importiert get_daten vom Dataset Feature

# Seitenkonfiguration von Streamlit: Titel setzen und mittig zentrieren
st.set_page_config(
    page_title="Immobilien-Preisschätzer Zürich",
    layout="centered"
)

# ─────────────────────────────────────────────
# BASISPREISE PRO QUARTIER (CHF pro m²)
# ─────────────────────────────────────────────
df= get_daten()
#Daten werden einmalig geladen (aus Feature Dataset.py)
BASISPREIS_PRO_QUARTIER = (
    df.groupby("Quartier")["Preis_pro_m2"]
    .mean()
    .round()
    .astype(int)
    .to_dict()
)


# ─────────────────────────────────────────────
# KOORDINATEN DER QUARTIERE (Mittelpunkte)
# Für die Heatmap auf der Karte !!!!! wird noch geändert
# ─────────────────────────────────────────────
QUARTIER_KOORDINATEN = {
    "Affoltern":            (47.4233, 8.5117),
    "Albisrieden":          (47.3733, 8.4900),
    "Altstetten":           (47.3867, 8.4833),
    "City":                 (47.3744, 8.5410),
    "Enge":                 (47.3617, 8.5300),
    "Escher Wyss":          (47.3883, 8.5167),
    "Fluntern":             (47.3833, 8.5617),
    "Gewerbeschule":        (47.3783, 8.5367),
    "Hard":                 (47.3817, 8.5067),
    "Hirslanden":           (47.3617, 8.5733),
    "Hirzenbach":           (47.4000, 8.5817),
    "Hochschulen":          (47.3767, 8.5483),
    "Hoengg":               (47.4000, 8.4933),
    "Hottingen":            (47.3700, 8.5617),
    "Langstrasse":          (47.3783, 8.5233),
    "Leimbach":             (47.3333, 8.5100),
    "Lindenhof":            (47.3683, 8.5217),
    "Oerlikon":             (47.4083, 8.5433),
    "Rathaus":              (47.3717, 8.5433),
    "Schwamendingen-Mitte": (47.4083, 8.5650),
    "Seebach":              (47.4250, 8.5367),
    "Wollishofen":          (47.3433, 8.5283),
    "Wipkingen":            (47.3933, 8.5267),
    "Witikon":              (47.3567, 8.5917),
}

# ─────────────────────────────────────────────
# KORREKTURFAKTOREN:Der Faktor wird mit dem Basispreis mulitpliziert und passt den Preis prozentual an. Bsp. Faktor 0.92 = Preis wird um 8% reduziert. Die Faktoren basieren auf Schätzwerten.
# ─────────────────────────────────────────────
FAKTOR_ZIMMER = {
    "1": 0.92, "1.5": 0.95, "2": 0.97, "2.5": 0.99,
    "3": 1.00, "3.5": 1.01, "4": 1.02, "4.5": 1.03, "5+": 1.04,
} 

FAKTOR_ZUSTAND = {
    "Neuwertig / Neubau":    1.10,
    "Gut gepflegt":          1.00,
    "Renovationsbeduerftig": 0.85,
}

FAKTOR_STOCKWERK = {
    "Erdgeschoss":       0.95,
    "1. Obergeschoss":   0.98,
    "2. Obergeschoss":   1.00,
    "3. Obergeschoss":   1.02,
    "4. Obergeschoss":   1.04,
    "5. OG oder hoeher": 1.06,
    "Dachgeschoss":      1.08,
}

AUSSTATTUNG_FAKTOREN = {
    "hat_balkon":    0.03,
    "hat_parkplatz": 0.04,
    "hat_lift":      0.02,
    "hat_keller":    0.01,
    "hat_seesicht":  0.08,
    "hat_minergie":  0.03,
} #Jede zusätzliche Ausstattung addiert einen Prozentsatz zum Preis: Bsp. Faktor 0.03 = +3%. Der Prozentsatz basiert auf Schätzwerten.

AUSSTATTUNG_LABELS = {
    "hat_balkon":    "Balkon / Terrasse",
    "hat_parkplatz": "Parkplatz / Garage",
    "hat_lift":      "Lift",
    "hat_keller":    "Keller / Estrich",
    "hat_seesicht":  "Seesicht",
    "hat_minergie":  "Minergie",
} #Übersetzung von Bezeichnungen in Texte, welche in der App ersichtlich sind


# ─────────────────────────────────────────────
# BAUJAHR-FAKTOR: 
# ─────────────────────────────────────────────
def faktor_baujahr(baujahr):
    alter = 2026 - baujahr #Alter der Immobilie wird berechnet. Das Alter wird in Kategorien eingeteil. Bsp. wenn Immobilie jünger als 5 Jahre ist, wird der Preis um 10% erhöht.
    if alter <= 5:    return 1.10
    elif alter <= 15: return 1.05
    elif alter <= 30: return 1.00
    elif alter <= 50: return 0.95
    else:             return 0.90


# ─────────────────────────────────────────────
# BERECHNUNGSFUNKTION: Die Funktion berechne_preis wird definiert
# ─────────────────────────────────────────────
def berechne_preis(quartier, zimmerzahl, wohnflaeche, baujahr,
                   stockwerk, zustand, ausstattung): #Definition einer Funktion mit Eingabewerten
    basispreis  = BASISPREIS_PRO_QUARTIER.get(quartier, 11000) #holt den Wert, der bei quartier als Input angegeben wurde und sucht dessen Basispreis. Falls der Wert nicht gefunden wurde, wird 11000 als Standardwert verwendet.
    f_zimmer    = FAKTOR_ZIMMER.get(zimmerzahl, 1.00) #holt den Wert, der bei zimmerzahl als Input angegeben wurde und nimmt den Korrekturfaktor. Falls der Wert nicht gefunden wurde, wird 1.00 als Standardwert verwendet.
    f_zustand   = FAKTOR_ZUSTAND.get(zustand, 1.00) #holt den Wert, der bei zustand als Input angegeben wurde und nimmt den Korrekturfaktor. Falls der Wert nicht gefunden wurde, wird 1.00 als Standardwert verwendet.
    f_stockwerk = FAKTOR_STOCKWERK.get(stockwerk, 1.00) #holt den Wert, der bei stockwerk als Input angegeben wurde und nimmt den Korrekturfaktor. Falls der Wert nicht gefunden wurde, wird 1.00 als Standardwert verwendet.
    f_baujahr   = faktor_baujahr(baujahr) #holt den Wert, der bei baujahr als Input angegeben wurde und nimmt den Korrekturfaktor.

    f_ausstattung = 1.00 #Startet bei 1.00. 
    for merkmal, wert in ausstattung.items(): #Iteriert mit einer for Schleife durch alle Ausstattungsmerkmale durch
        if wert: #Nur wenn eine Checkbox aktiviert ist (deren Wert = True) wird der nächste Schritt durchgeführt
            f_ausstattung += AUSSTATTUNG_FAKTOREN.get(merkmal, 0) #Holt den Faktor für das Ausstattungsmerkmal aus dem obigen Dictionary und addiert ihn zu 1.00

    preis_pro_m2 = (basispreis * f_zimmer * f_zustand
                    * f_stockwerk * f_baujahr * f_ausstattung) #Berechnet den Preis pro Quadratmeter inklusive allen Korrekturfaktoren
    gesamtpreis  = preis_pro_m2 * wohnflaeche #Berechnet den Gesamtpreis indem der Preis pro Quadratmeter mit der wohnflaeche als Input Multipliziert wird

    faktoren = { #speichert die berechneten Faktoren als Dictionary ab
        "Basispreis (Quartier)": basispreis,
        "Zimmerzahl":            f_zimmer,
        "Zustand":               f_zustand,
        "Stockwerk":             f_stockwerk,
        "Baujahr":               f_baujahr,
        "Ausstattung":           f_ausstattung,
    }

    return round(preis_pro_m2), round(gesamtpreis), faktoren #gibt den gerundeten Preis pro m2, den gerundeten Gesamtpreis und das Dictionary der Faktoren zurück


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


# ─────────────────────────────────────────────
# CHART 3: HEATMAP – Karte Zürich
# ─────────────────────────────────────────────
def erstelle_heatmap_karte(ausgewaehltes_quartier=None):
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
    alle_preise = list(BASISPREIS_PRO_QUARTIER.values())
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
    for quartier, (lat, lon) in QUARTIER_KOORDINATEN.items():
        preis = BASISPREIS_PRO_QUARTIER.get(quartier, 11000)
        farbe = preis_zu_farbe(preis)

        # Ausgewähltes Quartier speziell hervorheben
        ist_ausgewaehlt = (quartier == ausgewaehltes_quartier)
        rand_farbe  = "#1a1a2e" if ist_ausgewaehlt else "#ffffff"
        rand_breite = 3 if ist_ausgewaehlt else 1
        radius      = 600 if ist_ausgewaehlt else 450

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


# =============================================================
# STREAMLIT APP
# =============================================================

st.title("Immobilien-Preisschaetzer Zürich")
st.write("Gib die Eigenschaften deiner Immobilie ein - wir berechnen den geschätzten Marktwert.")
st.markdown("---")

# ── 1. LAGE ──
st.subheader("Lage")
QUARTIERE = ["— Bitte waehlen —"] + sorted(BASISPREIS_PRO_QUARTIER.keys())
quartier  = st.selectbox("In welchem Stadtquartier liegt die Immobilie?", options=QUARTIERE)

# ── 2. GROESSE ──
st.subheader("Groesse")
col1, col2 = st.columns(2)
with col1:
    zimmerzahl = st.selectbox(
        "Anzahl Zimmer",
        options=["1", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5+"],
        index=4
    )
with col2:
    wohnflaeche = st.number_input(
        "Wohnflaeche (m2)", min_value=20, max_value=500, value=80, step=5
    )

# ── 3. GEBAEUDE ──
st.subheader("Gebaeude")
col3, col4 = st.columns(2)
with col3:
    baujahr = st.slider("Baujahr", min_value=1900, max_value=2026, value=1990)
with col4:
    stockwerk = st.selectbox(
        "Stockwerk",
        options=[
            "Erdgeschoss", "1. Obergeschoss", "2. Obergeschoss",
            "3. Obergeschoss", "4. Obergeschoss",
            "5. OG oder hoeher", "Dachgeschoss"
        ]
    )

# ── 4. ZUSTAND ──
st.subheader("Zustand")
zustand = st.radio(
    "Wie ist der aktuelle Renovationsstand?",
    options=["Neuwertig / Neubau", "Gut gepflegt", "Renovationsbeduerftig"],
    index=1,
    horizontal=True
)

# ── 5. AUSSTATTUNG ──
st.subheader("Ausstattung")
col5, col6 = st.columns(2)
with col5:
    hat_balkon    = st.checkbox("Balkon / Terrasse")
    hat_parkplatz = st.checkbox("Parkplatz / Garage")
    hat_lift      = st.checkbox("Lift im Gebaeude")
with col6:
    hat_keller   = st.checkbox("Keller / Estrich")
    hat_seesicht = st.checkbox("Seesicht / Aussicht")
    hat_minergie = st.checkbox("Minergie-Standard")

# ── 6. BERECHNUNG & ERGEBNIS ──
st.markdown("---")
berechnen = st.button("Marktwert berechnen")

# Session State initialisieren – speichert Ergebnisse über Neuladen hinweg
if "ergebnis" not in st.session_state:
    st.session_state.ergebnis = None

if berechnen:
    if quartier == "— Bitte waehlen —":
        st.error("Bitte waehle ein Stadtquartier aus.")
    else:
        ausstattung = {
            "hat_balkon":    hat_balkon,
            "hat_parkplatz": hat_parkplatz,
            "hat_lift":      hat_lift,
            "hat_keller":    hat_keller,
            "hat_seesicht":  hat_seesicht,
            "hat_minergie":  hat_minergie,
        }

        preis_pro_m2, gesamtpreis, faktoren = berechne_preis(
            quartier, zimmerzahl, wohnflaeche,
            baujahr, stockwerk, zustand, ausstattung
        )

        # Ergebnis im Session State speichern
        st.session_state.ergebnis = {
            "preis_pro_m2": preis_pro_m2,
            "gesamtpreis":  gesamtpreis,
            "faktoren":     faktoren,
            "quartier":     quartier,
        }

# Ergebnis anzeigen – bleibt sichtbar solange session_state gefüllt ist
if st.session_state.ergebnis:
    e = st.session_state.ergebnis

    st.markdown("### Geschaetzter Marktwert")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.metric(
            label="Geschaetzter Kaufpreis",
            value=f"CHF {e['gesamtpreis']:,.0f}".replace(",", "'")
        )
    with col_r2:
        st.metric(
            label="Preis pro m2",
            value=f"CHF {e['preis_pro_m2']:,.0f}".replace(",", "'")
        )

    st.markdown("---")

    # Chart 1: Donut
    st.markdown("### Zusammensetzung des Preises")
    st.caption("Prozentualer Einfluss der einzelnen Merkmale auf den Endpreis.")
    fig_waterfall = erstelle_waterfall_chart(e["faktoren"], e["preis_pro_m2"])
    st.plotly_chart(fig_waterfall, width="stretch")

    # Chart 2: Gauge
    st.markdown("### Preis im Marktvergleich")
    st.caption(
        f"Der grüne Strich zeigt den Basispreis für {e['quartier']}. "
        "Die farbigen Zonen zeigen günstig (grün), mittel (gelb) und teuer (rot)."
    )
    fig_gauge = erstelle_gauge_chart(e["preis_pro_m2"], e["quartier"])
    st.plotly_chart(fig_gauge, width="stretch")

    # Chart 3: Heatmap
    st.markdown("### Preisübersicht Zürich – Heatmap")
    st.caption(
        "Grün = günstigere Quartiere, Rot = teurere Quartiere. "
        "Ihr Quartier ist dunkel umrandet."
    )
    karte = erstelle_heatmap_karte(ausgewaehltes_quartier=e["quartier"])
    st_folium(karte, use_container_width=True, height=450)