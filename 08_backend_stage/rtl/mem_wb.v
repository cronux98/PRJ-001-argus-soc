`default_nettype none
`timescale 1ns / 1ps

module mem_wb (
    input  wire        clk_i,
    input  wire        rst_ni,
    input  wire [31:0] mem_alu_result_i,
    input  wire [31:0] mem_mem_data_i,
    input  wire [ 4:0] mem_rd_addr_i,
    input  wire        mem_reg_write_i,
    input  wire        mem_mem_to_reg_i,
    input  wire [ 1:0] mem_result_src_i,
    output reg  [31:0] wb_alu_result_o,
    output reg  [31:0] wb_mem_data_o,
    output reg  [ 4:0] wb_rd_addr_o,
    output reg         wb_reg_write_o,
    output reg         wb_mem_to_reg_o,
    output reg  [ 1:0] wb_result_src_o
);

    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            wb_alu_result_o  <= 32'h0000_0000;
            wb_mem_data_o    <= 32'h0000_0000;
            wb_rd_addr_o     <= 5'b00000;
            wb_reg_write_o   <= 1'b0;
            wb_mem_to_reg_o  <= 1'b0;
            wb_result_src_o  <= 2'b00;
        end else begin
            wb_alu_result_o  <= mem_alu_result_i;
            wb_mem_data_o    <= mem_mem_data_i;
            wb_rd_addr_o     <= mem_rd_addr_i;
            wb_reg_write_o   <= mem_reg_write_i;
            wb_mem_to_reg_o  <= mem_mem_to_reg_i;
            wb_result_src_o  <= mem_result_src_i;
        end
    end

endmodule
