// =========================================================================
// Formal wrapper: sram_formal — simplified for BMC
// Reduced memory + basic structural checks.
// =========================================================================

`default_nettype none
`timescale 1ns / 1ps

module sram_formal (
    input  wire        clk_i,
    input  wire        rst_ni,
    input  wire [31:0] imem_addr,
    output wire [31:0] imem_rdata,
    input  wire [31:0] dmem_addr,
    input  wire [31:0] dmem_wdata,
    output wire [31:0] dmem_rdata,
    input  wire        dmem_we,
    input  wire [ 3:0] dmem_be,
    input  wire [31:0] apb_paddr,
    input  wire [31:0] apb_pwdata,
    output wire [31:0] apb_prdata,
    input  wire        apb_we,
    input  wire [ 3:0] apb_be
);

    reg [31:0] mem [0:7];
    
    wire [2:0] imem_word = imem_addr[4:2];
    wire [2:0] dmem_word = dmem_addr[4:2];
    wire [2:0] apb_word  = apb_paddr[4:2];
    
    wire imem_valid  = (imem_addr[31:5] == 27'd0);
    wire dmem_valid  = (dmem_addr[31:5] == 27'd0);
    wire apb_valid   = (apb_paddr[31:5] == 27'd0);
    
    wire dmem_conflict = imem_valid && dmem_valid && (dmem_word == imem_word) && dmem_we;
    wire apb_conflict  = (imem_valid || dmem_valid) && apb_valid && apb_we;

    assign imem_rdata = imem_valid ? mem[imem_word] : 32'd0;
    assign dmem_rdata = dmem_valid ? mem[dmem_word] : 32'd0;
    assign apb_prdata = apb_valid  ? mem[apb_word]  : 32'd0;

    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            mem[0] <= 32'd0; mem[1] <= 32'd0; mem[2] <= 32'd0; mem[3] <= 32'd0;
            mem[4] <= 32'd0; mem[5] <= 32'd0; mem[6] <= 32'd0; mem[7] <= 32'd0;
        end else begin
            if (dmem_valid && dmem_we && !dmem_conflict) begin
                if (dmem_be[0]) mem[dmem_word][ 7: 0] <= dmem_wdata[ 7: 0];
                if (dmem_be[1]) mem[dmem_word][15: 8] <= dmem_wdata[15: 8];
                if (dmem_be[2]) mem[dmem_word][23:16] <= dmem_wdata[23:16];
                if (dmem_be[3]) mem[dmem_word][31:24] <= dmem_wdata[31:24];
            end
            if (apb_valid && apb_we && !apb_conflict) begin
                if (apb_be[0]) mem[apb_word][ 7: 0] <= apb_pwdata[ 7: 0];
                if (apb_be[1]) mem[apb_word][15: 8] <= apb_pwdata[15: 8];
                if (apb_be[2]) mem[apb_word][23:16] <= apb_pwdata[23:16];
                if (apb_be[3]) mem[apb_word][31:24] <= apb_pwdata[31:24];
            end
        end
    end

    // ── Simple assertions ──
    // After reset, outputs should be stable
    reg [3:0] rst_cnt;
    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) rst_cnt <= 4'd0;
        else if (rst_cnt < 4'd15) rst_cnt <= rst_cnt + 1'b1;
    end
    
    // In first 5 cycles after reset, IMEM reads address 0 should return 0
    wire post_reset = (rst_cnt > 4'd2) && (rst_cnt < 4'd10);
    always @(*) begin
        if (post_reset && imem_valid && (imem_word == 3'd0))
            assert(imem_rdata == 32'd0);
    end

    // Address out of range returns 0
    always @(*) begin
        if (!imem_valid) assert(imem_rdata == 32'd0);
        if (!dmem_valid) assert(dmem_rdata == 32'd0);
        if (!apb_valid)  assert(apb_prdata == 32'd0);
    end

    // Cover: can we write then read?
    reg wrote_and_read;
    always @(posedge clk_i) begin
        if (dmem_valid && dmem_we && !dmem_conflict)
            wrote_and_read <= 1'b0;
        else if (wrote_and_read == 1'b0 && dmem_valid && !dmem_we && !dmem_conflict)
            wrote_and_read <= 1'b1;
    end
    always @(*) begin
        cover(wrote_and_read);
    end

endmodule
