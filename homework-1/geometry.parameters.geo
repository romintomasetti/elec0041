// Copper plate
DefineConstant[ CP_width  = {0.17          , Name "Constant/Copper plate width [m]"} ];
DefineConstant[ CP_height = {0.09          , Name "Constant/Copper plate height [m]"} ];
DefineConstant[ CP_thickn = {0.002         , Name "Constant/Copper plate thickness [m]"}];

// Input / output holes
DefineConstant[ IO_radius = {0.0025        , Name "Constant/Input and output ports hole radius [m]"}];

DefineConstant[ I_x       = {CP_width / 2.0, Name "Constant/Input hole X coordinate [m]"}];
DefineConstant[ I_y       = {0.06          , Name "Constant/Input hole Y coordinate [m]"}];

DefineConstant[ O_spacing = {0.05          , Name "Constant/Output holes spacing [m]"}];
DefineConstant[ O_height  = {0.01          , Name "Constant/Output holes height [m]"}];

// Design optimization
DefineConstant[ DO_x      = {CP_width / 2.0, Name "Constant/Ellipse center X coordinate [m]"}];
DefineConstant[ DO_y      = {0.035         , Name "Variable/Ellipse center Y coordinate [m]"}];
DefineConstant[ DO_a      = {0.015 / 2.0   , Name "Variable/Ellipse half vertical axis [m]"}];
DefineConstant[ DO_b      = {0.008 / 2.0   , Name "Variable/Ellipse half horizontal axis [m]"}];
