# Next.js + TypeScript Portfolio — Ready-to-Use Project

This textdoc contains a complete, ready-to-deploy **Next.js (App Router) + TypeScript** project that replaces your current project files. It integrates your original HTML/CSS content, restores styles, places static assets under `public/`, configures Tailwind (optional), and provides a deploy script for GitHub Pages (static export).

---

## How to apply these files locally

1. Make sure you're inside your project folder (the folder that will contain `package.json`):

```bash
cd ~/Desktop/HiGiangcoder.github.io/my-project/my-website
```

2. Back up any existing files you want to keep.

3. Replace the project contents with the files below (create files exactly as named). If you're comfortable with Git, commit current work, then copy the files into the repo.

4. Install dependencies and run dev:

```bash
npm install
npm run dev
```

5. To deploy (static export + gh-pages):

```bash
npm run deploy
```

---

## Project file tree (what's included)

```
my-website/
├─ package.json
├─ next.config.mjs
├─ tsconfig.json
├─ postcss.config.cjs
├─ tailwind.config.cjs
├─ public/
│  ├─ avatar.jpg                    # copy your Nguyễn Trường Giang_24520011.jpg -> avatar.jpg
│  └─ favicon.ico
└─ src/
   └─ app/
      ├─ layout.tsx
      ├─ page.tsx
      └─ globals.css
```

---

## Files (create these exact files)

### package.json

```json
{
  "name": "higiang-portfolio",
  "version": "0.0.1",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "export": "next export",
    "start": "next start",
    "deploy": "npm run build && npm run export && npx gh-pages -d out"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "gh-pages": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.21",
    "autoprefixer": "^10.4.14",
    "typescript": "^5.1.6"
  }
}
```

> If you don't want Tailwind, you can remove `tailwindcss`, `postcss`, and `autoprefixer` from devDependencies and delete `postcss.config.cjs` + `tailwind.config.cjs`. The provided CSS will still work.

---

### next.config.mjs

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  // If you're deploying to https://HiGiangcoder.github.io, set basePath to '/HiGiangcoder.github.io'
  // If you plan to use a user/organization page named exactly USERNAME.github.io, set basePath to '/HiGiangcoder.github.io'
  basePath: '/HiGiangcoder.github.io',
  images: { unoptimized: true }
};

export default nextConfig;
```

---

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["DOM", "ES2022"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
    "resolveJsonModule": true
  },
  "include": ["src"]
}
```

---

### postcss.config.cjs

```js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

---

### tailwind.config.cjs

```js
module.exports = {
  content: [
    './src/app/**/*.{ts,tsx,js,jsx}',
    './src/components/**/*.{ts,tsx,js,jsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

---

### public/avatar.jpg

- Copy your image `Nguyễn Trường Giang_24520011.jpg` into `public/avatar.jpg`.
- Also add `public/favicon.ico` if you want.

---

### src/app/layout.tsx

```tsx
import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Nguyễn Trường Giang | Portfolio',
  description: 'Sinh viên Khoa học Máy tính - UIT',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <head>
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
        />
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}
```

---

### src/app/page.tsx

```tsx
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
        <Image src="/avatar.jpg" alt="avatar" width={200} height={200} className="profile-img" />
        <h1 className="title">Nguyễn Trường Giang</h1>
        <p className="subtitle">Sinh viên Khoa học Máy tính - UIT</p>

        <div className="social-links">
          <a href="https://github.com/HiGiangcoder" target="_blank" className="social-btn" rel="noreferrer">
            <i className="fab fa-github"></i>
          </a>
          <a href="https://www.facebook.com/NgTrGiang2006" target="_blank" className="social-btn" rel="noreferrer">
            <i className="fab fa-facebook"></i>
          </a>
          <a href="mailto:giangnt.2006.it@gmail.com" className="social-btn">
            <i className="fas fa-envelope"></i>
          </a>
          <a href="https://zalo.me/0385630306" target="_blank" className="social-btn" rel="noreferrer">
            <i className="fas fa-comment-dots"></i>
          </a>
        </div>

        <div className="action-btns">
          <a href="/MyDocs" className="btn">
            <i className="fas fa-folder-open"></i> Tài liệu cá nhân
          </a>
          <a href="/TempDocs" className="btn">
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
            style={{ width: '100%', height: '500px', border: 'none', borderRadius: '8px' }}
            title="Jupyter Notebook"
          />
        </section>
      </main>
    </div>
  );
}
```

---

### src/app/globals.css

```css
/* Tailwind preflight + utilities are included when you use Tailwind. If you don't want Tailwind,
   remove the @tailwind lines and keep the custom CSS below. */

@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --primary-color: #3498db;
  --secondary-color: #2c3e50;
  --accent-color: #e74c3c;
  --light-bg: #f8f9fa;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: 'Segoe UI', Roboto, Arial, sans-serif;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  color: var(--secondary-color);
}

.container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
.hero { text-align: center; margin-bottom: 3rem; }
.profile-img { border-radius: 50%; border: 5px solid var(--primary-color); }
.title { color: var(--secondary-color); font-size: 2.4rem; margin-top: 1rem; }
.subtitle { color: var(--primary-color); }
.social-links { display:flex; gap:1rem; justify-content:center; margin-top:1rem; }
.social-btn { display:inline-flex; align-items:center; justify-content:center; width:48px; height:48px; background:white; border-radius:50%; box-shadow:0 6px 18px rgba(0,0,0,0.08); color:var(--primary-color); }
.btn { display:inline-flex; align-items:center; gap:0.6rem; padding:0.8rem 1.4rem; background:var(--primary-color); color:white; border-radius:999px; text-decoration:none; }
.info-card { background:white; border-radius:12px; padding:1.5rem; box-shadow:0 10px 30px rgba(0,0,0,0.08); margin-bottom:1.5rem; }
.timeline-item { border-left:3px solid var(--primary-color); padding-left:1rem; margin-bottom:1rem; }
.achievement-item { display:flex; gap:1rem; align-items:center; background:var(--light-bg); padding:1rem; border-radius:8px; }

@media (max-width: 768px) {
  .container { padding:1rem; }
  .profile-img { width:150px; height:150px; }
}
```

---

## Notes & next steps

- After creating files, run `npm install` to install dependencies.
- If you don't want Tailwind: remove `@tailwind` lines from `globals.css`, uninstall Tailwind packages, and remove `postcss.config.cjs` & `tailwind.config.cjs`.
- `basePath` in `next.config.mjs` must match your GitHub Pages repo name. For user/organization site `USERNAME.github.io` use `basePath: '/USERNAME.github.io'`.
- If you want automatic deploy on push, I'll add a GitHub Action workflow file next.

---

If you want, mình sẽ tiếp tục và **tạo file `.github/workflows/deploy.yml`** để tự động deploy khi push lên `main`. Hoặc mình có thể **xuất ZIP** của dự án để bạn tải về. Bạn muốn bước nào tiếp theo?