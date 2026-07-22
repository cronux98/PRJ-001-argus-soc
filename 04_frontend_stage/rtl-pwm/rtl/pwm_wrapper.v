// =========================================================================
// Module: pwm_wrapper
// Description: PWM + Watchdog wrapper. Instantiates EF_TMR32_APB (PWM)
//              and EF_WDT32_APB (Watchdog). Separate APB ports for each;
//              address decode handled upstream by APB interconnect.
//
// Source: PRJ-001 Architecture §4 (M07), REUSE* from EF_TMR32 + EF_WDT32
// =========================================================================

`default_nettype none
`timescale 1ns / 1ps

module pwm_wrapper (
    input  wire        clk_i,
    input  wire        rst_ni,

    // PWM APB port (connects to interconnect slave 5, base 0x0001_0400)
    input  wire [31:0] pwm_paddr,
    input  wire [31:0] pwm_pwdata,
    output wire [31:0] pwm_prdata,
    input  wire        pwm_pwrite,
    input  wire        pwm_psel,
    input  wire        pwm_penable,
    output wire        pwm_pready,

    // WDT APB port (connects to interconnect slave 7, base 0x0001_0600)
    input  wire [31:0] wdt_paddr,
    input  wire [31:0] wdt_pwdata,
    output wire [31:0] wdt_prdata,
    input  wire        wdt_pwrite,
    input  wire        wdt_psel,
    input  wire        wdt_penable,
    output wire        wdt_pready,

    // PWM outputs
    output wire        pwm0,
    output wire        pwm1,

    // Interrupts
    output wire        pwm_irq_o,       // PWM period match (to M09 IRQ[11])
    output wire        wdt_irq_o,       // WDT timeout warning (to M09 IRQ[12])
    output wire        wdt_rst_n_o      // WDT system reset (to sys_ctrl)
);

    // ── EF_TMR32_APB (PWM) ────────────────────────────────────────────
    EF_TMR32_APB u_tmr32 (
        .PCLK      (clk_i),
        .PRESETn   (rst_ni),
        .PWRITE    (pwm_pwrite),
        .PWDATA    (pwm_pwdata),
        .PADDR     (pwm_paddr),
        .PENABLE   (pwm_penable),
        .PSEL      (pwm_psel),
        .PREADY    (pwm_pready),
        .PRDATA    (pwm_prdata),
        .IRQ       (pwm_irq_o),
        .pwm0      (pwm0),
        .pwm1      (pwm1),
        .pwm_fault (2'b00)
    );

    // ── EF_WDT32_APB (Watchdog) ───────────────────────────────────────
    EF_WDT32_APB u_wdt32 (
        .PCLK      (clk_i),
        .PRESETn   (rst_ni),
        .PWRITE    (wdt_pwrite),
        .PWDATA    (wdt_pwdata),
        .PADDR     (wdt_paddr),
        .PENABLE   (wdt_penable),
        .PSEL      (wdt_psel),
        .PREADY    (wdt_pready),
        .PRDATA    (wdt_prdata),
        .IRQ       (wdt_irq_o)
    );

    // WDT system reset: not directly available from EF_WDT32_APB.
    // Firmware handles WDT reset via IRQ handler.
    assign wdt_rst_n_o = 1'b1;

endmodule
