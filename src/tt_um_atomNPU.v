/*
 * Copyright (c) 2024 Aakash Apoorv
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none
`timescale 1ns / 1ps

module tt_um_atomNPU (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
    // Declare internal wires
    wire start;
    wire done;
    wire npu_done;

    // Assign 'start' to uio_in[4]
    assign start = uio_in[4];

    // Instantiate the Tiny NPU Core
    atom_npu_core npu (
        .clk(clk),
        .rst_n(rst_n),
        .start(start),
        .input_data(ui_in[3:0]),   // Using lower 4 bits of ui_in
        .weight(uio_in[3:0]),      // Using lower 4 bits of uio_in
        .output_data(npu_output[3:0]),
        .done(npu_done)
    );

    // Assign the lower 4 bits of uo_out to the NPU output and set upper bits to 0
    assign uo_out = {4'd0, npu_output[3:0]};

    // Assign unused outputs to 0
    assign uio_out = 8'd0;
    assign uio_oe  = 8'd0;

    // Assign 'done' signal
    assign done = npu_done;

    // List all unused inputs to prevent warnings
    wire unused = &{ena, clk, rst_n, 1'b0, ui_in[7:4], uio_in[7:4]};
endmodule
