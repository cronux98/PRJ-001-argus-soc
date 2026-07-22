// =========================================================================
// Module: sram_blackbox
// Description: Blackbox wrapper for PRJ-001 Argus 4KB SRAM — synthesis/PD stub.
//              Same port interface as sram.v, no internal logic.
//              Prevents the 1024×32 inferred BRAM from being synthesized as
//              169K flip-flops. At P&R, the OpenRAM 2KB macro is placed.
//
// Ports match the triple-port arbitration interface:
//   - Ibex instruction port (read-only)
//   - Ibex data port (read/write)
//   - APB port (read/write)
//
// For synthesis: use this file INSTEAD of rtl-sram/rtl/sram.v
// For simulation: use the full behavioral model (sram.v)
// =========================================================================

(* blackbox *)
module sram (
    input  wire        clk_i,
    input  wire        rst_ni,

    input  wire [31:0] imem_addr,
    output wire [31:0] imem_rdata,

    input  wire [31:0] dmem_addr,
    input  wire [31:0] dmem_wdata,
    output wire [31:0] dmem_rdata,
    input  wire        dmem_we,
    input  wire [ 3:0] dmem_be,

    input  wire [31:0] apb_paddr,
    input  wire [31:0] apb_pwdata,
    output wire [31:0] apb_prdata,
    input  wire        apb_pwrite,
    input  wire        apb_psel,
    input  wire        apb_penable,
    output wire        apb_pready
);

    assign imem_rdata = 32'b0;
    assign dmem_rdata = 32'b0;
    assign apb_prdata = 32'b0;
    assign apb_pready = 1'b0;

endmodule
