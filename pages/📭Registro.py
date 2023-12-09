import streamlit as st
import requests
import re
import time  # Importação adicional para timestamp

# Configuração da página para layout "wide"
st.set_page_config(layout='wide')

# Função para validar o email
def validar_email(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return "Email inválido. Por favor, insira um email correto."
    return None

# Função para validar a senha
def validar_senha(senha):
    if len(senha) < 5:
        return "A senha deve ter pelo menos 5 caracteres."
    return None

# Função para validar o token
def validar_token(token):
    url = "http://anadata.pythonanywhere.com/api.ana-health/verify-token/"
    response = requests.post(url, data={'token': token})
    if response.status_code == 200 and response.json().get('status') == 'success':
        return None
    return "Token inválido ou expirado. Por favor, insira um token válido."

# Título da página
st.title("Registro")

# Entradas de dados do usuário
email = st.text_input("Email")
password = st.text_input("Senha", type="password")
token = st.text_input("Token")
btn_register = st.button("Registrar")

# Processamento do registro
if btn_register:
    erro_email = validar_email(email)
    erro_senha = validar_senha(password)
    erro_token = validar_token(token)

    if erro_email or erro_senha or erro_token:
        if erro_email:
            st.error(erro_email)
        if erro_senha:
            st.error(erro_senha)
        if erro_token:
            st.error(erro_token)
    else:
        url = "http://anadata.pythonanywhere.com/api.ana-health/register/"
        data = {'email': email, 'password': password, 'token': token}
        response = requests.post(url, data=data)

        if response.status_code == 200 and response.json().get('status') == 'success':
            st.success("Registro realizado com sucesso!")
        else:
            erro_registro = response.json().get('message', 'Erro desconhecido. Tente novamente mais tarde.')
            st.error(f"Erro no registro: {erro_registro}")

# Link para a página de login
st.write("Já tem uma conta? Faça o login na página de [login](/Login)")
