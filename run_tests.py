#!/usr/bin/env python3
"""
Script principal para executar os testes automatizados do ExpenseLit.
Este script instala dependências, executa testes e captura erros.
"""
import subprocess
import sys
import os
import asyncio
from datetime import datetime


def install_test_dependencies():
    """Instala as dependências de teste."""
    print("📦 Instalando dependências de teste...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependências instaladas com sucesso")

        # Instala browsers do Playwright
        print("🌐 Instalando browsers do Playwright...")
        subprocess.check_call([
            sys.executable, "-m", "playwright", "install", "chromium"
        ])
        print("✅ Browsers instalados com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False


def run_ui_tests():
    """Executa os testes de UI."""
    print("\n🧪 Executando testes de interface...")
    try:
        # Importa e executa os testes
        from tests.test_expenses_ui import run_tests
        results = asyncio.run(run_tests())
        return results
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return {"error": str(e)}


def generate_report(results):
    """Gera o relatório final em error.txt."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_content = f"""RELATÓRIO DE TESTES AUTOMATIZADOS - ExpenseLit
Executado em: {timestamp}
{"="*60}

OBJETIVO: Verificar se os erros críticos de edição foram corrigidos:
- ❌ st.session_state.edit_expense_X cannot be modified after widget instantiation
- ❌ st.session_state.edit_revenue_X cannot be modified after widget instantiation

"""

    if "error" in results:
        report_content += f"❌ ERRO CRÍTICO NO TESTE:\n{results['error']}\n\n"
    else:
        # Navegação
        report_content += "1. TESTE DE NAVEGAÇÃO BÁSICA:\n"
        report_content += "-" * 30 + "\n"
        nav_results = results.get("navigation", {})
        if "error" in nav_results:
            report_content += f"❌ ERRO: {nav_results['error']}\n"
        else:
            for section, result in nav_results.items():
                if result["status"] == "ok":
                    report_content += f"✅ {section}: Carregou sem erros\n"
                else:
                    report_content += f"❌ {section}: ERRO ENCONTRADO\n"
                    for error in result["errors"]:
                        report_content += f"   🔸 {error}\n"

        # Edição de despesas
        report_content += "\n2. TESTE DE EDIÇÃO DE DESPESAS:\n"
        report_content += "-" * 30 + "\n"
        expense_result = results.get("expense_edit")
        if expense_result is True:
            report_content += "✅ SUCESSO: Edição de despesas funcionando corretamente\n"
            report_content += "   🔹 Erro de session_state foi CORRIGIDO\n"
        elif expense_result is False:
            report_content += "❌ ERRO: Ainda existe problema na edição de despesas\n"
            report_content += "   🔸 Erro de session_state ainda presente\n"
        elif expense_result is None:
            report_content += "⚠️ AVISO: Teste inconcluso\n"
            report_content += "   🔸 Nenhuma despesa encontrada para testar\n"
            report_content += "   🔸 Para testar completamente, adicione dados de teste\n"

        # Edição de receitas
        report_content += "\n3. TESTE DE EDIÇÃO DE RECEITAS:\n"
        report_content += "-" * 30 + "\n"
        revenue_result = results.get("revenue_edit")
        if revenue_result is True:
            report_content += "✅ SUCESSO: Edição de receitas funcionando corretamente\n"
            report_content += "   🔹 Erro de session_state foi CORRIGIDO\n"
        elif revenue_result is False:
            report_content += "❌ ERRO: Ainda existe problema na edição de receitas\n"
            report_content += "   🔸 Erro de session_state ainda presente\n"
        elif revenue_result is None:
            report_content += "⚠️ AVISO: Teste inconcluso\n"
            report_content += "   🔸 Nenhuma receita encontrada para testar\n"
            report_content += "   🔸 Para testar completamente, adicione dados de teste\n"

    report_content += "\n" + "="*60 + "\n"
    report_content += "RESUMO DOS PROBLEMAS ENCONTRADOS:\n"
    report_content += "="*60 + "\n"

    # Conta erros
    error_count = 0
    if "error" in results:
        error_count += 1
        report_content += f"1. ERRO CRÍTICO: {results['error']}\n"

    nav_errors = 0
    if "navigation" in results and "error" not in results["navigation"]:
        for section, result in results["navigation"].items():
            if result["status"] != "ok":
                nav_errors += len(result["errors"])

    if nav_errors > 0:
        report_content += f"2. ERROS DE NAVEGAÇÃO: {
            nav_errors} problema(s) encontrado(s)\n"
        error_count += nav_errors

    if results.get("expense_edit") is False:
        report_content += "3. ERRO CRÍTICO: Edição de despesas ainda com problema de session_state\n"
        error_count += 1

    if results.get("revenue_edit") is False:
        report_content += "4. ERRO CRÍTICO: Edição de receitas ainda com problema de session_state\n"
        error_count += 1

    if error_count == 0:
        report_content += "🎉 NENHUM ERRO CRÍTICO ENCONTRADO!\n"
        report_content += "✅ Os problemas de session_state foram corrigidos com sucesso.\n"
    else:
        report_content += f"⚠️ TOTAL DE ERROS ENCONTRADOS: {error_count}\n"

    # Salva o relatório
    with open("error.txt", "w", encoding="utf-8") as f:
        f.write(report_content)

    print("📄 Relatório detalhado salvo em error.txt")
    print(f"📊 Total de erros encontrados: {error_count}")


def main():
    """Função principal."""
    print("🚀 INICIANDO TESTES AUTOMATIZADOS DO EXPENSELIT")
    print("="*50)

    # Verifica se estamos no diretório correto
    if not os.path.exists("app.py"):
        print("❌ ERRO: Execute este script na raiz do projeto ExpenseLit")
        sys.exit(1)

    # Instala dependências
    if not install_test_dependencies():
        print("❌ Falha ao instalar dependências. Abortando.")
        sys.exit(1)

    # Executa os testes
    print("\n⏳ Aguardando aplicação estar disponível em http://localhost:8501")
    print("💡 Certifique-se de que a aplicação está rodando com: docker compose up -d")
    input("Pressione ENTER quando a aplicação estiver rodando...")

    results = run_ui_tests()

    # Gera relatório
    generate_report(results)

    print("\n✅ Testes concluídos!")
    print("📋 Verifique o arquivo error.txt para detalhes completos")


if __name__ == "__main__":
    main()
