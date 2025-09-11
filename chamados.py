import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from database import cadastrar_chamado as db_cadastrar_chamado, finalizar_chamado as db_finalizar_chamado, ler_chamados

EXCEL_PATH = "chamado.xlsx"

# ---------------------------
# Carregar dados Excel
# ---------------------------
@st.cache_data
def carregar_dados_excel():
    try:
        df = pd.read_excel(EXCEL_PATH, header=1)
        df.columns = [str(c).strip().upper() for c in df.columns]
        for col in ["8", "1", "12"]:
            if col in df.columns:
                df[col] = df[col].astype(str)
        if "4" in df.columns:
            df["4"] = pd.to_datetime(df["4"], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame()

dados = carregar_dados_excel()

# ---------------------------
# Funções auxiliares
# ---------------------------
def listar_chamados(filtro="Chamados Abertos", inicio=None, fim=None):
    df = ler_chamados()
    if df.empty:
        return df
    if filtro == "Chamados Abertos":
        df = df[df["status"] == "Aberto"]
    elif filtro == "Chamados Finalizados":
        df = df[df["status"] == "Finalizado"]
    if inicio and fim:
        df["abertura"] = pd.to_datetime(df["abertura"], errors="coerce")
        df = df[df["abertura"].dt.date.between(inicio, fim)]
    return df

def exportar_chamados_para_excel(df):
    df_export = df.copy()
    for col in ["abertura", "fechamento"]:
        if col in df_export.columns:
            df_export[col] = pd.to_datetime(df_export[col], errors="coerce").dt.tz_localize(None)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_export.to_excel(writer, index=False, sheet_name="chamados")
    output.seek(0)
    return output.getvalue()

# ---------------------------
# Interface principal
# ---------------------------
def sistema_chamados(usuario_logado):
    st.title(f"📌 Sistema de Chamados - Usuário: {usuario_logado}")
    st.sidebar.header("Filtros")

    filtro_status = st.sidebar.selectbox("Filtrar Chamados", ["Chamados Abertos", "Chamados Finalizados"])
    data_inicio = st.sidebar.date_input("Data Início", value=datetime.today())
    data_fim = st.sidebar.date_input("Data Fim", value=datetime.today())

    regionais_disponiveis = []
    if "4" in dados.columns and "8" in dados.columns:
        mask = dados["4"].dt.date.between(data_inicio, data_fim)
        regionais_disponiveis = dados[mask]["8"].str.strip().unique().tolist()
    regional = st.selectbox("Regional", ["Selecione uma Regional"] + regionais_disponiveis)

    lojas_disponiveis = []
    if regional not in ["Selecione uma Regional"] and "1" in dados.columns and "8" in dados.columns:
        mask = (dados["8"].str.strip() == regional) & (dados["4"].dt.date.between(data_inicio, data_fim))
        lojas_disponiveis = dados[mask]["1"].str.strip().unique().tolist()
    loja = st.selectbox("Loja", ["Selecione uma Loja"] + lojas_disponiveis)

    lider = ""
    if loja not in ["Selecione uma Loja"] and {"8", "1", "12", "4"}.issubset(dados.columns):
        mask = (dados["8"].str.strip() == regional) & (dados["1"].str.strip() == loja) & (dados["4"].dt.date.between(data_inicio, data_fim))
        filtro = dados[mask]
        if not filtro.empty:
            lider = filtro["12"].iloc[0]
    lider_editado = st.text_input("Líder", value=lider)

    motivos = ["Selecione um Motivo","Falha Impressão","Impressora Queimada","Router não funciona","Notebook não liga","Coletor não conecta","Outro"]
    motivo = st.selectbox("Motivo do Suporte", motivos)
    outro_motivo = st.text_input("Digite o motivo do suporte:") if motivo=="Outro" else ""

    if st.button("Cadastrar Chamado"):
        motivo_final = outro_motivo if motivo=="Outro" else motivo
        if regional=="Selecione uma Regional" or loja=="Selecione uma Loja" or lider_editado.strip()=="" or motivo_final.strip()=="":
            st.warning("⚠️ Todos os campos devem ser preenchidos!")
        else:
            db_cadastrar_chamado(regional, loja, lider_editado, motivo_final)

    st.subheader("📋 Chamados")
    df_chamados = listar_chamados(filtro_status, data_inicio, data_fim)

    if not df_chamados.empty:
        for _, row in df_chamados.iterrows():
            col1,col2,col3,col4,col5,col6,col7 = st.columns([1,2,2,2,2,1,1])
            col1.write(row["id"])
            col2.write(row["regional"])
            col3.write(row["loja"])
            col4.write(row["lider"])
            col5.write(row["motivo"])
            col6.write(row["status"])
            if row["status"]=="Aberto":
                if col7.button("Finalizar", key=f"finalizar_{row['id']}"):
                    db_finalizar_chamado(row["id"])
                    st.rerun()
    else:
        st.info("ℹ️ Nenhum chamado encontrado.")

    if not df_chamados.empty:
        st.download_button(
            label="📥 Exportar Chamados para Excel",
            data=exportar_chamados_para_excel(df_chamados),
            file_name="chamados_exportados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    if st.button("🚪 Sair"):
        st.session_state.clear()
        st.stop()
