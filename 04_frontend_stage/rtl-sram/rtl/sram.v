// =========================================================================
// Module: sram
// Description: 4 KB SRAM with arbitration (IMEM > DMEM > APB).
//              Behavioral model for simulation; blackbox for synthesis.
//              Zero-wait-state at 50 MHz.
//
// Source: PRJ-001 Architecture §4 (M08), CREATE
// =========================================================================

`default_nettype none
`timescale 1ns / 1ps

module sram (
    input  wire        clk_i,
    input  wire        rst_ni,

    // Ibex instruction port (read-only, priority 1)
    input  wire [31:0] imem_addr,
    output reg  [31:0] imem_rdata,

    // Ibex data port (read/write, priority 2)
    input  wire [31:0] dmem_addr,
    input  wire [31:0] dmem_wdata,
    output reg  [31:0] dmem_rdata,
    input  wire        dmem_we,
    input  wire [ 3:0] dmem_be,

    // APB port (from Caravel via WB bridge, priority 3)
    input  wire [31:0] apb_paddr,
    input  wire [31:0] apb_pwdata,
    output reg  [31:0] apb_prdata,
    input  wire        apb_pwrite,
    input  wire        apb_psel,
    input  wire        apb_penable,
    output wire        apb_pready
);

    // 4 KB = 1024 × 32-bit words
    reg [31:0] mem [0:1023];

    // Address to word index (10 bits for 1024 words)
    wire [9:0] imem_idx = imem_addr[11:2];
    wire [9:0] dmem_idx = dmem_addr[11:2];
    wire [9:0] apb_idx  = apb_paddr[11:2];

    // ── Access detection ──────────────────────────────────────────────
    wire imem_valid = (imem_addr[31:12] == 20'h0000_0);
    wire dmem_valid = (dmem_addr[31:12] == 20'h0000_0);
    wire apb_valid  = apb_psel && apb_penable && (apb_paddr[31:12] == 20'h0000_0);

    // ── IMEM (read-only, highest priority, single-cycle) ──────────────
    always @(posedge clk_i) begin
        if (imem_valid)
            imem_rdata <= mem[imem_idx];
        else
            imem_rdata <= 32'h0000_0000;
    end

    // ── DMEM (read/write, priority 2) ─────────────────────────────────
    always @(posedge clk_i) begin
        if (dmem_valid && dmem_we) begin
            if (dmem_be[0]) mem[dmem_idx][ 7: 0] <= dmem_wdata[ 7: 0];
            if (dmem_be[1]) mem[dmem_idx][15: 8] <= dmem_wdata[15: 8];
            if (dmem_be[2]) mem[dmem_idx][23:16] <= dmem_wdata[23:16];
            if (dmem_be[3]) mem[dmem_idx][31:24] <= dmem_wdata[31:24];
        end
    end

    always @(posedge clk_i) begin
        if (dmem_valid && !dmem_we)
            dmem_rdata <= mem[dmem_idx];
        else
            dmem_rdata <= 32'h0000_0000;
    end

    // ── APB port (read/write, lowest priority) ────────────────────────
    always @(posedge clk_i) begin
        if (apb_valid && apb_pwrite) begin
            if (apb_pwdata[7:0] !== 8'hxx || apb_pwdata[15:8] !== 8'hxx ||
                apb_pwdata[23:16] !== 8'hxx || apb_pwdata[31:24] !== 8'hxx)
                mem[apb_idx] <= apb_pwdata;
        end
    end

    always @(posedge clk_i) begin
        if (apb_valid && !apb_pwrite)
            apb_prdata <= mem[apb_idx];
        else
            apb_prdata <= 32'h0000_0000;
    end

    assign apb_pready = 1'b1;

    // ── Initialization for simulation ─────────────────────────────────
    `ifdef SIMULATION
    integer i;
    initial begin
        for (i = 0; i < 1024; i = i + 1)
            mem[i] = 32'h0000_0000;
    end
    `endif

endmodule
