import time
import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

    tentativas = 4
    for tentativa in range(tentativas):
        try:
            resposta = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            return json.loads(resposta.text)
        except Exception as erro:
            if tentativa == tentativas - 1:
                raise
            espera = 2 ** tentativa  # 1s, 2s, 4s
            print(f"Tentativa {tentativa + 1} falhou ({erro}). Aguardando {espera}s...")
            time.sleep(espera)


if __name__ == "__main__":
    resultado = interpretar_descricao("música calma pra estudar à noite, com piano")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))