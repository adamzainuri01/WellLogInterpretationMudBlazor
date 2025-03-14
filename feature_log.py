import lasio
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.signal import savgol_filter
import matplotlib.gridspec as gridspec
from statistics import mean
import numpy as np
import math

def read_lasio(file_path):
    las = lasio.read(file_path)
    df_las = las.df().reset_index()
    df_las["WELL"] = las.well.WELL.value
    df_las.insert(0, "WELL", df_las.pop("WELL"))

    df_las, reverse_mapping = rename_columns(df_las)

    curve_data = dict()

    for _, curve in enumerate(las.curves):
        standardized_mnemonic = reverse_mapping.get(curve.mnemonic, curve.mnemonic)

        curve_data[standardized_mnemonic] = curve.unit

    return df_las, curve_data


def rename_columns(df):
    value_mapping = {
        "RDEEP": [
            "ILD",
            "LLD",
            "IDPH",
            "HLLD",
            "AO90",
            "AT90",
            "AF90",
            "SEXP",
            "SESP",
            "SEMP",
            "P40H",
            "A40H",
            "ES_LN_64",
        ],
        "RSHAL": ["LLS", "AO10", "AT10", "AF10", "P10H", "A10H"],
        "RMED": ["ILM", "IMPH", "SFLU", "ES_SN_16"],
        "MD": ["DEPT", "DEPTH"],
        "RMICRO": ["MSFL", "ML", "MLL", "PL"],
        "DTS": ["DTS", "DTSH", "DT4S", "DTRS", "DTSR", "DTSP"],
        "DTC": [
            "DT",
            "DTP",
            "DTC",
            "DT4P",
            "DTCO",
            "DTL",
            "DTLF",
            "DTLN",
            "DTRP",
            "DTCR",
            "DTCP",
        ],
        "NPHI": [
            "NPHI",
            "TNPH",
            "NPOR",
            "TNPU",
            "TNPB",
            "TNPL",
            "TNPR",
            "APLS",
            "CNTC",
            "CFTC",
        ],
        "PEF": [
            "PEF",
            "PEFZ",
            "PEF8",
            "PEFI",
            "PEB",
            "PEBU",
            "PEBL",
            "PEBR",
            "PE",
            "SPE",
        ],
        "GR": ["GR", "SGR", "ECGR", "HGR", "EHGR", "GR_ARC", "GR_CDR", "GR_ADN", "EGR"],
        "RHOB": [
            "RHOB",
            "RHOZ",
            "RHO8",
            "RHOI",
            "ROBB",
            "ROBU",
            "ROBL",
            "IDRO",
            "IDDR",
            "SBD2",
        ],
        "DRHO": ["DRHO", "HDRA", "HDRB", "HPRA", "DNPH", "SCO2"],
    }

    reverse_mapping = {
        variant: key for key, variants in value_mapping.items() for variant in variants
    }

    df.rename(columns=reverse_mapping, inplace=True)

    return df, reverse_mapping


def boxplot(data, curve_data):
    columns_to_plot = list(curve_data.keys())
    column_units = list(curve_data.values())

    # Get unique wells and assign colors
    wells = data["WELL"].unique()
    colors = sns.color_palette("viridis", n_colors=len(wells))

    # Calculate the number of rows and columns for subplots
    n_plots = len(columns_to_plot)
    n_cols = 3
    n_rows = (n_plots - 1) // n_cols + 1

    # Set the figure size for the overall plot
    plt.figure(figsize=(5 * n_cols, 4 * n_rows))

    # Create subplots for each selected column
    for i, column in enumerate(columns_to_plot, 1):
        plt.subplot(n_rows, n_cols, i)

        # Plot boxplots for each well with different colors
        sns.boxplot(x="WELL", y=column, data=data, palette=dict(zip(wells, colors)))

        plt.title(f"Boxplot for {column}", fontsize=10)
        plt.xlabel("Well", fontsize=8)
        plt.ylabel(f"{column} [{column_units[i-1]}]", fontsize=8)
        plt.xticks(rotation=45, ha="right")

    # Add an overall title for the set of subplots
    plt.suptitle("DATA DISTRIBUTION (BOX PLOT)", fontsize=16, fontweight="bold")

    # Adjust the layout and display the plot
    plt.tight_layout()
    plt.show()


def histplot(data, curve_data):
    columns_to_plot = list(curve_data.keys())
    column_units = list(curve_data.values())

    # Get unique wells and assign colors
    wells = data["WELL"].unique()
    colors = sns.color_palette("viridis", n_colors=len(wells))

    # Calculate the number of rows and columns for subplots
    n_plots = len(columns_to_plot)
    n_cols = 3
    n_rows = (n_plots - 1) // n_cols + 1

    # Create subplots for histograms
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
    fig.suptitle("DATA DISTRIBUTION (HISTOGRAM PLOT)", fontsize=16, fontweight="bold")
    fig.subplots_adjust(top=0.95, wspace=0.3, hspace=0.4)

    for i, (column_name, ax) in enumerate(zip(columns_to_plot, axes.flatten())):
        column_unit = column_units[i]
        ax.set_title(column_name, fontsize=10)

        # Plot histograms for each well with different colors
        for well, color in zip(wells, colors):
            well_data = data[data["WELL"] == well]
            sns.histplot(
                well_data[column_name].dropna(),
                bins=30,
                color=color,
                ax=ax,
                kde=True,
                label=well,
                alpha=0.5,
            )

        ax.set_xlabel(f"{column_name} [{column_unit}]", fontsize=8)
        ax.set_ylabel("Frequency", fontsize=8)
        ax.tick_params(axis="both", which="major", labelsize=6)
        ax.legend(title="WELL", fontsize=6, title_fontsize=8)

    # Remove empty subplots if there are more plots than columns
    for i in range(len(columns_to_plot), n_rows * n_cols):
        fig.delaxes(axes.flatten()[i])

    # Adjust the layout and display the plot
    plt.tight_layout()
    plt.show()


def densityplot(data, curve_data):
    columns_to_plot = list(curve_data.keys())
    column_units = list(curve_data.values())

    # Get unique wells and assign colors
    wells = data["WELL"].unique()
    colors = sns.color_palette("viridis", n_colors=len(wells))

    # Calculate the number of rows and columns for subplots
    n_plots = len(columns_to_plot)
    n_cols = 3
    n_rows = (n_plots - 1) // n_cols + 1

    # Create subplots for density plots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
    fig.suptitle("DATA DISTRIBUTION (DENSITY PLOT)", fontsize=16, fontweight="bold")
    fig.subplots_adjust(top=0.95, wspace=0.3, hspace=0.4)

    for i, (column_name, ax) in enumerate(zip(columns_to_plot, axes.flatten())):
        column_unit = column_units[i]
        ax.set_title(column_name, fontsize=10)

        # Plot density plots for each well with different colors
        for well, color in zip(wells, colors):
            well_data = data[data["WELL"] == well]
            sns.kdeplot(
                well_data[column_name].dropna(),
                ax=ax,
                color=color,
                label=well,
                alpha=0.7,
            )

        ax.set_xlabel(f"{column_name} [{column_unit}]", fontsize=8)
        ax.set_ylabel("Density", fontsize=8)
        ax.tick_params(axis="both", which="major", labelsize=6)
        ax.legend(title="WELL", fontsize=6, title_fontsize=8)

    # Remove empty subplots if there are more plots than columns
    for i in range(len(columns_to_plot), n_rows * n_cols):
        fig.delaxes(axes.flatten()[i])

    # Adjust the layout and display the plot
    plt.tight_layout()
    plt.show()


