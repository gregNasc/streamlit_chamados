import os
from datetime import datetime
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente localmente (não necessário no Streamlit Cloud)
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Debug seguro
st.write("SUPABASE_URL OK" if SUPABASE_URL else "SUPABASE_URL missing")
st.write("SUPABASE_KEY OK" if SUPABASE_KEY else "SUPABASE_KEY missing")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não encontradas.")

# Inicializar cliente Supabase
supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
    options={"auto_refresh_token": False, "persist_session": False}
)

# ---------------------------
# Funções de CRUD
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
    fechamento = agora.isoformat()
    duracao = str(agora - abertura).split(".")[0]

    update_data = {
        "fechamento": fechamento,
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

def cadastrar_usuario_se_nao_existir(usuario, senha, papel="usuario"):
    resultado = supabase.table("usuarios").select("id").eq("usuario", usuario).execute()
    if resultado.data:
        return False
    supabase.table("usuarios").insert({
        "usuario": usuario,
        "senha": senha,
        "papel": papel
    }).execute()
    return True

def zerar_banco(confirmar=False):
    if confirmar:
        supabase.table("chamados").delete().neq("id", 0).execute()
        # supabase.table("usuarios").delete().neq("id", 0).execute()
        st.success("✅ Banco de dados zerado com sucesso!")

# ---------------------------
# Exportar Excel seguro
# ---------------------------

def exportar_chamados_para_excel(df):
    df_export = df.copy()
    for col in ["abertura", "fechamento"]:
        if col in df_export.columns:
            df_export[col] = pd.to_datetime(df_export[col], errors="coerce").dt.tz_localize(None)
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_export.to_excel(writer, index=False, sheet_name="chamados")
    output.seek(0)
    return output.getvalue()
