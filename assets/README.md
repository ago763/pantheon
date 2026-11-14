# Artes do jogo

`references/` contém as 14 imagens extraídas de `jogo.docx`, sem modificar os originais.

`images/bosses-front.png` é a nova folha frontal enviada pelo usuário: seis linhas (Belzebu, Barbatos, Morax, Buer, Haborym e Focalors), com quatro quadros de 256×256 por linha. É a folha usada na partida.

`images/bosses-side.png` preserva a primeira folha enviada, de lado, para uso futuro. O carregador já permite acessar os quadros laterais; a partida atualmente usa a frente.

`images/beelzebul-lightning-zone.png` é a arte enviada para o ataque de zona do Belzebu. A primeira faixa tem o chão, a segunda os raios e a terceira os impactos; cada faixa tem quatro quadros.

## Recortes e transparência

Os recortes ficam em `goetia/assets.py`. As folhas do documento não têm uma grade uniforme apesar dos textos impressos nelas; por isso, cada recorte tem coordenadas explícitas. O fundo xadrez está incorporado às imagens do documento. O carregador aplica uma chave de cor cinza apenas aos sprites recortados, em memória. Isso pode remover alguns detalhes cinza muito escuros e será substituído se forem fornecidas folhas com transparência real. As novas imagens dos chefes e raios usam seu canal alpha original.

As imagens originais são preservadas. Não é necessário regenerar as folhas ao alterar o código. Os quadros recortados e escalados ficam em cache durante a execução.

## Artes utilizadas

- image10: os cinco personagens, com animações de parado e caminhada.
- image11: retratos dos cinco personagens na seleção.
- image3: os três cenários, com repetição dos recortes.
- image12: mariposas, brutamontes, olhos, bombas e projéteis comuns.
- image1, image2, image4, image6, image8 e image13: magias e camadas elementais.
- image5 e image9: os trinta ícones de itens e magias.
- image7: XP e poção.
- bosses-front.png: os corpos animados dos chefes.
- boss-attacks.png: apenas os efeitos dos 18 ataques; os corpos dessa folha não são usados.
- beelzebul-lightning-zone.png: zona elétrica do Belzebu.
- menu-reference.png: ilustração e título do menu. Botões, textos e ações são desenhados separadamente.

As transformações usam camadas ancoradas nos pés e não substituem o sprite-base. Os offsets por personagem ficam em data/balance.json. O xadrez incorporado nas referências exige remoção de fundo em memória; algumas bordas ainda podem precisar de retoque artístico, especialmente nas asas luminosas. As novas folhas com alpha preservam a transparência original.
