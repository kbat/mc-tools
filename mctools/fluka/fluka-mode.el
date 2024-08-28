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

;; Keywords specific for the FLUKA.CERN fork, the colour is CERN blue
(make-face 'font-lock-cern-face)
(set-face-foreground 'font-lock-cern-face "#3871a8")

;; create the list for font-lock.
;; each category of keyword is given a particular face
(setq fluka-font-lock-keywords
      (let* (
             ;; define several category of keywords
	     (keywords
	     '("BEAMSPOT" "BIASING" "BME" "DPMJET" "D-D" "D-T" "CHARMDEC" "EXPTRANS" "MYRQMD" "OPEN" "RQMD" "SOURCE" "SPECSOUR" "SPOTBEAM" "ERDUMP" "USRGCALL" "USRICALL"
	     "USROCALL" "COMBNAME" "DEFAULTS" "DELTARAY" "ELECTNUC" "ELPO-THR" "FREE" "GLOBAL"
	     "NEGATIVE" "PLOTGEOM" "RANDOMIZ" "RANDOMIZE" "ROT-DEFI" "TITLE"
	     "DISCARD" "DPMJET" "EMF-BIAS" "EMFF-OFF" "EMFCUT" "EMFFIX" "EMFFLUO" "EMFRAY" "EMXPTRANS"
	     "FLUKAFIX" "HI-PROPE" "IONFLUCT" "LAM-BIAS" "LOW-BIAS" "LOW-DOWN" "LPBEMF" "MCSTHRES" "MULSOPT"
	     "MUMUPAIR" "MUPHOTON" "OPT-PROD" "PAIRBREM" "PHOTONUC" "PRINT" "WW-FACTO" "WW-PROFI"
	     "WW-THRES" "BEAMAXES" "BEAMPOS" "BEAM" "COALESCE" "ELCFIELD" "EMF" "EVAPORAT" "EVENTYPE"
	     "INFLDCAY" "IONSPLIT" "IONTRANS" "ISOMERS" "LAMBBREM" "LOW-NEUT" "MGNFIELD" "PART-THR" "PHO2-THR" "PHOT-THR" "PHYSICS"
	     "POLARIZA" "PROD-CUT" "QUASI-EL" "QMDTHRES" "STEPSIZE" "THRESHOL" "TIME-CUT" "NEW" "OLD" "UNKNOWN" "SCRATCH"))
	     (surfaces
	      '("ARB" "BOX" "ELL" "PLA" "RAW" "RCC" "REC" "RPP" "SPH" "TRC" "WED" "XCC" "XEC" "XYP"
	      "XZP" "YCC" "YEC" "YZP" "ZCC" "ZEC" "QUA"))
	     (tallies
	      '("AUXSCORE" "DCYSCORE" "DCYTIMES" "DETECT" "EVENTBIN" "EVENTDAT" "IRRPROFI" "RADDECAY"
	      "RESNUCLE" "ROTPRBIN" "SCORE" "TCQUENCH" "USERDUMP" "USERWEIG" "USRBDX" "USRBIN" "USRCOLL"
	      "USRTRACK" "USRYIELD"))
	     (materials
	      '("56-FE" "ALUMINUM" "ARGON" "ASSIGNMA" "ASSIGNMAT" "BERYLLIU" "BLCKHOLE" "CALCIUM" "CARBON" "CHLORINE" "CHROMIUM" "COBALT" "COMPOUND" "COPPER" "CORRFACT" "DEUTERIU" "endfb8r0" "GRAPHITE" "GOLD" "HELIUM" "HYDROGEN" "IRON" "LEAD" "LOW-MAT" "LOW-PWXS" "MANGANES" "MAGNESIU" "MATERIAL" "MAT-PROP" "MERCURY" "njendfb8r0" "NICKEL" "NITROGEN" "OPT-PROP" "OXYGEN" "OXYGE-16" "PHOSPHO" "POLYETHY" "POTASSIU" "SILICON" "SILIC-28" "SILVER"
		"SODIUM" "STERNHEI" "SULFUR" "TANTALUM" "TIN" "TITANIUM" "TSL-PWXS" "TUNGSTEN" "VACUUM" "WATER" "ZINC"))
	     (defaults
	       '("CALORIME" "DAMAGE" "EET/TRAN" "EM-CASCA" "ICARUS" "HADROTHE" "NEUTRONS" "NEW-DEFA" "PRECISIO" "PRECISION" "SHIELDIN" "SHIELDING"))
	     (particles
	      '("4-HELIUM" "ALL-PART" "ANNIHRST" "BEAMPART" "DOSE" "DOSE-EQ" "DPA-SCO" "ELECTRON" "ENERGY" "ISOTOPE" "MUONS" "MUON+" "MUON-" "NEUTRON"
	      "OPTIPHOT" "POSITRON" "PIONS" "PHOTON" "PROTON"))
	     (fluence2dose
	      '("AMB74" "AMBDS" "AMBGS" "EAP116" "EAP74" "EIS116" "EPA116" "ERT74" "EWT74" "EAPMP"
	      "ERTMP" "EWTMP"))
	     (preprocessor
	      '("if" "elif" "else" "endif" "define" "$end_transform" "$end_translat" "$start_transform" "$start_translat"))
	     (last
	      '("LASTMAT" "LASTPAR" "LASTREG"))

	     (cern
	      '("PROFILE" "SYRASTEP"))

	     (startstop
	      '("END" "GEOBEGIN" "GEOEND" "START" "STOP"))

            ;; generate regex string for each category of keywords
            (keywords-regexp (regexp-opt keywords 'words))
            (surfaces-regexp (regexp-opt surfaces 'words))
            (tallies-regexp (regexp-opt tallies 'words))
            (materials-regexp (regexp-opt materials 'words))
            (particles-regexp (regexp-opt particles 'words))
            (fluence2dose-regexp (regexp-opt fluence2dose 'words))
            (defaults-regexp (regexp-opt defaults 'words))
            (preprocessor-regexp (regexp-opt preprocessor 'words))
            (last-regexp (regexp-opt last 'words))
            (cern-regexp (regexp-opt cern 'words))
            (startstop-regexp (regexp-opt startstop 'words))
	    )

        `(
	  ("^*.*" . 'font-lock-comment-face)
          (,keywords-regexp . 'font-lock-keyword-face)
          (,surfaces-regexp . 'font-lock-surface-face)
          (,tallies-regexp . 'font-lock-tally-face)
          (,materials-regexp . 'font-lock-material-face)
          (,particles-regexp . 'font-lock-particle-face)
          (,fluence2dose-regexp . 'font-lock-fluence2dose-face)
          (,defaults-regexp . 'font-lock-defaults-face)
          (,preprocessor-regexp . 'font-lock-preprocessor-face)
          (,last-regexp . 'font-lock-last-face)
          (,cern-regexp . 'font-lock-cern-face)
          (,startstop-regexp . 'font-lock-startstop-face)
          ;; note: order above matters, because once colored, that part won't change.
          ;; in general, put longer words first
          )))

;;;###autoload
(define-derived-mode fluka-mode fundamental-mode "FLUKA mode"
  "Major mode for editing FLUKA input files"

  ;; code for syntax highlighting
  (setq font-lock-defaults '((fluka-font-lock-keywords))))

;; add the mode to the `features' list
(provide 'fluka-mode)

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

;;; fluka-mode.el ends here
