"""
Testes de lógica para o módulo de membros.

Este módulo testa a lógica interna da funcionalidade de membros
sem depender da interface web ou API externa.
"""

import sys
import os
from unittest.mock import Mock, patch

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestMembersLogic:
    """Testes da lógica interna da página de membros."""

    def setup_method(self):
        """Configuração para cada teste."""
        # Mock do Streamlit
        self.mock_st = Mock()

        # Mock das dependências
        self.mock_auth = Mock()
        self.mock_api_client = Mock()
        self.mock_ui_components = Mock()
        self.mock_messages = Mock()
        self.mock_validation = Mock()

    @patch('pages.members.st')
    @patch('pages.members.require_auth')
    @patch('pages.members.api_client')
    @patch('pages.members.ui_components')
    @patch('pages.members.messages')
    @patch('pages.members.validation')
    def test_members_page_initialization(self, mock_validation, mock_messages,
                                         mock_ui_components, mock_api_client,
                                         mock_require_auth, mock_st):
        """Testa a inicialização da página de membros."""
        from pages.members import MembersPage

        # Configura mocks
        mock_require_auth.return_value = Mock()

        # Cria instância
        page = MembersPage()

        # Verifica se require_auth foi chamado
        mock_require_auth.assert_called_once()

        # Verifica se a instância foi criada corretamente
        assert page.auth is not None

    def test_get_member_type(self):
        """Testa a função _get_member_type."""
        from pages.members import MembersPage

        with patch('pages.members.require_auth') as mock_auth:
            mock_auth.return_value = Mock()
            page = MembersPage()

            # Testa membro regular
            member_regular = {'is_creditor': False, 'is_benefited': False}
            assert page._get_member_type(member_regular) == 'Regular'

            # Testa credor
            member_creditor = {'is_creditor': True, 'is_benefited': False}
            assert page._get_member_type(member_creditor) == 'Credor'

            # Testa beneficiário
            member_benefited = {'is_creditor': False, 'is_benefited': True}
            assert page._get_member_type(member_benefited) == 'Beneficiário'

            # Testa credor e beneficiário
            member_both = {'is_creditor': True, 'is_benefited': True}
            assert page._get_member_type(member_both) == 'Credor, Beneficiário'

    def test_format_date(self):
        """Testa a formatação de datas."""
        from pages.members import MembersPage

        with patch('pages.members.require_auth') as mock_auth:
            mock_auth.return_value = Mock()
            page = MembersPage()

            # Testa data None
            assert page._format_date(None) == 'Não informado'

            # Testa string vazia
            assert page._format_date('') == 'Não informado'

            # Testa data válida ISO
            iso_date = '2023-12-15T10:30:00Z'
            formatted = page._format_date(iso_date)
            assert '15/12/2023' in formatted
            assert '10:30' in formatted

            # Testa data inválida (deve retornar a string original)
            invalid_date = 'data inválida'
            assert page._format_date(invalid_date) == invalid_date

    @patch('pages.members.pd.DataFrame')
    def test_members_to_dataframe(self, mock_dataframe):
        """Testa a conversão de membros para DataFrame."""
        from pages.members import MembersPage

        with patch('pages.members.require_auth') as mock_auth:
            mock_auth.return_value = Mock()
            page = MembersPage()

            # Mock dos dados de entrada
            members = [
                {
                    'name': 'João Silva',
                    'document': '123.456.789-00',
                    'email': 'joao@email.com',
                    'phone': '(11) 99999-9999',
                    'is_creditor': True,
                    'is_benefited': False,
                    'active': True,
                    'created_at': '2023-12-15T10:30:00Z'
                },
                {
                    'name': 'Maria Santos',
                    'document': '987.654.321-00',
                    'email': None,
                    'phone': None,
                    'is_creditor': False,
                    'is_benefited': True,
                    'active': False,
                    'created_at': '2023-12-14T15:45:00Z'
                }
            ]

            # Executa a função
            page._members_to_dataframe(members)

            # Verifica se DataFrame foi chamado com os dados corretos
            mock_dataframe.assert_called_once()
            call_args = mock_dataframe.call_args[0][0]

            # Verifica primeiro membro
            assert call_args[0]['Nome'] == 'João Silva'
            assert call_args[0]['Documento'] == '123.456.789-00'
            assert call_args[0]['Email'] == 'joao@email.com'
            assert call_args[0]['Tipo'] == 'Credor'
            assert call_args[0]['Status'] == '✅ Ativo'

            # Verifica segundo membro
            assert call_args[1]['Nome'] == 'Maria Santos'
            assert call_args[1]['Email'] == 'Não informado'
            assert call_args[1]['Telefone'] == 'Não informado'
            assert call_args[1]['Tipo'] == 'Beneficiário'
            assert call_args[1]['Status'] == '❌ Inativo'

    def test_validate_member_data(self):
        """Testa validação de dados de membro."""
        from pages.members import MembersPage

        with patch('pages.members.require_auth') as mock_auth:
            with patch('pages.members.validation') as mock_validation:
                with patch('pages.members.st'):
                    mock_auth.return_value = Mock()
                    page = MembersPage()

                    # Configura mock de validação
                    mock_validation.validate_required_fields.return_value = (
                        None
                    )
                    mock_validation.validate_document.return_value = None
                    mock_validation.validate_email.return_value = None

                    # Mock da API
                    with patch('pages.members.api_client') as mock_api:
                        mock_api.post.return_value = {'id': 1}

                        # Dados válidos
                        valid_data = {
                            'name': 'João Silva',
                            'document': '123.456.789-00',
                            'email': 'joao@email.com',
                            'phone': '(11) 99999-9999',
                            'is_creditor': False,
                            'is_benefited': False,
                            'active': True
                        }

                        # Executa processamento
                        page._process_add_member(valid_data)

                        # Verifica se validações foram chamadas
                        mock_validation.validate_required_fields.\
                            assert_called_once()
                        mock_validation.validate_document.\
                            assert_called_once_with('123.456.789-00')
                        mock_validation.validate_email.\
                            assert_called_once_with('joao@email.com')

                        # Verifica se API foi chamada
                        mock_api.post.assert_called_once_with(
                            'members/', valid_data)


