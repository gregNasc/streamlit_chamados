import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from io import BytesIO

DB_PATH = "chamados.db"
EXCEL_PATH = "chamado.xlsx"

# Carregar dados do Excel apenas para preencher Regional, Loja, Líder e Data
@st.cache_data
def carregar_dados_excel():
    dados_excel = pd.read_excel(EXCEL_PATH, header=1)
    dados_excel.columns = [str(c).strip().upper() for c in dados_excel.columns]
    for col in ["8", "1", "12"]:
        dados_excel[col] = dados_excel[col].astype(str)
    dados_excel["4"] = pd.to_datetime(dados_excel["4"], errors='coerce')
    return dados_excel

dados = carregar_dados_excel()


def listar_chamados(filtro="Aberto", inicio=None, fim=None):
    with sqlite3.connect(DB_PATH) as conn:
        query = "SELECT * FROM chamados"
        conditions = []
        if filtro == "Chamados Abertos":
            conditions.append("status='Aberto'")
        elif filtro == "Chamados Finalizados":
            conditions.append("status='Finalizado'")
        if inicio and fim:
            conditions.append(f"(DATE(abertura) BETWEEN '{inicio}' AND '{fim}')")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        df = pd.read_sql_query(query, conn)
    return df


def cadastrar_chamado(regional, loja, lider, motivo):
    abertura = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chamados (regional, loja, lider, motivo, abertura, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (regional, loja, lider, motivo, abertura, "Aberto"))
        conn.commit()
    st.success("Chamado cadastrado!")


def finalizar_chamado(chamado_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT abertura FROM chamados WHERE id = ?", (chamado_id,))
        row = cursor.fetchone()
        if row is None:
            st.error("Chamado não encontrado!")
            return
        abertura = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        fechamento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        duracao = str(datetime.now() - abertura).split('.')[0]

        cursor.execute("""
            UPDATE chamados
            SET fechamento=?, duracao=?, status=?
            WHERE id=?
        """, (fechamento, duracao, "Finalizado", chamado_id))
        conn.commit()
    st.success(f"Chamado {chamado_id} finalizado!")


def exportar_chamados_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='chamados')
    output.seek(0)
    return output.getvalue()


def sistema_chamados(usuario_logado):
    st.title(f"Sistema de Chamados - Usuário: {usuario_logado}")
    st.sidebar.header("Filtros")

    filtro_status = st.sidebar.selectbox("Filtrar Chamados", ["Chamados Abertos", "Chamados Finalizados"])
    data_inicio = st.sidebar.date_input("Data Início", value=datetime.today())
    data_fim = st.sidebar.date_input("Data Fim", value=datetime.today())

    # Regional
    regionais_disponiveis = dados[dados["4"].dt.date.between(data_inicio, data_fim)]["8"].str.strip().unique().tolist()
    regional = st.selectbox("Regional", ["Selecione uma Regional"] + regionais_disponiveis)

    # Loja
    if regional not in ["Selecione uma Regional"]:
        lojas_disponiveis = dados[(dados["8"].str.strip() == regional) &
                                  (dados["4"].dt.date.between(data_inicio, data_fim))]["1"].str.strip().unique().tolist()
    else:
        lojas_disponiveis = []
    loja = st.selectbox("Loja", ["Selecione uma Loja"] + lojas_disponiveis)

    # Líder
    if loja not in ["Selecione uma Loja"]:
        lider = dados[(dados["8"].str.strip() == regional) &
                      (dados["1"].str.strip() == loja) &
                      (dados["4"].dt.date.between(data_inicio, data_fim))]["12"].iloc[0]
    else:
        lider = ""
    st.text_input("Líder", value=lider)

    # Motivo
    motivos = ["Selecione um Motivo", "Falha Impressão", "Impressora Queimada",
               "Router não funciona", "Notebook não liga", "Coletor não conecta", "Outro"]
    motivo = st.selectbox("Motivo do Suporte", motivos)
    outro_motivo = st.text_input("Digite o motivo do suporte:") if motivo == "Outro" else ""

    # Botão cadastrar
    if st.button("Cadastrar Chamado"):
        motivo_final = outro_motivo if motivo == "Outro" else motivo
        if regional in ["Selecione uma Regional"] or loja in ["Selecione uma Loja"] or lider.strip() == "" or motivo_final.strip() == "" or motivo_final == "Selecione um Motivo":
            st.warning("Todos os campos devem ser preenchidos!")
        else:
            cadastrar_chamado(regional, loja, lider, motivo_final)

    # Listar chamados filtrados
    st.subheader("Chamados")
    df_chamados = listar_chamados(filtro_status, data_inicio, data_fim)
    st.dataframe(df_chamados, width='stretch')

    # Exportar Excel
    if not df_chamados.empty:
        excel_data = exportar_chamados_para_excel(df_chamados)
        st.download_button("Exportar Chamados em Excel", data=excel_data, file_name="chamados.xlsx")

    # Finalizar chamado pelo ID
    if "Aberto" in filtro_status:
        st.subheader("Finalizar Chamado")
        if not df_chamados.empty:
            opcoes = df_chamados.apply(lambda row: f"ID {row['id']} - {row['motivo']} - {row['loja']}", axis=1)
            selecionado = st.selectbox("Selecione o chamado para finalizar", options=opcoes)
            if st.button("Finalizar Chamado Selecionado"):
                chamado_id = int(selecionado.split(" ")[1])
                finalizar_chamado(chamado_id)

    # Botão sair
    if st.button("Sair"):
        st.session_state.clear()  # limpa a sessão
        st.stop()  # interrompe o script e volta para a tela de login