import streamlit as st
import matplotlib.pyplot as plt
from chamados import listar_chamados  # função para carregar dados do DB

# Dashboard
def dashboard():
    st.title("📊 Dashboard de Chamados")

    # Carrega todos os chamados
    df = listar_chamados(filtro="Todos")
    if df.empty:
        st.warning("Nenhum chamado encontrado no banco de dados.")
        return

    # Filtros
    st.sidebar.header("Filtros")
    regional = st.sidebar.multiselect("Regional", df["regional"].dropna().unique(), placeholder="Selecione uma Regional")
    status = st.sidebar.multiselect("Status", df["status"].dropna().unique(), placeholder="Selecione um Status")
    motivo = st.sidebar.multiselect("Motivo", df["motivo"].dropna().unique(), placeholder="Selecione um Motivo")

    # Filtra dados
    df_filtrado = df.copy()
    if regional:
        df_filtrado = df_filtrado[df_filtrado["regional"].isin(regional)]
    if status:
        df_filtrado = df_filtrado[df_filtrado["status"].isin(status)]
    if motivo:
        df_filtrado = df_filtrado[df_filtrado["motivo"].isin(motivo)]

    # Gráficos lado a lado
    col1, col2, col3 = st.columns(3)

    # Status (Pizza)
    with col1:
        st.subheader("📌 Status")
        fig_status, ax_status = plt.subplots(figsize=(4, 4))
        df_filtrado["status"].value_counts().plot(
            kind="pie", autopct='%1.1f%%', startangle=25, ax=ax_status, colors=plt.cm.Paired.colors
        )
        ax_status.set_ylabel('')
        st.pyplot(fig_status)

    # Chamados por Regional (Barra)
    with col2:
        st.subheader("📊 Chamados por Regional")
        fig_reg, ax_reg = plt.subplots(figsize=(5, 4))
        df_count = df_filtrado["regional"].value_counts()
        df_count.sort_index().plot(kind="bar", ax=ax_reg, color='red')
        ax_reg.set_ylabel("Qtd")
        ax_reg.set_xlabel("")
        ax_reg.bar_label(ax_reg.containers[0])
        st.pyplot(fig_reg)

    # Principais Motivos (Barra)
    with col3:
        st.subheader("⚙️ Principais Motivos")
        fig_motivo, ax_motivo = plt.subplots(figsize=(5, 4))
        df_count = df_filtrado["motivo"].value_counts()
        df_count.sort_index().plot(kind="bar", ax=ax_motivo, color='blue')
        ax_motivo.set_ylabel("Qtd")
        ax_motivo.set_xlabel("")
        ax_motivo.bar_label(ax_motivo.containers[0])
        st.pyplot(fig_motivo)
