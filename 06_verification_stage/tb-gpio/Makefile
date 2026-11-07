# Makefile for gpio cocotb testbench
MODULE = test_gpio
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/common/ef_util_lib.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-gpio/rtl/EF_GPIO8_APB.v \
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-gpio/rtl/EF_GPIO8.v
TOPLEVEL = EF_GPIO8_APB
SIM = icarus
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

include $(shell cocotb-config --makefiles)/Makefile.sim
