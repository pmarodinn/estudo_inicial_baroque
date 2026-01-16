import pandas as pd
import numpy as np
import yfinance as yf
import requests
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
from datetime import datetime, timedelta

# --- 1. DADOS ---

# A. Baixar Selic (Série 11) e tratar como ATIVO (LFT Simulada)
# A API do BCB exige data inicial e final para séries diárias (máximo 10 anos)
data_fim = datetime.now().strftime('%d/%m/%Y')
data_inicio = (datetime.now() - timedelta(days=10*365)).strftime('%d/%m/%Y')
url_selic = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&dataInicial={data_inicio}&dataFinal={data_fim}'
headers = {'User-Agent': 'Mozilla/5.0'}

print("Carregando dados...")
try:
    # Usar a nova planilha selic_historica.csv
    selic_raw = pd.read_csv('selic_historica.csv')
    selic_raw.rename(columns={'date': 'data', 'selic_meta_aa': 'valor'}, inplace=True)
    selic_raw['data'] = pd.to_datetime(selic_raw['data'])
    
    # Converter taxa anual para diária (ex: 13.25 -> 0.1325 anual -> taxa diária)
    # A fórmula simplificada para taxa média diária a partir da anual é ((1 + i_a)^(1/252) - 1)
    selic_raw['valor'] = (1 + selic_raw['valor'] / 100)**(1/252) - 1
    
    selic_raw.set_index('data', inplace=True)
    
    # Criar o índice acumulado (Preço teórico da LFT)
    lft_simulada = (1 + selic_raw['valor']).cumprod()
    lft_simulada.name = 'LFT'
    
    # Taxa livre de risco referência (último valor anualizado disponível)
    risk_free_rate_ref = selic_raw['valor'].mean() * 252
except Exception as e:
    print(f"Erro ao carregar selic_historica.csv: {e}")
    exit()

# B. Baixar Ativos de Risco
tickers_risco = ['IMAB11.SA', 'BOVA11.SA', 'IVVB11.SA']
data_download = yf.download(tickers_risco, start='2020-01-01', progress=False)

if 'Adj Close' in data_download.columns.levels[0]:
    df_risco = data_download['Adj Close']
else:
    df_risco = data_download['Close']

# C. Unificar Tudo em um DataFrame Único
# Alinhar as datas (inner join) para garantir covariância justa
df_total = df_risco.join(lft_simulada, how='inner').dropna()

tickers = list(df_total.columns) # Agora inclui 'LFT' na lista!

print(f"Ativos considerados na Fronteira: {tickers}")

# --- 2. CÁLCULOS ESTATÍSTICOS ---

# Configuração Visual: Estilo Claro com Fonte Maharlika (Carregada do folder local)
fonts_path = '/home/usuario/Downloads/Documentos/baroque/markowitz/fonts/Maharlika-Regular.ttf'
try:
    # Registra a fonte no Matplotlib
    fm.fontManager.addfont(fonts_path)
    prop = fm.FontProperties(fname=fonts_path)
    plt.rcParams['font.family'] = prop.get_name()
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['axes.labelweight'] = 'bold'
    print(f"Fonte '{prop.get_name()}' carregada com sucesso!")
except Exception as e:
    print(f"Aviso: Não foi possível carregar a fonte '{fonts_path}': {e}")
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.weight'] = 'bold'

TV_BG = '#ffffff'
TV_GRID = '#f0f3fa'
TV_TEXT = '#131722'
TV_GREEN = "#37637E"
TV_RED = '#f23645'
TV_BLUE = "#013685"
TV_YELLOW = '#fbc02d'
TV_PURPLE = '#6a1b9a' # Roxo forte para LFT

def apply_tv_style(ax, title="", show_grid=True):
    ax.set_facecolor(TV_BG)
    if show_grid:
        ax.grid(True, color=TV_GRID, linestyle='-', linewidth=0.5, zorder=0)
        ax.set_axisbelow(True) # Garante que o grid fique ATRÁS dos dados
    else:
        ax.grid(False)
    
    ax.set_title(title, fontsize=18, fontweight='bold', pad=20, color=TV_TEXT)
    ax.tick_params(colors=TV_TEXT, labelsize=12)
    
    # Garantir labels e ticks em negrito
    ax.xaxis.label.set_size(14)
    ax.xaxis.label.set_fontweight('bold')
    ax.yaxis.label.set_size(14)
    ax.yaxis.label.set_fontweight('bold')
    
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')

    for spine in ax.spines.values():
        spine.set_color('#d1d4dc')

