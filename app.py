#importação dos pacotes necessários para que o site funcione.
from flask import Flask, render_template, url_for, redirect, session, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import mysql.connector
import os

#iniciação do app, conexão com o banco de dados e a variável onde definirá o caminho da foto do user.
app = Flask(__name__)
app.secret_key = 'gremio'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'pokebanco'
}
CAMINHO_FOTOS = "static/fotosperfil"

# -------------------------------------------------------------------
# Rota principal, redireciona para perfil, caso logado, ou para login em caso contrário.
# -------------------------------------------------------------------
@app.route('/')
def home():
    if session.get('id'):
        return redirect(url_for('perfil'))
    else:
        return redirect(url_for('login'))

# -------------------------------------------------------------------
# Cadastro de treinador, onde pede-se: nome, email, cpf, cidade e senha, a foto vai padrão e pode ser alterada futuramente.
# -------------------------------------------------------------------
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    
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
        
        #verifica se tudo foi preenchido.
        if not all([nome, email, cpf, cidade, senha_raw]):
            flash("Todos os campos são obrigatórios!", "erro")
            return redirect(url_for('cadastro'))

        # Conecta ao banco de dados.
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(buffered=True)
        
        #procura se o user já foi cadastrado.
        cursor.execute("SELECT * FROM treinador WHERE email = %s OR cpf = %s", (email, cpf))
        if cursor.fetchone():
            flash("E-mail ou CPF já cadastrado.", "erro")
            cursor.close()
            conn.close()
            return redirect(url_for('cadastro'))
        
        #se não foi cadastrado ainda cadastra agora.
        cursor.execute("""INSERT INTO treinador (nome, email, cpf, foto, cidade, senha)
                          VALUES (%s, %s, %s, %s, %s, %s)""", (nome, email, cpf, foto, cidade, senha))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("Cadastro realizado com sucesso! Você já pode fazer login.", "sucesso")
        return redirect(url_for('login'))
        
    # Se for uma requisição GET, apenas renderiza a página de cadastro.
    return render_template('cadastro.html')

# -------------------------------------------------------------------
# Rota de login, pde-se email e senha.
# -------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Caso formulário for enviado:
    if request.method == 'POST':
        email = request.form['email']
        senha_raw = request.form['senha_raw']
        
        # Conecta ao banco de dados.
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True, buffered=True)
        #'dictionary=True' faz o cursor retornar os resultados como dicionários (útil para acessar colunas pelo nome).
        
        #Busca o user pelo email fornecido.
        cursor.execute("SELECT * FROM treinador WHERE email = %s", (email,))
        treinador = cursor.fetchone()
        
        cursor.close()
        conn.close()

        # Verifica se o usuer existe e se a senha fornecida corresponde ao hash salvo no banco.
        if treinador and check_password_hash(treinador['senha'], senha_raw):
                                    
            # Salva os dados do usuário na sessão para mantê-lo logado.
            session['id'] = treinador['id']
            session['nome'] = treinador['nome']
            session['email'] = treinador['email']
            session['cpf'] = treinador['cpf']
            session['foto'] = treinador['foto']
            session['cidade'] = treinador['cidade']
            session['senha'] = treinador['senha']
            
            # Redireciona para o perfil.
            return redirect(url_for('perfil'))
            
        else:
            # Se o usuário não existir ou a senha estiver incorreta.
            flash("Usuário ou senha inválidos.", "erro")
            return redirect(url_for('login'))

    #página carregada em casos GET.   
    return render_template('login.html')

