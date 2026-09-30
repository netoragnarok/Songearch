import os
import requests
from dotenv import load_dotenv

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

_cache = {}

class CotaYoutubeEsgotada (Exception):
    """Exceção lançada quando a cota da API do YouTube é esgotada."""

def buscar_video(artista, musica):
    """Devolve o id de um vídeo do Youtube para a faixa, ou None se não achar."""
    chave = f"{artista} | {musica}" .lower()
    if chave in _cache:
        return _cache[chave]

    resposta = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "part": "snippet",
            "q": f"{artista} - {musica} audio",
            "type": "video",
            "videoEmbeddable": "true",
            "videoCategoryId": "10",
            "maxResults": 1,
            "key": YOUTUBE_API_KEY,
        },
    )

    if resposta.status_code == 403:
        erros = resposta.json().get("error", {}).get("error", {}).get("errors", [{}])
        if erros[0].get("reason") == "quotaExceeded":
            raise CotaYoutubeEsgotada("Cota da API do YouTube esgotada.")
    resposta.raise_for_status()

    itens = resposta.json().get("items", [])
    video_id = itens[0]["id"]["videoId"] if itens else None
    _cache[chave] = video_id
    return video_id