def combo_plot(
    data,
    top_depth=None,
    bottom_depth=None,
    figure_height=30,
    smoothing_traject1=False,
    smoothing_traject2=False,
    smoothing_traject3=False,
    column_data=None,  # Dictionary with column min and max values
):
    if top_depth == None or bottom_depth == None:
        top_depth = data.MD.min()
        bottom_depth = data.MD.max()

    logs = data[(data.MD >= top_depth) & (data.MD <= bottom_depth)]
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(12, figure_height), sharey=True)

    fig.subplots_adjust(wspace=0.1)

    # General setting for all axes
    for axes in ax:
        axes.set_ylim(top_depth, bottom_depth)
        axes.invert_yaxis()
        axes.yaxis.grid(True)
        axes.yaxis.grid(True, which="minor", linestyle=":")
        axes.yaxis.grid(True, which="major", linestyle="-", linewidth="1")
        axes.yaxis.set_major_locator(ticker.MultipleLocator(100))
        axes.yaxis.set_minor_locator(ticker.MultipleLocator(20))
        axes.get_xaxis().set_visible(False)

    # Apply smoothing if required
    if smoothing_traject1:
        for col in ["GR", "CALI", "SP"]:
            if col in logs.columns:
                logs[col].dropna(inplace=True)
                logs[col] = savgol_filter(logs[col], window_length=5, polyorder=3)
    if smoothing_traject2:
        for col in ["RDEEP", "RMED", "RSHAL"]:
            if col in logs.columns:
                logs[col].dropna(inplace=True)
                logs[col] = savgol_filter(logs[col], window_length=5, polyorder=3)
    if smoothing_traject3:
        for col in ["RHOB", "NPHI", "DTC"]:
            if col in logs.columns:
                logs[col].dropna(inplace=True)
                logs[col] = savgol_filter(logs[col], window_length=5, polyorder=3)

    # Plot each trajectory
    # First trajectory: GR, CALI, SP
    for col, color, pos, subplot_idx in [
        ("GR", "green", 80, 0),
        ("CALI", "black", 40, 0),
        ("SP", "blue", 0, 0),
    ]:
        # Check if the column exists in logs and has data in column_data
        if col in logs.columns and col in column_data:
            # Extract unit and limits from the combined dictionary
            unit = column_data[col]["unit"]
            limits = column_data[col]["limits"]

            # Dynamically create the label
            label = f"{col} [{unit}]"

            # Create a twiny axis and set its properties
            ax_temp = ax[subplot_idx].twiny()
            ax_temp.set_xlim(*limits)  # Use limits from column_data
            ax_temp.spines["top"].set_position(("outward", pos))
            ax_temp.set_xlabel(label, color=color)
            ax_temp.tick_params(axis="x", colors=color)

            # Plot the data
            ax_temp.plot(logs[col], logs.MD, label=label, color=color)

    # Second trajectory: DR, MR, SR
    for col, color, pos, subplot_idx in [
        ("RDEEP", "red", 80, 1),
        ("RMED", "purple", 40, 1),
        ("RSHAL", "black", 0, 1),
    ]:
        if col in logs.columns and column_data.get(col):
            unit = column_data[col]["unit"]
            limits = column_data[col]["limits"]

            label = f"{col} [{unit}]"

            ax_temp = ax[subplot_idx].twiny()
            ax_temp.set_xlim(*limits)
            ax_temp.set_xscale("log")
            ax_temp.spines["top"].set_position(("outward", pos))
            ax_temp.set_xlabel(label, color=color)
            ax_temp.tick_params(axis="x", colors=color)

            ax_temp.plot(logs[col], logs.MD, label=label, color=color)

    # Third trajectory: RHOB, NPHI, DT
    for col, color, pos, subplot_idx in [
        ("RHOB", "red", 80, 2),
        ("NPHI", "green", 40, 2),
        ("DTC", "blue", 0, 2),
    ]:
        if col in logs.columns and column_data.get(col):
            unit = column_data[col]["unit"]
            limits = column_data[col]["limits"]

            label = f"{col} [{unit}]"

            ax_temp = ax[subplot_idx].twiny()
            ax_temp.set_xlim(*limits)

            if col == "NPHI":
                ax_temp.invert_xaxis()

            ax_temp.spines["top"].set_position(("outward", pos))
            ax_temp.set_xlabel(label, color=color)
            ax_temp.tick_params(axis="x", colors=color)

            ax_temp.plot(logs[col], logs.MD, label=label, color=color)
            
    
    plt.tight_layout()
    
    return fig
    #plt.show()
    

def custom_formatter(x, pos):
        # Check if the number is an integer (i.e., decimal part is .00)
        if x.is_integer():
            return f'{int(x)}'  # Return as integer without decimals
        else:
            return f'{x:.2f}'  # Otherwise, display with 2 decimal places
        


def custom_interpretation_plot(
    df, column_data, selected_columns, depth_start=None, depth_end=None
):
    column_data_temp = {
        key: value for key, value in column_data.items() if key in selected_columns
    }

    if depth_start is None or depth_end is None:
        depth_start = df.MD.min()
        depth_end = df.MD.max()

    num_tracks = len(column_data_temp)
    fig, ax = plt.subplots(nrows=1, ncols=num_tracks, figsize=(15, 20), sharey=True)

    if num_tracks == 1:
        ax = [ax]

    columns_to_plot = list(column_data_temp.keys())
    column_units = [column_data_temp[key]["unit"] for key in columns_to_plot]
    column_limits = [column_data_temp[key]["limits"] for key in columns_to_plot]

    # General setting for all axes
    for axes in ax:
        axes.set_ylim(depth_start, depth_end)
        axes.invert_yaxis()
        axes.yaxis.grid(True, which="minor", linestyle=":")
        axes.yaxis.grid(True, which="major", linestyle="-", linewidth="1")
        axes.yaxis.set_major_locator(
            ticker.MultipleLocator(100)
        )  # Adjust the major tick interval
        axes.yaxis.set_minor_locator(
            ticker.MultipleLocator(20)
        )  # Adjust the minor tick interval (optional)
        
        axes.get_xaxis().set_visible(False)

    # Customizing each track with unit and color
    for i, (log_name, units, limits) in enumerate(
        zip(columns_to_plot, column_units, column_limits)
    ):
        current_ax = ax[i].twiny()
        current_ax.plot(
            df[log_name], df.MD, label=f"{log_name} [{units}]", color="C" + str(i)
        )

        # Set limits for each plot if limits are available
        if limits:
            current_ax.set_xlim(limits)
            
            current_ax.xaxis.set_major_locator(ticker.FixedLocator([limits[0], (limits[0] + limits[1]) / 2, limits[1]]))  # Set ticks at exact limits
            current_ax.xaxis.set_major_formatter(ticker.FuncFormatter(custom_formatter))  # Display with 2 decimal places

        if log_name == "RDEEP" or log_name == "RMED" or log_name == "RSHAL":
            current_ax.set_xscale("log")

        current_ax.set_xlabel(f"{log_name} [{units}]", color="C" + str(i))
        current_ax.tick_params(axis="x", colors="C" + str(i))
        current_ax.spines["top"].set_position(("outward", 0))
        current_ax.legend(
            loc="lower right", facecolor="white", framealpha=1, fontsize=7
        )
    
    plt.tight_layout()
    return fig
    # plt.show()


