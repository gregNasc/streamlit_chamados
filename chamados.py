import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Conexão com banco de dados
conn = sqlite3.connect("chamados.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS chamados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    regional TEXT,
    loja TEXT,
    lider TEXT,
    motivo TEXT,
    abertura TEXT,
    fechamento TEXT,
    duracao TEXT,
    status TEXT
)
""")
conn.commit()

# Carregar dados do Excel
dados = pd.read_excel("chamado.xlsx", header=1)
dados.columns = [str(c).strip().upper() for c in dados.columns]
for col in ["8", "1", "12"]:
    dados[col] = dados[col].astype(str)
dados["4"] = pd.to_datetime(dados["4"], errors='coerce')

# Funções do sistema
def listar_chamados(filtro="Aberto"):
#    if filtro == "Todos":
#        df = pd.read_sql_query("SELECT * FROM chamados", conn)
    if filtro == "Chamados Abertos":
        df = pd.read_sql_query("SELECT * FROM chamados WHERE status='Aberto'", conn)
    elif filtro == "Chamados Finalizados":
        df = pd.read_sql_query("SELECT * FROM chamados WHERE status='Finalizado'", conn)
    return df

def cadastrar_chamado(regional, loja, lider, motivo):
    if motivo == "Outro":
        motivo = st.text_input("Digite o motivo do suporte:")
    abertura = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    cursor.execute("""
        INSERT INTO chamados (regional, loja, lider, motivo, abertura, status)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (regional, loja, lider, motivo, abertura, "Aberto"))
    conn.commit()
    st.success("Chamado cadastrado!")

def finalizar_chamado(chamado_id):
    cursor.execute("SELECT abertura FROM chamados WHERE id = ?", (chamado_id,))
    abertura = datetime.strptime(cursor.fetchone()[0], "%d-%m-%Y %H:%M:%S")
    fechamento = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    duracao = str(datetime.now() - abertura).split('.')[0]
    cursor.execute("""
        UPDATE chamados
        SET fechamento=?, duracao=?, status=?
        WHERE id=?""",
        (fechamento, duracao, "Finalizado", chamado_id))
    conn.commit()
    st.success(f"Chamado {chamado_id} finalizado!")

# Interface
def sistema_chamados():
    st.title("Sistema de Chamados")
    st.sidebar.header("Filtros")
    filtro_status = st.sidebar.selectbox("Filtrar Chamados", ["Chamados Abertos", "Chamados Finalizados"])
    data_sel = st.date_input("Data do Chamado", value=datetime.today())

    # Regional
    regionais_disponiveis = dados[dados["4"].dt.date == data_sel]["8"].str.strip().unique().tolist()
    regional = st.selectbox("Regional", ["Selecione uma Regional"] + regionais_disponiveis)

    # Loja
    if regional not in ["Selecione uma Regional"]:
        lojas_disponiveis = dados[(dados["8"].str.strip() == regional) & (dados["4"].dt.date == data_sel)]["1"].str.strip().unique().tolist()
    else:
        lojas_disponiveis = []
    loja = st.selectbox("Loja", ["Selecione uma Loja"] + lojas_disponiveis)

    # Líder
    if loja not in ["Selecione uma Loja"]:
        lider = dados[(dados["8"].str.strip() == regional) &
                      (dados["1"].str.strip() == loja) &
                      (dados["4"].dt.date == data_sel)]["12"].iloc[0]
    else:
        lider = ""
    st.text_input("Líder", value=lider)

    # Motivo
    # Lista de motivos
    motivos = ["Selecione um Motivo", "Falha Impressão", "Impressora Queimada",
               "Router não funciona", "Notebook não liga", "Coletor não conecta", "Outro"]

    # Selectbox de motivos
    motivo = st.selectbox("Motivo do Suporte", motivos)

    # Se o usuário selecionar "Outro", abre o input de texto
    outro_motivo = ""
    if motivo == "Outro":
        outro_motivo = st.text_input("Digite o motivo do suporte:")

    # Botão de cadastrar chamado
    if st.button("Cadastrar Chamado", key="btn_cadastrar_chamado"):
        # lógica do cadastro
        motivo_final = outro_motivo if motivo == "Outro" else motivo

        if (regional in ["Selecione uma Regional"] or
                loja in ["Selecione uma Loja"] or
                lider.strip() == "" or
                motivo_final.strip() == "" or
                motivo_final == "Selecione um Motivo"):
            st.warning("Todos os campos devem ser preenchidos!")
        else:
            cadastrar_chamado(regional, loja, lider, motivo_final)

    #Botão para abrir chamado
#    if st.button("Cadastrar Chamado"):
#       if regional in ["Selecione uma Regional"] or loja in ["Selecione uma Loja"] or lider == "" or motivo in ["Selecione um Motivo"]:
#            st.warning("Todos os campos devem ser preenchidos!")
#        else:
#            cadastrar_chamado(regional, loja, lider, motivo)



    # Listar chamados
    st.subheader("Chamados")
    df_chamados = listar_chamados(filtro_status)
    st.dataframe(df_chamados, use_container_width=True)


    # Finalizar chamado
    if "Aberto" in filtro_status:
        st.subheader("Finalizar Chamado")
        if not df_chamados.empty:
            opcoes = df_chamados.apply(lambda row: f"ID {row['id']} - {row['motivo']} - {row['loja']}", axis=1)
            selecionado = st.selectbox("Selecione o chamado para finalizar", options=opcoes)

            if st.button("Finalizar Chamado Selecionado"):
                chamado_id = int(selecionado.split(" ")[1])
                finalizar_chamado(chamado_id)
                st.success(f"Chamado {chamado_id} finalizado!")
                df_chamados = listar_chamados(filtro_status)
                st.dataframe(df_chamados, use_container_width=True)
