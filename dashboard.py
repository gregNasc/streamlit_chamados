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

def plotar_barra(df, coluna, titulo=None, figsize=(8,5), top_n=10, ordenar_por_valor=True):
    fig, ax = plt.subplots(figsize=figsize)
    df_count = df[coluna].value_counts().head(top_n)
    if ordenar_por_valor:
        df_count = df_count.sort_values()
    else:
        df_count = df_count.sort_index()
    valores = pd.to_numeric(df_count.values)
    cores = ['green' if v <= 5 else 'red' for v in valores]
    df_count.plot(kind="bar", ax=ax, color=cores)
    ax.set_ylabel("Qtd")
    ax.set_xlabel("")
    ax.bar_label(ax.containers[0])
    if titulo:
        ax.set_title(titulo)
    fig.tight_layout()
    return fig


def plotar_tempo_medio(df, titulo="Tempo Médio por Motivo"):
    # Verifica se as colunas existem
    if 'abertura' not in df.columns or 'fechamento' not in df.columns:
        st.warning(
            "As colunas 'abertura' e/ou 'fechamento' não foram encontradas. Gráfico de tempo médio não será exibido.")
        return None

    # Considera apenas chamados finalizados
    df_finalizados = df[df['fechamento'].notna()].copy()

    if df_finalizados.empty:
        st.info("Nenhum chamado finalizado encontrado para calcular o tempo médio.")
        return None

    # Converter para datetime
    df_finalizados['abertura'] = pd.to_datetime(df_finalizados['abertura'])
    df_finalizados['fechamento'] = pd.to_datetime(df_finalizados['fechamento'])

    # Calcular tempo em minutos
    df_finalizados['tempo_minutos'] = (df_finalizados['fechamento'] - df_finalizados[
        'abertura']).dt.total_seconds() / 60

    # Média por motivo
    media_por_motivo = df_finalizados.groupby('motivo')['tempo_minutos'].mean().sort_values(ascending=False)

    # Seleciona apenas os 10 maiores
    media_por_motivo = media_por_motivo.head(10)

    # Criar gráfico menor
    fig, ax = plt.subplots(figsize=(20, 4))
    barras = ax.barh(media_por_motivo.index, media_por_motivo.values, color='black')

    # Adiciona labels no final de cada barra em horas e minutos
    labels = []
    for tempo_min in media_por_motivo.values:
        horas = int(tempo_min // 60)
        minutos = int(tempo_min % 60)
        labels.append(f"{horas}h {minutos}m")

    ax.bar_label(barras, labels=labels, label_type='edge')  # exibe horas e minutos no final da barra
    ax.set_xlabel("Tempo médio em Minutos")
    ax.set_ylabel("Motivo")
    ax.invert_yaxis()
    fig.tight_layout()

    return fig


# Função de filtros
def aplicar_filtros(df, colunas_filtro):
    df_filtrado = df.copy()
    for col in colunas_filtro:
        if col in df.columns:
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

    # Layout 2x2
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        st.subheader("📌 Status")
        st.pyplot(plotar_pizza(df_filtrado, "status"))

    with col2:
        st.subheader("👔 Principais Líderes")
        st.pyplot(plotar_barra(df_filtrado, "lider", titulo="Principais Líderes", figsize=(8,6)))

    with col3:
        st.subheader("⚙️ Principais Motivos")
        st.pyplot(plotar_barra(df_filtrado, "motivo", titulo="Principais Motivos", figsize=(8,6)))

    with col4:
        st.subheader("📊 Chamados por Regional")
        st.pyplot(plotar_barra(df_filtrado, "regional", titulo="Chamados por Regional", figsize=(8,6)))

    # Gráfico de tempo médio por motivo
    with st.expander("⏱ Tempo Médio de Suporte"):
        fig = plotar_tempo_medio(df_filtrado)
        if fig:
            st.pyplot(fig)

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
        st.pyplot(plotar_pizza(df_filtrado, "status"))
