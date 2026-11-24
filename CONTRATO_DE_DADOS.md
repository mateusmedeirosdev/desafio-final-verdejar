# Contrato de dados: ETL da Verdejar

## Objetivo

Define o que o ETL recebe das fontes e o que entrega no PostgreSQL: campos,
tipos, obrigatoriedade e regras de transformação. Os tipos seguem o
`insumos/schema.sql`, e as funções citadas estão em `etl/transformacao.py`.

## Fontes e destinos

| Fonte | Dados | Tabela de destino |
|---|---|---|
| API `/clientes` (paginada) | Cadastro de clientes | `clientes` |
| API `/pedidos` (paginada) | Pedidos, com os itens dentro de cada pedido | `pedidos` e `itens_pedido` |
| `insumos/dados/produtos.csv` | Catálogo de produtos (todos os valores chegam como texto) | `produtos` |

## Resumo das armadilhas

| Código | Problema na fonte | Tratamento | Função | Contador |
|---|---|---|---|---|
| A1 | E-mail ausente | Vira NULL; o cliente é mantido | `tratar_email` | `emails_nulos` |
| A2 | Estado em caixa mista | Espaços removidos e maiúsculas | `padronizar_estado` | `estados_padronizados` |
| A3 | Data em AAAA-MM-DD ou DD/MM/AAAA | Convertida para DATE | `converter_data` | `datas_convertidas` |
| A4 | Valor como número ou texto com vírgula | Número com 2 casas | `converter_valor` | `valores_convertidos` |
| A5 | Pedido repetido entre páginas | Mantida a primeira ocorrência | `remover_repetidos` | `repetidos_descartados` |
| A6 | Total diferente da soma dos itens | Os dois valores gravados e o pedido marcado | `calcular_valor_itens`, `eh_divergente` | `divergentes` |

## Tabela `produtos`

| Campo | Tipo | Nulo? | Origem | Regra de transformação |
|---|---|---|---|---|
| `produto_id` | INTEGER, PK | Não | `produto_id` (CSV) | Texto convertido para inteiro |
| `nome` | TEXT | Não | `nome` (CSV) | Sem alteração |
| `categoria` | TEXT | Não | `categoria` (CSV) | Sem alteração |
| `preco_base` | NUMERIC(10,2) | Não | `preco_base` (CSV) | Texto convertido para número com 2 casas |

## Tabela `clientes`

| Campo | Tipo | Nulo? | Origem | Regra de transformação |
|---|---|---|---|---|
| `id` | INTEGER, PK | Não | `id` | Sem alteração |
| `nome` | TEXT | Não | `nome` | Sem alteração |
| `email` | TEXT | **Sim** | `email` | **A1** (`tratar_email`): ausente ou vazio vira NULL |
| `cidade` | TEXT | Não | `cidade` | Sem alteração |
| `estado` | CHAR(2) | Não | `estado` | **A2** (`padronizar_estado`): `" rs "` vira `"RS"`. Conta apenas os que mudaram |
| `cadastro_em` | DATE | Não | `cadastro_em` | `converter_data` (sempre chega em AAAA-MM-DD) |

## Tabela `pedidos`

| Campo | Tipo | Nulo? | Origem | Regra de transformação |
|---|---|---|---|---|
| `id` | INTEGER, PK | Não | `id` | **A5** (`remover_repetidos`): um pedido por id, a primeira ocorrência na ordem das páginas |
| `cliente_id` | INTEGER, FK → clientes.id | Não | `cliente_id` | Sem alteração; precisa existir em `clientes` |
| `data_pedido` | DATE | Não | `data_pedido` | **A3** (`converter_data`): data inexistente (31/02) gera erro. Conta apenas as que vieram em DD/MM/AAAA |
| `status` | TEXT | Não | `status` | Sem alteração (`entregue`, `em_transporte`, `cancelado`) |
| `valor_total` | NUMERIC(12,2) | Não | `valor_total` | **A4** (`converter_valor`): `"125,84"` vira `125.84`. Conta apenas os que vieram como texto. Não trata separador de milhar |
| `valor_itens` | NUMERIC(12,2) | Não | **calculado** | **A6** (`calcular_valor_itens`): soma de quantidade × preço unitário dos itens, 2 casas |
| `divergente` | BOOLEAN | Não | **calculado** | **A6** (`eh_divergente`): verdadeiro quando a diferença passa de R$ 0,01 |

A divergência é **sinalizada, não corrigida**: `valor_total` (informado) e
`valor_itens` (calculado) são gravados lado a lado.

## Tabela `itens_pedido`

| Campo | Tipo | Nulo? | Origem | Regra de transformação |
|---|---|---|---|---|
| `pedido_id` | INTEGER, PK, FK → pedidos.id | Não | `id` do pedido | Herdado do pedido ao qual o item pertence |
| `linha` | INTEGER, PK | Não | **gerado** | Posição do item no pedido, de 1 a N (`enumerate`). A API não envia este campo |
| `produto_id` | INTEGER, FK → produtos.produto_id | Não | `itens[].produto_id` | Sem alteração |
| `quantidade` | INTEGER | Não | `itens[].quantidade` | Sem alteração |
| `preco_unitario` | NUMERIC(10,2) | Não | `itens[].preco_unitario` | Sem alteração (já chega como número) |

Só entram os itens dos pedidos únicos: os itens das cópias repetidas são
descartados junto com o pedido.

## Integridade e validação

- **Ordem da carga:** produtos, clientes, pedidos e itens, respeitando as chaves estrangeiras.
- **Idempotência:** as tabelas são limpas (`TRUNCATE`) e recarregadas numa única transação; se algo falhar, o banco volta ao estado anterior.
- **Valores numéricos:** `float` arredondado para 2 casas nas conversões e somas, eliminando resíduos do ponto flutuante (ex.: `92.19999999999999` vira `92.2`).
- **Estado nulo:** `padronizar_estado` devolve NULL sem quebrar, e o banco recusa na carga (coluna NOT NULL). Não ocorre nos dados atuais.
- **Como é verificado:** testes de cada armadilha (`tests/test_transformacao.py`), teste de reconciliação de contagem e soma (`tests/test_reconciliacao.py`) e consultas de validação (`consultas_validacao.sql`).