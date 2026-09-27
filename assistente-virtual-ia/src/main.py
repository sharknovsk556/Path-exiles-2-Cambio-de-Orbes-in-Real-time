import json
from pathlib import Path

if __package__:
    from .src.marketplace import abrir_marketplace, consultar_cotacoes, formatar_cotacoes, monitorar_cotacoes
else:
    from src.marketplace import abrir_marketplace, consultar_cotacoes, formatar_cotacoes, monitorar_cotacoes

def carregar_itens():
    caminho_itens = Path(__file__).resolve().parent / "data" / "items.json"
    with caminho_itens.open("r", encoding="utf-8") as f:
        return json.load(f)

def chat():
    print("Assistente Virtual IA - Path of Exile 2")
    print("Digite 'orbs' para ver o câmbio, 'monitorar' para acompanhar ou 'sair' para encerrar.\n")

    itens = carregar_itens()

    while True:
        pergunta = input("Você: ").strip().lower()
        if pergunta == "sair":
            print("Assistente: Até a próxima Exile!")
            break

        if pergunta in {"orbs", "moedas"}:
            try:
                print(f"Assistente:\n{formatar_cotacoes(consultar_cotacoes())}\n")
            except Exception as erro:
                print(f"Assistente: Não consegui consultar as cotações: {erro}\n")
            continue

        if pergunta == "monitorar":
            try:
                monitorar_cotacoes()
            except Exception as erro:
                print(f"Assistente: Não consegui monitorar as cotações: {erro}\n")
            continue

        if pergunta == "trade" or pergunta.startswith("trade "):
            partes = pergunta.split(maxsplit=1)
            item_busca = partes[1] if len(partes) > 1 else ""
            if abrir_marketplace():
                print("Assistente: Trade2 aberto no navegador.")
                if item_busca:
                    print(f"Pesquise por '{item_busca}' no site.\n")
                else:
                    print()
            else:
                print("Assistente: Não consegui abrir o navegador.\n")
            continue

        encontrado = False
        for item in itens:
            if pergunta in item["nome"].lower():
                print(f"Assistente: O preço médio de {item['nome']} é {item['preco']} Chaos Orbs.\n")
                encontrado = True
                break

        if not encontrado:
            print("Assistente: Não encontrei esse item na base offline.\n")

if __name__ == "__main__":
    chat()
