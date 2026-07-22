// =========================================================================
// Module: interrupt_ctrl
// Description: 13-source interrupt controller → 1 CPU IRQ
//              Per-source enable (IRQ_EN) and pending (IRQ_PENDING).
//              Pure combinational aggregator — no IRQ latching.
//              Level-sensitive: peripheral must hold IRQ until cleared.
//
// Source: PRJ-001 Architecture §4 (M09), CREATE
// =========================================================================

`default_nettype none
`timescale 1ns / 1ps

module interrupt_ctrl (
    input  wire        clk_i,
    input  wire        rst_ni,

    // APB slave interface
    input  wire [ 7:0] paddr,
    input  wire [31:0] pwdata,
    output reg  [31:0] prdata,
    input  wire        pwrite,
    input  wire        psel,
    input  wire        penable,
    output wire        pready,

    // Peripheral IRQ inputs (level-sensitive, synchronous to clk_i)
    input  wire [12:0] irq_in,

    // CPU interrupt output
    output wire        cpu_irq_o
);

    // Register map (from ARCH §4 M09):
    //   0x00: IRQ_EN      [15:0] R/W  — per-source enable (only bits 12:0 used)
    //   0x04: IRQ_PENDING [15:0] R    — per-source pending = IRQ_EN & irq_in
    //   0x08: CPU_IRQ     [0]    R    — global IRQ = OR of all pending

    reg [15:0] irq_en;      // offset 0x00
    // irq_pending and cpu_irq are combinational — see assigns below

    // ── APB write ────────────────────────────────────────────────────
    wire apb_write = psel && penable && pwrite;
    wire apb_read  = psel && penable && !pwrite;

    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            irq_en <= 16'h0000;
        end else if (apb_write) begin
            case (paddr)
                8'h00: irq_en <= pwdata[15:0];
                // 8'h04 IRQ_PENDING is read-only
                // 8'h08 CPU_IRQ is read-only
                default: ;
            endcase
        end
    end

    // ── APB read ─────────────────────────────────────────────────────
    wire [12:0] irq_pending_comb = irq_in[12:0] & irq_en[12:0];
    wire        cpu_irq_comb     = |irq_pending_comb;

    always @(*) begin
        prdata = 32'h0000_0000;
        if (apb_read) begin
            case (paddr)
                8'h00: prdata = {16'h0000, irq_en};
                8'h04: prdata = {16'h0000, 3'b0, irq_pending_comb};
                8'h08: prdata = {31'h0000_0000, cpu_irq_comb};
                default: prdata = 32'h0000_0000;
            endcase
        end
    end

    // ── Outputs ──────────────────────────────────────────────────────
    assign pready   = 1'b1;    // single-cycle APB, always ready
    assign cpu_irq_o = cpu_irq_comb;

endmodule