def add_watermark(fig):
    # Adiciona "B." em negrito no canto inferior direito de cada imagem
    fig.text(0.99, 0.01, 'B.', fontsize=24, fontweight='bold', 
             color='black', ha='right', va='bottom', alpha=1.0)

# Retornos Logarítmicos
retornos = np.log(df_total / df_total.shift(1)).dropna()
cov_matrix = retornos.cov() * 252
ret_mean = retornos.mean() * 252

# --- 3. OTIMIZAÇÃO (Markowitz Padrão com todos os ativos) ---

def get_stats(weights):
    weights = np.array(weights)
    ret = np.sum(ret_mean * weights)
    vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    # Sharpe Ratio (usando a média da Selic como benchmark fixo)
    sr = (ret - risk_free_rate_ref) / vol if vol > 0 else 0
    return np.array([ret, vol, sr])

# Funções Objetivo
def min_volatility(weights):
    return get_stats(weights)[1]

def neg_sharpe(weights):
    return -get_stats(weights)[2]

def target_vol_constraint(weights, target):
    return get_stats(weights)[1] - target

# Configuração da Otimização
num_assets = len(tickers)
args = ()
bounds = tuple((0, 1) for _ in range(num_assets))
constraints_sum = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
init_guess = num_assets * [1. / num_assets,]

# A. Carteira de Mínima Volatilidade Global
opt_min_vol = minimize(min_volatility, init_guess, method='SLSQP', bounds=bounds, constraints=constraints_sum)
w_min_vol = opt_min_vol.x
ret_min, vol_min, sr_min = get_stats(w_min_vol)

# B. Carteira de Máximo Sharpe
opt_max_sharpe = minimize(neg_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=constraints_sum)
w_max_sharpe = opt_max_sharpe.x
ret_sharpe, vol_sharpe, sr_sharpe = get_stats(w_max_sharpe)

# C. Carteira (Alvo de Volatilidade Específico na Curva)
# Ao invés de usar a reta CML, buscamos o ponto na FRONTEIRA com Vol = 5%
target_vol_baroque = 0.05
constraints_baroque = (
    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
    {'type': 'eq', 'fun': lambda x: get_stats(x)[1] - target_vol_baroque}
)

# Tentamos maximizar o retorno dado o risco de 5%
def neg_return(weights):
    return -get_stats(weights)[0]

try:
    opt_baroque = minimize(neg_return, init_guess, method='SLSQP', bounds=bounds, constraints=constraints_baroque)
    if not opt_baroque.success:
        raise ValueError("Não convergiu")
    w_baroque = opt_baroque.x
    ret_baroque, vol_baroque, sr_baroque = get_stats(w_baroque)
    baroque_success = True
except:
    print(f"Aviso: Não foi possível encontrar uma carteira na fronteira com exatos {target_vol_baroque*100}% de volatilidade.")
    print("Isso pode acontecer se a volatilidade mínima da carteira (com LFT) for maior que 5%.")
    print(f"Volatilidade Mínima Possível: {vol_min*100:.2f}%")
    # Fallback: Usa a mínima volatilidade como Carteira se o alvo for inatingível
    w_baroque = w_min_vol
    ret_baroque, vol_baroque, sr_baroque = ret_min, vol_min, sr_min
    baroque_success = False

# D. Cálculo do Contorno da Fronteira Eficiente (Matemático)
# Definimos um range de retornos do mínimo global até o ativo de maior retorno
target_rets = np.linspace(ret_min, max(ret_mean), 50)
vols_front = []
pesos_front = []

for r_target in target_rets:
    # Restrição: Pesos somam 1 E retorno esperado = r_target
    constraints_ef = (
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
        {'type': 'eq', 'fun': lambda x: np.sum(ret_mean * x) - r_target}
    )
    # Busca inteligente: Minimizamos a volatilidade para o retorno alvo
    res = minimize(min_volatility, init_guess, method='SLSQP', bounds=bounds, constraints=constraints_ef)
    if res.success:
        vols_front.append(res.fun)
        pesos_front.append(res.x)
    else:
        vols_front.append(None)
        pesos_front.append(np.zeros(num_assets))

