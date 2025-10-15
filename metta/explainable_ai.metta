; Climate Witness Chain - Explainable AI Knowledge Base
; Extends existing verification system with transparency and explainability

; AI Decision Transparency Levels
(transparency-level basic)
(transparency-level detailed)
(transparency-level technical)
(transparency-level citizen-friendly)

; Explanation Types for Different Audiences
(explanation-type verification-decision)
(explanation-type trust-calculation)
(explanation-type payout-determination)
(explanation-type risk-assessment)
(explanation-type policy-recommendation)

; Confidence Levels for AI Decisions
(confidence-level very-high 0.9)
(confidence-level high 0.75)
(confidence-level medium 0.6)
(confidence-level low 0.4)
(confidence-level very-low 0.2)

; Bias Detection Categories
(bias-type geographic-bias)
(bias-type demographic-bias)
(bias-type temporal-bias)
(bias-type source-bias)
(bias-type confirmation-bias)

; Explainable Verification Rule - Enhanced from existing auto-verify
(= (explainable-auto-verify $event $user $image_confidence $desc_confidence)
   (let* (
       ($trust_score (match &trust-space (trust-score $user $score) $score))
       ($is_qualified (>= $trust_score 60))
       ($data_qualified (and (>= $image_confidence 60) (>= $desc_confidence 60)))
       ($verified (and $is_qualified $data_qualified))
       ($explanation (generate-verification-explanation $event $user $trust_score $image_confidence $desc_confidence $verified))
       ($confidence (calculate-decision-confidence $trust_score $image_confidence $desc_confidence))
   )
   (verification-result $event $verified $explanation $confidence)))

; Generate Human-Readable Explanations
(= (generate-verification-explanation $event $user $trust_score $image_confidence $desc_confidence $result)
   (let* (
       ($trust_reason (if (>= $trust_score 60) 
                         "User has sufficient trust score" 
                         "User trust score below threshold"))
       ($image_reason (if (>= $image_confidence 60) 
                         "Image evidence meets quality standards" 
                         "Image evidence quality insufficient"))
       ($desc_reason (if (>= $desc_confidence 60) 
                        "Description provides adequate detail" 
                        "Description lacks sufficient detail"))
       ($decision_reason (if $result 
                           "All verification criteria met" 
                           "One or more criteria failed"))
   )
   (explanation-chain $trust_reason $image_reason $desc_reason $decision_reason)))

; Calculate Decision Confidence Score
(= (calculate-decision-confidence $trust_score $image_confidence $desc_confidence)
   (let* (
       ($trust_weight 0.4)
       ($image_weight 0.35)
       ($desc_weight 0.25)
       ($normalized_trust (/ $trust_score 100))
       ($normalized_image (/ $image_confidence 100))
       ($normalized_desc (/ $desc_confidence 100))
       ($weighted_score (+ (* $normalized_trust $trust_weight)
                          (* $normalized_image $image_weight)
                          (* $normalized_desc $desc_weight)))
   )
   $weighted_score))

; Bias Detection in Verification Decisions
(= (detect-verification-bias $location $event_type $time_period)
   (let* (
       ($total_events (count-events $location $event_type $time_period))
       ($verified_events (count-verified-events $location $event_type $time_period))
       ($verification_rate (/ $verified_events $total_events))
       ($global_avg_rate (get-global-verification-rate $event_type))
       ($bias_threshold 0.2)
       ($rate_difference (abs (- $verification_rate $global_avg_rate)))
       ($has_bias (> $rate_difference $bias_threshold))
   )
   (bias-detection-result $location $event_type $has_bias $rate_difference $verification_rate $global_avg_rate)))

; Policy Impact Assessment using Climate Data
(= (assess-policy-impact $policy_type $location $climate_data)
   (let* (
       ($historical_events (get-historical-events $location))
       ($vulnerability (get-location-vulnerability $location))
       ($economic_impact (calculate-verified-events-impact $location))
       ($predicted_reduction (calculate-policy-effectiveness $policy_type $vulnerability))
       ($cost_benefit_ratio (/ $predicted_reduction $economic_impact))
   )
   (policy-assessment $policy_type $location $predicted_reduction $cost_benefit_ratio)))

; Democratic Decision Support
(= (generate-civic-recommendation $issue $stakeholders $evidence)
   (let* (
       ($evidence_quality (assess-evidence-quality $evidence))
       ($stakeholder_consensus (calculate-consensus $stakeholders))
       ($transparency_score (calculate-transparency $evidence $stakeholders))
       ($recommendation_confidence (min $evidence_quality $stakeholder_consensus $transparency_score))
   )
   (civic-recommendation $issue $recommendation_confidence $evidence_quality $stakeholder_consensus)))

; Explanation Generation for Citizens
(= (citizen-friendly-explanation $decision_type $technical_details)
   (case $decision_type
     (verification-decision 
       "We verified this climate event by checking: 1) The reporter's trust score, 2) Photo quality, 3) Description accuracy. All criteria were met.")
     (trust-calculation 
       "Trust scores increase when reports are accurate and decrease when they're not. This helps us identify reliable community members.")
     (payout-determination 
       "Payouts are based on event severity and verification status. Higher severity verified events receive larger rewards.")
     (risk-assessment 
       "Risk levels consider past events, location vulnerability, and current conditions to predict future climate impacts.")
     (policy-recommendation 
       "Policy suggestions are based on verified climate data, economic impact analysis, and community input from affected areas.")))

; Audit Trail for AI Decisions
(= (create-audit-trail $decision_id $decision_type $inputs $outputs $timestamp)
   (audit-entry $decision_id $decision_type $inputs $outputs $timestamp 
                (generate-audit-explanation $decision_type $inputs $outputs)))

; Fairness Metrics Calculation
(= (calculate-fairness-metrics $decision_set)
   (let* (
       ($demographic_parity (calculate-demographic-parity $decision_set))
       ($equalized_odds (calculate-equalized-odds $decision_set))
       ($individual_fairness (calculate-individual-fairness $decision_set))
       ($overall_fairness (/ (+ $demographic_parity $equalized_odds $individual_fairness) 3))
   )
   (fairness-metrics $demographic_parity $equalized_odds $individual_fairness $overall_fairness)))

; Interactive Explanation System
(= (interactive-explanation $user_question $context)
   (case $user_question
     ("Why was this event verified?" 
       (get-verification-explanation $context))
     ("How is trust score calculated?" 
       (get-trust-explanation $context))
     ("What factors affect payouts?" 
       (get-payout-explanation $context))
     ("How do you detect bias?" 
       (get-bias-explanation $context))
     ("What data supports this policy?" 
       (get-policy-explanation $context))))