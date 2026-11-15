# Pantheon — Python e Pygame

Jogo 2D para Windows, executado em uma janela própria. A versão principal agora é feita em Python. A versão anterior de navegador está preservada em `legacy-web/`.

## Abrir e executar no VS Code

1. Selecione **Arquivo → Abrir Pasta** e abra a pasta `jogo` inteira.
2. Instale a extensão **Python**, da Microsoft, se ainda não a tiver. As extensões recomendadas aparecem ao abrir o projeto.
3. Abra **Terminal → Novo Terminal**.
4. Execute no PowerShell:

```powershell
.\.venv\Scripts\python.exe main.py
```

O ambiente `.venv` e o Pygame já foram instalados neste computador. Não é necessário ativar o ambiente virtual nem mudar a política de execução do PowerShell.

Para depurar, abra **Executar e Depurar**, selecione **Jogar Pantheon** e pressione **F5**. A configuração usa o Python da pasta `.venv`. Se o editor pedir um interpretador, use **Ctrl+Shift+P → Python: Select Interpreter** e selecione `.venv\Scripts\python.exe`.

## Onde editar

- `main.py`: entrada do programa.
- `data/balance.json`: balanceamento dos 30 itens/magias, personagens, formas, chefes e inimigos.
- `data/README.md`: explicação de cada ajuste.
- `goetia/config.py`: janela, FPS e duração da partida.
- `goetia/combat.py`: comportamento das magias.
- `goetia/enemy_attacks.py`: ataques dos chefes e inimigos.
- `goetia/transformations.py`: camadas visuais das cinco transformações.
- `goetia/entities.py`: dados do jogador, inimigos, projéteis, coletáveis e efeitos.
- `goetia/world.py`: regras da partida, movimento, combate, XP, vitória e derrota.
- `goetia/progression.py`: catálogo de cartas e efeitos das melhorias.
- `goetia/renderer.py`: desenho da arena, personagens, ataques e efeitos.
- `goetia/assets.py`: carregamento das artes, recortes de sprites e animações.
- `goetia/ui.py`: menus, textos, botões, HUD e cartas.
- `goetia/app.py`: janela, teclado, mouse e loop principal.
- `assets/images/`: novas folhas dos chefes e do ataque de raio enviadas pelo usuário.
- `assets/references/`: as 14 imagens originais extraídas do documento.
- `assets/README.md`: origem de cada arte, recortes e limitações das folhas.
- `assets/audio/`: pasta reservada para músicas e efeitos sonoros.
- `tests/test_game.py`: verificações automatizadas das regras e telas.
- `requirements.txt`: versão do Pygame usada pelo projeto.
- `.vscode/`: configuração para executar e depurar no VS Code.
- `legacy-web/`: protótipo anterior em HTML, CSS e JavaScript; não é necessário para rodar Python.

World cuida das regras; Renderer e UI desenham o resultado; Game conecta tudo ao teclado, mouse e janela. Isso permite mudar o visual sem misturar o desenho com as regras de combate.

## Primeiro ajuste

Em `data/balance.json`, procure `characters` → `ice_witch` e altere `speed` de `180` para `220`. Salve, feche o jogo e execute novamente. Para modificar o ataque, procure `spells` → `hyorinmaru`: `damage` é dano, `cooldown` é recarga, `range` é alcance e `projectile_speed` é velocidade dos tiros.

## Controles

- WASD ou setas: mover.
- Ataques: automáticos contra o inimigo mais próximo.
- Esc ou botão Pausar: pausar e continuar.
- Clique em uma carta ou pressione 1, 2, 3 ou 4 para escolher uma melhoria.
- Enter: iniciar uma partida, continuar da pausa ou reiniciar após o resultado.
- Fechar a janela: sair. Ao trocar de janela, a partida pausa automaticamente.

## Instalar em outro computador

Use Python 3.12. Abra o terminal na pasta do projeto e execute:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Não copie `.venv` de outro computador: recrie o ambiente com os comandos acima. A instalação inicial precisa de internet; depois, o jogo funciona offline.

## Verificar as regras

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes usam o modo de vídeo de teste do Pygame, sem abrir uma janela visível.

## Estado atual

- Menu inicial com Jogar, Personagens, Grimório, Opções e Sair.
- Seleção dos cinco personagens e três mapas. Cada personagem inicia com sua magia e bônus exclusivo.
- Quinze magias funcionais e quinze passivas. Limite de quatro magias e quatro passivas por partida.
- Quatro cartas por nível, com moldura em relevo, pixel art das referências, cor por elemento, atributos, estrelas e item de evolução. Cartas do elemento do personagem recebem peso 2× no sorteio.
- Evolução disponível ao ter a magia no nível 5 e a passiva correspondente. Os efeitos exclusivos das evoluções ainda são parciais; veja data/README.md.
- Transformação ao equipar três magias distintas do mesmo elemento, com camadas independentes e bônus reais.
- Seis chefes usando os corpos frontais enviados. Cada chefe tem três ataques; as artes dos ataques vêm da nova folha e a zona de raio usa sua imagem específica.
- Mariposas e olhos disparam projéteis; bombas avisam antes de explodir; brutamontes atacam por contato.

Escolha na preparação: Rápido (5 minutos), Médio (10 minutos) ou Completo (15 minutos). Os seis chefes aparecem em intervalos iguais, com o último no fim do tempo escolhido. A batalha continua enquanto algum chefe estiver vivo.

A vitória exige derrotar os seis chefes; perder toda a vida causa derrota. Baús, ouro, áudio e parte dos efeitos específicos das evoluções do documento ainda estão pendentes. Os cenários usam os recortes repetidos da referência; não há colisão nos enfeites do chão.

## Conferir as transformações

Execute:

```powershell
.\.venv\Scripts\python.exe tools/render_previews.py
```

Abra previews/transformacoes.png para o antes/depois dos cinco personagens e previews/todas-combinacoes.png para conferir as 25 combinações possíveis de personagem e elemento. As imagens usam o renderizador real do jogo. A pasta também contém as telas de menu, seleção e cartas.

## Interface Pantheon

Menu e seleção usam as artes em `assets/images/ui`. Clique em cada personagem para trocar seu painel de informações. O grimório possui cinco abas elementais com três magias e três passivas por aba, incluindo pares de evolução. Layout e cliques ficam em `goetia/menu_theme.py`.

## Executável Windows

Baixe [Pantheon.exe](https://github.com/ago763/pantheon/raw/refs/heads/main/dist/Pantheon.exe) e abra com dois cliques, sem instalar Python.

Abra `dist/Pantheon.exe` com dois cliques. O arquivo inclui Python, Pygame, dados e artes; não precisa instalar Python para jogar.

Para gerar novamente após alterar o projeto:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m PyInstaller Pantheon.spec --noconfirm
```

Verificação do pacote sem abrir janela: `dist/Pantheon.exe --self-test pantheon-self-test.json`. O executável usa os dados incorporados no momento da compilação.
