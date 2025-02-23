from time import sleep
from reference.diagrams.functions import functions
import streamlit as st


class Help:
    """
    Classe com métodos que fornecem ajuda ao usuário.
    """

    def generate_function_description(self, selected_function):
        """
        Elabora o resumo sobre a funcionalidade sobre a qual o usuário tem dúvida.

        Parameters
        ----------
        selected_function : Any
            Função selecionada pelo usuário.

        Returns
        -------
        response_description : A descrição da função.
        response_graphic : O gráfico descritivo da função.
        """
        info = functions.get(selected_function.lower(), "Funcionalidade não encontrada.")
        response_description = functions[selected_function]

        return response_description
    
    @st.dialog(title="Ajuda")
    def main_menu(self):
        """
        Menu principal.
        """
        selected_function = st.selectbox(label="Opções", options=functions.keys())
        description = self.generate_function_description(selected_function)
    
        st.markdown(body=description)