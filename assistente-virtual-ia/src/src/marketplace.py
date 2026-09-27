import json
import os
import webbrowser
from datetime import datetime
from time import sleep
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

URL_TRADE2 = "https://br.pathofexile.com/trade2?lang=pt_BR"
POE_NINJA_API = "https://poe.ninja/poe2/api/economy"
INTERVALO_COTACAO_SEGUNDOS = 3600
_CACHE = {}


def _buscar_json(url):
    cabecalhos = {"User-Agent": os.environ.get("POE_NINJA_USER_AGENT", "AssistenteVirtualIA/1.0")}
    cacheado = _CACHE.get(url)
    if cacheado and cacheado[0]:
        cabecalhos["If-None-Match"] = cacheado[0]

    requisicao = Request(url, headers=cabecalhos)
    try:
        with urlopen(requisicao, timeout=20) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))
            _CACHE[url] = (resposta.headers.get("ETag"), dados)
            return dados
    except HTTPError as erro:
        if erro.code == 304 and cacheado:
            return cacheado[1]
        raise


def consultar_cotacoes():
    ligas = _buscar_json(f"{POE_NINJA_API}/leagues")
    if not ligas:
        raise ValueError("O poe.ninja não retornou ligas disponíveis.")

    liga = ligas[0]
    parametros = urlencode({"league": liga["id"], "type": "Currency"})
    visao = _buscar_json(f"{POE_NINJA_API}/exchange/current/overview?{parametros}")
    nucleo = visao["core"]
    moedas = {moeda["id"]: moeda["name"] for moeda in nucleo.get("items", [])}
    referencia_id = nucleo["primary"]
    taxas = [
        (moedas.get(moeda_id, moeda_id), float(taxa))
        for moeda_id, taxa in nucleo.get("rates", {}).items()
        if float(taxa) > 0
    ]

    return {
        "liga": liga.get("name", liga["id"]),
        "referencia": moedas.get(referencia_id, referencia_id),
        "taxas": taxas,
        "consultado_em": datetime.now().astimezone().strftime("%d/%m/%Y %H:%M:%S"),
    }


def _formatar_numero(valor):
    numero = f"{valor:,.2f}".rstrip("0").rstrip(".")
    return numero.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_cotacoes(cotacoes):
    linhas = [
        f"Câmbio PoE 2 | Liga: {cotacoes['liga']}",
        f"Referência: {cotacoes['referencia']}",
        f"Leitura: {cotacoes['consultado_em']}",
    ]
    linhas.extend(
        f"1 {cotacoes['referencia']} = {_formatar_numero(taxa)} {moeda}"
        for moeda, taxa in cotacoes["taxas"]
    )
    return "\n".join(linhas)


def monitorar_cotacoes():
    print("Monitorando câmbio do PoE 2. Atualização da fonte: aproximadamente 1 hora.")
    print("Pressione Ctrl+C para parar.\n")
    cotacoes_anteriores = None

    try:
        while True:
            cotacoes = consultar_cotacoes()
            print(formatar_cotacoes(cotacoes))
            if cotacoes_anteriores == cotacoes["taxas"]:
                print("Sem variação desde a última consulta.")
            cotacoes_anteriores = cotacoes["taxas"]
            print(f"Próxima consulta em {INTERVALO_COTACAO_SEGUNDOS // 60} minutos.\n")
            sleep(INTERVALO_COTACAO_SEGUNDOS)
    except KeyboardInterrupt:
        print("Monitoramento encerrado.")


def abrir_marketplace():
    return webbrowser.open(URL_TRADE2)
