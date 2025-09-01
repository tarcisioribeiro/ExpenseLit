"""
Testes automatizados para interface de despesas.
Testa especificamente os erros de edição de receitas e despesas.
"""
import pytest
import asyncio
from playwright.async_api import async_playwright, Page, expect


class TestExpensesUI:
    """Testes de interface para despesas."""

    @pytest.fixture(scope="function")
    async def page(self):
        """Fixture para criar uma página do navegador."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            yield page
            await browser.close()

    async def test_expense_edit_functionality(self, page: Page):
        """
        Testa a funcionalidade de edição de despesas.
Verifica se o erro 'st.session_state.edit_expense_X cannot be modified' foi corrigido.
        """
        try:
            # Navega para a aplicação
            await page.goto("http://localhost:8501")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)  # Aguarda carregamento completo da página

            # Verifica se a página carregou
            await expect(page).to_have_title("ExpenseLit")

            # Navega para seção de despesas
            await page.click("text=💸 Despesas")
            await asyncio.sleep(2)

            # Vai para aba de despesas em conta corrente
            await page.click("text=💰 Despesas em Conta Corrente")
            await asyncio.sleep(2)

            # Vai para lista de despesas
            await page.click("text=📋 Lista de Despesas")
            await asyncio.sleep(3)

            # Procura por cards de despesas
            expense_cards = await page.query_selector_all(".element-container")

            if len(expense_cards) > 0:
                print(f"Encontradas {len(expense_cards)} despesas")

                # Procura pelo primeiro botão de ações (⚙️)
                actions_button = await page.query_selector("text=⚙️ Ações")
                if actions_button:
                    await actions_button.click()
                    await asyncio.sleep(1)

                    # Clica em editar
                    edit_button = await page.query_selector("text=✏️ Editar")
                    if edit_button:
                        await edit_button.click()
                        await asyncio.sleep(2)

                        # Verifica se não há erros de session_state
error_elements = await page.query_selector_all(
    ".stException")
                        errors = []
                        for error_elem in error_elements:
                            error_text = await error_elem.inner_text()
if "cannot be modified after the widget" in error_text:
                                errors.append(error_text)

                        if errors:
                            print("❌ ERRO ENCONTRADO:")
                            for error in errors:
                                print(f"  - {error}")
                            return False
                        else:
                            print("✅ Nenhum erro de session_state encontrado")
                            return True
                    else:
                        print("⚠️ Botão de editar não encontrado")
                        return None
                else:
                    print("⚠️ Botão de ações não encontrado")
                    return None
            else:
                print("ℹ️ Nenhuma despesa encontrada para testar")
                return None

        except Exception as e:
            print(f"❌ ERRO NO TESTE: {str(e)}")
            return False

    async def test_revenue_edit_functionality(self, page: Page):
        """
        Testa a funcionalidade de edição de receitas.
