# Sniff

Utilitário de código aberto desenvolvido para ajudar pesquisadores brasileiros a cruzar a lista de periódicos do Qualis/CAPES (Plataforma Sucupira) com os catálogos de editoras privadas que possuem acordo de gratuidade (isenção de APC) para publicação em Acesso Aberto (Open Access).

## Funcionalidades
- **Processamento automático:** Limpeza e padronização da planilha original exportada da Plataforma Sucupira (.xlsx)
- **Cruzamento de dados:** Match por ISSN/eISSN entre os dados governamentais e os catálogos das editoras
- **Suporte para Editoras:** ACM, Elsevier, IEEE, Springer Nature e Wiley
- **Exportação:** Geração do resultado consolidado em CSV para download e análise "offline"

## Como executar localmente

1. **Clone o repositório:**
```bash
git clone https://github.com/labioinfoufsc/Sniff.git
cd Sniff
```

2. **Crie e ative o ambiente virtual Python:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\\Scripts\\activate
```

3. **Instale as dependências:**
```bash
pip install --upgrade pip
pip install pandas openpyxl streamlit
```

4. **Execute o aplicativo:**
```bash
streamlit run app.py
```

5. O aplicativo será aberto automaticamente no seu navegador padrão (geralmente a URL `http://localhost:8501`).

## Como contribuir

Contribuições são bem-vindas, seja adicionando novos catálogos de editoras, corrigindo bugs ou acrescentando funcionalidades.

1. Faça um Fork do projeto
2. Crie sua Feature Branch (Exemplo: `git checkout -b feature/NovaEditora`)
3. Faça o Commit de suas alterações (Exemplo: `git commit -m 'feat: adiciona catalogo da editora X'`)
4. Faça o Push para a Branch (Exemplo: `git push origin feature/NovaEditora`)
5. Abra um Pull Request.
