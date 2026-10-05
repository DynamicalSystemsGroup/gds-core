// Experimental GDS structural view; see companion mapping manifest.
package GDSExport {
    item def Payload0 {
        attribute field0 : ScalarValues::Real;
    }
    port def Channel0 {
        out item payload : Payload0;
    }
    item def Payload1 {
        attribute field0 : ScalarValues::Real;
    }
    port def Channel1 {
        out item payload : Payload1;
    }
    item def Payload2 {
        attribute field0 : ScalarValues::Real;
        attribute field1 : ScalarValues::Real;
    }
    port def Channel2 {
        out item payload : Payload2;
    }
    item def Payload3 {
        attribute field0 : ScalarValues::Real;
    }
    port def Channel3 {
        out item payload : Payload3;
    }
    part system {
        part block0 {
            port forward_in0 : ~Channel3;
            port forward_out0 : Channel0;
        }
        part block1 {
            port forward_in0 : ~Channel0;
            port forward_out0 : Channel2;
        }
        part block2 {
            port forward_out0 : Channel3;
        }
        part block3 {
            port forward_in0 : ~Channel2;
        }
        connection wire0 connect block2.forward_out0 to block0.forward_in0;
        connection wire1 connect block0.forward_out0 to block1.forward_in0;
        connection wire2 connect block1.forward_out0 to block3.forward_in0;
    }
}
