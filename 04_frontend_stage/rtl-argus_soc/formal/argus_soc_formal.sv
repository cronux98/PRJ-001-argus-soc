// =========================================================================
// argus_soc_formal.sv — Safety assertions for argus_soc top-level interconnects
// Generated for PRJ-001 FE REWORK v2 FIX 1
// =========================================================================
`default_nettype none
`timescale 1ns / 1ps

module argus_soc_formal;

    // ── DUT ports ──────────────────────────────────────────────────
    wire        clk_sys_i;
    reg         rst_ni;

    wire        uart_tx_o;
    reg         uart_rx_i;

    wire        spi_sclk_o, spi_mosi_o;
    reg         spi_miso_i;
    wire [3:0]  spi_cs_n_o;

    wire        i2c_scl_io, i2c_sda_io;

    wire [7:0]  gpio_io;

    wire        pwm0_o, pwm1_o;

    reg  [31:0] wb_adr_i, wb_dat_i;
    wire [31:0] wb_dat_o;
    reg  [ 3:0] wb_sel_i;
    reg         wb_we_i, wb_stb_i, wb_cyc_i;
    wire        wb_ack_o, wb_err_o;

    // ── DUT instantiation ───────────────────────────────────────────
    argus_soc dut (.*);

    // ── Reset constraint pattern (formal-verification skill §Reset) ──
    // Force reset LOW at time 0 — solver starts from arbitrary state
    reg init_done;
    initial init_done = 1'b0;
    always @(posedge clk_sys_i) init_done <= 1'b1;
    always @(*) if (!init_done) assume (rst_ni == 1'b0);

    // Delay assertions until 1 cycle after reset deasserts
    reg settled;
    initial settled = 1'b0;
    always @(posedge clk_sys_i) begin
        if (!rst_ni) settled <= 1'b0;
        else         settled <= 1'b1;
    end

    // ── Assume WB interface is well-behaved ─────────────────────────
    // When WB is inactive, constrain inputs to reduce search space
    always @(posedge clk_sys_i) begin
        if (settled && rst_ni) begin
            assume (wb_ack_o == 1'b0 || wb_stb_i == 1'b1);
            assume (wb_ack_o == 1'b0 || wb_cyc_i == 1'b1);
        end
    end

    // ══════════════════════════════════════════════════════════════════
    // SAFETY ASSERTIONS
    // ══════════════════════════════════════════════════════════════════

    // S1: WB ack and err never simultaneously active
    always @(posedge clk_sys_i) begin
        if (settled && rst_ni) begin
            a_wb_ack_err_excl: assert (!(wb_ack_o && wb_err_o));
        end
    end

    // S2: WB dat_o is never X when settled
    always @(posedge clk_sys_i) begin
        if (settled && rst_ni) begin
            a_wb_dat_no_x: assert (!$isunknown(wb_dat_o));
        end
    end

    // S3: UART TX is idle (1) during reset
    always @(posedge clk_sys_i) begin
        if (!rst_ni) begin
            a_uart_tx_reset: assert (uart_tx_o == 1'b1);
        end
    end

    // S4: Critical outputs are never X when settled
    always @(posedge clk_sys_i) begin
        if (settled && rst_ni) begin
            a_uart_tx_no_x:  assert (!$isunknown(uart_tx_o));
            a_spi_sclk_no_x: assert (!$isunknown(spi_sclk_o));
            a_spi_mosi_no_x: assert (!$isunknown(spi_mosi_o));
            a_pwm0_no_x:     assert (!$isunknown(pwm0_o));
            a_pwm1_no_x:     assert (!$isunknown(pwm1_o));
        end
    end

    // S5: SPI CS lines not X when settled
    always @(posedge clk_sys_i) begin
        if (settled && rst_ni) begin
            a_spi_cs_no_x: assert (!$isunknown(spi_cs_n_o));
        end
    end

endmodule
