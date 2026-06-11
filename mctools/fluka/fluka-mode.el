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
(require 'jit-lock)

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
		"SODIUM" "STERNHEI" "SULFUR" "TANTALUM" "TIN" "TITANIUM" "TSL-PWXS" "TUNGSTEN" "VACUUM" "VANADIUM" "WATER" "YTTRIUM" "ZINC"))
	     (defaults
	       '("CALORIME" "DAMAGE" "EET/TRAN" "EM-CASCA" "ICARUS" "HADROTHE" "NEUTRONS" "NEW-DEFA" "PRECISIO" "PRECISION" "SHIELDIN" "SHIELDING"))
	     (particles
	      '("4-HELIUM" "ALL-PART" "ANNIHRST" "BEAMPART" "DOSAVLET" "DOSE" "DOSE-EQ" "DPA-SCO" "E+&E-" "E+E-GAMM" "ELECTRON" "EM-ENRGY" "ENERGY" "HAD-CHAR" "HEAVYION" "HVY-IONS" "ISOTOPE"  "LGH-IONS" "MUONS" "MUON+" "MUON-" "NEUTRON" "OPTIPHOT" "PIONS+-" "POSITRON" "PHOTON" "PROTON" "ALPHA-D" "SQBETA-D" "UNB-EMEN" "UNB-ENER"))
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

(defconst fluka--column-marker-columns '(10 20 30 40 50 60 70)
  "One-based columns where FLUKA WHAT separators are displayed.")

(defconst fluka--column-marker-overlay-property 'fluka-column-marker
  "Overlay property used to identify FLUKA column marker overlays.")

(defun fluka--delete-column-marker-overlays ()
  "Delete all FLUKA column marker overlays in the current buffer."
  (remove-overlays (point-min) (point-max)
                   fluka--column-marker-overlay-property t))

(defun fluka--delete-column-marker-overlays-in-region (beg end)
  "Delete FLUKA column marker overlays between BEG and END."
  (dolist (overlay (overlays-in beg end))
    (when (overlay-get overlay fluka--column-marker-overlay-property)
      (delete-overlay overlay))))

(defun fluka--make-column-marker-overlay (beg end face)
  "Highlight BEG to END with FACE and remember the overlay."
  (let ((overlay (make-overlay beg end nil nil nil)))
    (overlay-put overlay 'face face)
    (overlay-put overlay 'priority -100)
    (overlay-put overlay fluka--column-marker-overlay-property t)
    overlay))

(defun fluka--make-column-separator-overlay (pos)
  "Display the character at POS with the FLUKA separator face."
  (let ((overlay (make-overlay pos (1+ pos) nil nil nil)))
    (overlay-put overlay 'display
                 (propertize (char-to-string (char-after pos))
                             'face column-marker-1-face))
    (overlay-put overlay fluka--column-marker-overlay-property t)
    overlay))

(defun fluka--column-marker-position (column eol)
  "Return the buffer position for one-based COLUMN, or nil past EOL."
  (save-excursion
    (move-to-column (1- column))
    (and (<= (point) eol)
         (= (current-column) (1- column))
         (point))))

(defun fluka--line-overflows-column-80-p (eol)
  "Return non-nil if the current line has non-space text at column 80 or later."
  (save-excursion
    (move-to-column 80)
    (and (< (point) eol)
         (not (string-match-p "\\`[[:space:]]*\\'"
                              (buffer-substring-no-properties (point) eol))))))

(defun fluka--virtual-column-markers (end-column)
  "Return an after-string for separators past END-COLUMN."
  (let ((string ""))
    (dolist (column fluka--column-marker-columns)
      (when (> column end-column)
        (let* ((target-column (1- column))
               (padding (- target-column end-column (length string))))
          (setq string
                (concat string
                        (make-string (max padding 0) ?\s)
                        (propertize " " 'face column-marker-1-face))))))
    (when (> (length string) 0)
      (put-text-property 0 1 'cursor t string))
    string))

(defun fluka--add-line-column-markers ()
  "Add FLUKA column marker overlays for the current line."
  (let ((eol (line-end-position)))
    (dolist (column fluka--column-marker-columns)
      (let ((pos (fluka--column-marker-position column eol)))
        (when (and pos (< pos eol))
          (fluka--make-column-separator-overlay pos))))
    (let ((end-column (save-excursion
                        (goto-char eol)
                        (current-column))))
      (when (< end-column (car (last fluka--column-marker-columns)))
        (let ((after-string (fluka--virtual-column-markers end-column)))
          (unless (string= after-string "")
            (let ((overlay (make-overlay eol eol nil t nil)))
              (overlay-put overlay 'after-string after-string)
              (overlay-put overlay fluka--column-marker-overlay-property t))))))
    (when (fluka--line-overflows-column-80-p eol)
      (save-excursion
        (move-to-column 80)
        (when (< (point) eol)
          (fluka--make-column-marker-overlay
           (point) eol column-marker-last-face))))))

(defun fluka-refresh-column-markers ()
  "Refresh FLUKA column markers in the current buffer."
  (interactive)
  (fluka--delete-column-marker-overlays)
  (save-excursion
    (goto-char (point-min))
    (while (not (eobp))
      (fluka--add-line-column-markers)
      (forward-line 1))
    (when (and (= (point) (point-max))
               (bolp))
      (fluka--add-line-column-markers))))

(defun fluka--fontify-column-markers (start end)
  "Refresh FLUKA column markers between START and END for `jit-lock'."
  (let ((beg (save-excursion
               (goto-char start)
               (line-beginning-position)))
        (finish (save-excursion
                  (goto-char end)
                  (line-end-position))))
    (fluka--delete-column-marker-overlays-in-region
     beg (min (point-max) (1+ finish)))
    (save-excursion
      (goto-char beg)
      (while (and (< (point) finish)
                  (not (eobp)))
        (fluka--add-line-column-markers)
        (forward-line 1))
      (when (and (= (point) (point-max))
                 (bolp)
                 (<= (point) finish))
        (fluka--add-line-column-markers)))
    `(jit-lock-bounds ,beg . ,finish)))


;;;###autoload
(define-derived-mode fluka-mode fundamental-mode "FLUKA mode"
  "Major mode for editing FLUKA input files"

  ;; FLUKA input uses `*` at the start of a line for comments.
  (setq-local comment-start "*")
  (setq-local comment-start-skip "^\\*\\s-*")
  (setq-local comment-end "")
  (setq-local comment-use-syntax nil)


  ;; code for syntax highlighting
  (setq font-lock-defaults '((fluka-font-lock-keywords)))

  (ignore-errors
    (jit-lock-unregister #'fluka--fontify-column-markers))
  (fluka--delete-column-marker-overlays)
  (jit-lock-register #'fluka--fontify-column-markers t))

;; add the mode to the `features' list
(provide 'fluka-mode)

;;; fluka-mode.el ends here
