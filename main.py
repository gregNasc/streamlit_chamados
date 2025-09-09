import streamlit as st
from chamados import sistema_chamados
from database import verificar_usuario, inicializar_banco, cadastrar_usuario, zerar_banco
from dashboard import dashboard

# Inicializa banco e cria usuários/admin se não existirem
inicializar_banco()
cadastrar_usuario("admin", "admin123", papel="admin")
cadastrar_usuario("user", "user", papel="usuario")

# Função de sair
def sair():
    st.session_state.clear()
    st.rerun()

# Tela de login
if 'usuario_logado' not in st.session_state:
    st.title("Login Sistema de Chamados")  # Aparece apenas no login

    usuario_input = st.text_input("Usuário")
    senha_input = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        papel = verificar_usuario(usuario_input, senha_input)
        if papel:
            st.session_state['usuario_logado'] = usuario_input
            st.session_state['papel'] = papel
            st.success(f"Bem-vindo(a), {usuario_input}!")
            st.rerun()  # recarrega a página após login
        else:
            st.error("Usuário ou senha incorretos")

# Tela principal do sistema
else:
    usuario_logado = st.session_state['usuario_logado']
    papel = st.session_state['papel']

    # Configuração da página
    st.set_page_config(
        page_title="Sistema de Chamados",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Menu lateral
    st.sidebar.title("Menu")
    pagina = st.sidebar.radio("Ir para:", ["Dashboard", "Sistema de Chamados"])

    # Botão de sair
    if st.sidebar.button("Sair"):
        sair()

    # Navegação entre páginas
    if pagina == "Dashboard":
        dashboard()
    elif pagina == "Sistema de Chamados":
        sistema_chamados(usuario_logado)

    # Admin: Zerar banco
    if papel == "admin":
        if st.sidebar.button("Zerar Banco de Dados"):
            zerar_banco()
            st.warning("Banco de dados zerado! Recarregue a página.")

