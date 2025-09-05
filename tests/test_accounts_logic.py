"""
Testes de lógica para o módulo de contas.

Este módulo testa a lógica interna da funcionalidade de contas
sem depender da interface web ou API externa.
"""

import sys
import os
from unittest.mock import Mock, patch

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_import_accounts_page():
    """Testa se a página de contas pode ser importada sem erros."""
    try:
        from pages.accounts import AccountsPage, main
        assert AccountsPage is not None
        assert main is not None
        print("✅ Página de contas importada com sucesso")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar página de contas: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral na importação: {e}")
        return False


def test_accounts_page_structure():
    """Testa a estrutura básica da classe AccountsPage."""
    with patch('pages.accounts.require_auth'):
        from pages.accounts import AccountsPage

        # Verifica se a classe tem os métodos esperados
        expected_methods = [
            'render',
            '_render_accounts_list',
            '_render_add_account_form',
            '_render_manage_accounts',
            '_fetch_accounts',
            '_accounts_to_dataframe',
            '_get_account_type_display',
            '_get_owner_name',
            '_format_date',
            '_process_add_account',
            '_process_update_account',
            '_process_delete_account'
        ]

        for method_name in expected_methods:
            assert hasattr(
                AccountsPage, method_name
            ), f"Método {method_name} não encontrado"

        print("✅ Estrutura da classe AccountsPage está correta")
        return True


def test_account_type_display():
    """Testa a função de exibição de tipos de conta."""
    from pages.accounts import AccountsPage

    with patch('pages.accounts.require_auth') as mock_auth:
        mock_auth.return_value = Mock()
        page = AccountsPage()

        # Testa mapeamento de tipos
        assert page._get_account_type_display('corrente') == 'Conta Corrente'
        assert page._get_account_type_display('poupanca') == 'Poupança'
        assert page._get_account_type_display('investimento') == 'Investimento'
        assert page._get_account_type_display('outro') == 'Outro'
        assert page._get_account_type_display('invalido') == 'invalido'
        assert page._get_account_type_display(None) == 'N/A'

        print("✅ Função de tipo de conta funciona corretamente")
        return True


def test_owner_name_extraction():
    """Testa extração do nome do proprietário."""
    from pages.accounts import AccountsPage

    with patch('pages.accounts.require_auth') as mock_auth:
        mock_auth.return_value = Mock()
        page = AccountsPage()

        # Testa com proprietário válido
        account_with_owner = {
            'owner': {
                'name': 'João Silva',
                'document': '123.456.789-00'
            }
        }
        assert page._get_owner_name(account_with_owner) == 'João Silva'

        # Testa sem proprietário
        account_without_owner = {}
        assert page._get_owner_name(account_without_owner) == 'N/A'

        # Testa com proprietário inválido
        account_invalid_owner = {'owner': None}
        assert page._get_owner_name(account_invalid_owner) == 'N/A'

        print("✅ Extração de nome do proprietário funciona corretamente")
        return True


def test_accounts_to_dataframe():
    """Testa conversão de contas para DataFrame."""
    from pages.accounts import AccountsPage

    with patch('pages.accounts.require_auth') as mock_auth:
        with patch('pages.accounts.pd.DataFrame') as mock_dataframe:
            mock_auth.return_value = Mock()
            page = AccountsPage()

            # Mock de contas
            accounts = [
                {
                    'name': 'Conta Corrente Itaú',
                    'account_type': 'corrente',
                    'bank_code': '341',
                    'agency': '1234',
                    'current_balance': 1500.75,
                    'is_active': True,
                    'owner': {'name': 'João Silva'},
                    'created_at': '2023-12-15T10:30:00Z'
                },
                {
                    'name': 'Poupança Bradesco',
                    'account_type': 'poupanca',
                    'bank_code': '237',
                    'agency': None,
                    'current_balance': 850.00,
                    'is_active': False,
                    'owner': None,
                    'created_at': '2023-12-10T15:45:00Z'
                }
            ]

            # Executa a conversão
            page._accounts_to_dataframe(accounts)

            # Verifica se DataFrame foi chamado
            mock_dataframe.assert_called_once()
            call_args = mock_dataframe.call_args[0][0]

            # Verifica dados da primeira conta
            assert call_args[0]['Nome'] == 'Conta Corrente Itaú'
            assert call_args[0]['Tipo'] == 'Conta Corrente'
            assert call_args[0]['Banco'] == '341'
            assert call_args[0]['Saldo Atual'] == 1500.75
            assert call_args[0]['Status'] == '✅ Ativa'
            assert call_args[0]['Proprietário'] == 'João Silva'

            # Verifica dados da segunda conta
            assert call_args[1]['Nome'] == 'Poupança Bradesco'
            assert call_args[1]['Tipo'] == 'Poupança'
            assert call_args[1]['Agência'] == 'N/A'
            assert call_args[1]['Status'] == '❌ Inativa'
            assert call_args[1]['Proprietário'] == 'N/A'

            print("✅ Conversão para DataFrame funciona corretamente")
            return True


def test_date_formatting():
    """Testa formatação de datas."""
    from pages.accounts import AccountsPage

    with patch('pages.accounts.require_auth') as mock_auth:
        mock_auth.return_value = Mock()
        page = AccountsPage()

        # Testa data None
        assert page._format_date(None) == 'Não informado'

        # Testa string vazia
        assert page._format_date('') == 'Não informado'

        # Testa data válida ISO
        iso_date = '2023-12-15T10:30:00Z'
        formatted = page._format_date(iso_date)
        assert '15/12/2023' in formatted
        assert '10:30' in formatted

        # Testa data inválida
        invalid_date = 'data inválida'
        assert page._format_date(invalid_date) == invalid_date

        print("✅ Formatação de data funciona corretamente")
        return True


def run_accounts_tests():
    """Executa todos os testes da página de contas."""
    print("🧪 Iniciando testes de lógica para Contas...")

    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'tests': []
    }

    # Lista de testes
    tests = [
        ('Importação da página', test_import_accounts_page),
        ('Estrutura da classe', test_accounts_page_structure),
        ('Tipos de conta', test_account_type_display),
        ('Nome do proprietário', test_owner_name_extraction),
        ('Conversão para DataFrame', test_accounts_to_dataframe),
        ('Formatação de data', test_date_formatting),
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
    results = run_accounts_tests()
    exit(0 if results['failed'] == 0 else 1)
