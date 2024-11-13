# Artemis - Chatbot de Impostos

Artemis é um chatbot desenvolvido em Python com uma interface gráfica simples usando a biblioteca `customtkinter`. Ele consulta informações de impostos a partir de uma tabela pública no Google Sheets e fornece dados como Imposto de Importação, Exportação e IPI (Imposto sobre Produtos Industrializados) para fumo, bebidas, automóveis e importações.

## Funcionalidades

- **Consulta de Impostos**: Permite que o usuário pesquise informações de impostos filtradas por ano, mês e estado.
- **Interface gráfica**: Construída com `customtkinter`, proporcionando uma experiência de uso amigável.
- **Processamento de Respostas**: O chatbot analisa a solicitação do usuário e fornece uma resposta direta ou uma visão geral dos dados disponíveis.

## Pré-requisitos

- **Python 3.7+**: Verifique se o Python está instalado executando `python --version`.
- **Bibliotecas**: `customtkinter`, `requests`, `beautifulsoup4`

## Instalação

1. **Clone o Repositório**
   ```bash
   git clone https://github.com/usuario/seu-projeto.git
   cd seu-projeto
