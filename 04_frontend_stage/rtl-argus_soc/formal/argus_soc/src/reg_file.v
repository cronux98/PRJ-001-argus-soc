`default_nettype none
`timescale 1ns / 1ps

module reg_file (
    input  wire        clk_i,
    input  wire        rst_ni,
    input  wire [ 4:0] rs1_addr_i,
    input  wire [ 4:0] rs2_addr_i,
    output wire [31:0] rs1_data_o,
    output wire [31:0] rs2_data_o,
    input  wire [ 4:0] rd_addr_i,
    input  wire [31:0] rd_data_i,
    input  wire        rd_we_i
);

    reg [31:0] regs [1:31];

    assign rs1_data_o = (rs1_addr_i == 5'b00000) ? 32'h0000_0000 :
                        (rd_we_i && rd_addr_i == rs1_addr_i) ? rd_data_i :
                        regs[rs1_addr_i];

    assign rs2_data_o = (rs2_addr_i == 5'b00000) ? 32'h0000_0000 :
                        (rd_we_i && rd_addr_i == rs2_addr_i) ? rd_data_i :
                        regs[rs2_addr_i];

    integer i;
    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            for (i = 1; i < 32; i = i + 1) begin
                regs[i] <= 32'h0000_0000;
            end
        end else if (rd_we_i && rd_addr_i != 5'b00000) begin
            regs[rd_addr_i] <= rd_data_i;
        end
    end

endmodule
