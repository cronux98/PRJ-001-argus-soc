`default_nettype none
`timescale 1ns / 1ps

module hazard_unit (
    input  wire [ 4:0] id_ex_rd_addr_i,
    input  wire        id_ex_mem_read_i,
    input  wire [ 4:0] if_id_rs1_addr_i,
    input  wire [ 4:0] if_id_rs2_addr_i,
    input  wire        branch_taken_i,
    input  wire        jump_i,
    output wire        pc_stall_o,
    output wire        if_id_stall_o,
    output wire        if_id_flush_o,
    output wire        id_ex_flush_o
);

    wire load_use_hazard;
    assign load_use_hazard = id_ex_mem_read_i &&
                             (id_ex_rd_addr_i != 5'b00000) &&
                             (id_ex_rd_addr_i == if_id_rs1_addr_i ||
                              id_ex_rd_addr_i == if_id_rs2_addr_i);

    wire branch_jump_flush;
    assign branch_jump_flush = branch_taken_i | jump_i;

    assign pc_stall_o    = load_use_hazard;
    assign if_id_stall_o = load_use_hazard;
    assign if_id_flush_o = branch_jump_flush;
    assign id_ex_flush_o = load_use_hazard;

endmodule