vols_front = np.array(vols_front)
pesos_front = np.array(pesos_front)


# --- 4. EXIBIÇÃO ---

print("\n" + "="*50)
print("MATRIZ DE COVARIANCIA ANUALIZADA")
print("="*50)
print(cov_matrix)

# Visualização da Matriz de Covariância
fig, ax = plt.subplots(figsize=(10, 8), facecolor=TV_BG)
sns.heatmap(cov_matrix, annot=True, cmap='Blues', fmt=".6f", ax=ax, 
            cbar_kws={'label': 'Covariância'}, annot_kws={"size": 12, "color": TV_TEXT, "fontweight": "bold"})
apply_tv_style(ax, 'Matriz de Covariância Anualizada (Incluindo LFT)', show_grid=False)
add_watermark(fig)
plt.savefig('selic volatil/matriz_covariancia_lft.png', facecolor=TV_BG, bbox_inches='tight')
print("\nMapa de calor da covariância salvo como 'selic volatil/matriz_covariancia_lft.png'")

# MATRIZ DE CORRELAÇÃO
print("\n" + "="*50)
print("MATRIZ DE CORRELAÇÃO")
print("="*50)
correl_matrix = retornos.corr()
print(correl_matrix)

# Visualização da Matriz de Correlação
fig, ax = plt.subplots(figsize=(10, 8), facecolor=TV_BG)
sns.heatmap(correl_matrix, annot=True, cmap='RdYlGn', center=0, fmt=".4f", ax=ax,
            cbar_kws={'label': 'Correlação'}, annot_kws={"size": 12, "color": TV_TEXT, "fontweight": "bold"})
apply_tv_style(ax, 'Matriz de Correlação (Incluindo LFT)', show_grid=False)
add_watermark(fig)
plt.savefig('selic volatil/matriz_correlacao_lft.png', facecolor=TV_BG, bbox_inches='tight')
print("\nMapa de calor da correlação salvo como 'selic volatil/matriz_correlacao_lft.png'")

# --- 6. VISUALIZAÇÃO DE PROPORÇÕES (COMPOSIÇÃO DO PORTFÓLIO) ---

fig, ax = plt.subplots(figsize=(12, 7), facecolor=TV_BG)

# Já temos pesos_front calculado na seção de otimização
idx_lft = tickers.index('LFT')
peso_lft = pesos_front[:, idx_lft]
peso_risco = np.sum(pesos_front[:, [i for i in range(num_assets) if i != idx_lft]], axis=1)

# X-axis: Retorno Anual Esperado (%)
returns_pct = target_rets * 100

ax.stackplot(returns_pct, peso_lft * 100, peso_risco * 100, 
              labels=['% LFT', '% Ativos de Risco'], 
              colors=[TV_PURPLE, TV_RED], alpha=0.6)

apply_tv_style(ax, 'Proporção de Alocação vs. Retorno Esperado')
ax.set_xlabel('Retorno Anual Esperado (%)', color=TV_TEXT)
ax.set_ylabel('Proporção da Carteira (%)', color=TV_TEXT)

# Adicionar uma linha vertical para marcar o ponto de Risco = 5%
ret_risco_5 = ret_baroque * 100
ax.axvline(x=ret_risco_5, color=TV_BLUE, linestyle='--', linewidth=2, label=f'Risco 5% (Retorno: {ret_risco_5:.2f}%)')
ax.legend(loc='upper right', facecolor=TV_BG, edgecolor='#d1d4dc', labelcolor=TV_TEXT, fontsize=12)

add_watermark(fig)
plt.savefig('selic volatil/proporcao_alocacao_retorno.png', facecolor=TV_BG, bbox_inches='tight')
print("\nGráfico de proporções salvo como 'selic volatil/proporcao_alocacao_retorno.png'")

print("\n" + "="*50)
print("RESULTADOS (CONSIDERANDO LFT COMO ATIVO VOLÁTIL)")
print("="*50)

