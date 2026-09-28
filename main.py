from fastapi import FastAPI
from interpretador import interpretar_descricao
from spotify_client import buscar_musicas, buscar_faixa
from fastapi.responses import FileResponse

app = FastAPI()


def formatar_musica(musica):
    """Pega só os campos que interessam de uma faixa do Spotify."""
    imagens = musica["album"]["images"]
    return {
        "nome": musica["name"],
        "artista": musica["artists"][0]["name"],
        "album": musica["album"]["name"],
        "capa": imagens[0]["url"] if imagens else None,
        "preview_url": musica.get("preview_url"),
        "spotify_url": musica["external_urls"]["spotify"]
    }


@app.get("/")
def home():
    return FileResponse("index.html")


@app.get("/buscar")
def buscar(descricao: str):
    """Recebe uma descrição livre e devolve faixas reais do Spotify."""
    termos = interpretar_descricao(descricao)

    resultado = []
    for sugestao in termos.get("sugestoes", []):
        faixa = buscar_faixa(sugestao["artista"], sugestao["musica"])
        if faixa:
            resultado.append(formatar_musica(faixa))

    # Plano B: se nenhuma sugestão foi encontrada, usa a busca por palavra-chave
    if not resultado:
        for faixa in buscar_musicas(termos["termo_busca"], limite=10):
            resultado.append(formatar_musica(faixa))

    return {
        "interpretacao": {
            "generos": termos.get("generos"),
            "mood": termos.get("mood"),
            "instrumentos": termos.get("instrumentos"),
        },
        "resultados": resultado
    }