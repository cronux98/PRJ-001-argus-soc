// =========================================================================
// Module: wb_bridge
// Description: APB ↔ Wishbone B4 bridge for Caravel management SoC access.
//              Maps Wishbone 0x8000_0000 window to internal 0x0000_0000.
//              Single-clock implementation for simplicity; CDC FIFOs
//              added for dual-clock operation at physical design stage.
//
// Source: PRJ-001 Architecture §4 (M10), CREATE
// =========================================================================

`default_nettype none
`timescale 1ns / 1ps

module wb_bridge (
    input  wire        clk_i,
    input  wire        rst_ni,

    // Wishbone side (Caravel, same clock for this simplified version)
    input  wire [31:0] wb_adr_i,
    input  wire [31:0] wb_dat_i,
    output reg  [31:0] wb_dat_o,
    input  wire [ 3:0] wb_sel_i,
    input  wire        wb_we_i,
    input  wire        wb_stb_i,
    input  wire        wb_cyc_i,
    output reg         wb_ack_o,
    output wire        wb_err_o,

    // APB side (internal — connects to APB interconnect slave port)
    output reg  [31:0] apb_paddr,
    output reg  [31:0] apb_pwdata,
    input  wire [31:0] apb_prdata,
    output reg         apb_pwrite,
    output reg         apb_psel,
    output reg         apb_penable,
    input  wire        apb_pready,
    input  wire        apb_pslverr
);

    // ── Address translation: WB 0x8000_xxxx → internal 0x0000_xxxx ───
    wire wb_in_window = wb_adr_i[31];  // 0x8000_0000 and above

    // ── FSM states ────────────────────────────────────────────────────
    localparam IDLE     = 2'd0;
    localparam APB_SETUP = 2'd1;
    localparam APB_ACCESS = 2'd2;
    localparam DONE     = 2'd3;

    reg [1:0] state, next_state;

    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            state <= IDLE;
        end else begin
            state <= next_state;
        end
    end

    always @(*) begin
        next_state = state;
        case (state)
            IDLE: begin
                if (wb_cyc_i && wb_stb_i && wb_in_window)
                    next_state = APB_SETUP;
            end
            APB_SETUP: begin
                next_state = APB_ACCESS;
            end
            APB_ACCESS: begin
                if (apb_pready)
                    next_state = DONE;
            end
            DONE: begin
                next_state = IDLE;
            end
            default: next_state = IDLE;
        endcase
    end

    // ── APB signal generation ─────────────────────────────────────────
    always @(*) begin
        apb_paddr   = {1'b0, wb_adr_i[30:0]};  // strip bit 31
        apb_pwdata  = wb_dat_i;
        apb_pwrite  = wb_we_i;

        case (state)
            APB_SETUP: begin
                apb_psel    = 1'b1;
                apb_penable = 1'b0;
            end
            APB_ACCESS: begin
                apb_psel    = 1'b1;
                apb_penable = 1'b1;
            end
            default: begin
                apb_psel    = 1'b0;
                apb_penable = 1'b0;
            end
        endcase
    end

    // ── WB response ───────────────────────────────────────────────────
    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            wb_ack_o <= 1'b0;
            wb_dat_o <= 32'h0000_0000;
        end else begin
            if (state == APB_ACCESS && apb_pready) begin
                wb_ack_o <= 1'b1;
                wb_dat_o <= apb_prdata;
            end else begin
                wb_ack_o <= 1'b0;
            end
        end
    end

    assign wb_err_o = (state == APB_ACCESS && apb_pready && apb_pslverr) ||
                      (wb_cyc_i && wb_stb_i && !wb_in_window);

endmodule
