// Fetch and update dashboard
async function loadDashboard() {
    try {
        const statusResponse = await fetch('/api/status');
        const status = await statusResponse.json();
        document.getElementById('status').textContent = status.status + ' - ' + status.timestamp;
        
        const modelsResponse = await fetch('/api/models');
        const models = await modelsResponse.json();
        document.getElementById('models').innerHTML = Object.entries(models)
            .map(([name, active]) => `<div class="stat"><span class="stat-label">${name}</span><span class="stat-value ${active ? 'status-active' : 'status-inactive'}">${active ? '✓' : '✗'}</span></div>`)
            .join('');
        
        const tradesResponse = await fetch('/api/trades');
        const tradesData = await tradesResponse.json();
        const trades = tradesData.trades || [];
        if (trades.length > 0) {
            const latestTrade = trades[0];
            document.getElementById('trades').innerHTML = `
                <div class="stat"><span class="stat-label">Total Trades</span><span class="stat-value">${trades.length}</span></div>
                <div class="stat"><span class="stat-label">Latest</span><span class="stat-value">${latestTrade.symbol}</span></div>
                <div class="stat"><span class="stat-label">P&L</span><span class="stat-value">${latestTrade.pnl || 'N/A'}</span></div>
            `;
        }
        
        const skillsResponse = await fetch('/api/skills');
        const skills = await skillsResponse.json();
        document.getElementById('skills').innerHTML = Object.entries(skills)
            .map(([name, data]) => `<div class="stat"><span class="stat-label">${name}</span><span class="stat-value">Lvl ${data.level}</span></div>`)
            .join('');
    } catch (error) {
        console.error('Dashboard load error:', error);
    }
}

// Load dashboard on page load
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    setInterval(loadDashboard, 5000);  // Refresh every 5 seconds
});
