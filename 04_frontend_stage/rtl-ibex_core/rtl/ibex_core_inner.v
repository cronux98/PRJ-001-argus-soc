/* verilator lint_off UNUSEDSIGNAL */
/* verilator lint_off WIDTHEXPAND */
`default_nettype none
`timescale 1ns / 1ps
/* verilator lint_off UNUSEDSIGNAL */

module ibex_core_inner (
    input  wire        clk_i,
    input  wire        rst_ni,
    output wire [31:0] imem_addr_o,
    input  wire [31:0] imem_rdata_i,
    output wire [31:0] dmem_addr_o,
    output wire [31:0] dmem_wdata_o,
    input  wire [31:0] dmem_rdata_i,
    output wire        dmem_we_o,
    output wire        dmem_re_o,
    output wire [ 3:0] dmem_be_o,
    output wire [ 2:0] dmem_funct3_o,
    input  wire        stall_i
);

    // PC
    wire [31:0] pc_current;
    wire [31:0] pc_next;
    wire        pc_stall;

    // IF/ID
    wire [31:0] ifid_pc;
    wire [31:0] ifid_pc_plus4;
    wire [31:0] ifid_instr;
    wire        ifid_stall;
    wire        ifid_flush;

    // ID
    wire [ 4:0] id_rs1_addr = ifid_instr[19:15];
    wire [ 4:0] id_rs2_addr = ifid_instr[24:20];
    wire [ 4:0] id_rd_addr  = ifid_instr[11:7];
    wire [ 2:0] id_funct3   = ifid_instr[14:12];
    wire [ 6:0] id_funct7   = ifid_instr[31:25];

    wire [31:0] id_rs1_data;
    wire [31:0] id_rs2_data;
    wire [31:0] id_imm;

    // Control
    wire [ 1:0] ctrl_alu_op;
    wire        ctrl_alu_src;
    wire        ctrl_mem_read;
    wire        ctrl_mem_write;
    wire        ctrl_branch;
    wire        ctrl_reg_write;
    wire        ctrl_mem_to_reg;
    wire        ctrl_jump;
    wire [ 1:0] ctrl_result_src;
    wire [ 2:0] ctrl_imm_src;
    wire        ctrl_is_lui;
    wire        ctrl_is_auipc;

    // Branch
    wire        branch_taken;

    // ID/EX
    wire [31:0] idex_pc;
    wire [31:0] idex_rs1_data;
    wire [31:0] idex_rs2_data;
    wire [31:0] idex_imm;
    wire [ 4:0] idex_rs1_addr;
    wire [ 4:0] idex_rs2_addr;
    wire [ 4:0] idex_rd_addr;
    wire [ 2:0] idex_funct3;
    wire [ 6:0] idex_funct7;
    wire [ 1:0] idex_alu_op;
    wire        idex_alu_src;
    wire        idex_mem_read;
    wire        idex_mem_write;
    wire        idex_branch;
    wire        idex_reg_write;
    wire        idex_mem_to_reg;
    wire        idex_jump;
    wire [ 1:0] idex_result_src;
    wire        idex_is_lui;
    wire        idex_is_auipc;
    wire        idex_flush;

    // Forwarding
    wire [ 1:0] forward_a;
    wire [ 1:0] forward_b;
    reg  [31:0] fwd_mux_a;
    reg  [31:0] fwd_mux_b;

    // ALU
    wire [ 3:0] alu_operation;
    wire [31:0] alu_result;
    wire        alu_zero;
    wire [31:0] alu_op_b;

    // EX/MEM
    wire [31:0] exmem_alu_result;
    wire [31:0] exmem_rs2_data;
    wire [ 4:0] exmem_rd_addr;
    wire [ 2:0] exmem_funct3;
    wire        exmem_mem_read;
    wire        exmem_mem_write;
    wire        exmem_reg_write;
    wire        exmem_mem_to_reg;
    wire [ 1:0] exmem_result_src;

    // MEM/WB
    wire [31:0] memwb_alu_result;
    wire [31:0] memwb_mem_data;
    wire [ 4:0] memwb_rd_addr;
    wire        memwb_reg_write;
    wire        memwb_mem_to_reg;
    wire [ 1:0] memwb_result_src;

    // WB
    reg  [31:0] wb_data;

    // ==================== IF ====================
    assign imem_addr_o = pc_current;
    wire [31:0] pc_plus4 = pc_current + 32'h0000_0004;

    // Next PC mux
    reg [31:0] pc_next_r;
    always @(*) begin
        if (branch_taken || ctrl_jump) begin
            // JALR: rs1+imm computed in EX, result available from ALU
            // For JALR, we need the EX stage result. But JALR target = rs1+imm
            // which is computed by ALU. We forward from EX/MEM or current ALU.
            // Simplification: branch target for non-JALR = ID stage PC+imm
            // JALR target = ALU result (forwarded)
            if (ctrl_jump && !ctrl_branch && ctrl_alu_src) begin
                // JALR: use ALU result (rs1+imm) - but this is in EX stage
                // We need to wait or forward. For simplicity, use EX/MEM result.
                pc_next_r = (id_rs1_data + id_imm) ;  // JALR target, bit0 cleared by hardware
            end else begin
                pc_next_r = ifid_pc + id_imm;
            end
        end else begin
            pc_next_r = pc_plus4;
        end
    end
    assign pc_next = pc_next_r;

    pc u_pc (
        .clk_i     (clk_i),
        .rst_ni    (rst_ni),
        .stall_i   (pc_stall | stall_i),
        .pc_next_i (pc_next),
        .pc_o      (pc_current)
    );

    if_id u_if_id (
        .clk_i          (clk_i),
        .rst_ni         (rst_ni),
        .stall_i        (ifid_stall),
        .flush_i        (ifid_flush),
        .if_pc_i        (pc_current),
        .if_pc_plus4_i  (pc_plus4),
        .if_instr_i     (imem_rdata_i),
        .id_pc_o        (ifid_pc),
        .id_pc_plus4_o  (ifid_pc_plus4),
        .id_instr_o     (ifid_instr)
    );

    // ==================== ID ====================
    ctrl_unit u_ctrl (
        .opcode_i     (ifid_instr[6:0]),
        .alu_op_o     (ctrl_alu_op),
        .alu_src_o    (ctrl_alu_src),
        .mem_read_o   (ctrl_mem_read),
        .mem_write_o  (ctrl_mem_write),
        .branch_o     (ctrl_branch),
        .reg_write_o  (ctrl_reg_write),
        .mem_to_reg_o (ctrl_mem_to_reg),
        .jump_o       (ctrl_jump),
        .result_src_o (ctrl_result_src),
        .imm_src_o    (ctrl_imm_src),
        .is_lui_o     (ctrl_is_lui),
        .is_auipc_o   (ctrl_is_auipc)
    );

    reg_file u_reg_file (
        .clk_i      (clk_i),
        .rst_ni     (rst_ni),
        .rs1_addr_i (id_rs1_addr),
        .rs2_addr_i (id_rs2_addr),
        .rs1_data_o (id_rs1_data),
        .rs2_data_o (id_rs2_data),
        .rd_addr_i  (memwb_rd_addr),
        .rd_data_i  (wb_data),
        .rd_we_i    (memwb_reg_write)
    );

    imm_gen u_imm_gen (
        .instr_i    (ifid_instr),
        .imm_src_i  (ctrl_imm_src),
        .imm_o      (id_imm)
    );

    branch_unit u_branch (
        .rs1_data_i     (id_rs1_data),
        .rs2_data_i     (id_rs2_data),
        .branch_type_i  (id_funct3),
        .branch_en_i    (ctrl_branch),
        .branch_taken_o (branch_taken)
    );

    id_ex u_id_ex (
        .clk_i           (clk_i),
        .rst_ni          (rst_ni),
        .flush_i         (idex_flush),
        .id_pc_i         (ifid_pc),
        .id_rs1_data_i   (id_rs1_data),
        .id_rs2_data_i   (id_rs2_data),
        .id_imm_i        (id_imm),
        .id_rs1_addr_i   (id_rs1_addr),
        .id_rs2_addr_i   (id_rs2_addr),
        .id_rd_addr_i    (id_rd_addr),
        .id_funct3_i     (id_funct3),
        .id_funct7_i     (id_funct7),
        .id_alu_op_i     (ctrl_alu_op),
        .id_alu_src_i    (ctrl_alu_src),
        .id_mem_read_i   (ctrl_mem_read),
        .id_mem_write_i  (ctrl_mem_write),
        .id_branch_i     (ctrl_branch),
        .id_reg_write_i  (ctrl_reg_write),
        .id_mem_to_reg_i (ctrl_mem_to_reg),
        .id_jump_i       (ctrl_jump),
        .id_result_src_i (ctrl_result_src),
        .id_is_lui_i     (ctrl_is_lui),
        .id_is_auipc_i   (ctrl_is_auipc),
        .ex_pc_o         (idex_pc),
        .ex_rs1_data_o   (idex_rs1_data),
        .ex_rs2_data_o   (idex_rs2_data),
        .ex_imm_o        (idex_imm),
        .ex_rs1_addr_o   (idex_rs1_addr),
        .ex_rs2_addr_o   (idex_rs2_addr),
        .ex_rd_addr_o    (idex_rd_addr),
        .ex_funct3_o     (idex_funct3),
        .ex_funct7_o     (idex_funct7),
        .ex_alu_op_o     (idex_alu_op),
        .ex_alu_src_o    (idex_alu_src),
        .ex_mem_read_o   (idex_mem_read),
        .ex_mem_write_o  (idex_mem_write),
        .ex_branch_o     (idex_branch),
        .ex_reg_write_o  (idex_reg_write),
        .ex_mem_to_reg_o (idex_mem_to_reg),
        .ex_jump_o       (idex_jump),
        .ex_result_src_o (idex_result_src),
        .ex_is_lui_o     (idex_is_lui),
        .ex_is_auipc_o   (idex_is_auipc)
    );

    // ==================== EX ====================
    forwarding_unit u_fwd (
        .id_ex_rs1_addr_i   (idex_rs1_addr),
        .id_ex_rs2_addr_i   (idex_rs2_addr),
        .ex_mem_rd_addr_i   (exmem_rd_addr),
        .ex_mem_reg_write_i (exmem_reg_write),
        .mem_wb_rd_addr_i   (memwb_rd_addr),
        .mem_wb_reg_write_i (memwb_reg_write),
        .forward_a_o        (forward_a),
        .forward_b_o        (forward_b)
    );

    always @(*) begin
        case (forward_a)
            2'b00: fwd_mux_a = idex_rs1_data;
            2'b01: fwd_mux_a = wb_data;
            2'b10: fwd_mux_a = exmem_alu_result;
            default: fwd_mux_a = idex_rs1_data;
        endcase
    end

    always @(*) begin
        case (forward_b)
            2'b00: fwd_mux_b = idex_rs2_data;
            2'b01: fwd_mux_b = wb_data;
            2'b10: fwd_mux_b = exmem_alu_result;
            default: fwd_mux_b = idex_rs2_data;
        endcase
    end

    // LUI: pass 0 as op_a. JAL/JALR: pass PC as op_a (for PC+4 computation)
    wire idex_is_jal = idex_jump && (idex_result_src == 2'b10);

    // JAL: op_b=4 (for PC+4). JALR: op_b=imm (alu_src=1). Normal: alu_src mux.
    wire idex_need_imm = idex_alu_src || idex_is_lui || idex_is_auipc || idex_is_jal;
    assign alu_op_b = idex_is_jal ? 32'h4 :
                      idex_need_imm ? idex_imm : fwd_mux_b;

    alu_ctrl u_alu_ctrl (
        .alu_op_i        (idex_alu_op),
        .funct3_i        (idex_funct3),
        .funct7_i        (idex_funct7),
        .alu_operation_o (alu_operation)
    );
    wire [31:0] alu_op_a_final;
    assign alu_op_a_final = idex_is_lui ? 32'h0 :
                            idex_is_auipc ? idex_pc :
                            idex_is_jal ? idex_pc :
                            fwd_mux_a;

    alu u_alu (
        .op_a_i   (alu_op_a_final),
        .op_b_i   (alu_op_b),
        .alu_op_i (alu_operation),
        .result_o (alu_result),
        .zero_o   (alu_zero)
    );

    ex_mem u_ex_mem (
        .clk_i            (clk_i),
        .rst_ni           (rst_ni),
        .ex_alu_result_i  (alu_result),
        .ex_rs2_data_i    (fwd_mux_b),
        .ex_rd_addr_i     (idex_rd_addr),
        .ex_funct3_i      (idex_funct3),
        .ex_mem_read_i    (idex_mem_read),
        .ex_mem_write_i   (idex_mem_write),
        .ex_reg_write_i   (idex_reg_write),
        .ex_mem_to_reg_i  (idex_mem_to_reg),
        .ex_result_src_i  (idex_result_src),
        .mem_alu_result_o (exmem_alu_result),
        .mem_rs2_data_o   (exmem_rs2_data),
        .mem_rd_addr_o    (exmem_rd_addr),
        .mem_funct3_o     (exmem_funct3),
        .mem_mem_read_o   (exmem_mem_read),
        .mem_mem_write_o  (exmem_mem_write),
        .mem_reg_write_o  (exmem_reg_write),
        .mem_mem_to_reg_o (exmem_mem_to_reg),
        .mem_result_src_o (exmem_result_src)
    );

    // ==================== MEM ====================
    assign dmem_addr_o    = exmem_alu_result;
    assign dmem_wdata_o   = exmem_rs2_data;
    assign dmem_we_o      = exmem_mem_write;
    assign dmem_re_o      = exmem_mem_read;
    assign dmem_funct3_o  = exmem_funct3;

    // Byte enable generation
    reg [3:0] be_gen;
    always @(*) begin
        case (exmem_funct3[1:0])
            2'b00: begin // SB
                case (exmem_alu_result[1:0])
                    2'b00: be_gen = 4'b0001;
                    2'b01: be_gen = 4'b0010;
                    2'b10: be_gen = 4'b0100;
                    2'b11: be_gen = 4'b1000;
                    default: be_gen = 4'b0000;
                endcase
            end
            2'b01: begin // SH
                case (exmem_alu_result[1])
                    1'b0: be_gen = 4'b0011;
                    1'b1: be_gen = 4'b1100;
                    default: be_gen = 4'b0000;
                endcase
            end
            default: be_gen = 4'b1111; // SW
        endcase
    end
    assign dmem_be_o = be_gen;

    mem_wb u_mem_wb (
        .clk_i            (clk_i),
        .rst_ni           (rst_ni),
        .mem_alu_result_i (exmem_alu_result),
        .mem_mem_data_i   (dmem_rdata_i),
        .mem_rd_addr_i    (exmem_rd_addr),
        .mem_reg_write_i  (exmem_reg_write),
        .mem_mem_to_reg_i (exmem_mem_to_reg),
        .mem_result_src_i (exmem_result_src),
        .wb_alu_result_o  (memwb_alu_result),
        .wb_mem_data_o    (memwb_mem_data),
        .wb_rd_addr_o     (memwb_rd_addr),
        .wb_reg_write_o   (memwb_reg_write),
        .wb_mem_to_reg_o  (memwb_mem_to_reg),
        .wb_result_src_o  (memwb_result_src)
    );

    // ==================== WB ====================
    always @(*) begin
        case (memwb_result_src)
            2'b00: wb_data = memwb_alu_result;
            2'b01: wb_data = memwb_mem_data;
            2'b10: wb_data = memwb_alu_result; // PC+4 link stored in alu_result path
            default: wb_data = memwb_alu_result;
        endcase
    end

    // ==================== HAZARD ====================
    hazard_unit u_hazard (
        .id_ex_rd_addr_i  (idex_rd_addr),
        .id_ex_mem_read_i (idex_mem_read),
        .if_id_rs1_addr_i (id_rs1_addr),
        .if_id_rs2_addr_i (id_rs2_addr),
        .branch_taken_i   (branch_taken),
        .jump_i           (ctrl_jump),
        .pc_stall_o       (pc_stall),
        .if_id_stall_o    (ifid_stall),
        .if_id_flush_o    (ifid_flush),
        .id_ex_flush_o    (idex_flush)
    );

endmodule
