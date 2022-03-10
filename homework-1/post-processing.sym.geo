// Post-processing of results

Merge "busbar.sym.geo";
Merge "v.sym.pos";

// View [0] (voltage) setup
View[0].Name = "Scalar electric potential [V]";
View.IntervalsType = 3;
View.NbIso = 20;

// Save to files
Print.Text = 0;
Save "v.sym.png";
Print.Text = 1;
Save "v.sym.tex";

Sleep 0.5;

Exit;
