#! /bin/bash

if [ $# != 2 ]; then
    echo "Usage: $(basename "$0") <N> <path>"
    echo "       N - number of commits to show"
    echo "       path - same as the 'path' argument in git-log"
    exit 1
fi

N=$1
fff=$2

if [ ! -e $fff ]; then
    echo "Coult not open file '$fff'"
    exit 1
fi

if [ $fff = "." ]; then
    OUTPUT="this.gitlog"
else
    OUTPUT=$(basename $fff .tex).gitlog
fi

#tmp=$(mktemp --suffix .gitlog2latex)
tmp="/tmp/a.gitlog2latex"

echo "\begin{center}
\begin{longtable}{ccp{0.7\textwidth}}
\toprule
    Date & Hash & Commit message \\\\ \midrule " > $OUTPUT

#git log --pretty=format:"%ad & %h & %s" --date=short $fff
git log --pretty=format:"%ad & %h & %B" --date=short -$N $fff > $tmp

sed -i -e 's; ->; $\\to$;g' $tmp

# [ -> {[} and ] -> {]}
#sed -i -e 's;\([]\[]\);{\1};g' $tmp

# \begin{document} -> \verb|\begin{document}|
sed -i -e 's;\(\\[^}]*}\);\\verb\|\1\|;g' $tmp

# \command -> \verb|\command\|
sed -i -e 's;\(\\[a-z]* \);\\verb\|\1\|;g' $tmp

sed -i -e 's;>;\\textgreater{};g' $tmp

# % -> \%
sed -i -e 's;%;\\%;g' $tmp
# % \theta -> $\theta$
sed -i -e 's;\\theta;$\\theta$;g' $tmp
# LaTeX
sed -i -e 's;Latex;\\LaTeX;g' $tmp
# underscore
sed -i -e 's;_;\\_;g' $tmp

# Now we need to add \\ after each line, but instead we do it in the beginning the next one:
# add \\ before the lines starting with date assuming year > 2000
sed -i -e 's;^\(20[0-9][0-9]-[01][0-9]-[0-3][0-9].*\);\\\\ \1;' $tmp
# remove first \\ to prevent adding an empty line after the header in the LaTeX table
sed -i -e '0,/^\\\\/ s/^\\\\/ /1' $tmp

cat $tmp >> $OUTPUT

echo "\\\\ \bottomrule" >> $OUTPUT
echo "\end{longtable}
\end{center}" >> $OUTPUT

##sed -i -e 's/ \\\([A-Za-z]\)/ \\\\\1/' $OUTPUT

#sed -i -e 's;\(\\setcounter[^}]*}\);\\verb\|\1\|;' $OUTPUT
#sed -i -e 's;\(\\gridlines\);\\verb\|\1\|;' $OUTPUT
# verbatim -> quote
##sed -i -e 's;\(\\begin\|\\end\){verbatim};\1{quote};' $OUTPUT
#sed -i -e 's;\(\\begin\|\\end\){verbatim};;' $OUTPUT

gawk -i inplace NF $OUTPUT

rm -f $tmp
