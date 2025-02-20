import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import os

def berechne_nullstellen_mit_schritten(funktion, variable='x'):
    x = sp.symbols(variable)
    schritte = []
    try:
        f = sp.sympify(funktion, evaluate=False)
        schritte.append(f"1. Gegebene Funktion: f(x) = {f}")
        
        # Umformen in Nullstellenform (falls nötig)
        schritte.append("2. Setze die Funktion gleich 0: f(x) = 0")

        # Berechnung der Nullstellen
        nullstellen = sp.solve(f, x)
        
        if nullstellen:
            schritte.append("3. Nullstellen bestimmen:")
            for idx, ns in enumerate(nullstellen):
                schritte.append(f"   Nullstelle {idx + 1}: x = {ns}")
        else:
            schritte.append("   Keine Nullstellen gefunden.")

        return {
            "Nullstellen": [str(n) for n in nullstellen],
            "Rechenweg": schritte
        }
    except sp.SympifyError:
        return {"Fehler": "Die Funktion konnte nicht interpretiert werden."}

def berechne_integral_mit_schritten(funktion, grenzen=None, variable='x'):
    x = sp.symbols(variable)
    schritte = []
    
    nullstellen_ergebnis = berechne_nullstellen_mit_schritten(funktion, variable)
    schritte.extend(nullstellen_ergebnis["Rechenweg"])

    try:
        f = sp.sympify(funktion, evaluate=False)
    except sp.SympifyError:
        return {"Fehler": "Die Funktion konnte nicht interpretiert werden."}
    
    schritte.append("4. Bestimmung der Stammfunktion:")
    stammfunktion = sp.integrate(f, x)
    schritte.append(f"   ∫ f(x) dx = {stammfunktion} + C")
    
    bestimmtes_integral = None
    if grenzen and len(grenzen) > 1:
        schritte.append("5. Berechnung des bestimmten Integrals durch Einsetzen der Grenzen:")
        integrale = []
        for i in range(len(grenzen)-1):
            untere_grenze = grenzen[i]
            obere_grenze = grenzen[i+1]
            obere_auswertung = stammfunktion.subs(x, obere_grenze)
            untere_auswertung = stammfunktion.subs(x, untere_grenze)
            teil_integral = obere_auswertung - untere_auswertung
            
            schritte.append(f"   Intervall: [{untere_grenze}, {obere_grenze}] → F({obere_grenze}) - F({untere_grenze}) = {teil_integral}")
            integrale.append(teil_integral)
        
        bestimmtes_integral = sum(integrale)
        schritte.append(f"   Gesamtfläche: {bestimmtes_integral}")
    
    return {
        "Nullstellen": nullstellen_ergebnis["Nullstellen"],
        "Funktion": str(f),
        "Unbestimmtes Integral": str(stammfunktion) + " + C",
        "Bestimmtes Integral": str(bestimmtes_integral) if bestimmtes_integral is not None else "Nicht angegeben",
        "Rechenweg": schritte
    }

def plot_funktion_mit_flaeche(funktion, grenzen):
    x_vals = np.linspace(float(min(grenzen)) - 1, float(max(grenzen)) + 1, 400)
    x = sp.symbols('x')
    try:
        f_lambdified = sp.lambdify(x, sp.sympify(funktion, evaluate=False), 'numpy')
        y_vals = f_lambdified(x_vals)
        
        fig, ax = plt.subplots()
        ax.plot(x_vals, y_vals, label=f'f(x) = {funktion}')
        for i in range(len(grenzen)-1):
            ax.fill_between(x_vals, y_vals, where=(x_vals >= float(grenzen[i])) & (x_vals <= float(grenzen[i+1])), alpha=0.3, color='red')
        ax.axhline(0, color='black', linewidth=0.5)
        ax.axvline(0, color='black', linewidth=0.5)
        ax.legend()
        ax.set_title("Grafische Darstellung der Funktion und Flächenberechnung")
        return fig
    except Exception as e:
        st.error(f"Fehler beim Plotten: {e}")
        return None

def oeffne_verzeichnis(unterverzeichnis):
    verzeichnis = f"./Dokumente/{unterverzeichnis}"
    if not os.path.exists(verzeichnis):
        os.makedirs(verzeichnis)
    return verzeichnis

# Streamlit App
st.sidebar.title("Navigation")

# Erstelle ein aufklappbares Menü für "Analysis"
analysis_menu = st.sidebar.expander("📊 Analysis", expanded=True)
menu = analysis_menu.radio(
    "Wähle eine Kategorie:",
    ["Integrale", "Differentialrechnung", "Lineare Algebra"],
    index=0
)

if menu == "Integrale":
    unterverzeichnis = "Integrale"
    st.title("Integralrechner mit Rechenweg")
    funktion_input = st.text_input("Funktion eingeben (z. B. x**2, sin(x), e**x):", "x**2")
    grenzen_input = st.text_input("Grenzen (Kommagetrennt, z. B. -1, 0, 2):")
    grenzen = [sp.sympify(g.strip()) for g in grenzen_input.split(',')] if grenzen_input else None

    if st.button("Integral berechnen"):
        ergebnis = berechne_integral_mit_schritten(funktion_input, grenzen=grenzen)
        for schritt in ergebnis["Rechenweg"]:
            st.write(schritt)

        if grenzen:
            fig = plot_funktion_mit_flaeche(funktion_input, grenzen)
            if fig:
                st.pyplot(fig)

elif menu == "Differentialrechnung":
    unterverzeichnis = "Differentialrechnung"
    st.title("Differentialrechnung")
    funktion_input = st.text_input("Funktion eingeben:", "x**2")
    x = sp.symbols('x')
    if st.button("Ableitung berechnen"):
        f = sp.sympify(funktion_input, evaluate=False)
        ableitung = sp.diff(f, x)
        st.write(f"**Erste Ableitung:** {ableitung}")

elif menu == "Lineare Algebra":
    unterverzeichnis = "Lineare Algebra"
    st.title("Lineare Algebra")
    st.write("Matrix-Operationen kommen hierhin.")

# Dokumentenverwaltung
st.sidebar.subheader(f"📁 Dokumentenverwaltung ({unterverzeichnis})")
verzeichnis = oeffne_verzeichnis(unterverzeichnis)
dateien = os.listdir(verzeichnis) if os.path.exists(verzeichnis) else []

# Upload-Funktion
uploaded_file = st.sidebar.file_uploader("Datei hochladen", type=["pdf", "docx", "xlsx", "txt", "pptx"])
if uploaded_file:
    save_path = os.path.join(verzeichnis, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success(f"Datei {uploaded_file.name} hochgeladen!")

# Anzeige der vorhandenen Dokumente mit Download-Möglichkeit
if dateien:
    st.sidebar.write("### Gespeicherte Dokumente:")
    for datei in dateien:
        dateipfad = os.path.join(verzeichnis, datei)
        with open(dateipfad, "rb") as f:
            st.sidebar.download_button(label=f"📥 {datei}", data=f, file_name=datei)
else:
    st.sidebar.write("Keine Dokumente vorhanden.")
