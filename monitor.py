#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONITOR DE PERFORMANCE PYTHON

Este script serve como uma ferramenta de profiling para analisar o desempenho
de outros scripts Python. Ele monitora em tempo real: uso de RAM, consumo de
CPU e tempo de execução do processo alvo.

FUNCIONAMENTO:
1. O usuário informa qual arquivo Python deseja monitorar
2. O script inicia o arquivo como um processo separado (subprocess)
3. Durante a execução, coleta métricas periodicamente usando a biblioteca psutil
4. Ao final, exibe estatísticas consolidadas (médias e picos)

RECURSOS:
- Menu interativo com configurações ajustáveis
- Monitoramento em tempo real com logs opcionais
- Exportação de dados para CSV
- Suporte a monitoramento de subprocessos (threads/processos filhos)
- Timeout configurável para evitar execuções infinitas

USO: python monitor.py [opções]

OPÇÕES:
  -h, --help       Mostra esta mensagem de ajuda
  -c, --config     Abre diretamente o menu de configurações
  -f FILE          Executa o arquivo especificado sem menu

EXEMPLOS:
  python monitor.py
  python monitor.py --help
  python monitor.py -f teste.py
"""

import psutil
import subprocess
import time
import os
import sys
import itertools
import threading


# Cores RETRO - estilo terminal antigo (amber/phosphor)
class Cores:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Cores Retro (Amber/Phosphor)
    AMBER = '\033[38;5;208m'      # Âmbar clássico
    AMBER_ESCURO = '\033[38;5;130m'  # Âmbar escuro
    VERDE_FOSFORO = '\033[38;5;82m'  # Verde fosforo
    VERDE_ESCURO = '\033[38;5;22m'   # Verde escuro
    
    # Cores adicionais retro
    MARROM = '\033[38;5;94m'
    LARANJA = '\033[38;5;166m'
    AMARELO = '\033[38;5;214m'
    CIANO = '\033[38;5;51m'
    
    # Branco/cinza retro
    BRANCO = '\033[38;5;250m'
    CINZA = '\033[38;5;240m'
    CINZA_CLARO = '\033[38;5;245m'


# Configurações globais
configuracoes = {
    "logs_ativos": True,
    "intervalo_segundos": 1.0,
    "timeout_segundos": None,
    "monitorar_subprocessos": False,
    "exportar_csv": False
}


def limpar_tela():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')


def box(texto, tipo="info", padding=1):
    """Cria uma caixa estilizada ao redor do texto - estilo retro."""
    linhas = texto.split('\n')
    max_len = max(len(linha) for linha in linhas)
    
    # Cores por tipo - estilo retro
    cores = {
        "info": Cores.AMBER,
        "sucesso": Cores.VERDE_FOSFORO,
        "erro": Cores.LARANJA,
        "aviso": Cores.AMARELO
    }
    cor = cores.get(tipo, Cores.AMBER)
    
    # Bordas estilo retro (duplas)
    topo = f"{cor}╔{'═' * (max_len + padding * 2)}╗{Cores.RESET}"
    fundo = f"{cor}╚{'═' * (max_len + padding * 2)}╝{Cores.RESET}"
    
    print(topo)
    for _ in range(padding):
        print(f"{cor}║{' ' * (max_len + padding * 2)}║{Cores.RESET}")
    
    for linha in linhas:
        espacos = max_len - len(linha)
        print(f"{cor}║{Cores.RESET}{' ' * padding}{linha}{' ' * espacos}{' ' * padding}{cor}║{Cores.RESET}")
    
    for _ in range(padding):
        print(f"{cor}║{' ' * (max_len + padding * 2)}║{Cores.RESET}")
    
    print(fundo)


def tabela(headers, rows, align="left"):
    """Renderiza uma tabela ASCII - estilo retro."""
    # Calcula larguras
    all_rows = [headers] + rows
    col_widths = [max(len(str(row[i])) for row in all_rows) for i in range(len(headers))]
    
    # Cria linha horizontal estilo retro
    line = f"{Cores.AMBER_ESCURO}+" + "+".join(["-" * (w + 2) for w in col_widths]) + f"+{Cores.RESET}"
    
    def format_row(row, is_header=False):
        cells = []
        for i, cell in enumerate(row):
            cell_str = str(cell)
            padding = col_widths[i] - len(cell_str)
            if align == "center":
                left = padding // 2
                right = padding - left
                formatted = " " + " " * left + cell_str + " " * right + " "
            elif align == "right":
                formatted = " " + " " * padding + cell_str + " "
            else:
                formatted = " " + cell_str + " " * padding + " "
            cells.append(formatted)
        return f"{Cores.AMBER_ESCURO}|{Cores.RESET}" + f"{Cores.AMBER_ESCURO}|{Cores.RESET}".join(cells) + f"{Cores.AMBER_ESCURO}|{Cores.RESET}"
    
    # Imprime tabela
    print(line)
    print(f"{Cores.AMBER}{Cores.BOLD}{format_row(headers)}{Cores.RESET}")
    print(line)
    for row in rows:
        print(format_row(row))
    print(line)


def spinner(mensagem="Processando"):
    """Cria um spinner animado - estilo retro."""
    spinner_chars = itertools.cycle(['|', '/', '-', '\\'])
    stop_spinner = threading.Event()
    
    def spin():
        while not stop_spinner.is_set():
            char = next(spinner_chars)
            sys.stdout.write(f"\r  {Cores.AMBER}[{char}]{Cores.RESET} {mensagem}...")
            sys.stdout.flush()
            time.sleep(0.2)
        sys.stdout.write(f"\r  {Cores.VERDE_FOSFORO}[OK]{Cores.RESET} {mensagem} completo!{' ' * 20}\n")
        sys.stdout.flush()
    
    thread = threading.Thread(target=spin)
    thread.start()
    return stop_spinner, thread


def banner():
    """Exibe o banner do programa - estilo retro terminal."""
    print()
    print(f"{Cores.AMBER}    _____________________________________________________________{Cores.RESET}")
    print(f"{Cores.AMBER}   /                                                           \\{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}                                                             {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}    {Cores.AMBER}{Cores.BOLD}██████╗ ██████╗  ██████╗  ██████╗███████╗███████╗{Cores.RESET}       {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}    {Cores.AMBER}{Cores.BOLD}██╔══██╗██╔══██╗██╔═══██╗██╔════╝██╔════╝██╔════╝{Cores.RESET}       {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}    {Cores.AMBER}{Cores.BOLD}██████╔╝██████╔╝██║   ██║██║     █████╗  ███████╗{Cores.RESET}       {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}    {Cores.AMBER}{Cores.BOLD}██╔═══╝ ██╔══██╗██║   ██║██║     ██╔══╝  ╚════██║{Cores.RESET}       {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}    {Cores.AMBER}{Cores.BOLD}██║     ██║  ██║╚██████╔╝╚██████╗██║     ███████║{Cores.RESET}       {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}    {Cores.AMBER}{Cores.BOLD}╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚═╝     ╚══════╝{Cores.RESET}       {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}                                                            {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}          {Cores.AMBER}{Cores.BOLD}PROCESS_METRICS v1.0{Cores.RESET}                              {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}     {Cores.AMBER_ESCURO}Monitor de Performance Python{Cores.RESET}                           {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}                                                             {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}   \\___________________________________________________________{Cores.RESET}/")
    print()


def mostrar_ajuda():
    """Exibe a mensagem de ajuda do programa - estilo retro."""
    print(f"""
{Cores.AMBER}╔══════════════════════════════════════════════════════════════════╗{Cores.RESET}
{Cores.AMBER}║{Cores.RESET}  {Cores.AMBER}{Cores.BOLD}PROCESS_METRICS v1.0{Cores.RESET} - Monitor de Performance Python         {Cores.AMBER}║{Cores.RESET}
{Cores.AMBER}╚══════════════════════════════════════════════════════════════════╝{Cores.RESET}

