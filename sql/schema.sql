-- Criação das tabelas estruturadas para o projeto
-- Mantendo a organização relacional: Artistas -> Faixas -> Atributos

CREATE TABLE IF NOT EXISTS artistas (
    id INTEGER PRIMARY KEY,
    nome TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS faixas (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    artista_id INTEGER,
    popularidade INTEGER,
    genero TEXT,
    FOREIGN KEY (artista_id) REFERENCES artistas (id)
);

CREATE TABLE IF NOT EXISTS atributos_audio (
    faixa_id TEXT PRIMARY KEY,
    danceability REAL,
    energy REAL,
    valence REAL,
    tempo REAL,
    acousticness REAL,
    loudness REAL,
    FOREIGN KEY (faixa_id) REFERENCES faixas (id)
);
