# ============================================================================
# MONITOR DE PERFORMANCE PYTHON
# ============================================================================
# Este script serve como uma ferramenta de profiling para analisar o desempenho
# de outros scripts Python. Ele monitora em tempo real: uso de RAM, consumo de
# CPU e tempo de execução do processo alvo.
#
# FUNCIONAMENTO:
# 1. O usuário informa qual arquivo Python deseja monitorar
# 2. O script inicia o arquivo como um processo separado (subprocess)
# 3. Durante a execução, coleta métricas periodicamente usando a biblioteca psutil
# 4. Ao final, exibe estatísticas consolidadas (médias e picos)
#
# RECURSOS:
# - Menu interativo com configurações ajustáveis
# - Monitoramento em tempo real com logs opcionais
# - Exportação de dados para CSV
# - Suporte a monitoramento de subprocessos (threads/processos filhos)
# - Timeout configurável para evitar execuções infinitas
# ============================================================================

import psutil        # Biblioteca para acessar informações de processos e sistema (RAM, CPU, etc.)
import subprocess    # Permite criar e controlar outros processos (executar scripts externos)
import time          # Funções de tempo e cronômetro para medir duração da execução


# ============================================================================
# CONFIGURAÇÕES GLOBAIS
# ============================================================================
# Dicionário que armazena todas as configurações do monitor.
# Estas configurações podem ser alteradas pelo usuário através do menu.
#
# logs_ativos:              Se True, exibe logs em tempo real durante o monitoramento
# intervalo_segundos:       Tempo de espera entre cada medição (em segundos)
# timeout_segundos:         Tempo máximo de execução permitido (None = sem limite)
# monitorar_subprocessos:   Se True, inclui processos filhos na contagem de recursos
# exportar_csv:             Se True, salva os dados coletados em arquivo CSV
# ============================================================================
configuracoes = {
    "logs_ativos": True,
    "intervalo_segundos": 1.0,
    "timeout_segundos": None,
    "monitorar_subprocessos": False,
    "exportar_csv": False
}


def mostrar_banner():
    """
    Exibe o banner ASCII art com o nome do programa.
    Apenas uma identidade visual para tornar a interface mais amigável.
    """
    print(r"""
______                            ___  ___     _        _          
| ___ \                           |  \/  |    | |      (_)         
| |_/ / __ ___   ___ ___  ___ ___ | .  . | ___| |_ _ __ _  ___ ___ 
|  __/ '__/ _ \ / __/ _ \/ __/ __|| |\/| |/ _ \ __| '__| |/ __/ __|
| |  | | | (_) | (_|  __/\__ \__ \| |  | |  __/ |_| |  | | (__\__ \
\_|  |_|  \___/ \___\___||___/___/\_|  |_/\___|\__|_|  |_|\___|___/
""")


def mostrar_menu_principal():
    """
    Exibe o menu principal do programa.
    Oferece 3 opções: executar monitoramento, acessar configurações ou sair.
    """
    print("\n" + "=" * 50)
    print("MONITOR DE PERFORMANCE PYTHON")
    print("=" * 50)
    print("1. Executar script")
    print("2. Configurações")
    print("3. Sair")
    print("=" * 50)


def mostrar_menu_configuracoes():
    """
    Exibe o menu de configurações.
    Mostra o status atual de cada configuração para o usuário visualizar
    antes de fazer alterações.
    """
    print("\n" + "=" * 50)
    print("CONFIGURAÇÕES")
    print("=" * 50)
    
    # Converte valores booleanos para texto legível
    status_logs = "ATIVADO" if configuracoes["logs_ativos"] else "DESATIVADO"
    status_sub = "ATIVADO" if configuracoes["monitorar_subprocessos"] else "DESATIVADO"
    status_csv = "ATIVADO" if configuracoes["exportar_csv"] else "DESATIVADO"
    
    # Formata o timeout (None vira "Desativado")
    timeout_str = f"{configuracoes['timeout_segundos']}s" if configuracoes["timeout_segundos"] else "Desativado"

    # Exibe cada opção com seu status atual
    print(f"1. Logs em tempo real: [{status_logs}]")
    print(f"2. Intervalo de atualização: [{configuracoes['intervalo_segundos']}s]")
    print(f"3. Timeout: [{timeout_str}]")
    print(f"4. Monitorar subprocessos: [{status_sub}]")
    print(f"5. Exportar CSV: [{status_csv}]")
    print("6. Voltar ao menu principal")
    print("=" * 50)


def alternar_logs():
    """
    Alterna entre ligar/desligar os logs em tempo real.
    Quando desativado, o monitor funciona em modo silencioso (apenas resultado final).
    """
    # Inverte o valor booleano atual
    configuracoes["logs_ativos"] = not configuracoes["logs_ativos"]
    status = "ATIVADOS" if configuracoes["logs_ativos"] else "DESATIVADOS"
    print(f"\nLogs em tempo real {status}")


