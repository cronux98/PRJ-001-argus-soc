# CDC Plan — PRJ-001 Argus

**Project:** PRJ-001 (Argus) Environmental Sensor-Hub SoC
**Date:** 2026-07-20
**Architect:** architect-engineer (Hermes)
**Clock Domains:** 2 (clk_sys, clk_wb)

---

## 1. Clock Domain Summary

| Domain | Source | Frequency | Consumers |
|--------|--------|-----------|-----------|
| clk_sys | Caravel user_clock2 | 50 MHz | M01–M09, M11, M12 — all internal logic |
| clk_wb | Caravel management SoC | 10–25 MHz | M10 (wb_bridge, Wishbone side only) |

**Relationship:** Asynchronous. No fixed phase or frequency relationship.
clk_wb is generated independently by the Caravel management SoC.

---

## 2. CDC Path Inventory

### 2.1 Wishbone → APB (clk_wb → clk_sys)

| Path | Signal | Width | Method | Depth |
|------|--------|-------|--------|-------|
| WB command → APB transaction | {wb_adr_i[31:0], wb_dat_i[31:0], wb_sel_i[3:0], wb_we_i} | 69 bits | Async FIFO (dual-clock) | 8 entries |
| WB cycle control → APB enable | wb_cyc_i, wb_stb_i | 2 bits | 2-FF synchronizer | 2 stages |

**Rationale:** The command FIFO crosses all transaction data. Write pointer in clk_wb,
read pointer in clk_sys, Gray-coded for safe crossing. Full/empty flags prevent
overflow/underflow. The 2-FF synchronizer for cycle/strobe adds 2 clk_sys cycles of
latency (40 ns at 50 MHz) — acceptable for the slow Wishbone management path.

### 2.2 APB → Wishbone (clk_sys → clk_wb)

| Path | Signal | Width | Method | Depth |
|------|--------|-------|--------|-------|
| APB read response → WB response | apb_prdata[31:0] | 32 bits | Async FIFO (dual-clock) | 4 entries |
| APB ready/error → WB ack/err | apb_pready, apb_pslverr | 2 bits | 2-FF synchronizer | 2 stages |

**Rationale:** Read data FIFO captures APB response before crossing to clk_wb. The
response FIFO is shallower (4 deep) because read transactions are typically single
or few-beat bursts from the Caravel management SoC.

---

## 3. Non-CDC Paths (No Crossing Required)

All peripheral IRQs (M03–M07 → M09) and the CPU IRQ (M09 → M01) are wholly within
the clk_sys domain. No CDC synchronization needed. Per SYS-CR-011, the design is
single-clock-domain for all internal logic.

---

## 4. CDC Verification Strategy

| Check | Tool | Coverage |
|-------|------|----------|
| Async FIFO correctness | Yosys-SMTBMC (formal) | All read/write pointer crossings, full/empty flag generation |
| 2-FF synchronizer metastability | Static check (Yosys `cdc` pass) | All single-bit crossings enumerated above |
| No undocumented crossings | Lint (Verilator CDC) | All signals crossing domain boundaries must appear in this plan |
| Gate-level CDC | GLS (iverilog + SDF) | Post-synthesis simulation with realistic clk_wb/clk_sys phase drift |

---

## 5. CDC Design Rules

1. **No direct domain crossing:** All clk_wb ↔ clk_sys crossings go through M10 (wb_bridge).
   No other module may use signals from the other clock domain.
2. **Registered outputs:** All signals crossing into an async FIFO are registered in the
   source domain before the FIFO write.
3. **Gray coding:** All multi-bit pointers (FIFO read/write pointers) use Gray code to
   ensure at most one bit transitions per clock edge.
4. **No combinational crossing:** No combinational logic between domains. All crossings
   are through synchronizer cells or dual-clock FIFO primitives.
5. **CDC exceptions recorded:** Any waived CDC path is documented in this plan with
   justification (none currently).

---

## 6. Single-Domain Declaration

For all modules other than M10 (wb_bridge), the design operates on a single clock domain
(clk_sys). The CDC plan confirms:

- **Total CDC paths:** 2 (WB→APB command FIFO, APB→WB response FIFO)
- **Total CDC crossings:** 2 FIFOs + 4 single-bit synchronizers
- **CDC complexity:** Low — two async FIFOs, confined to one module (M10)

This is documented for the RTL flow agent and for the formal verification engineer.
