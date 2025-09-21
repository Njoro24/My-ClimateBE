# MeTTa Knowledge Files

This directory contains the MeTTa knowledge base files for the Climate Witness Chain project. These files define the core logic, rules, and knowledge used for climate event verification and automated reasoning.

## File Structure

### 📄 `base_knowledge.metta`

Contains foundational knowledge about climate events, trust scores, and system parameters.

**Key Components:**

- Climate event type definitions (Drought, Flood, Locust, ExtremeHeat)
- Trust score system (thresholds, defaults)
- Impact categories (Livestock_Risk, Crop_Failure, etc.)
- Severity levels (Low, Medium, High, Critical)
- Payout amounts for different severity levels
- Geographic regions and event mappings

### 📄 `verification_rules.metta`

Defines the core verification logic and rules for automated climate event verification.

**Key Components:**

- Auto-verification rules based on evidence, GPS, and trust scores
- Trust score update mechanisms
- Payout eligibility calculations
- Event correlation and pattern detection
- Consensus verification logic
- Fraud detection rules

### 📄 `climate_data.metta`

Contains climate-specific knowledge, patterns, and domain expertise.

**Key Components:**

- Seasonal patterns by region
- Climate event indicators and thresholds
- Economic impact calculations
- Vulnerability factors by region
- Climate change trends
- Early warning thresholds
- Traditional knowledge integration

### 📄 `helper_functions.metta`

Utility functions and mathematical operations used throughout the system.

**Key Components:**

- Distance calculations (Haversine approximation)
- Time difference calculations
- Geographic boundary checks
- Metadata consistency validation
- Trust score calculations
- Payout adjustments and multipliers

## Loading Order

The files are loaded in the following order to ensure proper dependency resolution:

1. `base_knowledge.metta` - Foundation knowledge
2. `helper_functions.metta` - Utility functions
3. `climate_data.metta` - Domain-specific data
4. `verification_rules.metta` - Complex rules that depend on the above

## Usage

### Loading in Python

```python
from app.services.metta_service import ClimateWitnessKnowledgeBase

# Knowledge base automatically loads all .metta files
kb = ClimateWitnessKnowledgeBase()
```

### Validation

Use the MeTTa loader utility to validate files:

```bash
python metta_loader.py
```

### Testing

Run the demo to see the knowledge base in action:

```bash
python demo_metta.py
```

## MeTTa Syntax Examples

### Basic Facts

```metta
(climate-event-type Drought)
(min-trust-score 60)
(payout-amount High 0.01)
```

### Rules with Logic

```metta
(= (auto-verify $event $user)
   (and (evidence-link $event $link)
        (gps-coords $event $coords)
        (trust-score $user $score)
        (>= $score 60))
   (verified $event))
```

### Conditional Logic

```metta
(= (calculate-severity $impact $area)
   (cond ((> $impact 80) Critical)
         ((> $impact 60) High)
         ((> $impact 40) Medium)
         (True Low))
   $severity)
```

## Extending the Knowledge Base

### Adding New Event Types

1. Add to `base_knowledge.metta`:

   ```metta
   (climate-event-type NewEventType)
   ```

2. Add impact mapping:

   ```metta
   (event-impact-mapping NewEventType SomeImpact)
   ```

3. Update verification rules if needed in `verification_rules.metta`

### Adding New Regions

1. Add region definition:

   ```metta
   (region "New Region, Country")
   ```

2. Add bounding box in `helper_functions.metta`:
   ```metta
   (region-bounds "New Region, Country" min-lat max-lat min-lng max-lng)
   ```

### Adding Custom Rules

Add new rules to `verification_rules.metta` following the pattern:

```metta
(= (rule-name $param1 $param2)
   (and (condition1 $param1)
        (condition2 $param2))
   (conclusion $result))
```

## Best Practices

1. **Comments**: Use `;` for comments to document complex rules
2. **Naming**: Use descriptive names with hyphens (kebab-case)
3. **Organization**: Group related facts and rules together
4. **Testing**: Always test new rules with the validation tools
5. **Dependencies**: Be aware of loading order for dependent rules

## Troubleshooting

### Common Issues

1. **Unbalanced Parentheses**: Every `(` must have a matching `)`
2. **Variable Naming**: Variables must start with `$`
3. **Rule Format**: Rules must follow `(= (head) (body) (conclusion))` format
4. **Loading Order**: Complex rules may fail if dependencies aren't loaded first

### Validation Tools

- `python metta_loader.py` - Interactive file validation
- `python run_metta_tests.py` - Automated testing
- `python demo_metta.py` - Live demonstration

## Integration

The MeTTa files are automatically loaded by the `ClimateWitnessKnowledgeBase` class and used throughout the Climate Witness Chain system for:

- Event verification
- Trust score management
- Payout calculations
- Pattern detection
- Fraud prevention
- Early warning systems

Changes to these files will be reflected immediately when the system restarts.
