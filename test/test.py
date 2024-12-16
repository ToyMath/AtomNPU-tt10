# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")
    
    # Create a 10us period clock on port clk
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    # Reset sequence
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    
    # Test case 1: Simple multiplication (2 x 3)
    dut._log.info("Test case 1: 2 x 3")
    dut.ui_in.value = 2  # input_data = 2
    dut.uio_in.value = 0x13  # weight = 3, start = 1 (bit 4)
    
    # Wait for done signal (bit 5 of uo_out)
    max_cycles = 20
    cycles = 0
    while cycles < max_cycles and dut.uo_out.value & 0x20 == 0:
        await RisingEdge(dut.clk)
        cycles += 1
    
    # Check result - expected 6
    result = dut.uo_out.value & 0x0F
    assert result == 6, f"Test case 1 failed. Expected 6, got {result}"
    dut._log.info(f"Test case 1 passed. Result: {result}")
    
    # Reset start signal
    dut.uio_in.value = 0x03  # Keep weight = 3, start = 0
    await ClockCycles(dut.clk, 2)
    
    # Test case 2: Maximum value test (15 x 15)
    dut._log.info("Test case 2: 15 x 15")
    dut.ui_in.value = 15  # input_data = 15
    dut.uio_in.value = 0x1F  # weight = 15, start = 1
    
    # Wait for done signal
    cycles = 0
    while cycles < max_cycles and dut.uo_out.value & 0x20 == 0:
        await RisingEdge(dut.clk)
        cycles += 1
    
    # Check result - expected 15 (saturation)
    result = dut.uo_out.value & 0x0F
    assert result == 15, f"Test case 2 failed. Expected 15, got {result}"
    dut._log.info(f"Test case 2 passed. Result: {result}")
    
    # Reset start signal
    dut.uio_in.value = 0x0F  # Keep weight = 15, start = 0
    await ClockCycles(dut.clk, 2)
    
    # Test case 3: Zero multiplication
    dut._log.info("Test case 3: 5 x 0")
    dut.ui_in.value = 5  # input_data = 5
    dut.uio_in.value = 0x10  # weight = 0, start = 1
    
    # Wait for done signal
    cycles = 0
    while cycles < max_cycles and dut.uo_out.value & 0x20 == 0:
        await RisingEdge(dut.clk)
        cycles += 1
    
    # Check result - expected 0
    result = dut.uo_out.value & 0x0F
    assert result == 0, f"Test case 3 failed. Expected 0, got {result}"
    dut._log.info(f"Test case 3 passed. Result: {result}")
    
    dut._log.info("All tests passed!")
