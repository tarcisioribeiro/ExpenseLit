import datetime
import streamlit as st


class GetActualTime:
    """
    Classe responsável por obter e mostrar o horário atual.

    Attributes
    ----------
    get_actual_time()
        Obtem o horário atual.
    show_current_time()
        Mostra o horário atual.
    """

    def get_actual_time(self):
        """
        Obtem o horário atual.

        Returns
        -------
        hour: str
            A cadeia de caracteres que representam o horário atual.
        """

        now = datetime.datetime.now()
        hour = now.strftime("%H:%M:%S")
        return hour

    def show_current_time(self):
        """
        Mostra o horário atual.
        """

        actual_hour = self.get_actual_time()
        st.info(body="Hora atual: {}".format(actual_hour))
