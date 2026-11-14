// Cartas de melhoria e progressão de nível.
function levelUp() {
  p.xp-=p.need;
  p.level++;
  p.need=Math.ceil(p.need*1.28);
  state='choice';
  keys.clear();
  $('choices').hidden=false;
  const pool=[ {
    name:'Cachecol Turquesa',desc:'+20% de dano em todos os disparos.',apply:()=>p.damage*=1.2
  }, {
    name:'Passos do Inverno',desc:'+15% de velocidade de movimento.',apply:()=>p.speed*=1.15
  }, {
    name:'Vitalidade Glacial',desc:'+20 de vida máxima e recupera 30 de vida.',apply:()=> {
      p.maxHp+=20;
      p.hp=Math.min(p.maxHp,p.hp+30)
    }
  }, {
    name:'Cálice Demoníaco',desc:'Ataque automático 12% mais rápido.',apply:()=>p.rate=Math.max(.18,p.rate*.88)
  }];
  if(p.weapon<5)pool.push( {
    name:'Hyorinmaru ★',desc:'Eleva a arma em um nível e aumenta seu dano em 30%.',apply:()=> {
      p.weapon++;
      p.damage*=1.3
    }
  });
  for(let i=pool.length-1;
  i>0;
  i--) {
    const j=Math.floor(Math.random()*(i+1));
    [pool[i],pool[j]]=[pool[j],pool[i]]
  }
  $('cards').replaceChildren();
  for(const c of pool.slice(0,3)) {
    const b=document.createElement('button');
    b.textContent=c.name;
    const s=document.createElement('span');
    s.textContent=c.desc;
    b.append(s);
    b.onclick=()=> {
      c.apply();
      upgrades++;
      $('choices').hidden=true;
      state='play';
      updateHud()
    };
    $('cards').append(b)
  }
  updateHud()
}
