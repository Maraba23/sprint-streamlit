import streamlit as st
import requests

# Configuração da página para layout "wide"
st.set_page_config(layout='wide')

#Título da página
st.title("Página de Administração")
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Você não está autenticado, faça login para acessar esta página")
    st.stop()

verify_url = "http://anadata.pythonanywhere.com/api.ana-health/access-granted/"
verify_data = {
    'token': st.session_state["token"],
}
verify_response = requests.post(verify_url, data=verify_data)
if verify_response.json()['status'] == 'error':
    st.error("Você não está autenticado, faça login para acessar esta página")
    st.stop()
elif verify_response.json()['role'] != 'admin':
    st.error("Você não tem permissão para acessar esta página, faça login com uma conta de administrador")
    st.stop()

# Inicialização do estado da sessão para 'alert_message' e 'tokens'
if 'alert_message' not in st.session_state:
    st.session_state['alert_message'] = (None, None)  # (mensagem, severidade)
if 'tokens' not in st.session_state:
    st.session_state['tokens'] = []

# Estilo personalizado
st.markdown(
    """
    <style>
    /* Estilos globais */
    .markdown-text-container {
        padding: 0 !important;
    }
    /* Mensagem de sucesso e erro */
    .stAlert-success {
        border: 1px solid #198754;
        background-color: #d1e7dd;
        color: #0f5132;
    }
    .stAlert-error {
        border: 1px solid #842029;
        background-color: #f8d7da;
        color: #842029;
    }
    /* Botões estilizados */
    .stButton>button {
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #28a745;
        color: white;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #218838;
    }
    </style>

    """,
    unsafe_allow_html=True
)


# Função para obter tokens
def get_tokens():
    url = "http://anadata.pythonanywhere.com/api.ana-health/tokens/"
    response = requests.get(url)
    if response.status_code == 200:
        st.session_state["tokens"] = response.json()

get_tokens()  # Obtém os tokens


# Função para criar um novo token e registrar a ação
def create_token():
    url = "http://anadata.pythonanywhere.com/api.ana-health/access-token/"
    data = {
        'token': st.session_state["token"] if "token" in st.session_state else None,
    }
    response = requests.post(url, data=data)
    if response.json()['status'] == 'success':
        st.session_state["alert_message"] = ("Token criado com sucesso!", "success")
        get_tokens()  # Atualiza a lista de tokens

        # Enviar informações da criação do token para o backend
        action_url = "http://anadata.pythonanywhere.com/api.ana-health/create-log/"
        action_data = {
            'token': st.session_state["token"],
            'action': 'create_token',
        }
        requests.post(action_url, json=action_data)
    else:
        st.session_state["alert_message"] = ("Erro ao criar token", "error")

# Função para deletar um token
def delete_token(token_id):
    url = f"http://anadata.pythonanywhere.com/api.ana-health/delete-token/{token_id}/"
    response = requests.delete(url)
    if response.status_code == 200:
        st.session_state["alert_message"] = ("Token deletado com sucesso!", "success")
        get_tokens()  # Atualiza a lista de tokens

        # Enviar informações da exclusão do token para o backend
        action_url = "http://anadata.pythonanywhere.com/api.ana-health/create-log/"
        action_data = {
            'token': st.session_state["token"],
            'action': 'delete_token',
        }
        requests.post(action_url, json=action_data)
    else:
        st.session_state["alert_message"] = ("Erro ao deletar token", "error")

# Exibe os tokens em uma tabela
if st.session_state["tokens"]:
    # Definindo as colunas da tabela
    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
    with col1:
        st.markdown("**Token**")
    with col2:
        st.markdown("**Criado em**")
    with col3:
        st.markdown("**Criado por**")
    with col4:
        st.markdown("**Ações**")
    
    # Listando os tokens
    for token in st.session_state["tokens"]:
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            st.write(token['token'])
        with col2:
            st.write(token['created'])
        with col3:
            st.write(token['created_by'])
        with col4:
            if st.button("Deletar", key=token['token']):
                delete_token(token['token'])  # Função de deleção a ser definida
                st.rerun()

# Mensagem de sucesso e erro
if st.session_state["alert_message"][0]:
    if st.session_state["alert_message"][1] == "success":
        st.success(st.session_state["alert_message"][0])
    elif st.session_state["alert_message"][1] == "error":
        st.error(st.session_state["alert_message"][0])
    # Redefine a mensagem de alerta para None
    st.session_state["alert_message"] = (None, None)

# Botão para criar um novo token
if st.button("Criar Token"):
    create_token()
    st.rerun()  # Rerun para atualizar a lista de tokens