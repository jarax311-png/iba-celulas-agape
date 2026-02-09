import sqlite3
import psycopg2
import os
from urllib.parse import urlparse

# CONFIGURAÇÃO
SQLITE_DB = 'igreja.db'
POSTGRES_URL = os.environ.get('DATABASE_URL') # Pega da variável de ambiente ou define manual

def migrate_data():
    if not POSTGRES_URL:
        print("❌ ERRO: A variável de ambiente DATABASE_URL não está definida.")
        print("Defina com: $env:DATABASE_URL='seu_endereco_postgres_copiado_do_render'")
        return

    print(f"🔄 Iniciando migração de {SQLITE_DB} para Postgres...")

    # Conectar SQLite
    conn_sqlite = sqlite3.connect(SQLITE_DB)
    conn_sqlite.row_factory = sqlite3.Row
    cursor_sqlite = conn_sqlite.cursor()

    # Conectar Postgres
    try:
        conn_pg = psycopg2.connect(POSTGRES_URL)
        cursor_pg = conn_pg.cursor()
    except Exception as e:
        print(f"❌ Erro ao conectar no Postgres: {e}")
        return

    # Ordem de migração (respeitando Foreign Keys)
    tables = ['rede', 'geracao', 'celula', 'membro', 'aviso', 'evento', 'story', 'reuniao', 
              'comentario', 'curtida', 'curtida_comentario']

    for table in tables:
        print(f"📦 Migrando tabela: {table}...")
        
        # Ler do SQLite
        try:
            cursor_sqlite.execute(f"SELECT * FROM {table}")
            rows = cursor_sqlite.fetchall()
        except sqlite3.OperationalError:
            print(f"⚠️ Tabela {table} não encontrada no SQLite. Pulando.")
            continue

        if not rows:
            print(f"   ℹ️ Tabela vazia.")
            continue

        # Inserir no Postgres
        columns = rows[0].keys()
        cols_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        query = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING"

        for row in rows:
            try:
                values = [dict(row)[c] for c in columns]
                # Converter booleans do SQLite (0/1) para True/False se necessário, 
                # mas psycopg2 costuma lidar bem.
                cursor_pg.execute(query, values)
            except Exception as e:
                print(f"   ❌ Erro ao inserir linha {dict(row)['id']}: {e}")
                conn_pg.rollback()
        
        conn_pg.commit()
        print(f"   ✅ {len(rows)} registros migrados.")

        # Atualizar sequências (para o ID auto-increment não dar erro)
        try:
            cursor_pg.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), coalesce(max(id),0) + 1, false) FROM {table};")
            conn_pg.commit()
        except:
            pass # Algumas tabelas podem não ter sequence, ignora

    print("\n🎉 Migração concluída com sucesso!")
    conn_sqlite.close()
    conn_pg.close()

if __name__ == "__main__":
    migrate_data()