# -------------------------------------------------------------------
# Perfil, página principal, que exibe os dados do user, os pokemons no time e no box.
# -------------------------------------------------------------------
@app.route('/perfil')
def perfil():
    # Verifica login.
    if not session.get("id"):
        flash("Você precisa estar logado para acessar o perfil.", "erro")
        return redirect(url_for("login"))

    treinador_id = session["id"]
    #Conecta ao banco.
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    #Pega todos os dados do treinador.
    cursor.execute("SELECT * FROM treinador WHERE id=%s", (treinador_id,))
    treinador = cursor.fetchone()

    #Pega todos os pokemons do time de um treinador.
    cursor.execute('''
        SELECT p.nome, p.numero_pokedex, p.tipo, p.imagem_url, p.altura, p.peso, p.habilidades, tp.id
        FROM treinador_pokemon tp
        JOIN pokemon p ON tp.pokemon_id = p.id
        WHERE tp.posicao = "time" AND tp.treinador_id = %s
        ORDER BY nome ASC
    ''', (treinador_id,))
    time = cursor.fetchall()

    #Pega todos os pokemons do box de um treinador.
    cursor.execute('''
        SELECT p.nome, p.numero_pokedex, p.tipo, p.imagem_url, p.altura, p.peso, p.habilidades, tp.id
        FROM treinador_pokemon tp
        JOIN pokemon p ON tp.pokemon_id = p.id
        WHERE tp.posicao = "box" AND tp.treinador_id = %s
        ORDER BY nome ASC
    ''', (treinador_id,))
    box = cursor.fetchall()

    cursor.close()
    conn.close()

    #Carrega a página com os dados do treinador, os pokemons no time e os pokemons no box.
    return render_template('perfil.html', treinador=treinador, time=time, box=box)

# -------------------------------------------------------------------
#Função básica de sair da conta, basicamente apaga a memória do session.
# -------------------------------------------------------------------
@app.route('/logout')
def logout():
    #Apaga os dados da sessão.
    session.clear()
    flash("Você saiu da sua conta.", "sucesso")
    #Redireciona para o login.
    return redirect(url_for('login'))


# -------------------------------------------------------------------
# Editar perfil.
# -------------------------------------------------------------------
@app.route('/perfil/editar/<int:id>', methods=['GET','POST'])
def editar_perfil(id):
    #Conecta ao banco.
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    #Ao enviar o formulário, recebe os novos dados
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form['cpf']
        cidade = request.form['cidade']
        foto = request.files['foto']

        #Processa, salva e gera o caminho de foto do usuário.
        if foto and foto.filename != '':
            nome_arquivo = secure_filename(foto.filename)
            caminho_foto = os.path.join(CAMINHO_FOTOS, nome_arquivo)
            foto.save(caminho_foto)
            url_foto = f'/static//fotosperfil/{nome_arquivo}'

        else:
            url_foto = 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp'

        #Atualiza os dados do usuário no banco.   
        cursor.execute("""
            UPDATE treinador 
            SET nome=%s, email=%s, cpf=%s, cidade=%s, foto=%s
            WHERE id=%s
        """, (nome, email, cpf, cidade, url_foto, id))
        conn.commit()

        cursor.close()
        conn.close()
        flash("Perfil atualizado!", "sucesso")
        #Retorna ao perfil.
        return redirect(url_for('perfil'))

    #Em casos get, seleciona os dados do treinador.
    cursor.execute("SELECT * FROM treinador WHERE id=%s", (id,))
    treinador = cursor.fetchone()

    cursor.close()
    conn.close()
    
    #Caso não encontre o treinador no banco.
    if not treinador:
        flash("Treinador não encontrado.", "erro")
        return redirect(url_for('perfil'))
    
    #Recarrega a página com os dados do treinador.
    return render_template('editar_perfil.html', treinador=treinador)


# -------------------------------------------------------------------
# Busca Pokémon
# -------------------------------------------------------------------
@app.route("/busca", methods=["GET","POST"])
def buscar_pokemon():

    #Conecta ao banco.
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    #Carrega lista com todos os pokemons
    cursor.execute("SELECT id, nome FROM pokemon ORDER BY id")
    lista_pokemon = cursor.fetchall()

    #Em casos de POST, recebe letras ou numéros e exibe pokemons com estas letras ou números para serem selecionados.
    if request.method == 'POST':
        termo = "%" + request.form['pokemon'] + "%"
        
        #Busca no banco.
        cursor.execute("""
            SELECT * FROM pokemon
            WHERE nome LIKE %s OR numero_pokedex LIKE %s
        """, (termo, termo))

        pokemons = cursor.fetchall()
        cursor.close()
        conn.close()
        #Recarrega uma página com apenas um pokemon específico, escolhido.
        return render_template("resultados.html", pokemons=pokemons)

    cursor.close()
    conn.close()
    #Exibe em tempo real a página de busca e opções de pokemons para ser escolhidos.
    return render_template("busca.html", lista_pokemon=lista_pokemon)

