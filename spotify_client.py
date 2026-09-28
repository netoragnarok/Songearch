import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

_cache = {"token": None, "expira_em": 0}

def obter_token():
    """Devolve um token do Spotify, reaproveitando o anterior enquanto for válido."""
    if _cache["token"] and time.time() < _cache["expira_em"]:
        return _cache["token"]
    
    resposta = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    resposta.raise_for_status()
    dados = resposta.json()

    _cache["token"] = dados["access_token"]
    _cache["expira_em"] = time.time() + dados["expires_in"] - 60
    return _cache["token"]


def buscar_musicas(termo, limite=5):
    """Busca faixas no Spotify por um termo de texto."""
    headers = {"Authorization": f"Bearer {obter_token()}"}
    params = {"q": termo, "type": "track", "limit": limite}

    resposta = requests.get(
        "https://api.spotify.com/v1/search",
        headers=headers,
        params=params
    )
    resposta.raise_for_status()
    return resposta.json()["tracks"]["items"]

def buscar_faixa(artista, musica):
    """Procura uma faixa específica (artista + nome). Devolve None se não achar."""
    headers = {"Authorization": f"Bearer {obter_token()}"}
    params = {
        "q": f'track:"{musica}" artist:"{artista}"',
        "type": "track",
        "limit": 1
    }

    resposta = requests.get(
        "https://api.spotify.com/v1/search",
        headers=headers,
        params=params
    )
    resposta.raise_for_status()
    itens = resposta.json()["tracks"]["items"]
    return itens[0] if itens else None


if __name__ == "__main__":
    faixa = buscar_faixa("Queen", "Bohemian Rhapsody")
    print(faixa["name"] if faixa else "não encontrada")