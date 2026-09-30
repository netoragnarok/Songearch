import os
import json
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Modelos em ordem de preferência. Se um falhar, tenta o próximo.
MODELOS = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]


def interpretar_descricao(descricao_usuario):
    """Interpreta a descrição e sugere faixas reais que combinam com ela."""

    prompt = f"""Você é um especialista em música e curadoria de playlists.
Com base na descrição abaixo, devolva um JSON com os campos:
- generos: lista de gêneros musicais prováveis
- mood: uma palavra descrevendo o clima
- instrumentos: lista de instrumentos mencionados ou implícitos (pode ser vazia)
- termo_busca: frase curta para busca no Spotify (usada só como plano B)
- sugestoes: lista com 12 faixas REAIS e conhecidas que combinam com a descrição,
  cada uma no formato {{"artista": "...", "musica": "..."}}

Regras: sugira apenas músicas que você tem certeza que existem, misture artistas
diferentes e não repita o mesmo artista mais de duas vezes.

Descrição do usuário: {descricao_usuario}"""

    ultimo_erro = None
    for modelo in MODELOS:
        for tentativa in range(2):
            try:
                resposta = client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                    config={"response_mime_type": "application/json"},
                )
                return json.loads(resposta.text)
            except Exception as erro:
                ultimo_erro = erro
                print(f"[{modelo}] tentativa {tentativa + 1} falhou: {erro}")
                if getattr(erro, "code", None) == 404:
                    break  # modelo indisponível: não adianta tentar de novo
                time.sleep(2)

    raise ultimo_erro


if __name__ == "__main__":
    resultado = interpretar_descricao("música calma pra estudar à noite, com piano")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))