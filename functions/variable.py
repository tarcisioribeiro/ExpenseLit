from dictionary.vars import DECIMAL_VALUES
import streamlit as st


class Variable:
    """
    Classe com métodos para análises de variáveis.
    """

    def treat_complex_string(self, value_passed: float):
        str_value = str(value_passed)
        str_value = str_value.replace(".", ",")
        last_two_values = str_value[-2:]

        if last_two_values in DECIMAL_VALUES:
            str_value = str_value + "0"

        return str_value

    def create_variable(self, name, value):
        """
        Cria uma nova variável.
        """
        globals()[name] = value

    def debug_variable(self, variable):
        """
        Exibe os dados da variável.
        """

        variable_type = type(variable).__name__

        st.info(body="Tipo: {}.".format(variable_type))
        st.info(body="Conteúdo: {}.".format(variable))

        if variable_type != "int" and variable_type != "float" and variable_type != "complex" and variable_type != "UploadedFile" and variable_type != "decimal.Decimal":
            st.info(body="Tamanho: {}.".format(len(variable)))

        if variable_type == "list":
            for i in range(0, len(variable)):
                st.info(body="Tipo: {}.".format(
                    type(variable[i]).__name__))
                st.info(body="Conteúdo: {}.".format(variable[i]))
