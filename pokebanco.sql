CREATE TABLE treinador(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(40) NOT NULL,
    email VARCHAR(100) NOT NULL,
    cpf VARCHAR(11) NOT NULL,
    foto VARCHAR(260),
    cidade VARCHAR(30) NOT NULL,
    senha VARCHAR(87) NOT NULL
);

CREATE TABLE pokemon (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    numero_pokedex VARCHAR(5) NOT NULL,
    tipo VARCHAR(10) NOT NULL,
    imagem_url VARCHAR(260),
    altura INT NOT NULL,
    peso FLOAT NOT NULL,
    habilidades VARCHAR(25) NOT NULL
);

CREATE TABLE treinador_pokemon(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
    treinador_id INT NOT NULL, 
    pokemon_id INT NOT NULL, 
    posicao VARCHAR(4) NOT NULL,    
    FOREIGN KEY (treinador_id) REFERENCES treinador(id),
    FOREIGN KEY (pokemon_id) REFERENCES pokemon(id)
);

CREATE TABLE tipo (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(40) NOT NULL
);

INSERT INTO pokemon (nome, numero_pokedex, tipo, imagem_url, altura, peso, habilidades) VALUES
('Bulbasaur', '001', 'Planta', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png', 7, 6.9, 'Overgrow'),
('Ivysaur', '002', 'Planta', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/2.png', 10, 13.0, 'Overgrow'),
('Venusaur', '003', 'Planta', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/3.png', 20, 100.0, 'Overgrow'),
('Charmander', '004', 'Fogo', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png', 6, 8.5, 'Blaze'),
('Charmeleon', '005', 'Fogo', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/5.png', 11, 19.0, 'Blaze'),
('Charizard', '006', 'Fogo', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/6.png', 17, 90.5, 'Blaze'),
('Squirtle', '007', 'Água', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/7.png', 5, 9.0, 'Torrent'),
('Wartortle', '008', 'Água', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/8.png', 10, 22.5, 'Torrent'),
('Blastoise', '009', 'Água', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/9.png', 16, 85.5, 'Torrent'),
('Pikachu', '025', 'Elétrico', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png', 4, 6.0, 'Static'),
('Raichu', '026', 'Elétrico', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/26.png', 8, 30.0, 'Static'),
('Rattata', '019', 'Normal', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/19.png', 3, 3.5, 'Run Away'),
('Raticate', '020', 'Normal', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/20.png', 7, 18.5, 'Run Away'),
('Sandshrew', '027', 'Terrestre', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/27.png', 6, 12.0, 'Sand Veil'),
('Sandslash', '028', 'Terrestre', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/28.png', 10, 29.5, 'Sand Veil'),
('Jigglypuff', '039', 'Normal', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/39.png', 5, 5.5, 'Cute Charm'),
('Wigglytuff', '040', 'Normal', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/40.png', 10, 12.0, 'Cute Charm'),
('Meowth', '052', 'Normal', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/52.png', 4, 4.2, 'Pickup'),
('Persian', '053', 'Normal', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/53.png', 10, 32.0, 'Pickup'),
('Psyduck', '054', 'Psíquico', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/54.png', 8, 19.6, 'Damp'),
('Golduck', '055', 'Psíquico', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/55.png', 17, 76.6, 'Damp'),
('Machop', '066', 'Lutador', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/66.png', 8, 19.5, 'Guts');