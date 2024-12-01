from cx_Freeze import setup, Executable

# Defina o script que você quer transformar em executável
executables = [Executable("chatbot5.py", icon="icone.ico")]

# Configura a construção
setup(
    name="ChatBot5",
    version="1.0",
    description="ChatBot com Python",
    executables=executables
)
