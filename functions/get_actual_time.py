import datetime
import streamlit as st


class GetActualTime:

    def get_actual_time(self):

        now = datetime.datetime.now()
        hour = now.strftime('%H:%M:%S')
        return hour

    def show_current_time(self):

        actual_hour = self.get_actual_time()
        st.info(body="Hora atual: {}".format(actual_hour))
