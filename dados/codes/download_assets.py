
import yfinance as yf
import pandas as pd
import os

# Define output directories
base_path = "/home/usuario/Downloads/Documentos/baroque/markowitz/dados"
us_fixed_path = os.path.join(base_path, "renda_fixa/US")
br_fixed_path = os.path.join(base_path, "renda_fixa/BR")
us_var_path = os.path.join(base_path, "renda_variavel/US")
br_var_path = os.path.join(base_path, "renda_variavel/BR")
metais_path = os.path.join(base_path, "metais")
ant_path = os.path.join(base_path, "ativos_nao_tradicionais")
art_path = os.path.join(ant_path, "ARTE")
cripto_path = os.path.join(ant_path, "CRIPTO")
cotacao_path = os.path.join(base_path, "cotacao")

# Create directories if they don't exist
os.makedirs(us_fixed_path, exist_ok=True)
os.makedirs(br_fixed_path, exist_ok=True)
os.makedirs(us_var_path, exist_ok=True)
os.makedirs(br_var_path, exist_ok=True)
os.makedirs(metais_path, exist_ok=True)
os.makedirs(ant_path, exist_ok=True)
os.makedirs(art_path, exist_ok=True)
os.makedirs(cripto_path, exist_ok=True)
os.makedirs(cotacao_path, exist_ok=True)

# Define assets to download
# (Key: Filename, Value: Ticker)
assets = {
    # 1. US Govt Bonds
    "us_treasury_bond_20y_TLT": "TLT",
    "us_treasury_bond_7_10y_IEF": "IEF",
    "us_treasury_bond_1_3y_SHY": "SHY",
    
    # 2. US Corporate Bonds (Private Credit)
    "us_corp_bond_inv_grade_LQD": "LQD",
    "us_corp_bond_high_yield_HYG": "HYG",
    
    # 3. Currency
    "usd_brl_currency": "BRL=X",
    "eur_brl_currency": "EURBRL=X",
    
    # 4. BR Govt Bonds (Proxies via ETF)
    "br_gov_inflation_IMAB11": "IMAB11.SA",
    "br_gov_fixed_rate_IRFM11": "IRFM11.SA",
    
    # 5. BR Private Credit - Debentures
    # DEBB11 is generic debetures, KDIF11 is infrastructure
    "br_debentures_DEBB11": "DEBB11.SA",
    "br_debentures_infra_KDIF11": "KDIF11.SA",
    
    # 6. BR Private Credit - CRI/CRA 
    # Using KNCR11 (Kinea Rendimentos Imobiliarios - mostly CDI) as a proxy for high grade private credit in Real Estate
    "br_cri_proxy_KNCR11": "KNCR11.SA",
    "br_cri_inflation_proxy_CPTS11": "CPTS11.SA",

    # 7. Metais
    "gold_ouro": "GC=F",
    "silver_prata": "SI=F",

    # 8. Stable coins
    "stable_usdt": "USDT-USD",

    # 9. Equity ETFs
    "us_sp500_SPY": "SPY",
    "br_ibovespa_BOVA11": "BOVA11.SA",

    # 10. Art Market Proxy (Artnet AG - Francfurt)
    # Using 'AYD.F' as a proxy for the Art Market industry
    "art_index_artnet": "AYD.F"
}

print("Iniciando downloads...")

for name, ticker in assets.items():
    # Determine Folder
    if "us_treasury" in name or "us_corp" in name:
        folder = us_fixed_path
    elif "br_gov" in name or "br_debentures" in name or "br_cri" in name:
        folder = br_fixed_path
    elif "usd_brl" in name or "eur_brl" in name:
        folder = cotacao_path
    elif "us_sp500" in name:
        folder = us_var_path
    elif "br_ibovespa" in name:
        folder = br_var_path
    elif "gold" in name or "silver" in name:
        folder = metais_path
    elif "stable" in name:
        folder = cripto_path
    elif "art_index" in name:
        folder = art_path
    else:
        folder = base_path

    file_path = os.path.join(folder, f"{name}.csv")

    if os.path.exists(file_path):
        print(f"Pilhando {ticker} -> {name} (Arquivo já existe em {file_path})")
        continue

    print(f"Baixando {ticker} -> {name}...")
    try:
        # Download max history
        data = yf.download(ticker, period="max", progress=False)
        
        if data.empty:
            print(f"  [AVISO] Sem dados para {ticker}.")
            continue
            
        # Clean up columns (Handle MultiIndex)
        # yfinance often returns columns like ('Adj Close', 'TLT')
        if isinstance(data.columns, pd.MultiIndex):
            # Prefer Adj Close, fallback to Close
            if 'Adj Close' in data.columns.get_level_values(0):
                series = data['Adj Close'][ticker]
            elif 'Close' in data.columns.get_level_values(0):
                series = data['Close'][ticker]
            else:
                # Fallback: take the first column
                series = data.iloc[:, 0]
        else:
            if 'Adj Close' in data.columns:
                series = data['Adj Close']
            elif 'Close' in data.columns:
                series = data['Close']
            else:
                series = data.iloc[:, 0]
        
        # Save to CSV
        series.to_csv(file_path)
        print(f"  Salvo em: {file_path}")
        
    except Exception as e:
        print(f"  [ERRO] Falha ao baixar {ticker}: {e}")

print("Concluído.")
