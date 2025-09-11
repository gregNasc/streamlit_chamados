import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from database import ler_chamados

# Exportar dados para Excel
def exportar_chamados_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='chamados')
    output.seek(0)
    return output.getvalue()

# Funções de gráficos
def plotar_pizza(df, coluna, titulo=None, figsize=(4,4)):
    fig, ax = plt.subplots(figsize=figsize)
    df[coluna].value_counts().plot(
        kind="pie", autopct='%1.1f%%', startangle=25, ax=ax, colors=plt.cm.Paired.colors
    )
    ax.set_ylabel('')
    if titulo:
        ax.set_title(titulo)
    fig.tight_layout()
    return fig

def plotar_barra(df, coluna, titulo=None, figsize=(5,4)):
    fig, ax = plt.subplots(figsize=figsize)

    # Conta valores
    df_count = df[coluna].value_counts()

    # Ordena os índices (categorias) e garante que os valores sejam numéricos
    df_count = df_count.sort_index()
    valores = pd.to_numeric(df_count.values)

    # Define cores com base nos valores corretos
    cores = ['green' if v <= 5 else 'red' for v in valores]

    # Plota gráfico de barras
    df_count.plot(kind="bar", ax=ax, color=cores)

    ax.set_ylabel("Qtd")
    ax.set_xlabel("")
    ax.bar_label(ax.containers[0])

    if titulo:
        ax.set_title(titulo)

    fig.tight_layout()
    return fig


# Filtros genéricos
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
    df = ler_chamados()
    if df.empty:
        st.warning("⚠️ Nenhum chamado encontrado no banco de dados.")
        return

    # Aplicar filtros
    colunas_filtro = ["regional", "status", "motivo", "lider"]
    df_filtrado = aplicar_filtros(df, colunas_filtro)

    # Layout 2x2 proporcional
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        st.subheader("📌 Status")
        st.pyplot(plotar_pizza(df_filtrado, "status", figsize=(4,4)))

    with col2:
        st.subheader("📊 Chamados por Regional")
        st.pyplot(plotar_barra(df_filtrado, "regional", titulo="Chamados por Regional", figsize=(5,4)))

    with col3:
        st.subheader("⚙️ Principais Motivos")
        st.pyplot(plotar_barra(df_filtrado, "motivo", titulo="Principais Motivos", figsize=(5,4)))

    with col4:
        st.subheader("👔 Principais Líderes")
        st.pyplot(plotar_barra(df_filtrado, "lider", titulo="Principais Líderes", figsize=(5,4)))

    # Exportar dados filtrados
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
    df = ler_chamados()
    if df.empty:
        st.warning("⚠️ Nenhum chamado encontrado no banco de dados.")
        return

    # Filtro apenas por status
    df_filtrado = aplicar_filtros(df, ["status"])

    st.subheader("📌 Status dos Chamados")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.pyplot(plotar_pizza(df_filtrado, "status", figsize=(4,4)))
