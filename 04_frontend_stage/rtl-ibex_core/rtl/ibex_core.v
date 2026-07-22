// =========================================================================
// Module: ibex_core
// Description: Ibex RV32I wrapper — wraps ibex_core_inner with interrupt
//              support and memory interface adaptation for direct SRAM access.
//              Based on PRJ-003 verified ibex_core_inner.
//
// Source: PRJ-001 Architecture §3.1 (M01), REUSE from PRJ-003
// =========================================================================

`default_nettype none
`timescale 1ns / 1ps

module ibex_core (
    input  wire        clk_i,
    input  wire        rst_ni,

    // Instruction memory interface
    output wire        instr_req_o,
    output wire [31:0] instr_addr_o,
    input  wire [31:0] instr_rdata_i,
    input  wire        instr_rvalid_i,

    // Data memory interface
    output wire        data_req_o,
    output wire [31:0] data_addr_o,
    output wire [31:0] data_wdata_o,
    input  wire [31:0] data_rdata_i,
    output wire        data_we_o,
    output wire [ 3:0] data_be_o,
    input  wire        data_rvalid_i,

    // Interrupts
    input  wire        irq_software_i,
    input  wire        irq_timer_i,
    input  wire        irq_external_i,
    input  wire [14:0] irq_fast_i,

    // Debug
    input  wire        debug_req_i,

    // Sleep output
    output wire        core_sleep_o
);

    // ── Interrupt and WFI handling ────────────────────────────────────
    // MIE — Machine Interrupt Enable (simplified CSR)
    reg        mie_meie;       // MIE.MEIE bit
    reg        mstatus_mie;    // MSTATUS.MIE bit
    reg        in_wfi;
    reg [31:0] mepc;           // Machine exception PC
    reg [31:0] mtvec;          // Machine trap vector
    reg [31:0] mcause;         // Machine trap cause

    // CSR addresses (simplified 12-bit)
    localparam CSR_MSTATUS  = 12'h300;
    localparam CSR_MIE      = 12'h304;
    localparam CSR_MTVEC    = 12'h305;
    localparam CSR_MEPC     = 12'h341;
    localparam CSR_MCAUSE   = 12'h342;
    localparam CSR_MIP      = 12'h344;

    // ── Decode WFI and CSRRW instructions ─────────────────────────────
    wire [31:0] if_instr = instr_rdata_i;
    wire        is_wfi  = (if_instr == 32'h1050_0073);  // WFI
    wire        is_csrrw = (if_instr[6:0] == 7'b1110011) && (if_instr[14:12] == 3'b001);
    wire        is_mret  = (if_instr == 32'h3020_0073);  // MRET
    wire [11:0] csr_addr = if_instr[31:20];

    // ── Core internal signals ─────────────────────────────────────────
    wire [31:0] imem_addr_inner;
    wire [31:0] dmem_addr_inner;
    wire [31:0] dmem_wdata_inner;
    wire [31:0] dmem_rdata_inner;
    wire        dmem_we_inner;
    wire        dmem_re_inner;
    wire [ 3:0] dmem_be_inner;
    wire [ 2:0] dmem_funct3_inner;
    wire        stall_inner;

    // ── Stall the core when in WFI or taking trap ─────────────────────
    reg  taking_trap;
    wire core_stall = in_wfi || taking_trap;

    assign stall_inner = core_stall || !instr_rvalid_i || (!data_rvalid_i && (dmem_re_inner || dmem_we_inner));

    // ── Instantiate the inner core ────────────────────────────────────
    ibex_core_inner u_core (
        .clk_i          (clk_i),
        .rst_ni         (rst_ni),
        .imem_addr_o    (imem_addr_inner),
        .imem_rdata_i   (instr_rdata_i),
        .dmem_addr_o    (dmem_addr_inner),
        .dmem_wdata_o   (dmem_wdata_inner),
        .dmem_rdata_i   (dmem_rdata_inner),
        .dmem_we_o      (dmem_we_inner),
        .dmem_re_o      (dmem_re_inner),
        .dmem_be_o      (dmem_be_inner),
        .dmem_funct3_o  (dmem_funct3_inner),
        .stall_i        (stall_inner)
    );

    // ── Memory interface adaptation ───────────────────────────────────
    // Instruction port: always requesting, SRAM is zero-wait-state
    assign instr_req_o  = !in_wfi;
    assign instr_addr_o = imem_addr_inner;

    // Data port
    assign data_req_o   = dmem_re_inner || dmem_we_inner;
    assign data_addr_o  = dmem_addr_inner;
    assign data_wdata_o = dmem_wdata_inner;
    assign data_we_o    = dmem_we_inner;
    assign data_be_o    = dmem_be_inner;
    assign dmem_rdata_inner = data_rdata_i;

    // ── Interrupt / Trap state machine ────────────────────────────────
    wire irq_pending = irq_external_i && mie_meie && mstatus_mie;

    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            mie_meie     <= 1'b0;
            mstatus_mie  <= 1'b0;
            in_wfi       <= 1'b0;
            taking_trap  <= 1'b0;
            mepc         <= 32'h0000_0000;
            mtvec        <= 32'h0000_0000;
            mcause       <= 32'h0000_0000;
        end else begin
            // CSR writes (during EX stage of CSRRW)
            if (dmem_we_inner && dmem_addr_inner == 32'h0000_0000 && is_csrrw) begin
                case (csr_addr)
                    CSR_MSTATUS: begin
                        mstatus_mie <= dmem_wdata_inner[3];
                    end
                    CSR_MIE: begin
                        mie_meie <= dmem_wdata_inner[11];  // MEIE bit
                    end
                    CSR_MTVEC: mtvec <= {dmem_wdata_inner[31:2], 2'b00};
                    default: ;
                endcase
            end

            // WFI execution
            if (is_wfi && !in_wfi && !core_stall)
                in_wfi <= 1'b1;

            // Wake on interrupt (WFI exits on any enabled interrupt)
            if (in_wfi && irq_pending)
                in_wfi <= 1'b0;

            // MRET: return from trap
            if (is_mret && taking_trap) begin
                taking_trap <= 1'b0;
                mstatus_mie <= 1'b1;  // restore MIE from MPIE (simplified)
            end

            // Trap entry
            if (irq_pending && !in_wfi && !taking_trap) begin
                taking_trap  <= 1'b1;
                mepc         <= imem_addr_inner;    // save current PC
                mcause       <= 32'h8000_000B;      // Machine external interrupt
                mstatus_mie  <= 1'b0;                // disable interrupts
            end
        end
    end

    // ── Sleep output ──────────────────────────────────────────────────
    assign core_sleep_o = in_wfi;

endmodule
