# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, FallingEdge

async def reset_dut(dut):
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

async def perform_calculation(dut, input_data, weight):
    dut.ui_in.value = input_data & 0xF
    dut.uio_in.value = weight & 0xF 
    await ClockCycles(dut.clk, 2)
    
    # Then assert start signal
    dut.uio_in.value = (weight & 0xF) | 0x10
    await ClockCycles(dut.clk, 1)
    
    # Clear start signal
    dut.uio_in.value = weight & 0xF
    
    # Wait for done signal
    max_cycles = 20
    for _ in range(max_cycles):
        if dut.uo_out.value & 0x20:
            break
        await RisingEdge(dut.clk)
    
    # Wait one more cycle for stability
    await ClockCycles(dut.clk, 1)
    
    # Return result
    return dut.uo_out.value & 0xF

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")
    
    # Create a 10us period clock
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    # Reset the DUT
    dut._log.info("Reset")
    await reset_dut(dut)
    
    # Test case 1: Simple multiplication (2 x 3)
    dut._log.info("Test case 1: 2 x 3")
    result = await perform_calculation(dut, 2, 3)
    assert result == 6, f"Test case 1 failed. Expected 6, got {result}"
    dut._log.info(f"Test case 1 passed. Result: {result}")
    await ClockCycles(dut.clk, 2)
    
    # Test case 2: Maximum value test (15 x 15)
    dut._log.info("Test case 2: 15 x 15")
    result = await perform_calculation(dut, 15, 15)
    assert result == 15, f"Test case 2 failed. Expected 15, got {result}"
    dut._log.info(f"Test case 2 passed. Result: {result}")
    await ClockCycles(dut.clk, 2)
    
    # Test case 3: Zero multiplication (5 x 0)
    dut._log.info("Test case 3: 5 x 0")
    result = await perform_calculation(dut, 5, 0)
    assert result == 0, f"Test case 3 failed. Expected 0, got {result}"
    dut._log.info(f"Test case 3 passed. Result: {result}")
    
    # Test case 4: Intermediate value (7 x 2)
    dut._log.info("Test case 4: 7 x 2")
    result = await perform_calculation(dut, 7, 2)
    assert result == 14, f"Test case 4 failed. Expected 14, got {result}"
    dut._log.info(f"Test case 4 passed. Result: {result}")
    
    dut._log.info("All tests passed!")
