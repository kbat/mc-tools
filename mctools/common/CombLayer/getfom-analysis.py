# An example of getfom-analysis.py used by getfom.py
# Calculates change (first derivative) of TGraphErrors fitted with pol2
#
gr.Sort()

N = gr.GetN()

xmin = gr.GetX()[0]
xmax = gr.GetX()[N-1]
dx = xmax-xmin
dy = gr.GetY()[N-1]-gr.GetY()[0]
print dy/dx

fit = gr.GetFunction("pol2")
change = fit.GetParameter(1) + 2*fit.GetParameter(2)*gr.GetX()[0]
change = change * 100 / fit.Eval(xmin)

tchange = ROOT.TLatex()
tchange.SetNDC()
tchange.DrawLatex(0.6, 0.6, "Change: %.1f %% / cm" % change)
ROOT.gPad.Update()
