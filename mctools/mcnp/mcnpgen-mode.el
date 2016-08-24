;; Generic mode for highlighting syntax for LANL's 
;; MCNP Monte Carlo transport code input file.
;;
;; Latest version is available here:
;; https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/mcnpgen-mode.el
;;
;; How to use:
;; Put -*-mcnpgen-*- on the first line of your 
;; input file to autoload this mode (often this is the title card).
;;
;; Your .emacs file should contain something like:
;; (setq load-path (cons (expand-file-name "/path/to/your/lispdirectory") load-path))
;; (global-font-lock-mode t)
;; (load "mcnpgen-mode")
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

(make-face 'font-lock-pstudy-face)
(set-face-foreground 'font-lock-pstudy-face "yellow")


(define-generic-mode 'mcnpgen-mode
  ;; comment-list (2 ways to comment in MCNP so do below)
  nil
  ;; keyword-list (do below also)
  nil
  ;; font-lock-list (additional expressions to highlight) 
  '(
    ;; PSTUDY variable definition
    ("@@@ .*" . 'font-lock-pstudy-face)
    ("^[Cc] " . 'font-lock-comment-face)   ;; to be able to colour PSTUDY after the space
    ("^[Cc] .*" . 'font-lock-comment-face)    ;; a "c" followed by a blank in
    ("^ [Cc] .*" . 'font-lock-comment-face)   ;; columns 1-5 is a comment line
    ("^  [Cc] .*" . 'font-lock-comment-face)  ;; (the reg exp \{n,m\} does not
    ("^   [Cc] .*" . 'font-lock-comment-face) ;; seem to work here)
    ("^    [Cc] .*" . 'font-lock-comment-face)
    ("$.*" . 'font-lock-comment-face)         ;; dollar sign comment indicator
    ("\\<\\(axs\\|cel\\|cut\\|dbcn\\|dir\\|eff\\|erg\\|ext\\|hlib\\|imp\\|kcode\\|^lc[abc]\\|^le[ab]\\|lost\\|mode\\|model\\|nps\\|nrm\\|par\\|phys\\|pnlib\\|pos\\|prdmp\\|res\\|rdum\\|print\\|ptrac\\|rad\\|rand\\|seed\\|sdef\\|stop\\|tme\\|tr\\|vec\\|void\\|vol\\|wgt\\|[^cpks/]x\\|[^cpks/]y\\|[^cpks/]z\\)\\>" . 'font-lock-keyword-face)
    ("\\<\\(AXS\\|CEL\\|CUT\\|DBCN\\|DIR\\|EFF\\|ERG\\|EXT\\|HLIB\\|IMP\\|KCODE\\|^LC[ABC]\\|^LE[AB]\\|LOST\\|MODE\\|MODEL\\|NPS\\|NRM\\|PAR\\|PHYS\\|PNLIB\\|POS\\|PRDMP\\|RES\\|RDUM\\|PRINT\\|PTRAC\\|RAD\\|RAND\\|SEED\\|SDEF\\|STOP\\|TME\\|TR\\|VEC\\|VOID\\|VOL\\|WGT\\|[^CPKS/]X\\|[^CPKS/]Y\\|[^CPKS/]Z\\)\\>" . 'font-lock-keyword-face)

    ("\\<\\(^s[ipb][0-9]+\\|^ds[0-9]+\\)\\>" . 'font-lock-keyword-face) ;; distributions
    ("\\<\\(^S[IPB][0-9]+\\|^DS[0-9]+\\)\\>" . 'font-lock-keyword-face) ;; distributions

    ("\\<\\(buffer\\|but\\|cell\\|d[0-9]+\\|dose [0-9]\\|event\\|fcel d[0-9]+\\|file\\|fill\\|filter\\|freq\\|ftme\\|like\\|max\\|meph\\|plot\\|surface\\|tally\\|traks\\|trcl\\|type\\|write\\|ulat\\)\\>" . 'font-lock-variable-name-face)

    ("\\<\\(BUFFER\\|BUT\\|CELL\\|D[0-9]+\\|DOSE [0-9]\\|EVENT\\|FCEL D[0-9]+\\|FILE\\|FILL\\|FILTER\\|FREQ\\|FTME\\|LIKE\\|MAX\\|MEPH\\|PLOT\\|SURFACE\\|TALLY\\|TRAKS\\|TRCL\\|TYPE\\|WRITE\\|ULAT\\)\\>" . 'font-lock-variable-name-face)
    
    ("[:=][|/hHnNpPzZ#]" . 'font-lock-particle-face) ;; particles

    ("\\<\\(^COR[ABC][0-9]+\\|^CMESH[0-9]+\\|^DXT\\|ENDMD\\|ERGSH[0-9]+\\|^[EF][0-9]+\\|^F[QST][0-9]+\\|^HISTP\\|MSHMF[0-9]+\\|^RMESH[0-9]+\\|^SD[0-9]+\\|^SSW\\|TMESH\\)\\>" . 'font-lock-tally-face)
    ("\\<\\(^cor[abc][0-9]+\\|^cmesh[0-9]+\\|^dxt\\|endmd\\|ergsh[0-9]+\\|^[ef][0-9]+\\|^f[qst][0-9]+\\|^histp\\|mshmf[0-9]+\\|^rmesh[0-9]+\\|^sd[0-9]+\\|^ssw\\|tmesh\\)\\>" . 'font-lock-tally-face)
    ("^+?[fF][0-9]+" . 'font-lock-tally-face) ;; +tallies

    ("^FC[0-9]+ .*" . 'font-lock-comment-face) ;; +TALLY COMMENT
    ("^fc[0-9]+ .*" . 'font-lock-comment-face) ;; +tally comment


    ("\\<\\(^M[TX]?[0-9]+\\|^AWTAB\\)\\>" . 'font-lock-material-face) ;; MATERIALS
    ("\\<\\(^m[tx]?[0-9]+\\|^awtab\\)\\>" . 'font-lock-material-face) ;; materials
    
    ("^\*?[Tt][Rr][0-9]+" . 'font-lock-transformation-face) ;; transformations
    (" trans [0-9]+" . 'font-lock-transformation-face) ;; transformations
    (" TRANS [0-9]+" . 'font-lock-transformation-face) ;; transformations
    
    ("\\<\\([0-9]*[jJrRiI]\\|[0-9]+log\\)\\>" . 'font-lock-skip-face) ;; skips, e.g "1 3j 10"
    
    ;; surfaces:
    ("\\<\\([CKPST][XYZ]\\|C/[XYZ]\\|SQ\\|SUR\\|SO\\|P\\)\\>" . 'font-lock-surface-face)
    ("\\<\\([ckpst][xyz]\\|c/[xyz]\\|sq\\|sur\\|so\\|p\\)\\>" . 'font-lock-surface-face)

    ;; temperatures
    ("\\<\\([tT][mM][pP]=[0-9.eE]+-?[0-9]*\\)\\>" . 'font-lock-temperature-face)

    ;; distribution types
    (" [lLdDsS] " . 'font-lock-distribution-type-face)
    )
  ;; auto-mode-list  (filename extension to autoload mode e.g.'(".mcn\\'"))
  '("inp\\'")
  ;; function-list
  nil
  ;; description
  "Generic mode for MCNP input files."
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
