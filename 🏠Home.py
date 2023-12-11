import streamlit as st
import pandas as pd

st.set_page_config(
   page_title='Seu App Streamlit',
   layout='wide',
   initial_sidebar_state='auto',
)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Conteúdo principal da página
st.title("Página Principal")


if not st.session_state["authenticated"] == True:
    st.warning("Essa página contem a documentação do projeto, para acessar ela e qualquer outra página você precisa estar logado")
    st.stop()

st.write("Você está logado!")
logout = st.button("Logout")
if logout:
    st.session_state["authenticated"] = False
    st.session_state["token"] = None

st.markdown(
    """
    # Documentação do projeto

    ## Sobre o projeto

    Nesse projeto tínhamos como objetivo criar uma analise de churn para a Ana Health, uma empresa de planos de saúde.

    Para isso utilizamos o dataset fornecido pela empresa, e criamos um modelo de machine learning para prever se um cliente iria cancelar o plano de saúde ou não.

    ---

    ## Como utilizar o projeto

    ### Página de Upload

    Na página de upload você pode enviar um arquivo csv para vizualizar gráficos e tabelas com os dados do arquivo.

    exemplo de arquivo csv:
    """
)

df = pd.read_csv("Example.csv")

st.dataframe(df)

st.warning("Todas as colunas do arquivo devem estar presentes no arquivo, mesmo que não sejam utilizadas")

st.markdown(
    """
    ### Pagina de Predição

    Na pagina de predição você pode enviar um arquivo csv para o modelo de machine learning prever se um cliente irá cancelar o plano de saúde ou não no proximo mês.

    Quando o csv é enviado, um pré-processamento dos dados é realizado e mostrado na tela.

    Após isso, basta usar o botão "Prever Churn" para que o modelo faça a predição.

    O arquivo csv pode ter quantos usuarios forem necessarios, mas deve conter as mesmas colunas do exemplo abaixo.

    A predição retorna o id do usuário a ser previsto e a predição em si. Os resultados podem ser: Continua, Sai da assinatura ou Incerto.

    exemplo de arquivo csv:
    """
)

df = pd.read_csv("Example.csv")

st.dataframe(df)

st.warning(
    """
    Todas as colunas do arquivo devem estar presentes nele, mesmo que não sejam utilizadas.

    Sobre a coluna target ("Status"), Ela deve estar presente no dataset, mesmo que esteja totalmente vazia, isso é necessário para o modelo funcionar corretamente.
    """
)

st.markdown(
    """
    ### Página de registro

    Na página de registro você pode criar uma conta para acessar as outras páginas do projeto.

    Para criar a conta é necessario um `token` fornecido pelo adiministrador do sistema.

    Sem o token, você não pode criar uma conta.

    ### Página de Admin

    Na página de admin você pode criar tokens para que outras pessoas possam criar contas.

    Aqui você pode criar e deletar tokens.

    - Apenas o administrador do sistema pode acessar essa página.

    ### Página de Logs

    Na página de logs você pode ver todos os logs de ações realizadas no sistema.

    Os logs são: Upload de arquivos para gráficos, Upload de arquivos para predição, Login, Criação de token, Deleção de token.

    - Apenas o administrador do sistema pode acessar essa página.
    """
)

