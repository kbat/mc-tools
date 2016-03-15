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

(define-generic-mode 'mcnpgen-mode
  ;; comment-list (2 ways to comment in MCNP so do below)
  nil
  ;; keyword-list (do below also)
  nil
  ;; font-lock-list (additional expressions to highlight) 
  '(
     ("^[Cc] .*" . 'font-lock-comment-face)    ;; a "c" followed by a blank in
     ("^ [Cc] .*" . 'font-lock-comment-face)   ;; columns 1-5 is a comment line
     ("^  [Cc] .*" . 'font-lock-comment-face)  ;; (the reg exp \{n,m\} does not
     ("^   [Cc] .*" . 'font-lock-comment-face) ;; seem to work here)
     ("^    [Cc] .*" . 'font-lock-comment-face)
     ("$.*" . 'font-lock-comment-face)         ;; dollar sign comment indicator
     ("\\<\\([mM][oO][dD][eE]\\|[iI][mM][pP]\\|[nN][pP][sS]\\|[pP][hH][yY][sS]\\|[cC][uU][tT]\\|[sS][dD][eE][fF]\\|[dD][xX][tT]\\|[lL][oO][sS][tT]\\|[pP][rR][iI][nN][tT]\\|[pP][rR][dD][mM][pP]\\|[dD][bB][cC][nN]\\|[kK][cC][oO][dD][eE]\\|[pP][tT][rR][aA][cC]\\|[sS][tT][oO][pP]\\|[vV][oO][iI][dD]\\)\\>" . 'font-lock-keyword-face) ;; mcnp keywords
     ("\\<\\([eE][rR][gG]\\|[pP][oO][sS]\\|[cC][eE][lL]\\|cor[abc][0-9]+\\|[dD][iI][rR]\\|endmd\\|mshmf[0-9]+\\|[vV][eE][cC]\\|[aA][xX][sS]\\|[rR][aA][dD]\\|rmesh[0-9]+\\|tmesh\\|[eE][xX][tT]\\|[pP][aA][rR]\\|[tT][mM][eE]\\)\\>" . 'font-lock-variable-name-face) ;; sdef variables
     ("\\<\\([fF][iI][lL][lL]\\|hello\\|[uU]\\|[lL][aA][tT]\\|[lL][iI][kK][eE]\\|[bB][uU][tT]\\|[tT][rR][cC][lL]\\)\\>" . 'font-lock-variable-name-face) ;; fill,universe,lat,trcl variables
     ("\\<\\([bB][uU][fF][fF][eE][rR]\\ergsh\\||[fF][iI][lL][eE]\\|freq\\|[mM][aA][xX]\\|[mM][eE][pP][hH]\\|plot\\|[wW][rR][iI][tT][eE]\\|[eE][vV][eE][nN][tT]\\|[fF][iI][lL][tT][eE][rR]\\|[tT][yY][pP][eE]\\|[cC][eE][lL][lL]\\|[sS][uU][rR][fF][aA][cC][eE]\\|[tT][aA][lL][lL][yY]\\|traks\\)\\>" . 'font-lock-variable-name-face) ;; ptrac variables
     ("\\>\\(:[hH]\\|:[nN]\\|:[pP]\\|:[zZ]\\)\\>" . 'font-lock-particle-face)
   )
  ;; auto-mode-list  (filename extension to autoload mode e.g.'(".mcn\\'"))
  '("inp\\'")
  ;; function-list
  nil
  ;; description
  "generic mode for editing MCNP input files.")
