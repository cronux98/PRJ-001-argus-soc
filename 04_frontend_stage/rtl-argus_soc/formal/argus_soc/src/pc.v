`default_nettype none
`timescale 1ns / 1ps

module pc (
    input  wire        clk_i,
    input  wire        rst_ni,
    input  wire        stall_i,
    input  wire [31:0] pc_next_i,
    output reg  [31:0] pc_o
);

    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            pc_o <= 32'h0000_0000;
        end else if (!stall_i) begin
            pc_o <= pc_next_i;
        end
    end

endmodule
