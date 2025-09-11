import os
from datetime import datetime
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Variáveis SUPABASE_URL ou SUPABASE_KEY não encontradas.")
    st.stop()

# Inicializar cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------
# Funções CRUD
# ---------------------------
def ler_chamados():
    response = supabase.table("chamados").select("*").execute()
    df = pd.DataFrame(response.data)
    return df

def cadastrar_chamado(regional, loja, lider, motivo):
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

def finalizar_chamado(chamado_id, finalizado_por=None):
    chamado = supabase.table("chamados").select("abertura").eq("id", chamado_id).execute()
    if not chamado.data:
        st.error("❌ Chamado não encontrado!")
        return

    abertura = datetime.fromisoformat(chamado.data[0]["abertura"])
    if abertura.tzinfo is not None:
        abertura = abertura.replace(tzinfo=None)

    agora = datetime.now()
    duracao = str(agora - abertura).split(".")[0]

    update_data = {
        "fechamento": agora.isoformat(),
        "duracao": duracao,
        "status": "Finalizado"
    }
    if finalizado_por:
        update_data["finalizado_por"] = finalizado_por

    supabase.table("chamados").update(update_data).eq("id", chamado_id).execute()
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
