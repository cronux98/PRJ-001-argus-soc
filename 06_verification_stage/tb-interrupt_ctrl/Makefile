# Makefile for interrupt_ctrl cocotb testbench
MODULE = test_interrupt_ctrl
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-interrupt_ctrl/rtl/interrupt_ctrl.v
TOPLEVEL = interrupt_ctrl
SIM = icarus
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

include $(shell cocotb-config --makefiles)/Makefile.sim
