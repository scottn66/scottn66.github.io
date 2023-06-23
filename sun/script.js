document.addEventListener('DOMContentLoaded', function() {
    // Update the current date
    updateCurrentDate();

    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();

    // Add event listener to the form
    document.getElementById('roi-form').addEventListener('submit', function(event) {
        event.preventDefault();
        updateEquation();
    });

    // Add event listeners to all inputs
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', function() {
            validateInput(input);
            updateEquation();
        });
    });
});

function updateCurrentDate() {
    var date = new Date();
    var day = date.getDate();
    var month = date.getMonth();
    var year = date.getFullYear();
    var suffix = ['th', 'st', 'nd', 'rd', 'th', 'th', 'th', 'th', 'th', 'th'][((day % 100) - 20) % 10] || 'th';
    var month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    document.getElementById('current_date').innerText = 'Today is ' + month_names[month] + ' ' + day + suffix + ', ' + year;
}

function validateInput(input) {
    let number = parseFloat(input.value);
    if (!isNaN(number) && number >= input.min && number <= input.max) {
        input.style.borderColor = 'green';
    } else {
        input.style.borderColor = 'red';
    }
}

function updateEquation() {
    let system_size = document.getElementById('system_size').value;
    let system_cost = document.getElementById('system_cost').value;
    let panel_efficiency = document.getElementById('panel_efficiency').value;
    let sunlight_hours = document.getElementById('sunlight_hours').value;
    let energy_usage = document.getElementById('energy_usage').value;
    let energy_sell_price = document.getElementById('energy_sell_price').value;
    let maintenance_cost_rate = document.getElementById('maintenance_cost_rate').value;

    let roi = ((system_size * panel_efficiency * sunlight_hours * 365 * energy_sell_price) - system_cost - (system_cost * maintenance_cost_rate)) / system_cost;

    document.getElementById('equation').innerText = 
        `ROI = ((System Size ${system_size} kW * Panel Efficiency ${panel_efficiency} * Sunlight Hours ${sunlight_hours} hours/day * 365 days/year * Energy Sell Price $${energy_sell_price}/kWh - System Cost $${system_cost} - Annual Maintenance Cost $${system_cost * maintenance_cost_rate}) / System Cost $${system_cost}) * 100%`;
    document.getElementById('roiResult').innerText = `Return on Investment: ${(roi * 100).toFixed(2)}%`;
}
