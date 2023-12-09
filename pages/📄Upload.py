import streamlit as st
import pandas as pd
import plotly.express as px
import time
import requests
from func.dataprocess import preProcess


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

# Função para criar gráfico de pizza
def plot_pie_chart(data, column, title, legend_title, background_color):
    counts = data[column].value_counts(dropna=False).reset_index()
    counts.columns = [column, 'count']
    counts[column] = counts[column].astype(str)

    fig = px.pie(counts, names=column, values='count', title=title)
    fig.update_traces(marker=dict(colors=px.colors.qualitative.Pastel), textinfo='percent+label')
    fig.update_layout(
        title_font_size=18,
        legend_title=legend_title,
        legend_title_font_size=16,
        legend_font_size=14,
        font=dict(family="Arial, sans-serif"),
        margin=dict(l=20, r=20, t=30, b=20),
        autosize=True,
        showlegend=True,
        paper_bgcolor=background_color,
        plot_bgcolor=background_color
        
    )
    return fig

# Função para criar gráfico de linha de razão de churn
def plot_churn_ratio(df, background_color):
    fig = px.line(df, y='ratio', title='Churn Percentage')
    fig.update_xaxes(title_text='Months', tickangle=45)
    fig.update_yaxes(title_text='Churn / Active', range=[0, 1])
    fig.update_layout(
        title_font_size=18,
        font=dict(family="Arial, sans-serif", color="white"),
        margin=dict(l=20, r=20, t=30, b=20),
        autosize=True,
        paper_bgcolor=background_color,
        plot_bgcolor=background_color
    )
    return fig

# Função para criar gráfico de linha de churn e usuários ativos com cor de fundo personalizada
def plot_churn_active(df, background_color):
    fig = px.line(df, y=['churn', 'active'], title='Churn to Active Users')
    fig.update_xaxes(title_text='Months', tickangle=45)
    fig.update_yaxes(title_text='Users')
    fig.update_layout(
        title_font_size=18,
        font=dict(family="Arial, sans-serif", color="white"),
        margin=dict(l=20, r=20, t=30, b=20),
        autosize=True,
        paper_bgcolor=background_color,
        plot_bgcolor=background_color
    )
    return fig

# Função atualizada para processar dados e enviar ação de upload
def process_data(uploaded_file, user_email=None):
    progress_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)
        progress_bar.progress(percent_complete + 1)

    preProcess(uploaded_file)

    # Enviar ação de upload para o backend se o e-mail do usuário estiver disponível
    action_url = "http://anadata.pythonanywhere.com/api.ana-health/create-log/"
    action_data = {
        'token': st.session_state["token"],
        'action': 'upload_graficos',
    }
    requesto = requests.post(action_url, json=action_data)
    with open('processed_data.csv', 'r') as file:
        st.download_button(label="Baixar Arquivo Processado", data=file, file_name='processed_data.csv', mime='text/csv')

    return pd.read_csv('processed_data.csv')

# Função para preparar os dados de churn
def prepare_churn_data(df):
    df['churn'] = df['contract_end_date'].apply(lambda x: x[:7] if isinstance(x, str) else x)
    tempDF = pd.DataFrame(index=df['churn'].unique())
    tempDF['churn'] = df['churn'].value_counts()
    tempDF['active'] = tempDF.index.map(lambda x: (((df['churn'] > x) | (df['churn'].isna())) & (df['contract_start_date'] <= x)).sum())
    tempDF['ratio'] = tempDF['churn'] / tempDF['active']
    return tempDF.sort_index().dropna()

marital_status_mapping = {
    80: "Solteiro(a)",
    81: "Viúvo(a)",
    82: "Casado(a)",
    83: "Divorciado(a)",
    84: "Separado(a)"
}
def map_marital_status(df, column):
    df[column] = df[column].replace({pd.NA: "Não Informado", None: "Não Informado"})
    df[column] = df[column].map(marital_status_mapping).fillna("Não Informado")
    return df

gender_mapping = {
    63: "Masculino",
    64: "Feminino",
    110: "Homem cis",
    111: "Mulher cis",
    112: "Homem trans",
    113: "Mulher trans",
    114: "Agênero",
    115: "Bigênero",
    116: "Gênero fluído",
    117: "Outro",
    118: "Prefere não dizer"
}
def map_gender(df, column):
    df[column] = df[column].map(gender_mapping)
    return df

pf_pj_mapping = {
    64: "PF",
    65: "PJ",
    66: "Acolhimento Desemprego",
}

