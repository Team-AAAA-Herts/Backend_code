def correlatePowerAndWeather(panel_data: dict, weather_data: dict) -> dict:
    """
    Calculates the expected output, efficiency ratio, and operational status 
    of a solar panel based on current weather and temperature conditions.
    """
    
    # 1. Extract inputs
    max_capacity = panel_data.get('maxCapacity', 0.0)
    current_output = max(0.0, panel_data.get('currentOutput', 0.0))
    temperature = panel_data.get('temperature', 25.0)
    
    cloud_cover = weather_data.get('cloudCover', 0.0)
    solar_irradiance = weather_data.get('solarIrradiance') # Optional

    # 2. Calculate the Light Factor
    if solar_irradiance is not None:
        # Fallback A: Use gold-standard Irradiance
        light_factor = solar_irradiance / 1000.0
    else:
        # Fallback B: Rely on cloud cover proxy
        light_factor = 1.0 - (cloud_cover / 100.0)

    # 3. Calculate the Temperature Factor
    # Using the continuous math formula: Multiplier = 1 - (T - 25) * 0.004
    temperature_factor = 1.0 - (temperature - 25.0) * 0.004

    # 4. Calculate Expected Output (Multiplicative)
    expected_output = max_capacity * light_factor * temperature_factor

    # 5. Guard Clause: Prevent ZeroDivisionError & Handle Night/Low Light
    if expected_output < 1.0:
        return {
            "expectedOutput": round(expected_output, 2),
            "efficiencyRatio": 0.0,
            "status": "Idle"
        }

    # 6. Calculate Efficiency Ratio
    efficiency_ratio = current_output / expected_output

    # 7. Determine Status (Inclusive Boundaries)
    if efficiency_ratio >= 0.90:
        status = "Optimal"
    elif efficiency_ratio >= 0.70:
        status = "Underperforming"
    else:
        status = "Faulty"

    # 8. Return the structured object
    return {
        "expectedOutput": round(expected_output, 2),
        "efficiencyRatio": round(efficiency_ratio, 4), # Keeping 4 decimals for accurate percentages
        "status": status
    }



def evaluateBatteryHealth(battery_data: dict) -> dict:
    """
    Evaluates the State of Charge (SOC), State of Health (SOH), 
    and operational safety status of a solar battery.
    """
    
    # 1. Extract inputs with safe fallbacks
    design_capacity = battery_data.get('designCapacity', 0.0)
    current_max_capacity = battery_data.get('currentMaxCapacity', 0.0)
    current_charge = battery_data.get('currentCharge', 0.0)
    temperature = battery_data.get('temperature', 25.0)
    cycle_count = battery_data.get('cycleCount', 0)

    # 2. Guard Clause: Invalid Design Capacity
    if design_capacity <= 0:
        return {
            "stateOfCharge": 0.0,
            "stateOfHealth": 0.0,
            "temperatureWarning": False,
            "status": "Error: Invalid Capacity"
        }

    # 3. Calculate State of Health (SOH)
    state_of_health = current_max_capacity / design_capacity

    # 4. Calculate State of Charge (SOC) with Bypass
    if current_max_capacity <= 0:
        state_of_charge = 0.0
    else:
        state_of_charge = current_charge / current_max_capacity

    # 5. Check the Thermometer
    temperature_warning = temperature > 35.0 or temperature < 0.0

    # 6. Determine Status (Factoring in SOH and Pro-Level Cycle Count)
    if cycle_count >= 4000:
        status = "Replace Soon"
    elif state_of_health >= 0.80:
        status = "Healthy"
    elif state_of_health >= 0.60:
        status = "Degraded"
    else:
        status = "Replace Soon"

    # 7. Return the structured object
    return {
        "stateOfCharge": round(state_of_charge, 4),
        "stateOfHealth": round(state_of_health, 4),
        "temperatureWarning": temperature_warning,
        "status": status
    }



