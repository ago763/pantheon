// Desenho da arena, personagens, projéteis e efeitos.
function diamond(x,y,r,color) {
  ctx.fillStyle=color;
  ctx.beginPath();
  ctx.moveTo(x,y-r);
  ctx.lineTo(x+r*.65,y);
  ctx.lineTo(x,y+r);
  ctx.lineTo(x-r*.65,y);
  ctx.closePath();
  ctx.fill()
}
function draw() {
  ctx.fillStyle='#111e2a';
  ctx.fillRect(0,0,w,h);
  const px=p?p.x:0,py=p?p.y:0;
  ctx.save();
  ctx.translate(w/2-px,h/2-py);
  const tile=100;
  for(let x=Math.floor((px-w/2)/tile)*tile;
  x<px+w/2+tile;
  x+=tile)for(let y=Math.floor((py-h/2)/tile)*tile;
  y<py+h/2+tile;
  y+=tile) {
    const n=Math.abs(Math.sin(x*7+y*19));
    ctx.strokeStyle='#213443';
    ctx.lineWidth=1;
    ctx.beginPath();
    ctx.moveTo(x+10,y+20);
    ctx.lineTo(x+40,y+44);
    ctx.lineTo(x+34,y+65);
    ctx.lineTo(x+78,y+90);
    ctx.stroke();
    if(n>.8) {
      diamond(x+65,y+30,18,'#335d71');
      diamond(x+73,y+35,12,'#4a8599')
    }
    ctx.fillStyle='#1b2e3b';
    ctx.fillRect(x+20,y+73,3,3)
  }
  if(p) {
    for(const g of gems)diamond(g.x,g.y,6,g.value===0?'#f57c91':g.value===5?'#7aebba':'#78caff');
    for(const e of enemies) {
      ctx.fillStyle='#060e1899';
      ctx.beginPath();
      ctx.ellipse(e.x,e.y+e.r,e.r,6,0,0,Math.PI*2);
      ctx.fill();
      ctx.fillStyle=e.slow?'#7ba9c1':e.tank?'#706b89':'#6f537d';
      ctx.fillRect(e.x-e.r,e.y-e.r,e.r*2,e.r*2);
      ctx.fillStyle='#c7a7c3';
      ctx.fillRect(e.x-e.r,e.y-e.r-7,5,9);
      ctx.fillRect(e.x+e.r-5,e.y-e.r-7,5,9);
      ctx.fillStyle='#ffadbf';
      ctx.fillRect(e.x-7,e.y-3,4,3);
      ctx.fillRect(e.x+3,e.y-3,4,3);
      if(e.hp<e.max) {
        ctx.fillStyle='#ef8b9c';
        ctx.fillRect(e.x-e.r,e.y-e.r-12,e.r*2*Math.max(0,e.hp)/e.max,2)
      }
    }
    for(const s of shots) {
      ctx.save();
      ctx.translate(s.x,s.y);
      ctx.rotate(s.a);
      ctx.shadowBlur=18;
      ctx.shadowColor='#73dfff';
      ctx.fillStyle='#97e7ff';
      ctx.beginPath();
      ctx.moveTo(22,0);
      ctx.lineTo(-12,-10);
      ctx.lineTo(-5,0);
      ctx.lineTo(-12,10);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle='#548ea8';
      ctx.beginPath();
      ctx.moveTo(-10,0);
      ctx.lineTo(-40,0);
      ctx.stroke();
      ctx.restore()
    }
    ctx.save();
    ctx.translate(Math.round(p.x),Math.round(p.y));
    ctx.globalAlpha=p.inv>0?.55:1;
    ctx.fillStyle='#050c1888';
    ctx.beginPath();
    ctx.ellipse(0,17,22,8,0,0,Math.PI*2);
    ctx.fill();
    const bob=keys.size?Math.sin(elapsed*16)*2:Math.sin(elapsed*3);
    ctx.translate(0,bob);
    ctx.fillStyle='#567d9b';
    ctx.fillRect(-12,-4,24,23);
    ctx.fillStyle='#bad1df';
    ctx.fillRect(-16,9,32,12);
    ctx.fillStyle='#7fc8e5';
    ctx.fillRect(-8,-19,16,16);
    ctx.fillStyle='#e2e8e5';
    ctx.fillRect(-27,-22,54,7);
    ctx.beginPath();
    ctx.moveTo(-17,-22);
    ctx.lineTo(-3,-52);
    ctx.lineTo(16,-22);
    ctx.fill();
    ctx.fillStyle='#8ba7bf';
    ctx.fillRect(-17,-25,34,4);
    ctx.fillStyle='#112d4e';
    ctx.fillRect(p.face===1?3:-6,-14,3,3);
    ctx.restore();
    ctx.fillStyle='#0b111b';
    ctx.fillRect(p.x-23,p.y+28,46,6);
    ctx.fillStyle='#92d5cc';
    ctx.fillRect(p.x-22,p.y+29,44*Math.max(0,p.hp)/p.maxHp,4);
    for(const e of effects) {
      ctx.globalAlpha=e.t*3;
      ctx.strokeStyle=e.color;
      ctx.beginPath();
      ctx.arc(e.x,e.y,e.r*(1-e.t),0,Math.PI*2);
      ctx.stroke()
    }
    ctx.globalAlpha=1
  }
  ctx.restore();
  const vignette=ctx.createRadialGradient(w/2,h/2,h*.2,w/2,h/2,Math.max(w,h)*.7);
  vignette.addColorStop(0,'transparent');
  vignette.addColorStop(1,'#030711bb');
  ctx.fillStyle=vignette;
  ctx.fillRect(0,0,w,h)
}
