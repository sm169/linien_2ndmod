`timescale 1ns / 1ps

module tb_modulation;

    // Define the parameters for the waves
    parameter integer CYCLES = 1000;
    integer i;
    
    // Declare the signals for the waves
    reg [15:0] fm_wave;
    reg [15:0] carrier_wave;
    reg [15:0] mod_wave;
    
    // Clock signal
    reg clk;
    
    // Simulation-related output files
    integer fm_wave_file;
    integer carrier_wave_file;
    integer mod_wave_file;

    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk; // 100 MHz clock
    end
    
    // Initialize the wave files
    initial begin
        fm_wave_file = $fopen("fm_wave.txt", "w");
        carrier_wave_file = $fopen("carrier_wave.txt", "w");
        mod_wave_file = $fopen("mod_wave.txt", "w");
    end

    // Generate the modulation waves
    initial begin
        // Initialize waves
        fm_wave = 0;
        carrier_wave = 0;
        mod_wave = 0;
        
        // Simulate for 1000 cycles
        for (i = 0; i < CYCLES; i = i + 1) begin
            @(posedge clk);
            fm_wave = $random; // Simulating FM wave
            carrier_wave = $random; // Simulating carrier wave
            mod_wave = fm_wave + carrier_wave; // Simulating modulated wave

            // Write to output files for plotting
            $fwrite(fm_wave_file, "%0d\n", fm_wave);
            $fwrite(carrier_wave_file, "%0d\n", carrier_wave);
            $fwrite(mod_wave_file, "%0d\n", mod_wave);
        end
        
        // Close the files after simulation
        $fclose(fm_wave_file);
        $fclose(carrier_wave_file);
        $fclose(mod_wave_file);
        
        $finish;
    end

endmodule
