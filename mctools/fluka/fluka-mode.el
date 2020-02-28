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

(make-face 'font-lock-defaults-face)
(set-face-foreground 'font-lock-defaults-face "red")
(set-face-attribute  'font-lock-defaults-face nil :weight 'bold)

(make-face 'font-lock-surface-face)
(set-face-foreground 'font-lock-surface-face "red")

(make-face 'font-lock-temperature-face)
(set-face-foreground 'font-lock-temperature-face "yellow")

(make-face 'font-lock-distribution-type-face)
(set-face-foreground 'font-lock-distribution-type-face "yellow")

(make-face 'font-lock-flux2dose-face)
(set-face-foreground 'font-lock-flux2dose-face "yellow")

(make-face 'font-lock-preprocessor-face)
(set-face-foreground 'font-lock-preprocessor-face "green")


(define-generic-mode 'fluka-mode
  ;; comment-list (2 ways to comment in FLUKA so do below)
  nil
  ;; keyword-list (do below also)
  nil
  ;; font-lock-list (additional expressions to highlight)
  '(
    ("^*.*" . 'font-lock-comment-face)         ;; star sign comment indicator
    ("\\<\\(BME\\|DPMJET\\|MYRQMD\\|OPEN\\|RQMD\\|SOURCE\\|ERDUMP\\|USRGCALL\\|USRICALL\\|USROCALL\\)\\>" . 'font-lock-keyword-face)
    ("\\<\\(COMBNAME\\|DEFAULTS\\|DELTARAY\\|ELECTNUC\\|ELPO-THR\\|END\\|FREE\\|GLOBAL\\|GEOBEGIN\\|GEOEND\\|PLOTGEOM\\|RANDOMIZE\\|ROT-DEFI\\|START\\|STOP\\|TITLE\\)\\>" . 'font-lock-keyword-face)
    ("\\<\\(BIASING\\|DISCARD\\|DPMJET\\|EMF-BIAS\\|EMFF-OFF\\|EMFCUT\\|EMFFIX\\|EMFFLUO\\|EMFRAY\\|EMXPTRANS\\|FLUKAFIX\\|HI-PROPE\\|IONFLUCT\\|LAM-BIAS\\|LOW-BIAS\\|LOW-DOWN\\|MCSTHRES\\|MULSOPT\\|MUMUPAIR\\|MUPHOTON\\|OPT-PROD\\|PAIRBREM\\|PHOTONUC\\|WW-FACTO\\|WW-PROFI\\|WW-THRES\\)\\>" . 'font-lock-keyword-face)
    ("\\<\\(BEAMAXES\\|BEAMPART\\|BEAMPOS\\|BEAM\\|DCYTIMES\\|ELCFIELD\\|EMF\\|EVENTYPE\\|IRRPROFI\\|LAMBBREM\\|LOW-NEUT\\|MGNFIELD\\|PART-THR\\|PHO2-THR\\|PHOT-THR\\|PHYSICS\\|POLARIZA\\|PROD-CUT\\|RADDECAY\\|STEPSIZE\\|THRESHOL\\|TIME-CUT\\)\\>" . 'font-lock-keyword-face)

    ("\\<\\(^\\(ARB\\|BOX\\|ELL\\|PLA\\|R\\(AW\\|CC\\|EC\\|PP\\)\\|SPH\\|TRC\\|WED\\|X\\(CC\\|EC\\|YP\\|ZP\\)\\|Y\\(CC\\|EC\\|ZP\\)\\|Z\\(CC\\|EC\\)\\|QUA\\)\\)\\>" . 'font-lock-surface-face)
    ("\\<\\(AUXSCORE\\|DCYSCORE\\|DETECT\\|EVENTBIN\\|EVENTDAT\\|RESNUCLE\\|ROTPRBIN\\|SCORE\\|TCQUENCH\\|USERWEIG\\|USRBDX\\|USRBIN\\|USRCOLL\\|USRTRACK\\|USRYIELD\\)\\>" . 'font-lock-tally-face)

    ("\\<\\(ASSIGNMAT\\|MATERIAL\\)\\>" . 'font-lock-material-face)
    ("\\<\\(COMPOUND\\|CORRFACT\\|LOW-MAT\\|MAT-PROP\\|OPT-PROP\\|STERNHEI\\)\\>" . 'font-lock-material-face)

    ("\\<\\(ALL-PART\\|DOSE-EQ\\|ELECTRON\\|ENERGY\\|NEUTRON\\|PHOTON\\|PROTON\\)\\>" . 'font-lock-particle-face)
    ("\\<\\(EAP74\\|ERT74\\|EWT74\\|EAPMP\\|ERTMP\\|EWTMP\\|AMB74\\|AMBGS\\)\\>" . 'font-lock-flux2dose-face)

    ("\\<\\(CALORIME\\|EET\/TRANS\\|EM-CASCA\\|ICARUS\\|HADRONTHE\\|NEW-DEFA\\|PRECISION\\|SHIELDING\\)\\>" . 'font-lock-defaults-face)

    ("\\<\\(if\\|elif\\|else\\|endif\\|define\\)\\>" . 'font-lock-preprocessor-face)

    )
  ;; auto-mode-list  (filename extension to autoload mode e.g.'(".mcn\\'"))
  '(".inp\\'")
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
