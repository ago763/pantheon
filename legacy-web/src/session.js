// Início, reinício, HUD e pausa da partida.
function start() {
  p= {
    ...PLAYER_CONFIG
  };
  enemies=[];
  shots=[];
  gems=[];
  effects=[];
  elapsed=kills=spawn=shotTimer=upgrades=0;
  keys.clear();
  state='play';
  for(const id of ['menu','end','paused','choices'])$(id).hidden=true;
  for(const id of ['hud','inventory','pause'])$(id).hidden=false;
  updateHud()
}
function updateHud() {
  $('level').textContent='NÍVEL '+p.level;
  $('timer').textContent=String(Math.floor(elapsed/60)).padStart(2,'0')+':'+String(Math.floor(elapsed%60)).padStart(2,'0');
  $('kills').textContent=kills;
  $('xp').style.width=(p.xp/p.need*100)+'%';
  $('weapon').textContent='❄ Hyorinmaru · '+p.weapon
}
function togglePause() {
  if(state==='play') {
    state='pause';
    keys.clear()
  }
  else if(state==='pause') {
    state='play'
  }
  $('paused').hidden=state!=='pause'
}
