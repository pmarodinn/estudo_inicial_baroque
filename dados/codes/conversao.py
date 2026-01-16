
import pandas as pd
import os

# Caminhos
base_path = "/home/usuario/Downloads/Documentos/baroque/markowitz/dados"

# Currency Files
currencies = {
    "USD": os.path.join(base_path, "cotacao/usd_brl_currency.csv"),
    "EUR": os.path.join(base_path, "cotacao/eur_brl_currency.csv")
}

# Configuration: Which folder uses which currency
conversion_tasks = [
    {"folder": os.path.join(base_path, "renda_fixa/US"), "currency": "USD"},
    {"folder": os.path.join(base_path, "renda_variavel/US"), "currency": "USD"},
    {"folder": os.path.join(base_path, "metais"), "currency": "USD"},
    {"folder": os.path.join(base_path, "ativos_nao_tradicionais/CRIPTO"), "currency": "USD"},
    {"folder": os.path.join(base_path, "ativos_nao_tradicionais/ARTE"), "currency": "EUR"},
]

def load_currency(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo de cotação não encontrado: {path}")
    
    # Load currency
    # Assumes Date is index (col 0) and the rate is the first data column
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    # Return the series
    return df.iloc[:, 0]

def convert_and_save():
    print("Iniciando conversão para BRL...")
    
    # Pre-load currencies
    loaded_currencies = {}
    for code, path in currencies.items():
        try:
            loaded_currencies[code] = load_currency(path)
            print(f"Cotação {code} carregada de: {path}")
        except Exception as e:
            print(f"Erro ao carregar cotação {code}: {e}")

    for task in conversion_tasks:
        folder = task["folder"]
        curr_code = task["currency"]
        
        if curr_code not in loaded_currencies:
            print(f"[SKIP] Cotação {curr_code} não disponível para pasta {folder}")
            continue

        currency_series = loaded_currencies[curr_code]

        if not os.path.exists(folder):
            print(f"Pasta não encontrada: {folder}")
            continue
            
        print(f"Processando pasta: {folder} ({curr_code} -> BRL)")
        files = os.listdir(folder)
        
        for file in files:
            if not file.endswith(".csv"):
                continue
            
            # Skip currency files if they happen to be there
            if "currency" in file:
                continue
                
            file_path = os.path.join(folder, file)
            print(f"  Convertendo {file}...", end=" ")
            
            try:
                # Read Asset
                df_asset = pd.read_csv(file_path, index_col=0, parse_dates=True)
                if df_asset.empty:
                    print("Vazio (ignorado).")
                    continue
                
                # Align dates (Join)
                # We want asset prices in BRL.
                # Price_BRL = Price_Origin * Rate_Origin_BRL
                
                # Access the first column of the asset
                asset_col_name = df_asset.columns[0]
                asset_series = df_asset.iloc[:, 0]
                
                # Join
                combined = pd.concat([asset_series, currency_series], axis=1, join='inner')
                combined.columns = ['Asset_Origin', 'Rate']
                
                # Calc
                combined['Asset_BRL'] = combined['Asset_Origin'] * combined['Rate']
                
                # Create result dataframe to save (keep original structure)
                df_result = combined[['Asset_BRL']]
                df_result.columns = [asset_col_name] 
                
                # Save
                df_result.to_csv(file_path)
                print("OK.")
                
            except Exception as e:
                print(f"ERRO: {e}")

    print("Conversão concluída.")

if __name__ == "__main__":
    convert_and_save()
