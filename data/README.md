# Editar os valores do jogo

Abra `balance.json` no VS Code. Ele reúne **15 magias, 15 passivas, 5 personagens, 3 mapas, 18 ataques de chefe e os inimigos comuns**. Salve e reinicie o jogo para carregar as alterações. Use ponto nos decimais; JSON não aceita comentários nem vírgula depois do último campo.

## Magias — seção spells

Cada magia tem um identificador estável, como `hyorinmaru` ou `hiken`. Não altere esses identificadores; edite os valores dentro deles.

- `damage`: dano base por acerto ou por pulso.
- `animation_fps`: quadros visuais por segundo. Altera só a animação; não altera dano, recarga ou colisão.
- `cooldown`: intervalo entre conjurações, em segundos. Menor = mais rápido.
- `range`: alcance de busca do alvo e alcance máximo dos projéteis, em pixels. Nas magias orbitais, também define a distância da órbita.
- `projectile_speed`: velocidade do projétil em pixels por segundo. Zero para magias de área.
- `radius`: raio de acerto/área, em pixels. No Hiken, é o raio da explosão; em cones, controla a largura visual.
- `duration`: duração dos efeitos de área. Órbitas permanecem ativas enquanto a magia estiver equipada.
- `projectiles`: quantidade base de projéteis por disparo.
- `tick_interval`: intervalo entre pulsos de dano das áreas. Menor = mais pulsos.
- `slow`: duração da lentidão aplicada por acerto.
- `burn`: duração da queimadura aplicada por acerto.
- `damage_per_level`: aumento proporcional por estrela adicional. `0.25` significa +25% do dano base.
- `range_per_level`: aumento proporcional do alcance por estrela adicional.
- `cooldown_per_level`: redução proporcional da recarga por estrela adicional.
- `evolution_multiplier`: multiplicador de dano da evolução.
- `passive`: identificador da passiva necessária para evoluir.
- `evolution`: nome mostrado na carta de estrela vermelha.
- `mechanic`: comportamento implementado; mudar esse campo altera o tipo de ataque, não só o balanceamento.

Exemplo: para aumentar a frequência de Hyorinmaru, reduza seu `cooldown` de `0.85` para `0.60`. Para aumentar o dano sem acelerar os disparos, altere somente `damage`.

Os efeitos exclusivos das evoluções ainda são parciais: todas recebem ampliação de dano, área e frequência; Godspeed ganha múltiplos acertos e Punição Celestial acompanha o alvo. Outros efeitos específicos do documento, como ressuscitar espectros e parar todos os projéteis, ainda precisam de implementação.

## Passivas — seção passives

- `stat`: atributo que o item melhora.
- `value_per_level`: valor por estrela. Percentuais usam frações: `0.10` = 10%.
- `max_level`: limite de estrelas.
- `icon_row` / `icon_column`: posição do ícone na folha de referência.

`damage`, `area`, `cooldown`, `magnet`, `projectile_speed`, `critical`, `duration`, `xp`, `armor` e `speed` são proporcionais. `projectiles` adiciona unidades inteiras; `regen` adiciona vida por segundo. Os itens não têm dano/alcance próprios: modificam esses atributos nas magias ou no personagem.

## Personagens e transformações

Em `characters`, ajuste `hp`, `speed`, `starting_spell`, `buff_spell`, `damage_bonus` e `cooldown_bonus`. O bônus só afeta a magia indicada em `buff_spell`.

O sprite de cada personagem cabe em um quadro de 64×64, com os pés no centro inferior. `head_offset`, `back_offset` e `feet_offset` definem a posição das camadas da transformação relativa aos pés. Valores negativos de Y sobem o efeito. Ajuste esses campos para mudar o encaixe sem editar o sprite.

Em `elements`, ficam cores, nomes e bônus das formas. A transformação exige **três magias distintas do mesmo elemento equipadas**, em qualquer personagem. Aumentar uma única magia para três estrelas não ativa a forma. Uma magia evoluída continua contando como uma magia do seu elemento.

- Gelo: aura que desacelera inimigos próximos.
- Escuridão: chance de esquiva e redução de recarga por abate.
- Luz: bônus de dano.
- Raio: bônus de movimento e redução de recarga.
- Fogo: bônus de dano e explosões nos abates.

## Chefes e inimigos

`boss_settings` controla o início da sequência, intervalo entre chefes, vida, velocidade e dano de contato. `boss_attacks` tem os 18 ataques, com dano, recarga, tempo de aviso, duração, alcance, velocidade, raio e quantidade. Campos que não se aplicam a um tipo de ataque podem estar zerados.

`enemies` controla mariposas, brutamontes, olhos atiradores e bombas. Os brutamontes atacam por contato; mariposas e olhos também disparam, e bombas avisam antes de explodir.

## Verificar e gerar prévias

