document.addEventListener('DOMContentLoaded', () => {
    // 1. Get Asset ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const assetId = urlParams.get('asset');

    if (!assetId) {
        document.getElementById('asset-name').textContent = 'Erro: Ativo não especificado.';
        document.getElementById('loading-msg').style.display = 'none';
        return;
    }

    // 2. Find config
    const assetConfig = ASSETS_CONFIG.find(a => a.id === assetId);
    if (!assetConfig) {
        document.getElementById('asset-name').textContent = 'Erro: Ativo não encontrado.';
        document.getElementById('loading-msg').style.display = 'none';
        return;
    }

    document.getElementById('asset-name').textContent = assetConfig.name;
    document.title = `Baroque - ${assetConfig.name}`;

    // 3. Setup Chart
    const container = document.getElementById('chart');
    const chart = LightweightCharts.createChart(container, {
        layout: {
            background: { type: 'solid', color: '#ffffff' },
            textColor: '#1a1a1a',
        },
        grid: {
            vertLines: { color: '#f0f0f0' },
            horzLines: { color: '#f0f0f0' },
        },
        rightPriceScale: {
            borderColor: '#dfe1e5',
        },
        timeScale: {
            borderColor: '#dfe1e5',
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
    });

    // Handle resizing
    window.addEventListener('resize', () => {
        chart.applyOptions({ width: container.clientWidth, height: container.clientHeight });
    });

    const series = chart.addLineSeries({
        color: '#800020', // Borgonha
        lineWidth: 2,
        crosshairMarkerVisible: true,
        crosshairMarkerBackgroundColor: '#800020',
        lineType: 0, // Simple
    });

    // 4. Load Data
    Papa.parse(assetConfig.path, {
        download: true,
        header: true,
        skipEmptyLines: true,
        complete: function(results) {
            document.getElementById('loading-msg').style.display = 'none';
            const data = processData(results.data);
            if (data && data.length > 0) {
                series.setData(data);
                chart.timeScale().fitContent();
            } else {
                console.error("No valid data found.");
            }
        },
        error: function(err) {
            console.error("Error loading CSV:", err);
            document.getElementById('loading-msg').textContent = 'Erro ao carregar dados.';
        }
    });

    function processData(csvData) {
        if (!csvData || csvData.length === 0) return [];
        
        const keys = Object.keys(csvData[0]);
        // Expect Date is key[0], Value is key[1]
        // Lightweight charts needs { time: 'yyyy-mm-dd', value: number }
        
        const mappedData = csvData.map(row => {
            const dateStr = row[keys[0]];
            const valStr = row[keys[1]];
            
            if (!dateStr || !valStr) return null;

            // Ensure date is in YYYY-MM-DD format if possible, but lightweight charts is quite forgiving with proper ISO strings
            // Our data seems to be YYYY-MM-DD from previous `read_file`.
            
            return {
                time: dateStr,
                value: parseFloat(valStr)
            };
        }).filter(item => item !== null && !isNaN(item.value));
        
        // Sort by time just in case
        mappedData.sort((a, b) => (new Date(a.time) - new Date(b.time)));

        // Remove duplicates on time (Lightweight charts throws error on duplicate time)
        const uniqueData = [];
        const seenTimes = new Set();
        
        for (const item of mappedData) {
            if (!seenTimes.has(item.time)) {
                seenTimes.add(item.time);
                uniqueData.push(item);
            }
        }

        return uniqueData;
    }
});