def checkMaintenanceTriggers(maintenance_data: dict) -> dict:
    """
    Evaluates system efficiency and historical service logs to trigger 
    appropriate cleaning and maintenance alerts.
    """
    
    # 1. Extract inputs with safe fallbacks
    efficiency_ratio = maintenance_data.get('efficiencyRatio', 1.0)
    days_since_last_cleaning = maintenance_data.get('daysSinceLastCleaning', -1)
    days_since_last_service = maintenance_data.get('daysSinceLastService', -1)

    # 2. Evaluate Triggers (Sentinel value -1 naturally fails the >= checks)
    needs_cleaning = (efficiency_ratio < 0.80) or (days_since_last_cleaning >= 60)
    needs_service = (efficiency_ratio < 0.70) or (days_since_last_service >= 180)

    # 3. Initialize Outputs
    urgency_level = "None"
    recommended_actions = []

    # 4. Grade Urgency and Append Messages (Independent Checks)
    
    # Check Service (Critical or Medium)
    if needs_service:
        if efficiency_ratio < 0.70:
            urgency_level = "Critical"
            recommended_actions.append("Severe efficiency drop. Schedule maintenance immediately.")
        else:
            urgency_level = "Medium"
            recommended_actions.append("Routine 6-month maintenance is due.")

    # Check Cleaning (Low)
    if needs_cleaning:
        # Only set urgency to Low if a higher urgency hasn't already been triggered
        if urgency_level == "None":
            urgency_level = "Low"
        recommended_actions.append("Panel efficiency dropping or routine wash due. Please clean panels.")

    # 5. Default "All Clear" State
    if not needs_service and not needs_cleaning:
        recommended_actions.append("System operating normally.")

    # 6. Return the structured Alert Object
    return {
        "needsCleaning": needs_cleaning,
        "needsService": needs_service,
        "urgencyLevel": urgency_level,
        "recommendedActions": recommended_actions
    }




def generateFinancialMetrics(financial_data: dict) -> dict:
    """
    Calculates financial savings and carbon offsets based on energy generation,
    handling missing energy rates with standard national defaults.
    """
    
    # 1. Extract and Sanitize Inputs
    total_kwh = financial_data.get('totalKilowattHours', 0.0)
    
    # Guard Clause: Clamp negative sensor glitches to 0.0
    if total_kwh < 0.0:
        total_kwh = 0.0
        
    local_energy_rate = financial_data.get('localEnergyRate')

    # 2. The Fallback Rate & Estimation Flag
    if local_energy_rate is None or local_energy_rate <= 0.0:
        local_energy_rate = 0.15  # Standard national average fallback
        is_estimated = True
    else:
        is_estimated = False

    # 3. Calculate the Money
    gross_savings = total_kwh * local_energy_rate

    # 4. Calculate the Carbon Offset
    # Using the standard EPA conversion factor: 0.39 kg CO2 per kWh
    carbon_offset_kg = total_kwh * 0.39

    # 5. Return the structured object
    return {
        "grossSavings": round(gross_savings, 2),
        "carbonOffsetKg": round(carbon_offset_kg, 2),
        "isEstimated": is_estimated
    }




# Assuming your generateFinancialMetrics function is defined above this

test_cases = [
    {
        "name": "1. Standard User (Known Rate)",
        "data": {"totalKilowattHours": 100.0, "localEnergyRate": 0.20},
        "expected_savings": 20.0,  # 100 * 0.20
        "expected_estimated": False
    },
    {
        "name": "2. Missing Rate (The Fallback)",
        "data": {"totalKilowattHours": 100.0}, # No rate provided
        "expected_savings": 15.0,  # 100 * 0.15 (default)
        "expected_estimated": True
    },
    {
        "name": "3. Zero Rate (Accidental User Input)",
        "data": {"totalKilowattHours": 100.0, "localEnergyRate": 0.0},
        "expected_savings": 15.0,  # Should override 0.0 with 0.15
        "expected_estimated": True
    },
    {
        "name": "4. Negative Sensor Glitch",
        "data": {"totalKilowattHours": -50.0, "localEnergyRate": 0.20},
        "expected_savings": 0.0,   # Clamped to 0
        "expected_estimated": False # Rate is valid, so not estimated
    },
    {
        "name": "5. Missing All Data (Empty Payload)",
        "data": {},
        "expected_savings": 0.0,   # 0.0 kWh * 0.15 rate
        "expected_estimated": True
    }
]

# --- Test Runner ---
print("--- Running Financial Metrics Tests ---\n")
for idx, test in enumerate(test_cases):
    print(f"Running: {test['name']}")
    
    result = generateFinancialMetrics(test['data'])
    
    savings_passed = result['grossSavings'] == test['expected_savings']
    estimated_passed = result['isEstimated'] == test['expected_estimated']
    
    if savings_passed and estimated_passed:
        print(f"✅ PASS! Savings: ${result['grossSavings']} | Estimated: {result['isEstimated']} | CO2 Offset: {result['carbonOffsetKg']}kg\n")
    else:
        print(f"❌ FAIL!")
        print(f"   Expected Savings: ${test['expected_savings']} | Got: ${result['grossSavings']}")
        print(f"   Expected Estimated: {test['expected_estimated']} | Got: {result['isEstimated']}")
        print(f"   Result details: {result}\n")