No terminal da pasta do projeto:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/render_previews.py
```

As imagens em `previews/` são capturas do próprio renderizador do jogo, com a mesma escala relativa, sprites e camadas usados na partida. As ampliações usam pixels sem suavização.

## Animações e órbita elétrica

`animations.json` define os quadros reais disponíveis de cada magia: imagem fonte, retângulos dos quadros e máscaras para remover os números impressos nas folhas. Projéteis usam o próprio tempo de vida e áreas usam o próprio tempo ativo; pausar a partida congela as animações.

Cada sequência usa a quantidade de recortes distintos disponível: 2, 3, 4 ou 5, sem duplicar quadros para completar quatro. Ice Age usa os cinco estágios da onda presentes na folha. Corpos completos do dragão são separados de partes e impactos. Nas formas, rastros e coroas usam suas sequências reais; asas com apenas um desenho permanecem estáticas. Os halos de luz e escuridão usam a arte original com quatro fases de tamanho/brilho, flutuação e partículas; não são quatro desenhos novos.

A magia `storm_orbs` usa a folha `assets/images/storm-orbs.png`, com esfera, eletricidade e trajeto recortados separadamente. `base_orbs: 3` e `orbs_per_level: 1` produzem 3/4/5/6/7 esferas. A evolução mantém sete e adiciona conexões que também causam dano. `orbit_speed` controla graus por segundo; `orbit_vertical_scale` controla a elipse e `orbit_center_y` posiciona a órbita. A colisão usa as mesmas coordenadas do desenho.

Para gerar uma prévia animada dos níveis 1 e 5:

```powershell
.\.venv\Scripts\python.exe tools/preview_animation.py
```

Abra `previews/animacoes.html` no navegador. A animação APNG e a imagem com os quadros disponíveis de todas as magias ficam na mesma pasta.

## Quatro cartas e afinidade elemental

Em `balance.json`, a seção `progression` contém `choices_per_level: 4` e `same_element_weight: 2`. O peso 2 favorece tanto magias quanto passivas do elemento do personagem. Não significa 50% de chance nem garante duas cartas do elemento: a probabilidade depende das melhorias elegíveis. Use 1 para remover o bônus.

O sorteio não repete melhorias e respeita os limites do inventário. Se restarem menos de quatro melhorias legais, os espaços restantes oferecem recuperação de vida. Clique na carta ou use as teclas 1, 2, 3 e 4.

## Projéteis e queda de gelo

`single_group` limita Static Needles e Judgement a um conjunto ativo por magia. Disparam automaticamente em linha reta para o alvo escolhido. `visual_size` altera o tamanho da arte. `native_angles` em animations.json corrige a direção original de cada quadro antes da rotação do disparo. `stages` escolhe os três estágios: 0–0,5 s, 0,5–1 s e último mantido. Dark Slash usa os quatro quadros ao longo da trajetória, com dissipação final.

Demon’s Extract usa `ice_rain`: `warning` (marca antes da queda), `fall_duration` (queda), `fall_height` (altura visual), `impact_duration` (dissipação), `radius` (área) e `duration` (vida total, pelo menos a soma das três fases). Quatro quadros das estacas e dois da marca. Dano uma vez no impacto, dentro da elipse marcada.

Os modos duram 300, 600 e 900 segundos; o cronograma em world.py divide a duração em seis aparições. `boss_settings.first_spawn` e `spawn_interval` antigos não são mais usados. A vitória depende das seis mortes, não do cronômetro.

Ray of Punishment: `beams_by_level: [1,1,2,2,3]` controla os feixes simultâneos; evolução mantém três. Alvos distintos são priorizados e, se faltarem, os feixes extras atingem o chão próximo. `visual_scale: 1.4` amplia a arte, desenhada sobre os inimigos.

Ice Age: `ring_thickness: 0.45` comprime a espessura radial da arte; 1 restaura a original. Não altera diâmetro nem dano.

Prévia dos 18 ataques de chefes, quatro inimigos e feixes de luz: execute `tools/preview_enemy_attacks.py` e abra `previews/ataques-inimigos.html`.

Belzebu: `boss_attacks.beel_slash.visual_size` controla o tamanho visual do corte (80 px), e `radius` sua colisão (30 px). `beel_grid.area_scale` amplia piso, avisos, raios e colisão juntos (1.5 = 50% maior por dimensão).

Morax: `mor_meteor.fall_duration` controla a queda depois do aviso; `fall_height` a altura visual e `fall_travel` o deslocamento no chão no sentido Morax-alvo. O dano só começa ao terminar a queda. `duration` inclui queda e impacto. Meteoros e lanças usam a direção do alvo no instante do disparo.

Espelhos de Focalors: um par fixado na posição da chefe e do alvo ao conjurar. Após `warning`, dispara a cada `shot_interval` da origem ao destino; `speed`, `damage` e `projectile_radius` controlam os tiros. Os dois espelhos e projéteis usam quatro quadros da folha nova. Substitui a duplicação antiga. Chuva de brasas usa `fall_height`, `fall_travel` e `fall_duration`, como o meteoro; dano apenas após a queda.

Pegadas das formas de gelo e fogo: `elements.<elemento>.trail` controla `max_count` (limitado a 5), `duration` (3 s), `spacing` (38 px), `width`, `height` e `effect_duration`. São fixas no chão, surgem apenas andando e expiram paradas. Gelo aplica lentidão e fogo usa a queimadura existente. Belzebu agora usa corte de 120 px e raio de colisão 45 px.

Luz e raio também usam `elements.<elemento>.trail`, com até cinco marcas: luz fica no chão por 3 s; raio deixa imagens residuais por 0,85 s. São efeitos visuais, sem aplicar queimadura ou lentidão. Light Whip usa quatro golpes por conjuração: cada quarto de `duration` seleciona um quadro distinto, com no máximo um acerto por inimigo por etapa. `damage` é o dano de cada golpe. Não sobrepõe dois combos.

A forma de luz agora usa uma única trilha contínua, seguindo as curvas do movimento: `max_length` limita o comprimento (220 px), `ribbon_width` a espessura (14 px) e `duration` o tempo de desaparecimento (3 s). Não usa mais as cinco pegadas separadas; conserva uma ponta animada com a arte original.
