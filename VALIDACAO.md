# Verificação do protótipo

Revisão de apresentação: 24/11/2026.

## Verificações automatizadas

13 testes do programa, banco e API executados com sucesso em Python 3.12.14/Linux durante a preparação e novamente na revisão do pacote de envio.

Os testes cobrem:

- Resultado do lote fictício e preservação de IDs com zeros à esquerda.
- Sinalização de todas as ocorrências de ID duplicado.
- Precisão dos centavos e rejeição de valores inválidos.
- Datas de calendário, cabeçalhos e quantidade de colunas.
- Preservação da entrada e proteção contra sobrescrita pela saída.
- Persistência SQLite e consistência do total em centavos.
- Importação de sugestões sem alteração de despesas ou total.
- Rejeição integral de respostas JSON inválidas.
- Consulta da API, exportação, rota inexistente e restrição de origem na importação.
- Escape dos dados incorporados ao HTML.

## Execução de demonstração

O protótipo foi iniciado por Diego em Windows com Python 3.13.0, conforme registro de tela de 24/11/2026. O terminal apresentou 15 registros, 3 válidos, 12 pendentes e total válido de R$ 1.402,46, com o painel aberto no navegador.

O programa também foi executado para geração de relatórios no ambiente de preparação. A verificação sintática do JavaScript foi concluída sem erro.

## Alcance

A suíte automatizada não foi executada no computador Windows do candidato. Não há teste automatizado de navegação visual neste pacote. O workflow de GitHub Actions está preparado, mas não há resultado remoto de CI declarado. Não foram realizadas verificações de uso em produção ou integrações externas com ERP, OCR ou provedores de LLM.
