import streamlit as st
import pandas as pd
import plotly.express as px
import time
import requests
import io
from func.dataprocess import preProcess
from func.dataPreprocessingMonth import process_csv
import io

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

def process_data(uploaded_file, user_email=None):
    progress_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)
        progress_bar.progress(percent_complete + 1)

    #preProcess(uploaded_file)
    process_csv(uploaded_file)

    action_url = "http://anadata.pythonanywhere.com/api.ana-health/create-log/"
    action_data = {
        'token': st.session_state["token"],
        'action': 'upload_predicao',
    }
    requests.post(action_url, json=action_data)

    with open('processed_data.csv', 'r') as file:
        st.download_button(label="Baixar Arquivo Processado", data=file, file_name='processed_data.csv', mime='text/csv')

    return pd.read_csv('processed_data.csv')

def main():
    st.set_page_config(layout="wide")
    st.title('Dashboard de Análise de Dados')

    with st.sidebar:
        st.header("Configurações")
        uploaded_file = st.file_uploader("Faça o upload de um arquivo CSV", type="csv")
        user_email = "email_do_usuario@example.com"

    # Layout da página principal
    if uploaded_file is not None:
        with st.spinner('Processando dados...'):
            df_processed = process_data(uploaded_file, user_email)
            st.write("DataFrame Processado:")
            st.write(df_processed)


            if st.button('Prever Churn'):
            
                csv_url = "http://anadata.pythonanywhere.com/api.ana-health/predict-csv/"
                csv_data = {
                    'token': st.session_state["token"],
                    'csv': df_processed.to_csv(),
                }

                csv_file = io.StringIO()
                df_processed.to_csv(csv_file, index=False)
                csv_file.seek(0)

                files = {
                    'file': ('filename.csv', csv_file, 'text/csv')
                }
                response = requests.post(csv_url, data=csv_data, files=files)

                st.write("Resposta da API:")

                response_data = response.json()
                print(response_data)
                if not response.status_code == 200:
                    st.json(response_data)
                if isinstance(response_data, dict):
                    # If the response is a dictionary, convert it into a DataFrame
                    df_response = pd.json_normalize(response_data)
                elif isinstance(response_data, list):
                    # If the response is a list of dictionaries, it is already in the right format for DataFrame conversion
                    df_response = pd.DataFrame(response_data)
                else:
                    st.error("Unsupported type of JSON response")
                    return

                st.dataframe(df_response.T)


                st.download_button(
                    label="Baixar CSV Processado",
                    data=df_processed.to_csv().encode('utf-8'),
                    file_name='processed_data.csv',
                    mime='text/csv',
                )



if __name__ == "__main__":
    main()