def vclgr(df, row, gr_clean=None, gr_clay=None, correction=None):
    # Get the 'GR' value for the current row
    gr_value = row["GR"]

    # Use default values if None are provided
    if gr_clean is None or gr_clay is None:
        gr_clean = df["GR"].min()
        gr_clay = df["GR"].max()

    # Calculate the initial ratio
    igr = (gr_value - gr_clean) / (gr_clay - gr_clean)

    # Apply the different correction methods
    vclgr_larionov_young = 0.083 * (2 ** (3.7 * igr) - 1)
    vclgr_larionov_old = 0.33 * (2 ** (2 * igr) - 1)
    vclgr_clavier = 1.7 - (3.38 - (igr + 0.7) ** 2) ** 0.5
    vclgr_steiber = 0.5 * igr / (1.5 - igr)

    if correction == "young":
        vclgr_result = vclgr_larionov_young
    elif correction == "older":
        vclgr_result = vclgr_larionov_old
    elif correction == "clavier":
        vclgr_result = vclgr_clavier
    elif correction == "steiber":
        vclgr_result = vclgr_steiber
    else:
        vclgr_result = igr

    return vclgr_result


def vclsp(df, row, sp_clean=None, sp_clay=None):
    sp_value = row["SP"]

    if sp_clean is None or sp_clay is None:
        if df["GR"].corr(df["SP"]) > 0:
            sp_clean, sp_clay = df.SP.min(), df.SP.max()
        else:
            sp_clean, sp_clay = df.SP.max(), df.SP.min()

    vclsp = (sp_value - sp_clean) / (sp_clay - sp_clean)

    return vclsp


def vclrt(df, row, rt_clean=None, rt_clay=None):
    if "RT" in df.columns:
        rt_value = row["RT"]
    elif "RDEEP" in df.columns:
        rt_value = row["RDEEP"]

    if rt_clean is None or rt_clay is None:
        if "RT" in df.columns:
            rt_clean, rt_clay = df.RT.min(), df.RT.max()
        elif "RDEEP" in df.columns:
            rt_clean, rt_clay = df.RDEEP.min(), df.RDEEP.max()

    vrt = (rt_clay / rt_value) * (rt_clean - rt_value) / (rt_clean - rt_clay)
    if rt_value > 2 * rt_clay:
        vclrt = 0.5 * (2 * vrt) ** (0.67 * (vrt + 1))
    else:
        vclrt = vrt

    return vclrt


def vclnd(
    df,
    row,
    neut_clean1=None,
    den_clean1=None,
    neut_clean2=None,
    den_clean2=None,
    neut_clay=None,
    den_clay=None,
):
    neut_value = row["NPHI"]
    den_value = row["RHOB"]

    if neut_clean1 is None:
        neut_clean1 = df.NPHI.min()
    if den_clean1 is None:
        den_clean1 = df.RHOB.max()
    if neut_clean2 is None:
        neut_clean2 = df.NPHI.max()
    if den_clean2 is None:
        den_clean2 = df.RHOB.min()
    if neut_clay is None:
        neut_clay = df.NPHI.max()
    if den_clay is None:
        den_clay = df.RHOB.max()

    term1 = (den_clean2 - den_clean1) * (neut_value - neut_clean1) - (
        den_value - den_clean1
    ) * (neut_clean2 - neut_clean1)
    term2 = (den_clean2 - den_clean1) * (neut_clay - neut_clean1) - (
        den_clay - den_clean1
    ) * (neut_clean2 - neut_clean1)
    vclnd = term1 / term2
    return vclnd


def calc_vcl(
    df,
    gr_clean=None,
    gr_clay=None,
    sp_clean=None,
    sp_clay=None,
    rt_clean=None,
    rt_clay=None,
    neut_clean1=None,
    den_clean1=None,
    neut_clean2=None,
    den_clean2=None,
    neut_clay=None,
    den_clay=None,
    correction_gr="young",
):
    if "GR" in df.columns:
        df["VCLGR"] = df.apply(
            lambda row: vclgr(
                df, row, gr_clean=gr_clean, gr_clay=gr_clay, correction=correction_gr
            ),
            axis=1,
        )

        if "SP" in df.columns:
            df["VCLSP"] = df.apply(
                lambda row: vclsp(df, row, sp_clean=sp_clean, sp_clay=sp_clay), axis=1
            )

    if ("RT" in df.columns) or ("RDEEP" in df.columns):
        df["VCLRT"] = df.apply(
            lambda row: vclrt(df, row, rt_clean=rt_clean, rt_clay=rt_clay), axis=1
        )

    if ("NPHI" in df.columns) and ("RHOB" in df.columns):
        df["VCLND"] = df.apply(
            lambda row: vclnd(
                df,
                row,
                neut_clean1=neut_clean1,
                den_clean1=den_clean1,
                neut_clean2=neut_clean2,
                den_clean2=den_clean2,
                neut_clay=neut_clay,
                den_clay=den_clay,
            ),
            axis=1,
        )

    return df


def select_vcl(df, select_vcl="gr"):
    if select_vcl == "gr":
        try:
            df["VCL"] = df["VCLGR"]
        except KeyError:
            print("No VCLGR column found. Please check the column names.")

            return df
    elif select_vcl == "sp":
        try:
            df["VCL"] = df["VCLSP"]
        except KeyError:
            print("No VCLSP column found. Please check the column names.")

            return df
    elif select_vcl == "rt":
        try:
            df["VCL"] = df["VCLRT"]
        except KeyError:
            print("No VCLRT column found. Please check the column names.")

            return df
    elif select_vcl == "nd":
        try:
            df["VCL"] = df["VCLND"]
        except KeyError:
            print("No VCLND column found. Please check the column names.")

            return df

    # df = df.drop(
    #     [i for i in df.columns if "vcl" in i.lower() and i.lower() != "vcl"], axis=1
    # )

    return df


