; Climate Witness Chain - Verification Rules

; Main auto-verification rule
(= (auto-verify $event $user $image_confidence $desc_confidence)
   (unique(let*
        (
           ($trust_score (match &trust-space (trust-score $user $score) $score))
           ($is_qualified (>= $trust_score 60))
           ($data_qualified (and
                              (>= $image_confidence 60) ; checing the confidence of the ai model
                              (>= $desc_confidence 60)))
           ($verified (and $is_qualified $data_qualified))
        )
        $verified
     )))

; High-trust verification (for users with trust >= 80)
(= (high-trust-verify $event $user)
   (unique(let*
        (
           ($trust_score (match &trust-space (trust-score $user $score) $score))
           ($is_qualified (>= $trust_score 80))
        )
        $is_qualified
     )))



; Payout eligibility (matches our smart contract logic)
; (= (payout-eligible $event $amount)
;    (if (and (verified $event)
;             (and (impact $event $impact-type)
;                  (and (severity $event $severity-level)
;                       (payout-amount $severity-level $amount))))
;        False))

(= (payout-eligible $event $amount)
   (unique(let*
     (
           ($trust_score (match &trust-space (trust-score $user $score) $score))
           ($severity (match &event-space (severity $event $level) $level))
           ($is_severe (case $level (
                         (Critical True)
                         (High True)   
                         (Medium False)
                         (Low False)
                    )))
                    ($is_qualified (and (>= $trust_score 60)
               $is_severe))
          )
          $is_qualified
     )))
;    (eligible-for-payout $event $amount)


; Simple event correlation for economic analysis
(= (events-correlated $event1 $event2)
   (if (and (gps-coords $event1 ($lat1 $lng1))
            (and (gps-coords $event2 ($lat2 $lng2))
                 (and (< (distance $lat1 $lng1 $lat2 $lng2) 25)
                      (and (event-type $event1 $type)
                           (event-type $event2 $type)))))
       (geographically-related $event1 $event2)
       False))

; Check if user can verify events (for community verification)
(= (can-verify-events $user)
   (if (and (trust-score $user $score)
            (>= $score 60))
       (eligible-verifier $user)
       False))

; Smart contract trigger conditions
(= (trigger-micro-insurance $event)
   (if (and (verified $event)
            (and (match &self (severity $event $severity-level) $severity-level)
                 (>= $severity-level medium)))
       (insurance-triggered $event)
       False))

(= (trigger-early-warning $location $event-type)
   (if (and (event-count-in-area $location $event-type $count)
            (and (match &event-space (warning-threshold $event-type $threshold))
                 (>= $count $threshold)))
       (warning-triggered $location $event-type)
       False))

(= (trigger-dao-relief $event)
   (if (and (not (== (match &event-space (verified $event) $event) ()))
            (and (match &event-space (severity $event $severity-level) $severity-level)
                 (>= $severity-level high)))
       (dao-relief-triggered $event)
       False))