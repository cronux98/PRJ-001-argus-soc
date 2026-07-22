`default_nettype none
`timescale 1ns / 1ps

module branch_unit (
    input  wire [31:0] rs1_data_i,
    input  wire [31:0] rs2_data_i,
    input  wire [ 2:0] branch_type_i,
    input  wire        branch_en_i,
    output reg         branch_taken_o
);

    always @(*) begin
        branch_taken_o = 1'b0;
        if (branch_en_i) begin
            case (branch_type_i)
                3'b000: branch_taken_o = (rs1_data_i == rs2_data_i);
                3'b001: branch_taken_o = (rs1_data_i != rs2_data_i);
                3'b100: branch_taken_o = ($signed(rs1_data_i) < $signed(rs2_data_i));
                3'b101: branch_taken_o = ($signed(rs1_data_i) >= $signed(rs2_data_i));
                3'b110: branch_taken_o = (rs1_data_i < rs2_data_i);
                3'b111: branch_taken_o = (rs1_data_i >= rs2_data_i);
                default: branch_taken_o = 1'b0;
            endcase
        end
    end

endmodule
