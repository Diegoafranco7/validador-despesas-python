"""Valida dados de despesas e produz relatórios rastreáveis.

Projeto de portfólio preparado com apoio de IA. A validação dos dados
não representa aprovação contábil, fiscal ou autorização de pagamento.
"""

import argparse
import csv
import json
import re
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path


PASTA = Path(__file__).resolve().parent
CAMPOS = ["id", "data", "fornecedor", "categoria", "valor"]
FORMATO_VALOR = re.compile(r"-?(?:[0-9]+|[0-9]{1,3}(?:\.[0-9]{3})+)(?:,[0-9]{1,2})?")


def converter_valor(texto):
    """Aceita formato brasileiro com até 12 algarismos na parte inteira."""
    texto = texto.strip()
    if not FORMATO_VALOR.fullmatch(texto):
        raise ValueError("valor inválido: use 125,90 ou 1.234,56")
    normalizado = texto.replace(".", "").replace(",", ".")
    if len(normalizado.lstrip("-").split(".")[0]) > 12:
        raise ValueError("valor excede o limite de 12 algarismos inteiros")
    valor = Decimal(normalizado)
    if valor <= 0:
        raise ValueError("valor deve ser maior que zero")
    return valor.quantize(Decimal("0.01"))


def ler_despesas(caminho):
    """Lê CSV com ponto e vírgula; preserva o número da linha de origem."""
    registros = []
    with Path(caminho).open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo, delimiter=";", strict=True)
        cabecalho = [campo.strip() for campo in next(leitor, [])]
        if len(cabecalho) != len(CAMPOS) or set(cabecalho) != set(CAMPOS):
            raise ValueError("cabeçalho deve conter uma vez cada campo: " + ";".join(CAMPOS))
        for celulas in leitor:
            if not celulas:
                continue
            if len(celulas) != len(CAMPOS):
                raise ValueError(f"linha {leitor.line_num}: quantidade de colunas inválida")
            dados = dict(zip(cabecalho, [celula.strip() for celula in celulas]))
            registros.append({"linha": leitor.line_num, **dados})
    return registros


def analisar(registros):
    """Separa registros conformes e pendentes, sem corrigir a entrada."""
    contagem_ids = Counter(item["id"] for item in registros if item["id"])
    validos = []
    pendentes = []
    total = Decimal("0.00")

    for item in registros:
        motivos = [f"{campo} obrigatório" for campo in CAMPOS if not item[campo]]
        if item["id"] and contagem_ids[item["id"]] > 1:
            motivos.append("id duplicado: revisar todas as ocorrências")

        if item["data"]:
            try:
                if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", item["data"]):
                    raise ValueError("formato")
                date.fromisoformat(item["data"])
            except ValueError:
                motivos.append("data inválida: use uma data existente em AAAA-MM-DD")

        valor = None
        if item["valor"]:
            try:
                valor = converter_valor(item["valor"])
            except ValueError as erro:
                motivos.append(str(erro))

        if motivos:
            pendentes.append({**item, "motivos": " | ".join(motivos)})
        else:
            validos.append(item.copy())
            total += valor

    resumo = {
        "registros_processados": len(registros),
        "registros_validos": len(validos),
        "registros_pendentes": len(pendentes),
        "total_valido_brl": format(total, ".2f"),
    }
    return validos, pendentes, resumo


def salvar_csv(caminho, campos, registros):
    with caminho.open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos, delimiter=";")
        escritor.writeheader()
        escritor.writerows(registros)


def executar(entrada, saida):
    entrada = Path(entrada)
    saida = Path(saida)
    destinos = [saida / nome for nome in ("validas.csv", "pendencias.csv", "resumo.json")]
    if entrada.resolve() in {destino.resolve() for destino in destinos}:
        raise ValueError("a entrada não pode ser um dos arquivos de saída")

    validos, pendentes, resumo = analisar(ler_despesas(entrada))
    saida.mkdir(parents=True, exist_ok=True)
    salvar_csv(destinos[0], ["linha"] + CAMPOS, validos)
    salvar_csv(destinos[1], ["linha"] + CAMPOS + ["motivos"], pendentes)
    destinos[2].write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return resumo


def main():
    argumentos = argparse.ArgumentParser(description="Validador de dados de despesas")
    argumentos.add_argument("--entrada", type=Path, default=PASTA / "dados" / "despesas.csv")
    argumentos.add_argument("--saida", type=Path, default=PASTA / "saida")
    opcoes = argumentos.parse_args()
    try:
        resumo = executar(opcoes.entrada, opcoes.saida)
    except (ValueError, OSError, csv.Error, UnicodeError) as erro:
        argumentos.exit(1, f"Não foi possível processar: {erro}\n")

    print(f"Registros: {resumo['registros_processados']}")
    print(f"Válidos: {resumo['registros_validos']}")
    print(f"Pendentes: {resumo['registros_pendentes']}")
    total = resumo["total_valido_brl"].replace(".", ",")
    print(f"Total válido: R$ {total}")
    print(f"Relatórios: {opcoes.saida.resolve()}")


if __name__ == "__main__":
    main()
