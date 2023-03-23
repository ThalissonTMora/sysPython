from flask import Flask, request
from database import Database

app = Flask(__name__)

@app.route('/api/log/rest', methods=['POST'])
def receive_notification():
    data = request.get_json()

    database = data['db_name']
    tabela = data['tabela']
    tipo = data['tipo']
    dados = data['dados']

    validacao = False

    with Database(database) as db:
        # Verifica se o tipo de operação é inserção
        if tipo == 'insert':
            for row in dados:
                if row['column'] == 'ActionType' and row['new_value'] == '114':
                    validacao = True
                elif row['column'] == 'ActionType' and row['new_value'] == '117':
                    validacao = True
            if validacao:
                db.execute_query("EXECUTE {0}.{1}.dbo.seu_codigo_TSQL".format(database, tabela))
        
        elif tipo == 'update':
            ''
        elif tipo == 'delete':
            ''


    return 'Ok'

if __name__ == '__main__':
    app.run()
