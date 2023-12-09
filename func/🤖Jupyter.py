import streamlit as st
import nbformat
from io import BytesIO

def read_notebook(file):
    return nbformat.read(file, as_version=4)

def save_notebook(notebook):
    buffer = BytesIO()
    nbformat.write(notebook, buffer)
    buffer.seek(0)
    return buffer.getvalue()

def main():
    st.sidebar.title("Upload de Notebook")
    uploaded_file = st.sidebar.file_uploader("Faça o upload de um Jupyter Notebook", type="ipynb")

    st.title('Visualização e Edição de Jupyter Notebook')

    # Inicialização da sessão do Streamlit
    if 'notebook' not in st.session_state:
        st.session_state.notebook = None
        st.session_state.edit_states = {}

    # Botão de recarregar é colocado na sidebar para manter a consistência
    if uploaded_file is not None and (st.session_state.notebook is None or st.sidebar.button('Recarregar Notebook')):
        st.session_state.notebook = read_notebook(uploaded_file)
        st.session_state.edit_states = {i: False for i, _ in enumerate(st.session_state.notebook.cells) if _.cell_type == 'code'}

    if st.session_state.notebook is not None:
        # Uso de expander para organização e melhor visualização
        for i, cell in enumerate(st.session_state.notebook.cells):
            if cell.cell_type == 'markdown':
                st.markdown(cell.source)
            elif cell.cell_type == 'code':
                with st.expander(f"Célula de Código {i+1}", expanded=True):
                    edit_state = st.checkbox(f"Editar Célula {i+1}", key=f"edit_{i}")
                    if edit_state:
                        new_code = st.text_area("", value=cell.source, height=200, key=f"textarea_{i}")
                        if st.button(f"Salvar Célula {i+1}", key=f"save_{i}"):
                            cell.source = new_code
                            st.session_state.edit_states[i] = False
                            st.experimental_rerun()
                    else:
                        st.code(cell.source)

        # Botão para baixar o notebook editado
        if st.button('Baixar Notebook Editado'):
            edited_notebook = save_notebook(st.session_state.notebook)
            st.download_button(
                label="Baixar Notebook Editado",
                data=edited_notebook,
                file_name='edited_notebook.ipynb',
                mime='application/x-ipynb+json'
            )

if __name__ == "__main__":
    main()