def vcl_plot(
    df,
    data,
    neut_clean1=None,
    den_clean1=None,
    neut_clean2=None,
    den_clean2=None,
    neut_clay=None,
    den_clay=None,
    depth_start=None,
    depth_end=None,
):

    if depth_start is None or depth_end is None:
        depth_start = df.MD.min()
        depth_end = df.MD.max()
    if neut_clean1 is None:
        neut_clean1 = df.NPHI.min()
    if den_clean1 is None:
        den_clean1 = df.RHOB.max()
    if neut_clean2 is None:
        neut_clean2 = df.NPHI.max()
    if den_clean2 is None:
        den_clean2 = df.RHOB.min()
    if neut_clay is None:
        neut_clay = df.NPHI.max()
    if den_clay is None:
        den_clay = df.RHOB.max()

    # Create a figure and subplots with a refined layout

    fig = plt.figure(figsize=(14, 12))

    # fig.suptitle("Volume of Clay from Different Methods", fontsize=16, weight="bold")
    fig.subplots_adjust(top=0.95, wspace=0.4, hspace=0.4)

    gs = gridspec.GridSpec(4, 3)
    ax1 = fig.add_subplot(gs[:, 0])  # All rows, column 1
    ax2 = fig.add_subplot(gs[0, 1])  # Row 1, column 2
    ax3 = fig.add_subplot(gs[1, 1])  # Row 2, column 2
    ax4 = fig.add_subplot(gs[2, 1])  # Row 3, column 2
    ax5 = fig.add_subplot(gs[3, 1])  # Row 4, column 2
    ax6 = fig.add_subplot(gs[:, 2], sharey=ax1)  # All rows, column 3

    # Graph for GR and SP

    ax1.invert_yaxis()
    ax1.grid(True, linestyle="--", alpha=0.7)

    ax1.set_ylabel(
        f'MD ({data["MD"]["unit"]})', fontsize=12
    )  # Use unit from dictionary

    ax1.plot(df.GR, df.MD, color="green", lw=2, label=f"GR [{data['GR']['unit']}]")
    ax1.set_xlabel(f'GR [{data["GR"]["unit"]}]', fontsize=12)

    ax11 = ax1.twiny()

    ax11.plot(df.SP, df.MD, color="blue", lw=2, label=f"SP [{data['SP']['unit']}]")
    ax11.set_xlabel(f'SP [{data["SP"]["unit"]}]', fontsize=12, color="blue")

    # Histograms for GR, SP, and DR

    ax2.hist(df.GR.dropna(), bins=20, color="green", edgecolor="black")
    ax2.set_xlabel(f'GR [{data["GR"]["unit"]}]', fontsize=12)
    ax2.set_ylabel("Frequency", fontsize=12)
    ax3.hist(df.SP.dropna(), bins=20, color="blue", edgecolor="black")
    ax3.set_xlabel(f'SP [{data["SP"]["unit"]}]', fontsize=12)
    ax3.set_ylabel("Frequency", fontsize=12)

    ax4.hist(df.RDEEP.dropna(), bins=20, color="gray", edgecolor="black")
    ax4.set_xlabel(f'RDEEP [{data["RDEEP"]["unit"]}]', fontsize=12)
    ax4.set_ylabel("Frequency", fontsize=12)

    # N-D XPlot for Volume of Clay

    points = ax5.scatter(df.NPHI, df.RHOB, c=df.GR, s=5, cmap="viridis", alpha=0.7)
    cbar = plt.colorbar(points, ax=ax5)
    cbar.set_label(f'GR [{data["GR"]["unit"]}]', rotation=90, fontsize=10)

    ax5.set_xlabel(f'NPHI [{data["NPHI"]["unit"]}]', fontsize=12)
    ax5.set_ylabel(f'RHOB [{data["RHOB"]["unit"]}]', fontsize=12)
    ax5.invert_yaxis()
    ax5.grid(True, linestyle="--", alpha=0.7)

    ax5.plot(
        [neut_clean1, neut_clean2],
        [den_clean1, den_clean2],
        marker="o",
        color="black",
        linewidth=1.5,
    )

    ax5.plot(neut_clay, den_clay, "ro", color="red", linewidth=2)

    # Add text annotations for Clean Points and Clay Point

    ax5.text(
        neut_clean1,
        den_clean1,
        "Clean Point 1",
        fontsize=10,
        color="black",
        ha="center",
        va="center",
        bbox=dict(boxstyle="round", fc="white", ec="0.5", alpha=0.8),
    )
    ax5.text(
        neut_clean2 - 0.02,
        den_clean2 + 0.05,
        "Clean Point 2",
        fontsize=10,
        color="black",
        ha="center",
        va="center",
        bbox=dict(boxstyle="round", fc="white", ec="0.5", alpha=0.8),
    )
    ax5.text(
        neut_clay,
        den_clay,
        "Clay Point",
        fontsize=10,
        color="black",
        ha="center",
        va="center",
        bbox=dict(boxstyle="round", fc="white", ec="0.5", alpha=0.8),
    )
    ax5.plot(
        [neut_clean1, neut_clay], [den_clean1, den_clay], color="black", linewidth=1.5
    )

    ax6.plot(df.VCLGR, df.MD, label="VCLGR", color="green", lw=2)
    ax6.plot(df.VCLND, df.MD, label="VCLND", color="red", lw=2)
    ax6.plot(df.VCLSP, df.MD, label="VCLSP", color="blue", lw=2)
    ax6.legend(loc="upper right", fontsize=10)
    ax6.set_xlim(0, 1)
    ax6.set_ylim(depth_start, depth_end)
    ax6.invert_yaxis()
    ax6.grid(True, linestyle="--", alpha=0.7)
    ax6.set_xlabel("VCL [V/V]", fontsize=12)
    
    plt.tight_layout()

    return fig
    #plt.show()


def phis_shale(df, dt_sh=None, dt_ma=None, dt_fl=None):
    if dt_sh is None:
        dt_sh = df.DTC.min()
    if dt_ma is None:
        dt_ma = df.DTC.min()
    if dt_fl is None:
        dt_fl = df.DTC.max()

    phis_shale = (dt_sh - dt_ma) / (dt_fl - dt_ma)

    return phis_shale


def phid_shale(df, den_sh=None, den_ma=None, den_fl=None):
    if den_sh is None:
        den_sh = df.RHOB.max()
    if den_ma is None:
        den_ma = df.RHOB.max()
    if den_fl is None:
        den_fl = df.RHOB.min()

    phid_shale = (den_sh - den_ma) / (den_fl - den_ma)
    return phid_shale


def phis_w(df, row, dt_ma=None, dt_fl=None, cp=1):
    dt_value = row["DTC"]

    if dt_ma is None:
        dt_ma = df.DTC.min()
    if dt_fl is None:
        dt_fl = df.DTC.max()

    phis_w = (1 / cp) * (dt_value - dt_ma) / (dt_fl - dt_ma)
    return phis_w


def phis_w_sh_corr(df, row, dt_sh=None, dt_ma=None, dt_fl=None, cp=1):
    vcl_value = row["VCL"]

    if dt_sh is None:
        dt_sh = df.DTC.min()
    if dt_ma is None:
        dt_ma = df.DTC.min()
    if dt_fl is None:
        dt_fl = df.DTC.max()

    phis_w_sh_corr = phis_w(df, row, dt_ma=dt_ma, dt_fl=dt_fl) - vcl_value * phis_shale(
        df, dt_sh=dt_sh, dt_ma=dt_ma, dt_fl=dt_fl
    )
    return phis_w_sh_corr


# Raymer-Hunt-Gardner (the alpha(5/8) ranges from 0.625-0.70, 0.67-most, 0.60-gas reservoirs)
def phis_rhg(df, row, dt_ma=None, alpha=0.67):
    dt_value = row["DTC"]

    if dt_ma is None:
        dt_ma = df.DTC.min()

    phis_rhg = (alpha) * (dt_value - dt_ma) / (dt_value)
    return phis_rhg


def phis_rhg_sh_corr(df, row, dt_ma=None, dt_sh=None, dt_fl=None, alpha=0.67):
    vcl_value = row["VCL"]

    if dt_sh is None:
        dt_sh = df.DTC.min()
    if dt_ma is None:
        dt_ma = df.DTC.min()
    if dt_fl is None:
        dt_fl = df.DTC.max()

    phis_rhg_sh_corr = phis_rhg(
        df, row, dt_ma=dt_ma, alpha=alpha
    ) - vcl_value * phis_shale(df, dt_sh=dt_sh, dt_ma=dt_ma, dt_fl=dt_fl)
    return phis_rhg_sh_corr


# Density
def phid(df, row, den_ma=None, den_fl=None):
    den_value = row["RHOB"]

    if den_ma is None:
        den_ma = df.RHOB.max()
    if den_fl is None:
        den_fl = df.RHOB.min()

    phid = (den_value - den_ma) / (den_fl - den_ma)
    return phid


def phid_sh_corr(df, row, den_ma=None, den_fl=None, den_sh=None):
    vcl_value = row["VCL"]

    if den_sh is None:
        den_sh = df.RHOB.max()
    if den_ma is None:
        den_ma = df.RHOB.max()
    if den_fl is None:
        den_fl = df.RHOB.min()

    phid_sh_corr = phid(df, row, den_ma=den_ma, den_fl=den_fl) - vcl_value * phid_shale(
        df, den_sh=den_sh, den_ma=den_ma, den_fl=den_fl
    )
    return phid_sh_corr


