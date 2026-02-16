import time

dados = []

print("Script alvo iniciado...")

i = 0
while i < 20:
    # consome ~30 MB por ciclo
    dados.append(bytearray(30 * 1024 * 1024))

    # pequeno trabalho de CPU
    soma = sum(range(1_000_000))

    i += 1
    print(f"Ciclo {i} | memória alocada ~{i * 30} MB")

    time.sleep(0.02)