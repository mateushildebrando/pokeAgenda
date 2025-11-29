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
    """ Rota para a página de cadastro de novos usuários. """
    # Se o formulário for enviado (método POST).
    if request.method == 'POST':
        # Coleta os dados do formulário.
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

        # Conecta ao banco de dados.
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
def login():
    """ Rota para a página de login do sistema. """
    if request.method == 'POST':
        email = request.form['email']
        senha_raw = request.form['senha_raw']
        
        conn = mysql.connector.connect(**db_config)
        # `dictionary=True` faz o cursor retornar os resultados como dicionários (útil para acessar colunas pelo nome).
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        # Busca o usuário pelo nome de usuário fornecido.
        cursor.execute("SELECT * FROM treinador WHERE email = %s", (email,))
        treinador = cursor.fetchone()
        
        cursor.close()
        conn.close()

        # Verifica se o usuário existe e se a senha fornecida corresponde ao hash salvo no banco.
        if treinador and check_password_hash(treinador['senha'], senha_raw):
            # Verifica se a conta não está desativada.
                        
            # Salva os dados do usuário na sessão para mantê-lo logado.
            session['id'] = treinador['id']
            session['nome'] = treinador['nome']
            session['email'] = treinador['email']
            session['cpf'] = treinador['cpf']
            session['foto'] = treinador['foto']
            session['cidade'] = treinador['cidade']
            session['senha'] = treinador['senha']
            
            # Redireciona para o perfil
            return redirect(url_for('perfil'))
            
        else:
            # Se o usuário não existir ou a senha estiver incorreta.
            flash("Usuário ou senha inválidos.", "erro")
            return redirect(url_for('login'))
            
    return render_template('login.html')


@app.route('/perfil')
def perfil():
    # Verifica login
    if not session.get("id"):
        flash("Você precisa estar logado para acessar o perfil.", "erro")
        return redirect(url_for("login"))

    treinador_id = session["id"]

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM treinador WHERE id=%s", (treinador_id,))
    treinador = cursor.fetchone()

    cursor.execute('SELECT p.nome, p.numero_pokedex, p.tipo, p.imagem_url, p.altura, p.peso, p.habilidades FROM treinador_pokemon tp JOIN pokemon p ON tp.pokemon_id = p.id JOIN treinador t ON tp.treinador_id = t.id WHERE tp.posicao = "time";')
    time = cursor.fetchall()

    cursor.execute('SELECT p.nome, p.numero_pokedex, p.tipo, p.imagem_url, p.altura, p.peso, p.habilidades FROM treinador_pokemon tp JOIN pokemon p ON tp.pokemon_id = p.id JOIN treinador t ON tp.treinador_id = t.id WHERE tp.posicao = "box";')
    box = cursor.fetchall()

    cursor.close()
    conn.close()

    if not treinador:
        flash("Erro ao carregar dados do usuário.", "erro")
        return redirect(url_for("login"))

    return render_template('perfil.html', treinador=treinador, time=time, box=box)


@app.route('/logout')
#função básica de sair da conta, basicamente apaga a memória do session
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for('login'))


# -------------------------------------------------------------------
# Editar perfil
# -------------------------------------------------------------------
@app.route('/perfil/editar/<int:id>', methods=['GET','POST'])
def editar_perfil(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form['cpf']
        cidade = request.form['cidade']

        cursor.execute("""
            UPDATE treinador 
            SET nome=%s, email=%s, cpf=%s, cidade=%s
            WHERE id=%s
        """, (nome, email, cpf, cidade, id))
        conn.commit()

        cursor.close()
        conn.close()
        flash("Perfil atualizado!", "sucesso")
        return redirect(url_for('perfil'))

    cursor.execute("SELECT * FROM treinador WHERE id=%s", (id,))
    treinador = cursor.fetchone()

    cursor.close()
    conn.close()

    if not treinador:
        flash("Treinador não encontrado.", "erro")
        return redirect(url_for('perfil'))

    return render_template('editar_perfil.html', treinador=treinador)


# -------------------------------------------------------------------
# Busca Pokémon
# -------------------------------------------------------------------
@app.route("/busca", methods=["GET","POST"])
def buscar_pokemon():
    if request.method == 'POST':
        termo = "%" + request.form['pokemon'] + "%"

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM pokemon
            WHERE nome LIKE %s OR numero_pokedex LIKE %s
        """, (termo, termo))

        pokemons = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template("resultados.html", pokemons=pokemons)

    return render_template("busca.html")


# -------------------------------------------------------------------
# Adicionar Pokémon ao time/box
# -------------------------------------------------------------------
@app.route("/adicionar_pokemon", methods=["GET", "POST"])
def adicionar_pokemon():
    treinador_id = session.get("id")

    if not treinador_id:
        flash("Você precisa estar logado para adicionar pokémons.", "erro")
        return redirect(url_for("login"))

    # GET → mostra formulário
    if request.method == "GET":
        return render_template("adicionar_pokemon.html")

    # POST → processa formulário
    pokemon = request.form["pokemon"].strip()

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM pokemon WHERE nome=%s OR numero_pokedex=%s",
                   (pokemon, pokemon))
    resultado = cursor.fetchone()

    if not resultado:
        flash("Pokémon não encontrado.", "erro")
        cursor.close()
        conn.close()
        return redirect(url_for("adicionar_pokemon"))

    pokemon_id = resultado["id"]

    cursor.execute("""
        SELECT COUNT(*) AS total 
        FROM treinador_pokemon 
        WHERE posicao='time' AND treinador_id=%s
    """, (treinador_id,))
    count = cursor.fetchone()['total']

    posicao = "time" if count < 6 else "box"
    msg = "Pokémon adicionado ao time!" if posicao == "time" else "Time cheio, enviado ao box!"

    cursor.execute("""
        INSERT INTO treinador_pokemon (treinador_id, pokemon_id, posicao)
        VALUES (%s, %s, %s)
    """, (treinador_id, pokemon_id, posicao))
    conn.commit()

    cursor.close()
    conn.close()

    flash(msg, "sucesso")
    return redirect(url_for("perfil"))



# -------------------------------------------------------------------
# Remover Pokémon
# -------------------------------------------------------------------
@app.route("/remover/<int:relacao_id>")
def remover_pokemon(relacao_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM treinador_pokemon WHERE id=%s", (relacao_id,))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Pokémon removido!", "sucesso")
    return redirect(url_for("perfil"))


# -------------------------------------------------------------------
# Trocar Pokémon do time ↔ box
# -------------------------------------------------------------------
@app.route("/trocar/<int:relacao_id>")
def trocar_pokemon(relacao_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT posicao FROM treinador_pokemon WHERE id=%s", (relacao_id,))
    rel = cursor.fetchone()

    if not rel:
        flash("Pokémon não encontrado.", "erro")
        return redirect(url_for("perfil"))

    nova = "box" if rel["posicao"] == "time" else "time"

    # verificar limite do time
    if nova == "time":
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM treinador_pokemon
            WHERE treinador_id=%s AND posicao='time'
        """, (session['id'],))
        count = cursor.fetchone()['total']
        if count >= 6:
            flash("Seu time já tem 6 pokémons!", "erro")
            return redirect(url_for("perfil"))

    cursor.execute("""
        UPDATE treinador_pokemon SET posicao=%s WHERE id=%s
    """, (nova, relacao_id))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Pokémon movido!", "sucesso")
    return redirect(url_for("perfil"))


# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)