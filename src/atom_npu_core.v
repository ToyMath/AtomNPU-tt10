module atom_npu_core (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       start,
    input  wire [3:0] input_data,
    input  wire [3:0] weight,
    output reg  [3:0] output_data,
    output reg        done
);

    localparam IDLE = 2'b00;
    localparam CALC = 2'b01;
    localparam DONE = 2'b10;

    reg [1:0] state;
    reg [2:0] bit_count;
    reg [3:0] multiplier;
    reg [7:0] accumulator;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state        <= IDLE;
            bit_count    <= 0;
            multiplier   <= 0;
            accumulator  <= 0;
            output_data  <= 0;
            done         <= 0;
        end else begin
            case (state)
                IDLE: begin
                    if (start) begin
                        state       <= CALC;
                        bit_count   <= 0;
                        multiplier  <= weight;
                        accumulator <= 0;
                        done        <= 0;
                    end
                end

                CALC: begin
                    if (bit_count < 4) begin
                        if (multiplier[0])
                            accumulator <= accumulator + ({4'b0000, input_data} << bit_count);
                        multiplier    <= multiplier >> 1;
                        bit_count     <= bit_count + 1;
                    end else begin
                        state <= DONE;
                        if (accumulator > 8'd15)
                            output_data <= 4'd15;
                        else
                            output_data <= accumulator[3:0];
                    end
                end

                DONE: begin
                    done    <= 1;
                    state   <= IDLE;
                end

                default: state <= IDLE;
            endcase
        end
    end

endmodule
