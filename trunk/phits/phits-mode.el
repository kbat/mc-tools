;;  Generic mode for highlighting syntax for PHITS input files
;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;  
;;
;; Author: Konstantin Batkov
;; e-mail: kbat.phits ((at)) lizardie.com
;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;  
;;         How to use:
;; Either put  -*-phits-mode-*- on the first line of your 
;; input file to autoload this mode or use the .phits extention
;;
;; Your .emacs file should contain something like:
;;  (setq load-path (cons (expand-file-name "/path/to/your/lispdirectory") load-path))
;;  (global-font-lock-mode t)
;;  (load "phits-mode")
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;  
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;  

(require 'font-lock)
(require 'generic)

(make-face 'font-lock-section-face)
(set-face-foreground 'font-lock-section-face "pink")

(make-face 'font-lock-parameter-face)
(set-face-foreground 'font-lock-parameter-face "lightblue")

(make-face 'font-lock-particle-face)
(set-face-foreground 'font-lock-particle-face "yellow")

(make-face 'font-lock-constant-face)
(set-face-foreground 'font-lock-constant-face "lightgreen")

(make-face 'font-lock-function-face)
(set-face-foreground 'font-lock-function-face "orange")


;; from stackoverflow.com/questions/4549015:
;; how to add it in phits-mode ???
(defun my-c-mode-font-lock-if0 (limit)
  (save-restriction
    (widen)
    (save-excursion
      (goto-char (point-min))
      (let ((depth 0) str start start-depth)
        (while (re-search-forward "^\\s-*#\\s-*\\(if\\|else\\|endif\\)" limit 'move)
          (setq str (match-string 1))
          (if (string= str "if")
              (progn
                (setq depth (1+ depth))
                (when (and (null start) (looking-at "\\s-+0"))
                  (setq start (match-end 0)
                        start-depth depth)))
            (when (and start (= depth start-depth))
              (c-put-font-lock-face start (match-beginning 0) 'font-lock-comment-face)
              (setq start nil))
            (when (string= str "endif")
              (setq depth (1- depth)))))
        (when (and start (> depth 0))
          (c-put-font-lock-face start (point) 'font-lock-comment-face)))))
  nil)

(defun my-c-mode-common-hook ()
  (font-lock-add-keywords
   nil
   '((my-c-mode-font-lock-if0 (0 font-lock-comment-face prepend))) 'add-to-end))

(add-hook 'c-mode-common-hook 'my-c-mode-common-hook)
;; end from stackoverflow


(define-generic-mode 'phits-mode
  ;; comment-list (2 ways to comment in PHITS so do below)
  nil
  ;; keyword-list (do below also)
  nil
  ;; font-lock-list (additional expressions to highlight) 
  '(
    ("^[Cc].*" . 'font-lock-comment-face)    ;; a "c" followed by a blank in
     ("^ [Cc] .*" . 'font-lock-comment-face)   ;; columns 1-5 is a comment line
     ("^  [Cc] .*" . 'font-lock-comment-face)  ;; (the reg exp \{n,m\} does not
     ("^   [Cc] .*" . 'font-lock-comment-face) ;; seem to work here)
     ("^    [Cc] .*" . 'font-lock-comment-face)
     ("$.*" . 'font-lock-comment-face)         ;; dollar sign comment indicator
     ("!.*" . 'font-lock-comment-face)         ;;
     ("^ \\{0,4\\}\\[\\<\\(cell\\|end\\|importance\\|material\\|parameters\\|mat name color\\|source\\|surface\\|t-3dshow\\|t-heat\\|t-deposit2?\\|t-gshow\\|timer\\|title\\|t-product\\|t-track\\|t-yield\\|transform\\|volume\\)\\>\\]" . 'font-lock-section-face)
     ("\\<\\(angel\\|[aelrtxyz]-type\\|axis\\|box\\|dir\\|dmax\\|dose\\|e0\\|edel\\|[el]-dst\\|ejamnu\\|[el]-phi\\|epsout\\|[el]-the\\|eqmdmin\\|eqmdnu\\|factor\\|file\\|[rg]-show\\|heaven\\|icntl\\|icput\\|icrhi\\|ielas\\|igamma\\|imout\\|inmed\\|inucr\\|ipreeq\\|isobar\\|itall\\|level\\|line\\|mat\\|ndata\\|ne\\|nedisp\\|nevap\\|nlost\\|nspred\\|material\\|maxbch\\|maxcas\\|mesh\\|multiplier\\|n[erxyz]\\|output\\|part\\|pnint\\|product\\|proj\\|r0\\|reg\\|resol\\|shadow\\|source\\|title\\|trcl\\|unit\\|w-dst\\|w-hgt\\|width\\|w-wdt\\|[erxyz]\\(max\\|min\\)\\|[xyz]\\([01]\\|max\\|min\\|-txt\\)\\|[xyz][xyz]\\)\\>" . 'font-lock-parameter-face)
     ("\\<\\(chart\\|color\\|c[xyz]\\|c\/[xyz]\\|dchain\\|eng\\|gshow\\|imp\\|mt?[0-9]\\{1,4\\}\\|name\\|nucleus\\|off\\|p[xyz]\\|q\\|qp\\|rpp\\|r-z\\|set\\|so\\|tr.\\|tr..\\|vol\\|xyz\\)\\>" . 'font-lock-keyword-face) ;; phits keywords
     ("\\<\\(all\\|alpha\\|electron\\|neutron\\|photon\\|positron\\|proton\\)\\>" . 'font-lock-particle-face) ;;
     ("\\<\\(a?cos\\|a?sin\\|a?tan\\|atan2\\)\\>" . 'font-lock-function-face) ;;

     ("\\<pi\\>" . 'font-lock-constant-face)
     ("\\<\\(brown\\|black\\|blue\\|cyan\\|cyanblue\\|darkgray\\|gray\\|green\\|lightgray\\|lightgreen\\|magneta\\|matblack\\|mossgreen\\|orange\\|pastelblue\\|pink\\|red\\|violet\\|white\\|yellow\\)\\>" . 'font-lock-constant-face) ;; phits colors

     ("\\<\\([fF][iI][lL][lL]\\|[uU]\\|[lL][aA][tT]\\|[lL][iI][kK][eE]\\|[bB][uU][tT]\\)\\>" . 'font-lock-variable-name-face) ;; fill,universe,lat,trcl variables
     ("\\<\\([bB][uU][fF][fF][eE][rR]\\|[fF][iI][lL][eE]\\|[mM][aA][xX]\\|[mM][eE][pP][hH]\\|[wW][rR][iI][tT][eE]\\|[eE][vV][eE][nN][tT]\\|[fF][iI][lL][tT][eE][rR]\\|[tT][yY][pP][eE]\\|[cC][eE][lL][lL]\\|[sS][uU][rR][fF][aA][cC][eE]\\|[tT][aA][lL][lL][yY]\\)\\>" . 'font-lock-variable-name-face) ;; ptrac variables
   )
  ;; auto-mode-list  (filename extension to autoload mode e.g.'(".phits\\'"))
  nil
  ;; function-list
  nil
  ;; description
  "generic mode for editing PHITS input files.")





;;(add-hook 'c-mode-common-hook 'my-c-mode-common-hook)
