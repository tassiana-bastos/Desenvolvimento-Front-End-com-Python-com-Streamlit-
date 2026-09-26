from statsbombpy import sb
import pandas as pd

"""
# Lista as competições disponíveis
competicoes = sb.competitions()

#print("\nCOMPETIÇÕES DISPONÍVEIS:\n")
#print(competicoes)
#print(competicoes.columns.tolist())

# competições disponíveis
competitions = sb.competitions()
print("Competições disponíveis:")
print(competitions.head())

# Teste com Women's World Cup 2019
comp_id = 72
season_id = 30

# Lista das partidas dessa competição/temporada
matches = sb.matches(competition_id=comp_id, season_id=season_id)
print("\nPartidas disponíveis:")
print(matches[['match_id', 'home_team', 'away_team', 'match_date']].head())

# Match_id para teste
test_match_id = matches.iloc[0]['match_id']
print(f"\nMatch ID para teste: {test_match_id}")

# eventos dessa partida
events = sb.events(match_id=test_match_id)
print("\nEventos da partida:")
print(events.head())

"""

# ID da partida que a ser analisada

match_id= 3888787

# Carrega os eventos
eventos = sb.events(match_id=match_id)

chutes = eventos[
    eventos["type"] == "Shot"
]

print("Total de chutes:", len(chutes))

# Chutes no 1º tempo
chutes_1_tempo = chutes[
    chutes["period"] == 1
]

print("Chutes no 1º tempo:", len(chutes_1_tempo))

# Chutes no 2º tempo
chutes_2_tempo = chutes[
    chutes["period"] == 2
]

print("Chutes no 2º tempo:", len(chutes_2_tempo))

# Gols
gols = chutes[
    chutes["shot_outcome"] == "Goal"
]

print("Total de gols:", len(gols))

print("\nGols:")
print(
    gols[
        ["minute", "second", "team", "player", "shot_outcome"]
    ]
)


"""
print("\nCOLUNAS DE LOCALIZACAO:")
print()

print("location:", "location" in eventos.columns)
print("pass_end_location:", "pass_end_location" in eventos.columns)


print("\nEXEMPLOS DE LOCATION:")
print(
    eventos["location"]
    .dropna()
    .head(10)
)


print("\nEXEMPLOS DE PASS_END_LOCATION:")
print(
    eventos["pass_end_location"]
    .dropna()
    .head(10)
)
"""
"""


print("\n" + "=" * 60)
print("VERIFICACAO DAS COORDENADAS DOS EVENTOS")
print("=" * 60)


# 1. Verifica se as colunas existem
print("\n1. COLUNAS DISPONIVEIS")

print(
    "location:",
    "location" in eventos.columns
)

print(
    "pass_end_location:",
    "pass_end_location" in eventos.columns
)


# 2. Verifica exemplos de location
print("\n2. EXEMPLOS DE LOCATION")

print(
    eventos["location"]
    .dropna()
    .head(10)
)


# 3. Verifica exemplos de pass_end_location
print("\n3. EXEMPLOS DE PASS_END_LOCATION")

print(
    eventos["pass_end_location"]
    .dropna()
    .head(10)
)


# 4. Verifica especificamente os passes
passes = eventos[
    eventos["type"] == "Pass"
].copy()


print("\n4. COORDENADAS DOS PASSES")

print(
    passes[
        [
            "player",
            "team",
            "location",
            "pass_end_location"
        ]
    ]
    .head(10)
)


# 5. Verifica quantos passes possuem coordenadas
print("\n5. QUANTIDADE DE PASSES")

print(
    "Total de passes:",
    len(passes)
)

print(
    "Passes com location:",
    passes["location"].notna().sum()
)

print(
    "Passes com pass_end_location:",
    passes["pass_end_location"].notna().sum()
)

"""