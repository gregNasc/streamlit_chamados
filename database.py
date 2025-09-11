import os
from datetime import datetime
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()  # Procura arquivo .env na raiz do projeto

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não encontradas.")

# Inicializar cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Funções de CRUD

def ler_chamados():
    response = supabase.table("chamados").select("*").execute()
    df = pd.DataFrame(response.data)
    return df

def cadastrar_chamado(regional, loja, lider, motivo):
    # Garantir datetime naive (sem timezone)
    abertura = datetime.now().replace(tzinfo=None).isoformat()
    supabase.table("chamados").insert({
        "regional": regional,
        "loja": loja,
        "lider": lider,
        "motivo": motivo,
        "abertura": abertura,
        "status": "Aberto"
    }).execute()
    st.success("✅ Chamado cadastrado!")

def finalizar_chamado(chamado_id):
    chamado = supabase.table("chamados").select("abertura").eq("id", chamado_id).execute()
    if not chamado.data:
        st.error("❌ Chamado não encontrado!")
        return

    # Converte string ISO 8601 para datetime
    abertura = datetime.fromisoformat(chamado.data[0]["abertura"])
    # Remover timezone caso exista
    if abertura.tzinfo is not None:
        abertura = abertura.replace(tzinfo=None)

    agora = datetime.now()  # datetime naive
    fechamento = agora.isoformat()
    duracao = str(agora - abertura).split(".")[0]

    supabase.table("chamados").update({
        "fechamento": fechamento,
        "duracao": duracao,
        "status": "Finalizado"
    }).eq("id", chamado_id).execute()
    st.success(f"✅ Chamado {chamado_id} finalizado!")

def verificar_usuario(usuario, senha):
    result = supabase.table("usuarios").select("papel").eq("usuario", usuario).eq("senha", senha).execute()
    if result.data:
        return result.data[0]["papel"]
    return None

def cadastrar_usuario(usuario, senha, papel="usuario"):
    supabase.table("usuarios").insert({
        "usuario": usuario,
        "senha": senha,
        "papel": papel
    }).execute()

def cadastrar_usuario_se_nao_existir(usuario, senha, papel="usuario"):
    resultado = supabase.table("usuarios").select("id").eq("usuario", usuario).execute()
    if resultado.data:
        return False  # Usuário já existe
    supabase.table("usuarios").insert({
        "usuario": usuario,
        "senha": senha,
        "papel": papel
    }).execute()
    return True

def zerar_banco(confirmar=False):
    if confirmar:
        supabase.table("chamados").delete().neq("id", 0).execute()
#       supabase.table("usuarios").delete().neq("id", 0).execute()
        st.success("✅ Banco de dados zerado com sucesso!")
