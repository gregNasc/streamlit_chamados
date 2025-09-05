import streamlit as st
import streamlit_authenticator as stauth

def autenticar_usuario():
    # Usuários e senhas
    names = ["User"]
    usernames = ["user"]
    passwords = ["user"]  # texto claro, não precisa gerar hash para teste local

    # Criar autenticação
    credentials = {
        "usernames": {
            "user": {
                "name": "user",
                "password": stauth.Hasher(["senha123"]).generate()[0]
            }
        }
    }

    authenticator = stauth.Authenticate(
        credentials,
        "meu_app_cookie",
        "chave_secreta",
        cookie_expiry_days=30
    )

    # Tela de login
    login_info = authenticator.login(location="main")  # 'location' apenas

    if login_info is not None:
        name, authentication_status, username = login_info
    else:
        name = authentication_status = username = None

    if authentication_status:
        st.success(f"Bem-vindo, {name} 👋")
        authenticator.logout("Sair", "sidebar")
        return True
    elif authentication_status is False:
        st.error("Usuário ou senha incorretos")
        return False
    else:
        st.warning("Por favor, insira usuário e senha")
        return False
