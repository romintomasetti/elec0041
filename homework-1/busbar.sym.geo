// Include geometrical parameters
Include "geometry.parameters.geo";

// Include mesh parameters
Include "mesh.parameters.geo";

// Copper plate 2 left corners + 2 middle points
CP_corner_blp = newp; Point(CP_corner_blp) = {0             ,0        ,0,CP_mesh_b};
CP_corner_bmp = newp; Point(CP_corner_bmp) = {CP_width / 2.0,0        ,0,CP_mesh_b};
CP_corner_tmp = newp; Point(CP_corner_tmp) = {CP_width / 2.0,CP_height,0,CP_mesh_t};
CP_corner_tlp = newp; Point(CP_corner_tlp) = {0             ,CP_height,0,CP_mesh_t};

// Copper plate 1 left border + 2 below and top half borders
CP_border_bottom = newl; Line(CP_border_bottom) = {CP_corner_blp,CP_corner_bmp};
CP_border_top    = newl; Line(CP_border_top   ) = {CP_corner_tmp,CP_corner_tlp};
CP_border_left   = newl; Line(CP_border_left  ) = {CP_corner_tlp,CP_corner_blp};

// Input current circle half (in 1 part)
I_hole_center_p  = newp; Point(I_hole_center_p ) = {I_x,I_y          ,0,IO_mesh};
I_hole_helper_pb = newp; Point(I_hole_helper_pb) = {I_x,I_y-IO_radius,0,IO_mesh};
I_hole_helper_pt = newp; Point(I_hole_helper_pt) = {I_x,I_y+IO_radius,0,IO_mesh};
I_hole_cl = newc; Circle(I_hole_cl) = {
    I_hole_helper_pt,
    I_hole_center_p,
    I_hole_helper_pb
};

// Output current hole left
O_l_hole_center_p  = newp; Point(O_l_hole_center_p ) = {I_x-O_spacing,O_height          ,0,IO_mesh};
O_l_hole_helper_pb = newp; Point(O_l_hole_helper_pb) = {I_x-O_spacing,O_height-IO_radius,0,IO_mesh};
O_l_hole_helper_pt = newp; Point(O_l_hole_helper_pt) = {I_x-O_spacing,O_height+IO_radius,0,IO_mesh};
O_l_hole_cr = newc; Circle(O_l_hole_cr) = {
    O_l_hole_helper_pb,
    O_l_hole_center_p,
    O_l_hole_helper_pt
};
O_l_hole_cl = newc; Circle(O_l_hole_cl) = {
    O_l_hole_helper_pt,
    O_l_hole_center_p,
    O_l_hole_helper_pb
};
O_l_hole_cloop = newcl; Curve Loop(O_l_hole_cloop) = {O_l_hole_cr,O_l_hole_cl};

// Output current hole center half
O_c_hole_center_p  = newp; Point(O_c_hole_center_p ) = {I_x,O_height          ,0,IO_mesh};
O_c_hole_helper_pb = newp; Point(O_c_hole_helper_pb) = {I_x,O_height-IO_radius,0,IO_mesh};
O_c_hole_helper_pt = newp; Point(O_c_hole_helper_pt) = {I_x,O_height+IO_radius,0,IO_mesh};
O_c_hole_cl = newc; Circle(O_c_hole_cl) = {
    O_c_hole_helper_pt,
    O_c_hole_center_p,
    O_c_hole_helper_pb
};

// Design optimization hole
DO_cp = newp; Point(DO_cp) = {DO_x     , DO_y     , 0, DO_mesh};
DO_lp = newp; Point(DO_lp) = {DO_x-DO_b, DO_y     , 0, DO_mesh};
DO_bp = newp; Point(DO_bp) = {DO_x     , DO_y-DO_a, 0, DO_mesh};
DO_tp = newp; Point(DO_tp) = {DO_x     , DO_y+DO_a, 0, DO_mesh};

DO_tl_el = newc; Ellipse(DO_tl_el) = {DO_tp,DO_cp,DO_tp,DO_lp};
DO_bl_el = newc; Ellipse(DO_bl_el) = {DO_bp,DO_cp,DO_bp,DO_lp};

// Symmetry plane
CP_symmetry_top_to_in = newl; Line(CP_symmetry_top_to_in) = {CP_corner_tmp     ,I_hole_helper_pt   }; CP_symmetry_top_to_in_CL = newc; Curve Loop(CP_symmetry_top_to_in) = {CP_symmetry_top_to_in};
CP_symmetry_in_to_opt = newl; Line(CP_symmetry_in_to_opt) = {I_hole_helper_pb  ,DO_tp              }; CP_symmetry_in_to_opt_CL = newc; Curve Loop(CP_symmetry_in_to_opt) = {CP_symmetry_in_to_opt};
CP_symmetry_opt_to_om = newl; Line(CP_symmetry_opt_to_om) = {DO_bp             ,O_c_hole_helper_pt }; CP_symmetry_opt_to_om_CL = newc; Curve Loop(CP_symmetry_opt_to_om) = {CP_symmetry_opt_to_om};
CP_symmetry_om_to_bot = newl; Line(CP_symmetry_om_to_bot) = {O_c_hole_helper_pb,CP_corner_bmp      }; CP_symmetry_om_to_bot_CL = newc; Curve Loop(CP_symmetry_om_to_bot) = {CP_symmetry_om_to_bot};

// Copper plate external curve loop (borders) (opened)
CP_external_c = newcl; Curve Loop(CP_external_c) = {
    CP_border_top,
    CP_border_left,
    CP_border_bottom,
    -CP_symmetry_om_to_bot,
    -O_c_hole_cl,
    -CP_symmetry_opt_to_om,
    DO_bl_el,
    -DO_tl_el,
    -CP_symmetry_in_to_opt,
    -I_hole_cl,
    -CP_symmetry_top_to_in
};

// Input hole loop (opened)
I_hole_cloop = newcl; Curve Loop(I_hole_cloop) = {I_hole_cl};

// Output hole left
O_l_hole_cloop = newcl; Curve Loop(O_l_hole_cloop) = {O_l_hole_cr,O_l_hole_cl};

// Output hole middle (opened)
O_c_hole_cloop = newcl; Curve Loop(O_c_hole_cloop) = {O_c_hole_cl};

// Design optimization loop (opened)
DO_hole_cloop = newcl; Curve Loop(DO_hole_cloop) = {
    DO_tl_el,
    -DO_bl_el
};

// Copper plate surface
CP_surface = newc; Plane Surface(CP_surface) = {
    CP_external_c,
    -O_l_hole_cloop
};

// Copper plate physical surface
Physical Surface("Copper plate surface", 200) = {CP_surface};

// Input/output holes physical curves
Physical Curve("input"        , 201) = {I_hole_cl};
Physical Curve("output_left"  , 202) = {O_l_hole_cr,O_l_hole_cl};
Physical Curve("output_center", 203) = {O_c_hole_cl};

// Design optimization hole physical curve
Physical Curve("optimization" , 205) = {
    DO_tl_el,
    -DO_bl_el
};
