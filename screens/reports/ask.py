import re
import streamlit as st
import mysql.connector
from functions.login import Login
from openai import OpenAI
from chromadb import PersistentClient
from dictionary.context import SCHEMA_DESCRIPTION, sql_prompt, response_prompt
from dictionary.db_config import api_key, db_config


class SQLChatBot:
    def __init__(self):

        self.user_id, self.user_document = Login().get_user_data()

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )

        self.chroma_client = PersistentClient(path="./chroma")
        self.collection = self.chroma_client.get_or_create_collection(
            name="consultas_financas"
        )

        if "history" not in st.session_state:
            st.session_state.history = []

    def generate_sql(self, question: str) -> str:
        formatted_sql_prompt = sql_prompt.format(
            self.user_id,
            self.user_document,
            question,
            SCHEMA_DESCRIPTION
        )

        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "user",
                        "content": formatted_sql_prompt
                    }
                ],
                temperature=0
            )
            sql = response.choices[0].message.content
            return re.sub(r"```.*?\n", "", sql).strip().replace("```", "")  # type: ignore
        except Exception as e:
            return f"ERRO_SQL_GENERATION: {e}"

    def execute_query(self, sql: str) -> tuple:
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            columns = cursor.column_names  # type: ignore
            cursor.close()
            conn.close()
            return columns, data
        except Exception as e:
            raise RuntimeError(f"Erro na execução do SQL: {e}")

    def generate_natural_language_response(
            self,
            question: str,
            sql: str,
            columns: list,
            data: list
            ) -> str:
        if not data:
            return "Nenhum dado foi encontrado com base na sua pergunta."

        preview = "\n".join(
            [", ".join(
                f"{col}: {val}" for col, val in zip(columns, row)
            ) for row in data[:5]]
        )

        formatted_response_prompt = response_prompt.format(
            question,
            sql,
            preview
        )

        try:
            response = self.client.chat.completions.create(
                model="gemma2-9b-it",
                messages=[
                    {
                        "role": "user",
                        "content": formatted_response_prompt
                    }
                ],
                temperature=0
            )
            return response.choices[0].message.content.strip()  # type: ignore
        except Exception as e:
            return f"Erro ao gerar explicação: {e}"

    def main_menu(self):

        col1, col2, col3 = st.columns(3)

        with col2:

            for item in st.session_state.history:
                with st.chat_message("user"):
                    st.markdown(item["answer"])
                with st.chat_message("assistant"):
                    st.markdown(item["response"])

            user_input = st.chat_input("Digite sua pergunta...")

            if user_input:
                with st.chat_message("user"):
                    st.markdown(user_input)

                with st.chat_message("assistant"):
                    with st.spinner(
                        text="""
                        Analisando sua pergunta e gerando resposta...
                        """
                    ):
                        sql = self.generate_sql(user_input)

                        if not sql or "erro" in sql.lower():
                            response = (
                                "Não consegui interpretar sua pergunta.\n"
                                "Poderia reformular ou fornecer mais detalhes?"
                            )
                            st.warning(response)
                            st.session_state.history.append({
                                "answer": user_input,
                                "response": response,
                                "sql": ""
                            })
                            return

                        try:
                            columns, data = self.execute_query(sql)
                            response = self.generate_natural_language_response(
                                user_input, sql, columns, data
                            )

                            st.info(response)

                            st.session_state.history.append({
                                "answer": user_input,
                                "response": response,
                                "sql": sql
                            })

                            self.collection.add(
                                documents=[response],
                                metadatas=[{"sql": sql}],
                                ids=[f"id_{len(st.session_state.history)}"]
                            )

                        except Exception as e:
                            error = f"Erro ao executar a consulta: {e}"
                            st.error(error)
                            st.session_state.history.append({
                                "answer": user_input,
                                "response": error,
                                "sql": sql
                            })
