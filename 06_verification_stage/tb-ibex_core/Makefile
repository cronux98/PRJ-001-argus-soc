# Makefile for ibex_core cocotb testbench
MODULE = test_ibex_core
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = \
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
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-ibex_core/rtl/reg_file.v
TOPLEVEL = ibex_core
SIM = icarus
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

include $(shell cocotb-config --makefiles)/Makefile.sim
