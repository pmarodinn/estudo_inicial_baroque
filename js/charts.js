document.addEventListener('DOMContentLoaded', () => {
    const assets = [
        { name: 'US Treasury Bond 7-10y (IEF)', path: '../dados/renda_fixa/US/us_treasury_bond_7_10y_IEF.csv' },
        { name: 'US Treasury Bond 20y (TLT)', path: '../dados/renda_fixa/US/us_treasury_bond_20y_TLT.csv' },
        { name: 'US Corp Bond Inv Grade (LQD)', path: '../dados/renda_fixa/US/us_corp_bond_inv_grade_LQD.csv' },
        { name: 'US Corp Bond High Yield (HYG)', path: '../dados/renda_fixa/US/us_corp_bond_high_yield_HYG.csv' },
        { name: 'US Treasury Bond 1-3y (SHY)', path: '../dados/renda_fixa/US/us_treasury_bond_1_3y_SHY.csv' },
        { name: 'BR CRI Inflation Proxy (CPTS11)', path: '../dados/renda_fixa/BR/br_cri_inflation_proxy_CPTS11.csv' },
        { name: 'BR Gov Fixed Rate (IRFM11)', path: '../dados/renda_fixa/BR/br_gov_fixed_rate_IRFM11.csv' },
        { name: 'BR Debêntures Infra (KDIF11)', path: '../dados/renda_fixa/BR/br_debentures_infra_KDIF11.csv' },
        { name: 'BR Gov Inflation (IMAB11)', path: '../dados/renda_fixa/BR/br_gov_inflation_IMAB11.csv' },
        { name: 'BR Debêntures (DEBB11)', path: '../dados/renda_fixa/BR/br_debentures_DEBB11.csv' },
        { name: 'BR CRI Proxy (KNCR11)', path: '../dados/renda_fixa/BR/br_cri_proxy_KNCR11.csv' },
        { name: 'Selic Histórica', path: '../dados/renda_fixa/BR/selic_historica.csv' },
        { name: 'Prata (Silver)', path: '../dados/metais/silver_prata.csv' },
        { name: 'Ouro (Gold)', path: '../dados/metais/gold_ouro.csv' },
        { name: 'Stablecoin (USDT)', path: '../dados/ativos_nao_tradicionais/CRIPTO/stable_usdt.csv' },
        { name: 'Art Index (Artnet)', path: '../dados/ativos_nao_tradicionais/ARTE/art_index_artnet.csv' },
        { name: 'USD/BRL', path: '../dados/cotacao/usd_brl_currency.csv' },
        { name: 'EUR/BRL', path: '../dados/cotacao/eur_brl_currency.csv' },
        { name: 'US S&P 500 (SPY)', path: '../dados/renda_variavel/US/us_sp500_SPY.csv' },
        { name: 'BR Ibovespa (BOVA11)', path: '../dados/renda_variavel/BR/br_ibovespa_BOVA11.csv' }
    ];

    const grid = document.getElementById('charts-grid');

    assets.forEach((asset, index) => {
        // Create HTML structure for each chart
        const card = document.createElement('article');
        card.className = 'card';
        
        const title = document.createElement('h3');
        title.textContent = asset.name;
        card.appendChild(title);

        const chartContainer = document.createElement('div');
        chartContainer.className = 'chart-container';
        
        const canvas = document.createElement('canvas');
        canvas.id = `chart-${index}`;
        chartContainer.appendChild(canvas);
        card.appendChild(chartContainer);
        
        grid.appendChild(card);

        // Fetch and parse CSV
        Papa.parse(asset.path, {
            download: true,
            header: true,
            skipEmptyLines: true,
            complete: function(results) {
                createChart(canvas.id, results.data, asset.name);
            },
            error: function(err) {
                console.error(`Error loading ${asset.name}:`, err);
                chartContainer.innerHTML = '<p style="color:red; font-size: 0.8rem;">Erro ao carregar dados.</p>';
            }
        });
    });

    function createChart(canvasId, data, label) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        // Extract labels (Date) and data (Value - assume 2nd column)
        // Check keys to find the value column (not 'Date')
        if (data.length === 0) return;
        
        const keys = Object.keys(data[0]);
        const dateKey = keys[0]; // Assuming first is Date
        const valueKey = keys[1]; // Assuming second is Value

        const labels = data.map(item => item[dateKey]);
        const values = data.map(item => parseFloat(item[valueKey]));

        // Calculate simple trend for color (Green if last > first)
        const isPositive = values[values.length - 1] >= values[0];
        // Minimalist colors: simple black or grey line, maybe green/red for trend only implicitly or subtle
        // Request was minimalist. Black line is very minimalist.
        const borderColor = '#800020'; 
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: values,
                    borderColor: borderColor,
                    borderWidth: 1.5,
                    pointRadius: 0, // Hide points for cleaner look
                    pointHoverRadius: 4,
                    fill: false,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false // Hide legend for minimalism
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    x: {
                        display: false, // Hide x axis labels for cleaner look on small charts
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        position: 'right', // Put axis on right
                        grid: {
                            color: '#f0f0f0'
                        },
                        ticks: {
                            font: {
                                size: 10,
                                family: 'Helvetica'
                            },
                            color: '#999'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }
});
