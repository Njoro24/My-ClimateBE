
; Practical climate data for event verification and economic correlation


;; Economic impact values (USD per event)

(economic-impact drought livestock_risk 1000)
(economic-impact drought water_scarcity 500)
(economic-impact flood infrastructure_damage 2000)
(economic-impact flood crop_failure 800)
(economic-impact locust crop_failure 1500)
(economic-impact extreme_heat water_scarcity 300)


;; Location vulnerability factors (0.0 to 1.0)

(location-vulnerability "Turkana" 0.8)
(location-vulnerability "Kajiado" 0.6)
(location-vulnerability "Marsabit" 0.7)
(location-vulnerability "Samburu" 0.6)
(location-vulnerability "default" 0.5)


;; Early warning thresholds (number of events)

(warning-threshold drought 3)
(warning-threshold flood 2)
(warning-threshold locust 1)
(warning-threshold extreme_heat 4)


;; Risk assessment factors

(risk-factor livestock_risk 0.7)
(risk-factor crop_failure 0.8)
(risk-factor infrastructure_damage 0.6)
(risk-factor water_scarcity 0.5)


;; Location economic multipliers

(location-economic-multiplier "Turkana" 1.2)
(location-economic-multiplier "Kajiado" 1.0)
(location-economic-multiplier "Marsabit" 1.1)
(location-economic-multiplier "Samburu" 1.0)
(location-economic-multiplier "default" 1.0)


;; Event-impact mapping

(event-impact drought livestock_risk)
(event-impact drought water_scarcity)
(event-impact flood crop_failure)
(event-impact flood infrastructure_damage)
(event-impact locust crop_failure)
(event-impact extreme_heat water_scarcity)


;; Verified events

(event-verified "drought" "Turkana" "2025-08-20")
(event-verified "flood" "Turkana" "2025-08-25")
(event-verified "locust" "Marsabit" "2025-08-22")
(event-verified "extreme_heat" "Kajiado" "2025-08-24")
(event-verified "flood" "Samburu" "2025-08-26")


;;Functions
; Get economic impact for an event type and impact type
(= (get-economic-impact $event-type $impact-type)
   (match &self (economic-impact $event-type $impact-type $value) $value))

; Get location vulnerability
(= (get-location-vulnerability $location)
   (let (($vulnerability (match &self (location-vulnerability $location $value) $value)))
     (if $vulnerability $vulnerability 0.5)))

; Get location economic multiplier
(= (get-location-multiplier $location)
   (let (($multiplier (match &self (location-economic-multiplier $location $value) $value)))
     (if $multiplier $multiplier 1.0)))

; Calculate total economic impact for an event at a location
(= (calculate-total-economic-impact $event-type $location)
   (let* (($impacts (match &self (event-impact $event-type $impact-type) $impact-type))
          ($vulnerability (get-location-vulnerability $location))
          ($multiplier (get-location-multiplier $location))
          ($total-impact (foldl-atom $impacts 0 $acc $impact-type
                           (let (($impact-value (get-economic-impact $event-type $impact-type)))
                             (+ $acc $impact-value))))
          ($adjusted-impact (* $total-impact $vulnerability $multiplier)))
     $adjusted-impact))

; Calculate total economic impact for all verified events at a location
(= (calculate-verified-events-impact $location)
   (let (($events (match &self (event-verified $event-type $location $date) $event-type)))
     (foldl-atom $events 0 $acc $event-type
       (let (($impact (calculate-total-economic-impact $event-type $location)))
         (+ $acc $impact)))))

; Check if an event type exceeds warning threshold at a location
(= (check-warning $event-type $location)
   (let* (($events (match &self (event-verified $event-type $location $date) $date))
          ($count (length $events))
          ($threshold (match &self (warning-threshold $event-type $value) $value)))
     (if (>= $count $threshold) "Warning" "OK")))
