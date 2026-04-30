# laedt das CSV Format des Datensets, umbennen der Spalten des Datensets --> erleichtert die Arbeit mit dem Set
import pandas as pd #Werkzeugpaket fuer Tabellen-Daten
import sqlite3 #dadurch kann man eine lokale Datenbank-datei erstellen
import os #um zu pruefen ob eine Datei bereits existiert --> noch nicht ganz verstanden


CSV_URL = "https://data.stadt-zuerich.ch/dataset/bau_hae_preis_stockwerkeigentum_zimmerzahl_stadtquartier_od5155/download/BAU515OD5155.csv" 
#Diese Variable speichert den Link zu unserem Datenset
DB_PATH = "immobilien.db" #erster durchlauf: ins internet, CSV laden und in immobilien.db speichern
#zweiter Durchlauf: immobilien.db wird direkt gelesen
#immobilien.db = Dateiname unserer lokalen Datenbank
#erstellt beim ersten Durchlauf des codes die datei automatisch --> speichert Daten aus dem CSV
#Ohne unsere Datenbank muesste die App jedes Mal das CSV neu vom Internet laden
# --> so wird es gespeichert
#Das ist die Idee von dem code in diesem feature, siehe Funktion 4:  get_daten()


#Funktion 1#:
def daten_laden(): #Definition der Funktion daten_laden
    df=pd.read_csv(CSV_URL) 
    #unsere CSV Datei wird vom link geladen und in einen Dataframe (tabelle) verwandelt. 
    #diese Tabelle wird in df (fuer Dataframe) gespeichert

    
    print(list(df.columns))  # ← NEU: zeigt die echten Spaltennamen im Log

    df = df.rename(columns={
        "Stichtagdatjahr":     "Jahr",
        "RaumLang":            "Quartier",
        "AnzZimmerLevel2Lang_noDM":  "Zimmer",
        "HAPreisWohnflaeche":  "Preis_pro_m2",
        "HAMedianPreis":       "Medianpreis",
        "AnzHA":               "Anzahl_Verkaeufe"
    })
    #Benennt die Spaltennamen vom CSV um --> einfacher fuer uns um unseren code zu lesen
    #Vorschlag von Claude - koennen wir auch noch aendern

    spalten= ["Jahr", "Quartier", "Zimmer", "Preis_pro_m2", "Medianpreis", "Anzahl_Verkaeufe"]
    df=df[spalten]
    #Fokus nur auf fuer uns relevante Spalten, die anderen von unserem Datenset werden so aussortiert (koennen wir gerne auch noch anpassen)
    #So werden nur diese Spalten in unserem DataFrame uebernommen

    #!!!Unsicherheit:Wollen/muessen wir hier noch weitere bearbeitungen unseres df integrieren? Wie z.b fehlende Werte aussortieren?

    df["Jahr"]=df["Jahr"].astype(int)
    df["Preis_pro_m2"] = df["Preis_pro_m2"].astype(float)
    df["Medianpreis"] = df["Medianpreis"].astype(float)
    #Anpassung gewisser Datentypen, weil CSV anscheinend oft alles als String laden
    #Anpassung noetig fuer die Rechnungen

    speichere_in_datenbank(df)
    return(df)

    #ruft Funktion 2 auf und speichert so die Daten, return gibt den fertigen df zurueck
    #so muesste man eine saubere Tabelle zurueck bekommen


 #Funktion 2: 
def speichere_in_datenbank(df): #Defintion der neuen Funktion, df als Parameter
    conn = sqlite3.connect(DB_PATH)
    #conn = connection --> oeffnet eine Verbindung zur Datenbankdatei immobilien.db
    df.to_sql("immobilienpreise", conn, if_exists="replace", index=False)
    #Schreibt kompletten DataFrame als Tabelle in die Datenbank. 
    #"immobilienpreise" ist der name dieser Tabelle
    #if_exits="replace" bedeutt: Falls die tabelle schon existiert, ueberschrieben
    #index=false verhindert dass panda eine unnoetige Nummerierungsspalte mitspeichert
    conn.close()
    #schliesst die Verbinsung zur Datenbank --> wichtig falls mehrere Teile darauf zugreifen wollen

#Funktion 3: 
def lade_aus_datenbank(): #liest die Daten aus der lokalen Datenbank --> so muss CVS nicht immer neu vom Internet geladen werden
    conn = sqlite3.connect(DB_PATH)
    #oeffnet verbindung zur Datenbank
    df = pd.read_sql("SELECT * FROM immobilienpreise", conn)
    #SQL-Abfrage --> verwandelt das Ergebnis direkt in einen DataFrame
    conn.close()
    #Verbindung schliessen
    return df


#Funktion 4: #Hauptfunktion --> muss in app.py integriert werden
def get_daten():
    if os.path.exists(DB_PATH):
        return lade_aus_datenbank()
    else:
        return daten_laden()
    # os.path.exists(DB_PATH) gibt True zurueck wenn die Datei immobilien.db bereits existiert, 
    #sonst False. Die Logik: beim allerersten Start existiert die Datenbank noch nicht
    #--> wir laden das CSV und speichern es. Ab dem zweiten Start existiert die Datei 
    #--> wir lesen einfach lokal. So wird das Internet nur einmal verwendet.