# -------------------------------------------------------------------
# Adicionar Pokémon ao time/box.
# -------------------------------------------------------------------
@app.route("/adicionar_pokemon", methods=["GET", "POST"])
def adicionar_pokemon():
    treinador_id = session.get("id")

    #se user não estiver logado, não pode adicionar pokemons.
    if not treinador_id:
        flash("Você precisa estar logado para adicionar pokémons.", "erro")
        return redirect(url_for("login"))

    # GET, mostra formulário.
    if request.method == "GET":
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        #Exibe a lista com todos os pokemons, para facilitar a escolha.
        cursor.execute("SELECT id, nome, numero_pokedex FROM pokemon ORDER BY numero_pokedex")
        lista_pokemons = cursor.fetchall()

        cursor.close()
        conn.close()
        return render_template("adicionar_pokemon.html", lista_pokemons=lista_pokemons)


    # POST,  processa formulário.
    pokemon = request.form["pokemon"].strip()

    # Conecta com o banco.
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Verifica se o pokémon existe.
    cursor.execute("SELECT id FROM pokemon WHERE nome=%s OR numero_pokedex=%s",
                   (pokemon, pokemon))
    resultado = cursor.fetchone()

    if not resultado:
        flash("Pokémon não encontrado.", "erro")
        cursor.close()
        conn.close()
        return redirect(url_for("adicionar_pokemon"))

    pokemon_id = resultado["id"]

    # Select para evitar duplicatas.
    cursor.execute("""
        SELECT id FROM treinador_pokemon
        WHERE treinador_id=%s AND pokemon_id=%s
    """, (treinador_id, pokemon_id))

    ja_tem = cursor.fetchone()

    if ja_tem:
        flash("Você já possui esse Pokémon no seu time ou box!", "erro")
        cursor.close()
        conn.close()
        return redirect(url_for("perfil"))

    # Verifica se o time está cheio.
    cursor.execute("""
        SELECT COUNT(*) AS total 
        FROM treinador_pokemon 
        WHERE posicao='time' AND treinador_id=%s
    """, (treinador_id,))
    count = cursor.fetchone()['total']

    #Se tiver espaço no time, adiciona no time, senão no box
    posicao = "time" if count < 6 else "box"
    msg = "Pokémon adicionado ao time!" if posicao == "time" else "Time cheio — enviado ao box!"

    # Insert.
    cursor.execute("""
        INSERT INTO treinador_pokemon (treinador_id, pokemon_id, posicao)
        VALUES (%s, %s, %s)
    """, (treinador_id, pokemon_id, posicao))
    conn.commit()

    cursor.close()
    conn.close()

    #Retorna ao perfil.
    flash(msg, "sucesso")
    return redirect(url_for("perfil"))



# -------------------------------------------------------------------
# Remover Pokémon
# -------------------------------------------------------------------
@app.route("/remover/<int:relacao_id>")
def remover_pokemon(relacao_id):

    treinador_id = session.get("id")
    # Conecta ao banco.
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Verifica se o pokemon está no time ou no box, para não deixar o time com 5 pokemons.
    cursor.execute("SELECT posicao FROM treinador_pokemon WHERE id=%s", (relacao_id,))
    resultado_posicao = cursor.fetchone()

    if not resultado_posicao:
        flash("Pokémon não encontrado.", "erro")
        return redirect(url_for("perfil"))

    posicao = resultado_posicao["posicao"]

    # Remove o pokemon.
    cursor.execute("DELETE FROM treinador_pokemon WHERE id=%s", (relacao_id,))
    conn.commit()

    # Se era do time, promover o primeiro do box.
    if posicao == 'time':

        #Selecao do id da primeira relação entre treinador e pokemon no box.
        cursor.execute("""
            SELECT id 
            FROM treinador_pokemon
            WHERE posicao='box' AND treinador_id=%s
            ORDER BY id ASC
            LIMIT 1
        """, (treinador_id,))
        proximo = cursor.fetchone()

        #Promove para o time.
        if proximo:
            cursor.execute("""
                UPDATE treinador_pokemon
                SET posicao='time'
                WHERE id=%s
            """, (proximo["id"],))
            conn.commit()

    cursor.close()
    conn.close()

    # Retorna ao perfil.
    flash("Pokémon removido!", "sucesso")
    return redirect(url_for("perfil"))

