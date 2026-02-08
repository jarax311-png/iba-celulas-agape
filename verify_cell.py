from app import app, Celula

with app.app_context():
    celula = Celula.query.filter_by(nome="Ebenézer").first()
    if celula:
        print(f"Célula encontrada: {celula.nome} - ID: {celula.id} - Lat/Long: {celula.latitude}/{celula.longitude}")
    else:
        print("Célula NÃO encontrada.")
