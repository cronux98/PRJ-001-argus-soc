`default_nettype none
`timescale 1ns / 1ps

module alu (
    input  wire [31:0] op_a_i,
    input  wire [31:0] op_b_i,
    input  wire [ 3:0] alu_op_i,
    output reg  [31:0] result_o,
    output wire        zero_o
);

    localparam ALU_ADD  = 4'b0000;
    localparam ALU_SUB  = 4'b0001;
    localparam ALU_SLT  = 4'b0010;
    localparam ALU_SLTU = 4'b0011;
    localparam ALU_XOR  = 4'b0100;
    localparam ALU_OR   = 4'b0101;
    localparam ALU_AND  = 4'b0110;
    localparam ALU_SLL  = 4'b0111;
    localparam ALU_SRL  = 4'b1000;
    localparam ALU_SRA  = 4'b1001;
    localparam ALU_LUI  = 4'b1010;
    localparam ALU_PCIM = 4'b1011;

    assign zero_o = (result_o == 32'h0000_0000);

    always @(*) begin
        case (alu_op_i)
            ALU_ADD:  result_o = op_a_i + op_b_i;
            ALU_SUB:  result_o = op_a_i - op_b_i;
            ALU_SLT:  result_o = ($signed(op_a_i) < $signed(op_b_i)) ? 32'h1 : 32'h0;
            ALU_SLTU: result_o = (op_a_i < op_b_i) ? 32'h1 : 32'h0;
            ALU_XOR:  result_o = op_a_i ^ op_b_i;
            ALU_OR:   result_o = op_a_i | op_b_i;
            ALU_AND:  result_o = op_a_i & op_b_i;
            ALU_SLL:  result_o = op_a_i << op_b_i[4:0];
            ALU_SRL:  result_o = op_a_i >> op_b_i[4:0];
            ALU_SRA:  result_o = $signed(op_a_i) >>> op_b_i[4:0];
            ALU_LUI:  result_o = op_b_i;
            ALU_PCIM: result_o = op_a_i + op_b_i;
            default:  result_o = 32'h0000_0000;
        endcase
    end

endmodule
