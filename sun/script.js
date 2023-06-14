<script>
        function updateValue(id, val) {
            document.getElementById(id + '_val').innerText = val;
        }
        function updateValue(id, val) {
                document.getElementById(id + '_val').innerText = val;
            }

            function validateInput(input) {
                let number = parseFloat(input.value);
                if (!isNaN(number) && number >= input.min && number <= input.max) {
                    input.style.borderColor = 'green';
                } else {
                    input.style.borderColor = 'red';
                }
            }

            // Tooltip initialization
            $(document).ready(function(){
                $('[data-toggle="tooltip"]').tooltip();
            });
        
        // Update the equation text whenever an input value changes
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

        // Call the updateEquation function whenever an input value changes
        document.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', updateEquation);
        });

        document.getElementById('date').innerText = new Date().toLocaleDateString();

        window.onload = function() {
            document.getElementById('current_date').innerHTML = getFormattedDate();
        }
        function getFormattedDate() {
            var date = new Date();

            var day = date.getDate(),
                month = date.getMonth(),
                year = date.getFullYear(),
                suffix = '';

            switch(day) {
                case 1: 
                case 21: 
                case 31: 
                    suffix = 'st'; 
                    break;
                case 2: 
                case 22: 
                    suffix = 'nd'; 
                    break;
                case 3: 
                case 23: 
                    suffix = 'rd'; 
                    break;
                default: 
                    suffix = 'th';
            }

            // Array of month names
            var month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

            return 'Today is ' + month_names[month] + ' ' + day + suffix + ', ' + year;
        }

        document.getElementById('roi-form').addEventListener('submit', function(event) {
            event.preventDefault();
            updateEquation();
        });

    </script>
