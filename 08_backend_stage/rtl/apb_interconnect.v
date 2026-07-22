// =========================================================================
// Module: apb_interconnect
// Description: APB v2.0 address decoder + mux. Single-cycle, no wait states.
//              Routes Ibex data port to up to 10 APB slaves.
//
// Source: PRJ-001 Architecture §4 (M02), CREATE
// =========================================================================

`default_nettype none
`timescale 1ns / 1ps

module apb_interconnect (
    input  wire        clk_i,
    input  wire        rst_ni,

    // Master side (Ibex data port)
    input  wire [31:0] master_paddr,
    input  wire [31:0] master_pwdata,
    input  wire        master_pwrite,
    input  wire        master_psel,
    input  wire        master_penable,
    output reg  [31:0] master_prdata,
    output wire        master_pready,
    output wire        master_pslverr,

    // Slave ports (10 slaves)
    // Slave 0: SRAM
    output wire [31:0] s0_paddr,
    output wire [31:0] s0_pwdata,
    output wire        s0_pwrite,
    output reg         s0_psel,
    output reg         s0_penable,
    input  wire [31:0] s0_prdata,
    input  wire        s0_pready,

    // Slave 1: UART
    output wire [31:0] s1_paddr,
    output wire [31:0] s1_pwdata,
    output wire        s1_pwrite,
    output reg         s1_psel,
    output reg         s1_penable,
    input  wire [31:0] s1_prdata,
    input  wire        s1_pready,

    // Slave 2: SPI
    output wire [31:0] s2_paddr,
    output wire [31:0] s2_pwdata,
    output wire        s2_pwrite,
    output reg         s2_psel,
    output reg         s2_penable,
    input  wire [31:0] s2_prdata,
    input  wire        s2_pready,

    // Slave 3: I2C
    output wire [31:0] s3_paddr,
    output wire [31:0] s3_pwdata,
    output wire        s3_pwrite,
    output reg         s3_psel,
    output reg         s3_penable,
    input  wire [31:0] s3_prdata,
    input  wire        s3_pready,

    // Slave 4: GPIO
    output wire [31:0] s4_paddr,
    output wire [31:0] s4_pwdata,
    output wire        s4_pwrite,
    output reg         s4_psel,
    output reg         s4_penable,
    input  wire [31:0] s4_prdata,
    input  wire        s4_pready,

    // Slave 5: PWM
    output wire [31:0] s5_paddr,
    output wire [31:0] s5_pwdata,
    output wire        s5_pwrite,
    output reg         s5_psel,
    output reg         s5_penable,
    input  wire [31:0] s5_prdata,
    input  wire        s5_pready,

    // Slave 6: Interrupt Controller
    output wire [31:0] s6_paddr,
    output wire [31:0] s6_pwdata,
    output wire        s6_pwrite,
    output reg         s6_psel,
    output reg         s6_penable,
    input  wire [31:0] s6_prdata,
    input  wire        s6_pready,

    // Slave 7: Watchdog (reuses PWM base + 0x200 offset)
    output wire [31:0] s7_paddr,
    output wire [31:0] s7_pwdata,
    output wire        s7_pwrite,
    output reg         s7_psel,
    output reg         s7_penable,
    input  wire [31:0] s7_prdata,
    input  wire        s7_pready,

    // Slave 8: System Control
    output wire [31:0] s8_paddr,
    output wire [31:0] s8_pwdata,
    output wire        s8_pwrite,
    output reg         s8_psel,
    output reg         s8_penable,
    input  wire [31:0] s8_prdata,
    input  wire        s8_pready,

    // Slave 9: Wishbone Bridge (external access)
    output wire [31:0] s9_paddr,
    output wire [31:0] s9_pwdata,
    output wire        s9_pwrite,
    output reg         s9_psel,
    output reg         s9_penable,
    input  wire [31:0] s9_prdata,
    input  wire        s9_pready
);

    // ── Fan-out: all slaves get same address/data/control ─────────────
    assign s0_paddr  = master_paddr;
    assign s0_pwdata = master_pwdata;
    assign s0_pwrite = master_pwrite;
    assign s1_paddr  = master_paddr;
    assign s1_pwdata = master_pwdata;
    assign s1_pwrite = master_pwrite;
    assign s2_paddr  = master_paddr;
    assign s2_pwdata = master_pwdata;
    assign s2_pwrite = master_pwrite;
    assign s3_paddr  = master_paddr;
    assign s3_pwdata = master_pwdata;
    assign s3_pwrite = master_pwrite;
    assign s4_paddr  = master_paddr;
    assign s4_pwdata = master_pwdata;
    assign s4_pwrite = master_pwrite;
    assign s5_paddr  = master_paddr;
    assign s5_pwdata = master_pwdata;
    assign s5_pwrite = master_pwrite;
    assign s6_paddr  = master_paddr;
    assign s6_pwdata = master_pwdata;
    assign s6_pwrite = master_pwrite;
    assign s7_paddr  = master_paddr;
    assign s7_pwdata = master_pwdata;
    assign s7_pwrite = master_pwrite;
    assign s8_paddr  = master_paddr;
    assign s8_pwdata = master_pwdata;
    assign s8_pwrite = master_pwrite;
    assign s9_paddr  = master_paddr;
    assign s9_pwdata = master_pwdata;
    assign s9_pwrite = master_pwrite;

    // ── Address decode (combinational) ────────────────────────────────
    wire hits_sram = (master_paddr[31:12] == 20'h0000_0);      // 0x0000_0000 – 0x0000_0FFF
    wire hits_periph = (master_paddr[31:16] == 16'h0001);       // 0x0001_0000 – 0x0001_FFFF

    // Peripheral select within 0x0001_xxxx region
    wire [7:0] periph_sel_byte = master_paddr[15:8];

    wire hit_uart    = hits_periph && (periph_sel_byte == 8'h00);
    wire hit_spi     = hits_periph && (periph_sel_byte == 8'h01);
    wire hit_i2c     = hits_periph && (periph_sel_byte == 8'h02);
    wire hit_gpio    = hits_periph && (periph_sel_byte == 8'h03);
    wire hit_pwm     = hits_periph && (periph_sel_byte == 8'h04);
    wire hit_irqctrl = hits_periph && (periph_sel_byte == 8'h05);
    wire hit_wdt     = hits_periph && (periph_sel_byte == 8'h06);
    wire hit_sysctrl = hits_periph && (periph_sel_byte == 8'h07);
    wire hit_wb      = master_paddr[31];                        // 0x8000_0000+

    wire any_hit = hits_sram | hit_uart | hit_spi | hit_i2c | hit_gpio |
                   hit_pwm | hit_irqctrl | hit_wdt | hit_sysctrl | hit_wb;

    // ── Registered slave selects (one-hot) ────────────────────────────
    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            {s0_psel, s1_psel, s2_psel, s3_psel, s4_psel,
             s5_psel, s6_psel, s7_psel, s8_psel, s9_psel} <= 10'b0;
            {s0_penable, s1_penable, s2_penable, s3_penable, s4_penable,
             s5_penable, s6_penable, s7_penable, s8_penable, s9_penable} <= 10'b0;
        end else begin
            // One-hot select based on address
            s0_psel <= master_psel && hits_sram;
            s1_psel <= master_psel && hit_uart;
            s2_psel <= master_psel && hit_spi;
            s3_psel <= master_psel && hit_i2c;
            s4_psel <= master_psel && hit_gpio;
            s5_psel <= master_psel && hit_pwm;
            s6_psel <= master_psel && hit_irqctrl;
            s7_psel <= master_psel && hit_wdt;
            s8_psel <= master_psel && hit_sysctrl;
            s9_psel <= master_psel && hit_wb;

            // Enable follows select with one-cycle pipeline
            s0_penable <= master_penable && hits_sram;
            s1_penable <= master_penable && hit_uart;
            s2_penable <= master_penable && hit_spi;
            s3_penable <= master_penable && hit_i2c;
            s4_penable <= master_penable && hit_gpio;
            s5_penable <= master_penable && hit_pwm;
            s6_penable <= master_penable && hit_irqctrl;
            s7_penable <= master_penable && hit_wdt;
            s8_penable <= master_penable && hit_sysctrl;
            s9_penable <= master_penable && hit_wb;
        end
    end

    // ── Read data mux ─────────────────────────────────────────────────
    always @(*) begin
        master_prdata = 32'h0000_0000;
        if (s0_psel) master_prdata = s0_prdata;
        else if (s1_psel) master_prdata = s1_prdata;
        else if (s2_psel) master_prdata = s2_prdata;
        else if (s3_psel) master_prdata = s3_prdata;
        else if (s4_psel) master_prdata = s4_prdata;
        else if (s5_psel) master_prdata = s5_prdata;
        else if (s6_psel) master_prdata = s6_prdata;
        else if (s7_psel) master_prdata = s7_prdata;
        else if (s8_psel) master_prdata = s8_prdata;
        else if (s9_psel) master_prdata = s9_prdata;
    end

    // ── Ready and error ───────────────────────────────────────────────
    // OR all slave readys; PSLVERR on unmapped address
    wire slave_pready_or =
        (s0_psel && s0_pready) || (s1_psel && s1_pready) ||
        (s2_psel && s2_pready) || (s3_psel && s3_pready) ||
        (s4_psel && s4_pready) || (s5_psel && s5_pready) ||
        (s6_psel && s6_pready) || (s7_psel && s7_pready) ||
        (s8_psel && s8_pready) || (s9_psel && s9_pready);

    assign master_pready  = master_psel ? (any_hit ? slave_pready_or : 1'b1) : 1'b1;
    assign master_pslverr = master_psel && master_penable && !any_hit;

endmodule