def map_pf_pj(df, column):
    df[column] = df[column].replace({pd.NA: "Não Informado", None: "Não Informado"})
    df[column] = df[column].map(pf_pj_mapping).fillna("Não Informado")
    return df



def main():
    st.set_page_config(layout="wide")
    st.title('Dashboard de Análise de Dados')

    # Sidebar para opções de filtragem e configuração
    with st.sidebar:
        st.header("Configurações")
        uploaded_file = st.file_uploader("Faça o upload de um arquivo CSV", type="csv")
        # Suponha que você possa obter o e-mail do usuário aqui
        user_email = "email_do_usuario@example.com"


        user_status_filter = st.selectbox(
            'Escolha o status do usuário:',
            ['Todos', 'Usuários Ativos', 'Usuários Não Ativos']
        )

        data_view_filter = st.selectbox(
        'Escolha a visualização dos dados:',
        ['Todos','Todos menos PJ', 'Somente PJ']
    )



    # Layout da página principal
    if uploaded_file is not None:
        with st.spinner('Processando dados...'):
            df_processed = process_data(uploaded_file, user_email)
            df_processed = map_marital_status(df_processed, 'id_marrital_status')
            df_processed = map_gender(df_processed, 'id_gender')
            df_processed = map_pf_pj(df_processed, 'id_stage')
            tempDF = prepare_churn_data(df_processed)

            
            if user_status_filter == 'Usuários Ativos':
                df_processed = df_processed[df_processed['contract_end_date'].isna()]
            elif user_status_filter == 'Usuários Não Ativos':
                df_processed = df_processed[df_processed['contract_end_date'].notna()]
            else:
                df_processed = df_processed


            
            if data_view_filter == 'Todos menos PJ':
                df_processed = df_processed[df_processed['id_stage'] != 'PJ']
            elif data_view_filter == 'Todos':
                df_processed = df_processed
            elif data_view_filter == 'Somente PJ':
                df_processed = df_processed[df_processed['id_stage'] == 'PJ']
            else:
                df_processed = df_processed

            # Cor de fundo para os contêineres e gráficos
            background_color = '#262730'  # Cor de fundo escolhida

            # Layout principal com colunas
            col1, col2 = st.columns([2,            1])

            # Coluna 1: Gráfico de Churn
            with col1:
                churn_fig = plot_churn_ratio(tempDF, background_color)
                st.plotly_chart(churn_fig, use_container_width=True)

                churn_active_fig = plot_churn_active(tempDF, background_color)
                st.plotly_chart(churn_active_fig, use_container_width=True)

                pie_status_assinatura_fig = plot_pie_chart(df_processed, 'status_assinatura', 'Status da Assinatura', 'Status', background_color)
                pie_status_assinatura_fig.update_layout(height=320)
                st.plotly_chart(pie_status_assinatura_fig, use_container_width=True)

            # Coluna 2: Gráficos de Pizza
            with col2:
                pie_chart_height = 213  # Altura fixa para os gráficos de pizza
                
                pie1_fig = plot_pie_chart(df_processed, 'id_marrital_status', 'Distribuição de Estado Civil', 'Estado Civil', background_color)
                pie1_fig.update_layout(height=pie_chart_height)
                st.plotly_chart(pie1_fig, use_container_width=True)
                
                pie2_fig = plot_pie_chart(df_processed, 'state', 'Distribuição por Estado', 'Estado', background_color)
                pie2_fig.update_layout(height=pie_chart_height)
                st.plotly_chart(pie2_fig, use_container_width=True)

                pie_stage_fig = plot_pie_chart(df_processed, 'id_stage', 'Distribuição de PF - PJ', 'Estágios', background_color)
                pie_stage_fig.update_layout(height=pie_chart_height)
                st.plotly_chart(pie_stage_fig, use_container_width=True)

                pie_gender_fig = plot_pie_chart(df_processed, 'id_gender', 'Distribuição de Gênero', 'Gênero', background_color)
                pie_gender_fig.update_layout(height=pie_chart_height)
                st.plotly_chart(pie_gender_fig, use_container_width=True)

                pie_preference_channel_fig = plot_pie_chart(df_processed, 'Canal de Preferência', 'Canal de Preferência', 'Canais', background_color)
                pie_preference_channel_fig.update_layout(height=320)
                st.plotly_chart(pie_preference_channel_fig, use_container_width=True)



if __name__ == "__main__":
    main()

