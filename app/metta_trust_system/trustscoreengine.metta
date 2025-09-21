;; Initialize knowledge base
!(bind! &kb (new-space))

!(bind! &kb (new-space))

;; Define all atom types used in the system
!(add-type &kb user)
!(add-type &kb trust-score)
!(add-type &kb status)
!(add-type &kb warnings)
!(add-type &kb verified-report)
!(add-type &kb false-report)
!(add-type &kb malicious-report)
!(add-type &kb score-change)
!(add-type &kb warning-issued)
!(add-type &kb suspension)
!(add-type &kb time-bonus)
!(add-type &kb system-initialized)
!(add-type &kb system-version)

(= (initial-trust-score) 50)
(= (max-trust-score) 100)
(= (min-trust-score) 0)
(= (verified-report-bonus) 15)
(= (false-report-penalty) -10)
(= (severe-false-penalty) -25)
(= (warning-threshold) 25)
(= (suspension-threshold) 10)


;; Register new user with initial trust score
(= (register-user $user-id)
   (let $initial-score (initial-trust-score)
        (and (add-atom &kb (user $user-id))
             (add-atom &kb (trust-score $user-id $initial-score))
             (add-atom &kb (status $user-id active))
             (add-atom &kb (warnings $user-id 0))
             $initial-score)))


(= (get-trust-score $user-id)
   (match &kb (trust-score $user-id $score) $score))

(= (get-user-status $user-id)
   (match &kb (status $user-id $status) $status))

(= (get-warning-count $user-id)
   (match &kb (warnings $user-id $count) $count))

;;TRUST SCORE CALCULATIONS
(= (calculate-new-score $current-score $delta)
   (let $new-score (+ $current-score $delta)
        (if (> $new-score (max-trust-score))
            (max-trust-score)
            (if (< $new-score (min-trust-score))
                (min-trust-score)
                $new-score))))

(= (update-trust-score $user-id $new-score)
   (and (remove-atom &kb (trust-score $user-id $_))
        (add-atom &kb (trust-score $user-id $new-score))
        $new-score))

;;REPORT VERIFICATION HANDLERS
(= (handle-verified-report $user-id $event-id)
   (let $current-score (get-trust-score $user-id)
        $bonus (verified-report-bonus)
        $new-score (calculate-new-score $current-score $bonus)
        (and (update-trust-score $user-id $new-score)
             (add-atom &kb (verified-report $user-id $event-id))
             (add-atom &kb (score-change $user-id $event-id $bonus "verified"))
             $new-score)))

(= (handle-false-report $user-id $event-id)
   (let $current-score (get-trust-score $user-id)
        $penalty (false-report-penalty)
        $new-score (calculate-new-score $current-score $penalty)
        $warning-count (get-warning-count $user-id)
        (and (update-trust-score $user-id $new-score)
             (add-atom &kb (false-report $user-id $event-id))
             (add-atom &kb (score-change $user-id $event-id $penalty "false"))
             (check-warning-needed $user-id $new-score $warning-count)
             $new-score)))

(= (handle-malicious-report $user-id $event-id)
   (let $current-score (get-trust-score $user-id)
        $penalty (severe-false-penalty)
        $new-score (calculate-new-score $current-score $penalty)
        $warning-count (get-warning-count $user-id)
        (and (update-trust-score $user-id $new-score)
             (add-atom &kb (malicious-report $user-id $event-id))
             (add-atom &kb (score-change $user-id $event-id $penalty "malicious"))
             (check-suspension-needed $user-id $new-score $warning-count)
             $new-score)))

;;WARNING AND SUSPENSION LOGIC
(= (check-warning-needed $user-id $trust-score $current-warnings)
   (if (<= $trust-score (warning-threshold))
       (issue-warning $user-id $current-warnings)
       True))

(= (issue-warning $user-id $current-warnings)
   (let $new-warning-count (+ $current-warnings 1)
        (and (remove-atom &kb (warnings $user-id $current-warnings))
             (add-atom &kb (warnings $user-id $new-warning-count))
             (add-atom &kb (warning-issued $user-id $new-warning-count))
             (if (>= $new-warning-count 3)
                 (suspend-user $user-id)
                 (update-user-status $user-id warned)))))

(= (check-suspension-needed $user-id $trust-score $current-warnings)
   (if (<= $trust-score (suspension-threshold))
       (suspend-user $user-id)
       (check-warning-needed $user-id $trust-score $current-warnings)))

(= (suspend-user $user-id)
   (and (update-user-status $user-id suspended)
        (add-atom &kb (suspension $user-id))
        suspended))

(= (update-user-status $user-id $new-status)
   (and (remove-atom &kb (status $user-id $_))
        (add-atom &kb (status $user-id $new-status))
        $new-status))

;;REPORT SUBMISSION AUTHORIZATION
(= (can-submit-report $user-id)
   (let $status (get-user-status $user-id)
        $trust-score (get-trust-score $user-id)
        (and (not (== $status suspended))
             (>= $trust-score 10))))

;;TRUST SCORE RECOVERY
(= (apply-time-bonus $user-id $days-since-last-false)
   (if (and (> $days-since-last-false 30)
            (< (get-trust-score $user-id) 50))
       (let $current-score (get-trust-score $user-id)
            $time-bonus (min 5 (/ $days-since-last-false 30))
            $new-score (calculate-new-score $current-score $time-bonus)
            (and (update-trust-score $user-id $new-score)
                 (add-atom &kb (time-bonus $user-id $time-bonus))
                 $new-score))
       (get-trust-score $user-id)))

;;INITIALIZATION
(= (init-trust-system)
   (and (add-atom &kb (system-initialized true))
        (add-atom &kb (system-version "1.0"))
        "Trust system initialized"))

;; Run initialization
!(init-trust-system)

;;TESTING FUNCTION
(= (test-user-flow)
   (let $user-id "test-user-001"
        (and (register-user $user-id)
             (handle-verified-report $user-id "event-001")
             (handle-verified-report $user-id "event-002")
             (handle-false-report $user-id "event-003")
             (get-trust-score $user-id))))
