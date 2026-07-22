`default_nettype none
`timescale 1ns / 1ps

module ctrl_unit (
    input  wire [ 6:0] opcode_i,
    output reg  [ 1:0] alu_op_o,
    output reg         alu_src_o,
    output reg         mem_read_o,
    output reg         mem_write_o,
    output reg         branch_o,
    output reg         reg_write_o,
    output reg         mem_to_reg_o,
    output reg         jump_o,
    output reg  [ 1:0] result_src_o,
    output reg  [ 2:0] imm_src_o,
    output reg         is_lui_o,
    output reg         is_auipc_o
);

    localparam OP_RTYPE  = 7'b0110011;
    localparam OP_I_ALU  = 7'b0010011;
    localparam OP_LOAD   = 7'b0000011;
    localparam OP_STORE  = 7'b0100011;
    localparam OP_BRANCH = 7'b1100011;
    localparam OP_LUI    = 7'b0110111;
    localparam OP_AUIPC  = 7'b0010111;
    localparam OP_JAL    = 7'b1101111;
    localparam OP_JALR   = 7'b1100111;

    always @(*) begin
        alu_op_o     = 2'b00;
        alu_src_o    = 1'b0;
        mem_read_o   = 1'b0;
        mem_write_o  = 1'b0;
        branch_o     = 1'b0;
        reg_write_o  = 1'b0;
        mem_to_reg_o = 1'b0;
        jump_o       = 1'b0;
        result_src_o = 2'b00;
        imm_src_o    = 3'b000;
        is_lui_o     = 1'b0;
        is_auipc_o   = 1'b0;

        case (opcode_i)
            OP_RTYPE: begin
                alu_op_o     = 2'b10;
                reg_write_o  = 1'b1;
            end
            OP_I_ALU: begin
                alu_op_o     = 2'b11;
                alu_src_o    = 1'b1;
                reg_write_o  = 1'b1;
                imm_src_o    = 3'b000;
        is_lui_o     = 1'b0;
            end
            OP_LOAD: begin
                alu_src_o    = 1'b1;
                mem_read_o   = 1'b1;
                reg_write_o  = 1'b1;
                mem_to_reg_o = 1'b1;
                result_src_o = 2'b01;
                imm_src_o    = 3'b000;
        is_lui_o     = 1'b0;
            end
            OP_STORE: begin
                alu_src_o    = 1'b1;
                mem_write_o  = 1'b1;
                imm_src_o    = 3'b001;
            end
            OP_BRANCH: begin
                alu_op_o     = 2'b01;
                branch_o     = 1'b1;
                imm_src_o    = 3'b010;
            end
            OP_LUI: begin
                alu_src_o    = 1'b1;
                reg_write_o  = 1'b1;
                imm_src_o    = 3'b011;
                is_lui_o     = 1'b1;
            end
            OP_AUIPC: begin
                reg_write_o  = 1'b1;
                imm_src_o    = 3'b011;
                is_auipc_o   = 1'b1;
            end
            OP_JAL: begin
                reg_write_o  = 1'b1;
                jump_o       = 1'b1;
                result_src_o = 2'b10;
                imm_src_o    = 3'b100;
            end
            OP_JALR: begin
                alu_src_o    = 1'b1;
                reg_write_o  = 1'b1;
                jump_o       = 1'b1;
                result_src_o = 2'b10;
                imm_src_o    = 3'b000;
        is_lui_o     = 1'b0;
            end
            default: begin
            end
        endcase
    end

endmodule
