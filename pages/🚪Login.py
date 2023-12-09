import streamlit as st
import requests

# Configuração da página para layout "wide"
st.set_page_config(layout='wide')

st.title("Login")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
btn_login = st.button("Login")
# não tem conta, crie uma na página de registro
st.write("Não tem conta? Crie uma na página de [registro](/Registro)")

if btn_login:
    login_url = "http://anadata.pythonanywhere.com/api.ana-health/login/"
    login_data = {
        'email': email,
        'password': password,
    }
    response = requests.post(login_url, data=login_data)

    if response.json()['status'] == 'success':
        st.success("Login realizado com sucesso!")
        st.session_state["authenticated"] = True
        st.session_state["token"] = response.json()['token']

        # Enviar informações de USER e ACTION para o backend
        action_url = "http://anadata.pythonanywhere.com/api.ana-health/create-log/"
        action_data = {
            'token': st.session_state["token"],
            'action': 'login',
        }
        action_response = requests.post(action_url, json=action_data)

        # Aqui você pode adicionar uma verificação para a resposta do action_response se necessário

    else:
        st.error("Email ou senha incorretos")
