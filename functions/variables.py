import streamlit as st


class Variables:

    def __init__(self):

        def create_variable(name, value):
            globals()[name] = value

        def debug_variable(variable):

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

        self.create = create_variable
        self.debug = debug_variable
