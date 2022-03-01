Group {
  Busbar             = Region[200];
  ElectrodeIn        = Region[201];
  ElectrodeOutLeft   = Region[202];
  ElectrodeOutCenter = Region[203];
  ElectrodeOutRight  = Region[204];
  OptimizationHole   = Region[205];

  Vol_Ele            = Region[ {Busbar} ];
  Sur_Neu_Ele        = Region[ {OptimizationHole} ];
  Sur_Electrodes_Ele = Region[ {ElectrodeIn, ElectrodeOutLeft, ElectrodeOutCenter, ElectrodeOutRight} ];
}

Function {
  DefineConstant [
    CurrentValue = {375, Name "Input current value"}
  ];
  sigma[Busbar] = 5e7;
}

Constraint {
  { Name Dirichlet_Ele; Type Assign;
    Case {
    }
  }

  { Name SetGlobalPotential; Type Assign;
    Case {
      { Region ElectrodeOutLeft   ; Value 0; }
      { Region ElectrodeOutCenter ; Value 0; }
      { Region ElectrodeOutRight  ; Value 0; }
    }
  }
  { Name SetGlobalCurrent; Type Assign;
    Case {
      { Region ElectrodeIn; Value CurrentValue; }
    }
  }
}

Group{
  Dom_Hgrad_v_Ele =  Region[ {Vol_Ele, Sur_Neu_Ele, Sur_Electrodes_Ele} ];
}

FunctionSpace {
  { Name Hgrad_v_Ele; Type Form0;
    BasisFunction {
      { Name sn; NameOfCoef vn; Function BF_Node;
        Support Dom_Hgrad_v_Ele; Entity NodesOf[ All, Not Sur_Electrodes_Ele ]; }
      { Name sf; NameOfCoef vf; Function BF_GroupOfNodes;
        Support Dom_Hgrad_v_Ele; Entity GroupsOfNodesOf[ Sur_Electrodes_Ele ]; }
    }
    GlobalQuantity {
      { Name GlobalPotential; Type AliasOf       ; NameOfCoef vf; }
      { Name GlobalCurrent  ; Type AssociatedWith; NameOfCoef vf; }
    }
    Constraint {
      { NameOfCoef vn; EntityType NodesOf;
        NameOfConstraint Dirichlet_Ele; }
      { NameOfCoef GlobalPotential; EntityType GroupsOfNodesOf;
	NameOfConstraint SetGlobalPotential; }
      { NameOfCoef GlobalCurrent; EntityType GroupsOfNodesOf;
	NameOfConstraint SetGlobalCurrent; }
    }
  }
}

Jacobian {
  { Name Vol ;
    Case {
      { Region All ; Jacobian Vol ; }
    }
  }
}

Integration {
  { Name Int ;
    Case { {Type Gauss ;
            Case { { GeoElement Triangle    ; NumberOfPoints  4 ; }
                   { GeoElement Quadrangle  ; NumberOfPoints  4 ; } }
      }
    }
  }
}

Formulation {
  { Name Electrokinetics_v; Type FemEquation;
    Quantity {
      { Name v; Type Local; NameOfSpace Hgrad_v_Ele; }
      { Name U; Type Global; NameOfSpace Hgrad_v_Ele [GlobalPotential]; }
      { Name I; Type Global; NameOfSpace Hgrad_v_Ele [GlobalCurrent]; }
    }
    Equation {
      Integral { [ sigma[] * Dof{d v} , {d v} ];
        In Vol_Ele; Jacobian Vol; Integration Int; }
      GlobalTerm { [ -Dof{I} , {U} ]; In Sur_Electrodes_Ele; }
    }
  }
}

Resolution {
  { Name EleKin_v;
    System {
      { Name Sys_Ele; NameOfFormulation Electrokinetics_v; }
    }
    Operation {
      Generate[Sys_Ele]; Solve[Sys_Ele]; SaveSolution[Sys_Ele];
    }
  }
}

PostProcessing {
 { Name EleKin_v; NameOfFormulation Electrokinetics_v;
    Quantity {
      { Name v; Value {
          Term { [ {v} ]; In Vol_Ele; Jacobian Vol; }
        }
      }
      { Name e; Value {
          Term { [ -{d v} ]; In Vol_Ele; Jacobian Vol; }
        }
      }
      { Name j; Value {
          Term { [ -sigma[] * {d v} ]; In Vol_Ele; Jacobian Vol; }
        }
      }
      { Name losses; Value {
          Term { [ sigma[] * SquNorm[{d v}] ]; In Vol_Ele; Jacobian Vol; }
        }
      }
      { Name integrated_losses; Value {
          Integral { Type Global;
            [ sigma[] * SquNorm[{d v}] ];
            In Vol_Ele; Jacobian Vol; Integration Int;
          }
	}
      }
      { Name I; Value {
          Term { [ {I} ]; In Sur_Electrodes_Ele; }
        }
      }
      { Name U; Value {
          Term { [ {U} ]; In Sur_Electrodes_Ele; }
        }
      }
      { Name R; Value {
          Term { [ {U}/{I} ]; In Sur_Electrodes_Ele; }
        }
      }
    }
  }
}

PostOperation {
  { Name Map; NameOfPostProcessing EleKin_v;
     Operation {
       Print[ v, OnElementsOf Dom_Hgrad_v_Ele, File "v.pos" ];
       Print[ j, OnElementsOf Dom_Hgrad_v_Ele, File "j.pos" ];
       Print[ losses, OnElementsOf Dom_Hgrad_v_Ele, File "losses.pos" ];
       Print[ I, OnRegion Sur_Electrodes_Ele, File "I.txt" , Format Table];
       Print[ U, OnRegion Sur_Electrodes_Ele, File "U.txt" , Format Table];
       Print[ R, OnRegion ElectrodeIn, Format Table];
       Print[ integrated_losses, OnGlobal , Format Table];
     }
  }
}
