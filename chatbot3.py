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

        ctk.set_appearance_mode("dark")  # "light" ou "dark"
        ctk.set_default_color_theme("dark-blue")  # Temas disponíveis: "blue", "green", "dark-blue"

        # Área de texto
        self.text_area = ctk.CTkTextbox(master, width=500, height=300, wrap="word")
        self.text_area.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.text_area.insert(ctk.END, "Olá! Eu sou a Artemis, sua assistente virtual. Me informe de qual ano você deseja saber informações?\n")
        self.text_area.configure(state="disabled")  # Apenas leitura na área de texto

        # Campo de entrada
        self.entry = ctk.CTkEntry(master, width=400, placeholder_text="Digite a sua solicitação...")
        self.entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.entry.bind("<Return>", self.process_input)

        # Botão de envio
        self.send_button = ctk.CTkButton(master, text="Enviar", fg_color="blue", command=self.process_input)
        self.send_button.grid(row=2, column=0, padx=20, pady=10)

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
    # Normalizar a entrada do usuário
        user_input_normalized = self.normalize_string(user_input)

        # Consultar a tabela do Google Sheets
        try:
            response = requests.get("https://docs.google.com/spreadsheets/d/e/2PACX-1vTWUPgGQGm6xfcoUcB1Uk9SbFqSznlyDX__Fcvnfc_BG6UhPvN368E1iRU-cygXUTzrWT4c2mcGKtBz/pubhtml")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                rows = soup.find_all('tr')

                # Variáveis para armazenar filtros de busca
                ano, mes, sigla_uf = None, None, None

                # Tentativa de extrair ano, mês e sigla de UF do input do usuário
                ano_match = re.search(r'\b(20\d{2})\b', user_input_normalized)
                if ano_match:
                    ano = ano_match.group(1)
                mes_match = re.search(r'\b(jan(?:eiro)?|fev(?:ereiro)?|mar(?:ço)?|abr(?:il)?|mai(?:o)?|jun(?:ho)?|jul(?:ho)?|ago(?:sto)?|set(?:embro)?|out(?:ubro)?|nov(?:embro)?|dez(?:embro)?)\b', user_input_normalized)
                if mes_match:
                    mes = mes_match.group(1)[:3].lower()  # abreviação para consistência
                uf_match = re.search(r'\b(?:ac|al|ap|am|ba|ce|df|es|go|ma|mt|ms|mg|pa|pb|pr|pe|pi|rj|rn|rs|ro|rr|sc|sp|se|to)\b', user_input_normalized)
                if uf_match:
                    sigla_uf = uf_match.group(0).upper()

                # Verificar se ao menos o ano ou a UF foi informado
                if not ano and not sigla_uf:
                    return "Por favor, especifique pelo menos o ano ou a sigla de UF para obter informações mais precisas."

                # Procurar pela linha correspondente na tabela
                for row in rows[1:]:  # Pular o cabeçalho
                    cells = row.find_all('td')
                    ano_cell = cells[0].get_text().strip()
                    mes_cell = cells[1].get_text().strip()[:3].lower()  # abreviar o mês
                    uf_cell = cells[2].get_text().strip().upper()

                    if (ano == ano_cell if ano else True) and (mes == mes_cell if mes else True) and (sigla_uf == uf_cell if sigla_uf else True):
                        imposto_importacao = cells[3].get_text().strip()
                        imposto_exportacao = cells[4].get_text().strip()
                        ipi_fumo = cells[5].get_text().strip()
                        ipi_bebidas = cells[6].get_text().strip()
                        ipi_automoveis = cells[7].get_text().strip()
                        ipi_importacoes = cells[8].get_text().strip()

                        # Verificar se a consulta foi específica (por exemplo, só perguntou sobre "importação")
                        if "importacao" in user_input_normalized:
                            return f"No ano {ano_cell}, no mês de {mes_cell}, o imposto de importação para {uf_cell} foi de R${imposto_importacao}."
                        elif "bebidas" in user_input_normalized:
                            return f"No ano {ano_cell}, no mês de {mes_cell}, o IPI para bebidas em {uf_cell} foi de R${ipi_bebidas}."
                        else:
                            # Resposta completa
                            return (f"Aqui estão os dados para {mes_cell}/{ano_cell} em {uf_cell}:\n"
                                    f"Imposto Importação: R${imposto_importacao}\n"
                                    f"Imposto Exportação: R${imposto_exportacao}\n"
                                    f"IPI Fumo: R${ipi_fumo}\n"
                                    f"IPI Bebidas: R${ipi_bebidas}\n"
                                    f"IPI Automóveis: R${ipi_automoveis}\n"
                                    f"IPI Importações: R${ipi_importacoes}")

                return "Não encontrei dados correspondentes para os parâmetros especificados."
            else:
                return "Desculpe, não consegui acessar a tabela no momento."
        except requests.exceptions.RequestException as e:
            return f"Erro ao conectar com a tabela: {e}"



if __name__ == "__main__":
    root = ctk.CTk()
    chatbot = Chatbot(root)
    root.mainloop()
