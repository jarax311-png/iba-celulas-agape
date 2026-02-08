from app import app, db, Escola

ESCOLAS = [
    "Escola de líderes",
    "Escola de fundamentos", 
    "Escola de casais", 
    "Escola de apresentação de crianças",
    "Escola de finanças", 
    "Escola evangelismo e missões",
    "Escola de intercessão",
    "Angelim College"
]

def populate():
    with app.app_context():
        # Check again to be safe
        if Escola.query.count() > 0:
            print("Escolas já existem.")
            return

        print("Populando escolas...")
        for nome in ESCOLAS:
            print(f"Adicionando {nome}...")
            nova = Escola(nome=nome, descricao="Formação ministerial da igreja.", dia_horario="Consulte a liderança")
            db.session.add(nova)
        
        db.session.commit()
        print("Sucesso! Todas as escolas foram adicionadas.")

if __name__ == "__main__":
    populate()
