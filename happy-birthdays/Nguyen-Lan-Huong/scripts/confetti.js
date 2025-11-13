/* Confetti animation */
const canvas = document.getElementById('confetti');
const ctx = canvas.getContext('2d');
let W, H; 

function resize() {
  W = canvas.width = innerWidth;
  H = canvas.height = innerHeight;
}

resize();
addEventListener('resize', resize);

function rand(min, max) {
  return Math.random() * (max - min) + min;
}

class Piece {
  constructor() {
    this.reset();
  }
  
  reset() {
    this.x = rand(0, W);
    this.y = rand(-H, 0);
    this.w = rand(6, 12);
    this.h = rand(8, 16);
    this.vy = rand(1, 4);
    this.vx = rand(-1, 1);
    this.r = rand(0, 360);
    this.rr = rand(-3, 3);
    this.color = ['#FF6F91', '#9DFFB8', '#FFD36B', '#7EE8FA', '#CDA4FF'][Math.floor(rand(0, 5))];
  }
  
  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.r += this.rr;
    
    if (this.y > H + 20) this.reset();
  }
  
  draw() {
    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.rotate(this.r * Math.PI / 180);
    ctx.fillStyle = this.color;
    ctx.fillRect(-this.w / 2, -this.h / 2, this.w, this.h);
    ctx.restore();
  }
}

const pieces = Array.from({length: 120}, () => new Piece());
let confOn = true;

function anim() {
  ctx.clearRect(0, 0, W, H);
  
  if (confOn) {
    for (const p of pieces) {
      p.update();
      p.draw();
    }
  }
  
  requestAnimationFrame(anim);
}

anim();

document.getElementById('toggleConf').addEventListener('click', () => {
  confOn = !confOn;
});