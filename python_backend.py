from fastapi import FastAPI, File, UploadFile, HTTPException, Form, BackgroundTasks
from functools import lru_cache
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import numpy as np
import shutil
import os
from feature_log import *
import io
import base64
import json
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Set the level to DEBUG to capture detailed info
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format with time and level
)
logger = logging.getLogger(__name__)

app = FastAPI()

CACHE = {}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5296"],  # Replace with your Blazor app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def get_dropdown_dict_vcl(df: pd.DataFrame):
    col_list = [col for col in df.columns if col.startswith("VCL") and col != "VCL"]

    column_mappings = []

    for col in col_list:
        if col == "VCLGR":
            column_mappings.append({"value": "gr", "text": "Gamma Ray"})
        elif col == "VCLSP":
            column_mappings.append({"value": "sp", "text": "Spontaneous Potential"})
        elif col == "VCLRT":
            column_mappings.append({"value": "rt", "text": "Resistivity"})
        elif col == "VCLND":
            column_mappings.append({"value": "nd", "text": "Neutron-Density"})

    return column_mappings


def get_dropdown_dict_phi(df: pd.DataFrame):
    col_list = [col for col in df.columns if col.startswith("PHI") and col != "PHIE"]

    column_mappings = []

    for col in col_list:
        if col == "PHISw":
            column_mappings.append({"value": "wyllie", "text": "Wyllie"})
        elif col == "PHISwshc":
            column_mappings.append(
                {"value": "wyllie_sh_corr", "text": "Wyllie Shale Correlation"}
            )
        elif col == "PHISrhg":
            column_mappings.append({"value": "rhg", "text": "Raymer-Hunt-Gardner"})
        elif col == "PHISrhgshc":
            column_mappings.append(
                {
                    "value": "rhg_sh_corr",
                    "text": "Raymer-Hunt-Gardner Shale Correlation",
                }
            )
        elif col == "PHID":
            column_mappings.append({"value": "density", "text": "Density"})
        elif col == "PHIDshc":
            column_mappings.append(
                {"value": "density_sh_corr", "text": "Density Shale Correlation"}
            )
        elif col == "PHINshc":
            column_mappings.append(
                {"value": "neutron_sh_corr", "text": "Neutron Shale Correlation"}
            )
        elif col == "PHIxND":
            column_mappings.append(
                {"value": "neutron_density", "text": "Neutron-Density"}
            )

    return column_mappings


def get_dropdown_dict_sw(df: pd.DataFrame):
    col_list = [col for col in df.columns if col.startswith("SW") and col != "SW"]

    column_mappings = []

    for col in col_list:
        if col == "SWarchie":
            column_mappings.append({"value": "archie", "text": "Archie"})
        elif col == "SWwaxman":
            column_mappings.append({"value": "waxman", "text": "Waxman"})
        elif col == "SWindonesia":
            column_mappings.append({"value": "indo", "text": "Indonesia"})

    return column_mappings


def save_to_disk(df_las: pd.DataFrame, column_data: dict):
    df_las.to_parquet("uploads/df_las.parquet", engine="pyarrow")

    df = pd.DataFrame(column_data).T
    df["limits"] = df["limits"].apply(lambda x: list(x))

    df.to_parquet("uploads/column_data.parquet", engine="pyarrow")


def save_to_cache(df_las: pd.DataFrame, column_data: dict):
    CACHE["df_las"] = df_las

    df = pd.DataFrame(column_data).T
    df["limits"] = df["limits"].apply(lambda x: list(x))

    CACHE["column_data"] = df


def dict_from_parquet():
    loaded_df = pd.read_parquet("uploads/column_data.parquet", engine="pyarrow")
    loaded_dict = loaded_df.to_dict(orient="index")

    for _, value in loaded_dict.items():
        value["limits"] = tuple(value["limits"])

    return loaded_dict


