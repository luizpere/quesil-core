import os
from app import app

# Carregar variáveis de ambiente em produção
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    # Nunca usar debug=True em produção
    app.run(host="0.0.0.0", port=5000, debug=False)
