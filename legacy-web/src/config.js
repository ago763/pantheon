// Ajustes da partida. Duração em segundos.
const GAME_CONFIG = {
  duration: 180,
};

// Valores iniciais da Ice Witch. Uma cópia é criada a cada nova partida.
const PLAYER_CONFIG = {
  x: 0,
  y: 0,
  hp: 100,        // Vida inicial.
  maxHp: 100,     // Limite de vida.
  xp: 0,
  level: 1,
  need: 8,        // XP necessário para alcançar o próximo nível.
  speed: 180,     // Velocidade em pixels por segundo.
  damage: 23,     // Dano de cada disparo.
  rate: 0.85,     // Intervalo entre disparos, em segundos.
  weapon: 1,      // Nível inicial da arma (1 a 5).
  inv: 0,         // Tempo de invulnerabilidade restante.
  face: 1,        // 1 = direita; -1 = esquerda.
};
