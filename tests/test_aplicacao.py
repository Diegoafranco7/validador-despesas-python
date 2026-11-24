import json
import sqlite3
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from aplicacao import criar_handler, fotografia, importar_sugestoes, preparar, relatorio_html
from validador import PASTA


class AplicacaoDespesas(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.saida = Path(self.pasta.name)
        self.banco, self.resumo = preparar(pasta_saida=self.saida)

    def tearDown(self):
        self.pasta.cleanup()

    def test_banco_preserva_ids_duplicados_linhas_e_total_em_centavos(self):
        dados = fotografia(self.banco)
        self.assertEqual(dados['resumo'], self.resumo)
        self.assertEqual(dados['resumo']['total_valido_brl'], '1402.46')
        self.assertEqual(sum(c['total_centavos'] for c in dados['categorias']), 140246)
        self.assertEqual(len([r for r in dados['registros'] if r['id'] == '002']), 2)
        self.assertEqual(dados['registros'][0]['id'], '001')
        self.assertTrue((self.saida / 'relatorio.html').exists())

    def test_sugestao_nao_altera_entrada_pendencias_ou_total(self):
        entrada = PASTA / 'dados/despesas.csv'
        antes = entrada.read_bytes()
        n = importar_sugestoes(self.banco, [{'linha': 11, 'categoria_sugerida': 'Escritório', 'justificativa': 'Papelaria; revisar.'}])
        self.assertEqual(n, 1)
        self.assertEqual(fotografia(self.banco)['resumo'], self.resumo)
        self.assertEqual(entrada.read_bytes(), antes)

    def test_rejeita_lote_ia_invalido_sem_salvar_parte(self):
        antes = fotografia(self.banco)['sugestoes_ia']
        casos = [
            [{'linha': 11, 'categoria_sugerida': 'Falsa', 'justificativa': 'x'}],
            [{'linha': 999, 'categoria_sugerida': 'Outros', 'justificativa': 'x'}],
            [{'linha': True, 'categoria_sugerida': 'Outros', 'justificativa': 'x'}],
            [{'linha': 11, 'categoria_sugerida': 'Outros', 'justificativa': 'x'}, {'linha': 999, 'categoria_sugerida': 'Outros', 'justificativa': 'x'}],
        ]
        for itens in casos:
            with self.subTest(itens=itens), self.assertRaises(ValueError):
                importar_sugestoes(self.banco, itens)
            self.assertEqual(fotografia(self.banco)['sugestoes_ia'], antes)

    def test_relatorio_nao_injeta_html_de_campos_do_csv(self):
        dados = fotografia(self.banco)
        ataque = '</script><img src=x onerror=alert(1)>'
        dados['registros'][0]['fornecedor'] = ataque
        html = relatorio_html(dados)
        self.assertNotIn(ataque, html)
        self.assertIn('\\u003c/script\\u003e', html)

    def test_api_resumo_exportacao_404_e_importacao(self):
        servidor = ThreadingHTTPServer(('127.0.0.1', 0), criar_handler(self.banco, self.saida))
        processo = threading.Thread(target=servidor.serve_forever, daemon=True)
        processo.start()
        base = f'http://127.0.0.1:{servidor.server_port}'
        try:
            with urlopen(base + '/api/resumo') as resposta:
                self.assertEqual(json.load(resposta), self.resumo)
            with urlopen(base + '/baixar/validas.csv') as resposta:
                self.assertIn('attachment', resposta.headers['Content-Disposition'])
                self.assertEqual(resposta.read(), (self.saida / 'validas.csv').read_bytes())
            with self.assertRaises(HTTPError) as erro:
                urlopen(base + '/../../aplicacao.py')
            self.assertEqual(erro.exception.code, 404)
            itens = [{'linha': 11, 'categoria_sugerida': 'Escritório', 'justificativa': 'Revisar classificação.'}]
            req = Request(base + '/api/sugestoes', data=json.dumps(itens).encode(), headers={'Content-Type': 'application/json'})
            with urlopen(req) as resposta:
                self.assertEqual(json.load(resposta)['sugestoes_importadas'], 1)
            req = Request(base + '/api/sugestoes', data=b'[]', headers={'Content-Type': 'application/json', 'Origin': 'https://externo.example'})
            with self.assertRaises(HTTPError) as erro:
                urlopen(req)
            self.assertEqual(erro.exception.code, 403)
        finally:
            servidor.shutdown()
            servidor.server_close()
            processo.join(timeout=3)


if __name__ == '__main__':
    unittest.main()
