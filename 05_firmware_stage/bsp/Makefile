# Makefile — PRJ-001 (Argus) Firmware Build
# GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT
#
# Pinned toolchain: riscv32-unknown-elf-gcc 14.2.1
# ISA: RV32I (no M, no C, no F, no A)
# ABI: ilp32

CC      := /opt/OpenROAD/riscv/gcc14-no-zcmp/bin/riscv32-unknown-elf-gcc
OBJCOPY := /opt/OpenROAD/riscv/gcc14-no-zcmp/bin/riscv32-unknown-elf-objcopy
OBJDUMP := /opt/OpenROAD/riscv/gcc14-no-zcmp/bin/riscv32-unknown-elf-objdump
SIZE    := /opt/OpenROAD/riscv/gcc14-no-zcmp/bin/riscv32-unknown-elf-size

MARCH   := rv32i_zicsr
MABI    := ilp32

CFLAGS  := -march=$(MARCH) -mabi=$(MABI) -Os -Wall -Wextra \
           -ffreestanding -nostdlib -nostartfiles \
           -fno-common -fno-builtin -fdata-sections -ffunction-sections

LDFLAGS := -march=$(MARCH) -mabi=$(MABI) -nostdlib -nostartfiles \
           -T bsp/link.ld -Wl,-Map,build/fw.map \
           -Wl,--gc-sections

# ── Project structure ──
PROJ_ROOT := /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/05_firmware_stage
INCLUDES  := -I$(PROJ_ROOT)/bsp/include \
             -I$(PROJ_ROOT)/fw/drivers/uart \
             -I$(PROJ_ROOT)/fw/drivers/spi \
             -I$(PROJ_ROOT)/fw/drivers/i2c \
             -I$(PROJ_ROOT)/fw/drivers/gpio \
             -I$(PROJ_ROOT)/fw/drivers/pwm \
             -I$(PROJ_ROOT)/fw/drivers/watchdog \
             -I$(PROJ_ROOT)/fw/drivers/sysctrl \
             -I$(PROJ_ROOT)/fw/drivers/intctrl \
             -I$(PROJ_ROOT)/fw/drivers/sensor

# ── Source files ──
CRT0     := bootrom/crt0.S

DRIVERS  := fw/drivers/uart/uart_driver.c \
            fw/drivers/spi/spi_driver.c \
            fw/drivers/i2c/i2c_driver.c \
            fw/drivers/gpio/gpio_driver.c \
            fw/drivers/pwm/pwm_driver.c \
            fw/drivers/watchdog/watchdog_driver.c \
            fw/drivers/sysctrl/sysctrl_driver.c \
            fw/drivers/intctrl/intctrl_driver.c \
            fw/drivers/sensor/sensor_poll.c

MAIN     := fw/main.c

SRCS     := $(CRT0) $(DRIVERS) $(MAIN)
OBJS     := $(patsubst %.c,build/%.o,$(patsubst %.S,build/%.o,$(SRCS)))

# ── Targets ──
.PHONY: all clean

all: build/fw.elf bootrom/bootrom.bin bootrom/bootrom.hex

# Create build directories
$(shell mkdir -p build/fw/drivers/uart \
                  build/fw/drivers/spi \
                  build/fw/drivers/i2c \
                  build/fw/drivers/gpio \
                  build/fw/drivers/pwm \
                  build/fw/drivers/watchdog \
                  build/fw/drivers/sysctrl \
                  build/fw/drivers/intctrl \
                  build/fw/drivers/sensor \
                  build/bootrom build/fw)

# Compile assembly files
build/%.o: %.S
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

# Compile C files
build/%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

# Link
build/fw.elf: $(OBJS) bsp/link.ld
	$(CC) $(LDFLAGS) $(OBJS) -o $@

# Generate binary and hex
bootrom/bootrom.bin: build/fw.elf
	$(OBJCOPY) -O binary $< $@

bootrom/bootrom.hex: build/fw.elf
	$(OBJCOPY) -O ihex $< $@

# Size report
size: build/fw.elf
	$(SIZE) $@

# Disassembly
disasm: build/fw.elf
	$(OBJDUMP) -d $< > build/fw.disasm

clean:
	rm -rf build bootrom/bootrom.bin bootrom/bootrom.hex
