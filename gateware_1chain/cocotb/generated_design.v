/* Machine-generated using Migen */
module mod(
	input sys_clk,
	input sys_rst
);

reg [31:0] freq_storage = 32'd0;
reg [17:0] mod_depth_storage = 18'd0;
reg [31:0] mod_freq_storage = 32'd0;
reg [31:0] carrier_phase = 32'd0;
reg [31:0] mod_phase = 32'd0;
reg signed [15:0] carrier_wave;
reg signed [15:0] mod_wave;
reg signed [15:0] fm_wave;
wire [9:0] carrier_lut_rdport_adr;
wire [15:0] carrier_lut_rdport_dat_r;
wire [9:0] mod_lut_rdport_adr;
wire [15:0] mod_lut_rdport_dat_r;
wire [9:0] fm_lut_rdport_adr;
wire [15:0] fm_lut_rdport_dat_r;
wire [31:0] combined_phase;
wire [8:0] carrier_address;
wire [8:0] mod_address;
wire [8:0] fm_address;
wire [15:0] carrier_lut_out;
wire [15:0] mod_lut_out;
wire [15:0] fm_lut_out;
wire [1:0] quadrant0;
wire [1:0] quadrant1;
wire [1:0] quadrant2;

// synthesis translate_off
reg dummy_s;
initial dummy_s <= 1'd0;
// synthesis translate_on

assign combined_phase = ($signed({1'd0, carrier_phase}) + (mod_wave * $signed({1'd0, mod_depth_storage})));
assign carrier_address = carrier_phase[31:23];
assign mod_address = mod_phase[31:23];
assign fm_address = combined_phase[31:23];
assign carrier_lut_rdport_adr = carrier_address;
assign carrier_lut_out = carrier_lut_rdport_dat_r;
assign mod_lut_rdport_adr = mod_address;
assign mod_lut_out = mod_lut_rdport_dat_r;
assign fm_lut_rdport_adr = fm_address;
assign fm_lut_out = fm_lut_rdport_dat_r;
assign quadrant0 = carrier_phase[31];

// synthesis translate_off
reg dummy_d;
// synthesis translate_on
always @(*) begin
	carrier_wave <= 16'sd0;
	if ((quadrant0 == 1'd0)) begin
		carrier_wave <= carrier_lut_out;
	end else begin
		if ((quadrant0 == 1'd1)) begin
			carrier_wave <= carrier_lut_out;
		end else begin
			if ((quadrant0 == 2'd2)) begin
				carrier_wave <= (-$signed({1'd0, carrier_lut_out}));
			end else begin
				carrier_wave <= (-$signed({1'd0, carrier_lut_out}));
			end
		end
	end
// synthesis translate_off
	dummy_d <= dummy_s;
// synthesis translate_on
end
assign quadrant1 = mod_phase[31];

// synthesis translate_off
reg dummy_d_1;
// synthesis translate_on
always @(*) begin
	mod_wave <= 16'sd0;
	if ((quadrant1 == 1'd0)) begin
		mod_wave <= mod_lut_out;
	end else begin
		if ((quadrant1 == 1'd1)) begin
			mod_wave <= mod_lut_out;
		end else begin
			if ((quadrant1 == 2'd2)) begin
				mod_wave <= (-$signed({1'd0, mod_lut_out}));
			end else begin
				mod_wave <= (-$signed({1'd0, mod_lut_out}));
			end
		end
	end
// synthesis translate_off
	dummy_d_1 <= dummy_s;
// synthesis translate_on
end
assign quadrant2 = combined_phase[31];

// synthesis translate_off
reg dummy_d_2;
// synthesis translate_on
always @(*) begin
	fm_wave <= 16'sd0;
	if ((quadrant2 == 1'd0)) begin
		fm_wave <= fm_lut_out;
	end else begin
		if ((quadrant2 == 1'd1)) begin
			fm_wave <= fm_lut_out;
		end else begin
			if ((quadrant2 == 2'd2)) begin
				fm_wave <= (-$signed({1'd0, fm_lut_out}));
			end else begin
				fm_wave <= (-$signed({1'd0, fm_lut_out}));
			end
		end
	end
// synthesis translate_off
	dummy_d_2 <= dummy_s;
// synthesis translate_on
end

always @(posedge sys_clk) begin
	carrier_phase <= (carrier_phase + freq_storage);
	mod_phase <= (mod_phase + mod_freq_storage);
	if (sys_rst) begin
		carrier_phase <= 32'd0;
		mod_phase <= 32'd0;
	end
end

reg [15:0] lut[0:1023];
reg [9:0] memadr;
reg [9:0] memadr_1;
reg [9:0] memadr_2;
always @(posedge sys_clk) begin
	memadr <= carrier_lut_rdport_adr;
end

always @(posedge sys_clk) begin
	memadr_1 <= mod_lut_rdport_adr;
end

always @(posedge sys_clk) begin
	memadr_2 <= fm_lut_rdport_adr;
end

assign carrier_lut_rdport_dat_r = lut[memadr];
assign mod_lut_rdport_dat_r = lut[memadr_1];
assign fm_lut_rdport_dat_r = lut[memadr_2];

initial begin
	$readmemh("lut.init", lut);
end

endmodule
