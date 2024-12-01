import customtkinter as ctk
import requests
from bs4 import BeautifulSoup
import unicodedata
import re
import random
import spacy

nlp = spacy.load('pt_core_news_sm')

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

        # Dicionário de sinônimos
        self.synonym_dict = {
            "imposto_importacao": ["importacao", "importação", "import"],
            "imposto_exportacao": ["exportacao", "exportação", "export"],
            "ipi_fumo": ["fumo", "tabaco", "cigarro"],
            "ipi_bebidas": ["bebidas", "alcool", "cerveja"],
            "ipi_automoveis": ["automoveis", "carros", "veiculos"],
            "ipi_importacoes": ["importacoes", "taxa de importação"]
        }

    def process_input(self, event=None):
        user_input = self.entry.get()
        if not user_input:
            return

        # Exibir a entrada do usuário na área de texto
        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Você: " + user_input + "\n")
        self.text_area.configure(state="disabled")

        # Limpar o campo de entrada
        self.entry.delete(0, ctk.END)

        # Processar a entrada e obter a resposta
        response = self.get_response(user_input)

        # Exibir a resposta do chatbot
        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Artemis: " + response + "\n")
        self.text_area.configure(state="disabled")

    def normalize_string(self, user_input):
        # Remover acentos e normalizar a string
        return unicodedata.normalize('NFKD', user_input).encode('ASCII', 'ignore').decode('ASCII')

    def tokenize_input(self, user_input):
        doc = nlp(user_input.lower())
        tokens = {
            "ano": None,
            "mes": None,
            "sigla_uf": None,
            "tipo_imposto": []
        }

        def tokenize_input_with_spacy(self, user_input):
            doc = nlp(user_input.lower())
            tokens = {
                "ano": None,
                "mes": None,
                "sigla_uf": None,
                "tipo_imposto": []
            }

        # Identificar entidades nomeadas
        # Identificar entidades nomeadas
        for ent in doc.ents:
            if ent.label_ == "DATE" and len(ent.text) == 4:  # Ano
                tokens["ano"] = ent.text    
        # Se o ano não foi encontrado via spaCy, podemos tentar uma extração direta
        if not tokens["ano"]:
            year_match = re.search(r"\b(\d{4})\b", user_input)
            if year_match:
                tokens["ano"] = year_match.group(1)    

        # Procurar por sinônimos de impostos nos tokens
        for token in doc:
            for key, synonyms in self.synonym_dict.items():
                if token.lemma_ in synonyms:
                    tokens["tipo_imposto"].append(key)

        return tokens

    def get_response(self, user_input):
        # Normalizar a entrada e tokenizar
        user_input_normalized = self.normalize_string(user_input)
        tokens = self.tokenize_input(user_input_normalized)

        # Consultar a tabela do Google Sheets
        try:
            response = requests.get("https://docs.google.com/spreadsheets/d/e/2PACX-1vTWUPgGQGm6xfcoUcB1Uk9SbFqSznlyDX__Fcvnfc_BG6UhPvN368E1iRU-cygXUTzrWT4c2mcGKtBz/pubhtml")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                rows = soup.find_all('tr')

                # Verificar se ao menos o ano ou a UF foi informado
                if not tokens["ano"] and not tokens["sigla_uf"]:
                    return "Por favor, especifique pelo menos o ano ou a sigla de UF para obter informações mais precisas."

                # Procurar pela linha correspondente na tabela
                for row in rows[1:]:  # Pular o cabeçalho
                    cells = row.find_all('td')
                    ano_cell = cells[0].get_text().strip()
                    mes_cell = cells[1].get_text().strip()[:3].lower()
                    uf_cell = cells[2].get_text().strip().upper()

                    # Checar condições com base nos tokens
                    if (tokens["ano"] == ano_cell if tokens["ano"] else True) and \
                       (tokens["sigla_uf"] == uf_cell if tokens["sigla_uf"] else True):

                        # Responder com os tipos de imposto solicitados
                        response_lines = []
                        for tipo in tokens["tipo_imposto"]:
                            imposto_value = cells[list(self.synonym_dict.keys()).index(tipo) + 3].get_text().strip()
                            response_lines.append(f"{tipo.replace('_', ' ').capitalize()}: R${imposto_value}")

                        if response_lines:
                            return "\n".join(response_lines)
                        else:
                            return "Nenhum dado encontrado para os critérios especificados."

                return random.choice(self.no_data_responses)
            else:
                return random.choice(self.error_responses)
        except requests.exceptions.RequestException as e:
            return random.choice(self.error_responses)

if __name__ == "__main__":
    root = ctk.CTk()
    chatbot = Chatbot(root)
    root.mainloop()