{Cores.AMBER}{Cores.BOLD}[DESCRIÇÃO]{Cores.RESET}
  Ferramenta de profiling para analisar desempenho de scripts Python.
  Monitora em tempo real: uso de RAM, consumo de CPU e tempo de execução.

{Cores.AMBER}{Cores.BOLD}[USO]{Cores.RESET}
  python monitor.py [opções]

{Cores.AMBER}{Cores.BOLD}[OPÇÕES]{Cores.RESET}
  {Cores.VERDE_FOSFORO}-h, --help{Cores.RESET}       Mostra esta mensagem de ajuda
  {Cores.VERDE_FOSFORO}-c, --config{Cores.RESET}     Abre diretamente o menu de configurações
  {Cores.VERDE_FOSFORO}-f FILE{Cores.RESET}          Executa o arquivo especificado sem menu

{Cores.AMBER}{Cores.BOLD}[RECURSOS]{Cores.RESET}
  * Menu interativo com configurações ajustáveis
  * Monitoramento em tempo real com logs opcionais
  * Exportação de dados para CSV
  * Suporte a monitoramento de subprocessos
  * Timeout configurável

{Cores.AMBER}{Cores.BOLD}[EXEMPLOS]{Cores.RESET}
  {Cores.CINZA}# Iniciar com menu interativo{Cores.RESET}
  python monitor.py

  {Cores.CINZA}# Mostrar ajuda{Cores.RESET}
  python monitor.py --help

  {Cores.CINZA}# Executar arquivo diretamente{Cores.RESET}
  python monitor.py -f teste.py

  {Cores.CINZA}# Abrir configurações{Cores.RESET}
  python monitor.py -c

