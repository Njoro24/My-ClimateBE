from hyperon import MeTTa

# Initialize MeTTa engine
metta = MeTTa()

# Load the KB file
with open("climate_witness_chain.metta", "r") as f:
    metta.run(f.read())

# Example: calculate total economic impact for Turkana
total_impact_result = metta.run('(calculate-verified-events-impact "Turkana")')
print("Total Economic Impact for Turkana:", total_impact_result)

# Example: check drought warning for Turkana
warning_status_result = metta.run('(check-warning "drought" "Turkana")')
print("Drought Warning Status for Turkana:", warning_status_result)
