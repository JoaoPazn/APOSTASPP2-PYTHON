from flask import Flask, request, jsonify
from flask_cors import CORS
# --- ALTERAÇÃO AQUI: Importa a biblioteca do MySQL em vez do MariaDB ---
import mysql.connector
import bcrypt  # Criptografia para senhas
from datetime import datetime # Importa o módulo datetime para lidar com o tempo

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
        # --- ALTERAÇÃO AQUI: Usa mysql.connector.connect ---
        conn = mysql.connector.connect(  # Conecta ao banco de dados, o ** serve para desempacotar o dicionário
            **db_config
        )
        return conn  # Retorna o objeto de conexão que será usado para executar os comandos SQL
    # --- ALTERAÇÃO AQUI: Captura o erro específico do MySQL ---
    except mysql.connector.Error as e:  # Caso ocorra algum erro na conexão, ele será capturado aqui
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
        # --- ALTERAÇÃO AQUI: O placeholder padrão do mysql-connector é %s ---
        cursor.execute(
            "INSERT INTO usuario (nome_usuario, senha_hash, gasto, ganho, saldoatual) VALUES (%s, %s, 0, 0, 100.00)",
            (nome_usuario, senha_hash.decode("utf-8")),
        )
        conn.commit()
        return (
            jsonify({"sucesso": True, "mensagem": "Usuário criado com sucessso!"}),
            201,
        )
    # --- ALTERAÇÃO AQUI: Captura os erros específicos do MySQL ---
    except mysql.connector.IntegrityError:
        return jsonify({"erro": "Esse nome de usuário já existe."}), 409
    except mysql.connector.Error as e:
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
        # Busca também o ID do usuário 
        # --- ALTERAÇÃO AQUI: Placeholder de ? para %s ---
        cursor.execute("SELECT id, senha_hash, saldoatual FROM usuario WHERE nome_usuario = %s", (nome_usuario,)) # Busca o usuário no banco de dados
        usuario = cursor.fetchone()  # Obtém o primeiro resultado da consulta

        if usuario and bcrypt.checkpw(senha_texto.encode("utf-8"), usuario["senha_hash"].encode("utf-8")): # Se a senha bate, retorna sucesso e os dados do usuário
            
            # Inicia uma nova sessão
            id_usuario = usuario['id']
            # --- ALTERAÇÃO AQUI: Placeholder de ? para %s ---
            cursor.execute("INSERT INTO sessoes_usuario (id_usuario) VALUES (%s)", (id_usuario,))
            conn.commit()
            id_sessao = cursor.lastrowid # Pega o ID da sessão que acabamos de criar

            return jsonify({
                "sucesso": True,  
                "nome_usuario": nome_usuario, 
                "saldo": usuario["saldoatual"],
                "id_usuario": id_usuario, # Envia o id do usuário para o frontend
                "id_sessao": id_sessao # Envia o id da sessão para o frontend
            }), 200
        else:
            return jsonify({"erro": "Usuário ou senha inválidos"}), 401 # Se não bate, retorna erro de autenticação
    # --- ALTERAÇÃO AQUI: Captura o erro específico do MySQL ---
    except mysql.connector.Error as e:
        return jsonify({"erro": f"Erro no banco de dados: {e}"}), 500
    finally:
        cursor.close()
        conn.close()

