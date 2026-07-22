# Makefile for pwm cocotb testbench
MODULE = test_pwm
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/common/ef_util_lib.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-pwm/rtl/pwm_wrapper.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-pwm/rtl/EF_TMR32_APB.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-pwm/rtl/EF_TMR32.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-pwm/rtl/EF_WDT32_APB.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-pwm/rtl/EF_WDT32.v
TOPLEVEL = pwm_wrapper
SIM = icarus
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

include $(shell cocotb-config --makefiles)/Makefile.sim
