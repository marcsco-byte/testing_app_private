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
from feature_Koordinaten import get_koordinaten
from feature_heatmap_chart import erstelle_heatmap_karte

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
# Fuer die Heatmap auf der Karte !!!!! wurde mit feature_Koordinaten angepasst
# ─────────────────────────────────────────────

QUARTIER_KOORDINATEN = get_koordinaten()


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

# =============================================================
# STREAMLIT APP
# =============================================================

st.title("Immobilien-Preisschaetzer Zürich") #Erstellt den Titel in Streamlit
st.write("Gib die Eigenschaften deiner Immobilie ein - wir berechnen den geschätzten Marktwert.") #Erstellt den Beschreibungstext in Streamlit
st.markdown("---") #Erstellt eine horizontale Trennlinie in Streamlit

# ── 1. LAGE ──
st.subheader("Lage") #Erstellt einen Untertitel in Streamlit
QUARTIERE = ["— Bitte waehlen —"] + sorted(BASISPREIS_PRO_QUARTIER.keys()) #Zwei Listen werden erstellt und miteinander verbunden. Die erste besteht aus dem Platzhalter: Bitte waehlen. Die zweite Liste besteht aus allen Schlüsseln (Quartiernamen) des Dictionaries, welche alphabetisch sortiert werden.
quartier  = st.selectbox("In welchem Stadtquartier liegt die Immobilie?", options=QUARTIERE) #Ein Dropdown Menü wird in Streamlit erstellt mit einem Beschriftungstext. Das Dropdown Menu beinhaltet eine Liste aller Optionen, die in der vorherigen Zeile definiert wurde. 

