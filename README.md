# ETL da Verdejar

Desafio Final do Bootcamp (Fellowship OCT26 AI-Driven Data Engineering).
ETL que extrai clientes e pedidos de uma API paginada e produtos de um CSV,
trata as seis armadilhas de qualidade (A1 a A6) e carrega tudo no
PostgreSQL, com testes, reconciliação e consultas de validação.

## Estrutura

```
desafio-final/
  README.md
  COMO_USEI_IA.md            registro do uso de IA
  CONTRATO_DE_DADOS.md       campos, tipos e regras de cada tabela
  consultas_validacao.sql    3 consultas de validação + teste de consulta
  etl/
    extracao.py              Parte 1: API paginada e CSV, grava brutos/
    transformacao.py         Parte 2: funções das armadilhas A1 a A6 e orquestradores
    carga.py                 Parte 3: carga idempotente no PostgreSQL
    reconciliacao.py         Parte 4: totais da origem e do destino
    main.py                  executa o ETL completo
  tests/
    test_transformacao.py    22 testes das armadilhas
    test_reconciliacao.py    teste de reconciliação origem x banco
  insumos/                   arquivos fornecidos pelo desafio
  brutos/                    dados extraídos (fora do Git)
```

## Ambiente

| Item | Escolha |
|---|---|
| Sistema | Debian 13 |
| Python | 3.13 |
| Banco | **Caminho A:** PostgreSQL 19 instalado localmente, porta 5432 |
| Conexão | `psycopg` 3 (`pip install "psycopg[binary]"`) |
| Testes | `pytest` |

O Docker é opcional no desafio e não é usado neste projeto.

## Como rodar

**1. Ambiente Python**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**2. Banco de dados**

```bash
psql -h localhost -U postgres -c "CREATE DATABASE verdejar;"
psql -h localhost -U postgres -d verdejar -f insumos/schema.sql
```

**3. Credenciais**

Copie o `.env.example` para `.env` e preencha a senha. O `.env` está no
`.gitignore` e nunca é versionado. A conexão usa as variáveis `PGHOST`,
`PGPORT`, `PGDATABASE`, `PGUSER` e `PGPASSWORD`, lidas com `python-dotenv`.

```bash
cp .env.example .env
```

**4. API (em um terminal separado, deixe rodando)**

```bash
python3 insumos/api_verdejar.py --dados insumos/dados
```

**5. ETL completo**

```bash
python3 -m etl.main
```

**6. Testes (depois do ETL, porque o teste de reconciliação usa o banco carregado)**

```bash
pytest -v
```

**7. Consultas de validação**

```bash
psql -h localhost -U postgres -d verdejar -f consultas_validacao.sql
```

## Resultado do ETL

Duas execuções seguidas, com as mesmas contagens:

```
extracao: clientes paginas=5 registros=1000
extracao: pedidos paginas=26 registros_brutos=5100
transformacao: pedidos_unicos=5000 repetidos_descartados=100
transformacao: emails_nulos=81 estados_padronizados=151 datas_convertidas=1037 valores_convertidos=1255
carga: clientes=1000 produtos=12 pedidos=5000 itens=12455
reconciliacao: soma_valor_itens_origem=311228.75 soma_valor_itens_destino=311228.75 diferenca=0.00
divergentes: 238 pedidos com valor_total diferente da soma dos itens
```

| Armadilha | Tratamento | Resultado |
|---|---|---|
| A1 e-mail ausente | Gravado como NULL; o cliente é mantido | 81 e-mails nulos |
| A2 estado em caixa mista | Espaços removidos e maiúsculas | 151 estados padronizados |
| A3 data em dois formatos | Convertida para `date`; data inexistente gera erro | 1037 datas em DD/MM/AAAA convertidas |
| A4 valor com vírgula | Número com 2 casas | 1255 valores em texto convertidos |
| A5 pedido repetido | Mantida a primeira ocorrência | 100 repetidos descartados |
| A6 total divergente | `valor_total` e `valor_itens` gravados; pedido marcado | 238 divergentes |

## Decisões técnicas

**Extração**
- `page_size=200`, o máximo aceito pela API, para fazer menos requisições.
- O fim da paginação vem do `total_pages` da própria resposta, sem número fixo.
- Em erro de conexão, timeout ou status diferente de 200, o programa imprime
  uma mensagem clara e encerra com `sys.exit(1)`. Seguir com dados parciais
  poderia carregar o banco pela metade sem ninguém perceber.
- Os dados são gravados em `brutos/` sem alteração, para reprocessar sem
  chamar a API de novo. A remoção de repetidos fica na transformação.

**Transformação**
- Cada armadilha é uma função pequena e pura, testada isoladamente.
- Os contadores de conversão contam só o que precisou ser convertido.
- Os repetidos são removidos antes das demais transformações, para os
  contadores refletirem apenas os pedidos carregados.
- O campo `linha` dos itens não vem da API: é gerado pela posição do item
  no pedido (1, 2, 3...).
- Valores em `float` são arredondados para 2 casas, eliminando resíduos do
  ponto flutuante (`3 * 4.3 + 5 * 15.86` dá `92.19999999999999`).

**Idempotência**
- Estratégia: **limpar as tabelas antes da carga** (`TRUNCATE`) e inserir
  tudo de novo, numa **única transação**. Se qualquer inserção falhar, o
  banco volta ao estado anterior, sem ficar vazio nem pela metade.
