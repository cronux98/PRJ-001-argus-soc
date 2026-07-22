# Makefile for sys_ctrl cocotb testbench
MODULE = test_sys_ctrl
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/../../04_frontend_stage/rtl-sys_ctrl/rtl/sys_ctrl.v
TOPLEVEL = sys_ctrl
SIM = icarus
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps
include $(shell cocotb-config --makefiles)/Makefile.sim