# ── 2. GROESSE ──
st.subheader("Groesse") #Erstellt einen Untertitel in Streamlit
col1, col2 = st.columns(2) #Die Seite wird in zwei gleich breite Spalten aufgeteilt. col1 links und col2 rechts.
with col1: #Definiert, was in der linken Spalte angezeigt wird
    zimmerzahl = st.selectbox( #Erstellt ein Dropdown Menü und speichert den Eingabewert unter zimmerzahl ab
        "Anzahl Zimmer", #Definiert den Text über dem Dropdown Menu
        options=["1", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5+"], #Beschreibt die Liste aller auswählbaren Optionen
        index=0 #Definiert den Standardwert bei Index 0 --> 1 Zimmer
    )
with col2: #Definiert, was in der rechten Spalte angezeigt wird
    wohnflaeche = st.number_input( #Erstellt ein Eingabefeld und speichert den Eingabewert unter wohnflaeche
        "Wohnflaeche (m2)", min_value=10, max_value=500, value=10, step=5 #Definiert die kleinste erlaubte Zahl, die grösste erlaubte Zahl, den Standardwert und die Steps (wenn man auf + klickt, springt die Zahl um diesen Wert)
    )

# ── 3. GEBAEUDE ──
st.subheader("Gebaeude") #Erstellt einen Untertitel in Streamlit
col3, col4 = st.columns(2) #Die Seite wird in zwei gleich breite Spalten aufgeteilt. col3 links und col4 rechts.
with col3: #Definiert die linke Seite
    baujahr = st.slider("Baujahr", min_value=1900, max_value=2026, value=1990) #Erstellt einen Schieberegler in Streamlit mit dem Beschriftungstext, dem Mindestwert, dem Maximalwert und dem Standardwert und speichert den Eingabewert unter baujahr
with col4: #Definiert die rechte Seite
    stockwerk = st.selectbox( #Erstellt ein Dropdown Menu und speichert den Eingabewert unter stockwerk ab
        "Stockwerk", #Definiert den Text über dem Dropdown Menü
        options=[ #Beschreibt die Liste aller auswählbaren Optionen, Erdgeschoss wird mit index 0 als Stadardwert gezeigt
            "Erdgeschoss", "1. Obergeschoss", "2. Obergeschoss",
            "3. Obergeschoss", "4. Obergeschoss",
            "5. OG oder hoeher", "Dachgeschoss"
        ]
    )

# ── 4. ZUSTAND ──
st.subheader("Zustand") #Erstellt einen Untertitel in Streamlit
zustand = st.radio( #Erstellt buttons, von denen der User eine Option wählen kann
    "Wie ist der aktuelle Renovationsstand?", #Definiert den Text über den Buttons
    options=["Neuwertig / Neubau", "Gut gepflegt", "Renovationsbeduerftig"], #Definiert die Liste aller auswählbaren Optionen
    index=1, #Setzt Gut gepflegt als Standardwert
    horizontal=True #Formatiert die Buttons horizontal, also nebeneinander
)

# ── 5. AUSSTATTUNG ──
st.subheader("Ausstattung") #Erstellt einen Untertitel in Streamlit
col5, col6 = st.columns(2) #Die Seite wird in zwei gleich breite Spalten aufgeteilt. col5 links und col6 rechts
with col5: #Definiert die linke Seite
    hat_balkon    = st.checkbox("Balkon / Terrasse") #Erstellt Checkboxen, welche den Wert als True speichert, wenn die Checkbox aktiviert wurde und als False, wenn sie nicht aktiviert wurde. Die Standardwerte sind False
    hat_parkplatz = st.checkbox("Parkplatz / Garage")
    hat_lift      = st.checkbox("Lift im Gebaeude")
with col6:
    hat_keller   = st.checkbox("Keller / Estrich")
    hat_seesicht = st.checkbox("Seesicht / Aussicht")
    hat_minergie = st.checkbox("Minergie-Standard") #Erstellt Checkboxen, welche den Wert als True speichert, wenn die Checkbox aktiviert wurde und als False, wenn sie nicht aktiviert wurde. Die Standardwerte sind False

# ── 6. BERECHNUNG & ERGEBNIS ──
st.markdown("---") #Erstellt eine horizontale Trennlinie in Streamlit
berechnen = st.button("Marktwert berechnen") #Erstellt einen Button mit dem Text Marktwert berechnen, wenn der Button angeglickt wird, wird der Wert True in der variable berechnen gespeichert. Ansonsten False

# Session State initialisieren – speichert Ergebnisse über Neuladen hinweg. Erstellt leeren Platz für Ergebnis beim Start der App. Wird päter mit dem berechneten Preis überschrieben, sobald User auf Marktwert berechnen klickt.
if "ergebnis" not in st.session_state:
    st.session_state.ergebnis = None

if berechnen: #Sofern der Button Marktwert berechnen geklickt wurde, ist diese if-Bedingung true
    if quartier == "— Bitte waehlen —":
        st.error("Bitte waehle ein Stadtquartier aus.") #Erstellt eine Fehlermeldung mit dem Text Bitte waehle ein Stadtquartier aus, wenn bei quartier nichts angewählt wurde
    else:
        ausstattung = {
            "hat_balkon":    hat_balkon,
            "hat_parkplatz": hat_parkplatz,
            "hat_lift":      hat_lift,
            "hat_keller":    hat_keller,
            "hat_seesicht":  hat_seesicht,
            "hat_minergie":  hat_minergie, #Wenn die obige if Bedingung nicht erfüllt ist, werden alle Ausstattungswerte, welche angegeben wurden, in einem Dictionary zusammengefasst
        }

        preis_pro_m2, gesamtpreis, faktoren = berechne_preis( #Ruft die in Zeile 122-148 definierte Funktion ab und übergibt die Angaben des Users
            quartier, zimmerzahl, wohnflaeche,
            baujahr, stockwerk, zustand, ausstattung
        )

        # Ergebnis im Session State speichern
        st.session_state.ergebnis = { #überschreibt das none im session state mit den berechneten und eingegebenen Werten
            "preis_pro_m2": preis_pro_m2,
            "gesamtpreis":  gesamtpreis,
            "faktoren":     faktoren,
            "quartier":     quartier,
        }

# Ergebnis anzeigen – bleibt sichtbar solange session_state gefüllt ist: Sofern Ergebnisse im Session state abgespeichert wurden, wird eine Kurzform für session state definiert
if st.session_state.ergebnis:
    e = st.session_state.ergebnis

    st.markdown("### Geschaetzter Marktwert") #Erstellt einen mittelgrossen Titel in Streamlit
    col_r1, col_r2 = st.columns(2) #Die Seite wird in zwei gleich breite Spalten aufgeteilt. col_r1 links und col_r2 rechts
    with col_r1: #Definiert die linke Seite
        st.metric( #Formatiert die nächsten Zeilen als Kennzahlen (Kleiner Text + Grosse Zahl)
            label="Geschaetzter Kaufpreis", #Kleiner Text
            value=f"CHF {e['gesamtpreis']:,.0f}".replace(",", "'") #Grosse Zahl, die berechnet wurde. Zahl wird mit Hochkommas als Tausendertrennzeichen dargestellt
        )
    with col_r2: #Definiert die rechte Seite
        st.metric(#Formatiert die nächsten Zeilen als Kennzahlen (Kleiner Text + Grosse Zahl)
            label="Preis pro m2", #Kleiner Text
            value=f"CHF {e['preis_pro_m2']:,.0f}".replace(",", "'") #Grosse Zahl, die berechnet wurde. Zahl wird mit Hochkommas als Tausendertrennzeichen dargestellt
        )

    st.markdown("---") #Erstellt eine horizontale Trennlinie in Streamlit

    # Chart 1: Donut
    st.markdown("### Zusammensetzung des Preises")
    st.caption("Prozentualer Einfluss der einzelnen Merkmale auf den Endpreis.")
    fig_donut = erstelle_donut_chart(e["faktoren"])
    st.plotly_chart(fig_donut, width="stretch")

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
    karte = erstelle_heatmap_karte(ausgewaehltes_quartier=e["quartier"], quartier_koordinaten=QUARTIER_KOORDINATEN, basispreis_pro_quartier=BASISPREIS_PRO_QUARTIER)
    st_folium(karte, use_container_width=True, height=450)