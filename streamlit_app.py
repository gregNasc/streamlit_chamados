import streamlit as st
from chamados import sistema_chamados
from database import verificar_usuario, inicializar_banco, cadastrar_usuario, zerar_banco
from dashboard import dashboard_admin, dashboard_usuario  # imports atualizados

# Configuração da página
st.set_page_config(
    page_title="Sistema de Chamados",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa banco e usuários
inicializar_banco()
cadastrar_usuario("admin", "admin123", papel="admin")
cadastrar_usuario("user", "user", papel="usuario")


# Sessão persistente
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None
    st.session_state["papel"] = None

# Função de logout
def sair():
    st.session_state["usuario_logado"] = None
    st.session_state["papel"] = None
    st.rerun()


# Tela de login
if not st.session_state["usuario_logado"]:
    st.title("Login Sistema de Chamados")
    usuario_input = st.text_input("Usuário")
    senha_input = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        papel = verificar_usuario(usuario_input, senha_input)
        if papel:
            st.session_state["usuario_logado"] = usuario_input
            st.session_state["papel"] = papel
            st.success(f"Bem-vindo(a), {usuario_input}!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")


# Tela principal
else:
    usuario_logado = st.session_state["usuario_logado"]
    papel = st.session_state["papel"]

    # Menu lateral
    st.sidebar.title("Menu")
    if st.sidebar.button("Sair"):
        sair()

    menu_opcoes = ["Dashboard", "Sistema de Chamados"]
    pagina = st.sidebar.radio("Ir para:", menu_opcoes)


    # Navegação entre páginas
    if pagina == "Dashboard":
        if papel == "admin":
            dashboard_admin()  # Dashboard completo com exportação
        else:
            dashboard_usuario()  # Apenas gráfico de status

    elif pagina == "Sistema de Chamados":
        sistema_chamados(usuario_logado)


    # Botão sensível apenas para admin
    if papel == "admin":
        st.sidebar.markdown("---")
        if "confirm_zerar" not in st.session_state:
            st.session_state["confirm_zerar"] = False

        if not st.session_state["confirm_zerar"]:
            if st.sidebar.button("Zerar Banco de Dados"):
                st.session_state["confirm_zerar"] = True

        else:
            st.warning("⚠️ Esta ação apagará TODOS os dados do banco de dados!")
            col1, col2 = st.sidebar.columns(2)
            if col1.button("Sim"):
                zerar_banco()
                st.success("✅ Banco de dados zerado com sucesso!")
                st.session_state["confirm_zerar"] = False
                st.rerun()  # Atualiza interface
            if col2.button("Não"):
                st.session_state["confirm_zerar"] = False
