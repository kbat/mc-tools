;;  Generic mode for highlighting syntax for PHITS input files
;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;
;; Latest version is available here:
;; https://github.com/kbat/mc-tools/blob/master/mctools/phits/phits-mode.el
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
(set-face-foreground 'font-lock-section-face "red")
(set-face-attribute  'font-lock-section-face nil :weight 'bold)

(make-face 'font-lock-particle-face)
(set-face-foreground 'font-lock-particle-face "yellow")

(make-face 'font-lock-transformation-face)
(set-face-foreground 'font-lock-transformation-face "yellow")

(make-face 'font-lock-parameter-face)
(set-face-foreground 'font-lock-parameter-face "lightblue")

(make-face 'font-lock-angel-parameter-face)
(set-face-foreground 'font-lock-angel-parameter-face "lightgreen")

(make-face 'font-lock-constant-face)
(set-face-foreground 'font-lock-constant-face "lightgreen")

(make-face 'font-lock-function-face)
(set-face-foreground 'font-lock-function-face "orange")

(make-face 'font-lock-surface-face)
(set-face-foreground 'font-lock-surface-face "lightgreen")


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
    ("^c.*" . 'font-lock-comment-face)    ;; a "c" followed by a blank in
     ("^ c .*" . 'font-lock-comment-face)   ;; columns 1-5 is a comment line
     ("^  c .*" . 'font-lock-comment-face)  ;; (the reg exp \{n,m\} does not
     ("^   c .*" . 'font-lock-comment-face) ;; seem to work here)
     ("^    c .*" . 'font-lock-comment-face)
     ("$.*" . 'font-lock-comment-face)
     ("!.*" . 'font-lock-comment-face)
     ("^#.*" . 'font-lock-comment-face)
     ("^ \\{0,4\\}\\[\\<\\(cell\\|end\\|importance\\|material\\|parameters\\|mat name color\\|reg name\\|source\\|surface\\|t-3dshow\\|t-heat\\|t-dpa\\|t-deposit2?\\|t-gshow\\|timer\\|title\\|t-cross\\|t-product\\|t-track\\|t-yield\\|temperature\\|transform\\|volume\\)\\>\\] ?.*" . 'font-lock-section-face) ;; ?.* in the end mean that we color also the section title (if any)
     ("^ *\\<\\(angel\\|[aelrstxyz]-type\\|axis\\|box\\|e-mode\\|dir\\|deltm\\|dmax\\|dose\\|e0\\|edel\\|[el]-dst\\|ejamnu\\|[el]-phi\\|epsout\\|[el]-the\\|eqmdmin\\|eqmdnu\\|factor\\|file\\|[rg]-show\\|heaven\\|icntl\\|icommat\\|icput\\|icrhi\\|ielas\\|igamma\\|igchk\\|igcut\\|imout\\|incut\\|infl\\|info\\|inmed\\|inucr\\|ipreeq\\|isobar\\|itall\\|level\\|line\\|mat\\|mirror\\|ndata\\|nedisp\\|nevap\\|nlost\\|nspred\\|nucdata\\|material\\|maxbch\\|maxcas\\|mesh\\|multiplier\\|n[aertxyz]\\|output\\|part\\|pnint\\|product\\|proj\\|r0\\|reg\\|resol\\|rseed\\|shadow\\|source\\|title\\|tmin\\|tmax\\|trcl\\|t[dnw]\\|unit\\|w-ang\\|w-dst\\|w-hgt\\|w-mn[hw]\\|w-wdt\\|width\\|[aerxyz]\\(max\\|min\\)\\|[xyz]\\([01]\\|max\\|min\\|-txt\\)\\|[xyz][xyz]\\)\\>" . 'font-lock-parameter-face) ;; note that there must be no other symbols (except space) before parameter
     ("\\<\\(area\\|a-curr\\|chart\\|color\\|current\\|deposit\\|dchain\\|dose\\|dpa\\|eng\\|gshow\\|heat\\|imp\\|flux\\|[mM]t?[0-9]\\{1,4\\}\\|name\\|nucleus\\|off\\|q\\|qp\\|reg\\|r-in\\|r-out\\|rpp\\|r-z\\|set\\|size\\|source\\|t\\|tmp\\|vol\\|[xyz][xyz]?[xyz]?\\)\\>" . 'font-lock-keyword-face) ;; phits keywords
     ("\\<\\(all\\|alpha\\|electron\\|neutron\\|photon\\|positron\\|proton\\)\\>" . 'font-lock-particle-face) ;;
     ("\\<\\(a?cos\\|a?sin\\|a?tan\\|atan2\\)\\>" . 'font-lock-function-face) ;;
     ("\\<\\(ylin\\)\\>" . 'font-lock-angel-parameter-face) ;;

     ("\\<pi\\|c[1-9]\\>" . 'font-lock-constant-face)
     ("\\<\\(brown\\|black\\|blue\\|bluegreen\\|cyan\\|cyanblue\\|darkgray\\|gray\\|green\\|lightgray\\|lightgreen\\|magneta\\|matblack\\|mossgreen\\|orange\\|orangeyellow\\|pastelblue\\|pastelcyan\\|pastelpink\\|pastelpurple\\|pastelviolet\\|pastelyellow\\|pink\\|red\\|violet\\|white\\|yellow\\|yellowgreen\\)\\>" . 'font-lock-constant-face) ;; phits colors

     ("\\<\\(box\\|[ck]\/[xyz]\\|[ckpst][xyz]\\|[gs]q\\|hex\\|[ps]\\|rcc\\|rhp\\|rpp\\|so\\|sph\\|xy\\|zp\\)\\>" . 'font-lock-surface-face)

     (" trans [0-9]+" . 'font-lock-transformation-face)
    ("^*?trcl[0-9]+" . 'font-lock-transformation-face)
    ("^*?tr[0-9]+" . 'font-lock-transformation-face)


     ("\\<\\(fill\\|u\\|lat\\|like\\|but\\)\\>" . 'font-lock-variable-name-face) ;; fill,universe,lat,trcl variables
   )
  ;; auto-mode-list
  '(".phits\\'")
  ;; function-list
  nil
  ;; description
  "generic mode for editing PHITS input files.")

;; case-insensitive keyword search
(defun case-insensitive-advice ()
  (set (make-local-variable 'font-lock-keywords-case-fold-search) t))
(advice-add 'phits-mode :after #'case-insensitive-advice)





;;(add-hook 'c-mode-common-hook 'my-c-mode-common-hook)
