pragma circom 2.0.0;

include "circomlib/circuits/comparators.circom";

template Main() {
    signal input a;
    signal input b;
    signal output out;

    component lt = LessThan(8); // 8-bit comparison
    lt.in[0] <== a;
    lt.in[1] <== b;
    out <== lt.out;
}

component main = Main();
