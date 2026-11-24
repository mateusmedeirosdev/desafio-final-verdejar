
# Como usei IA

**Ferramenta:** Claude (Claude Code), usado como **tutor** (para entender Python,
Git, testes e SQL) e como **par com escopo limitado** (para propor funções e
testes que eu pedia, parte por parte)

A  IA ia foi usada como ferramenta de apoio durante o desenvolvimento do projeto, principalmente para esclacer duvidas sobre a API e extração, sugerindo implementações pontuais em cada etapa e ajudando a entender e corrigir erros.

## 1. Sugestões aceitas

### 1.1. Extração paginada (Parte 1)
- **Contexto:** eu não sabia como percorrer as páginas da API.
- **O que pedi:** ajuda para escrever a função que consome uma rota paginada.
- **O que a IA propôs:** um laço `while pagina <= total_paginas`, usando o
  `total_pages` que vem da própria resposta, com `timeout`, verificação do
  status HTTP e encerramento com `sys.exit(1)` em caso de erro.
- **Por que aceitei:** o fim do laço é decidido pela API, sem número fixo no
  código. Entre devolver uma lista vazia e encerrar o programa no erro, escolhi
  encerrar: seguir em frente poderia carregar o banco pela metade sem ninguém
  perceber.
- **Como validei:** 5 páginas com 1000 clientes e 26 páginas com 5100 pedidos.
  Depois desliguei a API e confirmei a mensagem de erro, sem traceback.

### 1.2. Carga idempotente (Parte 3)
- **O que a IA propôs:** `TRUNCATE` das quatro tabelas e inserção na ordem das
  chaves estrangeiras, tudo numa única transação, com parâmetros `%(nome)s`.
- **Por que aceitei:** pedi a explicação passo a passo do `with`, do cursor e
  da transação antes de aceitar. A transação garante que, se algo falhar no
  meio, o banco volta ao estado anterior, nunca fica vazio nem pela metade.
- **Como validei:** rodei o ETL duas vezes seguidas e a linha
  `carga: clientes=1000 produtos=12 pedidos=5000 itens=12455` ficou idêntica.


## 2. Sugestões rejeitadas ou modificadas

### 2.1. Separador de milhar no converter_valor (A4)
- **O que foi sugerido:** remover os pontos antes de trocar a vírgula
  (`valor.replace(".", "").replace(",", ".")`), para tratar "1.234,56".
- **Por que rejeitei:** os dados não têm separador de milhar, e testei que
  essa versão transforma "94.34" em 9434.0: um erro cem vezes
  maior, sem nenhuma mensagem.
- **O que fiz no lugar:** mantive a versão simples, documentei o limite na
  docstring e criei o teste `test_valor_texto_com_ponto_nao_e_multiplicado`
  para impedir que a mudança volte.
### 2.2. Versão em uma linha do remover_repetidos (A5)
- **O que foi sugerido:** trocar o laço por um dicionário,
  `list({p["id"]: p for p in pedidos}.values())`, mais curto.
- **Por que rejeitei:** testei e o `test_mantem_a_primeira_ocorrencia` falhou.
  O dicionário sobrescreve o valor quando o id se repete, então guarda a
  última ocorrência, e o guia exige a primeira. É um erro pois a
  contagem de descartados continua certa, mas o pedido guardado é o errado.
- **O que fiz no lugar:** mantive o meu laço com `set`, que guarda a primeira
  ocorrência e é fácil de explicar. O teste protege contra essa troca.


## 3. Falhas e retrabalho

### 3.2. Bugs meus encontrados pelos testes
Não vieram da IA, mas mostram o TDD funcionando:
- **A5:** escrevi `if pedido["id"] == id_vistos` em vez de `in`. Comparar um
  número com um conjunto é sempre falso, então nenhum repetido era removido.
  O teste `test_remove_pedido_repetido_pelo_id` falhou e eu corrigi.
- **A6:** o `return` ficou dentro do `for`, então a função somava só o
  primeiro item (12.9 em vez de 92.2) e devolvia `None` para lista vazia.


## 5. Considerações finais
A utilização da IA foi importante para a minha compreensão de alguns pontos que estavam um pouco confusos para mim, especialmente na parte da extração, então utilizei como uma espécie de tutor para me auxiliar nessa parte.
Pude alinhar os conceitos aprendidos nas aulas da sprint com as sujestões da IA e lapidar alguns conceitos que eu ainda não tinha compreendido completamente.
Por fim, é válido ressaltar que o uso da IA foi como ferramenta de apoio e as decisões técnicas, implementações, testes, correções e validações foram minha responsabilidade.