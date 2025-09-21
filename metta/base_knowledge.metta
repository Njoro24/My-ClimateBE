; Climate Witness Chain - Base Knowledge
; Matches our actual backend models and database structure

; Event types from our backend models
(event-type drought)
(event-type flood)
(event-type locust)
(event-type extreme_heat)

; User roles from our backend
(user-role user)
(user-role researcher)

; Verification status from our backend
(verification-status pending)
(verification-status verified)
(verification-status rejected)
(verification-status manual_review)

; Trust score system (matches User model)
(min-trust-score 0)
(max-trust-score 100)
(default-trust-score 50)

; Trust thresholds for actions
(trust-threshold verification 60)
(trust-threshold reporting 30)
(trust-threshold high-trust-verify 80)

; Impact categories for economic correlation
(impact-category livestock_risk)
(impact-category crop_failure)
(impact-category infrastructure_damage)
(impact-category water_scarcity)

; Severity levels for payouts
(severity-level low)
(severity-level medium)
(severity-level high)
(severity-level critical)

; Payout amounts in ETH (matches our smart contract logic)
(payout-amount low 0.001)
(payout-amount medium 0.005)
(payout-amount high 0.01)
(payout-amount critical 0.02)

; Event type to impact mapping (for economic correlation)
(event-impact drought livestock_risk)
(event-impact drought water_scarcity)
(event-impact flood infrastructure_damage)
(event-impact flood crop_failure)
(event-impact locust crop_failure)
(event-impact extreme_heat water_scarcity)

; Event type to severity mapping (default)
(event-severity drought high)
(event-severity flood medium)
(event-severity locust high)
(event-severity extreme_heat medium)

; Verification rules
(max-event-age-hours 72)
(max-verification-distance 50)
(min-photo-evidence true)