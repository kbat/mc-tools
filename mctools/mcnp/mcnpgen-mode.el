;;Generic mode for highlighting syntax for LANL's 
;;MCNP Monte Carlo transport code input file.
;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;Inspired by the Tim Bohm's work
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;  
;;         How to use:
;;Put -*-mcnpgen-*- on the first line of your 
;;input file to autoload this mode (often this is the title card).
;;
;;Your .emacs file should contain something like:
;;(setq load-path (cons (expand-file-name "/path/to/your/lispdirectory") load-path))
;;(global-font-lock-mode t)
;;(load "mcnpgen-mode")
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
    ("\\<\\(axs\\|cel\\|cor[abc][0-9]+\\|cut\\|dbcn\\|dir\\|dxt\\|eff\\|endmd\\|erg\\|ext\\|imp\\|kcode\\|^lc[abc]\\|^le[ab]\\|lost\\|mode\\|model\\|mshmf[0-9]+\\|nps\\|par\\|phys\\|pos\\|prdmp\\|print\\|ptrac\\|rad\\|rmesh[0-9]+\\|sdef\\|stop\\|tme\\|tmesh\\|tr\\|vec\\|void\\|wgt\\|[^cpks/]x\\|[^cpks/]y\\|[^cpks/]z\\)\\>" . 'font-lock-keyword-face)
    ("\\<\\(AXS\\|CEL\\|COR[ABC][0-9]+\\|CUT\\|DBCN\\|DIR\\|DXT\\|EFF\\|ENDMD\\|ERG\\|EXT\\|IMP\\|KCODE\\|^LC[ABC]\\|^LE[AB]\\|LOST\\|MODE\\|MODEL\\|MSHMF[0-9]+\\|NPS\\|PAR\\|PHYS\\|POS\\|PRDMP\\|PRINT\\|PTRAC\\|RAD\\|RMESH[0-9]+\\|SDEF\\|STOP\\|TME\\|TMESH\\|TR\\|VEC\\|VOID\\|WGT\\|[^CPKS/]X\\|[^CPKS/]Y\\|[^CPKS/]Z\\)\\>" . 'font-lock-keyword-face)

    ("\\<\\(^s[ipb][0-9]+\\|^ds[0-9]+\\)\\>" . 'font-lock-keyword-face) ;; distributions
    ("\\<\\(^S[IPB][0-9]+\\|^DS[0-9]+\\)\\>" . 'font-lock-keyword-face) ;; distributions

    ("\\<\\(buffer\\|but\\|cell\\|d[0-9]+\\|dose\\|ergsh\\|event\\|fcel d[0-9]+\\|file\\|fill\\|filter\\|freq\\|ftme\\|like\\|max\\|meph\\|plot\\|surface\\|tally\\|traks\\|trcl\\|type\\|write\\|ulat\\)\\>" . 'font-lock-variable-name-face)

    ("\\<\\(BUFFER\\|BUT\\|CELL\\|D[0-9]+\\|DOSE\\|ERGSH\\|EVENT\\|FCEL D[0-9]+\\|FILE\\|FILL\\|FILTER\\|FREQ\\|FTME\\|LIKE\\|MAX\\|MEPH\\|PLOT\\|SURFACE\\|TALLY\\|TRAKS\\|TRCL\\|TYPE\\|WRITE\\|ULAT\\)\\>" . 'font-lock-variable-name-face)
    
    ("[:=][|/hHnNpPzZ]" . 'font-lock-particle-face) ;; particles

    ("\\<\\(^[eEfF][0-9]+\\|^[fF][sS][0-9]+\\|[sS][dD][0-9]+\\)\\>" . 'font-lock-tally-face) ;; tallies

    ("\\<\\(^[mM][tTxX]?[0-9]+\\)\\>" . 'font-lock-material-face) ;; materials
    ("^\*?TR[0-9]+" . 'font-lock-transformation-face) ;; transformations
    ("\\<\\([0-9]*[jJrRiI]\\|[0-9]+log\\)\\>" . 'font-lock-skip-face) ;; skips, e.g "1 3j 10"
    ;; surfaces:
    ("\\<\\([CKPST][XYZ]\\|C/[XYZ]\\|SQ\\|P\\)\\>" . 'font-lock-surface-face)
    ;; temperatures
    ("\\<\\(TMP=[0-9.E]+-?[0-9]*\\)\\>" . 'font-lock-temperature-face)
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

;; test a tool tip
(insert (propertize "foo\n" 'help-echo "Tooltip!"))
