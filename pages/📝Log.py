# importar as bibliotecas necessárias
import streamlit as st
import pandas as pd
import requests

# Configuração da página para layout "wide"
st.set_page_config(layout='wide')

st.title("Página de Registro de Ações dos Usuários")

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

# Função para obter os logs de usuário da API
def get_user_logs(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status() 
        data = response.json()
        df = pd.DataFrame(data)

        # Verifica se a coluna 'created' existe e, se sim, formata a data
        if 'created' in df.columns:
            df['created'] = pd.to_datetime(df['created']).dt.strftime('%Y-%m-%d || %H:%M:%S')

        return df
    except requests.RequestException as e:
        st.error(f"Erro ao obter dados da API: {e}")
        return pd.DataFrame(columns=["USER", "ACTION", "created"])  # Atualize as colunas conforme necessário

# Definir a URL da API (substitua pela URL real da sua API)
api_url = "https://anadata.pythonanywhere.com/api.ana-health/logs/"

# Definindo o estilo da tabela
st.markdown(
    """
    <style>
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th {
        background-color: #4CAF50;
        color: white;
    }
    th, td {
        padding: 8px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    tr:hover {
        background-color: #f5f5f5;
        color: black; /* Certifique-se de que o texto permaneça legível */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Inicializando uma variável de sessão para a página atual
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# Função para exibir a tabela com estilo e paginação
def display_styled_table(df):
    # Número de linhas por página
    rows_per_page = 10

    # Número total de páginas
    total_pages = len(df) // rows_per_page + int(len(df) % rows_per_page > 0)

    # Criando a caixa de entrada para seleção direta da página
    page_input = st.number_input('Ir para a página', min_value=1, max_value=total_pages, value=st.session_state.current_page, step=1)

    # Atualizando a página atual com base na entrada do usuário
    if page_input != st.session_state.current_page:
        st.session_state.current_page = page_input
        st.rerun()

    # Calculando o intervalo de linhas para a página atual
    start_row = (st.session_state.current_page - 1) * rows_per_page
    end_row = start_row + rows_per_page

    # Filtrando o DataFrame para a página atual
    df_page = df.iloc[start_row:end_row]

    # Convertendo DataFrame para HTML
    html = df_page.to_html(classes="table table-styled", index=False, escape=False)

    # Exibindo o HTML com estilo
    st.markdown(html, unsafe_allow_html=True)

    # Botões de navegação de página
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button('Anterior') and st.session_state.current_page > 1:
            st.session_state.current_page -= 1
            st.rerun()
    with col2:
        st.write(f"Página {st.session_state.current_page} de {total_pages}")
    with col3:
        if st.button('Próxima') and st.session_state.current_page < total_pages:
            st.session_state.current_page += 1
            st.rerun()

# Carregando os logs automaticamente
user_logs = get_user_logs(api_url)
if not user_logs.empty:
    display_styled_table(user_logs)
else:
    st.write("Nenhum dado disponível para mostrar.")
