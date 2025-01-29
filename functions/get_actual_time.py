import datetime
import streamlit as st


class GetActualTime:
    """
    Classe com métodos para exibição e consulta da hora atual.
    """

    def get_actual_time(self):
        """
        Conuslta o horárrio atual.

        Returns
        -------
        hour : str
            A hora atual.
        """

        now = datetime.datetime.now()
        hour = now.strftime('%H:%M:%S')
        return hour

    def show_current_time(self):
        """
        Exibe a hora atual.
        """

        actual_hour = self.get_actual_time()
        st.info(body="Hora atual: {}".format(actual_hour))
