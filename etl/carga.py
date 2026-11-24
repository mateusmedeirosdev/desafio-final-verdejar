"""carga dos dados tratados no PostgreSQL"""
import psycopg
from dotenv import load_dotenv


def conectar():
    """Abre a conexão usando as variáveis PG do arquivo .env"""
    load_dotenv()
    return psycopg.connect()


def carregar(conexao, produtos, clientes, pedidos, itens):
    """Limpa as tabelas e carrega tudo numa única transação.
    Ordem: produtos, clientes, pedidos e itens, respeitando as chaves
    estrangeiras.
    Se qualquer inserção falhar, nada é gravado e o banco continua como estava antes.
    """
    with conexao.transaction():
        with conexao.cursor() as cur:
            cur.execute("TRUNCATE itens_pedido, pedidos, clientes, produtos")

            cur.executemany(
                "INSERT INTO produtos (produto_id, nome, categoria, preco_base) "
                "VALUES (%(produto_id)s, %(nome)s, %(categoria)s, %(preco_base)s)",
                produtos,
            )
            cur.executemany(
                "INSERT INTO clientes (id, nome, email, cidade, estado, cadastro_em) "
                "VALUES (%(id)s, %(nome)s, %(email)s, %(cidade)s, %(estado)s, %(cadastro_em)s)",
                clientes,
            )
            cur.executemany(
                "INSERT INTO pedidos (id, cliente_id, data_pedido, status, valor_total, valor_itens, divergente) "
                "VALUES (%(id)s, %(cliente_id)s, %(data_pedido)s, %(status)s, %(valor_total)s, %(valor_itens)s, %(divergente)s)",
                pedidos,
            )
            cur.executemany(
                "INSERT INTO itens_pedido (pedido_id, linha, produto_id, quantidade, preco_unitario) "
                "VALUES (%(pedido_id)s, %(linha)s, %(produto_id)s, %(quantidade)s, %(preco_unitario)s)",
                itens,
            )


def contar(conexao):
    """Devolve a quantidade de linhas de cada tabela"""
    contagens = {}
    with conexao.cursor() as cur:
        for tabela in ("produtos", "clientes", "pedidos", "itens_pedido"):
            cur.execute(f"SELECT count(*) FROM {tabela}")
            contagens[tabela] = cur.fetchone()[0]
    return contagens