def test_import_members_page():
    """Testa se a página de membros pode ser importada sem erros."""
    try:
        from pages.members import MembersPage, main
        assert MembersPage is not None
        assert main is not None
        print("✅ Página de membros importada com sucesso")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar página de membros: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral na importação: {e}")
        return False


def test_members_page_structure():
    """Testa a estrutura básica da classe MembersPage."""
    with patch('pages.members.require_auth'):
        from pages.members import MembersPage

        # Verifica se a classe tem os métodos esperados
        expected_methods = [
            'render',
            '_render_members_list',
            '_render_add_member_form',
            '_render_manage_members',
            '_fetch_members',
            '_members_to_dataframe',
            '_get_member_type',
            '_format_date',
            '_process_add_member',
            '_process_update_member',
            '_process_delete_member'
        ]

        for method_name in expected_methods:
            assert hasattr(
                MembersPage, method_name
            ), f"Método {method_name} não encontrado"

        print("✅ Estrutura da classe MembersPage está correta")
        return True


def run_logic_tests():
    """Executa todos os testes de lógica."""
    print("🧪 Iniciando testes de lógica para Membros...")

    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'tests': []
    }

    # Lista de testes para executar
    tests = [
        ('Importação da página', test_import_members_page),
        ('Estrutura da classe', test_members_page_structure),
    ]

    for test_name, test_func in tests:
        results['total'] += 1
        try:
            success = test_func()
            if success:
                results['passed'] += 1
                print(f"✅ {test_name}: PASSOU")
            else:
                results['failed'] += 1
                print(f"❌ {test_name}: FALHOU")

            results['tests'].append({
                'name': test_name,
                'success': success,
                'error': None
            })

        except Exception as e:
            results['failed'] += 1
            print(f"❌ {test_name}: ERRO - {e}")
            results['tests'].append({
                'name': test_name,
                'success': False,
                'error': str(e)
            })

    # Executa testes com pytest se disponível
    try:
        import pytest
        print("\n🔬 Executando testes avançados com pytest...")
        pytest_result = pytest.main([__file__, '-v'])
        if pytest_result == 0:
            print("✅ Testes avançados passaram")
        else:
            print("❌ Alguns testes avançados falharam")
    except ImportError:
        print("ℹ️  pytest não disponível, pulando testes avançados")

    # Sumário
    success_rate = (
        results['passed'] /
        results['total'] *
        100) if results['total'] > 0 else 0
    print("\n📊 RESULTADOS:")
    print(
        f"Total: {results['total']} | Passou: {results['passed']} | "
        f"Falhou: {results['failed']}"
    )
    print(f"Taxa de sucesso: {success_rate:.1f}%")

    return results


if __name__ == "__main__":
    results = run_logic_tests()
    exit(0 if results['failed'] == 0 else 1)
