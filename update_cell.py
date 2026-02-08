from app import app, db, Celula

with app.app_context():
    celula = Celula.query.filter_by(nome="Ebenézer").first()
    if celula:
        celula.lider_treinamento = "Davi"
        db.session.commit()
        print(f"Célula {celula.nome} atualizada! Líder em treinamento: {celula.lider_treinamento}")
    else:
        print("Célula Ebenézer não encontrada.")
