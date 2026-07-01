# Projeto 1 - Automação de Sistema de Contabilidade
# Demanda
# Preciso automatizar o lançamento de transações financeiras em um sistema de contabilidade.
# O sistema atual exige que cada transação seja inserida manualmente, o que consome muito tempo e é propenso a erros.
# Gostaria de desenvolver um script que possa ler uma planilha contendo as
# transações e inserir automaticamente essas informações no sistema de contabilidade.

from playwright.sync_api import sync_playwright
from openpyxl import *
import re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={"width": 1200, "height": 600},
        accept_downloads=True,
        locale="pt-BR",
    )

    page = context.new_page()
    page.set_default_timeout(30000)
    page.set_default_navigation_timeout(60000)

    page.goto(
        "https://simulacontabil.netlify.app/",
        wait_until="domcontentloaded"
    )

    # Fazer login
    page.get_by_role("textbox", name="Email").click()
    page.get_by_role("textbox", name="Email").fill("admin@simulacontabil.com.br")

    page.get_by_role("textbox", name="Senha").click()
    page.get_by_role("textbox", name="Senha").fill("admin")

    page.get_by_role("button", name="Entrar").click()

    # Ir para lançamentos
    page.get_by_role("link", name="Lançamentos").click()

    # Ler planilha
    planilha = load_workbook("lancamentos.xlsx")
    pagina_lancamentos = planilha["Lançamentos"]

    # Percorrer as linhas
    for linha in pagina_lancamentos.iter_rows(min_row=2, values_only=True):

        descricao = linha[0]
        valor = str(linha[1])
        data = str(linha[2])
        tipo = linha[3]
        categoria = linha[4]
        status = linha[5]

        # Novo lançamento
        page.get_by_role("button", name="Novo Lançamento").click()

        # Descrição
        page.get_by_test_id("input-description").click()
        page.get_by_test_id("input-description").fill(descricao)

        # Valor
        page.get_by_test_id("input-amount").click()
        page.get_by_test_id("input-amount").fill(valor)

        # Data
        page.get_by_test_id("input-date").click()
        page.get_by_test_id("input-date").fill(data)

        # Tipo
        if tipo == "Receita":
            page.get_by_test_id("select-type").select_option("RECEITA")
        else:
            page.get_by_test_id("select-type").select_option("DESPESA")

        # Categoria
        page.get_by_test_id("select-category").select_option(categoria)

        # Status
        page.locator("div").filter(
            has_text=re.compile(r"^StatusPendentePagoAtrasado$")
        ).get_by_role("combobox").select_option(status.upper())

        # Salvar
        page.get_by_test_id("btn-save").click()

        page.wait_for_timeout(2000)

input("Digite ENTER para encerrar a automação")
browser.close()