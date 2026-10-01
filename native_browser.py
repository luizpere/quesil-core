#!/usr/bin/env python3
"""
ThinkinBrowser Native V1.1
Motor: PyQt5 + QtWebEngine (Chromium Real)
"""
import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QLineEdit, QPushButton, QToolBar)
from PyQt5.QtWebEngineWidgets import QWebEngineView

class ThinkinBrowser(QMainWindow):
    def __init__(self, start_url="https://duckduckgo.com"):
        super().__init__()
        self.setWindowTitle("ThinkinBrowser Nativo")
        self.resize(1024, 768)
        
        # Widget central e layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 1. CRIAR O NAVEGADOR PRIMEIRO
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(start_url))
        self.browser.urlChanged.connect(self.update_url_bar)
        self.browser.loadFinished.connect(self.on_load_finished)
        
        # 2. CRIAR BARRA DE FERRAMENTAS
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("QToolBar { background: #2d2d2d; border-bottom: 1px solid #444; padding: 4px; }")
        
        # Botão Voltar
        self.btn_back = QPushButton("◀")
        self.btn_back.setFixedSize(32, 32)
        self.btn_back.setStyleSheet("QPushButton { color: white; background: transparent; border: none; font-size: 16px; } QPushButton:hover { background: #444; border-radius: 4px; }")
        self.btn_back.clicked.connect(self.browser.back)
        toolbar.addWidget(self.btn_back)
        
        # Botão Avançar
        self.btn_forward = QPushButton("▶")
        self.btn_forward.setFixedSize(32, 32)
        self.btn_forward.setStyleSheet("QPushButton { color: white; background: transparent; border: none; font-size: 16px; } QPushButton:hover { background: #444; border-radius: 4px; }")
        self.btn_forward.clicked.connect(self.browser.forward)
        toolbar.addWidget(self.btn_forward)
        
        # Botão Recarregar
        self.btn_reload = QPushButton("↻")
        self.btn_reload.setFixedSize(32, 32)
        self.btn_reload.setStyleSheet("QPushButton { color: white; background: transparent; border: none; font-size: 16px; } QPushButton:hover { background: #444; border-radius: 4px; }")
        self.btn_reload.clicked.connect(self.browser.reload)
        toolbar.addWidget(self.btn_reload)
        
        # Barra de URL
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Pesquise ou digite uma URL...")
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background: #1e1e1e; color: #fff; border: 1px solid #444;
                border-radius: 4px; padding: 6px 12px; font-size: 14px;
            }
        """)
        self.url_bar.returnPressed.connect(self.navigate)
        toolbar.addWidget(self.url_bar)
        
        # Botão Ir
        self.btn_go = QPushButton("Ir")
        self.btn_go.setStyleSheet("""
            QPushButton {
                background: #007acc; color: white; border: none;
                border-radius: 4px; padding: 6px 16px; font-weight: bold;
            }
            QPushButton:hover { background: #005a9e; }
        """)
        self.btn_go.clicked.connect(self.navigate)
        toolbar.addWidget(self.btn_go)
        
        # Adicionar toolbar ao layout (no topo)
        layout.addWidget(toolbar)
        
        # Adicionar navegador ao layout (ocupa o resto)
        layout.addWidget(self.browser)

    def navigate(self):
        text = self.url_bar.text().strip()
        if not text:
            return
            
        # Lógica inteligente: URL ou Pesquisa?
        if not text.startswith('http://') and not text.startswith('https://'):
            if ' ' in text or '.' not in text:
                # É uma pesquisa
                text = f"https://duckduckgo.com/?q={text}"
            else:
                # Parece um domínio, adicionar https
                text = f"https://{text}"
                
        self.browser.setUrl(QUrl(text))

    def update_url_bar(self, url):
        self.url_bar.setText(url.toString())

    def on_load_finished(self, ok):
        if ok:
            print(f"✅ Página carregada: {self.browser.url().toString()}")

if __name__ == '__main__':
    start_url = sys.argv[1] if len(sys.argv) > 1 else "https://duckduckgo.com"
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Estilo moderno e limpo
    
    window = ThinkinBrowser(start_url)
    window.show()
    sys.exit(app.exec_())