def ajustar_intervalo():
    """
    Permite o usuário alterar o intervalo entre medições.
    Valores menores = mais precisão, mas mais logs/métricas
    Valores maiores = menos precisão, mas execução mais leve
    """
    print(f"\nIntervalo atual: {configuracoes['intervalo_segundos']}s")
    try:
        # Solicita novo valor e converte para float
        novo_valor = float(input("Digite o novo intervalo em segundos (ex: 0.5, 1, 2): "))
        if novo_valor > 0:
            configuracoes["intervalo_segundos"] = novo_valor
            print(f"Intervalo ajustado para {novo_valor}s")
        else:
            print("Valor deve ser maior que 0")
    except ValueError:
        print("Valor inválido")


def ajustar_timeout():
    """
    Permite configurar um tempo máximo de execução.
    Útil para evitar que scripts com loops infinitos ou travamentos
# executem indefinidamente.
    """
    print(f"\nTimeout atual: {configuracoes['timeout_segundos']}s")
    print("Digite o timeout em segundos ou deixe em branco para desativar")
    try:
        entrada = input("Novo timeout: ").strip()
        if entrada == "":
            # Se usuário não digitar nada, desativa o timeout
            configuracoes["timeout_segundos"] = None
            print("Timeout desativado")
        else:
            novo_valor = float(entrada)
            if novo_valor > 0:
                configuracoes["timeout_segundos"] = novo_valor
                print(f"Timeout ajustado para {novo_valor}s")
            else:
                print("Valor deve ser maior que 0")
    except ValueError:
        print("Valor inválido")


def alternar_subprocessos():
    """
    Alterna o monitoramento de subprocessos.
    Quando ativado, o monitor também coleta métricas dos processos filhos
    criados pelo script alvo (útil para programas que usam multiprocessing).
    """
    configuracoes["monitorar_subprocessos"] = not configuracoes["monitorar_subprocessos"]
    status = "ATIVADO" if configuracoes["monitorar_subprocessos"] else "DESATIVADO"
    print(f"\nMonitoramento de subprocessos {status}")


def alternar_csv():
    """
    Alterna a exportação para CSV.
    Quando ativado, salva todas as medições em arquivo CSV para análise posterior.
    O arquivo contém: tempo, RAM e CPU em cada ponto de medição.
    """
    configuracoes["exportar_csv"] = not configuracoes["exportar_csv"]
    status = "ATIVADO" if configuracoes["exportar_csv"] else "DESATIVADO"
    print(f"\nExportação para CSV {status}")


def menu_configuracoes():
    """
    Loop do menu de configurações.
    Mantém o usuário neste menu até que ele escolha voltar (opção 6).
    """
    while True:
        mostrar_menu_configuracoes()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            alternar_logs()
        elif opcao == "2":
            ajustar_intervalo()
        elif opcao == "3":
            ajustar_timeout()
        elif opcao == "4":
            alternar_subprocessos()
        elif opcao == "5":
            alternar_csv()
        elif opcao == "6":
            # Sai do loop e retorna ao menu principal
            break
        else:
            print("Opção inválida")


