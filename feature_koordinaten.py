# Mittelpunkt-Koordinaten der Züricher Quartiere
# Quelle: Stadt Zuerich Geodaten (statische Referenzdaten)
#Wir benutzen hardcodierte Daten weil der CSV link nicht funktioniert da die Stadt Zuerich hoechstwahrscheinlich den Zugriff blockiert hat
#Wir haben probiert die Daten herunterzuladen und manuell abzuspeichern, aber die Daten haben keine Lat/Lon Spalten sondern nur geometry mit POLYGON Koordinaten 

def get_koordinaten():
    return {
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