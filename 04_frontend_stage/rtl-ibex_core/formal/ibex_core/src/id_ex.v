`default_nettype none
`timescale 1ns / 1ps

module id_ex (
    input  wire        clk_i,
    input  wire        rst_ni,
    input  wire        flush_i,
    input  wire [31:0] id_pc_i,
    input  wire [31:0] id_rs1_data_i,
    input  wire [31:0] id_rs2_data_i,
    input  wire [31:0] id_imm_i,
    input  wire [ 4:0] id_rs1_addr_i,
    input  wire [ 4:0] id_rs2_addr_i,
    input  wire [ 4:0] id_rd_addr_i,
    input  wire [ 2:0] id_funct3_i,
    input  wire [ 6:0] id_funct7_i,
    input  wire [ 1:0] id_alu_op_i,
    input  wire        id_alu_src_i,
    input  wire        id_mem_read_i,
    input  wire        id_mem_write_i,
    input  wire        id_branch_i,
    input  wire        id_reg_write_i,
    input  wire        id_mem_to_reg_i,
    input  wire        id_jump_i,
    input  wire        id_is_lui_i,
    input  wire        id_is_auipc_i,
    input  wire [ 1:0] id_result_src_i,
    output reg  [31:0] ex_pc_o,
    output reg  [31:0] ex_rs1_data_o,
    output reg  [31:0] ex_rs2_data_o,
    output reg  [31:0] ex_imm_o,
    output reg  [ 4:0] ex_rs1_addr_o,
    output reg  [ 4:0] ex_rs2_addr_o,
    output reg  [ 4:0] ex_rd_addr_o,
    output reg  [ 2:0] ex_funct3_o,
    output reg  [ 6:0] ex_funct7_o,
    output reg  [ 1:0] ex_alu_op_o,
    output reg         ex_alu_src_o,
    output reg         ex_mem_read_o,
    output reg         ex_mem_write_o,
    output reg         ex_branch_o,
    output reg         ex_reg_write_o,
    output reg         ex_mem_to_reg_o,
    output reg         ex_jump_o,
    output reg         ex_is_lui_o,
    output reg         ex_is_auipc_o,
    output reg  [ 1:0] ex_result_src_o
);

    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            ex_pc_o         <= 32'h0000_0000;
            ex_rs1_data_o   <= 32'h0000_0000;
            ex_rs2_data_o   <= 32'h0000_0000;
            ex_imm_o        <= 32'h0000_0000;
            ex_rs1_addr_o   <= 5'b00000;
            ex_rs2_addr_o   <= 5'b00000;
            ex_rd_addr_o    <= 5'b00000;
            ex_funct3_o     <= 3'b000;
            ex_funct7_o     <= 7'b0000000;
            ex_alu_op_o     <= 2'b00;
            ex_alu_src_o    <= 1'b0;
            ex_mem_read_o   <= 1'b0;
            ex_mem_write_o  <= 1'b0;
            ex_branch_o     <= 1'b0;
            ex_reg_write_o  <= 1'b0;
            ex_mem_to_reg_o <= 1'b0;
            ex_jump_o       <= 1'b0;
            ex_result_src_o <= 2'b00;
            ex_is_lui_o     <= 1'b0;
            ex_is_auipc_o   <= 1'b0;
        end else if (flush_i) begin
            ex_pc_o         <= 32'h0000_0000;
            ex_rs1_data_o   <= 32'h0000_0000;
            ex_rs2_data_o   <= 32'h0000_0000;
            ex_imm_o        <= 32'h0000_0000;
            ex_rs1_addr_o   <= 5'b00000;
            ex_rs2_addr_o   <= 5'b00000;
            ex_rd_addr_o    <= 5'b00000;
            ex_funct3_o     <= 3'b000;
            ex_funct7_o     <= 7'b0000000;
            ex_alu_op_o     <= 2'b00;
            ex_alu_src_o    <= 1'b0;
            ex_mem_read_o   <= 1'b0;
            ex_mem_write_o  <= 1'b0;
            ex_branch_o     <= 1'b0;
            ex_reg_write_o  <= 1'b0;
            ex_mem_to_reg_o <= 1'b0;
            ex_jump_o       <= 1'b0;
            ex_result_src_o <= 2'b00;
            ex_is_lui_o     <= 1'b0;
            ex_is_auipc_o   <= 1'b0;
        end else begin
            ex_pc_o         <= id_pc_i;
            ex_rs1_data_o   <= id_rs1_data_i;
            ex_rs2_data_o   <= id_rs2_data_i;
            ex_imm_o        <= id_imm_i;
            ex_rs1_addr_o   <= id_rs1_addr_i;
            ex_rs2_addr_o   <= id_rs2_addr_i;
            ex_rd_addr_o    <= id_rd_addr_i;
            ex_funct3_o     <= id_funct3_i;
            ex_funct7_o     <= id_funct7_i;
            ex_alu_op_o     <= id_alu_op_i;
            ex_alu_src_o    <= id_alu_src_i;
            ex_mem_read_o   <= id_mem_read_i;
            ex_mem_write_o  <= id_mem_write_i;
            ex_branch_o     <= id_branch_i;
            ex_reg_write_o  <= id_reg_write_i;
            ex_mem_to_reg_o <= id_mem_to_reg_i;
            ex_jump_o       <= id_jump_i;
            ex_result_src_o <= id_result_src_i;
            ex_is_lui_o     <= id_is_lui_i;
            ex_is_auipc_o   <= id_is_auipc_i;
        end
    end

endmodule