# Neutron
def phin_sh_corr(df, row, neut_sh=None):
    neut_value = row["NPHI"]
    vcl_value = row["VCL"]

    if neut_sh is None:
        neut_sh = df.NPHI.max()

    phin_sh_corr = neut_value - vcl_value * neut_sh
    return phin_sh_corr


# Neutron-Density
def phixnd(phinshc, phidshc):
    phixnd = (phinshc + phidshc) / 2
    return phixnd


def phixnd_gas_corr(phin, phid):
    phixnd_gas_corr = ((phin**2 + phid**2) / 2) ** (
        0.5
    )  # for gas intervals (nphi<dphi = crossover)
    return phixnd_gas_corr


def calc_phi(
    df,
    dt_ma=None,
    dt_fl=None,
    dt_sh=None,
    den_ma=None,
    den_fl=None,
    den_sh=None,
    neut_sh=None,
    cp=1,
    alpha=0.67,
):
    if "DTC" in df.columns:
        df["PHISw"] = df.apply(
            lambda row: phis_w(df, row, dt_ma=dt_ma, dt_fl=dt_fl, cp=cp),
            axis=1,
        )
        df["PHISwshc"] = df.apply(
            lambda row: phis_w_sh_corr(
                df, row, dt_sh=dt_sh, dt_ma=dt_ma, dt_fl=dt_fl, cp=1
            ),
            axis=1,
        )

        df["PHISrhg"] = df.apply(
            lambda row: phis_rhg(df, row, dt_ma=dt_ma, alpha=alpha),
            axis=1,
        )
        df["PHISrhgshc"] = df.apply(
            lambda row: phis_rhg_sh_corr(
                df, row, dt_sh=dt_sh, dt_ma=dt_ma, dt_fl=dt_fl, alpha=alpha
            ),
            axis=1,
        )

    if "RHOB" in df.columns:
        df["PHID"] = df.apply(
            lambda row: phid(df, row, den_ma=den_ma, den_fl=den_fl),
            axis=1,
        )
        df["PHIDshc"] = df.apply(
            lambda row: phid_sh_corr(
                df, row, den_ma=den_ma, den_fl=den_fl, den_sh=den_sh
            ),
            axis=1,
        )

    if "NPHI" in df.columns:
        df["PHINshc"] = df.apply(
            lambda row: phin_sh_corr(df, row, neut_sh=neut_sh),
            axis=1,
        )
        if "RHOB" in df.columns:
            df["PHIxND"] = phixnd(df["PHINshc"], df["PHIDshc"])

    return df


def select_phi(df, select_phi="neutron_density"):
    if select_phi == "wyllie":
        try:
            df["PHIE"] = df["PHISw"]
        except KeyError:
            print("No PHISw column found. Please check the column names.")

            return df
    elif select_phi == "wyllie_sh_corr":
        try:
            df["PHIE"] = df["PHISwshc"]
        except KeyError:
            print("No PHISwshc column found. Please check the column names.")

            return df
    elif select_phi == "rhg":
        try:
            df["PHIE"] = df["PHISrhg"]
        except KeyError:
            print("No PHISrhg column found. Please check the column names.")

            return df
    elif select_phi == "rhg_sh_corr":
        try:
            df["PHIE"] = df["PHISrhgshc"]
        except KeyError:
            print("No PHISrhgshc column found. Please check the column names.")

            return df
    elif select_phi == "density":
        try:
            df["PHIE"] = df["PHID"]
        except KeyError:
            print("No PHID column found. Please check the column names.")

            return df
    elif select_phi == "density_sh_corr":
        try:
            df["PHIE"] = df["PHIDshc"]
        except KeyError:
            print("No PHIDshc column found. Please check the column names.")

            return df
    elif select_phi == "neutron_sh_corr":
        try:
            df["PHIE"] = df["PHINshc"]
        except KeyError:
            print("No PHINshc column found. Please check the column names.")

            return df
    elif select_phi == "neutron_density":
        try:
            df["PHIE"] = df["PHIxND"]
        except KeyError:
            print("No PHIxND column found. Please check the column names.")

            return df

    # df = df.drop(
    #     [
    #         i
    #         for i in df.columns
    #         if "phi" in i.lower() and i.lower() != "phie" and i != "NPHI"
    #     ],
    #     axis=1,
    # )

    return df


def sw_archie(df, row, rw=0.08, a=1, m=2, n=2):
    if "RT" in df.columns:
        rt_value = row["RT"]
    elif "RDEEP" in df.columns:
        rt_value = row["RDEEP"]

    phie_value = row["PHIE"]

    F = a / (phie_value**m)
    sw_archie = (F * rw / rt_value) ** (1 / n)
    return sw_archie


def sw_waxman(
    df, row, rw=0.08, a=1, m=2, n=2, mid_perf_md=None, mid_perf_bht=210, surface_temp=60
):
    phi_value = row["PHIE"]
    vcl_value = row["VCL"]

    if "RT" in df.columns:
        rt_value = row["RT"]
    elif "RDEEP" in df.columns:
        rt_value = row["RDEEP"]

    if mid_perf_md is None:
        mid_perf_md = mean(df.MD)

    temp_grad = (mid_perf_bht - surface_temp) / (mid_perf_md)

    qv_value = -47.619 * vcl_value**2.0 + 61.429 * vcl_value

    sw, swi = 0.0, 0.0
    bmax = max(51.31 * math.log(temp_grad + 460) - 317.2, 0)
    
    b = (1 - 0.83 / math.exp(0.5 / rw)) * bmax
    f = a / (phi_value**m)

    swi = (f * rw / rt_value) ** (1 / n)

    while abs(sw - swi) > 0.01:
        sw = (f / rt_value / (1 / rt_value + (b * qv_value / swi))) ** (1 / n)
        swi=sw
    
    return sw


def sw_indonesia(df, row, rw=0.08, a=1, m=2, n=2, rsh=None):
    phi_value = row["PHIE"]
    vcl_value = row["VCL"]

    if "RT" in df.columns:
        rt_value = row["RT"]

        if rsh is None:
            rsh = df.RT.min()
    elif "RDEEP" in df.columns:
        rt_value = row["RDEEP"]

        if rsh is None:
            rsh = df.RDEEP.min()

    sw_indonesia = (
        (1 / rt_value)
        / (
            max(
                (
                    (vcl_value ** (1 - (0.5 * vcl_value))) / (rsh**0.5)
                )
                + (
                    ((phi_value**m) / (a * rw)) ** 0.5
                ),
                0  # Ensure the denominator is non-negative
            )
        )
    ) ** (2 / n)
    
    return sw_indonesia


def calc_sw(
    df,
    rw=0.08,
    a=1,
    m=2,
    n=2,
    mid_perf_md=None,
    mid_perf_bht=210,
    surface_temp=60,
    rsh=None,
):
    if ("RT" in df.columns) or ("RDEEP" in df.columns):
        df["SWarchie"] = df.apply(
            lambda row: sw_archie(df, row, rw=rw, a=a, m=m, n=n),
            axis=1,
        )
        df["SWwaxman"] = df.apply(
            lambda row: sw_waxman(
                df,
                row,
                rw=rw,
                a=a,
                m=m,
                n=n,
                mid_perf_md=mid_perf_md,
                mid_perf_bht=mid_perf_bht,
                surface_temp=surface_temp,
            ),
            axis=1,
        )
        
        print(type(df['SWwaxman'].iloc[0]))
        
        df["SWindonesia"] = df.apply(
            lambda row: sw_indonesia(df, row, rw=rw, a=a, m=m, n=n, rsh=rsh),
            axis=1,
        )

    if all(col in df.columns for col in ["SWarchie", "SWwaxman"]):
        mean_archie = df["SWarchie"].mean()
        mean_waxman = df["SWwaxman"].mean()
        df["SWwaxman"] *= mean_archie / mean_waxman
    else:
        df.drop(columns=[col for col in ["SWarchie", "SWwaxman"] if col in df.columns], inplace=True)

    return df


