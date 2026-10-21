import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import os
from datetime import datetime

st.set_page_config(page_title="Cardoso Bet Control", page_icon="⚽", layout="wide")

DB_FILE = "apostas.csv"

# Dados das suas 8 apostas dos prints
DADOS_INICIAIS = [
    {"ID": 1, "Data": "2026-10-17", "Tipo": "Múltipla (4)", "Descricao": "Man City, PSG, Barça, Bayern", "Odd": 2.84, "Valor": 5.00, "Resultado": "GREEN", "Ganhos": 14.20, "Lucro": 9.20},
    {"ID": 2, "Data": "2026-10-17", "Tipo": "Múltipla (4)", "Descricao": "Botafogo, Galo, Over 1.5, Over 1.5", "Odd": 3.34, "Valor": 4.20, "Resultado": "RED", "Ganhos": 0.00, "Lucro": -4.20},
    {"ID": 3, "Data": "2026-10-18", "Tipo": "Múltipla (3)", "Descricao": "1X Man Utd, Over 2.5 (BRIxCRY), 1X Bournemouth", "Odd": 2.53, "Valor": 5.00, "Resultado": "GREEN", "Ganhos": 12.65, "Lucro": 7.65},
    {"ID": 4, "Data": "2026-10-18", "Tipo": "Simples", "Descricao": "Real Madrid marca em ambos tempos", "Odd": 2.30, "Valor": 5.00, "Resultado": "GREEN", "Ganhos": 11.50, "Lucro": 6.50},
    {"ID": 5, "Data": "2026-10-18", "Tipo": "Múltipla (5)", "Descricao": "Arsenal, 2X Cruzeiro, Real, 2X Fla, Timão", "Odd": 5.43, "Valor": 5.00, "Resultado": "RED", "Ganhos": 0.00, "Lucro": -5.00},
    {"ID": 6, "Data": "2026-10-20", "Tipo": "Múltipla (2)", "Descricao": "1X PSG, X2 Atl. Madrid", "Odd": 2.05, "Valor": 5.00, "Resultado": "GREEN", "Ganhos": 10.25, "Lucro": 5.25},
    {"ID": 7, "Data": "2026-10-20", "Tipo": "Múltipla (3)", "Descricao": "Man City (1ºT), Liverpool, Nápoles", "Odd": 3.37, "Valor": 5.00, "Resultado": "GREEN", "Ganhos": 16.85, "Lucro": 11.85},
    {"ID": 8, "Data": "2026-10-20", "Tipo": "Múltipla (4)", "Descricao": "Fenerbahce, City (1ºT), Liverpool, 1X Nápoles", "Odd": 3.70, "Valor": 5.00, "Resultado": "RED", "Ganhos": 0.00, "Lucro": -5.00},
]

def carregar_dados():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Data'] = pd.to_datetime(df['Data'])
        return df
    else:
        df = pd.DataFrame(DADOS_INICIAIS)
        df['Data'] = pd.to_datetime(df['Data'])
        df.to_csv(DB_FILE, index=False)
        return df

def salvar_aposta(nova_aposta):
    df = carregar_dados()
    nova_aposta['ID'] = len(df) + 1
    df = pd.concat([df, pd.DataFrame([nova_aposta])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

df_apostas = carregar_dados()

st.sidebar.title("⚽ Cardoso Bet Control")
menu = st.sidebar.radio("Menu", ["📊 Dashboard", "📸 Importar Print", "📜 Histórico de Apostas"])

if menu == "📊 Dashboard":
    st.title("📈 Cardoso Bet Control - Dashboard")
    
    if not df_apostas.empty:
        total_apostado = df_apostas["Valor"].sum()
        lucro_total = df_apostas["Lucro"].sum()
        roi = (lucro_total / total_apostado * 100) if total_apostado > 0 else 0
        greens = len(df_apostas[df_apostas["Resultado"] == "GREEN"])
        total_bets = len(df_apostas)
        taxa_acerto = (greens / total_bets * 100) if total_bets > 0 else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Apostado", f"{total_apostado:.2f} €")
        c2.metric("Lucro Líquido", f"{lucro_total:.2f} €", delta=f"{lucro_total:.2f} €")
        c3.metric("ROI (%)", f"{roi:.1f}%")
        c4.metric("Taxa de Green", f"{taxa_acerto:.1f}% ({greens}/{total_bets})")

        st.divider()

        df_sorted = df_apostas.sort_values("Data")
        df_sorted["Lucro_Acumulado"] = df_sorted["Lucro"].cumsum()

        fig = px.line(
            df_sorted, 
            x="Data", 
            y="Lucro_Acumulado", 
            title="Evolução do Lucro (€)",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

elif menu == "📸 Importar Print":
    st.title("📸 Registrar Nova Aposta por Print")
    uploaded_file = st.file_uploader("Selecione o print da aposta", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.image(Image.open(uploaded_file), width=300)
        
        with st.form("form_aposta"):
            col1, col2 = st.columns(2)
            with col1:
                data_aposta = st.date_input("Data", datetime.now())
                tipo = st.selectbox("Tipo", ["Simples", "Múltipla (2)", "Múltipla (3)", "Múltipla (4)", "Múltipla (5+)"])
                descricao = st.text_input("Descrição / Jogos", value="")
            with col2:
                odd = st.number_input("Odd Total", min_value=1.01, value=2.00, step=0.05)
                valor = st.number_input("Montante (€)", min_value=0.5, value=5.0, step=0.5)
                resultado = st.selectbox("Resultado", ["GREEN", "RED", "PENDENTE"])

            if st.form_submit_button("💾 Salvar Aposta"):
                ganhos = (valor * odd) if resultado == "GREEN" else (0.0 if resultado == "RED" else valor)
                lucro = (ganhos - valor) if resultado != "PENDENTE" else 0.0

                salvar_aposta({
                    "Data": data_aposta.strftime("%Y-%m-%d"),
                    "Tipo": tipo,
                    "Descricao": descricao,
                    "Odd": odd,
                    "Valor": valor,
                    "Resultado": resultado,
                    "Ganhos": ganhos,
                    "Lucro": lucro
                })
                st.success("✅ Aposta salva no Cardoso Bet Control!")

elif menu == "📜 Histórico de Apostas":
    st.title("📜 Histórico Completo de Apostas")
    st.dataframe(df_apostas, use_container_width=True)
