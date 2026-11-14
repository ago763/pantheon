// Tela de vitória e derrota.
function finish(win) {
  state='end';
  $('end').hidden=false;
  $('pause').hidden=true;
  $('endLabel').textContent=win?'EXPEDIÇÃO CONCLUÍDA':'O INVERNO SE LEMBRA';
  $('endTitle').textContent=win?'Você resistiu à horda.':'Uma alma retorna ao gelo.';
  $('result').textContent=`${Math.floor(elapsed)} segundos de sobrevivência · ${kills} abates · nível ${p.level}.`
}
