// =========================================================================
// Module: argus_soc
// Description: PRJ-001 "Argus" Environmental Sensor-Hub SoC top-level.
//              Instantiates all 11 internal modules.
//
// Source: PRJ-001 Architecture §1-4
// =========================================================================

`default_nettype none
`timescale 1ns / 1ps

module argus_soc (
    input  wire        clk_sys_i,
    input  wire        rst_ni,

    output wire        uart_tx_o,
    input  wire        uart_rx_i,

    output wire        spi_sclk_o,
    output wire        spi_mosi_o,
    input  wire        spi_miso_i,
    output wire [3:0]  spi_cs_n_o,

    inout  wire        i2c_scl_io,
    inout  wire        i2c_sda_io,

    inout  wire [7:0]  gpio_io,

    output wire        pwm0_o,
    output wire        pwm1_o,

    input  wire [31:0] wb_adr_i,
    input  wire [31:0] wb_dat_i,
    output wire [31:0] wb_dat_o,
    input  wire [ 3:0] wb_sel_i,
    input  wire        wb_we_i,
    input  wire        wb_stb_i,
    input  wire        wb_cyc_i,
    output wire        wb_ack_o,
    output wire        wb_err_o
);

    // ══════════════════════════════════════════════════════════════════
    // Internal buses
    // ══════════════════════════════════════════════════════════════════
    wire [31:0] ibex_imem_addr, ibex_imem_rdata;
    wire [31:0] ibex_dmem_addr, ibex_dmem_wdata, ibex_dmem_rdata;
    wire        ibex_dmem_we;
    wire [ 3:0] ibex_dmem_be;
    wire        ibex_data_req, data_target_sram, ibex_sleep;
    wire        instr_req, instr_rvalid, data_rvalid;

    // APB master mux (Ibex + WB bridge → one APB master)
    wire        wb_active;
    wire [31:0] wb_apb_paddr, wb_apb_pwdata, wb_apb_prdata;
    wire        wb_apb_pwrite, wb_apb_psel, wb_apb_penable, wb_apb_pready;

    wire [31:0] apb_mpaddr = wb_active ? wb_apb_paddr : ibex_dmem_addr;
    wire [31:0] apb_mpwdata = wb_active ? wb_apb_pwdata : ibex_dmem_wdata;
    wire        apb_mpwrite = wb_active ? wb_apb_pwrite : ibex_dmem_we;
    wire        apb_mpsel   = wb_active ? wb_apb_psel   : (ibex_data_req && !data_target_sram);
    wire        apb_mpenable = wb_active ? wb_apb_penable : (ibex_data_req && !data_target_sram);
    wire [31:0] apb_mprdata;
    wire        apb_mpready, apb_mpslverr;

    // Slave ports (9 slaves: s0-s8; s9 unused — WB bridge shares master port)
    wire [31:0] s_paddr   [0:8];
    wire [31:0] s_pwdata  [0:8];
    wire        s_pwrite  [0:8];
    wire        s_psel    [0:8];
    wire        s_penable [0:8];
    wire [31:0] s_prdata  [0:8];
    wire        s_pready  [0:8];

    wire        irq_uart, irq_spi, irq_i2c, irq_pwm, irq_wdt;
    wire        irq_gpio_combined;
    wire        cpu_irq, wdt_rst_n_ignored;
    wire [11:0] clk_gate_en;

    // ══════════════════════════════════════════════════════════════════
    // M01: Ibex Core
    // ══════════════════════════════════════════════════════════════════
    ibex_core u_ibex (
        .clk_i(clk_sys_i), .rst_ni(rst_ni),
        .instr_req_o(instr_req), .instr_addr_o(ibex_imem_addr),
        .instr_rdata_i(ibex_imem_rdata), .instr_rvalid_i(instr_rvalid),
        .data_req_o(ibex_data_req), .data_addr_o(ibex_dmem_addr),
        .data_wdata_o(ibex_dmem_wdata), .data_rdata_i(ibex_dmem_rdata),
        .data_we_o(ibex_dmem_we), .data_be_o(ibex_dmem_be),
        .data_rvalid_i(data_rvalid),
        .irq_software_i(1'b0), .irq_timer_i(1'b0),
        .irq_external_i(cpu_irq), .irq_fast_i(15'h0000),
        .debug_req_i(1'b0), .core_sleep_o(ibex_sleep)
    );

    // ══════════════════════════════════════════════════════════════════
    // M08: SRAM
    // ══════════════════════════════════════════════════════════════════
    assign instr_rvalid = 1'b1;
    assign data_target_sram = (ibex_dmem_addr[31:12] == 20'h0000_0);

    wire [31:0] sram_dmem_rdata;
    assign ibex_dmem_rdata = data_target_sram ? sram_dmem_rdata :
                              (wb_active ? 32'h0 : apb_mprdata);
    assign data_rvalid = data_target_sram ? 1'b1 :
                         (wb_active ? 1'b1 : apb_mpready);

    sram u_sram (
        .clk_i(clk_sys_i), .rst_ni(rst_ni),
        .imem_addr(ibex_imem_addr), .imem_rdata(ibex_imem_rdata),
        .dmem_addr(ibex_dmem_addr), .dmem_wdata(ibex_dmem_wdata),
        .dmem_rdata(sram_dmem_rdata),
        .dmem_we(ibex_dmem_we && data_target_sram), .dmem_be(ibex_dmem_be),
        .apb_paddr(s_paddr[0]), .apb_pwdata(s_pwdata[0]),
        .apb_prdata(s_prdata[0]), .apb_pwrite(s_pwrite[0]),
        .apb_psel(s_psel[0]), .apb_penable(s_penable[0]),
        .apb_pready(s_pready[0])
    );

    // ══════════════════════════════════════════════════════════════════
    // M02: APB Interconnect
    // ══════════════════════════════════════════════════════════════════
    apb_interconnect u_apb (
        .clk_i(clk_sys_i), .rst_ni(rst_ni),
        .master_paddr(apb_mpaddr), .master_pwdata(apb_mpwdata),
        .master_pwrite(apb_mpwrite), .master_psel(apb_mpsel),
        .master_penable(apb_mpenable),
        .master_prdata(apb_mprdata), .master_pready(apb_mpready),
        .master_pslverr(apb_mpslverr),
        .s0_paddr(s_paddr[0]), .s0_pwdata(s_pwdata[0]), .s0_pwrite(s_pwrite[0]),
        .s0_psel(s_psel[0]), .s0_penable(s_penable[0]),
        .s0_prdata(s_prdata[0]), .s0_pready(s_pready[0]),
        .s1_paddr(s_paddr[1]), .s1_pwdata(s_pwdata[1]), .s1_pwrite(s_pwrite[1]),
        .s1_psel(s_psel[1]), .s1_penable(s_penable[1]),
        .s1_prdata(s_prdata[1]), .s1_pready(s_pready[1]),
        .s2_paddr(s_paddr[2]), .s2_pwdata(s_pwdata[2]), .s2_pwrite(s_pwrite[2]),
        .s2_psel(s_psel[2]), .s2_penable(s_penable[2]),
        .s2_prdata(s_prdata[2]), .s2_pready(s_pready[2]),
        .s3_paddr(s_paddr[3]), .s3_pwdata(s_pwdata[3]), .s3_pwrite(s_pwrite[3]),
        .s3_psel(s_psel[3]), .s3_penable(s_penable[3]),
        .s3_prdata(s_prdata[3]), .s3_pready(s_pready[3]),
        .s4_paddr(s_paddr[4]), .s4_pwdata(s_pwdata[4]), .s4_pwrite(s_pwrite[4]),
        .s4_psel(s_psel[4]), .s4_penable(s_penable[4]),
        .s4_prdata(s_prdata[4]), .s4_pready(s_pready[4]),
        .s5_paddr(s_paddr[5]), .s5_pwdata(s_pwdata[5]), .s5_pwrite(s_pwrite[5]),
        .s5_psel(s_psel[5]), .s5_penable(s_penable[5]),
        .s5_prdata(s_prdata[5]), .s5_pready(s_pready[5]),
        .s6_paddr(s_paddr[6]), .s6_pwdata(s_pwdata[6]), .s6_pwrite(s_pwrite[6]),
        .s6_psel(s_psel[6]), .s6_penable(s_penable[6]),
        .s6_prdata(s_prdata[6]), .s6_pready(s_pready[6]),
        .s7_paddr(s_paddr[7]), .s7_pwdata(s_pwdata[7]), .s7_pwrite(s_pwrite[7]),
        .s7_psel(s_psel[7]), .s7_penable(s_penable[7]),
        .s7_prdata(s_prdata[7]), .s7_pready(s_pready[7]),
        .s8_paddr(s_paddr[8]), .s8_pwdata(s_pwdata[8]), .s8_pwrite(s_pwrite[8]),
        .s8_psel(s_psel[8]), .s8_penable(s_penable[8]),
        .s8_prdata(s_prdata[8]), .s8_pready(s_pready[8]),
        // s9 unused (wb_bridge shares master port)
        .s9_paddr(), .s9_pwdata(), .s9_pwrite(),
        .s9_psel(), .s9_penable(), .s9_prdata(32'h0), .s9_pready(1'b1)
    );

    // ══════════════════════════════════════════════════════════════════
    // M03: UART
    // ══════════════════════════════════════════════════════════════════
    EF_UART_APB u_uart (
        .PCLK(clk_sys_i), .PRESETn(rst_ni),
        .PWRITE(s_pwrite[1]), .PWDATA(s_pwdata[1]), .PADDR(s_paddr[1]),
        .PENABLE(s_penable[1]), .PSEL(s_psel[1]),
        .PREADY(s_pready[1]), .PRDATA(s_prdata[1]),
        .IRQ(irq_uart), .rx(uart_rx_i), .tx(uart_tx_o)
    );

    // ══════════════════════════════════════════════════════════════════
    // M04: SPI
    // ══════════════════════════════════════════════════════════════════
    EF_SPI_APB u_spi (
        .PCLK(clk_sys_i), .PRESETn(rst_ni),
        .PWRITE(s_pwrite[2]), .PWDATA(s_pwdata[2]), .PADDR(s_paddr[2]),
        .PENABLE(s_penable[2]), .PSEL(s_psel[2]),
        .PREADY(s_pready[2]), .PRDATA(s_prdata[2]),
        .IRQ(irq_spi),
        .sclk(spi_sclk_o), .mosi(spi_mosi_o), .miso(spi_miso_i),
        .csb(spi_cs_n_o[0])
    );
    assign spi_cs_n_o[3:1] = 3'b111;

    // ══════════════════════════════════════════════════════════════════
    // M05: I2C
    // ══════════════════════════════════════════════════════════════════
    wire i2c_scl_o, i2c_scl_oen, i2c_sda_o, i2c_sda_oen;
    EF_I2C_APB u_i2c (
        .PCLK(clk_sys_i), .PRESETn(rst_ni),
        .PWRITE(s_pwrite[3]), .PWDATA(s_pwdata[3]), .PADDR(s_paddr[3]),
        .PENABLE(s_penable[3]), .PSEL(s_psel[3]),
        .PREADY(s_pready[3]), .PRDATA(s_prdata[3]),
        .i2c_irq(irq_i2c),
        .scl_i(i2c_scl_io), .scl_o(i2c_scl_o), .scl_oen_o(i2c_scl_oen),
        .sda_i(i2c_sda_io), .sda_o(i2c_sda_o), .sda_oen_o(i2c_sda_oen)
    );
    assign i2c_scl_io = i2c_scl_oen ? 1'bz : i2c_scl_o;
    assign i2c_sda_io = i2c_sda_oen ? 1'bz : i2c_sda_o;

    // ══════════════════════════════════════════════════════════════════
    // M06: GPIO
    // ══════════════════════════════════════════════════════════════════
    wire [7:0] gpio_in, gpio_out, gpio_oe;
    EF_GPIO8_APB u_gpio (
        .PCLK(clk_sys_i), .PRESETn(rst_ni),
        .PWRITE(s_pwrite[4]), .PWDATA(s_pwdata[4]), .PADDR(s_paddr[4]),
        .PENABLE(s_penable[4]), .PSEL(s_psel[4]),
        .PREADY(s_pready[4]), .PRDATA(s_prdata[4]),
        .IRQ(irq_gpio_combined),
        .io_in(gpio_in), .io_out(gpio_out), .io_oe(gpio_oe)
    );
    assign gpio_in = gpio_io;
    assign gpio_io = gpio_oe ? gpio_out : 8'bz;

    // ══════════════════════════════════════════════════════════════════
    // M07: PWM + Watchdog
    // ══════════════════════════════════════════════════════════════════
    pwm_wrapper u_pwm (
        .clk_i(clk_sys_i), .rst_ni(rst_ni),
        .pwm_paddr(s_paddr[5]), .pwm_pwdata(s_pwdata[5]), .pwm_prdata(s_prdata[5]),
        .pwm_pwrite(s_pwrite[5]), .pwm_psel(s_psel[5]), .pwm_penable(s_penable[5]),
        .pwm_pready(s_pready[5]),
        .wdt_paddr(s_paddr[7]), .wdt_pwdata(s_pwdata[7]), .wdt_prdata(s_prdata[7]),
        .wdt_pwrite(s_pwrite[7]), .wdt_psel(s_psel[7]), .wdt_penable(s_penable[7]),
        .wdt_pready(s_pready[7]),
        .pwm0(pwm0_o), .pwm1(pwm1_o),
        .pwm_irq_o(irq_pwm), .wdt_irq_o(irq_wdt), .wdt_rst_n_o(wdt_rst_n_ignored)
    );

    // ══════════════════════════════════════════════════════════════════
    // M09: Interrupt Controller
    // ══════════════════════════════════════════════════════════════════
    wire [12:0] irq_vec;
    assign irq_vec = {irq_wdt, irq_pwm, 5'b0, irq_gpio_combined, 2'b0, irq_i2c, irq_spi, irq_uart};
    interrupt_ctrl u_intc (
        .clk_i(clk_sys_i), .rst_ni(rst_ni),
        .paddr(s_paddr[6][7:0]), .pwdata(s_pwdata[6]), .prdata(s_prdata[6]),
        .pwrite(s_pwrite[6]), .psel(s_psel[6]), .penable(s_penable[6]),
        .pready(s_pready[6]), .irq_in(irq_vec), .cpu_irq_o(cpu_irq)
    );

    // ══════════════════════════════════════════════════════════════════
    // M12: System Control
    // ══════════════════════════════════════════════════════════════════
    sys_ctrl u_sysctrl (
        .clk_i(clk_sys_i), .rst_ni(rst_ni),
        .paddr(s_paddr[8][7:0]), .pwdata(s_pwdata[8]), .prdata(s_prdata[8]),
        .pwrite(s_pwrite[8]), .psel(s_psel[8]), .penable(s_penable[8]),
        .pready(s_pready[8]),
        .wdt_rst_n(1'b1), .ext_rst_n(rst_ni),
        .core_sleep_i(ibex_sleep), .clk_gate_en(clk_gate_en), .wake_event_i(2'b00)
    );

    // ══════════════════════════════════════════════════════════════════
    // M10: Wishbone Bridge (shares APB master port with Ibex)
    // ══════════════════════════════════════════════════════════════════
    wb_bridge u_wb_bridge (
        .clk_i(clk_sys_i), .rst_ni(rst_ni),
        .wb_adr_i(wb_adr_i), .wb_dat_i(wb_dat_i), .wb_dat_o(wb_dat_o),
        .wb_sel_i(wb_sel_i), .wb_we_i(wb_we_i), .wb_stb_i(wb_stb_i),
        .wb_cyc_i(wb_cyc_i), .wb_ack_o(wb_ack_o), .wb_err_o(wb_err_o),
        .apb_paddr(wb_apb_paddr), .apb_pwdata(wb_apb_pwdata),
        .apb_prdata(wb_apb_prdata), .apb_pwrite(wb_apb_pwrite),
        .apb_psel(wb_apb_psel), .apb_penable(wb_apb_penable),
        .apb_pready(wb_apb_pready), .apb_pslverr(apb_mpslverr)
    );
    assign wb_active = wb_cyc_i && wb_stb_i;

endmodule
