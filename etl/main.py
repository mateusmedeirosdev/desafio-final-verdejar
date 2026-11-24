"""Executa o ETL completo: extração, transformação, carga e reconciliação."""
from etl.extracao import extrair_paginado, ler_produtos_csv, salvar_bruto
from etl.transformacao import transformar_clientes, transformar_pedidos, transformar_produtos
from etl.carga import conectar, carregar, contar
from etl.reconciliacao import totais_origem, totais_destino


def main():
    # 1. Extração: busca na API e no CSV e guarda os brutos
    clientes_brutos, pags_c = extrair_paginado("clientes")
    print(f"extracao: clientes paginas={pags_c} registros={len(clientes_brutos)}")
    salvar_bruto("clientes", clientes_brutos)

    pedidos_brutos, pags_p = extrair_paginado("pedidos")
    print(f"extracao: pedidos paginas={pags_p} registros_brutos={len(pedidos_brutos)}")
    salvar_bruto("pedidos", pedidos_brutos)

    produtos_brutos = ler_produtos_csv("insumos/dados/produtos.csv")
    salvar_bruto("produtos", produtos_brutos)

    # 2. Transformação: aplica as armadilhas A1 a A6
    produtos = transformar_produtos(produtos_brutos)
    clientes, cont_c = transformar_clientes(clientes_brutos)
    pedidos, itens, cont_p = transformar_pedidos(pedidos_brutos)
    print(f"transformacao: pedidos_unicos={cont_p['pedidos_unicos']} "
          f"repetidos_descartados={cont_p['repetidos_descartados']}")
    print(f"transformacao: emails_nulos={cont_c['emails_nulos']} "
          f"estados_padronizados={cont_c['estados_padronizados']} "
          f"datas_convertidas={cont_p['datas_convertidas']} "
          f"valores_convertidos={cont_p['valores_convertidos']}")

    # 3. Carga: grava no PostgreSQL e lê as contagens e a soma do destino
    with conectar() as conexao:
        carregar(conexao, produtos, clientes, pedidos, itens)
        c = contar(conexao)
        _, soma_destino = totais_destino(conexao)
    print(f"carga: clientes={c['clientes']} produtos={c['produtos']} "
          f"pedidos={c['pedidos']} itens={c['itens_pedido']}")

    # 4. Reconciliação: compara a soma da origem com a do banco
    _, soma_origem = totais_origem(pedidos_brutos)
    print(f"reconciliacao: soma_valor_itens_origem={soma_origem:.2f} "
          f"soma_valor_itens_destino={soma_destino:.2f} "
          f"diferenca={abs(soma_origem - soma_destino):.2f}")
    print(f"divergentes: {cont_p['divergentes']} pedidos com valor_total diferente da soma dos itens")


if __name__ == "__main__":
    main()