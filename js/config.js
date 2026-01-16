const ASSETS_CONFIG = [
    // EUA - Renda Fixa
    { id: 'us_treasury_7_10', name: 'US Treasury Bond 7-10y (IEF)', path: '../dados/renda_fixa/US/us_treasury_bond_7_10y_IEF.csv', region: 'EUA', category: 'Renda Fixa' },
    { id: 'us_treasury_20', name: 'US Treasury Bond 20y (TLT)', path: '../dados/renda_fixa/US/us_treasury_bond_20y_TLT.csv', region: 'EUA', category: 'Renda Fixa' },
    { id: 'us_corp_inv', name: 'US Corp Bond Inv Grade (LQD)', path: '../dados/renda_fixa/US/us_corp_bond_inv_grade_LQD.csv', region: 'EUA', category: 'Renda Fixa' },
    { id: 'us_corp_high', name: 'US Corp Bond High Yield (HYG)', path: '../dados/renda_fixa/US/us_corp_bond_high_yield_HYG.csv', region: 'EUA', category: 'Renda Fixa' },
    { id: 'us_treasury_1_3', name: 'US Treasury Bond 1-3y (SHY)', path: '../dados/renda_fixa/US/us_treasury_bond_1_3y_SHY.csv', region: 'EUA', category: 'Renda Fixa' },
    
    // EUA - Renda Variável
    { id: 'sp500', name: 'US S&P 500 (SPY)', path: '../dados/renda_variavel/US/us_sp500_SPY.csv', region: 'EUA', category: 'Renda Variável' },

    // BR - Renda Fixa
    { id: 'br_cri_inf', name: 'BR CRI Inflation Proxy (CPTS11)', path: '../dados/renda_fixa/BR/br_cri_inflation_proxy_CPTS11.csv', region: 'Brasil', category: 'Renda Fixa' },
    { id: 'br_gov_fixed', name: 'BR Gov Fixed Rate (IRFM11)', path: '../dados/renda_fixa/BR/br_gov_fixed_rate_IRFM11.csv', region: 'Brasil', category: 'Renda Fixa' },
    { id: 'br_deb_infra', name: 'BR Debêntures Infra (KDIF11)', path: '../dados/renda_fixa/BR/br_debentures_infra_KDIF11.csv', region: 'Brasil', category: 'Renda Fixa' },
    { id: 'br_gov_inf', name: 'BR Gov Inflation (IMAB11)', path: '../dados/renda_fixa/BR/br_gov_inflation_IMAB11.csv', region: 'Brasil', category: 'Renda Fixa' },
    { id: 'br_deb', name: 'BR Debêntures (DEBB11)', path: '../dados/renda_fixa/BR/br_debentures_DEBB11.csv', region: 'Brasil', category: 'Renda Fixa' },
    { id: 'br_cri_proxy', name: 'BR CRI Proxy (KNCR11)', path: '../dados/renda_fixa/BR/br_cri_proxy_KNCR11.csv', region: 'Brasil', category: 'Renda Fixa' },
    { id: 'selic', name: 'Selic Histórica', path: '../dados/renda_fixa/BR/selic_historica.csv', region: 'Brasil', category: 'Renda Fixa' },
    
    // BR - Renda Variável
    { id: 'ibovespa', name: 'BR Ibovespa (BOVA11)', path: '../dados/renda_variavel/BR/br_ibovespa_BOVA11.csv', region: 'Brasil', category: 'Renda Variável' },

    // BR - Cotações (Câmbio)
    { id: 'usd_brl', name: 'USD/BRL', path: '../dados/cotacao/usd_brl_currency.csv', region: 'Brasil', category: 'Cotações' },
    { id: 'eur_brl', name: 'EUR/BRL', path: '../dados/cotacao/eur_brl_currency.csv', region: 'Brasil', category: 'Cotações' },

    // Ativos Não Tradicionais / Globais
    { id: 'silver', name: 'Prata (Silver)', path: '../dados/metais/silver_prata.csv', region: 'Ativos Não Tradicionais', category: 'Metais' },
    { id: 'gold', name: 'Ouro (Gold)', path: '../dados/metais/gold_ouro.csv', region: 'Ativos Não Tradicionais', category: 'Metais' },
    { id: 'usdt', name: 'Stablecoin (USDT)', path: '../dados/ativos_nao_tradicionais/CRIPTO/stable_usdt.csv', region: 'Ativos Não Tradicionais', category: 'Cripto' },
    { id: 'art', name: 'Art Index (Artnet)', path: '../dados/ativos_nao_tradicionais/ARTE/art_index_artnet.csv', region: 'Ativos Não Tradicionais', category: 'Arte' }
];