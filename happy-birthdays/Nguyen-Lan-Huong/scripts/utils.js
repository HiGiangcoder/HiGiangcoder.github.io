/* Utility functions */
document.getElementById('download').addEventListener('click', async () => {
  // try to capture the photo area using HTMLCanvasElement.toDataURL by drawing simple rectangle — lightweight fallback
  const photo = document.getElementById('photo');
  const w = photo.offsetWidth, h = photo.offsetHeight;
  const c = document.createElement('canvas'); 
  c.width = w; 
  c.height = h; 
  const cctx = c.getContext('2d');
  
  cctx.fillStyle = getComputedStyle(photo).backgroundColor || '#fff';
  cctx.fillRect(0, 0, w, h);
  cctx.fillStyle = '#b0466b'; 
  cctx.font = '20px Poppins'; 
  cctx.textAlign = 'center'; 
  cctx.fillText('Lời chúc gửi tới Hương', w / 2, h / 2);
  
  const a = document.createElement('a'); 
  a.href = c.toDataURL('image/png'); 
  a.download = 'loichuc-huong.png'; 
  a.click();
});

/* Quick edit: open the file in a new tab as text (data URL) for manual edit locally */
document.getElementById('edit').addEventListener('click', () => {
  const html = `<!doctype html>\n` + document.documentElement.outerHTML;
  const blob = new Blob([html], {type: 'text/html'});
  const url = URL.createObjectURL(blob);
  window.open(url, '_blank');
});