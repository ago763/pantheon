// Estado compartilhado, canvas e funções auxiliares.
'use strict';
const $=id=>document.getElementById(id),canvas=$('game'),ctx=canvas.getContext('2d');
let w,h,dpr;
function resize() {
  dpr=Math.min(devicePixelRatio||1,2);
  w=innerWidth;
  h=innerHeight;
  canvas.width=w*dpr;
  canvas.height=h*dpr;
  ctx.setTransform(dpr,0,0,dpr,0,0)
}
addEventListener('resize',resize);
resize();
let state='menu',p,enemies=[],shots=[],gems=[],effects=[],elapsed=0,kills=0,spawn=0,shotTimer=0,last=0,upgrades=0;
const keys=new Set();
const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
const rnd=(a,b)=>a+Math.random()*(b-a);
