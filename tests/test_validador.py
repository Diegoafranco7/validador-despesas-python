import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from validador import PASTA, analisar, converter_valor, executar, ler_despesas


class RegrasDeDespesas(unittest.TestCase):
    def test_exemplo_tem_totais_e_ids_esperados(self):
        validos, pendentes, resumo = analisar(ler_despesas(PASTA / "dados" / "despesas.csv"))
        self.assertEqual(resumo, {
            "registros_processados": 15,
            "registros_validos": 3,
            "registros_pendentes": 12,
            "total_valido_brl": "1402.46",
        })
        self.assertEqual([item["id"] for item in validos], ["001", "003", "010"])
        duplicados = [item for item in pendentes if item["id"] == "002"]
        self.assertEqual(len(duplicados), 2)
        self.assertTrue(all("id duplicado" in item["motivos"] for item in duplicados))

    def test_centavos_sao_exatos_e_formato_brasileiro_e_aceito(self):
        self.assertEqual(converter_valor("0,10") + converter_valor("0,20"), Decimal("0.30"))
        self.assertEqual(converter_valor("1.234,56"), Decimal("1234.56"))
        self.assertEqual(converter_valor("10,5"), Decimal("10.50"))

    def test_rejeita_valores_invalidos_sem_arredondar_entrada(self):
        for texto in ["0", "-1,00", "10,999", "NaN", "Infinity", "10.50", "1,234.56", "1000000000000"]:
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                converter_valor(texto)

    def test_reconhece_dia_bissexto_e_rejeita_data_inexistente(self):
        base = {"linha": 2, "id": "a", "data": "2024-02-29", "fornecedor": "Exemplo", "categoria": "Teste", "valor": "1,00"}
        validos, pendentes, _ = analisar([base, {**base, "linha": 3, "id": "b", "data": "2026-02-29"}])
        self.assertEqual(len(validos), 1)
        self.assertIn("data inválida", pendentes[0]["motivos"])

    def test_cabecalho_duplicado_ou_incompleto_nao_passa(self):
        with tempfile.TemporaryDirectory() as pasta:
            entrada = Path(pasta) / "entrada.csv"
            for cabecalho in ["id;data;fornecedor;valor", "id;data;fornecedor;valor;valor"]:
                entrada.write_text(cabecalho + "\n", encoding="utf-8")
                with self.subTest(cabecalho=cabecalho), self.assertRaisesRegex(ValueError, "cabeçalho"):
                    ler_despesas(entrada)

    def test_linha_com_coluna_extra_nao_e_ignorada(self):
        with tempfile.TemporaryDirectory() as pasta:
            entrada = Path(pasta) / "entrada.csv"
            entrada.write_text("id;data;fornecedor;categoria;valor\na;2026-11-01;Exemplo;Teste;1,00;extra\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "quantidade de colunas"):
                ler_despesas(entrada)

    def test_saida_criada_sem_alterar_entrada(self):
        entrada = PASTA / "dados" / "despesas.csv"
        antes = entrada.read_bytes()
        with tempfile.TemporaryDirectory() as pasta:
            executar(entrada, pasta)
            self.assertEqual({arquivo.name for arquivo in Path(pasta).iterdir()}, {"validas.csv", "pendencias.csv", "resumo.json"})
        self.assertEqual(entrada.read_bytes(), antes)

    def test_impede_sobrescrever_entrada_com_arquivo_de_saida(self):
        with tempfile.TemporaryDirectory() as pasta:
            entrada = Path(pasta) / "validas.csv"
            entrada.write_text("conteúdo que não deve ser alterado", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "entrada não pode"):
                executar(entrada, pasta)
            self.assertEqual(entrada.read_text(encoding="utf-8"), "conteúdo que não deve ser alterado")


if __name__ == "__main__":
    unittest.main()
