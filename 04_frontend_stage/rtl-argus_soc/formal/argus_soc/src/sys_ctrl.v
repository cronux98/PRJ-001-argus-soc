// =========================================================================
// Module: sys_ctrl
// Description: System control — chip ID, clock divider, reset cause, sleep.
//
// Source: PRJ-001 Architecture §4 (M12), CREATE
// =========================================================================

`default_nettype none
`timescale 1ns / 1ps

module sys_ctrl (
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

    // External reset inputs
    input  wire        wdt_rst_n,
    input  wire        ext_rst_n,

    // Core sleep status
    input  wire        core_sleep_i,

    // Clock gate enables (per-module)
    output wire [11:0] clk_gate_en,

    // Wake events
    input  wire [ 1:0] wake_event_i
);

    localparam CHIP_ID_VAL = 32'h4152_4755;     // "ARGU"

    reg [ 7:0] clk_div;
    reg [ 2:0] reset_cause;
    reg [ 7:0] sleep_ctrl;
    reg [ 3:0] wake_source;
    reg        in_sleep;

    // ── APB interface ─────────────────────────────────────────────────
    wire apb_write = psel && penable && pwrite;
    wire apb_read  = psel && penable && !pwrite;

    // ── Reset cause capture ───────────────────────────────────────────
    // Sample ext_rst_n and wdt_rst_n at the cycle rst_ni deasserts
    // to determine what caused the most recent reset.
    reg        rst_ni_d;
    reg        cause_captured;
    reg        ext_was_low, wdt_was_low;

    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            clk_div        <= 8'h01;
            sleep_ctrl     <= 8'h00;
            in_sleep       <= 1'b0;
            wake_source    <= 4'h0;
            rst_ni_d       <= 1'b0;
            cause_captured <= 1'b0;
            ext_was_low    <= 1'b0;
            wdt_was_low    <= 1'b0;
            reset_cause    <= 3'b000;   // POR default
        end else begin
            rst_ni_d <= rst_ni;

            // On rst_ni rising edge (deassertion): capture reset cause
            if (rst_ni && !rst_ni_d && !cause_captured) begin
                cause_captured <= 1'b1;
                if (!wdt_rst_n && !ext_rst_n)
                    reset_cause <= 3'b010;   // both: watchdog wins
                else if (!ext_rst_n)
                    reset_cause <= 3'b001;   // external
                else if (!wdt_rst_n)
                    reset_cause <= 3'b010;   // watchdog
                else
                    reset_cause <= 3'b000;   // POR
            end

            // APB writes
            if (apb_write) begin
                case (paddr)
                    8'h04: clk_div    <= pwdata[7:0];
                    8'h0C: sleep_ctrl <= pwdata[7:0];
                    default: ;
                endcase
            end

            // Sleep state machine
            if (sleep_ctrl[0] && core_sleep_i && !in_sleep) begin
                in_sleep <= 1'b1;
            end else if (in_sleep && (|wake_event_i)) begin
                in_sleep        <= 1'b0;
                wake_source     <= {2'b00, wake_event_i};
                sleep_ctrl[0]   <= 1'b0;
            end
        end
    end

    // ── APB read ──────────────────────────────────────────────────────
    always @(*) begin
        prdata = 32'h0000_0000;
        if (apb_read) begin
            case (paddr)
                8'h00: prdata = CHIP_ID_VAL;
                8'h04: prdata = {24'h00_0000, clk_div};
                8'h08: prdata = {29'h0000_0000, reset_cause};
                8'h0C: prdata = {20'h0_0000, wake_source, 4'b0000, sleep_ctrl[3:0]};
                default: prdata = 32'h0000_0000;
            endcase
        end
    end

    // ── Clock gate enables ────────────────────────────────────────────
    wire [11:0] clk_gate_all_on = 12'hFFF;
    wire [11:0] clk_gate_sleep  = 12'h048;  // GPIO(bit6) + PWM(bit7)

    assign clk_gate_en = in_sleep ? clk_gate_sleep : clk_gate_all_on;
    assign pready = 1'b1;

endmodule
