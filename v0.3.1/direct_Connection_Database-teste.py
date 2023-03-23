from database import Database

with Database('Testes') as db:
    results = db.execute_query("SELECT * FROM Tab")
    for row in results:
        print(row)
