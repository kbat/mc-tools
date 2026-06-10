;;; fluka-mode.el --- major mode for editing FLUKA input files. -*- coding: utf-8; lexical-binding: t; -*-

;; Copyright © 2019-2024 by Konstantin Batkov

;; Author: Konstantin Batkov (batkov at gmail.com)
;; Inspired by: http://xahlee.info/emacs/emacs/elisp_syntax_coloring.html
;; Version: 2.0
;; Created: 17 Dec 2023
;; Keywords: languages
;; Homepage: http://github.com/kbat/mc-tools

;; This file is not part of GNU Emacs.

;;; License:

;; You can redistribute this program and/or modify it under the terms
;; of this license:
;; https://github.com/kbat/mc-tools/blob/master/LICENSE

;; Commentary:
;; In order to autoload this mode for the *.inp files
;; your .emacs configuration file should contain something like:
;;
;; (autoload 'fluka-mode "/path/to/fluka-mode.el" "FLUKA Mode." t)
;; (or (assoc "\\.inp$" auto-mode-alist)
;;     (setq auto-mode-alist
;;     (cons '("\\.inp$" . fluka-mode) auto-mode-alist)))
;;
;; In order to re-evaluate this buffer after editing it: M-x eval-buffer
;; then update the mode in the input file buffer: M-x fluka-mode

;; full doc on how to use here

;;; Code:

(require 'font-lock)
(require 'generic)

(defconst fluka--field-width 10
  "Width of one fixed FLUKA input field.")

(defun fluka--make-keyword-table (keywords)
  "Return a hash table containing KEYWORDS for fixed-column matching."
  (let ((table (make-hash-table :test 'equal)))
    (dolist (keyword keywords table)
      (puthash keyword t table))))

(defun fluka--fixed-column-matcher (keyword-table)
  "Return a font-lock matcher for KEYWORD-TABLE.
Matches tokens in 10-column fields on a single line."
  (lambda (limit)
    (catch 'found
      (while (< (point) limit)
        (let ((start (point))
              (bol (line-beginning-position))
              (eol (min (line-end-position) limit)))
          (unless (or (>= start eol)
                      (eq (char-after bol) ?*))
            (let ((field-beg bol))
              (while (< field-beg eol)
                (let ((field-end (min (+ field-beg fluka--field-width) eol)))
                  (let ((token-beg field-beg)
                        (token-end field-end))
                    (while (and (< token-beg token-end)
                                (eq (char-syntax (char-after token-beg)) 32))
                      (setq token-beg (1+ token-beg)))
                    (while (and (> token-end token-beg)
                                (eq (char-syntax (char-before token-end)) 32))
                      (setq token-end (1- token-end)))
                    (when (and (>= token-beg start)
                               (< token-beg token-end)
                               (gethash (buffer-substring-no-properties token-beg token-end)
                                        keyword-table))
                      (set-match-data (list token-beg token-end))
                      (goto-char token-end)
                      (throw 'found t)))
                  (setq field-beg field-end)))))
          (forward-line 1)))
      nil)))

(make-face 'font-lock-particle-face)
(set-face-foreground 'font-lock-particle-face "yellow")

(make-face 'font-lock-tally-face)
(set-face-foreground 'font-lock-tally-face "olive")

(make-face 'font-lock-material-face)
(set-face-foreground 'font-lock-material-face "orange")

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

(make-face 'font-lock-fluence2dose-face)
(set-face-foreground 'font-lock-fluence2dose-face "yellow")

(make-face 'font-lock-preprocessor-face)
(set-face-foreground 'font-lock-preprocessor-face "green")

(make-face 'font-lock-last-face)
(set-face-foreground 'font-lock-last-face "red")

(make-face 'font-lock-startstop-face)
(set-face-foreground 'font-lock-startstop-face "red")

;; Keywords specific for the original FLUKA
(make-face 'font-lock-orig-face)
(set-face-foreground 'font-lock-orig-face "#ff0000")

;; Keywords specific for the FLUKA.CERN fork, the colour is CERN blue
(make-face 'font-lock-cern-face)
(set-face-foreground 'font-lock-cern-face "#3871a8")

;; create the list for font-lock.
;; each category of keyword is given a particular face
(setq fluka-font-lock-keywords
      (let* (
             ;; define several category of keywords
	     (keywords
	     '("BEAMSPOT" "BIASING" "BIOTOBIN" "BME" "DECAYS" "DPMJET" "DPA-ENER" "DPMTHRES" "D-D" "D-T" "CHARMDEC" "EXPTRANS" "GCR-SPE" "GCR-IONF" "GCR-AMS" "MYRQMD" "OPEN" "RQMD" "SOURCE" "SPECSOUR" "SPOTBEAM" "SPOTDIR" "SPOTPOS" "SPOTPOS" "SPORTRAN" "ERDUMP" "USRGCALL" "USRICALL" "VOXELS"
	     "USROCALL" "COMBNAME" "DEFAULTS" "DELTARAY" "ELECTNUC" "ELPO-THR" "FREE" "GLOBAL"
	     "NEGATIVE" "PLOTGEOM" "RANDOMIZ" "RANDOMIZE" "ROT-DEFI" "TITLE"
	     "DISCARD" "DPMJET" "EM-DISSO" "EMF-BIAS" "EMFF-OFF" "EMFCUT" "EMFFIX" "EMFFLUO" "EMFRAY" "EMXPTRANS"
	     "FLUKAFIX" "HI-PROPE" "IONFLUCT" "LAM-BIAS" "LIMITS" "LOW-BIAS" "LOW-DOWN" "LPBEMF" "MCSTHRES" "MULSOPT"
	     "MUMUPAIR" "MUPHOTON" "NEUTRINO" "NOPRINT" "NOUSER" "OPT-PROD" "PAIRBREM" "PEATHRES" "PHOTONUC" "PRINT" "PRPONLY"  "WW-FACTO" "WW-PROFI"
	     "WW-THRES" "BEAMAXES" "BEAMPOS" "BEAM" "COALESCE" "ELCFIELD" "EMF" "EVAPORAT" "EVENTYPE" "INEALL"
	     "INFLDCAY" "IONSPLIT" "IONTRANS" "IONBRPAI" "ISOMERS" "LAMBBREM" "LOW-NEUT" "MGNFIELD" "PART-THR" "PHO2-THR" "PHOT-THR" "PHYSICS"
	     "POLARIZA" "PROD-CUT" "QUASI-EL" "QMDTHRES" "RAD-BIOL" "STEPSIZE" "SYNC-RAD" "SYNC-RDN" "SYNC-RAS" "SYNC-RDS" "THRESHOL" "TIME-CUT"  "NEW" "OLD" "UNKNOWN" "USER" "USERDIRE" "SCRATCH" "INEPRI"))
	     (surfaces
	      '("ARB" "BOX" "ELL" "PLA" "RAW" "RCC" "REC" "RPP" "SPH" "TRC" "WED" "XCC" "XEC" "XYP"
	      "XZP" "YCC" "YEC" "YZP" "ZCC" "ZEC" "QUA"))
	     (tallies
	      '("AUXSCORE" "DCYSCORE" "DCYTIMES" "DETECT" "EVENTBIN" "EVENTDAT" "IRRPROFI" "RADDECAY"
	      "RESNUCLE" "ROTPRBIN" "SCORE" "TCQUENCH" "TPSSCORE" "USERDUMP" "USERWEIG" "USRBDX" "USRBIN" "USRCOLL"
	      "USRTRACK" "USRYIELD"))
	     (materials
	      '("56-FE" "ALUMINUM" "ARGON" "ASSIGNMA" "ASSIGNMAT" "BERYLLIU" "BLCKHOLE" "BORON-10" "BORON-11" "BORON" "CALCIUM" "CARBON" "CHLORINE" "CHROMIUM" "COBALT" "COMPOUND" "COPPER" "CORRFACT" "DEUTERIU" "endfb8r0" "GRAPHITE" "GOLD" "HELIUM" "HYDROGEN" "HYDROG-1" "IRON"  "LEAD" "LOW-MAT" "LOW-PWXS" "MANGANES" "MAGNESIU" "MATERIAL" "MAT-PROP" "MERCURY" "MOLYBDEN" "njendfb8r0" "NEODYMIU" "NICKEL" "NIOBIUM" "NITROGEN" "OPT-PROP" "OXYGEN" "OXYGE-16" "PHOSPHO" "POLYETHY" "POTASSIU" "SILICON" "SILIC-28" "SILVER"
		"SODIUM" "STERNHEI" "SULFUR" "TANTALUM" "TIN" "TITANIUM" "TSL-PWXS" "TUNGSTEN" "VACUUM" "VANADIUM" "WATER" "ZINC"))
	     (defaults
	       '("CALORIME" "DAMAGE" "EET/TRAN" "EM-CASCA" "ICARUS" "HADROTHE" "NEUTRONS" "NEW-DEFA" "PRECISIO" "PRECISION" "SHIELDIN" "SHIELDING"))
	     (particles
	      '("4-HELIUM" "ALL-PART" "ANNIHRST" "BEAMPART" "DOSAVLET" "DOSE" "DOSE-EQ" "DPA-SCO" "E+E-GAMM" "ELECTRON" "EM-ENRGY" "ENERGY" "HAD-CHAR" "HEAVYION" "HVY-IONS" "ISOTOPE"  "LGH-IONS" "MUONS" "MUON+" "MUON-" "NEUTRON" "OPTIPHOT" "PIONS+-" "POSITRON" "PHOTON" "PROTON" "ALPHA-D" "SQBETA-D"))
	     (fluence2dose
	      '("AMB74" "AMBDS" "AMBGS" "EAP116" "EAP74" "EIS116" "EPA116" "ERT74" "EWT74" "EAPMP"
	      "ERTMP" "EWTMP"))
	     (preprocessor
	      '("if" "elif" "else" "endif" "define" "$end_transform" "$end_translat" "$start_transform" "$start_translat"))
	     (last
	      '("LASTMAT" "LASTPAR" "LASTREG"))

	     (cern
	      '("PROFILE" "SYRASTEP" "KILL"))

	     (orig
	      '("BMAX-REG" "DELAYNEU" "INVCOMPT" "NIEL-PFN" "PWXSTEMP" "RUNGKUTT" "SYNCRAD" "SYNCROFF" "SYNCRON" "SYPRONLY" "N-REFLEC" "X-REFLEC" "USRPOINT" "POINTREG" ))

	     (startstop
	      '("END" "GEOBEGIN" "GEOEND" "START" "STOP"))

            ;; generate regex string for each category of keywords
            (keywords-matcher (fluka--fixed-column-matcher
                               (fluka--make-keyword-table keywords)))
            (surfaces-regexp (regexp-opt surfaces 'words))
            (tallies-matcher (fluka--fixed-column-matcher
                              (fluka--make-keyword-table tallies)))
            (materials-matcher (fluka--fixed-column-matcher
                                (fluka--make-keyword-table materials)))
            (particles-matcher (fluka--fixed-column-matcher
                                (fluka--make-keyword-table particles)))
            (fluence2dose-matcher (fluka--fixed-column-matcher
                                   (fluka--make-keyword-table fluence2dose)))
            (defaults-matcher (fluka--fixed-column-matcher
                               (fluka--make-keyword-table defaults)))
            (preprocessor-matcher (fluka--fixed-column-matcher
                                   (fluka--make-keyword-table preprocessor)))
            (last-matcher (fluka--fixed-column-matcher
                           (fluka--make-keyword-table last)))
            (orig-matcher (fluka--fixed-column-matcher
                           (fluka--make-keyword-table orig)))
            (cern-matcher (fluka--fixed-column-matcher
                           (fluka--make-keyword-table cern)))
            (startstop-matcher (fluka--fixed-column-matcher
                                (fluka--make-keyword-table startstop)))
	    )

        `(
	  ("^\\*.*" . 'font-lock-comment-face)
          (,keywords-matcher 0 'font-lock-keyword-face)
          (,surfaces-regexp . 'font-lock-surface-face)
          (,tallies-matcher 0 'font-lock-tally-face)
          (,materials-matcher 0 'font-lock-material-face)
          (,particles-matcher 0 'font-lock-particle-face)
          (,fluence2dose-matcher 0 'font-lock-fluence2dose-face)
          (,defaults-matcher 0 'font-lock-defaults-face)
          (,preprocessor-matcher 0 'font-lock-preprocessor-face)
          (,last-matcher 0 'font-lock-last-face)
          (,orig-matcher 0 'font-lock-orig-face)
          (,cern-matcher 0 'font-lock-cern-face)
          (,startstop-matcher 0 'font-lock-startstop-face)
          ;; note: order above matters, because once colored, that part won't change.
          ;; in general, put longer words first
          )))

;; test a tool tip - does not work
;;(insert (propertize "foo\n" 'help-echo "Tooltip!"))

;; add a tooltip to every instance of foobar
;; http://kitchingroup.cheme.cmu.edu/blog/2013/04/12/Tool-tips-on-text-in-Emacs/
;; It works, but how to call it automatically?
(save-excursion  ;return cursor to current-point
  (goto-char 1)
  (while (search-forward "foobar" (point-max) t)
    (set-text-properties  (match-beginning 0) (match-end 0)
			  `(help-echo "You know... a bar for foos!"
				      font-lock-face (:foreground "dark slate gray"))
			  )
    )
  )


;;; Vertical lines to separate WHATs
;;; Currently, a copy of https://www.emacswiki.org/emacs/column-marker.el
;;; to avoid depending on additional external file, but the intention is to simplify it
;;; as much as possible and better adapt for the FLUKA syntax
;;; (for example, avoid separators in the comment lines).

(defface column-marker-1 '((t (:background "#252525"))) ; my background is #303030
  "Face used for WHAT separators.  Usually close to the background color."
  :group 'faces)

(defvar column-marker-1-face 'column-marker-1
    "Face used for WHAT separators. Changing this directly affects only new separators.")

(defface column-marker-last '((t (:background "red")))
  "Face used for the last column."
  :group 'faces)

(defvar column-marker-last-face 'column-marker-last
    "Face used for the last column")

(defvar column-marker-vars ()
  "List of all internal column-marker variables")
(make-variable-buffer-local 'column-marker-vars) ; Buffer local in all buffers.

(defmacro column-marker-create (var &optional face)
  "Define a column marker named VAR.
FACE is the face to use.  If nil, then face `column-marker-1' is used."
  (setq face (or face 'column-marker-1))
  `(progn
     ;; define context variable ,VAR so marker can be removed if desired
     (defvar ,var ()
       "Buffer local. Used internally to store column marker spec.")
     ;; context must be buffer local since font-lock is
     (make-variable-buffer-local ',var)
     ;; Define wrapper function named ,VAR to call `column-marker-internal'
     (defun ,var (arg)
       ,(concat "Highlight column with face `" (symbol-name face)
                "'.\nWith no prefix argument, highlight current column.\n"
                "With non-negative numeric prefix arg, highlight that column number.\n"
                "With plain `C-u' (no number), turn off this column marker.\n"
                "With `C-u C-u' or negative prefix arg, turn off all column-marker highlighting.")
       (interactive "P")
       (unless (memq ',var column-marker-vars) (push ',var column-marker-vars))
       (cond ((null arg)          ; Default: highlight current column.
              (column-marker-internal ',var (1+ (current-column)) ,face))
             ((consp arg)
              (if (= 4 (car arg))
                  (column-marker-internal ',var nil) ; `C-u': Remove this column highlighting.
                (dolist (var column-marker-vars)
                  (column-marker-internal var nil)))) ; `C-u C-u': Remove all column highlighting.
             ((and (integerp arg) (>= arg 0)) ; `C-u 70': Highlight that column.
              (column-marker-internal ',var (1+ (prefix-numeric-value arg)) ,face))
             (t           ; `C-u -40': Remove all column highlighting.
              (dolist (var column-marker-vars)
                (column-marker-internal var nil)))))))

(defun column-marker-find (col)
  "Defines a function to locate a character in column COL.
Returns the function symbol, named `column-marker-move-to-COL'."
  (let ((fn-symb  (intern (format "column-marker-move-to-%d" col))))
    (fset `,fn-symb
          `(lambda (end)
             (let ((start (point)))
               (when (> end (point-max)) (setq end (point-max)))

               ;; Try to keep `move-to-column' from going backward, though it still can.
               (unless (< (current-column) ,col) (forward-line 1))

               ;; Again, don't go backward.  Try to move to correct column.
               (when (< (current-column) ,col) (move-to-column ,col))

               ;; If not at target column, try to move to it.
               (while (and (< (current-column) ,col) (< (point) end)
                           (= 0 (+ (forward-line 1) (current-column)))) ; Should be bol.
                 (move-to-column ,col))

               ;; If at target column, not past end, and not prior to start,
               ;; then set match data and return t.  Otherwise go to start
               ;; and return nil.
               (if (and (= ,col (current-column)) (<= (point) end) (> (point) start))
                   (progn (set-match-data (list (1- (point)) (point)))
                          t)            ; Return t.
                 (goto-char start)
                 nil))))                ; Return nil.
    fn-symb))

(defun column-marker-internal (sym col &optional face)
  "SYM is the symbol for holding the column marker context.
COL is the column in which a marker should be set.
Supplying nil or 0 for COL turns off the marker.
FACE is the face to use.  If nil, then face `column-marker-1' is used."
  (setq face (or face 'column-marker-1))
  (when (symbol-value sym)   ; Remove any previously set column marker
    (font-lock-remove-keywords nil (symbol-value sym))
    (set sym nil))
  (when (or (listp col) (< col 0)) (setq col nil)) ; Allow nonsense stuff to turn off the marker
  (when col                             ; Generate a new column marker
    (set sym `((,(column-marker-find col) (0 ',face prepend t))))
    (font-lock-add-keywords nil (symbol-value sym) t))
  (font-lock-fontify-buffer))

;; If you need more markers you can create your own similarly.
;; All markers can be in use at once, and each is buffer-local,
;; so there is no good reason to define more unless you need more
;; markers in a single buffer.
(column-marker-create column-marker-1 column-marker-1-face)
(column-marker-create column-marker-2 column-marker-1-face)
(column-marker-create column-marker-3 column-marker-1-face)
(column-marker-create column-marker-4 column-marker-1-face)
(column-marker-create column-marker-5 column-marker-1-face)
(column-marker-create column-marker-6 column-marker-1-face)
(column-marker-create column-marker-7 column-marker-1-face)
(column-marker-create column-marker-8 column-marker-last-face)

;;(require 'column-marker)
(add-hook 'fluka-mode-hook (lambda () (interactive) (column-marker-1 10)))
(add-hook 'fluka-mode-hook (lambda () (interactive) (column-marker-2 20)))
(add-hook 'fluka-mode-hook (lambda () (interactive) (column-marker-3 30)))
(add-hook 'fluka-mode-hook (lambda () (interactive) (column-marker-4 40)))
(add-hook 'fluka-mode-hook (lambda () (interactive) (column-marker-5 50)))
(add-hook 'fluka-mode-hook (lambda () (interactive) (column-marker-6 60)))
(add-hook 'fluka-mode-hook (lambda () (interactive) (column-marker-7 70)))
(add-hook 'fluka-mode-hook (lambda () (interactive) (column-marker-8 80)))


;;;###autoload
(define-derived-mode fluka-mode fundamental-mode "FLUKA mode"
  "Major mode for editing FLUKA input files"

  ;; FLUKA input uses `*` at the start of a line for comments.
  (setq-local comment-start "*")
  (setq-local comment-start-skip "^\\*\\s-*")
  (setq-local comment-end "")
  (setq-local comment-use-syntax nil)


  ;; code for syntax highlighting
  (setq font-lock-defaults '((fluka-font-lock-keywords))))

;; add the mode to the `features' list
(provide 'fluka-mode)

;;; fluka-mode.el ends here
