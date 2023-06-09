from flask import Flask, render_template, request

app = Flask(__name__)

def calculate_solar_roi(system_size=4.0, system_cost=10000.0, panel_efficiency=0.18, 
                        sunlight_hours=5.0, energy_usage=4000.0, energy_sell_price=0.10, 
                        maintenance_cost_rate=0.01):
    
    total_energy_produced = system_size * sunlight_hours * 365 * panel_efficiency
    surplus_energy = max(0, total_energy_produced - energy_usage)
    revenue_from_energy_sale = surplus_energy * energy_sell_price
    maintenance_cost = system_cost * maintenance_cost_rate
    roi = (revenue_from_energy_sale - maintenance_cost) / system_cost
    
    return roi

@app.route('/', methods=['GET', 'POST'])
def index():
    roi = None
    if request.method == 'POST':
        system_size = float(request.form.get('system_size', 4.0))
        system_cost = float(request.form.get('system_cost', 10000.0))
        panel_efficiency = float(request.form.get('panel_efficiency', 0.18))
        sunlight_hours = float(request.form.get('sunlight_hours', 5.0))
        energy_usage = float(request.form.get('energy_usage', 4000.0))
        energy_sell_price = float(request.form.get('energy_sell_price', 0.10))
        maintenance_cost_rate = float(request.form.get('maintenance_cost_rate', 0.01))

        roi = calculate_solar_roi(system_size, system_cost, panel_efficiency, sunlight_hours,
                                  energy_usage, energy_sell_price, maintenance_cost_rate)

    return render_template('index.html', roi=roi)

@app.route('/map')
def map():
    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)
