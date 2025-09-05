"""
Serviço de conexão e consulta ao banco de dados PostgreSQL.

Este módulo fornece uma classe para conectar-se ao banco PostgreSQL local
e realizar consultas, salvando resultados em arquivos markdown na pasta .data.
"""

import os
import psycopg2
from datetime import datetime
from typing import List, Dict, Any, Optional
from psycopg2.extras import RealDictCursor
from dictionary.db_config import db_config


class DatabaseConnection:
    """
    Classe para gerenciar conexão e consultas ao banco PostgreSQL.

    Esta classe permite conectar-se ao banco de dados PostgreSQL usando as
    configurações do arquivo dictionary/db_config.py e realizar consultas,
    armazenando os resultados em arquivos markdown na pasta .data.
    """

    def __init__(self) -> None:
        """
        Inicializa a classe DatabaseConnection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.connection: Optional[psycopg2.extensions.connection] = None
        self.cursor: Optional[psycopg2.extras.RealDictCursor] = None

    def connect(self) -> bool:
        """
        Estabelece conexão com o banco de dados PostgreSQL.

        Utiliza as configurações do arquivo dictionary/db_config.py para
        estabelecer a conexão com o banco PostgreSQL.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            True se a conexão estabelecida com sucesso, False caso contrário.

        Raises
        ------
        psycopg2.Error
            Em caso de erro na conexão com o banco.
        """
        try:
            self.connection = psycopg2.connect(
                host=db_config["host"],
                port=db_config["port"],
                user=db_config["user"],
                password=db_config["password"],
                database=db_config["database"]
            )
            self.cursor = self.connection.cursor(
                cursor_factory=RealDictCursor
            )
            return True
        except psycopg2.Error as error:
            print(f"Erro ao conectar com o banco de dados: {error}")
            return False

    def disconnect(self) -> None:
        """
        Fecha a conexão com o banco de dados.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str,
                      params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Executa uma consulta SQL e retorna os resultados.

        Parameters
        ----------
        query : str
            Consulta SQL a ser executada.
        params : tuple, optional
            Parâmetros para a consulta SQL.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de dicionários com os resultados da consulta.

        Raises
        ------
        psycopg2.Error
            Em caso de erro na execução da consulta.
        """
        try:
            if not self.cursor:
                raise psycopg2.Error("Conexão não estabelecida")

            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except psycopg2.Error as error:
            print(f"Erro ao executar consulta: {error}")
            return []

    def save_results_to_markdown(self, results: List[Dict[str, Any]],
                                 filename: str, query: str) -> bool:
        """
        Salva os resultados da consulta em arquivo markdown na pasta .data.

        Parameters
        ----------
        results : List[Dict[str, Any]]
            Resultados da consulta a serem salvos.
        filename : str
            Nome do arquivo (sem extensão) onde salvar os resultados.
        query : str
            Consulta SQL original para documentação.

        Returns
        -------
        bool
            True se resultados salvos com sucesso, False caso contrário.
        """
        try:
            # Garantir que o diretório .data existe
            os.makedirs('.data', exist_ok=True)

            # Criar o arquivo markdown
            filepath = f".data/{filename}.md"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(f"# Resultados da Consulta - {filename}\n\n")
                file.write(f"**Data de execução:** {timestamp}\n\n")
                file.write("**Consulta executada:**\n")
                file.write(f"```sql\n{query}\n```\n\n")
                file.write(f"**Total de registros:** {len(results)}\n\n")

                if results:
                    file.write("## Resultados\n\n")

                    # Criar cabeçalho da tabela
                    headers = list(results[0].keys())
                    file.write("| " + " | ".join(headers) + " |\n")
                    sep = "| " + " | ".join(["---"] * len(headers)) + " |\n"
                    file.write(sep)

                    # Adicionar dados
                    for row in results:
                        values = [str(row.get(header, ""))
                                  for header in headers]
                        file.write("| " + " | ".join(values) + " |\n")
                else:
                    file.write("## Resultados\n\n")
                    file.write("Nenhum resultado encontrado.\n")

            print(f"Resultados salvos em: {filepath}")
            return True

        except Exception as error:
            print(f"Erro ao salvar resultados: {error}")
            return False

    def query_and_save(self, query: str, filename: str,
                       params: Optional[tuple] = None) -> bool:
        """
        Executa uma consulta e salva os resultados em markdown.

        Método de conveniência que combina execução da consulta e
        salvamento dos resultados em um único método.

        Parameters
        ----------
        query : str
            Consulta SQL a ser executada.
        filename : str
            Nome do arquivo (sem extensão) onde salvar os resultados.
        params : tuple, optional
            Parâmetros para a consulta SQL.

        Returns
        -------
        bool
            True se a operação foi bem-sucedida, False caso contrário.
        """
        if not self.connect():
            return False

        try:
            results = self.execute_query(query, params)
            success = self.save_results_to_markdown(results, filename, query)
            return success
        finally:
            self.disconnect()

    def get_table_info(self, table_name: str) -> bool:
        """
        Obtém informações sobre uma tabela específica e salva em markdown.

        Parameters
        ----------
        table_name : str
            Nome da tabela para análise.

        Returns
        -------
        bool
            True se a operação foi bem-sucedida, False caso contrário.
        """
        query = """
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
        """

        return self.query_and_save(
            query,
            f"table_info_{table_name}",
            (table_name,)
        )

    def get_table_stats(self, table_name: str) -> bool:
        """
        Obtém estatísticas básicas de uma tabela e salva em markdown.

        Parameters
        ----------
        table_name : str
            Nome da tabela para análise estatística.

        Returns
        -------
        bool
            True se a operação foi bem-sucedida, False caso contrário.
        """
        query = f"""
        SELECT
            COUNT(*) as total_records,
            COUNT(*) FILTER (
                WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
            ) as records_last_30_days,
            MIN(created_at) as oldest_record,
            MAX(created_at) as newest_record
        FROM {table_name}
        WHERE created_at IS NOT NULL;
        """

        return self.query_and_save(
            query,
            f"table_stats_{table_name}",
            ()
        )
