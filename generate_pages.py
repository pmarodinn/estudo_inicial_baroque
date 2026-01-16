import os

ASSETS_CONFIG = [
    { 'id': 'us_treasury_7_10', 'name': 'US Treasury Bond 7-10y (IEF)', 'path': '../dados/renda_fixa/US/us_treasury_bond_7_10y_IEF.csv' },
    { 'id': 'us_treasury_20', 'name': 'US Treasury Bond 20y (TLT)', 'path': '../dados/renda_fixa/US/us_treasury_bond_20y_TLT.csv' },
    { 'id': 'us_corp_inv', 'name': 'US Corp Bond Inv Grade (LQD)', 'path': '../dados/renda_fixa/US/us_corp_bond_inv_grade_LQD.csv' },
    { 'id': 'us_corp_high', 'name': 'US Corp Bond High Yield (HYG)', 'path': '../dados/renda_fixa/US/us_corp_bond_high_yield_HYG.csv' },
    { 'id': 'us_treasury_1_3', 'name': 'US Treasury Bond 1-3y (SHY)', 'path': '../dados/renda_fixa/US/us_treasury_bond_1_3y_SHY.csv' },
    { 'id': 'br_cri_inf', 'name': 'BR CRI Inflation Proxy (CPTS11)', 'path': '../dados/renda_fixa/BR/br_cri_inflation_proxy_CPTS11.csv' },
    { 'id': 'br_gov_fixed', 'name': 'BR Gov Fixed Rate (IRFM11)', 'path': '../dados/renda_fixa/BR/br_gov_fixed_rate_IRFM11.csv' },
    { 'id': 'br_deb_infra', 'name': 'BR Debêntures Infra (KDIF11)', 'path': '../dados/renda_fixa/BR/br_debentures_infra_KDIF11.csv' },
    { 'id': 'br_gov_inf', 'name': 'BR Gov Inflation (IMAB11)', 'path': '../dados/renda_fixa/BR/br_gov_inflation_IMAB11.csv' },
    { 'id': 'br_deb', 'name': 'BR Debêntures (DEBB11)', 'path': '../dados/renda_fixa/BR/br_debentures_DEBB11.csv' },
    { 'id': 'br_cri_proxy', 'name': 'BR CRI Proxy (KNCR11)', 'path': '../dados/renda_fixa/BR/br_cri_proxy_KNCR11.csv' },
    { 'id': 'selic', 'name': 'Selic Histórica', 'path': '../dados/renda_fixa/BR/selic_historica.csv' },
    { 'id': 'silver', 'name': 'Prata (Silver)', 'path': '../dados/metais/silver_prata.csv' },
    { 'id': 'gold', 'name': 'Ouro (Gold)', 'path': '../dados/metais/gold_ouro.csv' },
    { 'id': 'usdt', 'name': 'Stablecoin (USDT)', 'path': '../dados/ativos_nao_tradicionais/CRIPTO/stable_usdt.csv' },
    { 'id': 'art', 'name': 'Art Index (Artnet)', 'path': '../dados/ativos_nao_tradicionais/ARTE/art_index_artnet.csv' },
    { 'id': 'usd_brl', 'name': 'USD/BRL', 'path': '../dados/cotacao/usd_brl_currency.csv' },
    { 'id': 'eur_brl', 'name': 'EUR/BRL', 'path': '../dados/cotacao/eur_brl_currency.csv' },
    { 'id': 'sp500', 'name': 'US S&P 500 (SPY)', 'path': '../dados/renda_variavel/US/us_sp500_SPY.csv' },
    { 'id': 'ibovespa', 'name': 'BR Ibovespa (BOVA11)', 'path': '../dados/renda_variavel/BR/br_ibovespa_BOVA11.csv' }
]

TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Baroque - {name}</title>
    <link rel="stylesheet" href="../css/style.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.0/papaparse.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/hammer.js/2.0.8/hammer.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-zoom/2.0.1/chartjs-plugin-zoom.min.js"></script>
    <style>
        .chart-full-container {{
            height: 70vh;
            width: 100%;
            margin-top: 2rem;
            position: relative;
        }}
        #chart {{
            width: 100%;
            height: 100%;
        }}
        .header-controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        .back-link {{
            font-size: 0.9rem;
            color: var(--secondary-color);
        }}
        .back-link:hover {{
            color: var(--primary-color);
        }}
        .loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: var(--primary-color);
        }}
        .asset-title {{
            font-size: 2rem;
            font-family: var(--font-title);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1 class="brand-title"><a href="../index.html">BAROQUE</a></h1>
            <nav>
                <ul>
                    <li><a href="../index.html">Home</a></li>
                    <li><a href="assets.html" class="active">Cotações</a></li>
                </ul>
            </nav>
        </header>

        <main>
            <div class="header-controls">
                <a href="assets.html" class="back-link">&larr; Voltar para Lista</a>
                <h2 id="asset-name" class="asset-title">{name}</h2>
            </div>
            
            <div class="chart-full-container">
                <div id="chart"></div>
                <div id="loading-msg" class="loading">Carregando dados...</div>
            </div>
        </main>

        <footer>
            <p>&copy; 2026 Baroque Inc. Todos os direitos reservados.</p>
        </footer>
    </div>
    <script>
        // Inject configuration specific to this asset
        const CURRENT_ASSET_CONFIG = {{
            name: "{name}",
            path: "{path}"
        }};
    </script>
    <script src="../js/render_chart.js"></script>
</body>
</html>
"""

output_dir = "pages"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for asset in ASSETS_CONFIG:
    filename = f"{asset['id']}.html"
    filepath = os.path.join(output_dir, filename)
    
    content = TEMPLATE.format(
        name=asset['name'],
        path=asset['path']
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {filepath}")

print("All asset pages created successfully.")
