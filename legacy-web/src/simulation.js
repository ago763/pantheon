// Movimento, inimigos, combate e coleta de XP.
function update(dt) {
  elapsed+=dt;
  p.inv=Math.max(0,p.inv-dt);
  let dx=Number(keys.has('d')||keys.has('arrowright'))-Number(keys.has('a')||keys.has('arrowleft')),dy=Number(keys.has('s')||keys.has('arrowdown'))-Number(keys.has('w')||keys.has('arrowup'));
  let len=Math.hypot(dx,dy)||1;
  p.x+=dx/len*p.speed*dt;
  p.y+=dy/len*p.speed*dt;
  if(dx)p.face=Math.sign(dx);
  spawn-=dt;
  if(spawn<=0) {
    spawn=Math.max(.2,1-elapsed/210);
    const a=rnd(0,Math.PI*2),r=Math.hypot(w,h)/2+50;
    const tank=Math.random()<.18;
    enemies.push( {
      x:p.x+Math.cos(a)*r,y:p.y+Math.sin(a)*r,hp:tank?95:30+elapsed*.16,max:tank?95:30+elapsed*.16,speed:tank?38:65+elapsed*.17,r:tank?20:12,tank,slow:0
    })
  }
  shotTimer-=dt;
  if(shotTimer<=0&&enemies.length) {
    let target=enemies.reduce((a,b)=>distance(p,a)<distance(p,b)?a:b);
    const a=Math.atan2(target.y-p.y,target.x-p.x);
    shots.push( {
      x:p.x,y:p.y,vx:Math.cos(a)*450,vy:Math.sin(a)*450,life:1.7,hit:new Set(),a
    });
    shotTimer=p.rate
  }
  for(const e of enemies) {
    e.slow=Math.max(0,e.slow-dt);
    let dist=distance(p,e)||1;
    e.x+=(p.x-e.x)/dist*e.speed*(e.slow?0.45:1)*dt;
    e.y+=(p.y-e.y)/dist*e.speed*(e.slow?0.45:1)*dt;
    if(dist<e.r+13&&p.inv===0) {
      p.hp-=e.tank?20:10;
      p.inv=.8;
      effects.push( {
        x:p.x,y:p.y,r:30,t:.25,color:'#ff8b9b'
      })
    }
  }
  for(const s of shots) {
    s.x+=s.vx*dt;
    s.y+=s.vy*dt;
    s.life-=dt;
    for(const e of enemies) {
      if(e.hp>0&&!s.hit.has(e)&&distance(s,e)<e.r+18) {
        e.hp-=p.damage;
        e.slow=1;
        s.hit.add(e);
        effects.push( {
          x:e.x,y:e.y,r:22,t:.2,color:'#a4eaff'
        })
      }
    }
  }
  shots=shots.filter(s=>s.life>0);
  enemies=enemies.filter(e=> {
    if(e.hp>0)return true;
    kills++;
    gems.push( {
      x:e.x,y:e.y,value:e.tank?5:1
    });
    if(Math.random()<.035)gems.push( {
      x:e.x+10,y:e.y,value:0
    });
    return false
  });
  gems=gems.filter(g=> {
    const d=distance(g,p);
    if(d<110) {
      g.x+=(p.x-g.x)*dt*7;
      g.y+=(p.y-g.y)*dt*7
    }
    if(d<18) {
      if(g.value)p.xp+=g.value;
      else p.hp=Math.min(p.maxHp,p.hp+20);
      return false
    }
    return true
  });
  for(const e of effects)e.t-=dt;
  effects=effects.filter(e=>e.t>0);
  updateHud();
  if(p.hp<=0)finish(false);
  else if(elapsed>=GAME_CONFIG.duration)finish(true);
  else if(p.xp>=p.need)levelUp()
}
