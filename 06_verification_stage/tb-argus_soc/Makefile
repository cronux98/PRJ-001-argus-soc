# Makefile for argus_soc cocotb testbench
MODULE = test_argus_soc
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/common/ef_util_lib.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-argus_soc/rtl/argus_soc.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-uart/rtl/EF_UART_APB.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-uart/rtl/EF_UART.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-gpio/rtl/EF_GPIO8_APB.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-gpio/rtl/EF_GPIO8.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-spi_master/rtl/EF_SPI_APB.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-spi_master/rtl/EF_SPI.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-spi_master/rtl/spi_master.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/EF_I2C_APB.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/i2c_master.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/i2c_master_axil.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/i2c_master_wbs_16.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/i2c_init.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/axis_fifo.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/i2c_single_reg.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-pwm/rtl/pwm_wrapper.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-pwm/rtl/EF_TMR32_APB.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-pwm/rtl/EF_TMR32.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-pwm/rtl/EF_WDT32_APB.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-pwm/rtl/EF_WDT32.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-sram/rtl/sram.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-interrupt_ctrl/rtl/interrupt_ctrl.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-wb_bridge/rtl/wb_bridge.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-apb_interconnect/rtl/apb_interconnect.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/ibex_core.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/ibex_core_inner.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/alu.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/alu_ctrl.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/branch_unit.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/ctrl_unit.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/ex_mem.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/forwarding_unit.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/hazard_unit.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/id_ex.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/if_id.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/imm_gen.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/mem_wb.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/pc.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/reg_file.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-sys_ctrl/rtl/sys_ctrl.v
TOPLEVEL = argus_soc
SIM = icarus
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

include $(shell cocotb-config --makefiles)/Makefile.sim
