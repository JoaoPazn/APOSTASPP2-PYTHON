from flask import Flask, request, jsonify
from flask_cors import CORS
import mariadb
import bcrypt  # Criptografia para senhas

app = Flask(__name__)
CORS(app)  # Permite requisições do HTML, assim o fontend se comunica com o backend

db_config = {  # Configurando a conexão com o banco de dados
    "host": "127.0.0.1",
    "user": "root",
    "password": "senha",  # NÃO SE ESQUECA DE ALTERAR A SENHA!
    "database": "jackpot_if",
}


def get_db_connection():  # Função para obter a conexão com o banco de dados
    try:
        conn = mariadb.connect(  # Conecta ao banco de dados, o ** serve para desempacotar o dicionário
            **db_config
        )
        return conn  # Retorna o objeto de conexão que será usado para executar os comandos SQL
    except mariadb.Error as e:  # Caso ocorra algum erro na conexão, ele será capturado aqui
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None


@app.route("/registrar", methods=["POST"])  # Rota para registrar um novo usuário
def registrar_usuario():
    dados = request.get_json()  # Obtém os dados enviados pelo frontend em formato JSON
    nome_usuario = dados["nome_usuario"]
    # O frontend envia a senha no campo "senha". O backend recebe e cria o hash.
    senha_texto = dados["senha"] 
    senha_hash = bcrypt.hashpw(  # Criptografando a senha com bcrypt
        senha_texto.encode("utf-8"), bcrypt.gensalt()
    )

    conn = get_db_connection()
    if conn is None:  # Se a conexão falhar, retorna um erro
        return jsonify({"erro": "Falha na conexão com o banco de dados"}), 500

    cursor = conn.cursor()  # Cria um cursor para executar comandos SQL
    try:
        cursor.execute(
            "INSERT INTO usuario (nome_usuario, senha_hash, gasto, ganho, saldoatual) VALUES (?, ?, 0, 0, 100.00)",
            (nome_usuario, senha_hash.decode("utf-8")),
        )
        conn.commit()
        return (
            jsonify({"sucesso": True, "mensagem": "Usuário criado com sucessso!"}),
            201,
        )
    except mariadb.IntegrityError:
        return jsonify({"erro": "Esse nome de usuário já existe."}), 409
    except mariadb.Error as e:
        return jsonify({"erro": f"erro no banco de dados: {e}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/login", methods=["POST"]) # Rota para fazer login
def login_usuario():
    dados = request.get_json() 
    nome_usuario = dados["nome_usuario"] # O frontend envia o nome de usuário no campo "nome_usuario" para o login. 
    senha_texto = dados["senha"] # O frontend também envia a senha no campo "senha" para o login.

    conn = get_db_connection()
    if conn is None:
        return jsonify({"erro": "Falha na conexão com o banco de dados"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT senha_hash, saldoatual FROM usuario WHERE nome_usuario = ?", (nome_usuario,)) # Busca o usuário no banco de dados
        usuario = cursor.fetchone()  # Obtém o primeiro resultado da consulta

        if usuario and bcrypt.checkpw(senha_texto.encode("utf-8"), usuario["senha_hash"].encode("utf-8")): # Se a senha bate, retorna sucesso e os dados do usuário
            return jsonify({"sucesso": True,  
                            "nome_usuario": nome_usuario, 
                            "saldo": usuario["saldoatual"]
                            }), 200
        else:
            return jsonify({"erro": "Usuário ou senha inválidos"}), 401 # Se não bate, retorna erro de autenticação
    except mariadb.Error as e:
        return jsonify({"erro": f"Erro no banco de dados: {e}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/aposta/esporte', methods=['POST']) # Rota para registrar uma aposta em esportes
def registrar_aposta_esporte(): 
    dados = request.get_json()
    login_usuario = dados['login_usuario']
    gasto = dados['gasto']
    ganho = dados['ganho']
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'erro': 'Falha na conexão com o banco de dados'}), 500

    cursor = conn.cursor()
    try:
        
        cursor.execute( # Insere o registro da aposta na tabela 'esporte'
            "INSERT INTO esporte (login_usuario, gastoesp, ganhoesp) VALUES (?, ?, ?)",
            (login_usuario, gasto, ganho)
        )

        saldo_final_aposta = ganho - gasto # Calcula o saldo final da aposta
        cursor.execute( # Atualiza o saldo do usuário na tabela 'usuario'
            "UPDATE usuario SET gasto = gasto + ?, ganho = ganho + ?, saldoatual = saldoatual + ? WHERE nome_usuario = ?",
            (gasto, ganho, saldo_final_aposta, login_usuario)
        ) 
        conn.commit() # Confirma as alterações no banco de dados

        cursor.execute("SELECT saldoatual FROM usuario WHERE nome_usuario = ?", (login_usuario,)) # Pega o saldo mais recente
        novo_saldo = cursor.fetchone()[0]

        return jsonify({'sucesso': True, 'novo_saldo': novo_saldo}), 200
    except mariadb.Error as e:
        conn.rollback() # Desfaz as operações se der erro
        return jsonify({'erro': f'Erro ao registrar aposta: {e}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/aposta/tigrinho', methods=['POST']) # Rota para registrar uma aposta no jogo Tigrinho
def registrar_aposta_tigrinho():
    dados = request.get_json()
    login_usuario = dados['login_usuario']
    gasto = dados['gasto']
    ganho = dados['ganho']
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'erro': 'Falha na conexão com o banco de dados'}), 500

    cursor = conn.cursor()
    try:
        
        cursor.execute( # Insere o registro da aposta na tabela 'tigrinho'
            "INSERT INTO tigrinho (login_usuario, gastotig, ganhotig) VALUES (?, ?, ?)",
            (login_usuario, gasto, ganho)
        )

        saldo_final_aposta = ganho - gasto # Calcula o saldo final da aposta
        cursor.execute( # Atualiza o saldo do usuário na tabela 'usuario'
            "UPDATE usuario SET gasto = gasto + ?, ganho = ganho + ?, saldoatual = saldoatual + ? WHERE nome_usuario = ?",
            (gasto, ganho, saldo_final_aposta, login_usuario)
        ) 
        conn.commit() # Confirma as alterações no banco de dados

        cursor.execute("SELECT saldoatual FROM usuario WHERE nome_usuario = ?", (login_usuario,)) # Pega o saldo mais recente
        novo_saldo = cursor.fetchone()[0]

        return jsonify({'sucesso': True, 'novo_saldo': novo_saldo}), 200
    except mariadb.Error as e:
        conn.rollback() # Desfaz as operações se der erro
        return jsonify({'erro': f'Erro ao registrar aposta: {e}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/aposta/roleta', methods=['POST']) # Rota para registrar uma aposta no três cores
def registrar_aposta_roleta():
    dados = request.get_json()
    login_usuario = dados['login_usuario']
    gasto = dados['gasto']
    ganho = dados['ganho']
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'erro': 'Falha na conexão com o banco de dados'}), 500

    cursor = conn.cursor()
    try:
        
        cursor.execute( # Insere o registro da aposta na tabela 'roleta'
            "INSERT INTO roleta (login_usuario, gastorol, ganhorol) VALUES (?, ?, ?)",
            (login_usuario, gasto, ganho)
        )

        saldo_final_aposta = ganho - gasto # Calcula o saldo final da aposta
        cursor.execute( # Atualiza o saldo do usuário na tabela 'usuario'
            "UPDATE usuario SET gasto = gasto + ?, ganho = ganho + ?, saldoatual = saldoatual + ? WHERE nome_usuario = ?",
            (gasto, ganho, saldo_final_aposta, login_usuario)
        ) 
        conn.commit() # Confirma as alterações no banco de dados

        cursor.execute("SELECT saldoatual FROM usuario WHERE nome_usuario = ?", (login_usuario,)) # Pega o saldo mais recente
        novo_saldo = cursor.fetchone()[0] 

        return jsonify({'sucesso': True, 'novo_saldo': novo_saldo}), 200
    except mariadb.Error as e:
        conn.rollback() # Desfaz as operações se der erro
        return jsonify({'erro': f'Erro ao registrar aposta: {e}'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/usuario/adicionar_saldo', methods=['POST']) # Rota para adicionar saldo ao usuário
def adicionar_saldo():
    dados = request.get_json()
    login_usuario = dados.get('login_usuario')
    valor = dados.get('valor')

    if not login_usuario or not isinstance(valor, (int, float)) or valor <= 0:
        return jsonify({'erro': 'Dados inválidos fornecidos.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'erro': 'Falha na conexão com o banco de dados'}), 500

    cursor = conn.cursor()
    try:
        cursor.execute( # Adiciona o valor ao saldo atual do usuário
            "UPDATE usuario SET saldoatual = saldoatual + ? WHERE nome_usuario = ?",
            (valor, login_usuario)
        )
        if cursor.rowcount == 0: # Verifica se algum usuário foi de fato atualizado
            return jsonify({'erro': 'Usuário não encontrado.'}), 404
            
        conn.commit()

        cursor.execute("SELECT saldoatual FROM usuario WHERE nome_usuario = ?", (login_usuario,)) # Pega o saldo mais recente para retornar ao frontend
        novo_saldo = cursor.fetchone()[0]

        return jsonify({'sucesso': True, 'novo_saldo': novo_saldo}), 200

    except mariadb.Error as e:
        conn.rollback()
        return jsonify({'erro': f'Erro ao adicionar saldo: {e}'}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True) # Executa o servidor Flask em modo de depuração
# O modo de depuração permite ver erros diretamente no navegador e recarrega o servidor automaticamente ao fazer alterações no código.