{Cores.CINZA}Para mais informações, consulte o arquivo README.md{Cores.RESET}
""")


def menu_principal():
    """Exibe o menu principal do programa - estilo retro."""
    print()
    print(f"{Cores.AMBER}  +-------------------------------------------------------------+{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}  {Cores.AMBER}{Cores.BOLD}MENU PRINCIPAL{Cores.RESET}                                              {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  +-------------------------------------------------------------+{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}                                                             {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}    [{Cores.VERDE_FOSFORO}1{Cores.RESET}] Executar script                                   {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}    [{Cores.AMARELO}2{Cores.RESET}] Configurações                                     {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}    [{Cores.LARANJA}3{Cores.RESET}] Sair                                              {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}                                                             {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  +-------------------------------------------------------------+{Cores.RESET}")


def menu_config():
    """Exibe o menu de configurações - estilo retro."""
    status_logs = f"{Cores.VERDE_FOSFORO}[ON]{Cores.RESET}" if configuracoes["logs_ativos"] else f"{Cores.CINZA}[OFF]{Cores.RESET}"
    status_sub = f"{Cores.VERDE_FOSFORO}[ON]{Cores.RESET}" if configuracoes["monitorar_subprocessos"] else f"{Cores.CINZA}[OFF]{Cores.RESET}"
    status_csv = f"{Cores.VERDE_FOSFORO}[ON]{Cores.RESET}" if configuracoes["exportar_csv"] else f"{Cores.CINZA}[OFF]{Cores.RESET}"
    timeout_str = f"{Cores.AMBER}{configuracoes['timeout_segundos']}s{Cores.RESET}" if configuracoes["timeout_segundos"] else f"{Cores.CINZA}--{Cores.RESET}"
    
    print()
    print(f"{Cores.AMBER}  +-------------------------------------------------------------+{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}  {Cores.AMBER}{Cores.BOLD}CONFIGURAÇÕES{Cores.RESET}                                               {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  +-------------------------------------------------------------+{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}                                                             {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}    [1] Logs em tempo real         {status_logs}              {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}    [2] Intervalo de atualização   {Cores.AMBER}{configuracoes['intervalo_segundos']}s{Cores.RESET}                 {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}    [3] Timeout                    {timeout_str}                 {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}    [4] Monitorar subprocessos     {status_sub}              {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}    [5] Exportar CSV               {status_csv}              {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}    [{Cores.LARANJA}6{Cores.RESET}] Voltar ao menu principal                          {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  |{Cores.RESET}                                                             {Cores.AMBER}|{Cores.RESET}")
    print(f"{Cores.AMBER}  +-------------------------------------------------------------+{Cores.RESET}")


def validar_float(mensagem, min_val=None, permitir_vazio=False):
    """Solicita input numérico com validação."""
    while True:
        entrada = input(mensagem).strip()
        
        if permitir_vazio and entrada == "":
            return None
        
        try:
            valor = float(entrada)
            if min_val is not None and valor <= min_val:
                print(f"  {Cores.LARANJA}[ERR]{Cores.RESET} Valor deve ser maior que {min_val}")
                continue
            return valor
        except ValueError:
            print(f"  {Cores.LARANJA}[ERR]{Cores.RESET} Valor inválido. Digite um número.")


def alternar_logs():
    """Alterna entre ligar/desligar os logs em tempo real."""
    configuracoes["logs_ativos"] = not configuracoes["logs_ativos"]
    status = "ATIVADO" if configuracoes["logs_ativos"] else "DESATIVADO"
    box(f"Logs em tempo real: {status}", tipo="sucesso" if configuracoes["logs_ativos"] else "info")


def ajustar_intervalo():
    """Permite o usuário alterar o intervalo entre medições."""
    print(f"\n  Intervalo atual: {Cores.AMBER}{configuracoes['intervalo_segundos']}s{Cores.RESET}")
    novo_valor = validar_float(f"  Novo intervalo (s): {Cores.AMBER}", min_val=0)
    print(Cores.RESET, end="")
    
    if novo_valor:
        configuracoes["intervalo_segundos"] = novo_valor
        box(f"Intervalo ajustado para {novo_valor}s", tipo="sucesso")


def ajustar_timeout():
    """Permite configurar um tempo máximo de execução."""
    atual = f"{configuracoes['timeout_segundos']}s" if configuracoes["timeout_segundos"] else "--"
    print(f"\n  Timeout atual: {Cores.AMBER}{atual}{Cores.RESET}")
    print(f"  {Cores.CINZA}(deixe em branco para desativar){Cores.RESET}")
    
    novo_valor = validar_float(f"  Novo timeout (s): {Cores.AMBER}", min_val=0, permitir_vazio=True)
    print(Cores.RESET, end="")
    
    if novo_valor is None:
        configuracoes["timeout_segundos"] = None
        box("Timeout desativado", tipo="info")
    else:
        configuracoes["timeout_segundos"] = novo_valor
        box(f"Timeout ajustado para {novo_valor}s", tipo="sucesso")


def alternar_subprocessos():
    """Alterna o monitoramento de subprocessos."""
    configuracoes["monitorar_subprocessos"] = not configuracoes["monitorar_subprocessos"]
    status = "ATIVADO" if configuracoes["monitorar_subprocessos"] else "DESATIVADO"
    box(f"Monitoramento de subprocessos: {status}", tipo="sucesso" if configuracoes["monitorar_subprocessos"] else "info")


def alternar_csv():
    """Alterna a exportação para CSV."""
    configuracoes["exportar_csv"] = not configuracoes["exportar_csv"]
    status = "ATIVADO" if configuracoes["exportar_csv"] else "DESATIVADO"
    box(f"Exportação para CSV: {status}", tipo="sucesso" if configuracoes["exportar_csv"] else "info")


def menu_configuracoes():
    """Loop do menu de configurações."""
    while True:
        menu_config()
        opcao = input(f"\n  {Cores.AMBER}>>{Cores.RESET} ").strip()

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
            break
        else:
            print(f"  {Cores.LARANJA}[ERR]{Cores.RESET} Opção inválida")


def executar_monitoramento(arquivo=None):
    """
    Função principal de monitoramento.
    Executa um script Python e coleta métricas de performance em tempo real.
    """
    if arquivo is None:
        print()
        print(f"{Cores.VERDE_FOSFORO}  +-------------------------------------------------------------+{Cores.RESET}")
        print(f"{Cores.VERDE_FOSFORO}  |{Cores.RESET}  {Cores.VERDE_FOSFORO}{Cores.BOLD}EXECUTAR SCRIPT{Cores.RESET}                                             {Cores.VERDE_FOSFORO}|{Cores.RESET}")
        print(f"{Cores.VERDE_FOSFORO}  +-------------------------------------------------------------+{Cores.RESET}")
        print()
        
        arquivo = input(f"  Arquivo Python: {Cores.AMBER}").strip()
        print(Cores.RESET, end="")

        if not arquivo:
            box("Nome do arquivo não pode estar vazio", tipo="erro")
            return
    
    # Valida extensão do arquivo
    if not arquivo.endswith('.py'):
        arquivo += '.py'

    try:
        processo_alvo = subprocess.Popen(["python", arquivo])
    except FileNotFoundError:
        box(f"Arquivo '{arquivo}' não encontrado", tipo="erro")
        return
    except Exception as e:
        box(f"Erro ao iniciar processo: {e}", tipo="erro")
        return

    print(f"\n  {Cores.VERDE_FOSFORO}[RUN]{Cores.RESET} Executando {Cores.AMBER}{arquivo}{Cores.RESET} (PID {processo_alvo.pid})")
    
    if configuracoes["logs_ativos"]:
        print(f"  {Cores.CINZA}Iniciando coleta de métricas...{Cores.RESET}\n")

    proc = psutil.Process(processo_alvo.pid)
    
    medidas_ram = []
    medidas_cpu = []
    dados_csv = []
    inicio = time.perf_counter()

    try:
        while processo_alvo.poll() is None:
            agora = time.perf_counter()
            tempo_exec = agora - inicio

            if configuracoes["timeout_segundos"] and tempo_exec > configuracoes["timeout_segundos"]:
                print(f"\n  {Cores.AMARELO}[TIMEOUT]{Cores.RESET} Tempo limite atingido ({configuracoes['timeout_segundos']}s)")
                processo_alvo.terminate()
                break

            mem = proc.memory_info().rss / 1024 / 1024
            cpu = proc.cpu_percent(interval=None)

            if configuracoes["monitorar_subprocessos"]:
                for filho in proc.children(recursive=True):
                    try:
                        mem += filho.memory_info().rss / 1024 / 1024
                        cpu += filho.cpu_percent(interval=None)
                    except psutil.NoSuchProcess:
                        pass

            medidas_ram.append(mem)
            medidas_cpu.append(cpu)

            if configuracoes["exportar_csv"]:
                dados_csv.append(f"{tempo_exec:.2f},{mem:.2f},{cpu:.1f}")

            if configuracoes["logs_ativos"]:
                media_ram = sum(medidas_ram) / len(medidas_ram)
                media_cpu = sum(medidas_cpu) / len(medidas_cpu)
                
                print(
                    f"  {Cores.CINZA}[{tempo_exec:7.2f}s]{Cores.RESET} "
                    f"{Cores.AMBER}RAM:{Cores.RESET} {mem:8.2f}MB {Cores.CINZA}({media_ram:8.2f}MB avg){Cores.RESET} | "
                    f"{Cores.VERDE_FOSFORO}CPU:{Cores.RESET} {cpu:6.1f}% {Cores.CINZA}({media_cpu:6.1f}% avg){Cores.RESET}"
                )

            time.sleep(configuracoes["intervalo_segundos"])

    except KeyboardInterrupt:
        print(f"\n  {Cores.AMARELO}[STOP]{Cores.RESET} Monitoramento interrompido pelo usuário")
        processo_alvo.terminate()

    fim = time.perf_counter()
    tempo_total = fim - inicio

    if medidas_ram:
        print()
        print(f"{Cores.VERDE_FOSFORO}  +-------------------------------------------------------------+{Cores.RESET}")
        print(f"{Cores.VERDE_FOSFORO}  |{Cores.RESET}  {Cores.VERDE_FOSFORO}{Cores.BOLD}RESULTADOS{Cores.RESET}                                                  {Cores.VERDE_FOSFORO}|{Cores.RESET}")
        print(f"{Cores.VERDE_FOSFORO}  +-------------------------------------------------------------+{Cores.RESET}")
        print()
        
        ram_media = sum(medidas_ram) / len(medidas_ram)
        ram_pico = max(medidas_ram)
        cpu_media = sum(medidas_cpu) / len(medidas_cpu)
        cpu_pico = max(medidas_cpu)
        
        # Exibe resultados em tabela
        headers = ["METRICA", "VALOR"]
        rows = [
            ["Tempo total", f"{tempo_total:.3f}s"],
            ["RAM media", f"{ram_media:.3f} MB"],
            ["Pico de RAM", f"{ram_pico:.3f} MB"],
            ["CPU media", f"{cpu_media:.2f}%"],
            ["Pico de CPU", f"{cpu_pico:.2f}%"]
        ]
        tabela(headers, rows, align="right")

        if configuracoes["exportar_csv"]:
            nome_csv = f"monitor_{arquivo.replace('.py', '')}_{int(time.time())}.csv"
            with open(nome_csv, "w") as f:
                f.write("tempo_segundos,ram_mb,cpu_percent\n")
                f.write("\n".join(dados_csv))
            print()
            box(f"Dados exportados: {nome_csv}", tipo="sucesso")

    print(f"\n  {Cores.CINZA}Processo finalizado.{Cores.RESET}")


def main():
    """Ponto de entrada do programa."""
    # Verifica argumentos da linha de comando
    args = sys.argv[1:]
    
    if "-h" in args or "--help" in args:
        mostrar_ajuda()
        return
    
    if "-c" in args or "--config" in args:
        limpar_tela()
        banner()
        menu_configuracoes()
        return
    
    # Verifica se há arquivo para executar diretamente
    arquivo_direto = None
    if "-f" in args:
        idx = args.index("-f")
        if idx + 1 < len(args):
            arquivo_direto = args[idx + 1]
    
    limpar_tela()
    banner()
    
    if arquivo_direto:
        executar_monitoramento(arquivo_direto)
    else:
        while True:
            menu_principal()
            opcao = input(f"\n  {Cores.AMBER}>>{Cores.RESET} ").strip()

            if opcao == "1":
                executar_monitoramento()
            elif opcao == "2":
                menu_configuracoes()
            elif opcao == "3":
                print(f"\n  {Cores.CINZA}Sistema encerrado. Ate logo!{Cores.RESET}\n")
                break
            else:
                print(f"  {Cores.LARANJA}[ERR]{Cores.RESET} Opção inválida")


if __name__ == "__main__":
    main()
