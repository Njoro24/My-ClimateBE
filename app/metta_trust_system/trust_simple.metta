;; Simple MeTTa Trust Engine - Working Version

;; Constants
(= (initial-score) 50)
(= (verified-bonus) 15)
(= (false-penalty) -10)

;; Simple trust score storage using assertions
(trust-score user1 50)
(trust-score user2 65)

;; Register user function
(= (register-user $user)
   (initial-score))

;; Get trust score
(= (get-score $user)
   (if (== $user user1) 50
   (if (== $user user2) 65
   (initial-score))))

;; Update score for verified report
(= (verified-report $user)
   (let $current (get-score $user)
        (+ $current (verified-bonus))))

;; Test function
(= (test-system)
   (verified-report user1))
