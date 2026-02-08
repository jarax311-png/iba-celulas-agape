from app import app, db, Escola
import sqlite3

# Lista de escolas dada pelo usuário
ESCOLAS_INCIAIS = [
    "Escola de líderes",
    "Escola de fundamentos", 
    "Escola de casais", 
    "Escola de apresentação de crianças",
    "Escola de finanças", 
    "Escola evangelismo e missões",
    "Escola de intercessão",
    "Angelim College"
]

def migrate():
    with app.app_context():
        # Cria as tabelas novas
        db.create_all()
        print("Tabelas criadas/verificadas.")

        # Popula Escolas se estiver vazio
        if Escola.query.count() == 0:
            print("Populando escolas...")
            for nome in ESCOLAS_INCIAIS:
                nova = Escola(nome=nome, descricao="Formação para membros.")
                db.session.add(nova)
            db.session.commit()
            print("Escolas adicionadas!")
        else:
            print("Escolas já existem.")

if __name__ == "__main__":
    migrate()
