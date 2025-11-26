from config import *

@app.route('/')
# rota inicial que redireciona o user para seu perfil ou para login.

def home():
    if session.get('id'):
        return redirect(url_for('perfil'))
    else:
        return redirect(url_for('login'))


@app.route('/cadastro', methods=['GET', 'POST'])
#rota de cadastro, onde pede-se: nome, email, cpf, cidade e senha, a foto vai padrão e pode ser alterada futuramente

def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form['cpf']
        foto = 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp'
        cidade = request.form['cidade']
        senha_raw = request.form['senha_raw']
        senha = generate_password_hash(senha_raw)

#verifica se tudo foi preenchido
        if not all([nome, email, cpf, cidade, senha_raw]):
            flash("Todos os campos são obrigatórios!", "erro")
            return redirect(url_for('cadastro'))

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(buffered=True)
#procura se o user já foi cadastrado
        cursor.execute("SELECT * FROM treinador WHERE email = %s OR cpf = %s", (email, cpf))
        if cursor.fetchone():
            flash("E-mail ou CPF já cadastrado.", "erro")
            cursor.close()
            conn.close()
            return redirect(url_for('cadastro'))
#se não foi cadastrado ainda cadastra agora   
        cursor.execute("""INSERT INTO treinador (nome, email, cpf, foto, cidade, senha)
                          VALUES (%s, %s, %s, %s, %s, %s)""", (nome, email, cpf, foto, cidade, senha))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("Cadastro realizado com sucesso! Você já pode fazer login.", "sucesso")
        return redirect(url_for('login'))
        
# Se for uma requisição GET, apenas renderiza a página de cadastro.
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
#função de login. Pede email e senha.
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        senha_raw = request.form['senha_raw'].strip()
        
#verifica se tudo foi preenchido
        if not all([email, senha_raw]):
            flash("Todos os campos são obrigatórios!", "erro")
            return redirect(url_for('cadastro'))

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True, buffered=True)
#procura no banco
        cursor.execute("SELECT * FROM treinador WHERE email = %s", (email,))
        treinador = cursor.fetchone()
        
        cursor.close()
        conn.close()
#guarda os dados do user
        if treinador and check_password_hash(treinador['senha'], senha_raw):
            session['id'] = treinador['id']
            session['nome'] = treinador['nome']
            session['email'] = treinador['email']
            session['cpf'] = treinador['cpf']
            session['foto'] = treinador['foto']
            session['cidade'] = treinador['cidade']
#redireciona para a tela de perfil
        if treinador:
            return redirect(url_for('perfil'))
#caso não encontre, retorna erro       
        else:
            flash("Usuário ou senha inválidos.", "erro")
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/perfil')
#exibe as informações do treinador na tela
def perfil():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM treinador")
    treinador = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('perfil.html', treinador=treinador)

@app.route('/logout')
#função básica de sair da conta, basicamente apaga a memória do session
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/perfil/editar/<int:id>', methods=['GET', 'POST'])
#função para editar o user
def editar_perfil(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
#coleta e atualização dos dados
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form['cpf']
        cidade = request.form['cidade']

        query = """
            UPDATE treinador SET nome = %s, email = %s, cpf = %s, cidade = %s
            WHERE id = %s
        """
        cursor.execute(query, (nome, email, cpf, cidade, id))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Perfil atualizado com sucesso!", "sucesso")
        return redirect(url_for('perfil'))
#procurando o usuario no banco de dados
    cursor.execute("SELECT * FROM treinador WHERE id = %s", (id,))
    treinador = cursor.fetchone()
    if not treinador:
        flash("Treinador não encontrado.", "erro")
        return redirect(url_for('perfil'))
    
    cursor.close()
    conn.close()
    return render_template('editar_perfil.html', treinador=treinador)

@app.route("/busca", methods=["GET", "POST"])
def buscar_pokemon():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        pokemon = request.form['pokemon']
  
        query = """
            SELECT nome, tipo, imagem, altura, peso, habilidades
            FROM pokemon 
            WHERE nome LIKE %s 
               OR numero_pokedex LIKE %s
        """
    
        cursor.execute(query, (pokemon, pokemon))
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template("resultados.html", pokemons=resultados)
    
    #return principal ainda não sei, pois provavelmente essa função será associada a uma barra de pesquisa, e não uma página separada

@app.route("/adicionar_pokemon", methods=["POST"])
def adicionar_pokemon():
    treinador_id = session.get("id")
    pokemon = request.form["pokemon"]

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Buscar ID do Pokémon
    query = """
        SELECT id 
        FROM pokemon 
        WHERE nome = %s OR numero_pokedex = %s
    """
    cursor.execute(query, (pokemon, pokemon))
    resultado = cursor.fetchone()

    if not resultado:
        flash("Pokémon não encontrado.")
        return redirect(url_for("pagina_de_adicionar"))

    pokemon_id = resultado["id"]

    # Checar quantos Pokémon há no time
    query = """
        SELECT COUNT(id) AS total 
        FROM treinador_pokemon 
        WHERE posicao = "time" AND treinador_id = %s
    """
    cursor.execute(query, (treinador_id,))
    count = cursor.fetchone()["total"]

    # Inserção
    if count < 6:
        posicao = "time"
        flash("Pokémon adicionado ao time!")
    else:
        posicao = "box"
        flash("Time cheio, Pokémon enviado à box!")

    insert = """
        INSERT INTO treinador_pokemon (treinador_id, pokemon_id, posicao)
        VALUES (%s, %s, %s)
    """
    cursor.execute(insert, (treinador_id, pokemon_id, posicao))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("pagina_que_exibe_os_pokemons"))