def select_sw(df, select_sw="archie"):
    if select_sw == "archie":
        try:
            df["SW"] = df["SWarchie"]
        except KeyError:
            print("No SWarchie column found. Please check the column names.")

            return df
    elif select_sw == "waxman":
        try:
            df["SW"] = df["SWwaxman"]
        except KeyError:
            print("No SWwaxman column found. Please check the column names.")

            return df
    elif select_sw == "indo":
        try:
            df["SW"] = df["SWindonesia"]
        except KeyError:
            print("No SWindonesia column found. Please check the column names.")

            return df

    # df = df.drop(
    #     [i for i in df.columns if i.lower().startswith("sw") and i.lower() != "sw"],
    #     axis=1,
    # )

    return df


def pickett_plot(df, vcl_limit=0.5, rw=0.08, a=1, m=2, n=2, z="VCL"):
    fig = plt.figure(figsize=(7, 6))
    plt.title(
        "Pickett Plot"
        + " for VCL < "
        + str(int(vcl_limit * 100))
        + "%"
        + " and Rw = "
        + str(rw)
        + " ohm.m"
    )
    c = df[z][df.VCL < vcl_limit]
    plt.scatter(
        df.RDEEP[df.VCL < vcl_limit],
        df.PHIE[df.VCL < vcl_limit],
        c=c,
        s=20,
        cmap="plasma",
    )
    cbar = plt.colorbar()
    cbar.set_label(f"{z}")
    plt.xlim(0.1, 1000)
    plt.ylim(0.01, 1)
    plt.ylabel("PHIE [V/V]")
    plt.xlabel("RDEEP [m.ohm]")
    plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(custom_formatter))
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(custom_formatter))
    plt.gca().set_xscale("log")
    plt.gca().set_yscale("log")

    # calculate the saturation lines
    sw_plot = (1.0, 0.8, 0.6, 0.4, 0.2)
    phie_plot = (0.01, 1)
    rt_plot = np.zeros((len(sw_plot), len(phie_plot)))

    for i in range(0, len(sw_plot)):
        for j in range(0, len(phie_plot)):
            rt_result = (a * rw) / (sw_plot[i] ** n) / (phie_plot[j] ** m)
            rt_plot[i, j] = rt_result
    for i in range(0, len(sw_plot)):
        plt.plot(rt_plot[i], phie_plot, label="SW " + str(int(sw_plot[i] * 100)) + "%")
        plt.legend(loc="best")

    plt.grid(True, which="both", ls="-", color="gray")
    
    plt.tight_layout()
    
    return fig


def perm_timur(phie, sw):
    perm = ((93 * (phie**2.2)) / sw) ** 2
    return perm


