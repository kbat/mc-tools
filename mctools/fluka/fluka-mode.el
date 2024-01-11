;;; fluka-mode.el --- major mode for editing FLUKA input files. -*- coding: utf-8; lexical-binding: t; -*-

;; Copyright © 2019-2023 by Konstantin Batkov

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


;; create the list for font-lock.
;; each category of keyword is given a particular face
(setq fluka-font-lock-keywords
      (let* (
             ;; define several category of keywords
	     (keywords
	     '("BIASING" "BME" "DPMJET" "MYRQMD" "OPEN" "RQMD" "SOURCE" "ERDUMP" "USRGCALL" "USRICALL"
	     "USROCALL" "COMBNAME" "DEFAULTS" "DELTARAY" "ELECTNUC" "ELPO-THR" "END" "FREE" "GLOBAL"
	     "GEOBEGIN" "GEOEND" "PLOTGEOM" "RANDOMIZ" "RANDOMIZE" "ROT-DEFI" "START" "STOP" "TITLE"
	     "DISCARD" "DPMJET" "EMF-BIAS" "EMFF-OFF" "EMFCUT" "EMFFIX" "EMFFLUO" "EMFRAY" "EMXPTRANS"
	     "FLUKAFIX" "HI-PROPE" "IONFLUCT" "LAM-BIAS" "LOW-PWXS" "LOW-BIAS" "LOW-DOWN" "MCSTHRES" "MULSOPT"
	     "MUMUPAIR" "MUPHOTON" "OPT-PROD" "PAIRBREM" "PHOTONUC" "PRINT" "SYRASTEP" "TSL-PWXS" "WW-FACTO" "WW-PROFI"
	     "WW-THRES" "BEAMAXES" "BEAMPOS" "BEAM" "COALESCE" "ELCFIELD" "EMF" "EVAPORAT" "EVENTYPE"
	     "INFLDCAY" "IONSPLIT" "IONTRANS" "ISOMERS" "LAMBBREM" "LOW-NEUT" "MGNFIELD" "PART-THR" "PHO2-THR" "PHOT-THR" "PHYSICS"
	     "POLARIZA" "PROD-CUT" "QUASI-EL" "QMDTHRES" "STEPSIZE" "THRESHOL" "TIME-CUT" "USERDUMP" "NEW" "OLD" "UNKNOWN" "SCRATCH"))
	     (surfaces
	      '("ARB" "BOX" "ELL" "PLA" "RAW" "RCC" "REC" "RPP" "SPH" "TRC" "WED" "XCC" "XEC" "XYP"
	      "XZP" "YCC" "YEC" "YZP" "ZCC" "ZEC" "QUA"))
	     (tallies
	      '("AUXSCORE" "DCYSCORE" "DCYTIMES" "DETECT" "EVENTBIN" "EVENTDAT" "IRRPROFI" "RADDECAY"
	      "RESNUCLE" "ROTPRBIN" "SCORE" "TCQUENCH" "USERWEIG" "USRBDX" "USRBIN" "USRCOLL"
	      "USRTRACK" "USRYIELD"))
	     (materials
	      '("ASSIGNMA" "ASSIGNMAT" "BLCKHOLE" "CARBON" "COMPOUND" "CORRFACT" "HYDROGEN" "LOW-MAT" "MATERIAL" "MAT-PROP" "OPT-PROP"
	      "STERNHEI" "VACUUM" "WATER"))
	     (particles
	      '("4-HELIUM" "ALL-PART" "BEAMPART" "DOSE-EQ" "ELECTRON" "ENERGY" "MUONS" "MUON+" "MUON-" "NEUTRON"
	      "OPTIPHOT" "PIONS" "PHOTON" "PROTON"))
	     (fluence2dose
	      '("AMB74" "AMBDS" "AMBGS" "EAP116" "EAP74" "EIS116" "EPA116" "ERT74" "EWT74" "EAPMP"
	      "ERTMP" "EWTMP"))
	     (defaults
	       '("CALORIME" "EM-CASCA" "ICARUS" "HADROTHE" "NEW-DEFA" "PRECISION" "SHIELDING"))
	     (preprocessor
	      '("if" "elif" "else" "endif" "define"))
	     (last
	      '("LASTMAT" "LASTPAR" "LASTREG"))

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