def print_portfolio(name, weights, ret, vol, sr):
    print(f"\n>>> {name}")
    for i, ticker in enumerate(tickers):
        print(f"{ticker}: {weights[i]*100:.2f}%")
    print(f"Retorno Esperado: {ret*100:.2f}%")
    print(f"Volatilidade: {vol*100:.2f}%")
    print(f"Sharpe Ratio: {sr:.2f}")

print_portfolio("Carteira Mínima Volatilidade Global", w_min_vol, ret_min, vol_min, sr_min)
print_portfolio("Carteira Máximo Sharpe", w_max_sharpe, ret_sharpe, vol_sharpe, sr_sharpe)
label_baroque = f"Carteira (Target Vol {target_vol_baroque*100}%)" if baroque_success else "Carteira (Fallback: Mín Vol)"
print_portfolio(label_baroque, w_baroque, ret_baroque, vol_baroque, sr_baroque)


# --- 5. GRÁFICO DA FRONTEIRA EFICIENTE ---

# Simulação de Monte Carlo para visualizar a "nuvem"
np.random.seed(42)
sim_rets, sim_vols, sim_srs = [], [], []
for _ in range(30000): # 30.000 casos
    w = np.random.random(num_assets)
    w /= np.sum(w)
    r, v, s = get_stats(w)
    sim_rets.append(r)
    sim_vols.append(v)
    sim_srs.append(s)

fig, ax = plt.subplots(figsize=(12, 8), facecolor=TV_BG)

# B. Plotagem
scatter = ax.scatter(sim_vols, sim_rets, c=sim_srs, cmap='viridis', s=8, alpha=0.2, label='Portfólios Aleatórios')
cbar = fig.colorbar(scatter, ax=ax)
cbar.set_label('Sharpe Ratio', color=TV_TEXT, fontweight='bold')
cbar.ax.yaxis.set_tick_params(color=TV_TEXT)
# Tick labels da colorbar em negrito
for label in cbar.ax.get_yticklabels():
    label.set_fontweight('bold')
plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=TV_TEXT)

# Plotar o Contorno Matematico (Linha da Fronteira)
valid_idx = [i for i, v in enumerate(vols_front) if v is not None]
ax.plot([vols_front[i] for i in valid_idx], [target_rets[i] for i in valid_idx], 
         color=TV_TEXT, linestyle='-', linewidth=2.5, label='Fronteira Eficiente')

# Plotar os Pontos Ótimos
ax.scatter(vol_min, ret_min, color=TV_BLUE, s=150, marker='o', label='Mínima Volatilidade', edgecolors=TV_TEXT, zorder=5)
ax.scatter(vol_sharpe, ret_sharpe, color=TV_YELLOW, s=200, marker='*', label='Máximo Sharpe', edgecolors=TV_TEXT, zorder=5)
ax.scatter(vol_baroque, ret_baroque, color=TV_RED, s=150, marker='D', label='Carteira (Meta Vol)', edgecolors=TV_TEXT, zorder=5)

apply_tv_style(ax, 'Fronteira Eficiente (LFT incluída na Otimização)')
ax.set_xlabel('Volatilidade Anual (Risco)', color=TV_TEXT)
ax.set_ylabel('Retorno Esperado Anual', color=TV_TEXT)
ax.legend(loc='upper right', facecolor=TV_BG, edgecolor='#d1d4dc', labelcolor=TV_TEXT, fontsize=12)

add_watermark(fig)
plt.savefig('selic volatil/fronteira_com_oscilacao.png', facecolor=TV_BG, bbox_inches='tight')
print(f"\nGráfico da Fronteira salvo como 'selic volatil/fronteira_com_oscilacao.png'")

# --- 7. GRÁFICO COMBINADO DE VOLATILIDADE (INDIVIDUAL E TEMPORAL) ---

vols_individuais = np.sqrt(np.diag(cov_matrix))
vol_acumulada = retornos.expanding().std() * np.sqrt(252)

# Cálculo da evolução da volatilidade da Carteira
ret_baroque_diario = (retornos * w_baroque).sum(axis=1)
vol_baroque_acumulada = ret_baroque_diario.expanding().std() * np.sqrt(252)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8), facecolor=TV_BG)

