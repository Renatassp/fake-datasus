#Criando os arquivos de nomes fictícios
###Código Python que gera dados sintéticos para simulação de linkage de registros de saúde
#Cria um dataset fake de 6 milhões de registros simulando dados de pacientes do SUS para testes de linkage (vinculação de registros)

# Importação 
import pandas as pd #organizar os dados em um DataFrame e salvar em CSV.
from faker import Faker #biblioteca que gera dados fictícios (nomes, cidades, etc.).
import Random #usado para gerar escolhas aleatórias

# Configurações
fake = Faker('pt_BR')  # Dados em português do Brasil
total_linhas = 6_000_000  # 6 milhões de linhas

# Variáveis pré-definidas
racas = ["Branca", "Preta", "Parda", "Amarela", "Indígena", "Outra"]  # 6 opções
sexos = ["Masculino", "Feminino", "Outro"]  # 3 opções
municipios = [fake.city() for _ in range(100)]  # 100 municípios fictícios

#Funções personalizadas
# Função para gerar CNS SUS válido (15 dígitos, começando com 7, 8 ou 9)
def gerar_cns():
    prefixo = str(random.choice([7, 8, 9]))  # CNS válido começa com 7, 8 ou 9
    resto = ''.join([str(random.randint(0, 9)) for _ in range(14)])
    return prefixo + resto

# Função para gerar nome da mãe com variações (ex: "Maria de Fátima Fernandes" ou "Maria de F Fernandes")
def gerar_nome_mae():
    nome = fake.first_name_female() + " " + fake.last_name() + " " + fake.last_name()
    if random.random() > 0.5:  # 50% de chance de abreviar um nome
        partes = nome.split()
        partes[1] = partes[1][0]  # Abrevia o segundo nome (ex: "Fátima" -> "F")
        nome = ' '.join(partes)
    return nome

# Criar DataFrame
dados = {
    "Raça": [random.choice(racas) for _ in range(total_linhas)],
    "Sexo": [random.choice(sexos) for _ in range(total_linhas)],
    "CNS_SUS": [gerar_cns() for _ in range(total_linhas)],
    "Nome_Mãe": [gerar_nome_mae() for _ in range(total_linhas)],
    "Município": [random.choice(municipios) for _ in range(total_linhas)]
}

df = pd.DataFrame(dados)

# Salvar em CSV (opcional, dividido em partes para evitar arquivos muito grandes)
df.to_csv("dados_linkage.csv", index=False, chunksize=1_000_000)  # Divide em 6 arquivos de 1M linhas
