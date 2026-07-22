// ===================================================================
// argus_soc_asserts.sv — Safety assertions bound to argus_soc internals
// Uses SV bind — no wrapper needed, no inout port exposure
// ===================================================================
`default_nettype none

module argus_soc_asserts(
    input wire clk_sys_i, rst_ni,
    input wire wb_ack_o, wb_err_o,
    input wire [31:0] wb_dat_o,
    input wire uart_tx_o, spi_sclk_o, spi_mosi_o,
    input wire [3:0] spi_cs_n_o,
    input wire pwm0_o, pwm1_o
);
    // S1: WB ack and err never simultaneously active
    always @(posedge clk_sys_i) begin
        if (rst_ni) begin
            a_wb_ack_err_excl: assert (!(wb_ack_o && wb_err_o));
        end
    end

    // S2: WB dat_o is never X when settled
    always @(posedge clk_sys_i) begin
        if (rst_ni) begin
            a_wb_dat_no_x: assert (!$isunknown(wb_dat_o));
        end
    end

    // S3: UART TX is idle (1) during reset
    always @(posedge clk_sys_i) begin
        if (!rst_ni) begin
            a_uart_tx_reset: assert (uart_tx_o == 1'b1);
        end
    end

    // S4: Critical outputs are never X
    always @(posedge clk_sys_i) begin
        if (rst_ni) begin
            a_spi_sclk_no_x: assert (!$isunknown(spi_sclk_o));
            a_spi_mosi_no_x: assert (!$isunknown(spi_mosi_o));
            a_spi_cs_no_x:   assert (!$isunknown(spi_cs_n_o));
            a_pwm0_no_x:     assert (!$isunknown(pwm0_o));
            a_pwm1_no_x:     assert (!$isunknown(pwm1_o));
        end
    end
endmodule

// Bind assertions to argus_soc top-level
bind argus_soc argus_soc_asserts u_asserts (
    .clk_sys_i(clk_sys_i),
    .rst_ni(rst_ni),
    .wb_ack_o(wb_ack_o),
    .wb_err_o(wb_err_o),
    .wb_dat_o(wb_dat_o),
    .uart_tx_o(uart_tx_o),
    .spi_sclk_o(spi_sclk_o),
    .spi_mosi_o(spi_mosi_o),
    .spi_cs_n_o(spi_cs_n_o),
    .pwm0_o(pwm0_o),
    .pwm1_o(pwm1_o)
);