def interpretation_plot(
    df,
    depth_start=None,
    depth_end=None,
    column_data=None,
    core_data=None,
    fill_plot=True,
    net_pay_intervals=None,
):  
    if net_pay_intervals:
        fig, ax = plt.subplots(nrows=1, ncols=8, figsize=(12, 20), sharey=True)
    else:
        fig, ax = plt.subplots(nrows=1, ncols=7, figsize=(12, 20), sharey=True)
        
    fig.subplots_adjust(top=0.88, wspace=0.2)

    if depth_start == None or depth_end == None:
        depth_start = df.MD.min()
        depth_end = df.MD.max()

    # General setting for all axis
    for axes in ax:
        axes.set_ylim(depth_start, depth_end)
        axes.invert_yaxis()
        axes.yaxis.grid(True, which="minor", linestyle=":")
        axes.yaxis.grid(True, which="major", linestyle="-", linewidth="1")
        axes.yaxis.set_major_locator(ticker.MultipleLocator(100))
        axes.yaxis.set_minor_locator(ticker.MultipleLocator(20))
        axes.get_xaxis().set_visible(False)

    # 1st track: GR, SP, CALI track
    for col, color, pos, subplot_idx in [
        ("GR", "green", 80, 0),
        ("CALI", "black", 40, 0),
        ("SP", "blue", 0, 0),
    ]:
        # Check if the column exists in the DataFrame and has data
        if col in df.columns:
            # Extract unit and limits from the column_data dictionary
            unit = column_data[col]["unit"]
            limits = column_data[col]["limits"]

            # Dynamically create the label
            label = f"{col} [{unit}]"

            # Create a twiny axis and set its properties
            ax_temp = ax[subplot_idx].twiny()
            ax_temp.set_xlim(*limits)
            ax_temp.spines["top"].set_position(("outward", pos))
            ax_temp.set_xlabel(label, color=color)
            ax_temp.tick_params(axis="x", colors=color)

            # Plot the data
            ax_temp.plot(df[col], df.MD, label=label, color=color)

    # 2nd track: Resistivities
    for col, color, pos, subplot_idx in [
        ("RDEEP", "red", 80, 1),
        ("RMED", "purple", 40, 1),
        ("RSHAL", "black", 0, 1),
    ]:
        if col in df.columns and column_data.get(col):
            # Extract unit and limits from the column_data dictionary
            unit = column_data[col]["unit"]
            limits = column_data[col]["limits"]

            # Dynamically create the label
            label = f"{col} [{unit}]"

            # Create a twiny axis and set its properties
            ax_temp = ax[subplot_idx].twiny()
            ax_temp.set_xlim(*limits)
            ax_temp.set_xscale("log")
            ax_temp.spines["top"].set_position(("outward", pos))
            ax_temp.set_xlabel(label, color=color)
            ax_temp.tick_params(axis="x", colors=color)

            # Plot the data
            ax_temp.plot(df[col], df.MD, label=label, color=color)

    # 3rd track: DT, RHOB, NPHI track
    for col, color, pos, subplot_idx in [
        ("DT", "blue", 0, 2),
        ("NPHI", "green", 40, 2),
        ("RHOB", "red", 80, 2),
    ]:
        if col in df.columns and column_data.get(col):
            # Extract unit and limits from the column_data dictionary
            unit = column_data[col]["unit"]
            limits = column_data[col]["limits"]

            # Dynamically create the label
            label = f"{col} [{unit}]"

            # Create a twiny axis and set its properties
            ax_temp = ax[subplot_idx].twiny()
            if limits != ("auto", "auto"):  # Check if limits are not auto
                ax_temp.set_xlim(*limits)

            # Invert axis for NPHI
            if col == "NPHI":
                ax_temp.invert_xaxis()

            ax_temp.spines["top"].set_position(("outward", pos))
            ax_temp.set_xlabel(label, color=color)
            ax_temp.tick_params(axis="x", colors=color)

            # Plot the data
            ax_temp.plot(df[col], df.MD, label=label, color=color)

    # 3rd track: SW
    for col, color, pos, subplot_idx in [
        ("SW", "blue", 0, 3),
    ]:
        if col in df.columns and column_data.get(col):
            # Extract unit and limits from the column_data dictionary
            unit = column_data[col]["unit"]
            limits = column_data[col]["limits"]

            # Dynamically create the label
            label = f"{col} [{unit}]"

            # Create a twiny axis and set its properties
            ax_temp = ax[subplot_idx].twiny()
            ax_temp.set_xlim(*limits)

            # Set fill areas if the `fill` flag is True
            if fill_plot:
                left_limit, right_limit = limits
                line_value = df[col]  # Or some other value based on logic

                # Fill from left limit to line value with blue
                ax_temp.fill_betweenx(
                    df.MD,
                    left_limit,
                    line_value,
                    color="lightblue",
                    alpha=0.5,
                    label="Water",
                )
                # Fill from line value to right limit with green
                ax_temp.fill_betweenx(
                    df.MD,
                    line_value,
                    right_limit,
                    color="green",
                    alpha=0.5,
                    label="Hydrocarbon",
                )

            # Plot the data
            ax_temp.invert_xaxis()

            ax_temp.plot(df[col], df.MD, label="_nolegend_", color=color)

            # Set the axis properties
            ax_temp.spines["top"].set_position(("outward", pos))
            ax_temp.set_xlabel(label, color=color)
            ax_temp.tick_params(axis="x", colors=color)
            ax_temp.legend(loc="lower right")

    # 4th track: Permeability
    for col, color, pos, subplot_idx in [
        ("PERM", "green", 0, 4),  # Plotting 'PermTimur'
        ("core_perm", "red", 40, 4),  # Plotting 'core_perm'
    ]:
        if col == "PERM" and col in df.columns:
            unit = column_data[col]["unit"]
            limits = column_data[col]["limits"]
            label = f"{col}-LOG [{unit}]"

            # Create a twiny axis for PermTimur
            ax_temp = ax[subplot_idx].twiny()
            ax_temp.set_xlim(*limits)
            ax_temp.plot(df[col], df.MD, label=label, color=color)
            ax_temp.spines["top"].set_position(("outward", pos))
            ax_temp.set_xlabel(label, color=color)
            ax_temp.tick_params(axis="x", colors=color)

        elif (
            col == "core_perm"
            and core_data is not None
            and "core_perm" in core_data.columns
        ):
            unit = column_data[col]["unit"]
            limits = column_data[col]["limits"]
            label = f"{col} [{unit}]"

            # Create a twiny axis for core_perm
            ax_temp = ax[subplot_idx].twiny()
            ax_temp.set_xlim(*limits)
            ax_temp.scatter(
                core_data[col], core_data.MD, label=label, color=color, linewidths=0.5
            )
            ax_temp.spines["top"].set_position(("outward", pos))
            ax_temp.set_xlabel(label, color=color)
            ax_temp.tick_params(axis="x", colors=color)

    # 5th track: PHIE, BVW
    for col, color, pos, subplot_idx, fill, scatter_col, scatter_color in [
        ("PHIE", "orange", 0, 5, fill_plot, None, None),  # Plotting 'PHIE' with fill
        (
            "BVW",
            "blue",
            40,
            5,
            fill_plot,
            "core_por",
            "red",
        ),  # Plotting 'BVW' with core_por scatter
        (
            "core_por",
            "red",
            80,
            5,
            False,
            "core_por",
            "red",
        ),  # Plotting core data (PHIE-CORE) scatter
    ]:
        if col != "core_por":
            unit = column_data[col]["unit"]
            limits = column_data[col]["limits"]
            label = f"{col} [{unit}]"

            # Create a twiny axis for PHIE
            ax_temp = ax[subplot_idx].twiny()
            ax_temp.set_xlim(*limits)
            ax_temp.invert_xaxis()

            # Fill between for PHIE
            if fill:
                ax_temp.fill_betweenx(
                    df.MD, 0, df.BVW, color="lightblue", alpha=0.5, label="Water"
                )
                ax_temp.fill_betweenx(
                    df.MD,
                    df.PHIE,
                    df.BVW,
                    color="green",
                    alpha=0.2,
                    label="Hydrocarbon",
                )

            ax_temp.legend(loc="lower right")
            ax_temp.spines["top"].set_position(("outward", pos))
            ax_temp.set_xlabel(label, color=color)
            ax_temp.tick_params(axis="x", colors=color)

            # Plot PHIE data (line)
            ax_temp.plot(
                df[col],
                df.MD,
                label="_nolegend_",
                color=color,
                linewidth=0.5,
                alpha=0.5,
            )

        elif (
            col == "core_por"
            and core_data is not None
            and scatter_col in core_data.columns
        ):
            unit = column_data["core_perm"]["unit"]
            limits = column_data["core_perm"]["limits"]
            label = f"core_perm [{unit}]"

            # Create a twiny axis for core_perm
            ax_temp = ax[subplot_idx].twiny()
            ax_temp.set_xlim(*limits)
            ax_temp.invert_xaxis()

            # Scatter plot for core data
            ax_temp.scatter(
                core_data[scatter_col],
                core_data.MD,
                label="_nolegend_",
                color=scatter_color,
                linewidths=0.5,
            )

            ax_temp.spines["top"].set_position(("outward", pos))
            ax_temp.set_xlabel(f"{scatter_col} - CORE", color=scatter_color)
            ax_temp.tick_params(axis="x", colors=scatter_color)

    # 6th track: PHIE, MATRIX, VCL
    for col, color, pos, subplot_idx, fill in [
        ("BVW", "blue", 120, 6, fill_plot),
        ("PHIE", "black", 80, 6, fill_plot),
        ("MATRIX", "orange", 40, 6, fill_plot),
        ("VCL", "green", 0, 6, fill_plot),
    ]:
        # Check if the column exists in the DataFrame and has data
        if col in df.columns:
            # Extract unit and limits from the column_data dictionary
            unit = column_data[col]["unit"]
            limits = column_data[col]["limits"]

            # Dynamically create the label
            label = f"{col} [{unit}]"

            # Create a twiny axis and set its properties
            ax_temp = ax[subplot_idx].twiny()
            ax_temp.set_xlim(*limits)
            ax_temp.spines["top"].set_position(("outward", pos))
            ax_temp.set_xlabel(label, color=color)
            ax_temp.tick_params(axis="x", colors=color)

            if col == "PHIE" or col == "MATRIX":
                ax_temp.invert_xaxis()

            # Plot the data or fill between if fill flag is set
            if fill and col == "MATRIX":
                ax_temp.fill_betweenx(
                    df.MD, 0, df.BVW, color="lightgray", label="Water"
                )
                ax_temp.fill_betweenx(
                    df.MD, df.BVW, df.PHIE, color="green", label="Hydrocarbon"
                )
                ax_temp.fill_betweenx(
                    df.MD, df.PHIE, 1 - df.VCL, color="orange", label="Matrix"
                )
                ax_temp.fill_betweenx(
                    df.MD, 1 - df.VCL, 1, color="lightgreen", label="Shale"
                )
                ax_temp.legend(loc="lower right")

            if col != "MATRIX":
                ax_temp.plot(
                    df[col], df.MD, label="_nolegend_", color=color, linewidth=0.5
                )

    # 7th track: Net Pay
    if net_pay_intervals:
        print(net_pay_intervals)
        for col, color, pos, subplot_idx, fill in [
            ("Net Pay", "black", 0, 7, fill_plot),
        ]:
            label = f"{col}"

            ax_temp = ax[subplot_idx].twiny()
            ax_temp.set_xlim(0, 1)  # Set x-axis limits
            ax_temp.spines["top"].set_position(("outward", pos))
            ax_temp.set_xlabel(label, color=color)
            ax_temp.tick_params(axis="x", colors=color)

            # Iterate through the netpay intervals and plot them
            for interval in net_pay_intervals:
                # Assuming interval is a tuple (start_depth, end_depth)
                start_depth, end_depth = interval

                # Plotting the net pay interval on the temp axis using fill_betweenx
                ax_temp.fill_betweenx(
                    df.MD[
                        (df.MD >= start_depth) & (df.MD <= end_depth)
                    ],  # Use depth from df.MD
                    0,
                    1,  # Set the x-axis range
                    color="purple",
                    alpha=0.5,
                )
    plt.tight_layout()
    
    return fig


