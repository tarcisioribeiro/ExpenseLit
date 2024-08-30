import datetime
import streamlit as st


class GetActualTime:

    def __init__(self):

        def get_actual_time():

            now = datetime.datetime.now()
            hour = now.strftime('%H:%M:%S')
            return hour

        def show_current_time():

            actual_hour = get_actual_time()
            st.info(body="Hora atual: {}".format(actual_hour))


        self.get_actual_time = get_actual_time
        self.show_current_time = show_current_time