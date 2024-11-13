import customtkinter as ctk
import requests
from bs4 import BeautifulSoup
import unicodedata
import re

class Chatbot:
    def __init__(self, master):
        self.master = master
        master.title("Artemis")
        master.geometry("600x500")

        # Configuração da janela
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)
        master.grid_rowconfigure(2, weight=0)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Área de texto
        self.text_area = ctk.CTkTextbox(master, width=500, height=300, wrap="word")
        self.text_area.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.text_area.insert(ctk.END, "Olá! Eu sou a Artemis, sua assistente virtual. Me informe de qual ano você deseja saber informações?\n")
        self.text_area.configure(state="disabled")

        # Campo de entrada
        self.entry = ctk.CTkEntry(master, width=400, placeholder_text="Digite a sua solicitação...")
        self.entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.entry.bind("<Return>", self.process_input)

        # Botão de envio
        self.send_button = ctk.CTkButton(master, text="Enviar", fg_color="blue", command=self.process_input)
        self.send_button.grid(row=2, column=0, padx=20, pady=10)

        # Dicionário de sinônimos para as colunas da tabela
        self.column_synonyms = {
            'ano': ['ano', 'data', 'ano específico'],
            'mes': ['mês', 'mes', 'mês específico', 'data mês'],
            'sigla_uf': ['uf', 'estado', 'unidade federativa', 'sigla', 'local'],
            'imposto_importacao': ['importação', 'imposto de importação', 'taxa de importação'],
            'imposto_exportacao': ['exportação', 'imposto de exportação', 'taxa de exportação'],
            'ipi_fumo': ['ipi fumo', 'fumo', 'imposto sobre fumo'],
            'ipi_bebidas': ['ipi bebidas', 'bebidas', 'imposto sobre bebidas'],
            'ipi_automoveis': ['ipi automóveis', 'automóveis', 'imposto sobre automóveis'],
            'ipi_importacoes': ['ipi importações', 'importações', 'imposto sobre importações']
        }

    def process_input(self, event=None):
        user_input = self.entry.get()
        if not user_input:
            return

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Você: " + user_input + "\n")
        self.text_area.configure(state="disabled")

        # Processar a entrada do usuário
        response = self.get_response(user_input)

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Artemis: " + response + "\n")
        self.text_area.configure(state="disabled")

        self.entry.delete(0, ctk.END)

    def normalize_string(self, s):
        # Remover acentos e converter para minúsculas
        return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8').lower()

    def get_response(self, user_input):
        user_input_normalized = self.normalize_string(user_input)

        try:
            response = requests.get("https://docs.google.com/spreadsheets/d/e/2PACX-1vTWUPgGQGm6xfcoUcB1Uk9SbFqSznlyDX__Fcvnfc_BG6UhPvN368E1iRU-cygXUTzrWT4c2mcGKtBz/pubhtml")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                rows = soup.find_all('tr')

                ano, mes, sigla_uf = None, None, None

                ano_match = re.search(r'\b(20\d{2})\b', user_input_normalized)
                if ano_match:
                    ano = ano_match.group(1)
                mes_match = re.search(r'\b(jan(?:eiro)?|fev(?:ereiro)?|mar(?:ço)?|abr(?:il)?|mai(?:o)?|jun(?:ho)?|jul(?:ho)?|ago(?:sto)?|set(?:embro)?|out(?:ubro)?|nov(?:embro)?|dez(?:embro)?)\b', user_input_normalized)
                if mes_match:
                    mes = mes_match.group(1)[:3].lower()
                uf_match = re.search(r'\b(?:ac|al|ap|am|ba|ce|df|es|go|ma|mt|ms|mg|pa|pb|pr|pe|pi|rj|rn|rs|ro|rr|sc|sp|se|to)\b', user_input_normalized)
                if uf_match:
                    sigla_uf = uf_match.group(0).upper()

                if not ano and not sigla_uf:
                    return "Por favor, especifique pelo menos o ano ou a sigla de UF para obter informações mais precisas."

                for row in rows[1:]:
                    cells = row.find_all('td')
                    ano_cell = cells[0].get_text().strip()
                    mes_cell = cells[1].get_text().strip()[:3].lower()
                    uf_cell = cells[2].get_text().strip().upper()

                    if (ano == ano_cell if ano else True) and (mes == mes_cell if mes else True) and (sigla_uf == uf_cell if sigla_uf else True):
                        impostos = {
                            'imposto_importacao': cells[3].get_text().strip(),
                            'imposto_exportacao': cells[4].get_text().strip(),
                            'ipi_fumo': cells[5].get_text().strip(),
                            'ipi_bebidas': cells[6].get_text().strip(),
                            'ipi_automoveis': cells[7].get_text().strip(),
                            'ipi_importacoes': cells[8].get_text().strip()
                        }

                        for key, synonyms in self.column_synonyms.items():
                            if any(synonym in user_input_normalized for synonym in synonyms):
                                return f"No ano {ano_cell}, no mês de {mes_cell}, o {synonyms[0]} para {uf_cell} foi de R${impostos[key]}."

                        return (f"Aqui estão os dados para {mes_cell}/{ano_cell} em {uf_cell}:\n"
                                f"Imposto Importação: R${impostos['imposto_importacao']}\n"
                                f"Imposto Exportação: R${impostos['imposto_exportacao']}\n"
                                f"IPI Fumo: R${impostos['ipi_fumo']}\n"
                                f"IPI Bebidas: R${impostos['ipi_bebidas']}\n"
                                f"IPI Automóveis: R${impostos['ipi_automoveis']}\n"
                                f"IPI Importações: R${impostos['ipi_importacoes']}")

                return "Não encontrei dados correspondentes para os parâmetros especificados."
            else:
                return "Desculpe, não consegui acessar a tabela no momento."
        except requests.exceptions.RequestException as e:
            return f"Erro ao conectar com a tabela: {e}"


if __name__ == "__main__":
    root = ctk.CTk()
    chatbot = Chatbot(root)
    root.mainloop()
