;; Generic mode for highlighting syntax for LANL's
;; MCNP Monte Carlo transport code input file.
;;
;; Latest version is available here:
;; https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/mcnpgen-mode.el
;; Based on http://homepages.cae.wisc.edu/~bohm/mcnpgen-mode.el
;;
;; How to use:
;; Put -*-mcnpgen-*- on the first line of your
;; input file to autoload this mode (often this is the title card).
;;
;; Your .emacs file should contain something like:
;; (setq load-path (cons (expand-file-name "/path/to/your/lispdirectory") load-path))
;; (global-font-lock-mode t)
;; (load "mcnpgen-mode")
;;
;; Reload mcnpgen-mode.el after editing it: M-x eval-buffer
;; followed by M-x mcnpgen-mode in the MCNP deck
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

(make-face 'font-lock-title-face)
(set-face-foreground 'font-lock-title-face "red")
(set-face-attribute  'font-lock-title-face nil :slant 'italic)

(make-face 'font-lock-temperature-face)
(set-face-foreground 'font-lock-temperature-face "yellow")

(make-face 'font-lock-distribution-type-face)
(set-face-foreground 'font-lock-distribution-type-face "yellow")

(make-face 'font-lock-pstudy-face)
(set-face-foreground 'font-lock-pstudy-face "yellow")

(make-face 'font-lock-wwg-face)
(set-face-foreground 'font-lock-wwg-face "orange")


(define-generic-mode 'mcnpgen-mode
  ;; comment-list (2 ways to comment in MCNP so do below)
  nil
  ;; keyword-list (do below also)
  nil
  ;; font-lock-list (additional expressions to highlight)
  '(
    ;; PSTUDY variable definition
    ("c @@@ .*" . 'font-lock-pstudy-face)
    ("^c$" . 'font-lock-comment-face)
    ("^c .*" . 'font-lock-comment-face)    ;; a "c" followed by a blank in
    ("^ c .*" . 'font-lock-comment-face)   ;; columns 1-5 is a comment line
    ("^  c .*" . 'font-lock-comment-face)  ;; (the reg exp \{n,m\} does not
    ("^   c .*" . 'font-lock-comment-face) ;; seem to work here)
    ("^    c .*" . 'font-lock-comment-face)
    ("$.*" . 'font-lock-comment-face)         ;; dollar sign comment indicator

    ;; tally comments go before keywords so that tally comment with a keyword is highlighted correctly
    ("^fc[0-9]+ .*" . 'font-lock-comment-face) ;; +tally comment

    ("\\<\\(ara\\|axs\\|cap\\|cel\\|ctme\\|cut\\|cyl\\|dbcn\\|dir\\|eff\\|elc\\|erg\\|ext\\|flux\\|frv\\|geb\\|hlib\\|icd\\|imp\\|inc\\|kcode\\|^lc[abc]\\|^le[abt]\\|lost\\|mgopt +[af]\\|mode\\|model\\|mphys\\|nps\\|nrm\\|par\\|phys\\|pnlib\\|pos\\|prdmp\\|rec\\|res\\|rdum\\|roc\\|phl\\|print\\|ptrac\\|psc=[0-9]\\|ptt\\|rad\\|rand\\|res\\|seed\\|scd\\|scx\\|sdef\\|stop\\|ssr\\|tag\\|tme\\|tmc\\|xvec\\|vec\\|void\\|wgt\\|[^cpks/]x\\|[^cpks/]y\\|[^cpks/]z\\)\\>" . 'font-lock-keyword-face)

    ;; Data cards related to geometry
    ("\\<\\(area\\|fill\\|lat\\|u\\|uran\\|vol\\|\\>" . 'font-lock-keyword-face)
    (" trans [0-9]+" . 'font-lock-transformation-face)
    ("^*?trcl[0-9]+" . 'font-lock-transformation-face)
    ("^*?tr[0-9]+" . 'font-lock-transformation-face)

    ("\\<\\(buffer\\|but\\|cell\\|d[0-9]+\\|dose [0-9]\\|event\\|fcel d[0-9]+\\|file\\|filter\\|freq\\|ftme\\|like\\|max\\|meph\\|plot\\|surface\\|tally\\|traks\\|type\\|write\\|ulat\\)\\>" . 'font-lock-variable-name-face)

    ("[:= ]\\([|/hnpz#]\\)[\n \,=]" . 'font-lock-particle-face) ;; particles
    ;;("<h1>\\([^<]+?\\)</h1>" . 'font-lock-particle-face)

    ("\\<\\(^cor[abc][0-9]+\\|^cmesh[0-9]+\\|^dxt\\|endmd\\|ergsh[0-9]+\\|^[eft][0-9]+\\|^em[0-9]+\\|^f[qstu][0-9]+\\|^histp\\|mshmf[0-9]+\\|^rmesh[0-9]+\\|^sd[0-9]+\\|^ssw\\|^tf[0-9]\\|tmesh\\)\\>" . 'font-lock-tally-face)
    ("^+?fm?[0-9]+" . 'font-lock-tally-face) ;; +tallies
    ("^*?c[0-9]+" . 'font-lock-tally-face) ;; *tallies
    (" f[0-9]+ " . 'font-lock-tally-face) ;; e.g. " f4 "

    ;; Variance reduction
    ("^mesh" . 'font-lock-wwg-face)
    (" geom" . 'font-lock-keyword-face)
    (" ref" . 'font-lock-keyword-face)
    (" origin" . 'font-lock-keyword-face)
    ("[ijk]mesh" . 'font-lock-keyword-face)
    ("[ijk]ints" . 'font-lock-keyword-face)
    ("^wwge" . 'font-lock-wwg-face)
    ("^ww[gp]" . 'font-lock-wwg-face)


    ("\\<\\(^m[tx]?[0-9]+\\|^awtab\\)\\>" . 'font-lock-material-face) ;; materials

    ("\\<\\([0-9]*[jJrRiI]\\|[0-9]+i?log\\)\\>" . 'font-lock-skip-face) ;; skips, e.g "1 3j 10"

    ;; surfaces:
    ("\\<\\([ckpst][xyz]\\|c/[xyz]\\|gq\\|sq\\|sur\\|so\\|p\\)\\>" . 'font-lock-surface-face)

    ;; temperatures
    ("\\<\\(tmp=[0-9.e]+-?[0-9]*\\)\\>" . 'font-lock-temperature-face)

    ;; distribution types
    (" [lds] " . 'font-lock-distribution-type-face)
    ("\\<\\(^s[ipb][0-9]+\\|^ds[0-9]+\\)\\>" . 'font-lock-distribution-type-face) ;; distributions

    )
  ;; auto-mode-list  (filename extension to autoload mode e.g.'(".mcn\\'"))
  '("inp\\'")
  ;; function-list
  nil
  ;; description
  "Generic mode for MCNP input files."
  )

;; case-insensitive keyword search
(defun case-insensitive-advice ()
  (set (make-local-variable 'font-lock-keywords-case-fold-search) t))
(advice-add 'mcnpgen-mode :after #'case-insensitive-advice)

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
