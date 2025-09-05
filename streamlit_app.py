import streamlit as st
from dashboard import dashboard
from chamados import sistema_chamados

# Menu lateral
st.sidebar.title("Menu")
pagina = st.sidebar.radio("Ir para:", ["Dashboard", "Sistema de Chamados"])

if pagina == "Dashboard":
    dashboard()
elif pagina == "Sistema de Chamados":
    sistema_chamados()
