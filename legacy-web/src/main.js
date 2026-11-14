// Loop principal: atualiza a simulação e desenha a cada quadro.
function frame(t) {
  const dt=Math.min((t-last)/1000,.035);
  last=t;
  if(state==='play')update(dt);
  draw();
  requestAnimationFrame(frame)
}
requestAnimationFrame(frame);
