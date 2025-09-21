; Climate Witness Chain - Helper Functions
; This file contains utility functions and mathematical operations

; Distance calculation helper (simplified Haversine formula approximation)
; For small distances, this approximation is sufficient
(= (distance $lat1 $lng1 $lat2 $lng2)
   (and (- $lat2 $lat1 $dlat)
        (- $lng2 $lng1 $dlng)
        (* $dlat $dlat $dlat2)
        (* $dlng $dlng $dlng2)
        (+ $dlat2 $dlng2 $sum)
        (sqrt $sum $distance))
   $distance)

(= (distance $lat1 $lng1 $lat2 $lng2)
   (let* (($dlat (- $lat2 $lat1))
          ($dlng (- $lng2 $lng1)))
      ((py-atom math.sqrt) (+ (* $dlat $dlat) (* $dlng $dlng)))))


; Time difference calculation (in hours)
(= (time-diff $time1 $time2)
   (and (parse-time $time1 $t1)
        (parse-time $time2 $t2)
        (- $t2 $t1 $diff)
        (abs $diff $abs-diff)
        (/ $abs-diff 3600 $hours))  ; Convert seconds to hours
   $hours)

; Check if events are within specified hours of each other
(= (within-hours $event1 $event2 $max-hours)
   (and (timestamp $event1 $time1)
        (timestamp $event2 $time2)
        (time-diff $time1 $time2 $diff)
        (<= $diff $max-hours))
   True)

; Check if two events are of the same type
(= (same-event-type $event1 $event2)
   (and (event-type $event1 $type)
        (event-type $event2 $type))
   True)

; Check if two events are at the same location (within 1km)
(= (same-location $event1 $event2)
   (and (gps-coords $event1 ($lat1 $lng1))
        (gps-coords $event2 ($lat2 $lng2))
        (distance $lat1 $lng1 $lat2 $lng2 $dist)
        (<= $dist 1))
   True)

; Check if coordinates are within a region (simplified bounding box)
(= (in-region $lat $lng $region)
   (and (region-bounds $region $min-lat $max-lat $min-lng $max-lng)
        (>= $lat $min-lat)
        (<= $lat $max-lat)
        (>= $lng $min-lng)
        (<= $lng $max-lng))
   True)

; Region bounding boxes (approximate)
(region-bounds "Turkana, Kenya" 2.5 4.5 34.5 36.5)
(region-bounds "Kajiado, Kenya" -3.0 -1.0 36.0 38.0)
(region-bounds "Marsabit, Kenya" 1.5 4.5 36.5 39.0)
(region-bounds "Samburu, Kenya" 0.5 2.5 36.0 38.5)

; Check if metadata is consistent (photo timestamp matches event timestamp)
(= (metadata-consistent $photo-link $event-time $coords)
   (and (extract-photo-time $photo-link $photo-time)
        (time-diff $event-time $photo-time $diff)
        (<= $diff 1))  ; Within 1 hour
   True)

; Trust score validation
(= (valid-trust-score $score)
   (and (>= $score 0)
        (<= $score 100))
   True)

; Calculate trust score change based on verification accuracy
(= (trust-delta $accuracy)
   (cond ((<= $accuracy 0.5) -5)     ; Poor accuracy: -5 points
         ((<= $accuracy 0.7) 0)      ; Average accuracy: no change
         ((<= $accuracy 0.9) 2)      ; Good accuracy: +2 points
         (True 5))                   ; Excellent accuracy: +5 points
   $delta)

; Severity calculation based on multiple factors
(= (calculate-severity $event-type $impact-score $area-affected)
   (cond ((and (> $impact-score 80) (> $area-affected 1000)) Critical)
         ((and (> $impact-score 60) (> $area-affected 500)) High)
         ((and (> $impact-score 40) (> $area-affected 100)) Medium)
         (True Low))
   $severity)

; Payout calculation with adjustments
(= (adjusted-payout $base-amount $trust-score $severity $region)
   (and (trust-multiplier $trust-score $trust-mult)
        (severity-multiplier $severity $sev-mult)
        (region-multiplier $region $reg-mult)
        (* $base-amount $trust-mult $temp1)
        (* $temp1 $sev-mult $temp2)
        (* $temp2 $reg-mult $final-amount))
   $final-amount)

; Multiplier functions
(= (trust-multiplier $score)
   (cond ((>= $score 90) 1.2)   ; 20% bonus for very high trust
         ((>= $score 80) 1.1)   ; 10% bonus for high trust
         ((>= $score 60) 1.0)   ; No adjustment for adequate trust
         (True 0.8))             ; 20% reduction for low trust
   $multiplier)

(= (severity-multiplier $severity)
   (cond ((= $severity Critical) 2.0)
         ((= $severity High) 1.5)
         ((= $severity Medium) 1.0)
         ((= $severity Low) 0.5))
   $multiplier)

(= (region-multiplier $region)
   (cond ((= $region "Turkana, Kenya") 1.3)    ; Higher need area
         ((= $region "Marsabit, Kenya") 1.2)   ; High need area
         ((= $region "Samburu, Kenya") 1.1)    ; Medium need area
         (True 1.0))                           ; Standard rate
   $multiplier)

; Event age validation (events should be recent)
(= (recent-event $event)
   (and (timestamp $event $time)
        (current-time $now)
        (time-diff $time $now $age-hours)
        (<= $age-hours 72))  ; Within 72 hours
   True)

; Check if user has different validators (for consensus)
(= (different $user1 $user2)
   (not (= $user1 $user2))
   True)