# Subplot 1: Volatilidade Individual (Barras)
# Identificar o índice da LFT para colocar a cor roxa
bar_colors = []
for ticker in tickers:
    if ticker == 'LFT':
        bar_colors.append(TV_PURPLE)
    elif ticker == 'BOVA11.SA':
        bar_colors.append(TV_BLUE)
    elif ticker == 'IMAB11.SA':
        bar_colors.append(TV_YELLOW)
    else:
        bar_colors.append(TV_RED)

ax1.bar(tickers, vols_individuais * 100, color=bar_colors, alpha=0.7, edgecolor=TV_TEXT)
apply_tv_style(ax1, 'Volatilidade Individual (Anualizada %)')
ax1.set_ylabel('Volatilidade (%)', color=TV_TEXT)
ax1.set_xlabel('Ativos', color=TV_TEXT)

for i, v in enumerate(vols_individuais):
    ax1.text(i, (v * 100) + 0.2, f"{v*100:.2f}%", ha='center', fontweight='bold', color=TV_TEXT, fontsize=12)

# Subplot 2: Evolução Temporal
for i, ticker in enumerate(tickers):
    ax2.plot(vol_acumulada.index, vol_acumulada[ticker] * 100, label=ticker, linewidth=1.5, color=bar_colors[i], alpha=0.6)

# Plotar a Carteira com destaque (Linha preta grossa)
ax2.plot(vol_baroque_acumulada.index, vol_baroque_acumulada * 100, 
         label='CARTEIRA', linewidth=4, color='#131722', linestyle='-', zorder=10)

apply_tv_style(ax2, 'Evolução da Volatilidade Histórica (Anualizada %)')
ax2.set_ylabel('Volatilidade Acumulada (%)', color=TV_TEXT)
ax2.set_xlabel('Ano', color=TV_TEXT)
ax2.legend(facecolor=TV_BG, edgecolor='#d1d4dc', labelcolor=TV_TEXT, fontsize=11, loc='upper right')

plt.tight_layout()
add_watermark(fig)
plt.savefig('selic volatil/analise_volatilidade_completa.png', facecolor=TV_BG, bbox_inches='tight')
print("\nAnálise completa de volatilidade salva como 'selic volatil/analise_volatilidade_completa.png'")

# --- 8. GRÁFICO DE EVOLUÇÃO DO RETORNO ACUMULADO (BASE R$ 100) ---

# Normalizar ativos para base R$ 100 no início do período
ret_acum_ativos = np.exp(retornos.cumsum()) * 100
ret_acum_carteira = np.exp(ret_baroque_diario.cumsum()) * 100

fig, ax = plt.subplots(figsize=(14, 8), facecolor=TV_BG)

# Plotar Ativos
for i, ticker in enumerate(tickers):
    ax.plot(ret_acum_ativos.index, ret_acum_ativos[ticker], label=ticker, linewidth=2, color=bar_colors[i], alpha=0.7)

# Plotar Carteira (Destaque em Preto)
ax.plot(ret_acum_carteira.index, ret_acum_carteira, label='CARTEIRA', linewidth=4, color='#131722', linestyle='-', zorder=10)

apply_tv_style(ax, 'Simulação de Investimento: Evolução de R$ 100,00')
ax.set_ylabel('Valor Acumulado (R$)', color=TV_TEXT)
ax.set_xlabel('Ano', color=TV_TEXT)
ax.legend(facecolor=TV_BG, edgecolor='#d1d4dc', labelcolor=TV_TEXT, fontsize=12, loc='upper right')

plt.tight_layout()
add_watermark(fig)
plt.savefig('selic volatil/evolucao_retorno_acumulado.png', facecolor=TV_BG, bbox_inches='tight')
print("\nGráfico de evolução do retorno (R$ 100) salvo como 'selic volatil/evolucao_retorno_acumulado.png'")

print(f"\nGráficos salvos na pasta 'selic volatil/':")
print("- selic volatil/matriz_covariancia_lft.png")
print("- selic volatil/matriz_correlacao_lft.png")
print("- selic volatil/fronteira_com_oscilacao.png")
print("- selic volatil/analise_volatilidade_completa.png")
print("- selic volatil/evolucao_retorno_acumulado.png")
