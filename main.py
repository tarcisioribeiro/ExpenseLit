try:

    import os

    actual_path = os.getcwd()

    software_env_path = '{}/.env'.format(actual_path)
    session_state_path = '{}/data/cache/session_state.py'.format(actual_path)

    if not os.path.isfile(software_env_path):
        import streamlit as st

        col1, col2, col3 = st.columns(3)

        with col2:
            st.error(body="Não foi configurado o ambiente de conexão. Informe os dados de conexão.", icon="🚨")

    if not os.path.isfile(session_state_path):

        with open(session_state_path, 'w') as session_state_archive:
            session_state_archive.write("logged_user = ''")
            session_state_archive.write("\nlogged_user_password = ''")

    from dictionary.sql import check_user_query
    from dictionary.vars import to_remove_list
    from functions.login import User
    from functions.create_user import CreateUser
    from functions.query_executor import QueryExecutor
    import streamlit as st


    def main():

        st.set_page_config(page_title='Controle Financeiro', page_icon=':moneybag:', layout="wide", initial_sidebar_state="auto", menu_items=None)

        hide_streamlit_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
                    """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)

        query_executor = QueryExecutor()
        user_quantity = query_executor.simple_consult_query(check_user_query)
        user_quantity = query_executor.treat_simple_result(user_quantity, to_remove_list)
        user_quantity = int(user_quantity)

        if user_quantity == 0:
            create_user = CreateUser()
            create_user.main_menu()

        elif user_quantity > 0:
            if 'is_logged_in' not in st.session_state:
                st.session_state.is_logged_in = False

            if st.session_state.is_logged_in:
                from screens.app import HomePage
                HomePage()
            else:
                try:
                    call_user = User()
                    call_user.get_login()
                except KeyError:
                    st.warning(body=":warning: Alguns erros no Login.")

    if __name__ == "__main__":
        main()

except KeyError:
    import streamlit as st
    st.rerun()
