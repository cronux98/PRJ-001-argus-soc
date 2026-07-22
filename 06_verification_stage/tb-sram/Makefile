# Makefile for sram cocotb testbench
MODULE = test_sram
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-sram/rtl/sram.v
TOPLEVEL = sram
SIM = icarus
COMPILE_ARGS = -DSIMULATION
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

include $(shell cocotb-config --makefiles)/Makefile.sim
