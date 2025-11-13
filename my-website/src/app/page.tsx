'use client';

import Image from 'next/image';
import { useEffect } from 'react';

export default function HomePage() {
  useEffect(() => {
    console.log('Portfolio loaded!');
  }, []);

  return (
    <div className="container">
      <header className="hero">
        <Image
          src="/Nguyễn Trường Giang_24520011.jpg"
          alt="Nguyễn Trường Giang"
          width={200}
          height={200}
          className="profile-img"
        />
        <h1 className="title">Nguyễn Trường Giang</h1>
        <p className="subtitle">Sinh viên Khoa học Máy tính - UIT</p>

        <div className="social-links">
          <a href="https://github.com/HiGiangcoder" target="_blank" className="social-btn">
            <i className="fab fa-github"></i>
          </a>
          <a href="https://www.facebook.com/NgTrGiang2006" target="_blank" className="social-btn">
            <i className="fab fa-facebook"></i>
          </a>
          <a href="mailto:giangnt.2006.it@gmail.com" className="social-btn">
            <i className="fas fa-envelope"></i>
          </a>
          <a href="https://zalo.me/0385630306" target="_blank" className="social-btn">
            <i className="fas fa-comment-dots"></i>
          </a>
        </div>

        <div className="action-btns">
          <a href="https://higiangcoder.github.io/MyDocs" className="btn">
            <i className="fas fa-folder-open"></i> Tài liệu cá nhân
          </a>
          <a href="https://higiangcoder.github.io/TempDocs" className="btn">
            <i className="fas fa-file-archive"></i> Tài liệu tạm
          </a>
        </div>
      </header>

      <main className="content">
        <section className="info-card">
          <h2><i className="fas fa-graduation-cap"></i> Học vấn</h2>
          <div className="timeline">
            <div className="timeline-item">
              <h3>Đại học Công nghệ Thông tin - UIT</h3>
              <p>2023 - Hiện tại</p>
              <p>Khoa Khoa học Máy tính - CTTN</p>
              <p>Tham gia Lab AI (Computer Vision)</p>
            </div>
            <div className="timeline-item">
              <h3>THPT Chuyên Nguyễn Chí Thanh</h3>
              <p>2020 - 2023</p>
              <p>Chuyên Toán - Giải Ba Tin học Quốc gia 2023</p>
            </div>
          </div>
        </section>

        <section className="info-card">
          <h2><i className="fas fa-trophy"></i> Thành tích</h2>
          <div className="achievements">
            <div className="achievement-item">
              <div className="achievement-icon">
                <i className="fas fa-medal"></i>
              </div>
              <div className="achievement-content">
                <h3>Giải Khuyến khích Tin học Quốc gia</h3>
                <p>Năm học lớp 11 - 2022</p>
              </div>
            </div>
            <div className="achievement-item">
              <div className="achievement-icon">
                <i className="fas fa-award"></i>
              </div>
              <div className="achievement-content">
                <h3>Giải Ba Tin học Quốc gia</h3>
                <p>Năm học lớp 12 - 2023</p>
              </div>
            </div>
          </div>
        </section>

        <section className="info-card">
          <h2><i className="fas fa-book"></i> Jupyter Notebook</h2>
          <iframe
            src="https://jupyterlite.github.io/demo/repl/index.html"
            style={{
              width: '100%',
              height: '500px',
              border: 'none',
              borderRadius: '8px',
            }}
            title="Jupyter Notebook"
          />
        </section>
      </main>
    </div>
  );
}
