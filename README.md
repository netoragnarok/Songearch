# Songearch

Aplicação web que descobre músicas a partir de uma descrição em linguagem natural.
A pessoa descreve o clima, os instrumentos ou a sensação que procura (ex: "música
calma pra estudar à noite, com piano") e o sistema usa IA para interpretar essa
descrição, sugerir faixas reais que combinam com ela, localizar cada uma no
Spotify e permitir a reprodução direto na página, via YouTube.

## Tecnologias

- **Python + FastAPI** — backend e servidor web
- **Google Gemini API** — interpretação da descrição e sugestão de faixas
- **Spotify Web API** — metadados das faixas (capa, álbum, link)
- **YouTube Data API v3** — reprodução das faixas
- **HTML/CSS/JavaScript puro** — frontend, sem frameworks

## Arquitetura

O backend é dividido em módulos com responsabilidades separadas, no mesmo
espírito de uma arquitetura em camadas:

- **`interpretador.py`** — conversa com o Gemini. Recebe a descrição livre do
  usuário e devolve um JSON estruturado com gêneros, clima, instrumentos e uma
  lista de faixas sugeridas (artista + música). Tenta múltiplos modelos em
  sequência, com espera progressiva entre tentativas, para lidar com
  instabilidade do serviço de IA.
- **`spotify_client.py`** — conversa com o Spotify. Autentica via Client
  Credentials, guarda o token em cache (evitando pedir um novo a cada
  requisição) e localiza cada faixa sugerida pela IA, devolvendo capa, álbum
  e link.
- **`youtube_client.py`** — conversa com o YouTube. Busca o vídeo de uma faixa
  específica, sob demanda (só quando o usuário pede para ouvir), e guarda o
  resultado em cache para não repetir buscas.
- **`main.py`** — orquestra os três módulos acima através de rotas HTTP
  (`/buscar` e `/video`) e serve a página inicial (`index.html`). É a única
  camada que sabe como os outros três módulos se conectam.

O frontend (`index.html`) é uma página única: envia a descrição para `/buscar`,
recebe a lista de faixas e monta os cards dinamicamente. Cada card só busca o
vídeo do YouTube quando o botão "Ouvir" é clicado.

## Decisões técnicas

**Sugestão de faixas pela IA, não busca por palavra-chave no Spotify.** O
endpoint de recomendações automáticas do Spotify (`/recommendations`) foi
descontinuado em novembro de 2024, junto com o de características de áudio
(`/audio-features`). Sem esses dados, uma busca por palavra-chave no Spotify
(`/search`) traz resultados superficiais: faixas que têm "night" ou "chill" no
título, por exemplo, sem necessariamente combinar com o clima pedido. A solução
foi inverter a responsabilidade: a IA, que tem conhecimento real sobre música,
sugere artista e nome de faixas reais que combinam com a descrição, e o Spotify
é usado só para localizar cada uma (por filtros exatos de `track:` e
`artist:`) e devolver seus metadados. A busca por palavra-chave continua
existindo como plano B, caso nenhuma sugestão da IA seja encontrada.

**Busca de vídeo sob demanda, não em lote.** A API do YouTube cobra 100
unidades por busca, contra uma cota gratuita diária de 10.000 unidades — cerca
de 100 buscas por dia. Buscar o vídeo de todas as faixas sugeridas de uma vez
(até 12 por pedido) esgotaria a cota em poucas buscas. Por isso, a busca no
YouTube só acontece quando o usuário clica em "Ouvir" numa faixa específica, e
o resultado fica em cache para não repetir a mesma busca.

**Múltiplos modelos de IA com tentativas em sequência.** O modelo gratuito do
Gemini apresentou instabilidade (erro 503, alta demanda) durante o
desenvolvimento. Para tornar o sistema mais resiliente, o `interpretador.py`
tenta o modelo principal algumas vezes com espera progressiva entre tentativas
e, se continuar falhando, passa para modelos alternativos da mesma família.

**Gemini em vez de OpenAI.** A API da OpenAI cobra por uso desde a primeira
chamada, sem camada gratuita permanente. A Gemini API do Google oferece uma
cota gratuita contínua, sem necessidade de cartão de crédito, o que a torna
mais adequada para um projeto de portfólio em desenvolvimento.

## Limitações conhecidas

- O campo `preview_url` (prévia de 30 segundos) do Spotify vem sempre vazio,
  porque esse recurso foi restringido a aplicativos aprovados após as mudanças
  na API em 2024–2026.
- Alguns vídeos do YouTube aparecem como indisponíveis para reprodução
  embutida, mesmo filtrados por `videoEmbeddable=true` — a plataforma só
  confirma isso no momento em que o player tenta carregar o vídeo.
- A cota gratuita da YouTube Data API é de aproximadamente 100 reproduções por
  dia. Em uso intenso, novas buscas de vídeo podem falhar até a cota renovar.
- O app roda como projeto de "Development Mode" no Spotify, limitado a 5
  usuários de teste, por conta das restrições impostas pelo Spotify em
  fevereiro de 2026.

## Como executar

1. Clonar o repositório
2. Criar e ativar um ambiente virtual Python
3. Instalar as dependências: `pip install -r requirements.txt`
4. Criar um arquivo `.env` na raiz do projeto com:
   ```
   SPOTIFY_CLIENT_ID=...
   SPOTIFY_CLIENT_SECRET=...
   GEMINI_API_KEY=...
   YOUTUBE_API_KEY=...
   ```
5. Rodar o servidor: `uvicorn main:app --reload`
6. Abrir `http://127.0.0.1:8000/` no navegador

## Dificuldades e aprendizados

O desenvolvimento passou por diversos obstáculos típicos de quem está
aprendendo Python vindo de outra linguagem: erros de indentação (que em Python
define blocos de código, diferente das chaves do C#), vírgulas faltando em
chamadas de função, e um erro de digitação (`respota` em vez de `resposta`)
que só apareceu em tempo de execução, não na inicialização do servidor — uma
diferença importante em relação a erros de compilação.

Também foi necessário lidar com instabilidade de serviços externos fora do
controle do projeto: a API do Gemini apresentou picos de indisponibilidade
(erro 503), resolvidos com tentativas repetidas e modelos alternativos; e a
API do YouTube tem uma cota rígida, que moldou a decisão de buscar vídeos sob
demanda em vez de antecipadamente.

De forma geral, este projeto reforçou a mesma lição do desafio técnico
anterior: separar responsabilidades em módulos distintos facilita tanto o
desenvolvimento quanto a adaptação a mudanças externas — como as restrições
sucessivas impostas pela API do Spotify ao longo do projeto.