def dict_from_cache():
    loaded_df = CACHE["column_data"]
    loaded_dict = loaded_df.to_dict(orient="index")

    for _, value in loaded_dict.items():
        value["limits"] = tuple(value["limits"])

    return loaded_dict


def load_data():
    if "df_las" in CACHE:
        df = CACHE["df_las"]
    else:
        df = pd.read_parquet("uploads/df_las.parquet", engine="pyarrow")
    
    if "column_data" in CACHE:
        dict_ = dict_from_cache()
    else:
        dict_ = dict_from_parquet()
        
    return df, dict_

@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    try:
        os.makedirs("uploads", exist_ok=True)

        # Save uploaded file
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        df_las, curve_data = read_lasio(file_path)

        dict_test = {
            i: (df_las[i].min(), df_las[i].max()) for i in list(curve_data.keys())
        }
        column_data = {
            key: {"unit": curve_data.get(key), "limits": dict_test.get(key)}
            for key in curve_data.keys()
        }
        
        limit_mapping = {
            "GR": (0, 200),
            "SP": (-125, 125),
            "RHOB": (1.95, 2.95),
            "NPHI": (-0.15, 0.45),
            "RDEEP": (0.2, 2000),
            "RMED": (0.2, 2000),
            "RSHAL": (0.2, 2000),
        }

        for key, limits in limit_mapping.items():
            if key in column_data:
                column_data[key]["limits"] = limits

        for i in ["VCL", "PHI", "PHIE", "SW"]:
            column_data[i] = {"unit": "V/V", "limits": (0, 1)}
        
        save_to_disk(df_las, column_data)
        save_to_cache(df_las, column_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-combo-plot/")
async def process_combo_plot(
    figure_height: Optional[int] = Form(30),
):
    try:

        df_las, column_data = load_data()

        ### Combo Plot Image using Python (deprecated) ###
        # combo_plot_img = combo_plot(
        #     df_las, figure_height=figure_height, column_data=column_data
        # )

        # combo_plot_base64 = plot_to_base64(combo_plot_img)

        # plt.close(combo_plot_img)
        
        df_las_json = {}

        for column in df_las.columns:
            df_las_json[column] = df_las[column].tolist()

        return JSONResponse(
            {
                "df_las": json.loads(json.dumps(df_las_json), parse_constant=lambda x: None),
                "column_data": column_data,
                # "combo_plot": combo_plot_base64,
                "message": "Combo plot generated successfully",
            }
        )
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-vcl-plot/")
async def process_vcl_plot(
    gr_clean: Optional[float] = Form(None),
    gr_clay: Optional[float] = Form(None),
    sp_clean: Optional[float] = Form(None),
    sp_clay: Optional[float] = Form(None),
    rt_clean: Optional[float] = Form(None),
    rt_clay: Optional[float] = Form(None),
    neut_clean1: Optional[float] = Form(None),
    neut_clean2: Optional[float] = Form(None),
    neut_clay: Optional[float] = Form(None),
    den_clean1: Optional[float] = Form(None),
    den_clean2: Optional[float] = Form(None),
    den_clay: Optional[float] = Form(None),
    correction_gr: Optional[str] = Form("young"),
):
    try:
        df_las, column_data = load_data()

        df_las = calc_vcl(
            df_las,
            gr_clean,
            gr_clay,
            sp_clean,
            sp_clay,
            rt_clean,
            rt_clay,
            neut_clean1,
            den_clean1,
            neut_clean2,
            den_clean2,
            neut_clay,
            den_clay,
            correction_gr,
        )

        dropdown_vcl = get_dropdown_dict_vcl(df_las)

        ### VCL Plot Image using Python (deprecated) ###
        # vcl_plot_img = vcl_plot(
        #     df_las,
        #     column_data,
        #     neut_clean1,
        #     den_clean1,
        #     neut_clean2,
        #     den_clean2,
        #     neut_clay,
        #     den_clay,
        # )
        # vcl_plot_base64 = plot_to_base64(vcl_plot_img)

        # plt.close(vcl_plot_img)
        
        df_las_json = {}

        for column in df_las.columns:
            df_las_json[column] = df_las[column].tolist()

        save_to_cache(df_las, column_data)

        return JSONResponse(
            {
                "df_las": json.loads(json.dumps(df_las_json), parse_constant=lambda x: None),
                "column_data": column_data,
                "dropdown_vcl": json.dumps(dropdown_vcl, indent=4),
                # "vcl_plot": vcl_plot_base64,
                "message": "VCL plot generated successfully",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-phi-plot/")
async def process_phi_plot(
    dt_ma: Optional[float] = Form(None),
    dt_fl: Optional[float] = Form(None),
    dt_sh: Optional[float] = Form(None),
    den_ma: Optional[float] = Form(None),
    den_fl: Optional[float] = Form(None),
    den_sh: Optional[float] = Form(None),
    neut_sh: Optional[float] = Form(None),
    cp: Optional[float] = Form(0.67),
    alpha: Optional[float] = Form(1),
    vcl_select: Optional[str] = Form("gr")
):
    try:
        df_las, column_data = load_data()
        
        df_las = select_vcl(df_las, vcl_select)

        df_las = calc_phi(
            df_las,
            dt_ma=dt_ma,
            dt_fl=dt_fl,
            dt_sh=dt_sh,
            den_ma=den_ma,
            den_fl=den_fl,
            den_sh=den_sh,
            neut_sh=neut_sh,
            cp=cp,
            alpha=alpha,
        )

        dropdown_phi = get_dropdown_dict_phi(df_las)

        ### PHI Plot Image using Python (deprecated) ###
        # phi_plot_img = custom_interpretation_plot(
        #     df_las,
        #     column_data,
        #     [i for i in df_las.columns if "phi" in i.lower() and i != "NPHI"],
        # )
        # phi_plot_base64 = plot_to_base64(phi_plot_img)

        # plt.close(phi_plot_img)
        
        df_las_json = {}

        for column in df_las.columns:
            df_las_json[column] = df_las[column].tolist()

        save_to_cache(df_las, column_data)

        return JSONResponse(
            {
                "df_las": json.loads(json.dumps(df_las_json), parse_constant=lambda x: None),
                "column_data": column_data,
                "dropdown_phi": json.dumps(dropdown_phi, indent=4),
                # "phi_plot": phi_plot_base64,
                "message": "PHI plot generated successfully",
            }
        )
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-pickett-plot/")
async def process_pickett_plot(
    phi_select: Optional[str] = Form("neutron_density")
):
    try:
        df_las, _ = load_data()
        
        df_las = select_phi(df_las, phi_select)

        ### Pickett Plot Image using Python (deprecated) ###
        # pickett_plot_img = pickett_plot(df_las, vcl_limit, rw, a, m, n, z_ax)

        # pickett_plot_base64 = plot_to_base64(pickett_plot_img)

        # plt.close(pickett_plot_img)

        return JSONResponse(
            {
                # "pickett_plot": pickett_plot_base64,
                "message": "Pickett plot generated successfully",
            }
        )
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-sw-plot/")
async def process_sw_plot(
    rw: Optional[float] = Form(0.08),
    rsh: Optional[float] = Form(None),
    a: Optional[float] = Form(1),
    m: Optional[float] = Form(2),
    n: Optional[float] = Form(2),
    mid_perf_md: Optional[float] = Form(None),
    mid_perf_bht: Optional[float] = Form(210),
    surface_temp: Optional[float] = Form(60),
    phi_select: Optional[str] = Form("neutron_density"),
):
    try:
        df_las, column_data = load_data()
        
        df_las = select_phi(df_las, phi_select)

        df_las = calc_sw(
            df_las,
            rw=rw,
            a=a,
            m=m,
            n=n,
            mid_perf_md=mid_perf_md,
            mid_perf_bht=mid_perf_bht,
            surface_temp=surface_temp,
            rsh=rsh,
        )

        dropdown_sw = get_dropdown_dict_sw(df_las)

        ### SW Plot Image using Python (deprecated) ###
        # sw_plot_img = custom_interpretation_plot(
        #     df_las,
        #     column_data,
        #     [i for i in df_las.columns if i.lower().startswith("sw")],
        # )
        # sw_plot_base64 = plot_to_base64(sw_plot_img)

        # plt.close(sw_plot_img)
        
        df_las_json = {}

        for column in df_las.columns:
            df_las_json[column] = df_las[column].tolist()
        
        save_to_cache(df_las, column_data)

        return JSONResponse(
            {
                "df_las": json.loads(json.dumps(df_las_json), parse_constant=lambda x: None),
                "column_data": column_data,
                "dropdown_sw": json.dumps(dropdown_sw, indent=4),
                # "sw_plot": sw_plot_base64,
                "message": "SW plot generated successfully",
            }
        )
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-cutoff-plot/")
async def process_cut_off(
    sw_cutoff: Optional[float] = Form(0.8),  
    phi_cutoff: Optional[float] = Form(0.2),
    vcl_cutoff: Optional[float] = Form(0.2),
    sw_select: Optional[str] = Form("archie"),
):
    
    df_las, column_data = load_data()
    
    df_las_select = select_sw(df_las, sw_select)

    for i in df_las_select.columns:
        if (i not in list(column_data.keys())) and i.lower().startswith("sw"):
            column_data[i] = {"unit": "V/V", "limits": (0, 1)}
    
    df_las_select["BVW"] = df_las_select["SW"] * df_las_select["PHIE"]
    df_las_select["MATRIX"] = 1 - df_las_select["VCL"] - df_las_select["PHIE"] 
    
    df_las_select["PERM"] = perm_timur(df_las_select["PHIE"], df_las_select["SW"])
    
    for i in df_las_select.columns:
        if (i not in list(column_data.keys())) and ("perm" in i.lower()):
            column_data[i] = {"unit": "MD", "limits": (0, 1000)}

    column_data["BVW"] = {"unit": "dec", "limits": (0, 1)}
    column_data["MATRIX"] = {"unit": "dec", "limits": (0, 1)}
    
    cutoff_plot_img = plot_with_cutoffs(df_las_select, sw_cutoff, vcl_cutoff, phi_cutoff)
    
    cutoff_plot_base64 = plot_to_base64(cutoff_plot_img)

    plt.close(cutoff_plot_img)
    
    df_las_json = {}

    for column in df_las_select.columns:
        df_las_json[column] = df_las_select[column].tolist()
    
    save_to_cache(df_las_select, column_data)
    
    return JSONResponse(
        {
            "df_las": json.loads(json.dumps(df_las_json), parse_constant=lambda x: None),
            "column_data": column_data,
            "cutoff_plot": cutoff_plot_base64,
            "message": "Cutoff plot generated successfully",
        }
    )

@app.post("/process-interpretation-plot/")
async def process_interpretation_plot(
    sw_cutoff: Optional[float] = Form(0.8),  
    phi_cutoff: Optional[float] = Form(0.2),
    vcl_cutoff: Optional[float] = Form(0.2),
):
    df_las, column_data = load_data()
    
    df_with_netpay, net_pay_intervals = calculate_net_pay(
        df_las, sw_cutoff, phi_cutoff, vcl_cutoff
    )
    
    interpretation_plot_img = interpretation_plot(
        df_with_netpay, column_data=column_data, net_pay_intervals=net_pay_intervals
    )
    
    interpretation_plot_base64 = plot_to_base64(interpretation_plot_img)
    
    plt.close(interpretation_plot_img)
    
    save_to_disk(df_las, column_data)
    save_to_cache(df_las, column_data)
    
    return JSONResponse(
        {
            "interpretation_plot": interpretation_plot_base64,
            "message": "Interpretation plot generated successfully",
        }
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
