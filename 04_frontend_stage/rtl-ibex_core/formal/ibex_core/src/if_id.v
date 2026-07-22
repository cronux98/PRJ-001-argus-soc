`default_nettype none
`timescale 1ns / 1ps

module if_id (
    input  wire        clk_i,
    input  wire        rst_ni,
    input  wire        stall_i,
    input  wire        flush_i,
    input  wire [31:0] if_pc_i,
    input  wire [31:0] if_pc_plus4_i,
    input  wire [31:0] if_instr_i,
    output reg  [31:0] id_pc_o,
    output reg  [31:0] id_pc_plus4_o,
    output reg  [31:0] id_instr_o
);

    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            id_pc_o       <= 32'h0000_0000;
            id_pc_plus4_o <= 32'h0000_0000;
            id_instr_o    <= 32'h0000_0000;
        end else if (flush_i) begin
            id_pc_o       <= 32'h0000_0000;
            id_pc_plus4_o <= 32'h0000_0000;
            id_instr_o    <= 32'h0000_0000;
        end else if (!stall_i) begin
            id_pc_o       <= if_pc_i;
            id_pc_plus4_o <= if_pc_plus4_i;
            id_instr_o    <= if_instr_i;
        end
    end

endmodule
