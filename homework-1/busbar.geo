// Include geometrical parameters
Include "geometry.parameters.geo";

// Include mesh parameters
Include "mesh.parameters.geo";

// Copper plate 4 corners
CP_corner_blp = newp; Point(CP_corner_blp) = {0       ,0        ,0,CP_mesh_b};
CP_corner_brp = newp; Point(CP_corner_brp) = {CP_width,0        ,0,CP_mesh_b};
CP_corner_trp = newp; Point(CP_corner_trp) = {CP_width,CP_height,0,CP_mesh_t};
CP_corner_tlp = newp; Point(CP_corner_tlp) = {0       ,CP_height,0,CP_mesh_t};

// Copper plate 4 borders
CP_border_bottom = newl; Line(CP_border_bottom) = {CP_corner_blp,CP_corner_brp};
CP_border_right  = newl; Line(CP_border_right ) = {CP_corner_brp,CP_corner_trp};
CP_border_top    = newl; Line(CP_border_top   ) = {CP_corner_trp,CP_corner_tlp};
CP_border_left   = newl; Line(CP_border_left  ) = {CP_corner_tlp,CP_corner_blp};

// Copper plate external curve loop (borders)
CP_external_c = newcl; Curve Loop(CP_external_c) = {
    CP_border_bottom,
    CP_border_right,
    CP_border_top,
    CP_border_left
};

// Input current circle (in 2 parts) and curve loop
I_hole_center_p  = newp; Point(I_hole_center_p ) = {I_x,I_y          ,0,IO_mesh};
I_hole_helper_pb = newp; Point(I_hole_helper_pb) = {I_x,I_y-IO_radius,0,IO_mesh};
I_hole_helper_pt = newp; Point(I_hole_helper_pt) = {I_x,I_y+IO_radius,0,IO_mesh};
I_hole_cr = newc; Circle(I_hole_cr) = {
    I_hole_helper_pb,
    I_hole_center_p,
    I_hole_helper_pt
};
I_hole_cl = newc; Circle(I_hole_cl) = {
    I_hole_helper_pt,
    I_hole_center_p,
    I_hole_helper_pb
};
I_hole_cloop = newcl; Curve Loop(I_hole_cloop) = {I_hole_cr,I_hole_cl};

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

// Output current hole center
O_c_hole_center_p  = newp; Point(O_c_hole_center_p ) = {I_x,O_height          ,0,IO_mesh};
O_c_hole_helper_pb = newp; Point(O_c_hole_helper_pb) = {I_x,O_height-IO_radius,0,IO_mesh};
O_c_hole_helper_pt = newp; Point(O_c_hole_helper_pt) = {I_x,O_height+IO_radius,0,IO_mesh};
O_c_hole_cr = newc; Circle(O_c_hole_cr) = {
    O_c_hole_helper_pb,
    O_c_hole_center_p,
    O_c_hole_helper_pt
};
O_c_hole_cl = newc; Circle(O_c_hole_cl) = {
    O_c_hole_helper_pt,
    O_c_hole_center_p,
    O_c_hole_helper_pb
};
O_c_hole_cloop = newcl; Curve Loop(O_c_hole_cloop) = {O_c_hole_cr,O_c_hole_cl};

// Output current hole right
O_r_hole_center_p  = newp; Point(O_r_hole_center_p ) = {I_x+O_spacing,O_height          ,0,IO_mesh};
O_r_hole_helper_pb = newp; Point(O_r_hole_helper_pb) = {I_x+O_spacing,O_height-IO_radius,0,IO_mesh};
O_r_hole_helper_pt = newp; Point(O_r_hole_helper_pt) = {I_x+O_spacing,O_height+IO_radius,0,IO_mesh};
O_r_hole_cr = newc; Circle(O_r_hole_cr) = {
    O_r_hole_helper_pb,
    O_r_hole_center_p,
    O_r_hole_helper_pt
};
O_r_hole_cl = newc; Circle(O_r_hole_cl) = {
    O_r_hole_helper_pt,
    O_r_hole_center_p,
    O_r_hole_helper_pb
};
O_r_hole_cloop = newcl; Curve Loop(O_r_hole_cloop) = {O_r_hole_cr,O_r_hole_cl};

// Design optimization hole
DO_cp = newp; Point(DO_cp) = {DO_x     , DO_y     , 0, DO_mesh};
DO_lp = newp; Point(DO_lp) = {DO_x-DO_b, DO_y     , 0, DO_mesh};
DO_bp = newp; Point(DO_bp) = {DO_x     , DO_y-DO_a, 0, DO_mesh};
DO_rp = newp; Point(DO_rp) = {DO_x+DO_b, DO_y     , 0, DO_mesh};
DO_tp = newp; Point(DO_tp) = {DO_x     , DO_y+DO_a, 0, DO_mesh};

DO_br_el = newc; Ellipse(DO_br_el) = {DO_bp,DO_cp,DO_bp,DO_rp};
DO_tr_el = newc; Ellipse(DO_tr_el) = {DO_tp,DO_cp,DO_tp,DO_rp};
DO_tl_el = newc; Ellipse(DO_tl_el) = {DO_tp,DO_cp,DO_tp,DO_lp};
DO_bl_el = newc; Ellipse(DO_bl_el) = {DO_bp,DO_cp,DO_bp,DO_lp};

DO_hole_cloop = newcl; Curve Loop(DO_hole_cloop) = {
    DO_br_el,
    -DO_tr_el,
    DO_tl_el,
    -DO_bl_el
};

// Copper plate surface
CP_surface = newc; Plane Surface(CP_surface) = {
    CP_external_c,
    -I_hole_cloop,
    -O_l_hole_cloop,
    -O_c_hole_cloop,
    -O_r_hole_cloop,
    -DO_hole_cloop
};

// Copper plate physical surface
Physical Surface("Copper plate surface", 200) = {CP_surface};

// Input/output holes physical curves
Physical Curve("input"        , 201) = {I_hole_cr  ,I_hole_cl  };
Physical Curve("output_left"  , 202) = {O_l_hole_cr,O_l_hole_cl};
Physical Curve("output_center", 203) = {O_c_hole_cr,O_c_hole_cl};
Physical Curve("output_right" , 204) = {O_r_hole_cr,O_r_hole_cl};

// Design optimization hole physical curve
Physical Curve("optimization" , 205) = {
    DO_br_el,
    -DO_tr_el,
    DO_tl_el,
    -DO_bl_el
};
