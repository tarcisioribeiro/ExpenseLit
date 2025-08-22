from functions.query_executor import QueryExecutor
from dictionary.vars import TO_REMOVE_LIST
from dictionary.sql.user_queries import check_user_query
import streamlit as st
import mysql.connector


st.set_page_config(
    page_title='ExpenseLit - Controle Financeiro',
    page_icon=':moneybag:',
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None
)

hide_streamlit_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
                    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

try:
    from dictionary.db_config import db_config
    st.write(db_config)
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        def main():
            query_executor = QueryExecutor()
            user_quantity = query_executor.simple_consult_query(
                check_user_query,
                params=()
            )
            user_quantity = query_executor.treat_simple_result(
                user_quantity,
                TO_REMOVE_LIST
            )
            treated_user_quantity = int(user_quantity)

            if treated_user_quantity == 0:
                st.session_state.is_logged_in = False
                from functions.login import CreateUser
                CreateUser().main_menu()

            elif treated_user_quantity > 0:
                if 'is_logged_in' not in st.session_state:
                    st.session_state.is_logged_in = False
                    if st.session_state.is_logged_in:
                        from screens.app import App
                        App().main_menu()
                    else:
                        try:
                            from functions.login import Menu
                            Menu().main_menu()
                        except KeyError as key_error:
                            st.warning(
                                body="""
                                :warning: Alguns erros no Login.
                                {}.
                                """.format(key_error)
                            )

                    if __name__ == "__main__":
                        main()

except mysql.connector.Error as error:
    col1, col2, col3 = st.columns(3)
    with col2:
        if error.errno == 1049:
            st.error(
                body="""
                Erro ao conectar ao MySQL: O banco de dados {} não existe.
                Faça a importação do arquivo de backup/implantação.
                """.format(
                    db_config["database"]
                )
            )
        else:
            st.error(
                body="""
                Erro ao conectar ao MySQL: {}.
                """.format(error)
            )
