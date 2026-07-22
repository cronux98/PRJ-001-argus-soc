`default_nettype none
`timescale 1ns / 1ps
/* verilator lint_off UNUSEDSIGNAL */

module alu_ctrl (
    input  wire [ 1:0] alu_op_i,
    input  wire [ 2:0] funct3_i,
    input  wire [ 6:0] funct7_i,
    output reg  [ 3:0] alu_operation_o
);

    always @(*) begin
        case (alu_op_i)
            2'b00: alu_operation_o = 4'b0000;
            2'b01: alu_operation_o = 4'b0001;
            2'b10: begin
                case (funct3_i)
                    3'b000: alu_operation_o = (funct7_i[5]) ? 4'b0001 : 4'b0000;
                    3'b001: alu_operation_o = 4'b0111;
                    3'b010: alu_operation_o = 4'b0010;
                    3'b011: alu_operation_o = 4'b0011;
                    3'b100: alu_operation_o = 4'b0100;
                    3'b101: alu_operation_o = (funct7_i[5]) ? 4'b1001 : 4'b1000;
                    3'b110: alu_operation_o = 4'b0101;
                    3'b111: alu_operation_o = 4'b0110;
                    default: alu_operation_o = 4'b0000;
                endcase
            end
            2'b11: begin
                case (funct3_i)
                    3'b000: alu_operation_o = 4'b0000;
                    3'b001: alu_operation_o = 4'b0111;
                    3'b010: alu_operation_o = 4'b0010;
                    3'b011: alu_operation_o = 4'b0011;
                    3'b100: alu_operation_o = 4'b0100;
                    3'b101: alu_operation_o = (funct7_i[5]) ? 4'b1001 : 4'b1000;
                    3'b110: alu_operation_o = 4'b0101;
                    3'b111: alu_operation_o = 4'b0110;
                    default: alu_operation_o = 4'b0000;
                endcase
            end
            default: alu_operation_o = 4'b0000;
        endcase
    end

endmodule
