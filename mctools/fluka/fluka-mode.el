;; Generic mode for highlighting syntax for LANL's 
;; FLUKA Monte Carlo transport code input file.
;;
;; Latest version is available here:
;; https://github.com/kbat/mc-tools/blob/master/mctools/fluka/fluka-mode.el
;;
;; How to use:
;; Put -*-fluka-*- on the first line of your 
;; input file to autoload this mode (often this is the title card).
;;
;; Your .emacs file should contain something like:
;; (setq load-path (cons (expand-file-name "/path/to/your/lispdirectory") load-path))
;; (global-font-lock-mode t)
;; (load "fluka-mode")
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;  
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;  
(require 'font-lock)
(require 'generic)

(make-face 'font-lock-particle-face)
(set-face-foreground 'font-lock-particle-face "yellow")

(make-face 'font-lock-tally-face)
(set-face-foreground 'font-lock-tally-face "olive")

(make-face 'font-lock-material-face)
(set-face-foreground 'font-lock-material-face "red")

(make-face 'font-lock-transformation-face)
(set-face-foreground 'font-lock-transformation-face "yellow")

(make-face 'font-lock-skip-face)
(set-face-foreground 'font-lock-skip-face "green")
(set-face-attribute  'font-lock-skip-face nil :slant 'italic)

(make-face 'font-lock-surface-face)
(set-face-foreground 'font-lock-surface-face "red")

(make-face 'font-lock-temperature-face)
(set-face-foreground 'font-lock-temperature-face "yellow")

(make-face 'font-lock-distribution-type-face)
(set-face-foreground 'font-lock-distribution-type-face "yellow")

(make-face 'font-lock-flux2dose-face)
(set-face-foreground 'font-lock-flux2dose-face "yellow")


(define-generic-mode 'fluka-mode
  ;; comment-list (2 ways to comment in FLUKA so do below)
  nil
  ;; keyword-list (do below also)
  nil
  ;; font-lock-list (additional expressions to highlight) 
  '(
    ("^*.*" . 'font-lock-comment-face)         ;; star sign comment indicator
    ("\\<\\(BME\\|DPMJET\\|EVENTDAT\\|MYRQMD\\|OPEN\\|RQMD\\|SOURCE\\|US\\(ERDUMP\\|R\\(GCALL\\|ICALL\\|OCALL\\)\\)\\)\\>" . 'font-lock-keyword-face)
    ("\\<\\(DE\\(FAULTS\\|LTARAY\\)\\|END\\|FREE\\|G\\(LOBAL\\|EO\\(BEGIN\\|END\\)\\)\\|PLOTGEOM\\|R\\(ANDOMIZ\\|OT-DEFI\\)\\|ST\\(ART\\|OP\\)\\|TITLE\\)\\>" . 'font-lock-keyword-face)
    ("\\<\\(BIASING\\|D\\(ISCARD\\|PMJET\\)\\|E\\(M\\(F-BIAS\\|F-OFF\\|FCUT\\|FFIX\\|FFLUO\\|FRAY\\)\\|XPTRANS\\)\\|FLUKAFIX\\|HI-PROPE\\|IONFLUCT\\|L\\(AM-BIAS\\|OW-BIAS\\|OW-DOWN\\)\\|M\\(CSTHRES\\|U\\(LSOPT\\|PHOTON\\)\\)\\|OPT-PROD\\|P\\(AIRBREM\\|HOTONUC\\)\\|WW-\\(FACTO\\|PROFI\\|THRES\\)\\)\\>" . 'font-lock-keyword-face)
    ("\\<\\(BEA\\(MAXES\\|MPART\\|MPOS\\|M\\)\\|DCYTIMES\\|E\\(LCFIELD\\|MF\\|VENTYPE\\)\\|IRRPROFI\\|LOW-NEUT\\|MGNFIELD\\|P\\(ART-THR\\|HYSICS\\|OLARIZA\\)\\|RADDECAY\\)\\|STEPSIZE\\|T\\(HRESHOL\\|IME-CUT\\)\\>" . 'font-lock-keyword-face)
    ("\\<\\(^\\(ARB\\|BOX\\|ELL\\|PLA\\|R\\(AW\\|CC\\|EC\\|PP\\)\\|SPH\\|TRC\\|WED\\|X\\(CC\\|EC\\|YP\\|ZP\\)\\|Y\\(CC\\|EC\\|ZP\\)\\|Z\\(CC\\|EC\\)\\|QUA\\)\\)\\>" . 'font-lock-surface-face)
    ("\\<\\(AUXSCORE\\|D\\(CYSCORE\\|ETECT\\)\\|EVENTBIN\\|R\\(ESNUCLE\\|OTPRBIN\\)\\|SCORE\\|TCQUENCH\\|US\\(ERWEIG\\|\\(R\\(B\\(DX\\|IN\\)\\|COLL\\|TRACK\\|YIELD\\)\\)\\)\\)\\>" . 'font-lock-tally-face)
    ("\\<\\(ASSIGNMAT\\|MATERIAL\\)\\>" . 'font-lock-material-face)
    ("\\<\\(CO\\(MPOUND\\|RRFACT\\)\\|LOW-MAT\\|MAT-PROP\\|OPT-PROP\\|STERNHEI\\)\\>" . 'font-lock-material-face)
    ("\\<\\(ALL-PART\\|DOSE-EQ\\|NEUTRON\\|PHOTON\\)\\>" . 'font-lock-particle-face)
    ("\\<\\(EAP74\\|ERT74\\|EWT74\\|EAPMP\\|ERTMP\\|EWTMP\\|AMB74\\|AMBGS\\)\\>" . 'font-lock-flux2dose-face)
    )
  ;; auto-mode-list  (filename extension to autoload mode e.g.'(".mcn\\'"))
  '("inp\\'")
  ;; function-list
  nil
  ;; description
  "Generic mode for FLUKA input files."
  )

;; test a tool tip - does not work
;;(insert (propertize "foo\n" 'help-echo "Tooltip!"))

;; add a tooltip to every instance of foobar
;; http://kitchingroup.cheme.cmu.edu/blog/2013/04/12/Tool-tips-on-text-in-Emacs/
;; kbat: it works, but how to call it automatically?
(save-excursion  ;return cursor to current-point
  (goto-char 1)
  (while (search-forward "foobar" (point-max) t)
    (set-text-properties  (match-beginning 0) (match-end 0)
			  `(help-echo "You know... a bar for foos!"
				      font-lock-face (:foreground "dark slate gray"))
			  )
    )
  )
