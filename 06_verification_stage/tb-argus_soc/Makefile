# Makefile for argus_soc cocotb testbench
MODULE = test_argus_soc
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/common/ef_util_lib.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-argus_soc/rtl/argus_soc.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-uart/rtl/EF_UART_APB.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-uart/rtl/EF_UART.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-gpio/rtl/EF_GPIO8_APB.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-gpio/rtl/EF_GPIO8.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-spi_master/rtl/EF_SPI_APB.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-spi_master/rtl/EF_SPI.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-spi_master/rtl/spi_master.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/EF_I2C_APB.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/i2c_master.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/i2c_master_axil.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/i2c_master_wbs_16.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/i2c_init.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/axis_fifo.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/i2c_single_reg.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-pwm/rtl/pwm_wrapper.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-pwm/rtl/EF_TMR32_APB.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-pwm/rtl/EF_TMR32.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-pwm/rtl/EF_WDT32_APB.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-pwm/rtl/EF_WDT32.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-sram/rtl/sram.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-interrupt_ctrl/rtl/interrupt_ctrl.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-wb_bridge/rtl/wb_bridge.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-apb_interconnect/rtl/apb_interconnect.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/ibex_core.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/ibex_core_inner.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/alu.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/alu_ctrl.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/branch_unit.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/ctrl_unit.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/ex_mem.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/forwarding_unit.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/hazard_unit.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/id_ex.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/if_id.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/imm_gen.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/mem_wb.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/pc.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/reg_file.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-sys_ctrl/rtl/sys_ctrl.v
TOPLEVEL = argus_soc
SIM = icarus
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

include $(shell cocotb-config --makefiles)/Makefile.sim
