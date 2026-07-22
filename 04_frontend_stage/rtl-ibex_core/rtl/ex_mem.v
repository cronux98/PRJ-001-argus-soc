`default_nettype none
`timescale 1ns / 1ps

module ex_mem (
    input  wire        clk_i,
    input  wire        rst_ni,
    input  wire [31:0] ex_alu_result_i,
    input  wire [31:0] ex_rs2_data_i,
    input  wire [ 4:0] ex_rd_addr_i,
    input  wire [ 2:0] ex_funct3_i,
    input  wire        ex_mem_read_i,
    input  wire        ex_mem_write_i,
    input  wire        ex_reg_write_i,
    input  wire        ex_mem_to_reg_i,
    input  wire [ 1:0] ex_result_src_i,
    output reg  [31:0] mem_alu_result_o,
    output reg  [31:0] mem_rs2_data_o,
    output reg  [ 4:0] mem_rd_addr_o,
    output reg  [ 2:0] mem_funct3_o,
    output reg         mem_mem_read_o,
    output reg         mem_mem_write_o,
    output reg         mem_reg_write_o,
    output reg         mem_mem_to_reg_o,
    output reg  [ 1:0] mem_result_src_o
);

    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            mem_alu_result_o  <= 32'h0000_0000;
            mem_rs2_data_o    <= 32'h0000_0000;
            mem_rd_addr_o     <= 5'b00000;
            mem_funct3_o      <= 3'b000;
            mem_mem_read_o    <= 1'b0;
            mem_mem_write_o   <= 1'b0;
            mem_reg_write_o   <= 1'b0;
            mem_mem_to_reg_o  <= 1'b0;
            mem_result_src_o  <= 2'b00;
        end else begin
            mem_alu_result_o  <= ex_alu_result_i;
            mem_rs2_data_o    <= ex_rs2_data_i;
            mem_rd_addr_o     <= ex_rd_addr_i;
            mem_funct3_o      <= ex_funct3_i;
            mem_mem_read_o    <= ex_mem_read_i;
            mem_mem_write_o   <= ex_mem_write_i;
            mem_reg_write_o   <= ex_reg_write_i;
            mem_mem_to_reg_o  <= ex_mem_to_reg_i;
            mem_result_src_o  <= ex_result_src_i;
        end
    end

endmodule
