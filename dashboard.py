import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

def carregar_dados():
    conn = sqlite3.connect("chamados.db")
    df = pd.read_sql_query("SELECT * FROM chamados", conn)
    conn.close()
    return df

def dashboard():
    st.title("📊 Dashboard de Chamados")
    df = carregar_dados()
    if df.empty:
        st.warning("Nenhum chamado encontrado no banco de dados.")
        return

    # Filtros
    st.header("Filtros")
    regional = st.sidebar.multiselect("Regional", df["regional"].dropna().unique(), placeholder="Selecione uma Regional")
    status = st.sidebar.multiselect("Status", df["status"].dropna().unique(), placeholder="Selecione um Status")
    motivo = st.sidebar.multiselect("Motivo", df["motivo"].dropna().unique(), placeholder="Selecione um Motivo")

    df_filtrado = df.copy()
    if regional:
        df_filtrado = df_filtrado[df_filtrado["regional"].isin(regional)]
    if status:
        df_filtrado = df_filtrado[df_filtrado["status"].isin(status)]
    if motivo:
        df_filtrado = df_filtrado[df_filtrado["motivo"].isin(motivo)]

    # Colunas para exibir gráficos lado a lado
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📌 Status")
        fig_status, ax_status = plt.subplots(figsize=(4, 4))
        df_filtrado["status"].value_counts().plot(kind="pie", autopct='%1.1f%%', startangle=25, ax=ax_status, colors=plt.cm.Paired.colors
        )
        ax_status.set_ylabel('')
        st.pyplot(fig_status)

    with col2:
        st.subheader("📊 Chamados por Regional")
        fig_reg_bar, ax_reg_bar = plt.subplots(figsize=(5, 4))
        df_count = df_filtrado["regional"].value_counts()
        df_count.sort_index().plot(kind="bar", ax=ax_reg_bar, color='red')
        ax_reg_bar.set_ylabel("Qtd")
        ax_reg_bar.set_xlabel("")
        ax_reg_bar.bar_label(ax_reg_bar.containers[0])
        st.pyplot(fig_reg_bar)

    with col3:

        st.subheader("⚙️ Principais Motivos de Chamados")
        fig_reg_bar, ax_reg_bar = plt.subplots(figsize=(5, 4))
        df_count = df_filtrado["motivo"].value_counts()
        df_count.sort_index().plot(kind="bar", ax=ax_reg_bar, color='blue')
        ax_reg_bar.set_ylabel("Qtd")
        ax_reg_bar.set_xlabel("")
        ax_reg_bar.bar_label(ax_reg_bar.containers[0])
        st.pyplot(fig_reg_bar)
    # Linha abaixo para ocupar a tela inteira


