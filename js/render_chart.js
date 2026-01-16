document.addEventListener('DOMContentLoaded', () => {
    // 1. Check for global config
    if (typeof CURRENT_ASSET_CONFIG === 'undefined') {
        console.error('CURRENT_ASSET_CONFIG not defined');
        return;
    }

    const assetConfig = CURRENT_ASSET_CONFIG;

    // Set title if exists
    const titleEl = document.getElementById('asset-name');
    if (titleEl) {
        titleEl.textContent = assetConfig.name;
        document.title = `Baroque - ${assetConfig.name}`;
    }

    // 2. Load Data
    Papa.parse(assetConfig.path, {
        download: true,
        header: true,
        skipEmptyLines: true,
        complete: function(results) {
            const loadingMsg = document.getElementById('loading-msg');
            if(loadingMsg) loadingMsg.style.display = 'none';
            
            const data = processData(results.data);
            if (data.labels.length > 0) {
                createChart(data);
            } else {
                console.error("No valid data found.");
                if(loadingMsg) {
                    loadingMsg.style.display = 'block';
                    loadingMsg.textContent = 'Dados insuficientes para exibir o gráfico.';
                }
            }
        },
        error: function(err) {
            console.error("Error loading CSV:", err);
            const loadingMsg = document.getElementById('loading-msg');
            if(loadingMsg) {
                loadingMsg.style.display = 'block';
                loadingMsg.textContent = 'Erro ao carregar dados.';
            }
        }
    });

    function processData(csvData) {
        if (!csvData || csvData.length === 0) return { labels: [], values: [] };
        
        const keys = Object.keys(csvData[0]);
        // Expecting first column Date, second column Value
        
        const labels = [];
        const values = [];

        csvData.forEach(row => {
            const dateStr = row[keys[0]];
            const valStr = row[keys[1]];
            
            if (dateStr && valStr && !isNaN(parseFloat(valStr))) {
                labels.push(dateStr);
                values.push(parseFloat(valStr));
            }
        });

        return { labels, values };
    }

    function createChart(data) {
        // Need to create a canvas element inside the container because Chart.js needs a canvas context
        // The container currently has <div id="chart"></div> which might not be a canvas depending on previous edits
        // But generate_pages.py template has <div id="chart"></div>. Chart.js needs <canvas>.
        // So we should replace the innerHTML or assume we can create one.
        
        const container = document.getElementById('chart');
        
        // Clear container and add canvas
        container.innerHTML = '';
        const canvas = document.createElement('canvas');
        container.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: assetConfig.name,
                    data: data.values,
                    borderColor: '#800020', // Borgonha
                    backgroundColor: 'rgba(128, 0, 32, 0.1)', // Light Burgundy fill
                    borderWidth: 1.5,
                    pointRadius: 0, // Clean look
                    pointHoverRadius: 4,
                    fill: false, // Minimalist, just line
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: '#fff',
                        titleColor: '#1a1a1a',
                        bodyColor: '#1a1a1a',
                        borderColor: '#eee',
                        borderWidth: 1,
                        displayColors: false
                    },
                    zoom: {
                        zoom: {
                            wheel: {
                                enabled: true,
                            },
                            pinch: {
                                enabled: true
                            },
                            mode: 'x', // Zoom mainly in time
                        },
                        pan: {
                            enabled: true,
                            mode: 'x',
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxTicksLimit: 8,
                            color: '#999',
                            font: {
                                family: 'Helvetica'
                            }
                        }
                    },
                    y: {
                        position: 'right',
                        grid: {
                            color: '#f0f0f0'
                        },
                        ticks: {
                            color: '#999',
                            font: {
                                family: 'Helvetica'
                            }
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
