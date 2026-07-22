`default_nettype none
`timescale 1ns / 1ps

module forwarding_unit (
    input  wire [ 4:0] id_ex_rs1_addr_i,
    input  wire [ 4:0] id_ex_rs2_addr_i,
    input  wire [ 4:0] ex_mem_rd_addr_i,
    input  wire        ex_mem_reg_write_i,
    input  wire [ 4:0] mem_wb_rd_addr_i,
    input  wire        mem_wb_reg_write_i,
    output reg  [ 1:0] forward_a_o,
    output reg  [ 1:0] forward_b_o
);

    always @(*) begin
        forward_a_o = 2'b00;
        if (ex_mem_reg_write_i && ex_mem_rd_addr_i != 5'b00000 &&
            ex_mem_rd_addr_i == id_ex_rs1_addr_i) begin
            forward_a_o = 2'b10;
        end else if (mem_wb_reg_write_i && mem_wb_rd_addr_i != 5'b00000 &&
                     mem_wb_rd_addr_i == id_ex_rs1_addr_i) begin
            forward_a_o = 2'b01;
        end
    end

    always @(*) begin
        forward_b_o = 2'b00;
        if (ex_mem_reg_write_i && ex_mem_rd_addr_i != 5'b00000 &&
            ex_mem_rd_addr_i == id_ex_rs2_addr_i) begin
            forward_b_o = 2'b10;
        end else if (mem_wb_reg_write_i && mem_wb_rd_addr_i != 5'b00000 &&
                     mem_wb_rd_addr_i == id_ex_rs2_addr_i) begin
            forward_b_o = 2'b01;
        end
    end

endmodule