def executar_monitoramento():
    """
    FUNÇÃO PRINCIPAL DE MONITORAMENTO
    
    Fluxo de execução:
    1. Solicita nome do arquivo Python a ser monitorado
    2. Inicia o arquivo como processo separado usando subprocess
    3. Cria objeto psutil.Process para coletar métricas do processo
    4. Em loop: coleta RAM, CPU e tempo a cada intervalo configurado
    5. Verifica timeout (se configurado)
    6. Opcionalmente inclui subprocessos na contagem
    7. Salva dados para CSV (se ativado)
    8. Exibe logs em tempo real (se ativado)
    9. Ao término: calcula e exibe estatísticas finais
    """
    # Cabeçalho da seção
    print("\n" + "=" * 50)
    print("EXECUTAR SCRIPT")
    print("=" * 50)
    print("monitor de performance de códigos Python")
    print("métricas analisadas: RAM consumida, pico de RAM, uso de CPU, tempo de execucao")
    print("")

    # Solicita nome do arquivo ao usuário
    arquivo = input("Nome do arquivo Python (ex: teste.py): ").strip()

    # Validação básica
    if not arquivo:
        print("Nome do arquivo não pode estar vazio")
        return

    # Tenta iniciar o processo
    try:
        # subprocess.Popen cria um novo processo independente
        # A lista ["python", arquivo] equivale a rodar "python arquivo.py" no terminal
        processo_alvo = subprocess.Popen(["python", arquivo])
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo}' não encontrado")
        return
    except Exception as e:
        print(f"Erro ao iniciar processo: {e}")
        return

    # Confirma início do monitoramento
    print(f"\nExecutando {arquivo} (PID {processo_alvo.pid})...")

    if configuracoes["logs_ativos"]:
        print("Monitorando RAM, CPU e tempo...\n")

    # Cria objeto psutil.Process para acessar métricas do processo
    # O psutil usa o PID (Process ID) para identificar o processo no sistema
    proc = psutil.Process(processo_alvo.pid)
    
    # Listas para armazenar todas as medições
    medidas_ram = []   # Armazena uso de RAM em MB
    medidas_cpu = []   # Armazena uso de CPU em %
    dados_csv = []     # Armazena dados formatados para exportação

    # Marca o momento inicial usando perf_counter (alta precisão)
    inicio = time.perf_counter()

    try:
        # Loop principal de monitoramento
        # processo_alvo.poll() retorna None enquanto o processo está rodando
        while processo_alvo.poll() is None:
            # Calcula tempo de execução atual
            agora = time.perf_counter()
            tempo_exec = agora - inicio

            # Verifica timeout (se configurado)
            if configuracoes["timeout_segundos"] and tempo_exec > configuracoes["timeout_segundos"]:
                print(f"\nTimeout atingido ({configuracoes['timeout_segundos']}s)")
                processo_alvo.terminate()  # Encerra o processo alvo
                break

            # COLETA DE MÉTRICAS
            # ------------------
            # memory_info().rss retorna RAM usada em bytes
            # Dividimos por 1024 duas vezes para converter para MB
            mem = proc.memory_info().rss / 1024 / 1024
            
            # cpu_percent() retorna uso percentual de CPU desde a última chamada
            # interval=None retorna imediatamente (não bloqueia)
            cpu = proc.cpu_percent(interval=None)

            # Se monitoramento de subprocessos estiver ativo,
            # soma as métricas de todos os processos filhos
            if configuracoes["monitorar_subprocessos"]:
                # proc.children() retorna lista de processos filhos
                for filho in proc.children(recursive=True):
                    try:
                        # Tenta acessar métricas do subprocesso
                        # psutil.NoSuchProcess pode ocorrer se o processo já terminou
                        mem += filho.memory_info().rss / 1024 / 1024
                        cpu += filho.cpu_percent(interval=None)
                    except psutil.NoSuchProcess:
                        # Ignora subprocessos que já encerraram
                        pass

            # Armazena medições nas listas
            medidas_ram.append(mem)
            medidas_cpu.append(cpu)

            # Salva dados para CSV (se ativado)
            # Formato: tempo,ram,cpu
            if configuracoes["exportar_csv"]:
                dados_csv.append(f"{tempo_exec:.2f},{mem:.2f},{cpu:.1f}")

            # Exibe logs em tempo real (se ativado)
            if configuracoes["logs_ativos"]:
                # Calcula médias até o momento
                media_ram = sum(medidas_ram) / len(medidas_ram)
                media_cpu = sum(medidas_cpu) / len(medidas_cpu)
                
                # Formata e exibe linha de log
                print(
                    f"[MONITOR] RAM: {mem:.2f} MB | "
                    f"Média RAM: {media_ram:.2f} MB | "
                    f"CPU: {cpu:.1f}% | "
                    f"Média CPU: {media_cpu:.1f}% | "
                    f"Tempo: {tempo_exec:.2f}s"
                )

            # Aguarda o intervalo configurado antes da próxima medição
            time.sleep(configuracoes["intervalo_segundos"])

    except KeyboardInterrupt:
        # Captura Ctrl+C para encerramento limpo
        print("\nMonitoramento interrompido pelo usuário.")
        processo_alvo.terminate()  # Garante que o processo alvo seja encerrado

    # CÁLCULO DAS ESTATÍSTICAS FINAIS
    # --------------------------------
    # Marca tempo final e calcula duração total
    fim = time.perf_counter()
    tempo_total = fim - inicio

    # Se houver medições (processo rodou por algum tempo)
    if medidas_ram:
        print("\n" + "=" * 50)
        print("RESULTADO FINAL")
        print("=" * 50)
        
        # Estatísticas básicas
        print(f"Tempo total: {tempo_total:.5f}s")
        print(f"RAM média: {sum(medidas_ram) / len(medidas_ram):.5f} MB")
        print(f"Pico de RAM: {max(medidas_ram):.5f} MB")
        print(f"CPU média: {sum(medidas_cpu) / len(medidas_cpu):.2f}%")
        print(f"Pico de CPU: {max(medidas_cpu):.2f}%")

        # Exportação para CSV (se ativado)
        if configuracoes["exportar_csv"]:
            # Gera nome único baseado no arquivo monitorado e timestamp
            nome_csv = f"monitor_{arquivo.replace('.py', '')}_{int(time.time())}.csv"
            with open(nome_csv, "w") as f:
                # Cabeçalho do CSV
                f.write("tempo_segundos,ram_mb,cpu_percent\n")
                # Dados coletados
                f.write("\n".join(dados_csv))
            print(f"\nDados exportados para: {nome_csv}")

    print("Processo finalizado.")


def main():
    """
    FUNÇÃO PRINCIPAL
    
    Ponto de entrada do programa. Exibe o banner e entra no loop
    do menu principal, mantendo o programa rodando até o usuário
# escolher sair.
    """
    mostrar_banner()

    # Loop infinito do menu principal
    while True:
        mostrar_menu_principal()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            # Inicia o fluxo de monitoramento
            executar_monitoramento()
        elif opcao == "2":
            # Abre submenu de configurações
            menu_configuracoes()
        elif opcao == "3":
            # Encerra o programa
            print("\nSaindo...")
            break
        else:
            print("Opção inválida")


# Ponto de entrada do programa
# Verifica se o script está sendo executado diretamente (não importado como módulo)
if __name__ == "__main__":
    main()
