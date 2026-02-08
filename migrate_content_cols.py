
import sqlite3

def migrate():
    conn = sqlite3.connect('igreja.db')
    cursor = conn.cursor()

    print("Iniciando migração das tabelas Story e Aviso...")

    # Colunas para Story
    try:
        cursor.execute("ALTER TABLE story ADD COLUMN autor_id INTEGER REFERENCES membro(id)")
        print("Coluna autor_id adicionada a Story")
    except sqlite3.OperationalError:
        print("Coluna autor_id já existe em Story")

    try:
        cursor.execute("ALTER TABLE story ADD COLUMN celula_id INTEGER REFERENCES celula(id)")
        print("Coluna celula_id adicionada a Story")
    except sqlite3.OperationalError:
        print("Coluna celula_id já existe em Story")

    try:
        cursor.execute("ALTER TABLE story ADD COLUMN rede_id INTEGER REFERENCES rede(id)")
        print("Coluna rede_id adicionada a Story")
    except sqlite3.OperationalError:
        print("Coluna rede_id já existe em Story")

    try:
        cursor.execute("ALTER TABLE story ADD COLUMN geracao_id INTEGER REFERENCES geracao(id)")
        print("Coluna geracao_id adicionada a Story")
    except sqlite3.OperationalError:
        print("Coluna geracao_id já existe em Story")

    # Colunas para Aviso
    try:
        cursor.execute("ALTER TABLE aviso ADD COLUMN rede_id INTEGER REFERENCES rede(id)")
        print("Coluna rede_id adicionada a Aviso")
    except sqlite3.OperationalError:
        print("Coluna rede_id já existe em Aviso")

    try:
        cursor.execute("ALTER TABLE aviso ADD COLUMN geracao_id INTEGER REFERENCES geracao(id)")
        print("Coluna geracao_id adicionada a Aviso")
    except sqlite3.OperationalError:
        print("Coluna geracao_id já existe em Aviso")
        
    # Adicionalmente, tornar celula_id opcional (SQLite não suporta ALTER COLUMN para remover NOT NULL facilmente, 
    # mas o SQLAlchemy vai lidar com isso se removermos a restrição no código, o banco continuará aceitando NULL se não houver restrição restrita no nível do SQLite que impeça).
    # Na verdade, em SQLite, se não foi definido como NOT NULL, aceita NULL.

    conn.commit()
    conn.close()
    print("Migração concluída!")

if __name__ == "__main__":
    migrate()
