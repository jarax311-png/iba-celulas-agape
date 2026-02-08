from app import app, db, Celula

with app.app_context():
    # Verifica se já existe para evitar duplicata
    existente = Celula.query.filter_by(nome="Ebenézer").first()
    if existente:
        print("Célula Ebenézer já existe.")
    else:
        nova_celula = Celula(
            nome="Ebenézer",
            lider="Ataide e Edileia (Treinamento: Davi)",
            endereco="Condomínio Village dos Pássaros V, Rua P, Quadra 12",
            numero="33",
            bairro="Pindai",
            cidade="São José de Ribamar",
            estado="MA",
            cep="65115-456",
            latitude=-2.5525882,
            longitude=-44.1213910
        )
        db.session.add(nova_celula)
        db.session.commit()
        print(f"Célula Ebenézer cadastrada com ID: {nova_celula.id}")
