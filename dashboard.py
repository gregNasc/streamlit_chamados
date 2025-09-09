import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from chamados import listar_chamados

# Exportar para Excel
def exportar_chamados_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='chamados')
    output.seek(0)
    return output.getvalue()

# Gráfico pizza
def plotar_pizza(df, coluna, titulo=None):
    fig, ax = plt.subplots(figsize=(4, 4))
    df[coluna].value_counts().plot(
        kind="pie", autopct='%1.1f%%', startangle=25, ax=ax, colors=plt.cm.Paired.colors
    )
    ax.set_ylabel('')
    if titulo:
        ax.set_title(titulo)
    fig.tight_layout()
    return fig

# Gráfico barra
def plotar_barra(df, coluna, titulo=None):
    fig, ax = plt.subplots(figsize=(5, 4))
    df_count = df[coluna].value_counts()
    cores = ['red' if valor >= 5 else 'green' for valor in df_count.values]
    df_count.sort_index().plot(kind="bar", ax=ax, color=cores)
    ax.set_ylabel("Qtd")
    ax.set_xlabel("")
    ax.bar_label(ax.containers[0])
    if titulo:
        ax.set_title(titulo)
    fig.tight_layout()
    return fig

# Aplicar filtros
def aplicar_filtros(df, colunas_filtro):
    df_filtrado = df.copy()
    for col in colunas_filtro:
        valores = st.sidebar.multiselect(
            col.capitalize(), df[col].dropna().unique(),
            placeholder=f"Selecione {col.capitalize()}"
        )
        if valores:
            df_filtrado = df_filtrado[df_filtrado[col].isin(valores)]
    return df_filtrado

# Dashboard Admin
def dashboard_admin():
    st.title("📊 Dashboard de Chamados - Admin")
    df = listar_chamados(filtro="Todos")
    if df.empty:
        st.warning("Nenhum chamado encontrado no banco de dados.")
        return

    # Aplicar filtros
    colunas_filtro = ["regional", "status", "motivo", "lider"]
    df_filtrado = aplicar_filtros(df, colunas_filtro)

    # Layout 2x2 para gráficos
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        st.subheader("📌 Status")
        st.pyplot(plotar_pizza(df_filtrado, "status"))

    with col2:
        st.subheader("📊 Chamados por Regional")
        st.pyplot(plotar_barra(df_filtrado, "regional", titulo="Chamados por Regional"))

    with col3:
        st.subheader("⚙️ Principais Motivos")
        st.pyplot(plotar_barra(df_filtrado, "motivo", titulo="Principais Motivos"))

    with col4:
        st.subheader("👔 Principais Líderes")
        st.pyplot(plotar_barra(df_filtrado, "lider", titulo="Principais Líderes"))

    # Botão de exportação
    if not df_filtrado.empty:
        excel_data = exportar_chamados_para_excel(df_filtrado)
        st.download_button(
            label="📥 Exportar Chamados para Excel",
            data=excel_data,
            file_name="chamados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Dashboard Usuário
def dashboard_usuario():
    st.title("📊 Status dos Chamados")
    df = listar_chamados(filtro="Todos")
    if df.empty:
        st.warning("Nenhum chamado encontrado no banco de dados.")
        return

    df_filtrado = aplicar_filtros(df, ["status"])

    st.subheader("📌 Status dos Chamados")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.pyplot(plotar_pizza(df_filtrado, "status"))
