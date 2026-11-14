// Botões, teclado e pausa ao sair da janela.
for(const id of ['start','restart'])$(id).onclick=start;
$('pause').onclick=togglePause;
$('resume').onclick=togglePause;
addEventListener('keydown',e=> {
  if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(e.key))e.preventDefault();
  keys.add(e.key.toLowerCase());
  if(e.key==='Escape'&&!e.repeat)togglePause()
});
addEventListener('keyup',e=>keys.delete(e.key.toLowerCase()));
addEventListener('blur',()=> {
  keys.clear();
  if(state==='play')togglePause()
});
