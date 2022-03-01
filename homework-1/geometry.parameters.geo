// Copper plate
DefineConstant[ CP_width  = {0.17, Name "Copper plate width [m]"} ];
DefineConstant[ CP_height = {0.09, Name "Copper plate height [m]"} ];

// Input / output holes
DefineConstant[ IO_radius = {0.0025        , Name "Input/output hole radius [m]"}];

DefineConstant[ I_x       = {CP_width / 2.0, Name "Input hole X coordinate [m]"}];
DefineConstant[ I_y       = {0.06          , Name "Input hole Y coordinate [m]"}];

DefineConstant[ O_spacing = {0.05          , Name "Output holes spacing [m]"}];
DefineConstant[ O_height  = {0.01          , Name "Output holes height [m]"}];

// Design optimization
DefineConstant[ DO_x      = {CP_width / 2.0, Name "Ellipse center X coordinate [m]"}];
DefineConstant[ DO_y      = {0.035         , Name "Ellipse center Y coordinate [m]"}];
DefineConstant[ DO_a      = {0.015 / 2.0   , Name "Ellipse half vertical axis [m]"}];
DefineConstant[ DO_b      = {0.008 / 2.0   , Name "Ellipse half horizontal axis [m]"}];
