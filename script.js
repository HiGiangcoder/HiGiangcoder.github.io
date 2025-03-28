// Hiệu ứng scroll mượt mà
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Hiệu ứng khi scroll xuống
window.addEventListener('scroll', () => {
    const cards = document.querySelectorAll('.info-card');
    const windowHeight = window.innerHeight;

    cards.forEach(card => {
        const cardTop = card.getBoundingClientRect().top;
        if (cardTop < windowHeight - 100) {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }
    });
});

// Hiệu ứng hover cho các card
document.querySelectorAll('.info-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        card.style.setProperty('--mouse-x', `${x}px`);
        card.style.setProperty('--mouse-y', `${y}px`);
    });
});

// Load animation
window.onload = () => {
    document.body.style.opacity = '1';
};

// Ace Editor Configuration
let cppEditor, pythonEditor;

function initEditors() {
    // C++ Editor
    cppEditor = ace.edit("cpp-editor");
    cppEditor.setTheme("ace/theme/chrome");
    cppEditor.session.setMode("ace/mode/c_cpp");
    cppEditor.setOptions({
        enableBasicAutocompletion: true,
        enableLiveAutocompletion: true,
        fontSize: "14px"
    });
    cppEditor.session.setValue(`#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello from C++!" << endl;\n    return 0;\n}`);

    // Python Editor
    pythonEditor = ace.edit("python-editor");
    pythonEditor.setTheme("ace/theme/chrome");
    pythonEditor.session.setMode("ace/mode/python");
    pythonEditor.setOptions({
        enableBasicAutocompletion: true,
        enableLiveAutocompletion: true,
        fontSize: "14px"
    });
    pythonEditor.session.setValue(`print("Hello from Python!")\n# Your code here`);
}

function switchTab(lang) {
    // Remove active class từ tất cả các tab
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Thêm active class cho tab được chọn
    document.querySelector(`button[data-lang="${lang}"]`).classList.add('active');
    
    // Hiển thị editor tương ứng
    currentEditor = lang === 'cpp' ? cppEditor : pythonEditor;
    document.querySelectorAll('.editor-container').forEach(editor => {
        editor.style.display = editor.id === `${lang}-editor` ? 'block' : 'none';
    });
    
    // Kích hoạt resize editor
    currentEditor.resize();
    currentEditor.focus();
}

// Khởi tạo editor khi trang load xong
window.addEventListener('load', () => {
    initEditors();
    switchTab('cpp'); // Mặc định hiển thị C++
});
const JUDGE0_API_KEY = '672bceb264msh0d539fcf0eef7d7p1bcce0jsn4709c5138896'; // Đăng ký tại https://judge0.com
let currentEditor;

async function runCode() {
    const output = document.getElementById('output');
    output.textContent = 'Running...';
    output.style.color = '#3498db';

    try {
        const code = currentEditor.getValue();
        const languageId = currentEditor === cppEditor ? 54 : 71; // C++:54, Python:71
        
        const response = await fetch('https://judge0-ce.p.rapidapi.com/submissions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-RapidAPI-Key': JUDGE0_API_KEY,
                'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com'
            },
            body: JSON.stringify({
                source_code: code,
                language_id: languageId,
                stdin: '',
                redirect_stderr_to_stdout: true
            })
        });

        const submission = await response.json();
        const result = await getSubmissionResult(submission.token);
        
        output.textContent = result.status.description + '\n\n' + (result.stdout || result.stderr);
        output.style.color = result.status.id === 3 ? '#2ecc71' : '#e74c3c';
    } catch (error) {
        output.textContent = 'Error: ' + error.message;
        output.style.color = '#e74c3c';
    }
}

async function getSubmissionResult(token) {
    return new Promise((resolve, reject) => {
        const checkInterval = setInterval(async () => {
            try {
                const response = await fetch(`https://judge0-ce.p.rapidapi.com/submissions/${token}`, {
                    headers: {
                        'X-RapidAPI-Key': JUDGE0_API_KEY,
                        'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com'
                    }
                });
                const result = await response.json();
                
                if (result.status.id > 2) { // 3 = done, 4+ = error
                    clearInterval(checkInterval);
                    resolve(result);
                }
            } catch (error) {
                clearInterval(checkInterval);
                reject(error);
            }
        }, 1000);
    });
}

function downloadCode() {
    const filename = document.getElementById('filename').value || 'program';
    const extension = currentEditor === cppEditor ? '.cpp' : '.py';
    const blob = new Blob([currentEditor.getValue()], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    
    a.href = url;
    a.download = filename + extension;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Cập nhật hàm switchTab
function switchTab(lang) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.lang === lang) btn.classList.add('active');
    });

    currentEditor = lang === 'cpp' ? cppEditor : pythonEditor;
    document.querySelectorAll('.editor-container').forEach(editor => {
        editor.style.display = editor.id === `${lang}-editor` ? 'block' : 'none';
    });
    
    currentEditor.resize();
    currentEditor.focus();
}

// Thêm Jupyter Notebook (sử dụng JupyterLite)
const jupyterHtml = `
<iframe 
    src="https://jupyterlite.github.io/demo/repl/index.html"
    style="width: 100%; height: 500px; border: none; border-radius: 8px;"
    title="Jupyter Notebook"
></iframe>`;

function addJupyterTab() {
    const editorSection = document.querySelector('.info-card:last-child');
    const jupyterTab = document.createElement('div');
    jupyterTab.innerHTML = jupyterHtml;
    editorSection.appendChild(jupyterTab);
}

// Khởi tạo
window.addEventListener('load', () => {
    initEditors();
    switchTab('cpp');
    addJupyterTab(); // Thêm Jupyter Notebook
});