from config import *

@app.route('/')
def home():
    if session.get('id'):
        return redirect(url_for('perfil'))
    else:
        return redirect(url_for('login'))


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form['cpf']
        foto = 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp'
        cidade = request.form['cidade']
        senha_raw = request.form['senha']
        senha = generate_password_hash(senha_raw)

        if not all([nome, email, cpf, cidade, senha_raw]):
            flash("Todos os campos são obrigatórios!", "erro")
            return redirect(url_for('cadastro'))

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(buffered=True)

        cursor.execute("SELECT * FROM treinador WHERE email = %s OR cpf = %s", (email, cpf))
        if cursor.fetchone():
            flash("E-mail ou CPF já cadastrado.", "erro")
            cursor.close()
            conn.close()
            return redirect(url_for('cadastro'))
        
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
    if request.method == 'POST':
        email = request.form['email'].strip()
        senha_raw = request.form['senha_raw'].strip()
        
        if not all([email, senha_raw]):
            flash("Todos os campos são obrigatórios!", "erro")
            return redirect(url_for('cadastro'))

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        cursor.execute("SELECT * FROM treinador WHERE email = %s", (email,))
        treinador = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if treinador and check_password_hash(treinador['senha'], senha_raw):
            session['id'] = treinador['id']
            session['nome'] = treinador['nome']
            session['email'] = treinador['email']
            session['cpf'] = treinador['cpf']
            session['foto'] = treinador['foto']
            session['cidade'] = treinador['cidade']

            return redirect(url_for('perfil'))
                    
        else:
            flash("Usuário ou senha inválidos.", "erro")
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/perfil')
def perfil():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM treinador")
    treinador = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('perfil.html', treinador=treinador)

@app.route('/logout')
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

@app.route('perfil/editar')
def editar_perfil():
    pass