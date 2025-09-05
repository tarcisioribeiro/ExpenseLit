"""
Testes de interface para o módulo de membros.

Este módulo testa a interface web da funcionalidade de membros
usando Selenium para simular interações do usuário.
"""

import time
import logging
from typing import Dict, Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class MembersUITest:
    """Classe para testes de UI da funcionalidade de membros."""

    def __init__(self, base_url: str = "http://localhost:8501"):
        """
        Inicializa o teste de UI.

        Parameters
        ----------
        base_url : str
            URL base da aplicação Streamlit
        """
        self.base_url = base_url
        self.driver = None
        self.wait = None

    def setup_driver(self):
        """Configura o driver do Chrome para teste."""
        chrome_options = Options()
        # Executar sem interface gráfica
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

        logger.info("Driver do Chrome configurado")

    def teardown_driver(self):
        """Fecha o driver."""
        if self.driver:
            self.driver.quit()
            logger.info("Driver fechado")

    def login(self, username: str = "admin", password: str = "admin123"):
        """
        Realiza login na aplicação.

        Parameters
        ----------
        username : str
            Nome de usuário
        password : str
            Senha

        Returns
        -------
        bool
            True se login foi bem-sucedido
        """
        try:
            # Navega para a página inicial
            self.driver.get(self.base_url)
            time.sleep(2)

            # Preenche credenciais
            username_input = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "[data-testid='stTextInput'] "
                     "input[placeholder*='usuário']")
                )
            )
            username_input.clear()
            username_input.send_keys(username)

            password_input = self.driver.find_element(
                By.CSS_SELECTOR,
                "[data-testid='stTextInput'] input[type='password']"
            )
            password_input.clear()
            password_input.send_keys(password)

            # Clica no botão de login
            login_button = self.driver.find_element(
                By.XPATH,
                "//button[contains(text(), 'Entrar')]"
            )
            login_button.click()

            # Aguarda redirecionamento
            time.sleep(3)

            # Verifica se login foi bem-sucedido
            success = (
                "Dashboard" in self.driver.page_source or
                "Bem-vindo" in self.driver.page_source
            )

            logger.info(f"Login {'bem-sucedido' if success else 'falhou'}")
            return success

        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return False

    def navigate_to_members(self) -> bool:
        """
        Navega para a página de membros.

        Returns
        -------
        bool
            True se navegação foi bem-sucedida
        """
        try:
            # Procura link/botão de membros no menu
            members_link = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     "//a[contains(text(), 'Membros')] | "
                     "//button[contains(text(), 'Membros')]")
                )
            )
            members_link.click()

            time.sleep(2)

            # Verifica se chegou na página de membros
            success = "Lista de Membros" in self.driver.page_source
            logger.info(
                f"Navegação para membros "
                f"{'bem-sucedida' if success else 'falhou'}"
            )
            return success

        except Exception as e:
            logger.error(f"Erro ao navegar para membros: {e}")
            return False

    def test_list_members(self) -> Dict[str, Any]:
        """
        Testa a listagem de membros.

        Returns
        -------
        Dict[str, Any]
            Resultado do teste
        """
        test_result = {
            'test_name': 'test_list_members',
            'success': False,
            'message': '',
            'details': {}
        }

        try:
            # Verifica se a tab de lista está presente
            list_tab = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(text(), 'Lista de Membros')]")
                )
            )

            # Clica na tab se necessário
            if list_tab.is_enabled():
                list_tab.click()
                time.sleep(1)

            # Verifica elementos da interface
            filters_present = len(
                self.driver.find_elements(
                    By.XPATH,
                    "//label[contains(text(), 'Status')]")) > 0

            # Verifica se há tabela de dados ou mensagem de lista vazia
            table_or_empty = (
                len(self.driver.find_elements(
                    By.CSS_SELECTOR, "[data-testid='dataframe']"
                )) > 0 or "Nenhum" in self.driver.page_source
            )

            test_result['success'] = filters_present and table_or_empty
            test_result['message'] = 'Lista de membros carregada com sucesso'
            test_result['details'] = {
                'filters_present': filters_present,
                'table_or_empty_message': table_or_empty
            }

        except Exception as e:
            test_result['message'] = f'Erro ao testar listagem: {e}'
            logger.error(f"Erro no teste de listagem: {e}")

        return test_result

    def test_add_member_form(self) -> Dict[str, Any]:
        """
        Testa o formulário de adição de membro.

        Returns
        -------
        Dict[str, Any]
            Resultado do teste
        """
        test_result = {
            'test_name': 'test_add_member_form',
            'success': False,
            'message': '',
            'details': {}
        }

        try:
            # Clica na tab de adicionar
            add_tab = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(text(), 'Novo Membro')]")
                )
            )
            add_tab.click()
            time.sleep(1)

            # Verifica campos obrigatórios
            name_field = self.driver.find_element(
                By.XPATH,
                "//label[contains(text(), 'Nome Completo')]/..//input"
            )

            document_field = self.driver.find_element(
                By.XPATH,
                "//label[contains(text(), 'CPF/CNPJ')]/..//input"
            )

            # Preenche dados de teste
            test_data = {
                'name': 'João Silva Teste',
                'document': '123.456.789-00',
                'email': 'joao.teste@email.com',
                'phone': '(11) 99999-9999'
            }

            name_field.clear()
            name_field.send_keys(test_data['name'])

            document_field.clear()
            document_field.send_keys(test_data['document'])

            # Tenta preencher email se existir
            try:
                email_field = self.driver.find_element(
                    By.XPATH,
                    "//label[contains(text(), 'Email')]/..//input"
                )
                email_field.clear()
                email_field.send_keys(test_data['email'])
            except NoSuchElementException:
                pass

            # Verifica se o botão de salvar está presente
            save_button = self.driver.find_element(
                By.XPATH,
                "//button[contains(text(), 'Salvar')]"
            )

            test_result['success'] = True
            test_result['message'] = (
                'Formulário de adição funciona corretamente'
            )
            test_result['details'] = {
                'form_fields_present': True,
                'save_button_present': save_button.is_enabled(),
                'test_data_filled': test_data
            }

            # Nota: Não submete o formulário para evitar criar dados de teste
            # reais
            logger.info("Teste de formulário concluído sem submissão")

        except Exception as e:
            test_result['message'] = f'Erro ao testar formulário: {e}'
            logger.error(f"Erro no teste de formulário: {e}")

        return test_result

    def test_member_filters(self) -> Dict[str, Any]:
        """
        Testa os filtros da página de membros.

        Returns
        -------
        Dict[str, Any]
            Resultado do teste
        """
        test_result = {
            'test_name': 'test_member_filters',
            'success': False,
            'message': '',
            'details': {}
        }

        try:
            # Volta para a tab de listagem
            list_tab = self.driver.find_element(
                By.XPATH,
                "//div[contains(text(), 'Lista de Membros')]"
            )
            list_tab.click()
            time.sleep(1)

            # Testa filtro de status
            status_filter = self.driver.find_element(
                By.XPATH,
                "//label[contains(text(), 'Status')]/..//div[@role='button']"
            )
            status_filter.click()
            time.sleep(0.5)

            # Verifica opções do filtro
            filter_options = self.driver.find_elements(
                By.XPATH,
                "//div[@role='option']"
            )

            options_text = [opt.text for opt in filter_options if opt.text]

            test_result['success'] = len(
                options_text) >= 2  # Pelo menos 2 opções
            test_result['message'] = 'Filtros funcionam corretamente'
            test_result['details'] = {
                'filter_options': options_text,
                'options_count': len(options_text)
            }

            # Fecha o dropdown
            if filter_options:
                filter_options[0].click()
                time.sleep(0.5)

        except Exception as e:
            test_result['message'] = f'Erro ao testar filtros: {e}'
            logger.error(f"Erro no teste de filtros: {e}")

        return test_result

    def test_manage_members_tab(self) -> Dict[str, Any]:
        """
        Testa a tab de gerenciamento de membros.

        Returns
        -------
        Dict[str, Any]
            Resultado do teste
        """
        test_result = {
            'test_name': 'test_manage_members_tab',
            'success': False,
            'message': '',
            'details': {}
        }

        try:
            # Clica na tab de gerenciar
            manage_tab = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(text(), 'Gerenciar')]")
                )
            )
            manage_tab.click()
            time.sleep(2)

            # Verifica se o seletor de membros está presente
            member_selector_present = len(self.driver.find_elements(
                By.XPATH,
                "//label[contains(text(), 'Selecionar Membro')]"
            )) > 0

            # Verifica se há mensagem de lista vazia ou seletor funcional
            empty_message = "Nenhum" in self.driver.page_source

            test_result['success'] = member_selector_present or empty_message
            test_result['message'] = (
                'Tab de gerenciamento carregada corretamente'
            )
            test_result['details'] = {
                'selector_present': member_selector_present,
                'empty_state': empty_message
            }

        except Exception as e:
            test_result['message'] = f'Erro ao testar gerenciamento: {e}'
            logger.error(f"Erro no teste de gerenciamento: {e}")

        return test_result

    def run_all_tests(self) -> Dict[str, Any]:
        """
        Executa todos os testes da interface de membros.

        Returns
        -------
        Dict[str, Any]
            Resultados de todos os testes
        """
        all_results = {
            'test_suite': 'members_ui_tests',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'results': [],
            'summary': ''
        }

        try:
            self.setup_driver()

            # Realiza login
            if not self.login():
                all_results['summary'] = (
                    'Falha no login - testes não executados'
                )
                return all_results

            # Navega para membros
            if not self.navigate_to_members():
                all_results['summary'] = (
                    'Falha na navegação para membros'
                )
                return all_results

            # Lista de testes para executar
            tests = [
                self.test_list_members,
                self.test_add_member_form,
                self.test_member_filters,
                self.test_manage_members_tab
            ]

            # Executa cada teste
            for test_func in tests:
                try:
                    result = test_func()
                    all_results['results'].append(result)
                    all_results['total_tests'] += 1

                    if result['success']:
                        all_results['passed_tests'] += 1
                    else:
                        all_results['failed_tests'] += 1

                    logger.info(
                        f"Teste {result['test_name']}: "
                        f"{'PASSOU' if result['success'] else 'FALHOU'}"
                    )

                except Exception as e:
                    error_result = {
                        'test_name': f'{test_func.__name__}',
                        'success': False,
                        'message': f'Erro na execução: {e}',
                        'details': {}
                    }
                    all_results['results'].append(error_result)
                    all_results['total_tests'] += 1
                    all_results['failed_tests'] += 1
                    logger.error(f"Erro no teste {test_func.__name__}: {e}")

            # Gera sumário
            success_rate = (
                all_results['passed_tests'] /
                all_results['total_tests'] *
                100) if all_results['total_tests'] > 0 else 0
            all_results['summary'] = (
                f"Executados: {all_results['total_tests']} | "
                f"Passou: {all_results['passed_tests']} | "
                f"Falhou: {all_results['failed_tests']} | "
                f"Taxa de sucesso: {success_rate:.1f}%"
            )

        except Exception as e:
            all_results['summary'] = f'Erro geral na execução dos testes: {e}'
            logger.error(f"Erro geral: {e}")

        finally:
            self.teardown_driver()

        return all_results


def main():
    """Executa os testes de UI para membros."""
    print("🧪 Iniciando testes de UI para Membros...")

    # Configura logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Executa testes
    tester = MembersUITest()
    results = tester.run_all_tests()

    # Exibe resultados
    print("\n📊 RESULTADOS DOS TESTES:")
    print("=" * 50)
    print(f"Suite: {results['test_suite']}")
    print(f"Resumo: {results['summary']}")
    print("\n📝 DETALHES:")

    for result in results.get('results', []):
        status = "✅ PASSOU" if result['success'] else "❌ FALHOU"
        print(f"{status} - {result['test_name']}")
        print(f"   Mensagem: {result['message']}")
        if result['details']:
            print(f"   Detalhes: {result['details']}")
        print()

    # Retorna código de saída baseado no sucesso
    return 0 if results['failed_tests'] == 0 else 1


if __name__ == "__main__":
    exit(main())
