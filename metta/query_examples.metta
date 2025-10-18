; Climate Witness Chain - Query Examples
; Basic MeTTa atoms and functions for natural language queries

; Sample user data
(user user_001)
(user user_002)
(user user_123)

; Sample trust scores
(trust-score user_001 85)
(trust-score user_002 72)
(trust-score user_123 91)

; Sample locations
(location user_001 "Turkana County")
(location user_002 "Marsabit County")
(location user_123 "Kajiado County")

; Sample events
(event drought_001)
(event flood_002)
(event locust_003)

; Event types
(event-type drought_001 drought)
(event-type flood_002 flood)
(event-type locust_003 locust)

; Event locations
(location drought_001 "Turkana County")
(location flood_002 "Marsabit County")
(location locust_003 "Kajiado County")

; Event reporters
(reports user_001 drought_001)
(reports user_002 flood_002)
(reports user_123 locust_003)

; Verified events
(verified drought_001)
(verified flood_002)

; Evidence links
(evidence-link drought_001 "/uploads/drought_photo_001.jpg")
(evidence-link flood_002 "/uploads/flood_photo_002.jpg")
(evidence-link locust_003 "/uploads/locust_photo_003.jpg")

; GPS coordinates
(gps-coords drought_001 (3.1219 35.3781))
(gps-coords flood_002 (2.0469 37.9083))
(gps-coords locust_003 (-1.8500 36.7667))

; Timestamps
(timestamp drought_001 "2024-01-15T10:30:00Z")
(timestamp flood_002 "2024-01-14T15:45:00Z")
(timestamp locust_003 "2024-01-13T09:20:00Z")

; Economic impacts
(economic-impact drought_001 50000)
(economic-impact flood_002 35000)
(economic-impact locust_003 75000)

; Payout eligibility
(payout-eligible drought_001 0.15)
(payout-eligible flood_002 0.12)

; Helper functions for queries
(= (find-events-by-location $location)
   (match &self (location $event $location) $event))

(= (find-events-by-type $type)
   (match &self (event-type $event $type) $event))

(= (find-user-trust $user)
   (match &self (trust-score $user $score) $score))

(= (find-verified-events)
   (match &self (verified $event) $event))

(= (find-high-trust-users $threshold)
   (match &self (and (trust-score $user $score) (> $score $threshold)) $user))

(= (find-events-in-location-by-user $location $user)
   (match &self (and (location $event $location) (reports $user $event)) $event))

; Advanced query functions
(= (get-user-location $user)
   (match &self (location $user $loc) $loc))

(= (get-event-reporter $event)
   (match &self (reports $user $event) $user))

(= (calculate-location-impact $location)
   (let* (
       ($events (find-events-by-location $location))
       ($impacts (match &self (economic-impact $event $amount) $amount))
   )
   (sum $impacts)))

; Sample complex queries
(= (analyze-user-activity $user)
   (let* (
       ($trust (find-user-trust $user))
       ($location (get-user-location $user))
       ($events (match &self (reports $user $event) $event))
       ($verified_events (match &self (and (reports $user $event) (verified $event)) $event))
   )
   (user-activity-summary $user $trust $location $events $verified_events)))

; Query validation functions
(= (validate-query-result $result)
   (if (== $result ())
       (query-result "No results found")
       (query-result $result)))