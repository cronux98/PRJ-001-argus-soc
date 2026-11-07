# Makefile for i2c_master cocotb testbench
MODULE = test_i2c_master
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/common/ef_util_lib.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/EF_I2C_APB.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/i2c_master.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/i2c_master_axil.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/i2c_master_wbs_16.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/i2c_init.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/axis_fifo.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-i2c_master/rtl/i2c_single_reg.v
TOPLEVEL = EF_I2C_APB
SIM = icarus
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

include $(shell cocotb-config --makefiles)/Makefile.sim
