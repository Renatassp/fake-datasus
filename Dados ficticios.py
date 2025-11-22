#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
GERAR BASES COM DADOS SENSÍVEIS FICTÍCIOS
==============================================================================
Resumo: Criação de 2 bancos fictícios com variáveis sensíveis para linkage
- 10% de overlap
- Inconsistências intencionais: duplicatas, campos vazios, abreviações, 
  formatos divergentes, datas em formatos diferentes, campos vazios e CNS inválidos
- Registros exclusivos em cada banco
==============================================================================
"""
# ==================== IMPORTAÇÃO E CONFIGURAÇÃO ====================
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

# Configurações
fake = Faker('pt_BR')  # Gera nomes brasileiros
random.seed(42)  # Para reprodutibilidade

# Tamanhos dos bancos
n_vacina = 6126278
n_sinan = 6382906
n_base_comum = int(n_vacina * 0.10)  # 10% do menor banco

# ==================== FUNÇÕES AUXILIARES ====================

def gerar_cns():
    """Gera CNS válido (15 dígitos, começando com 7, 8 ou 9)"""
    prefixo = str(random.choice([7, 8, 9]))
    resto = ''.join([str(random.randint(0, 9)) for _ in range(14)])
    return prefixo + resto

def gerar_cns_com_inconsistencias():
    """Gera CNS com possibilidade de estar vazio ou inválido"""
    prob = random.random()
    if prob < 0.05:  # 5% de CNS vazios
        return ""
    elif prob < 0.08:  # 3% de CNS inválidos (menos de 15 dígitos)
        return ''.join([str(random.randint(0, 9)) for _ in range(random.randint(10, 14))])
    else:
        return gerar_cns()

def gerar_nome_paciente():
    """Gera nome completo do paciente"""
    return fake.name()

def gerar_nome_paciente_com_inconsistencias(nome_original):
    """Adiciona inconsistências ao nome do paciente"""
    prob = random.random()
    if prob < 0.03:  # 3% de nomes vazios
        return ""
    elif prob < 0.10:  # 7% de nomes com abreviações
        partes = nome_original.split()
        if len(partes) >= 3:
            # Abrevia nome do meio
            partes[1] = partes[1][0] + "."
        return ' '.join(partes)
    elif prob < 0.12:  # 2% de nomes em maiúsculo
        return nome_original.upper()
    elif prob < 0.14:  # 2% de nomes em minúsculo
        return nome_original.lower()
    else:
        return nome_original

def gerar_nome_mae():
    """Gera nome da mãe"""
    primeiro = fake.first_name_female()
    meio = fake.last_name()
    ultimo = fake.last_name()
    return f"{primeiro} {meio} {ultimo}"

def gerar_nome_mae_com_inconsistencias(nome_original):
    """Adiciona inconsistências ao nome da mãe"""
    prob = random.random()
    if prob < 0.08:  # 8% de nomes vazios (dados faltantes)
        return ""
    elif prob < 0.25:  # 17% de nomes com abreviações
        partes = nome_original.split()
        if len(partes) >= 3:
            # Abrevia o nome do meio
            partes[1] = partes[1][0]
        return ' '.join(partes)
    elif prob < 0.28:  # 3% em maiúsculo
        return nome_original.upper()
    else:
        return nome_original

def gerar_data_nascimento():
    """Gera data de nascimento entre 1920 e 2024"""
    inicio = datetime(1920, 1, 1)
    fim = datetime(2024, 12, 31)
    delta = fim - inicio
    dias_aleatorios = random.randint(0, delta.days)
    return inicio + timedelta(days=dias_aleatorios)

def formatar_data_com_inconsistencias(data):
    """Formata data com formatos divergentes"""
    prob = random.random()
    if prob < 0.05:  # 5% de datas vazias
        return ""
    elif prob < 0.35:  # 30% no formato DD/MM/YYYY
        return data.strftime("%d/%m/%Y")
    elif prob < 0.60:  # 25% no formato YYYY-MM-DD
        return data.strftime("%Y-%m-%d")
    elif prob < 0.75:  # 15% no formato DD-MM-YYYY
        return data.strftime("%d-%m-%Y")
    elif prob < 0.85:  # 10% no formato DDMMYYYY (sem separador)
        return data.strftime("%d%m%Y")
    else:  # 15% no formato padrão ISO
        return data.strftime("%Y/%m/%d")

# ============== GERAÇÃO DA BASE COMUM (10% overlap) ====================

base_comum = []
for i in range(n_base_comum):
    if i % 500000 == 0:
        print(f"  Processando: {i:,}/{n_base_comum:,}")
    
    nome_pac = gerar_nome_paciente()
    nome_mae = gerar_nome_mae()
    data_nasc = gerar_data_nascimento()
    cns = gerar_cns()
    
    base_comum.append({
        'nome_paciente_original': nome_pac,
        'nome_mae_original': nome_mae,
        'data_nasc_original': data_nasc,
        'numero_sus_original': cns
    })

df_base_comum = pd.DataFrame(base_comum)

# ==================== BANCO 1: VACINA ====================

# Pegar base comum e adicionar inconsistências
df_vacina_comum = df_base_comum.copy()
df_vacina_comum['nome_paciente'] = df_vacina_comum['nome_paciente_original'].apply(
    gerar_nome_paciente_com_inconsistencias
)
df_vacina_comum['nome_mae'] = df_vacina_comum['nome_mae_original'].apply(
    gerar_nome_mae_com_inconsistencias
)
df_vacina_comum['data_nasc'] = df_vacina_comum['data_nasc_original'].apply(
    formatar_data_com_inconsistencias
)
df_vacina_comum['numero_sus'] = df_vacina_comum['numero_sus_original'].apply(
    lambda x: gerar_cns_com_inconsistencias() if random.random() < 0.08 else x
)

# Adicionar registros exclusivos do banco VACINA
n_exclusivos_vacina = n_vacina - n_base_comum
print(f"  Adicionando {n_exclusivos_vacina:,} registros exclusivos...")

exclusivos_vacina = []
for i in range(n_exclusivos_vacina):
    if i % 500000 == 0:
        print(f"    Processando: {i:,}/{n_exclusivos_vacina:,}")
    
    nome_pac = gerar_nome_paciente()
    nome_mae = gerar_nome_mae()
    data_nasc = gerar_data_nascimento()
    
    exclusivos_vacina.append({
        'nome_paciente': gerar_nome_paciente_com_inconsistencias(nome_pac),
        'nome_mae': gerar_nome_mae_com_inconsistencias(nome_mae),
        'data_nasc': formatar_data_com_inconsistencias(data_nasc),
        'numero_sus': gerar_cns_com_inconsistencias()
    })

df_exclusivos_vacina = pd.DataFrame(exclusivos_vacina)

# Juntar base comum com exclusivos
df_vacina = pd.concat([
    df_vacina_comum[['nome_paciente', 'nome_mae', 'data_nasc', 'numero_sus']],
    df_exclusivos_vacina
], ignore_index=True)

# Adicionar duplicatas intencionais (5% de duplicatas)
n_duplicatas_vacina = int(n_vacina * 0.05)
print(f"  Adicionando {n_duplicatas_vacina:,} duplicatas intencionais...")
indices_duplicar = random.sample(range(len(df_vacina)), n_duplicatas_vacina)
df_duplicatas_vacina = df_vacina.iloc[indices_duplicar].copy()
df_vacina = pd.concat([df_vacina, df_duplicatas_vacina], ignore_index=True)

# Embaralhar
df_vacina = df_vacina.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\n✓ Banco VACINA criado: {len(df_vacina):,} registros")

# ==================== BANCO 2: SINAN ====================

# Pegar base comum e adicionar DIFERENTES inconsistências
df_sinan_comum = df_base_comum.copy()
df_sinan_comum['nome_paciente'] = df_sinan_comum['nome_paciente_original'].apply(
    gerar_nome_paciente_com_inconsistencias
)
df_sinan_comum['nome_mae'] = df_sinan_comum['nome_mae_original'].apply(
    gerar_nome_mae_com_inconsistencias
)
df_sinan_comum['data_nasc'] = df_sinan_comum['data_nasc_original'].apply(
    formatar_data_com_inconsistencias
)
df_sinan_comum['numero_sus'] = df_sinan_comum['numero_sus_original'].apply(
    lambda x: gerar_cns_com_inconsistencias() if random.random() < 0.08 else x
)

# Adicionar registros exclusivos do banco SINAN
n_exclusivos_sinan = n_sinan - n_base_comum
print(f"  Adicionando {n_exclusivos_sinan:,} registros exclusivos...")

exclusivos_sinan = []
for i in range(n_exclusivos_sinan):
    if i % 500000 == 0:
        print(f"    Processando: {i:,}/{n_exclusivos_sinan:,}")
    
    nome_pac = gerar_nome_paciente()
    nome_mae = gerar_nome_mae()
    data_nasc = gerar_data_nascimento()
    
    exclusivos_sinan.append({
        'nome_paciente': gerar_nome_paciente_com_inconsistencias(nome_pac),
        'nome_mae': gerar_nome_mae_com_inconsistencias(nome_mae),
        'data_nasc': formatar_data_com_inconsistencias(data_nasc),
        'numero_sus': gerar_cns_com_inconsistencias()
    })

df_exclusivos_sinan = pd.DataFrame(exclusivos_sinan)

# Juntar base comum com exclusivos
df_sinan = pd.concat([
    df_sinan_comum[['nome_paciente', 'nome_mae', 'data_nasc', 'numero_sus']],
    df_exclusivos_sinan
], ignore_index=True)

# Adicionar duplicatas intencionais (5% de duplicatas)
n_duplicatas_sinan = int(n_sinan * 0.05)
print(f"  Adicionando {n_duplicatas_sinan:,} duplicatas intencionais...")
indices_duplicar = random.sample(range(len(df_sinan)), n_duplicatas_sinan)
df_duplicatas_sinan = df_sinan.iloc[indices_duplicar].copy()
df_sinan = pd.concat([df_sinan, df_duplicatas_sinan], ignore_index=True)

# Embaralhar
df_sinan = df_sinan.sample(frac=1, random_state=43).reset_index(drop=True)

print(f"\n✓ Banco SINAN criado: {len(df_sinan):,} registros")

# ==================== SALVAR ARQUIVOS ====================

# Salvar em chunks para evitar problemas de memória
df_vacina.to_csv('nomes_ficticios_vacina.csv', index=False)
df_sinan.to_csv('nomes_ficticios_sinan.csv', index=False)

