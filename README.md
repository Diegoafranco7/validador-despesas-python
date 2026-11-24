# Validador de despesas

Projeto de portfólio de Diego Franco, preparado com apoio de IA. Protótipo local em Python para conferir registros financeiros, explicar pendências e disponibilizar resultados em SQLite, API HTTP e painel web. Os dados incluídos são fictícios.

## Visualizar a demonstração

Extraia o pacote e abra **`saida/relatorio.html`** no navegador. A prévia apresenta o lote incluído e seus resultados, sem instalação. Os arquivos CSV e JSON ficam na mesma pasta.

## Executar a aplicação

Requisito: Python 3.10 ou superior. A aplicação utiliza somente a biblioteca padrão, incluindo SQLite; não há dependências externas para instalar.

Abra o terminal na pasta do projeto e execute:

```text
python aplicacao.py
```

Em Linux/macOS, pode ser necessário usar `python3`. O programa gera os relatórios, inicializa a API em `127.0.0.1` e abre o painel no navegador. A porta padrão é 8765; caso esteja ocupada, o endereço disponível aparece no terminal. Para encerrar, use Ctrl+C.

```text
http://127.0.0.1:8765
http://127.0.0.1:8765/api/resumo
```

Para gerar somente os arquivos, sem iniciar o servidor:

```text
python aplicacao.py --somente-relatorios
```

## Problema e decisões

Registros financeiros podem conter campos vazios, IDs duplicados, datas inexistentes e valores inválidos. O protótipo separa registros conformes e pendentes, mantém a linha de origem e informa os motivos de revisão.

- Valores são processados com `Decimal` e persistidos como centavos inteiros no SQLite.
- IDs permanecem como texto para preservar zeros à esquerda.
- Todas as ocorrências de um ID duplicado ficam pendentes.
- O arquivo de entrada é preservado; não há correção silenciosa.
- Sugestões de categoria ficam separadas da validação e exigem revisão humana.

## Resultado do lote incluído

| Indicador | Resultado |
|---|---:|
| Registros processados | 15 |
| Registros válidos | 3 |
| Registros pendentes | 12 |
| Total válido | R$ 1.402,46 |

Esses resultados são do conjunto fictício de demonstração, não métricas de produtividade de uma operação real.

## Componentes

| Arquivo | Responsabilidade |
|---|---|
| `validador.py` | Leitura CSV, regras de dados e exportação |
| `aplicacao.py` | Persistência SQLite, API HTTP e execução |
| `web/index.html` | Painel com filtros, indicadores e downloads |
| `consultas.sql` | Consultas de totais, pendências e duplicidades |
| `dados/despesas.csv` | Lote fictício de entrada |
| `dados/sugestoes_ia_exemplo.json` | Sugestões de exemplo identificadas como assistidas por IA |
| `tests/` | Testes automatizados do validador, banco e API |
| `saida/` | Relatório HTML, CSV/JSON e banco de demonstração |
| `VALIDACAO.md` | Escopo das verificações realizadas |

## API

| Método | Rota | Conteúdo |
|---|---|---|
| GET | `/api/saude` | Estado da aplicação |
| GET | `/api/resumo` | Contagens e total válido |
| GET | `/api/despesas` | Todos os registros |
| GET | `/api/pendencias` | Registros pendentes e motivos |
| GET | `/api/categorias` | Totais por categoria, em centavos |
| GET | `/api/sugestoes` | Sugestões para revisão humana |
| GET | `/api/prompt` | Prompt com os dados do lote |
| POST | `/api/sugestoes` | Importação validada de sugestões JSON |
| GET | `/baixar/validas.csv` | Exportação dos registros válidos |
| GET | `/baixar/pendencias.csv` | Exportação das pendências |
| GET | `/baixar/resumo.json` | Exportação do resumo |

Exemplo de resposta:

```json
{"registros_processados":15,"registros_validos":3,"registros_pendentes":12,"total_valido_brl":"1402.46"}
```

## Regras e limites de entrada

O CSV utiliza UTF-8, ponto e vírgula e os campos `id;data;fornecedor;categoria;valor`. Os campos são obrigatórios. Datas devem existir no calendário e usar AAAA-MM-DD. Valores devem ser positivos, em formato brasileiro, com até duas casas decimais e até 12 algarismos inteiros. Não há arredondamento silencioso de valores com casas excedentes. Cabeçalhos inválidos e linhas com quantidade incorreta de colunas interrompem o processamento.

Cada execução recria a fotografia do banco, os relatórios e as sugestões de demonstração. Esta versão não mantém histórico de lotes.

Para executar outro lote:

```text
python aplicacao.py --entrada dados/meu_arquivo.csv --saida saida/outro_lote
```

## Papel da IA

O código e os exemplos de classificação foram preparados com apoio de IA. O fluxo opcional de classificação consiste em obter uma resposta de um LLM a partir do prompt apresentado no painel e importar a lista JSON para revisão. Não há chamada automática a um modelo ou chave de API embutida.

O importador valida a estrutura da resposta, a categoria permitida e a existência da linha de origem. Um lote inválido é rejeitado sem gravação parcial. As sugestões não alteram os registros originais, o total válido ou a situação de pagamento.

Exemplo de sugestão:

```json
[{"linha":11,"categoria_sugerida":"Escritório","justificativa":"O fornecedor indica papelaria; requer revisão humana."}]
```

## Verificação

```text
python -m unittest discover -s tests -v
```

A suíte contém 13 testes de regras, centavos, datas, duplicidades, entrada/saída, persistência, importação de sugestões e API. Consulte `VALIDACAO.md` para os ambientes e o alcance das verificações. O workflow de CI incluído está preparado para Python 3.12/3.13 e Linux/Windows; a execução remota depende da publicação em um repositório.

## Escopo do protótipo

A validação de dados não equivale a aprovação fiscal, contábil ou autorização de pagamento. Esta versão não implementa OCR, leitura de notas fiscais, integração com ERP, autenticação ou inferência automática de LLM. O servidor foi configurado para demonstração local; não foi preparado para exposição pública ou uso em produção.

## Referências técnicas

- Python: https://www.python.org/downloads/
- SQLite: https://docs.python.org/3/library/sqlite3.html
- Decimal: https://docs.python.org/3/library/decimal.html
- CSV: https://docs.python.org/3/library/csv.html
- HTTP: https://docs.python.org/3/library/http.server.html
