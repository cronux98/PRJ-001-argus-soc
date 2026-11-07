# Makefile for ibex_core cocotb testbench
MODULE = test_ibex_core
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = \
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
    ~/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/reg_file.v
TOPLEVEL = ibex_core
SIM = icarus
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

include $(shell cocotb-config --makefiles)/Makefile.sim
