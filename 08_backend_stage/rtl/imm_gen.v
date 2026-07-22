`default_nettype none
`timescale 1ns / 1ps
/* verilator lint_off UNUSEDSIGNAL */

module imm_gen (
    input  wire [31:0] instr_i,
    input  wire [ 2:0] imm_src_i,
    output reg  [31:0] imm_o
);

    localparam IMM_I = 3'b000;
    localparam IMM_S = 3'b001;
    localparam IMM_B = 3'b010;
    localparam IMM_U = 3'b011;
    localparam IMM_J = 3'b100;

    always @(*) begin
        case (imm_src_i)
            IMM_I: imm_o = {{20{instr_i[31]}}, instr_i[31:20]};
            IMM_S: imm_o = {{20{instr_i[31]}}, instr_i[31:25], instr_i[11:7]};
            IMM_B: imm_o = {{19{instr_i[31]}}, instr_i[31], instr_i[7], instr_i[30:25], instr_i[11:8], 1'b0};
            IMM_U: imm_o = {instr_i[31:12], 12'h000};
            IMM_J: imm_o = {{11{instr_i[31]}}, instr_i[31], instr_i[19:12], instr_i[20], instr_i[30:21], 1'b0};
            default: imm_o = 32'h0000_0000;
        endcase
    end

endmodule