- Prova: duas execuções seguidas com as mesmas contagens (acima).

**Carga**
- Ordem: produtos, clientes, pedidos e itens, respeitando as chaves estrangeiras.
- Inserções com parâmetros (`%(nome)s`), nunca concatenando texto no SQL.

## Testes

```
$ pytest -v
tests/test_reconciliacao.py::test_reconciliacao_origem_e_destino PASSED  [  4%]
tests/test_transformacao.py::test_email_nulo_permanece_nulo PASSED       [  8%]
tests/test_transformacao.py::test_email_vazio_vira_nulo PASSED           [ 13%]
tests/test_transformacao.py::test_email_valido_permanece PASSED          [ 17%]
tests/test_transformacao.py::test_estado_minusculo_vira_maiusculo PASSED [ 21%]
tests/test_transformacao.py::test_estado_maiusculo_permanece PASSED      [ 26%]
tests/test_transformacao.py::test_estado_com_espacos_e_limpo PASSED      [ 30%]
tests/test_transformacao.py::test_estado_nulo_permanece_nulo PASSED      [ 34%]
tests/test_transformacao.py::test_data_formato_iso_vira_date PASSED      [ 39%]
tests/test_transformacao.py::test_data_formato_brasileiro_vira_date PASSED [ 43%]
tests/test_transformacao.py::test_data_invalida_gera_erro PASSED         [ 47%]
tests/test_transformacao.py::test_valor_com_virgula_vira_numero PASSED   [ 52%]
tests/test_transformacao.py::test_valor_numerico_permanece PASSED        [ 56%]
tests/test_transformacao.py::test_valor_arredonda_para_duas_casas PASSED [ 60%]
tests/test_transformacao.py::test_valor_texto_com_ponto_nao_e_multiplicado PASSED [ 65%]
tests/test_transformacao.py::test_remove_pedido_repetido_pelo_id PASSED  [ 69%]
tests/test_transformacao.py::test_mantem_a_primeira_ocorrencia PASSED    [ 73%]
tests/test_transformacao.py::test_lista_sem_repetidos_nao_muda PASSED    [ 78%]
tests/test_transformacao.py::test_valor_itens_soma_quantidade_vezes_preco PASSED [ 82%]
tests/test_transformacao.py::test_valor_itens_de_lista_vazia_e_zero PASSED [ 86%]
tests/test_transformacao.py::test_valores_iguais_nao_sao_divergentes PASSED [ 91%]
tests/test_transformacao.py::test_diferenca_de_um_centavo_nao_e_divergente PASSED [ 95%]
tests/test_transformacao.py::test_diferenca_maior_que_um_centavo_e_divergente PASSED [100%]

============================== 23 passed in 0.10s ==============================

- `tests/test_transformacao.py`: 22 testes, cobrindo as seis armadilhas (A1 a A6),
  escritos antes das funções (TDD).
- `tests/test_reconciliacao.py`: compara a contagem de pedidos únicos e a soma
  de `valor_itens` da origem com o banco, tolerando um centavo.

## Consultas de validação

**(a) Total de vendas por mês**

```
    mes     | pedidos | total_vendas
------------+---------+--------------
 2026-01-01 |     488 |     30449.02
 2026-02-01 |     536 |     33923.86
 2026-03-01 |     487 |     30678.70
 2026-04-01 |     521 |     31253.96
 2026-05-01 |     512 |     30890.02
 2026-06-01 |     523 |     31627.73
 2026-07-01 |     519 |     32796.17
 2026-08-01 |     458 |     29328.04
 2026-09-01 |     476 |     29995.71
 2026-10-01 |     480 |     31104.54
```

**Teste da consulta (a):** a soma dos meses é igual à soma geral da tabela.

```
 soma_dos_meses | soma_geral
----------------+------------
      312047.75 |  312047.75
```

**(b) Pedidos por estado**

```
 estado | pedidos
--------+---------
 RS     |    1543
 SC     |    1127
 PR     |     974
 SP     |     880
 MG     |     476
```

Todas as siglas aparecem em maiúsculas: sem a A2, `RS` e `rs` seriam contados
como estados diferentes.

**(c) Pedidos divergentes:** 238 pedidos, o mesmo número do contador do ETL.

### Observações sobre os resultados

- A soma de vendas (R$ 312.047,75, coluna `valor_total`) é diferente da soma
  da reconciliação (R$ 311.228,75, coluna `valor_itens`). A diferença de
  R$ 819,00 vem exatamente dos 238 pedidos divergentes.
- A consulta (a) inclui todos os status, inclusive `cancelado`, para o teste
  de consulta bater com a soma geral da tabela. Num relatório de vendas real,
  os cancelados provavelmente ficariam de fora.
- Há pedido divergente com `valor_total` negativo (por exemplo, o pedido 81).
  O ETL grava e marca como divergente, como o desafio pede, sem corrigir.

## Validação cruzada

Os contadores foram comparados com os de uma colega da squad, que implementou
o ETL de forma independente: todos os números bateram.

## Melhorias futuras

- Usar `Decimal` em vez de `float` para valores monetários, eliminando os
  arredondamentos.
- Dividir o trabalho em branches por funcionalidade, com PRs menores.
- Orquestrar API, banco e ETL com `docker-compose`.

