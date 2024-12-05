import streamlit as st


class Variables:
    """
    Classe responsável pela identificação e detalhamento de uma variável.
    """

    def debug_variable(self, variable):

        variable_type = type(variable).__name__

        st.info(body="Tipo: {}.".format(variable_type))
        st.info(body="Conteúdo: {}.".format(variable))

        if (
            variable_type != "int"
            and variable_type != "float"
            and variable_type != "complex"
            and variable_type != "UploadedFile"
            and variable_type != "decimal.Decimal"
        ):
            st.info(body="Tamanho: {}.".format(len(variable)))