# Rota para finalizar a sessão do usuário
@app.route("/logout", methods=["POST"])
def logout_usuario():
    dados = request.get_json()
    id_sessao = dados.get('id_sessao')

    if not id_sessao:
        return jsonify({"erro": "ID da sessão não fornecido."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'erro': 'Falha na conexão com o banco de dados'}), 500

    cursor = conn.cursor()
    try:
        # Atualiza a sessão com a data de logout e calcula a duração em minutos
        # --- ALTERAÇÃO AQUI: Placeholder de ? para %s ---
        cursor.execute(
            """
            UPDATE sessoes_usuario 
            SET data_logout = CURRENT_TIMESTAMP, 
                duracao_minutos = TIMESTAMPDIFF(MINUTE, data_login, CURRENT_TIMESTAMP)
            WHERE id_sessao = %s AND data_logout IS NULL
            """,
            (id_sessao,)
        )
        conn.commit()
        return jsonify({"sucesso": True, "mensagem": "Sessão finalizada com sucesso."}), 200
    # --- ALTERAÇÃO AQUI: Captura o erro específico do MySQL ---
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({'erro': f'Erro ao finalizar sessão: {e}'}), 500
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
        # --- ALTERAÇÃO AQUI: Placeholder de ? para %s ---
        cursor.execute( "INSERT INTO esporte (login_usuario, gastoesp, ganhoesp) VALUES (%s, %s, %s)", (login_usuario, gasto, ganho) )
        saldo_final_aposta = ganho - gasto
        # --- ALTERAÇÃO AQUI: Placeholder de ? para %s ---
        cursor.execute( "UPDATE usuario SET gasto = gasto + %s, ganho = ganho + %s, saldoatual = saldoatual + %s WHERE nome_usuario = %s", (gasto, ganho, saldo_final_aposta, login_usuario) ) 
        conn.commit()
        # --- ALTERAÇÃO AQUI: Placeholder de ? para %s ---
        cursor.execute("SELECT saldoatual FROM usuario WHERE nome_usuario = %s", (login_usuario,))
        novo_saldo = cursor.fetchone()[0]
        return jsonify({'sucesso': True, 'novo_saldo': novo_saldo}), 200
    # --- ALTERAÇÃO AQUI: Captura o erro específico do MySQL ---
    except mysql.connector.Error as e:
        conn.rollback()
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
        # --- ALTERAÇÃO AQUI: Placeholder de ? para %s ---
        cursor.execute( "INSERT INTO tigrinho (login_usuario, gastotig, ganhotig) VALUES (%s, %s, %s)", (login_usuario, gasto, ganho) )
        saldo_final_aposta = ganho - gasto
        # --- ALTERAÇÃO AQUI: Placeholder de ? para %s ---
        cursor.execute( "UPDATE usuario SET gasto = gasto + %s, ganho = ganho + %s, saldoatual = saldoatual + %s WHERE nome_usuario = %s", (gasto, ganho, saldo_final_aposta, login_usuario) ) 
        conn.commit()
        # --- ALTERAÇÃO AQUI: Placeholder de ? para %s ---
        cursor.execute("SELECT saldoatual FROM usuario WHERE nome_usuario = %s", (login_usuario,))
        novo_saldo = cursor.fetchone()[0]
        return jsonify({'sucesso': True, 'novo_saldo': novo_saldo}), 200
    # --- ALTERAÇÃO AQUI: Captura o erro específico do MySQL ---
    except mysql.connector.Error as e:
        conn.rollback()
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
        # --- ALTERAÇÃO AQUI: Placeholder de ? para %s ---
        cursor.execute( "INSERT INTO roleta (login_usuario, gastorol, ganhorol) VALUES (%s, %s, %s)", (login_usuario, gasto, ganho) )
        saldo_final_aposta = ganho - gasto
        # --- ALTERAÇÃO AQUI: Placeholder de ? para %s ---
        cursor.execute( "UPDATE usuario SET gasto = gasto + %s, ganho = ganho + %s, saldoatual = saldoatual + %s WHERE nome_usuario = %s", (gasto, ganho, saldo_final_aposta, login_usuario) ) 
        conn.commit()
        # --- ALTERAÇÃO AQUI: Placeholder de ? para %s ---
        cursor.execute("SELECT saldoatual FROM usuario WHERE nome_usuario = %s", (login_usuario,))
        novo_saldo = cursor.fetchone()[0] 
        return jsonify({'sucesso': True, 'novo_saldo': novo_saldo}), 200
    # --- ALTERAÇÃO AQUI: Captura o erro específico do MySQL ---
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({'erro': f'Erro ao registrar aposta: {e}'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/usuario/adicionar_saldo', methods=['POST']) # Rota para adicionar saldo ao usuário
def adicionar_saldo():
    dados = request.get_json()
    id_usuario = dados.get('id_usuario') # Recebe o id_usuario em vez do nome
    valor = dados.get('valor')

    if not id_usuario or not isinstance(valor, (int, float)) or valor <= 0:
        return jsonify({'erro': 'Dados inválidos fornecidos.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'erro': 'Falha na conexão com o banco de dados'}), 500

    cursor = conn.cursor(dictionary=True) # Usar dicionário para pegar o nome do usuário
    try:
        # Insere no log de depósitos 
        # --- ALTERAÇÃO AQUI: Placeholder de ? para %s ---
        cursor.execute("INSERT INTO log_depositos (id_usuario, valor_adicionado) VALUES (%s, %s)", (id_usuario, valor))

        # Atualiza o saldo (usando o ID para mais segurança)
        # --- ALTERAÇÃO AQUI: Placeholder de ? para %s ---
        cursor.execute( "UPDATE usuario SET saldoatual = saldoatual + %s WHERE id = %s", (valor, id_usuario) )
        
        if cursor.rowcount == 0: # Verifica se algum usuário foi de fato atualizado
            conn.rollback() # Desfaz o insert no log se o usuário não for encontrado
            return jsonify({'erro': 'Usuário não encontrado.'}), 404
            
        conn.commit()

        # Pega o saldo mais recente para retornar ao frontend
        # --- ALTERAÇÃO AQUI: Placeholder de ? para %s ---
        cursor.execute("SELECT saldoatual FROM usuario WHERE id = %s", (id_usuario,))
        resultado = cursor.fetchone()
        novo_saldo = resultado['saldoatual']

        return jsonify({'sucesso': True, 'novo_saldo': novo_saldo}), 200

    # --- ALTERAÇÃO AQUI: Captura o erro específico do MySQL ---
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({'erro': f'Erro ao adicionar saldo: {e}'}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True) # O modo de depuração permite ver erros diretamente no navegador e recarrega o servidor automaticamente ao fazer alterações no código.