# -------------------------------------------------------------------
# Trocar Pokémon do time com um do box. Parte 1
# -------------------------------------------------------------------
@app.route('/trocar/<int:relacao_id>')
def trocar_pokemon(relacao_id):
    # Verifica o login do user.
    if not session.get("id"):
        flash("Você precisa estar logado.", "erro")
        return redirect(url_for("login"))

    treinador_id = session["id"]

    #Conecta ao banco.
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Pega nome e id do pokemon, a ser trocado.
    cursor.execute("""
        SELECT p.nome, tp.id 
        FROM treinador_pokemon tp 
        JOIN pokemon p ON tp.pokemon_id = p.id
        WHERE tp.id = %s
    """, (relacao_id,))
    pokemon_atual = cursor.fetchone()

    # Seleciona o box para exibir as opções.
    cursor.execute("""
        SELECT p.nome, tp.id 
        FROM treinador_pokemon tp 
        JOIN pokemon p ON tp.pokemon_id = p.id
        WHERE tp.treinador_id = %s AND tp.posicao = 'box'
    """, (treinador_id,))
    box = cursor.fetchall()

    cursor.close()
    conn.close()

    #Renderiza template separado com: id da relação entre treinador e pokemon no time ao ser trocado;
    #id e nome do pokemon a ser trocado; id e nome dos pokemons no box.
    return render_template(
        "trocar.html",
        relacao_id=relacao_id,
        pokemon_atual=pokemon_atual,
        box=box
    )
# -------------------------------------------------------------------
# Trocar Pokémon do time com um do box. parte 2
# -------------------------------------------------------------------
@app.route('/trocar_confirmar')
def trocar_pokemon_confirmar():
    
    #Agora que já temos id da relação, id do pokemon do time, só falta pedir ao user, qual o pokemon do box ele quer promover.
    time_id = request.args.get("time_id")
    box_nome = request.args.get("box_nome")
    
    #Se der problema no formulário.
    if not time_id or not box_nome:
        flash("Seleção inválida.", "erro")
        return redirect(url_for("perfil"))

    #Conecta no banco.
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Pega o id do pokemon selecionado no box.
    cursor.execute("SELECT id FROM pokemon WHERE nome=%s", (box_nome,))
    resultado = cursor.fetchone()

    if not resultado:
        flash("Pokémon inválido.", "erro")
        return redirect(url_for("perfil"))

    box_pokemon_id = resultado["id"]

    # Pega o id da relação do Pokémon escolhido no box.
    cursor.execute("""
        SELECT id 
        FROM treinador_pokemon 
        WHERE pokemon_id=%s AND treinador_id=%s AND posicao='box'
        LIMIT 1
    """, (box_pokemon_id, session["id"]))
    
    relacao_box = cursor.fetchone()
    
    if not relacao_box:
        flash("Esse Pokémon não está no seu box.", "erro")
        return redirect(url_for("perfil"))
    
    box_relacao_id = relacao_box["id"]


    # Por fim troca as posições.
    cursor.execute("UPDATE treinador_pokemon SET posicao='box' WHERE id=%s", (time_id,))
    cursor.execute("UPDATE treinador_pokemon SET posicao='time' WHERE id=%s", (box_relacao_id,))
    
    conn.commit()

    cursor.close()
    conn.close()
    # Retorna ao perfil.
    flash("Pokémons trocados com sucesso!", "sucesso")
    return redirect(url_for("perfil"))

# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)