def calculate_net_pay(df, sw_cutoff=0.2, vcl_cutoff=0.2, phi_cutoff=0.2):
    # Apply conditions
    net_pay_condition = (
        (df["SW"] <= sw_cutoff)  # SW below cutoff (indicating oil)
        & (df["PHIE"] >= phi_cutoff)  # Porosity above cutoff (indicating porosity)
        & (
            df["VCL"] <= vcl_cutoff
        )  # Clay volume below cutoff (indicating productive zone)
    )

    # Create a column for net pay flag (1 for net pay, 0 for non-net pay)
    df["Net_Pay"] = np.where(net_pay_condition, 1, 0)

    # Identify the depth intervals for net pay (where Net_Pay == 1)
    net_pay_intervals = []
    start_depth = None

    for idx in range(len(df)):
        if df["Net_Pay"].iloc[idx] == 1:
            if start_depth is None:
                start_depth = df["MD"].iloc[idx]  # Start of a new net pay zone
            end_depth = df["MD"].iloc[idx]  # Update end depth to current depth
        elif start_depth is not None:
            net_pay_intervals.append((start_depth, end_depth))
            start_depth = None

    # In case the last net pay zone ends at the last depth
    if start_depth is not None:
        net_pay_intervals.append((start_depth, end_depth))

    return df, net_pay_intervals


def plot_with_cutoffs(df, sw_cutoff=0.2, vcl_cutoff=0.2, phi_cutoff=0.2):
    # First Plot: SW vs VCL with heatmap based on GR
    fig = plt.figure(figsize=(12, 6))

    # Create scatter plot with heatmap based on df['GR']
    plt.subplot(1, 2, 1)
    scatter1 = plt.scatter(
        df["SW"].clip(0, 1),
        df["VCL"],
        c=df["GR"],  # Color by 'GR' value
        cmap="viridis",  # Choose your color map here
        edgecolors="k",  # Optional: add black edge to each point
        alpha=0.7,
    )  # Optional: control transparency of points

    # Add vertical line at SW cutoff
    plt.axvline(
        x=sw_cutoff, color="red", linestyle="--", label=f"SW Cutoff at {sw_cutoff}"
    )
    # Add horizontal line at VCL cutoff
    plt.axhline(
        y=vcl_cutoff, color="green", linestyle="--", label=f"VCL Cutoff at {vcl_cutoff}"
    )

    plt.fill_betweenx(y=[0, vcl_cutoff], x1=0, x2=sw_cutoff, color="green", alpha=0.5)

    # Add labels and title
    plt.xlabel("SW")
    plt.ylabel("VCL")
    plt.title("Scatter Plot: SW vs VCL")

    # Add color bar to indicate the GR values
    plt.colorbar(scatter1, label="GR")
    plt.legend()

    # Second Plot: VCL vs PHIE with heatmap based on GR
    plt.subplot(1, 2, 2)
    scatter2 = plt.scatter(
        df["VCL"],
        df["PHIE"],
        c=df["GR"],  # Color by 'GR' value
        cmap="viridis",  # Choose your color map here
        edgecolors="k",  # Optional: add black edge to each point
        alpha=0.7,
    )  # Optional: control transparency of points

    # Add vertical line at VCL cutoff
    plt.axvline(
        x=vcl_cutoff, color="red", linestyle="--", label=f"VCL Cutoff at {vcl_cutoff}"
    )
    # Add horizontal line at PHIE cutoff
    plt.axhline(
        y=phi_cutoff,
        color="green",
        linestyle="--",
        label=f"PHIE Cutoff at {phi_cutoff}",
    )

    plt.fill_betweenx(y=[phi_cutoff, 1], x1=0, x2=vcl_cutoff, color="green", alpha=0.5)

    # Add labels and title
    plt.xlabel("VCL")
    plt.ylabel("PHIE")
    plt.title("Scatter Plot: VCL vs PHIE")

    # Add color bar to indicate the GR values
    plt.colorbar(scatter2, label="GR")
    plt.legend()

    # Show the plots
    plt.tight_layout()
    
    return fig
    # plt.show()


def calculate_net_pay_bopd(df, depth_intervals, oil_viscosity=1, oil_fvf=1.2):
    """
    Calculate Net Pay in BOPD for multiple depth intervals where Net Pay = 1.
    This version includes oil viscosity and oil FVF (Formation Volume Factor).

    Parameters:
    - df: DataFrame containing 'MD', 'PERM', 'VCL', 'SW', 'Net Pay', 'PHIE' columns.
    - depth_intervals: List of lists where each list contains [start_depth, end_depth].
    - oil_viscosity: Oil viscosity in cP (default is 1 cP).
    - oil_fvf: Oil Formation Volume Factor in bbl/STB (default is 1.2 bbl/STB).

    Returns:
    - result_df: DataFrame with 'start_depth', 'end_depth', and 'Net Pay (BOPD)' columns.
    """
    results = []

    # Iterate through each depth interval
    for interval in depth_intervals:
        start_depth, end_depth = interval

        # Filter the data for the specified depth interval
        df_interval = df[(df["MD"] >= start_depth) & (df["MD"] <= end_depth)]

        # Initialize the net pay BOPD sum for this interval
        net_pay_fhcp = 0
        net_pay_bopd = 0

        # Iterate over the rows in the filtered dataframe
        for _, row in df_interval.iterrows():
            if row["Net_Pay"] == 1:  # Only consider rows where Net Pay = 1
                # Calculate BOPD for this row (adjusted with oil viscosity and FVF)
                net_pay_thickness = (
                    1  # Assuming 1 meter or foot thickness per row (adjust as needed)
                )

                # Calculate BOPD for this row (adjusted with oil viscosity and FVF)
                bopd_contribution = (
                    row["PERM"]
                    * row["PHIE"]
                    * (1 - row["SW"])
                    * net_pay_thickness
                    * oil_fvf
                ) / (oil_viscosity * 1000)
                fhcp_contribution = net_pay_thickness * row["PHIE"] * (1 - row["SW"])

                # Add this row's contribution to the total BOPD
                net_pay_bopd += bopd_contribution
                net_pay_fhcp += fhcp_contribution

        ntg_ratio = len(df_interval[df_interval["Net_Pay"] == 1]) / len(df_interval)
        avg_phi = mean(df_interval[df_interval["Net_Pay"] == 1]["PHIE"])
        avg_sw = mean(df_interval[df_interval["Net_Pay"] == 1]["SW"])
        avg_vcl = mean(df_interval[df_interval["Net_Pay"] == 1]["VCL"])

        # Append the result for this interval
        results.append([start_depth, end_depth, ntg_ratio, net_pay_fhcp, net_pay_bopd, avg_phi, avg_sw, avg_vcl])

    # Convert the results to a DataFrame
    result_df = pd.DataFrame(
        results,
        columns=[
            "Start Depth",
            "End Depth",
            "NTG Ratio",
            "Net Pay (FHCP)",
            "Net Pay (BOPD)",
            "Avg PHI",
            "Avg SW",
            "Avg VCL",
        ],
    )
    return result_df
