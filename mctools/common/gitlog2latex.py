#! /bin/bash

if [ $# != 2 ]; then
    echo "Usage: $(basename "$0") <N> <path>"
    echo "       N - number of commits to show"
    echo "       path - same as the 'path' argument in git-log"
    exit 1
fi

if ! command -v pandoc >/dev/null; then
    echo "ERROR: pandoc is not installed"
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

tmp=$(mktemp --suffix .gitlog2latex)

echo "\begin{center}
\begin{longtable}{ccp{0.7\textwidth}}
\toprule
    Date & Hash & Commit message \\\\ \midrule " > $OUTPUT

#git log --pretty=format:"%ad & %h & %s" --date=short $fff
git log --pretty=format:"%ad & %h & %B" --date=short -$N $fff | pandoc -f markdown -t latex -o $tmp
# \& -> &
sed -i -e 's;\\&;\&;g' $tmp
# add \\ before the lines starting with date assuming year > 2000
sed -i -e 's;^\(20[0-9][0-9]-[01][0-9]-[0-3][0-9].*\);\\\\ \1;' $tmp
# remove first \\ to prevent adding an empty line after the header in the LaTeX table
sed -i -e '0,/^\\\\/ s/^\\\\/ /1' $tmp

cat $tmp >> $OUTPUT

echo "\\\\ \bottomrule" >> $OUTPUT
echo "\end{longtable}
\end{center}" >> $OUTPUT

#sed -i -e 's/ \\\([A-Za-z]\)/ \\\\\1/' $OUTPUT

#sed -i -e 's/\\setcounter/\\verb\|\\setcounter\|/g' $OUTPUT
sed -i -e 's;\(\\setcounter[^}]*}\);\\verb\|\1\|;' $OUTPUT
sed -i -e 's;\(\\gridlines\);\\verb\|\1\|;' $OUTPUT
# verbatim -> quote
#sed -i -e 's;\(\\begin\|\\end\){verbatim};\1{quote};' $OUTPUT
sed -i -e 's;\(\\begin\|\\end\){verbatim};;' $OUTPUT
sed -i -e 's; \-\\textgreater{}; $\\to$;' $OUTPUT

gawk -i inplace NF $OUTPUT

rm -f $tmp
