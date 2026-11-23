# Como usei IA


## Sugestões aceitas
### 1. Extração paginada (Parte 1)
- **O que pedi:** ajuda para escrever a função que percorre todas as páginas da API, pois eu não sabia como fazer a paginação.
- **O que aceitei:** o laço `while pagina <= total_paginas`, usando o `total_pages` que vem da própria resposta, e o encerramento com `sys.exit(1)` em caso de erro.
- **Por que aceitei:** o fim do laço é decidido pela API, sem número fixo no código. Encerrar no erro evita carregar o banco pela metade.
- **Como validei:** rodei e conferi 5 páginas com 1000 clientes e 26 páginas com 5100 pedidos. Depois desliguei a API e confirmei a mensagem de erro, sem traceback.

## Sugestões rejeitadas
### 1. Separador de milhar no converter_valor (A4)
- **O que foi sugerido:** remover os pontos antes de trocar a vírgula (`valor.replace(".", "").replace(",", ".")`), para tratar valores como "1.234,56".
- **Por que rejeitei:** os dados não têm separador de milhar, e testei que essa versão transforma "94.34" em 9434.0: um erro de 100 vezes no valor.
- **O que fiz no lugar:** mantive a versão simples e criei o teste `test_valor_texto_com_ponto_nao_e_multiplicado` para impedir que a mudança volte.

## Falhas e retrabalho

