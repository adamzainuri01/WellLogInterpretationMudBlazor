using Well_Log_Mudblazor.Models.LogClass;
using Newtonsoft.Json;
using System.Text.Json;
using Microsoft.JSInterop;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace Well_Log_Mudblazor.Models.LogTask
{
    public class LogTask
    {
        private readonly PlotData? plotData;
        private readonly PlotOptions? plotOptions;
        private readonly PlotImage? plotImage;
        private readonly LogValues? logValues;
        private readonly ResParams? resParams;
        private readonly HttpClient Http;
        private readonly IJSRuntime _jsRuntime;

        public LogTask(IJSRuntime jsRuntime, HttpClient httpClient, PlotData plotData, PlotOptions plotOptions, PlotImage plotImage, LogValues? logValues, ResParams? resParams)
        {
            _jsRuntime = jsRuntime;
            Http = httpClient;
            this.plotData = plotData;
            this.plotOptions = plotOptions;
            this.plotImage = plotImage;
            this.logValues = logValues;
            this.resParams = resParams;
        }

        public async Task ProcessComboPlot()
        {
            try
            {
                var content = new MultipartFormDataContent();

                content.Add(new StringContent(plotOptions.FigureHeight.ToString()), "figure_height");

                var response = await Http.PostAsync("http://localhost:8000/process-combo-plot/", content);

                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
                    if (result != null)
                    {
                        // Process the plot image information
                        plotImage.ResultMessage = result["message"].ToString();
                        
                        // Combo Plot Image using Python (deprecated)
                        // plotImage.Combo_Plot = result["combo_plot"].ToString();

                        var dfLasDict = result["df_las"] as JsonElement?;

                        var dfLasDictValue = dfLasDict.Value;
                        plotData.df_las_global = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, List<object>>>(dfLasDictValue.ToString());

                        var ColumnDataDict = result["column_data"] as JsonElement?;

                        var ColumnDataDictValue = ColumnDataDict.Value;
                        plotData.ColumnData = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, Dictionary<string, object>>>(ColumnDataDictValue.ToString());

                        plotData.Combo_Plot = true;
                    }
                }
                else
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    plotImage.ResultMessage = $"Failed to process file. Status code: {response.StatusCode}\nError details: {errorContent}";
                }
            }
            catch (Exception ex)
            {
                plotImage.ResultMessage = $"An error occurred: {ex.Message}";
            }
        }

        public async Task SendGlobalPlotData(string type_ = "combo")
        {
            var dfLasJson = System.Text.Json.JsonSerializer.Serialize(plotData.df_las_global);
            var columnDataJson = System.Text.Json.JsonSerializer.Serialize(plotData.ColumnData);

            if (type_ == "combo")
            {
                await _jsRuntime.InvokeVoidAsync("comboPlot", dfLasJson, columnDataJson);
            }

            else if (type_ == "vcl")          
            {
                await _jsRuntime.InvokeVoidAsync(
                    "vclPlot", 
                    dfLasJson, 
                    columnDataJson, 
                    new List<float?> 
                    { 
                        logValues.NPHI_Clean1, 
                        logValues.NPHI_Clean2, 
                        logValues.NPHI_Clay, 
                        logValues.RHOB_Clean1, 
                        logValues.RHOB_Clean2, 
                        logValues.RHOB_Clay 
                    }
                );
            }

            else if (type_ == "phi")          
            {
                await _jsRuntime.InvokeVoidAsync("comparisonPlot", dfLasJson, columnDataJson, "PHI");
            }

            else if (type_ == "pickett")          
            {
                await _jsRuntime.InvokeVoidAsync("pickettPlot", dfLasJson, columnDataJson, resParams.VCL_Limit, plotOptions.Z_Axis, resParams.A_Value, resParams.Water_Resistivity, resParams.M_Value, resParams.N_Value);
            }

            else if (type_ == "sw")          
            {
                await _jsRuntime.InvokeVoidAsync("comparisonPlot", dfLasJson, columnDataJson, "SW");
            }

            else if (type_ == "cutoff")          
            {
                await _jsRuntime.InvokeVoidAsync("cutoffPlot", dfLasJson, columnDataJson, resParams.VCL_Cutoff, resParams.PHI_Cutoff, resParams.SW_Cutoff);
            }      
        }

        public async Task ProcessVCLPlot()
        {
            try
            {
                var content = new MultipartFormDataContent();

                if (logValues.GR_Clean.HasValue)
                    content.Add(new StringContent(logValues.GR_Clean.ToString()), "gr_clean");
                if (logValues.GR_Clay.HasValue)
                    content.Add(new StringContent(logValues.GR_Clay.ToString()), "gr_clay");
                if (logValues.SP_Clean.HasValue)
                    content.Add(new StringContent(logValues.SP_Clean.ToString()), "sp_clean");
                if (logValues.SP_Clay.HasValue)
                    content.Add(new StringContent(logValues.SP_Clay.ToString()), "sp_clay");
                if (logValues.RT_Clean.HasValue)
                    content.Add(new StringContent(logValues.RT_Clean.ToString()), "rt_clean");
                if (logValues.RT_Clay.HasValue)
                    content.Add(new StringContent(logValues.RT_Clay.ToString()), "rt_clay");
                if (logValues.NPHI_Clean1.HasValue)
                    content.Add(new StringContent(logValues.NPHI_Clean1.ToString()), "neut_clean1");
                if (logValues.NPHI_Clean2.HasValue)
                    content.Add(new StringContent(logValues.NPHI_Clean2.ToString()), "neut_clean2");
                if (logValues.NPHI_Clay.HasValue)
                    content.Add(new StringContent(logValues.NPHI_Clay.ToString()), "neut_clay");
                if (logValues.RHOB_Clean1.HasValue)
                    content.Add(new StringContent(logValues.RHOB_Clean1.ToString()), "den_clean1");
                if (logValues.RHOB_Clean2.HasValue)
                    content.Add(new StringContent(logValues.RHOB_Clean2.ToString()), "den_clean2");
                if (logValues.RHOB_Clay.HasValue)
                    content.Add(new StringContent(logValues.RHOB_Clay.ToString()), "den_clay");

                content.Add(new StringContent(plotOptions.GR_Correction.ToString()), "correction_gr");

                var response = await Http.PostAsync("http://localhost:8000/process-vcl-plot/", content);

                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
                    if (result != null)
                    {
                        plotImage.ResultMessage = result["message"].ToString();
                        
                        // VCL Plot Image using Python (deprecated)
                        // plotImage.VCL_Plot = result["vcl_plot"].ToString();
                        
                        plotOptions.VCLOptions = JsonConvert.DeserializeObject<List<DropdownValue>>(result["dropdown_vcl"].ToString());

                        var dfLasDict = result["df_las"] as JsonElement?;

                        var dfLasDictValue = dfLasDict.Value;
                        plotData.df_las_global = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, List<object>>>(dfLasDictValue.ToString());

                        var ColumnDataDict = result["column_data"] as JsonElement?;

                        var ColumnDataDictValue = ColumnDataDict.Value;
                        plotData.ColumnData = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, Dictionary<string, object>>>(ColumnDataDictValue.ToString());

                        plotData.VCL_Plot = true;
                    }
                }
                else
                {
                    plotImage.ResultMessage = $"Failed to process file. Status code: {response.StatusCode}";
                }
            }
            catch (Exception ex)
            {
                plotImage.ResultMessage = $"An error occurred: {ex.Message}";
            }
        }

        public async Task ProcessPHIPlot()
        {
            try
            {   
                var content = new MultipartFormDataContent();

                if (logValues.NPHI_Clay.HasValue)
                    content.Add(new StringContent(logValues.NPHI_Clay.ToString()), "neut_sh");
                if (logValues.RHOB_Clean1.HasValue)
                    content.Add(new StringContent(logValues.RHOB_Clean1.ToString()), "den_ma");
                if (logValues.RHOB_Clean2.HasValue)
                    content.Add(new StringContent(logValues.RHOB_Clean2.ToString()), "den_fl");
                if (logValues.RHOB_Clay.HasValue)
                    content.Add(new StringContent(logValues.RHOB_Clay.ToString()), "den_sh");
                if (logValues.DT_Matrix.HasValue)
                    content.Add(new StringContent(logValues.DT_Matrix.ToString()), "dt_ma");
                if (logValues.DT_Fluid.HasValue)
                    content.Add(new StringContent(logValues.DT_Fluid.ToString()), "dt_fl");
                if (logValues.DT_Shale.HasValue)
                    content.Add(new StringContent(logValues.DT_Shale.ToString()), "dt_sh");

                content.Add(new StringContent(resParams.Cp.ToString()), "cp");
                content.Add(new StringContent(resParams.Alpha.ToString()), "alpha");
                content.Add(new StringContent(plotOptions.VCL_Select.ToString()), "vcl_select");

                var response = await Http.PostAsync("http://localhost:8000/process-phi-plot/", content);

                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
                    if (result != null)
                    {
                        plotImage.ResultMessage = result["message"].ToString();

                        // VCL Plot Image using Python (deprecated)
                        // plotImage.PHI_Plot = result["phi_plot"].ToString();

                        plotOptions.PHIOptions = JsonConvert.DeserializeObject<List<DropdownValue>>(result["dropdown_phi"].ToString());

                        var dfLasDict = result["df_las"] as JsonElement?;

                        var dfLasDictValue = dfLasDict.Value;
                        plotData.df_las_global = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, List<object>>>(dfLasDictValue.ToString());

                        var ColumnDataDict = result["column_data"] as JsonElement?;

                        var ColumnDataDictValue = ColumnDataDict.Value;
                        plotData.ColumnData = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, Dictionary<string, object>>>(ColumnDataDictValue.ToString());

                        plotData.PHI_Plot = true;
                    }
                }
                else
                {
                    plotImage.ResultMessage = $"Failed to process file. Status code: {response.StatusCode}";
                }
            }
            catch (Exception ex)
            {
                plotImage.ResultMessage = $"An error occurred: {ex.Message}";
            }
        }

        public async Task FromStartToFinish(string type_ = null)
        {   
            if (type_ == null)
            {
                await ProcessVCLPlot();
                await SendGlobalPlotData("vcl");
                await ProcessPHIPlot();
                await SendGlobalPlotData("phi");
                await Task.WhenAll(ProcessPickettPlot(), ProcessSWPlot());
                await Task.WhenAll(SendGlobalPlotData("pickett"), SendGlobalPlotData("sw"));
                await ProcessNetPayPlot("cutoff");
                await SendGlobalPlotData("cutoff");
                await ProcessNetPayPlot("interpretation");
            }
            else if (type_ == "vcl")
            {
                await ProcessPHIPlot();
                await SendGlobalPlotData("phi");
                await Task.WhenAll(ProcessPickettPlot(), ProcessSWPlot());
                await Task.WhenAll(SendGlobalPlotData("pickett"), SendGlobalPlotData("sw"));
                await ProcessNetPayPlot("cutoff");
                await SendGlobalPlotData("cutoff");
                await ProcessNetPayPlot("interpretation");
            }
            else if (type_ == "phi")
            {
                await Task.WhenAll(ProcessPickettPlot(), ProcessSWPlot());
                await Task.WhenAll(SendGlobalPlotData("pickett"), SendGlobalPlotData("sw"));
                await ProcessNetPayPlot("cutoff");
                await SendGlobalPlotData("cutoff");
                await ProcessNetPayPlot("interpretation");
            }
            else if (type_ == "sw")
            {
                await ProcessNetPayPlot("cutoff");
                await SendGlobalPlotData("cutoff");
                await ProcessNetPayPlot("interpretation");
            }
        }

        public async Task ProcessPickettPlot()
        {
            try
            {
                var content = new MultipartFormDataContent();

                content.Add(new StringContent(plotOptions.PHI_Select.ToString()), "phi_select");

                var response = await Http.PostAsync("http://localhost:8000/process-pickett-plot/", content);

                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content.ReadFromJsonAsync<Dictionary<string, string>>();
                    if (result != null)
                    {
                        plotImage.ResultMessage = result["message"];
                        
                        // Pickett Plot Image using Python (deprecated)
                        // plotImage.Pickett_Plot = result["pickett_plot"];

                        plotData.Pickett_Plot = true;
                    }
                }
                else
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    plotImage.ResultMessage = $"Failed to process file. Status code: {response.StatusCode}\nError details: {errorContent}";
                }
            }
            catch (Exception ex)
            {
                plotImage.ResultMessage = $"An error occurred: {ex.Message}";
            }
        }

        public async Task ProcessSWPlot()
        {
            try
            {
                var content = new MultipartFormDataContent();

                if (resParams.Shale_Resistivity.HasValue)
                    content.Add(new StringContent(resParams.Shale_Resistivity.ToString()), "rsh");
                if (resParams.Mid_Perf_Depth.HasValue)
                    content.Add(new StringContent(resParams.Mid_Perf_Depth.ToString()), "mid_perf_md");

                content.Add(new StringContent(resParams.Water_Resistivity.ToString()), "rw");
                content.Add(new StringContent(resParams.A_Value.ToString()), "a");
                content.Add(new StringContent(resParams.M_Value.ToString()), "m");
                content.Add(new StringContent(resParams.N_Value.ToString()), "n");
                content.Add(new StringContent(resParams.Mid_Perf_Temp.ToString()), "mid_perf_bht");
                content.Add(new StringContent(resParams.Surface_Temp.ToString()), "surface_temp");
                
                content.Add(new StringContent(plotOptions.PHI_Select.ToString()), "phi_select");

                var response = await Http.PostAsync("http://localhost:8000/process-sw-plot/", content);

                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
                    if (result != null)
                    {
                        plotImage.ResultMessage = result["message"].ToString();

                        // VCL Plot Image using Python (deprecated)
                        // plotImage.SW_Plot = result["sw_plot"].ToString();

                        plotOptions.SWOptions = JsonConvert.DeserializeObject<List<DropdownValue>>(result["dropdown_sw"].ToString());

                        var dfLasDict = result["df_las"] as JsonElement?;

                        var dfLasDictValue = dfLasDict.Value;
                        plotData.df_las_global = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, List<object>>>(dfLasDictValue.ToString());

                        var ColumnDataDict = result["column_data"] as JsonElement?;

                        var ColumnDataDictValue = ColumnDataDict.Value;
                        plotData.ColumnData = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, Dictionary<string, object>>>(ColumnDataDictValue.ToString());

                        plotData.SW_Plot = true;
                    }
                }
                else
                {
                    plotImage.ResultMessage = $"Failed to process file. Status code: {response.StatusCode}";
                }
            }
            catch (Exception ex)
            {
                plotImage.ResultMessage = $"An error occurred: {ex.Message}";
            }
        }

        public async Task ProcessNetPayPlot(string type_ = "cutoff")
        {
            try
            {
                var content = new MultipartFormDataContent();

                content.Add(new StringContent(resParams.SW_Cutoff.ToString()), "sw_cutoff");
                content.Add(new StringContent(resParams.VCL_Cutoff.ToString()), "vcl_cutoff");
                content.Add(new StringContent(resParams.PHI_Cutoff.ToString()), "phi_cutoff");
                content.Add(new StringContent(plotOptions.SW_Select.ToString()), "sw_select");

                if (type_ == "cutoff")
                {
                    var response = await Http.PostAsync("http://localhost:8000/process-cutoff-plot/", content);

                    if (response.IsSuccessStatusCode)
                    {
                        var result = await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
                        if (result != null)
                        {
                            plotImage.ResultMessage = result["message"].ToString();
                            plotImage.Cutoff_Plot = result["cutoff_plot"].ToString();

                            var dfLasDict = result["df_las"] as JsonElement?;

                            var dfLasDictValue = dfLasDict.Value;
                            plotData.df_las_global = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, List<object>>>(dfLasDictValue.ToString());

                            var ColumnDataDict = result["column_data"] as JsonElement?;

                            var ColumnDataDictValue = ColumnDataDict.Value;
                            plotData.ColumnData = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, Dictionary<string, object>>>(ColumnDataDictValue.ToString());

                            plotData.Cutoff_Plot = true;
                        }
                    }
                    else
                    {
                        plotImage.ResultMessage = $"Failed to process file. Status code: {response.StatusCode}";
                    }
                }

                else if (type_ == "interpretation")
                {
                    var response = await Http.PostAsync("http://localhost:8000/process-interpretation-plot/", content);

                    if (response.IsSuccessStatusCode)
                    {
                        var result = await response.Content.ReadFromJsonAsync<Dictionary<string, string>>();
                        if (result != null)
                        {
                            plotImage.ResultMessage = result["message"];
                            plotImage.Interpretation_Plot = result["interpretation_plot"];
                        }
                    }
                    else
                    {
                        plotImage.ResultMessage = $"Failed to process file. Status code: {response.StatusCode}";
                    }
                }
            }
            catch (Exception ex)
            {
                plotImage.ResultMessage = $"An error occurred: {ex.Message}";
            }
        }
    }
}