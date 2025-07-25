import streamlit as st
import pandas as pd
import re
from datetime import datetime
from io import StringIO

st.set_page_config(page_title="Suivi des Entraînements", layout="wide")
st.title("📊 Super Structure | Suivi des Entraînements")

st.markdown("""
Ce tableau de bord vous permet de suivre automatiquement les entraînements de la team via les exports WhatsApp.
- Uploadez le fichier `.txt` d'export WhatsApp
- Les stats se mettront à jour automatiquement
""")

uploaded_file = st.file_uploader("📁 Uploader le fichier .txt de l'export WhatsApp", type=["txt"])

def parse_whatsapp_chat(chat_text):
    pattern = r"\[(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2})\] (.*?): (.*)"
    messages = []
    lines = chat_text.splitlines()
    for line in lines:
        match = re.match(pattern, line)
        if match:
            date_str, time_str, author, message = match.groups()
            try:
                dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
            except:
                continue
            # Entraînement détecté si présence d'émojis sportifs ou mots-clés
            if re.search(r"\ud83c\udfcb|\ud83d\udcaa|\ud83c\udfc3|\ud83c\udfca|\ud83c\udfcb|sport|entrainement|run|muscu", message, re.IGNORECASE):
                messages.append({
                    "date": dt.date(),
                    "heure": dt.time(),
                    "membre": author,
                    "message": message
                })
    return pd.DataFrame(messages)

if uploaded_file:
    chat_text = uploaded_file.read().decode("utf-8")
    df = parse_whatsapp_chat(chat_text)

    if df.empty:
        st.warning("Aucun pointage détecté dans le fichier.")
    else:
        st.success(f"✅ {len(df)} entraînements détectés !")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("📆 Total Séances", len(df))
            st.metric("👥 Membres actifs", df['membre'].nunique())
        with col2:
            st.metric("📈 Dernière activité", str(df['date'].max()))
            st.metric("📉 Première activité", str(df['date'].min()))

        st.markdown("### 🔝 Nombre de séances par membre")
        st.bar_chart(df['membre'].value_counts())

        st.markdown("### 📅 Activité par semaine")
        df["semaine"] = pd.to_datetime(df["date"]).dt.to_period("W").astype(str)
        st.line_chart(df.groupby(["semaine", "membre"]).size().unstack(fill_value=0))

        st.markdown("### 📋 Détail des séances")
        st.dataframe(df)
else:
    st.info("Veuillez uploader un fichier .txt exporté depuis WhatsApp.")
