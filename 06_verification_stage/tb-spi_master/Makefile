# Makefile for spi_master cocotb testbench
MODULE = test_spi_master
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/common/ef_util_lib.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-spi_master/rtl/EF_SPI_APB.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-spi_master/rtl/EF_SPI.v \
    /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/04_frontend_stage/rtl-spi_master/rtl/spi_master.v
TOPLEVEL = EF_SPI_APB
SIM = icarus
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

include $(shell cocotb-config --makefiles)/Makefile.sim
