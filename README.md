# Monitor de Performance Python

Um profiler de performance para scripts Python que monitora em tempo real o uso de recursos do sistema.

## Índice

- [Sobre](#sobre)
- [Funcionalidades](#funcionalidades)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Configurações](#configurações)
- [Métricas Monitoradas](#métricas-monitoradas)
- [Exemplo de Uso](#exemplo-de-uso)
- [Estrutura do CSV Exportado](#estrutura-do-csv-exportado)
- [Tecnologias](#tecnologias)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Sobre

O **Monitor de Performance Python** é uma ferramenta de profiling que permite analisar o desempenho de scripts Python durante sua execução. Ele coleta métricas em tempo real sobre consumo de memória RAM, uso de CPU e tempo de execução, apresentando estatísticas detalhadas ao final do processo.

Ideal para:
- Identificar vazamentos de memória
- Otimizar uso de recursos
- Comparar performance entre diferentes implementações
- Documentar benchmarks de scripts

## Funcionalidades

- **Monitoramento em Tempo Real**: Acompanhamento contínuo de RAM e CPU
- **Menu Interativo**: Interface simples com navegação por números
- **Configurações Ajustáveis**:
  - Ativar/desativar logs em tempo real
  - Ajustar intervalo entre medições
  - Definir timeout máximo de execução
  - Monitoramento de subprocessos (threads/processos filhos)
  - Exportação automática para CSV
- **Exportação CSV**: Salva todas as métricas para análise posterior
- **Foco no Processo Alvo**: Monitora apenas o script especificado
- **Interrupção Segura**: Encerramento limpo com Ctrl+C

## Instalação

### Pré-requisitos

- Python 3.7 ou superior
- Biblioteca `psutil`

### Passo a Passo

1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/monitor-performance-python.git
cd monitor-performance-python
```

2. **Instale as dependências:**
```bash
pip install psutil
```

3. **Execute o monitor:**
```bash
python monitor.py
```

## Como Usar

### Menu Principal

Ao executar o programa, você verá o menu principal:

```
==================================================
MONITOR DE PERFORMANCE PYTHON
==================================================
1. Executar script
2. Configurações
3. Sair
==================================================
```

### Opção 1: Executar Script

1. Escolha a opção **1**
2. Digite o nome do arquivo Python que deseja monitorar (ex: `teste.py`)
3. O monitor iniciará automaticamente

### Opção 2: Configurações

Acesse as configurações antes de executar para personalizar o monitoramento:

```
==================================================
CONFIGURAÇÕES
==================================================
1. Logs em tempo real: [ATIVADO]
2. Intervalo de atualização: [1.0s]
3. Timeout: [Desativado]
4. Monitorar subprocessos: [DESATIVADO]
5. Exportar CSV: [DESATIVADO]
6. Voltar ao menu principal
==================================================
```

## Configurações

| Configuração | Descrição | Padrão |
|-------------|-----------|---------|
| **Logs em tempo real** | Exibe métricas a cada intervalo no terminal | Ativado |
| **Intervalo de atualização** | Tempo entre medições (em segundos) | 1.0s |
| **Timeout** | Tempo máximo de execução (None = ilimitado) | Desativado |
| **Monitorar subprocessos** | Inclui processos filhos na contagem | Desativado |
| **Exportar CSV** | Salva dados em arquivo CSV | Desativado |

### Dicas de Configuração

- **Intervalos menores** (0.1s - 0.5s): Melhor precisão, mais dados
- **Intervalos maiores** (2s - 5s): Menor overhead, menos precisão
- **Timeout**: Útil para scripts com risco de loop infinito
- **Subprocessos**: Ative quando o script usa multiprocessing/threading

## Métricas Monitoradas

Durante a execução, o monitor coleta:

### Em Tempo Real (se logs ativados)
- RAM atual (MB)
- Média de RAM (MB)
- CPU atual (%)
- Média de CPU (%)
- Tempo de execução (s)

### Resultado Final
- **Tempo total**: Duração total da execução
- **RAM média**: Consumo médio de memória
- **Pico de RAM**: Maior consumo registrado
- **CPU média**: Uso médio de processamento
- **Pico de CPU**: Maior uso registrado

## Exemplo de Uso

### Script de Teste (testeRAM.py)

```python
import time

dados = []

print("Script alvo iniciado...")

i = 0
while i < 20:
    # Consome ~30 MB por ciclo
    dados.append(bytearray(30 * 1024 * 1024))
    
    # Trabalho de CPU
    soma = sum(range(1_000_000))
    
    i += 1
    print(f"Ciclo {i} | memória alocada ~{i * 30} MB")
    
    time.sleep(0.02)
```

### Execução

```bash
$ python monitor.py

 ______                            ___  ___     _        _          
| ___ \                           |  \/  |    | |      (_)         
| |_/ / __ ___   ___ ___  ___ ___ | .  . | ___| |_ _ __ _  ___ ___ 
|  __/ '__/ _ \ / __/ _ \/ __/ __|| |\/| |/ _ \ __| '__| |/ __/ __|
| |  | | | (_) | (_|  __/\__ \__ \| |  | |  __/ |_| |  | | (__\__ \
\_|  |_|  \___/ \___\___||___/___/\_|  |_/\___|\__|_|  |_|\___|___/


==================================================
MONITOR DE PERFORMANCE PYTHON
==================================================
1. Executar script
2. Configurações
3. Sair
==================================================
Escolha uma opção: 1

==================================================
EXECUTAR SCRIPT
==================================================
Nome do arquivo Python (ex: teste.py): testeRAM.py

Executando testeRAM.py (PID 12345)...
Monitorando RAM, CPU e tempo...

[MONITOR] RAM: 30.45 MB | Média RAM: 30.45 MB | CPU: 45.2% | Média CPU: 45.2% | Tempo: 1.05s
[MONITOR] RAM: 60.89 MB | Média RAM: 45.67 MB | CPU: 42.8% | Média CPU: 44.0% | Tempo: 2.05s
...

==================================================
RESULTADO FINAL
==================================================
Tempo total: 21.34234s
RAM média: 315.23456 MB
Pico de RAM: 600.12345 MB
CPU média: 38.45%
Pico de CPU: 98.20%
Processo finalizado.
```

## Estrutura do CSV Exportado

Quando a exportação CSV está ativada, o arquivo gerado segue o formato:

```csv
tempo_segundos,ram_mb,cpu_percent
1.05,30.45,45.2
2.05,60.89,42.8
3.05,91.34,41.5
...
```

O nome do arquivo segue o padrão: `monitor_[nome_script]_[timestamp].csv`

## Tecnologias

- **Python 3.7+**: Linguagem principal
- **psutil**: Biblioteca para acesso a informações de processos e sistema
- **subprocess**: Módulo nativo para criação de processos
- **time**: Módulo nativo para medição de tempo

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### Ideias para Contribuição

- [ ] Gráficos em tempo real (matplotlib/plotly)
- [ ] Interface gráfica (Tkinter/PyQt)
- [ ] Suporte a múltiplos processos simultâneos
- [ ] Análise comparativa entre execuções
- [ ] Relatórios em PDF
- [ ] Docker container para execução isolada

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Autor

**Seu Nome** - [@felipemenezes937](https://github.com/FelipeMenezes937)

## Agradecimentos

- [psutil](https://github.com/giampaolo/psutil) - Biblioteca essencial para coleta de métricas
- Comunidade Python - Pelo ecossistema incrível

---

Feito para a comunidade Python
