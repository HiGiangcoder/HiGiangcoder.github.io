/* Audio controls với autoplay sau tương tác và điều khiển đĩa nhạc */
const bgm = document.getElementById('bgm');
const playButton = document.getElementById('playAudio');
const startButton = document.getElementById('startButton');
const startOverlay = document.getElementById('startOverlay');
const record = document.getElementById('record');
let isPlaying = false;

// Hàm bắt đầu trải nghiệm
function startExperience() {
  // Ẩn overlay
  if (startOverlay) {
    startOverlay.style.display = 'none';
  }
  
  // Bắt đầu phát nhạc
  playAudio();
  
  // Bắt đầu confetti (nếu biến tồn tại)
  if (typeof confOn !== 'undefined') {
    confOn = true;
  }
}

// Hàm phát nhạc
function playAudio() {
  if (!bgm) return;
  
  bgm.volume = 0.7;
  bgm.play().then(() => {
    isPlaying = true;
    if (playButton) playButton.textContent = 'Dừng nhạc';
    
    // Bắt đầu quay đĩa nhạc
    if (record) {
      record.classList.add('playing');
    }
    
    console.log('Nhạc đang phát');
  }).catch(error => {
    console.log('Không thể phát nhạc tự động:', error);
    if (playButton) playButton.textContent = 'Phát nhạc';
  });
}

// Hàm dừng nhạc
function pauseAudio() {
  if (!bgm) return;
  
  bgm.pause();
  isPlaying = false;
  if (playButton) playButton.textContent = 'Phát nhạc';
  
  // Dừng quay đĩa nhạc
  if (record) {
    record.classList.remove('playing');
  }
}

// Sự kiện cho nút bắt đầu
if (startButton) {
  startButton.addEventListener('click', startExperience);
}

// Sự kiện cho nút play/pause
if (playButton) {
  playButton.addEventListener('click', () => {
    if (isPlaying) {
      pauseAudio();
    } else {
      playAudio();
    }
  });
}

// Tự động dừng nhạc khi rời trang
window.addEventListener('beforeunload', () => {
  if (isPlaying && bgm) {
    bgm.pause();
  }
});

// Thử phát nhạc khi trang load (có thể bị chặn)
document.addEventListener('DOMContentLoaded', () => {
  if (bgm) {
    bgm.play().catch(() => {
      console.log('Autoplay bị chặn, chờ tương tác người dùng');
    });
  }
});

// Khi nhạc kết thúc (dù có loop)
bgm.addEventListener('ended', () => {
  if (record) {
    record.classList.remove('playing');
  }
  isPlaying = false;
  if (playButton) playButton.textContent = 'Phát nhạc';
});