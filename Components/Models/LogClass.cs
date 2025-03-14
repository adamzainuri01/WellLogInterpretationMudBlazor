using System.ComponentModel;
using System.Runtime.CompilerServices;
using ScottPlot;
using ScottPlot.Blazor;

namespace Well_Log_Mudblazor.Models.LogClass
{
    public class PlotData : INotifyPropertyChanged
    {
        public Dictionary<string, List<object>>? df_las_global { get; set; }
        public Dictionary<string, Dictionary<string, object>>? ColumnData { get; set; }
        private bool _comboPlot = false;
        private bool _vclPlot = false;
        private bool _phiPlot = false;
        private bool _pickettPlot = false;
        private bool _swPlot = false;
        private bool _cutoffPlot = false;
        public bool Combo_Plot
        {
            get => _comboPlot;
            set { _comboPlot = value; OnPropertyChanged(); }
        }
        public bool VCL_Plot
        {
            get => _vclPlot;
            set { _vclPlot = value; OnPropertyChanged(); }
        }
        public bool PHI_Plot
        {
            get => _phiPlot;
            set { _phiPlot = value; OnPropertyChanged(); }
        }
        public bool Pickett_Plot
        {
            get => _pickettPlot;
            set { _pickettPlot = value; OnPropertyChanged(); }
        }
        public bool SW_Plot
        {
            get => _swPlot;
            set { _swPlot = value; OnPropertyChanged(); }
        }
        public bool Cutoff_Plot
        {
            get => _cutoffPlot;
            set { _cutoffPlot = value; OnPropertyChanged(); }
        }
        public event PropertyChangedEventHandler? PropertyChanged;
        protected void OnPropertyChanged([CallerMemberName] string? propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
    public class LogValues
    {
        public float? GR_Clean { get; set; }
        public float? GR_Clay { get; set; }
        public float? SP_Clean { get; set; }
        public float? SP_Clay { get; set; }
        public float? RT_Clean { get; set; }
        public float? RT_Clay { get; set; }
        public float? NPHI_Clean1 { get; set; }
        public float? NPHI_Clean2 { get; set; }
        public float? NPHI_Clay { get; set; }
        public float? RHOB_Clean1 { get; set; }
        public float? RHOB_Clean2 { get; set; }
        public float? RHOB_Clay { get; set; }
        public float? DT_Matrix { get; set; }
        public float? DT_Fluid { get; set; }
        public float? DT_Shale { get; set; }
    }

    public class ResParams
    {
        public float? Mid_Perf_Depth { get; set; }
        public float? Shale_Resistivity { get; set; } 
        public float? Cp { get; set; } = 1;
        public float? Alpha { get; set; } = 0.67f;
        public float? VCL_Limit { get; set; } = 0.5f;
        public float? Water_Resistivity { get; set; } = 0.08f;
        public float? A_Value { get; set; } = 1;
        public float? M_Value { get; set; } = 2;
        public float? N_Value { get; set; } = 2;
        public float? Mid_Perf_Temp { get; set; } = 210;
        public float? Surface_Temp { get; set; } = 60;
        public float? VCL_Cutoff { get; set; } = 0.2f;
        public float? PHI_Cutoff { get; set; } = 0.2f;
        public float? SW_Cutoff { get; set; } = 0.8f;
    }

    public class PlotImage : INotifyPropertyChanged
    {
        private string? _comboPlot;
        private string? _vclPlot;
        private string? _phiPlot;
        private string? _pickettPlot;
        private string? _swPlot;
        private string? _cutoffPlot;
        private string? _interpretationPlot;
        private string? _resultMessage;

        public string? Combo_Plot
        {
            get => _comboPlot;
            set { _comboPlot = value; OnPropertyChanged(); }
        }

        public string? VCL_Plot
        {
            get => _vclPlot;
            set { _vclPlot = value; OnPropertyChanged(); }
        }

        public string? PHI_Plot
        {
            get => _phiPlot;
            set { _phiPlot = value; OnPropertyChanged(); }
        }

        public string? Pickett_Plot
        {
            get => _pickettPlot;
            set { _pickettPlot = value; OnPropertyChanged(); }
        }

        public string? SW_Plot
        {
            get => _swPlot;
            set { _swPlot = value; OnPropertyChanged(); }
        }

        public string? Cutoff_Plot
        {
            get => _cutoffPlot;
            set { _cutoffPlot = value; OnPropertyChanged(); }
        }

        public string? Interpretation_Plot
        {
            get => _interpretationPlot;
            set { _interpretationPlot = value; OnPropertyChanged(); }
        }

        public string? ResultMessage
        {
            get => _resultMessage;
            set { _resultMessage = value; OnPropertyChanged(); }
        }

        public event PropertyChangedEventHandler? PropertyChanged;

        protected void OnPropertyChanged([CallerMemberName] string? propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }

    public class DropdownValue
        {
            public string Value { get; set; }
            public string Text { get; set; }
        }

    public class PlotOptions
    {
        public int? FigureHeight { get; set; } = 30;
        public string? GR_Correction { get; set; } = "young";
        public string? VCL_Select { get; set; } = "gr";
        public string? PHI_Select { get; set; } = "neutron_density";
        public string? SW_Select { get; set; } = "archie";
        public string? Z_Axis { get; set; } = "VCL";
        public  List<DropdownValue> VCLOptions { get; set; } = new();
        public  List<DropdownValue> PHIOptions { get; set; } = new();
        public  List<DropdownValue> SWOptions { get; set; } = new();
    }
}