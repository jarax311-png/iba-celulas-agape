
import sqlite3
import os

def migrate_db(db_path):
    if not os.path.exists(db_path):
        print(f"Skipping {db_path} - not found")
        return

    print(f"Migrating {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Migrate CURTIDA
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='curtida'")
    if not cursor.fetchone():
        print("Table 'curtida' not found, skipping.")
    else:
        cursor.execute("PRAGMA table_info(curtida)")
        columns = [c[1] for c in cursor.fetchall()]
        if 'aviso_id' not in columns:
            print("Migrating 'curtida' table...")
            cursor.execute("CREATE TABLE curtida_new (id INTEGER PRIMARY KEY, evento_id INTEGER, membro_id INTEGER NOT NULL, aviso_id INTEGER, FOREIGN KEY(evento_id) REFERENCES evento(id), FOREIGN KEY(membro_id) REFERENCES membro(id), FOREIGN KEY(aviso_id) REFERENCES aviso(id))")
            cursor.execute("INSERT INTO curtida_new (id, evento_id, membro_id) SELECT id, evento_id, membro_id FROM curtida")
            cursor.execute("DROP TABLE curtida")
            cursor.execute("ALTER TABLE curtida_new RENAME TO curtida")
            print("'curtida' table migrated.")
        else:
            print("'curtida' table already up to date.")

    # 2. Migrate COMENTARIO
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comentario'")
    if not cursor.fetchone():
        print("Table 'comentario' not found, skipping.")
    else:
        cursor.execute("PRAGMA table_info(comentario)")
        columns = [c[1] for c in cursor.fetchall()]
        if 'aviso_id' not in columns:
            print("Migrating 'comentario' table...")
            cursor.execute("CREATE TABLE comentario_new (id INTEGER PRIMARY KEY, texto TEXT NOT NULL, data_criacao DATETIME, evento_id INTEGER, membro_id INTEGER NOT NULL, aviso_id INTEGER, parent_id INTEGER, FOREIGN KEY(evento_id) REFERENCES evento(id), FOREIGN KEY(membro_id) REFERENCES membro(id), FOREIGN KEY(aviso_id) REFERENCES aviso(id), FOREIGN KEY(parent_id) REFERENCES comentario(id))")
            cursor.execute("INSERT INTO comentario_new (id, texto, data_criacao, evento_id, membro_id, parent_id) SELECT id, texto, data_criacao, evento_id, membro_id, parent_id FROM comentario")
            cursor.execute("DROP TABLE comentario")
            cursor.execute("ALTER TABLE comentario_new RENAME TO comentario")
            print("'comentario' table migrated.")
        else:
            print("'comentario' table already up to date.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate_db('igreja.db')
    migrate_db('instance/igreja.db')