Verifica se o erro 'st.session_state.edit_revenue_X cannot be modified' foi corrigido.
        """
        try:
            # Navega para a aplicação
            await page.goto("http://localhost:8501")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)

            # Navega para seção de receitas
            await page.click("text=💰 Receitas")
            await asyncio.sleep(2)

            # Vai para lista de receitas (primeira aba)
            await page.click("text=📋 Minhas Receitas")
            await asyncio.sleep(3)

            # Procura por cards de receitas
            revenue_cards = await page.query_selector_all(".element-container")

            if len(revenue_cards) > 0:
                print(f"Encontradas {len(revenue_cards)} receitas")

                # Procura pelo primeiro botão de ações (⚙️)
                actions_button = await page.query_selector("text=⚙️ Ações")
                if actions_button:
                    await actions_button.click()
                    await asyncio.sleep(1)

                    # Clica em editar
                    edit_button = await page.query_selector("text=✏️ Editar")
                    if edit_button:
                        await edit_button.click()
                        await asyncio.sleep(2)

                        # Verifica se não há erros de session_state
error_elements = await page.query_selector_all(
    ".stException")
                        errors = []
                        for error_elem in error_elements:
                            error_text = await error_elem.inner_text()
if "cannot be modified after the widget" in error_text:
                                errors.append(error_text)

                        if errors:
                            print("❌ ERRO ENCONTRADO:")
                            for error in errors:
                                print(f"  - {error}")
                            return False
                        else:
                            print("✅ Nenhum erro de session_state encontrado")
                            return True
                    else:
                        print("⚠️ Botão de editar não encontrado")
                        return None
                else:
                    print("⚠️ Botão de ações não encontrado")
                    return None
            else:
                print("ℹ️ Nenhuma receita encontrada para testar")
                return None

        except Exception as e:
            print(f"❌ ERRO NO TESTE: {str(e)}")
            return False

    async def test_navigation_and_loading(self, page: Page):
        """Testa navegação básica e carregamento das páginas."""
        try:
            await page.goto("http://localhost:8501")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)

            # Testa navegação para diferentes seções
            sections = [
                "💰 Receitas",
                "💸 Despesas",
                "💳 Cartões de Crédito",
                "📊 Dashboard"
            ]

            results = {}

            for section in sections:
                try:
                    await page.click(f"text={section}")
                    await asyncio.sleep(2)

                    # Verifica se há erros de exceção
error_elements = await page.query_selector_all(
    ".stException")
                    if error_elements:
                        errors = []
                        for elem in error_elements:
                            errors.append(await elem.inner_text())
                        results[section] = {"status": "erro", "errors": errors}
                    else:
                        results[section] = {"status": "ok", "errors": []}

                except Exception as e:
                    results[section] = {"status": "erro", "errors": [str(e)]}

            return results

        except Exception as e:
            print(f"❌ ERRO NO TESTE DE NAVEGAÇÃO: {str(e)}")
            return {"error": str(e)}


async def run_tests():
    """Executa os testes e gera relatório."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        test_instance = TestExpensesUI()

        print("🧪 INICIANDO TESTES AUTOMATIZADOS")
        print("=" * 50)

        # Teste 1: Navegação básica
        print("\n1. Testando navegação básica...")
        nav_results = await test_instance.test_navigation_and_loading(page)

        # Teste 2: Edição de despesas
        print("\n2. Testando edição de despesas...")
expense_result = await test_instance. \
    test_expense_edit_functionality(page)

        # Teste 3: Edição de receitas
        print("\n3. Testando edição de receitas...")
revenue_result = await test_instance. \
    test_revenue_edit_functionality(page)

        await browser.close()

        # Gera relatório
        return {
            "navigation": nav_results,
            "expense_edit": expense_result,
            "revenue_edit": revenue_result
        }


if __name__ == "__main__":
    results = asyncio.run(run_tests())

    print("\n" + "=" * 50)
    print("📋 RELATÓRIO FINAL")
    print("=" * 50)

    # Salva resultados em error.txt
    with open("/home/tarcisio/Development/ExpenseLit/error.txt", "w") as f:
        f.write("RELATÓRIO DE TESTES AUTOMATIZADOS - ExpenseLit\n")
        f.write("=" * 50 + "\n\n")

        # Resultados de navegação
        f.write("1. TESTE DE NAVEGAÇÃO:\n")
        if "error" in results["navigation"]:
            f.write(f"❌ ERRO CRÍTICO: {results['navigation']['error']}\n")
        else:
            for section, result in results["navigation"].items():
                if result["status"] == "ok":
                    f.write(f"✅ {section}: OK\n")
                else:
                    f.write(f"❌ {section}: ERRO\n")
                    for error in result["errors"]:
                        f.write(f"   - {error}\n")

        f.write("\n2. TESTE DE EDIÇÃO DE DESPESAS:\n")
        if results["expense_edit"] is True:
            f.write("✅ Edição de despesas funcionando corretamente\n")
        elif results["expense_edit"] is False:
            f.write("❌ ERRO: Problema na edição de despesas\n")
        elif results["expense_edit"] is None:
f.write(
    "⚠️ AVISO: Não foi possível testar - nenhuma despesa encontrada\n")

        f.write("\n3. TESTE DE EDIÇÃO DE RECEITAS:\n")
        if results["revenue_edit"] is True:
            f.write("✅ Edição de receitas funcionando corretamente\n")
        elif results["revenue_edit"] is False:
            f.write("❌ ERRO: Problema na edição de receitas\n")
        elif results["revenue_edit"] is None:
f.write(
    "⚠️ AVISO: Não foi possível testar - nenhuma receita encontrada\n")

        f.write(f"\nTeste executado em: {asyncio.get_event_loop().time()}\n")

    print("📄 Resultados salvos em error.txt")
