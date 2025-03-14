function comboPlot(dfLasJson, columnDataJson) {
    const dfLas = JSON.parse(dfLasJson);
    const columnData = JSON.parse(columnDataJson);

    const data = [];
    
    // Helper function to add traces only if the column exists
    const addTrace = (columnName, xaxis, yaxis, lineColor = null, titleColor = null) => {
        if (dfLas[columnName]) {
            data.push({
                x: dfLas[columnName],
                y: dfLas["MD"],
                type: 'scatter',
                xaxis: xaxis,
                yaxis: yaxis,
                name: columnName,
                line: {color: lineColor},
                ...(titleColor && { marker: { color: titleColor } }) // Optional: apply color if provided
            });
        }
    };

    // Add traces conditionally
    addTrace("GR", "x3", "y", "green");
    addTrace("CALI", "x2", "y", "blue");
    addTrace("SP", "x", "y", "black");

    addTrace("RDEEP", "x6", "y", "red");
    addTrace("RMED", "x5", "y", "pink");
    addTrace("RSHAL", "x4", "y", "purple");

    addTrace("RHOB", "x9", "y", "red");
    addTrace("NPHI", "x8", "y", "green");
    addTrace("DTC", "x7", "y", "black");

    var layout = {
        height: 3000,
        showlegend: false,
        yaxis: {
            title: {
                text: `MD (${columnData['MD']?.unit || ''})`,
            },
            autorange: 'reversed',
            domain: [0, 0.95],
        },
        xaxis: {
            title: {
                text: `SP (${columnData['SP']?.unit || ''})`,
                standoff: 1
            },
            domain: [0, 0.3],
            side: 'top',
            automargin: 'true',
            range: columnData['SP']?.limits,
            zeroline: false
        },
        xaxis2: {
            title: {
                text: `CALI (${columnData['CALI']?.unit || ''})`,
                font: {color: 'blue'},
                standoff: 1
            },
            tickfont: {color: 'blue'},
            domain: [0, 0.3],
            overlaying: 'x',
            side: 'top',
            position: 0.975,
            automargin: 'true',
            range: columnData['CALI']?.limits,
            zeroline: false
        },
        xaxis3: {
            title: {
                text: `GR (${columnData['GR']?.unit || ''})`,
                font: {color: 'green'},
                standoff: 1
            },
            tickfont: {color: 'green'},
            domain: [0, 0.3],
            overlaying: 'x',
            side: 'top',
            position: 1,
            automargin: 'true',
            range: columnData['GR']?.limits,
            zeroline: false
        },
        xaxis4: {
            title: {
                text: `RSHAL (${columnData['RSHAL']?.unit || ''})`,
                font: {color: 'purple'},
                standoff: 1
            },
            domain: [0.35, 0.65],
            tickfont: {color: 'purple'},
            side: 'top',
            type: 'log',
            automargin: 'true',
            range: [-0.69897000433, 3.30102999566],
            zeroline: false
        },
        xaxis5: {
            title: {
                text: `RMED (${columnData['RMED']?.unit || ''})`,
                font: {color: 'pink'},
                standoff: 1
            },
            domain: [0.35, 0.65],
            tickfont: {color: 'pink'},
            overlaying: 'x4',
            side: 'top',
            type: 'log',
            position: 0.975,
            automargin: 'true',
            range: [-0.69897000433, 3.30102999566],
            zeroline: false
        },
        xaxis6: {
            title: {
                text: `RDEEP (${columnData['RDEEP']?.unit || ''})`,
                font: {color: 'red'},
                standoff: 1
            },
            domain: [0.35, 0.65],
            tickfont: {color: 'red'},
            overlaying: 'x4',
            side: 'top',
            type: 'log',
            position: 1,
            automargin: 'true',
            range: [-0.69897000433, 3.30102999566],
            zeroline: false
        },
        xaxis7: {
            title: {
                text: `DTC (${columnData['DTC']?.unit || ''})`,
                standoff: 1
            },
            domain: [0.7, 1],
            side: 'top',
            automargin: 'true',
            range: columnData['DTC']?.limits,
            zeroline: false
        },
        xaxis8: {
            title: {
                text: `NPHI (${columnData['NPHI']?.unit || ''})`,
                font: {color: 'green'},
                standoff: 1
            },
            domain: [0.7, 1],
            tickfont: {color: 'green'},
            overlaying: 'x7',
            side: 'top',
            position: 0.975,
            automargin: 'true',
            range: (columnData['NPHI']?.limits).reverse(),
            zeroline: false
        },
        xaxis9: {
            title: {
                text: `RHOB (${columnData['RHOB']?.unit || ''})`,
                font: {color: 'red'},
                standoff: 1
            },
            domain: [0.7, 1],
            tickfont: {color: 'red'},
            overlaying: 'x7',
            side: 'top',
            position: 1,
            automargin: 'true',
            range: columnData['RHOB']?.limits,
            zeroline: false
        }
    };

    Plotly.newPlot('comboPlotly', data, layout);
}

function vclPlot(dfLasJson, columnDataJson, listData) {
    const dfLas = JSON.parse(dfLasJson);
    const columnData = JSON.parse(columnDataJson);

    let [
        nphiClean1,
        nphiClean2,
        nphiClay,
        rhobClean1,
        rhobClean2,
        rhobClay
    ] = listData;

    console.log(rhobClean2);

    if (dfLas["RHOB"] && dfLas["NPHI"]) {
        if (nphiClean1 == null) {
            nphiClean1 = Math.min(...dfLas.NPHI); // Get the minimum value of NPHI
        }
        if (rhobClean1 == null) {
            rhobClean1 = Math.max(...dfLas.RHOB); // Get the maximum value of RHOB
        }
        if (nphiClean2 == null) {
            nphiClean2 = Math.max(...dfLas.NPHI); // Get the maximum value of NPHI
        }
        if (rhobClean2 == null) {
            rhobClean2 = Math.min(...dfLas.RHOB); // Get the minimum value of RHOB
        }
        if (nphiClay == null) {
            nphiClay = Math.max(...dfLas.NPHI); // Get the maximum value of NPHI
        }
        if (rhobClay == null) {
            rhobClay = Math.max(...dfLas.RHOB); // Get the maximum value of RHOB
        }
    }
    
    const data = [];
    
    // Helper function to add traces only if the column exists
    const addTrace = (columnName, xaxis, yaxis, lineColor = null, titleColor = null) => {
        if (dfLas[columnName]) {
            data.push({
                x: dfLas[columnName],
                y: dfLas["MD"],
                type: "scatter",
                xaxis: xaxis,
                yaxis: yaxis,
                name: columnName,
                line: {color: lineColor},
                ...(titleColor && { marker: { color: titleColor } }) // Optional: apply color if provided
            });
        }
    };

    const addScatterWithColorBar = (columnNameX, columnNameY, xaxis, yaxis, titleColor = null) => {
        // Check if the columns exist in dfLas
        if (dfLas[columnNameX] && dfLas[columnNameY] && dfLas["GR"]) {
            // Add the main scatter plot data
            data.push({
                x: dfLas[columnNameX],
                y: dfLas[columnNameY],
                type: "scatter",
                mode: "markers",
                xaxis: xaxis,
                yaxis: yaxis,
                name: "NXD",
                marker: {
                    color: dfLas["GR"],
                    colorscale: "Viridis",
                    showscale: true,
                    colorbar: {
                        title: `GR (${columnData['GR']?.unit || ''})`,
                        x: 0.655,
                        xref: "container",
                        len: 0.2313,
                        y: 0.115,
                    }
                },
                ...(titleColor && { marker: { color: titleColor } }) // Optional: apply color if provided
            });
        }
    
        // Add the additional points (nphiClean1, rhobClean1), (nphiClean2, rhobClean2), (nphiClay, rhobClay)
        const additionalPoints = [
            { x: nphiClean1, y: rhobClean1, name: 'Clean1' },
            { x: nphiClean2, y: rhobClean2, name: 'Clean2' },
            { x: nphiClay, y: rhobClay, name: 'Clay' }
        ];
    
        additionalPoints.forEach(point => {
            data.push({
                x: [point.x],
                y: [point.y],
                type: "scatter",
                mode: "markers",
                xaxis: xaxis,
                yaxis: yaxis,
                name: point.name,
                marker: {
                    color: 'red',
                    size: 10
                }
            });
        });

        data.push({
            x: [nphiClean1, nphiClean2], // X-coordinates of the line
            y: [rhobClean1, rhobClean2], // Y-coordinates of the line
            type: "scatter",
            mode: "lines",
            xaxis: xaxis,
            yaxis: yaxis,
            name: "Clean1 - Clean2",
            line: {
                color: 'black', // Line color
                width: 3, // Line width
            }
        });
    
        // Add a line connecting Clean1 to Clay
        data.push({
            x: [nphiClean1, nphiClay], // X-coordinates of the line
            y: [rhobClean1, rhobClay], // Y-coordinates of the line
            type: "scatter",
            mode: "lines",
            xaxis: xaxis,
            yaxis: yaxis,
            name: "Clean1 - Clay",
            line: {
                color: 'black', // Line color
                width: 3, // Line width
            }
        });
    };

    const addHistogram = (columnName, xaxis, yaxis, barColor = null, edgeColor = null) => {
        if (dfLas[columnName]) {
            data.push({
                x: dfLas[columnName],
                type: "histogram",
                xaxis: xaxis,
                yaxis: yaxis,
                nbinsx: 20,
                name: `(${columnName}) Frequency`,
                marker: {
                    color: barColor,
                    line: {
                        color: edgeColor,
                        width: 1,
                    }
                }
            });
        }
    };

    // Add traces conditionally
    addTrace("GR", "x2", "y", "blue");
    addTrace("SP", "x", "y", "black");

    addHistogram("GR", "x6", "y2", "blue", "black");
    addHistogram("SP", "x5", "y3", "black", "white");
    addHistogram("RDEEP", "x4", "y4", "red", "black");

    addScatterWithColorBar("NPHI", "RHOB", "x3", "y5");

    addTrace("VCLGR", "x7", "y", "red");
    addTrace("VCLND", "x7", "y", "green");
    addTrace("VCLSP", "x7", "y", "blue");

    var layout = {
        height: 2000,
        showlegend: false,
        yaxis: {
            title: {
                text: `MD (${columnData['MD']?.unit || ''})`,
            },
            autorange: 'reversed',
            domain: [0, 0.975],
            zeroline: false
        },
        yaxis2: {
            title: {
                text: `Frequency`,
            },
            domain: [0.7688, 1],
            position: 0.345
        },
        yaxis3: {
            title: {
                text: `Frequency`,
            },
            domain: [0.5125, 0.7438],
            position: 0.345
        },
        yaxis4: {
            title: {
                text: `Frequency`,
            },
            domain: [0.2563, 0.4875],
            position: 0.345
        },
        yaxis5: {
            title: {
                text: `RHOB (${columnData['RHOB']?.unit || ''})`,
            },
            autorange: 'reversed',
            domain: [0, 0.2313],
            position: 0.345,
            zeroline: false
        },
        xaxis: {
            title: {
                text: `SP (${columnData['SP']?.unit || ''})`,
                standoff: 1
            },
            domain: [0, 0.3],
            side: 'top',
            automargin: 'true',
            range: columnData['SP']?.limits,
            zeroline: false
        },
        xaxis2: {
            title: {
                text: `GR (${columnData['GR']?.unit || ''})`,
                font: {color: 'blue'},
                standoff: 1
            },
            tickfont: {color: 'blue'},
            domain: [0, 0.3],
            overlaying: 'x',
            side: 'top',
            position: 1,
            automargin: 'true',
            range: columnData['GR']?.limits,
            zeroline: false
        },
        xaxis3: {
            title: {
                text: `NPHI (${columnData['NPHI']?.unit || ''})`,
                standoff: 1
            },
            domain: [0.35, 0.65],
            side: 'bottom',
            position: 0,
            automargin: 'true',
            zeroline: false
        },
        xaxis4: {
            title: {
                text: `RDEEP (${columnData['RDEEP']?.unit || ''})`,
                standoff: 1
            },
            domain: [0.35, 0.65],
            side: 'bottom',
            position: 0.2563,
            automargin: 'true'
        },
        xaxis5: {
            title: {
                text: `SP (${columnData['SP']?.unit || ''})`,
                standoff: 1
            },
            domain: [0.35, 0.65],
            side: 'bottom',
            position: 0.5125,
            automargin: 'true',
        },
        xaxis6: {
            title: {
                text: `GR (${columnData['GR']?.unit || ''})`,
                standoff: 1
            },
            domain: [0.35, 0.65],
            side: 'bottom',
            position: 0.7688,
            automargin: 'true',
        },
        xaxis7: {
            title: {
                text: `VCL (${columnData['VCL']?.unit || ''})`,
                standoff: 1
            },
            domain: [0.7, 1],
            side: 'top',
            automargin: 'true',
            range: columnData['VCL']?.limits,
            zeroline: false
        },
    };

    Plotly.newPlot('vclPlotly', data, layout);

}

function comparisonPlot(dfLasJson, columnDataJson, kontol) {
    const dfLas = JSON.parse(dfLasJson);
    const columnData = JSON.parse(columnDataJson);

    const type = kontol;

    const data = [];
    
    // Helper function to add traces only if the column exists
    const addTrace = (columnName, xaxis, yaxis, lineColor = null, titleColor = null) => {
        if (dfLas[columnName]) {
            data.push({
                x: dfLas[columnName],
                y: dfLas["MD"],
                type: 'scatter',
                xaxis: xaxis,
                yaxis: yaxis,
                name: columnName,
                line: {color: lineColor},
                ...(titleColor && { marker: { color: titleColor } }) // Optional: apply color if provided
            });
        }
    };

    for (let i in dfLas) {
        if (i.startsWith(type)) {
            addTrace(i, "x", "y");
        }
    }

    var layout = {
        height: 3000,
        yaxis: {
            title: {
                text: `MD (${columnData['MD']?.unit || ''})`,
            },
            autorange: 'reversed',
        },
        xaxis: {
            title: {
                text: `${type} (${columnData[type]?.unit || ''})`,
                standoff: 1
            },
            side: 'top',
            automargin: 'true',
            range: columnData[type]?.limits,
            zeroline: false
        },
    };

    const plotId = `compare${type}Plotly`;

    console.log(plotId);

    Plotly.newPlot(plotId, data, layout);
}

function pickettPlot(dfLasJson, columnDataJson, vclLimit, zAxis, a, rw, m, n) {
    const dfLas = JSON.parse(dfLasJson);
    const columnData = JSON.parse(columnDataJson);

    const vclLim = vclLimit;

    const filteredIndices = dfLas["VCL"]
    .map((value, index) => (value < vclLim ? index : null)) // Mark indices where condition is met
    .filter(index => index !== null); // Remove null values

    // Filter other columns using the filtered indices
    const filteredDfLas = {};
    Object.keys(dfLas).forEach(column => {
        filteredDfLas[column] = filteredIndices.map(index => dfLas[column][index]);
    });

    const colZ = zAxis;

    const a_value = a;
    const rw_value = rw;
    const m_value = m;
    const n_value = n;

    const data = [];
    
    const addPickettPlot = (columnNameX, columnNameY, columnNameZ, a, rw, m, n, xaxis, yaxis, titleColor = null) => {
        // Check if the columns exist in dfLas
        if (filteredDfLas[columnNameX] && filteredDfLas[columnNameY] && filteredDfLas[columnNameZ]) {
            // Add the main scatter plot data
            data.push({
                x: filteredDfLas[columnNameX],
                y: filteredDfLas[columnNameY],
                type: "scatter",
                mode: "markers",
                xaxis: xaxis,
                yaxis: yaxis,
                type: "log",
                name: "Pickett",
                marker: {
                    color: filteredDfLas[columnNameZ],
                    colorscale: "Viridis",
                    showscale: true,
                    colorbar: {
                        title: `${columnNameZ} (${columnData[columnNameZ]?.unit || ''})`,
                    }
                },
                ...(titleColor && { marker: { color: titleColor } }) // Optional: apply color if provided
            });
        }

        const swPlot = [1.0, 0.8, 0.6, 0.4, 0.2];
        const phiePlot = [0.01, 1]; 

        swPlot.forEach(sw => {
            const rtValues = phiePlot.map(phie => {
                return (a * rw) / (Math.pow(sw, n) * Math.pow(phie, m));
            });
        
            // Add each SW curve as a line to the data
            data.push({
                x: rtValues, // Rt values
                y: phiePlot, // Porosity values
                xaxis: xaxis,
                yaxis: yaxis,
                type: "scatter",
                mode: "lines",
                name: `SW ${Math.round(sw * 100)}%`,
                line: {
                    width: 2
                }
            });
        });
        
    };

    let colX;

    if ("RT" in filteredDfLas) {
        colX = "RT";
    }
    else if ("RDEEP" in filteredDfLas) {
        colX = "RDEEP";
    }
    else if ("RMED" in filteredDfLas) {
        colX = "RMED";
    }
    else {
        colX = "RSHAL";
    }

    addPickettPlot(colX, "PHIE", colZ, a_value, rw_value, m_value, n_value, "x", "y")

    var layout = {
        height: 1000,
        showlegend: false,
        yaxis: {
            title: {
                text: `PHIE (${columnData['PHIE']?.unit || ''})`,
                standoff: 1
            },
            automargin: 'true',
            zeroline: false,
            type: 'log',
            range: [-2, 0]
        },
        xaxis: {
            title: {
                text: `${colX} (${columnData[colX]?.unit || ''})`,
                standoff: 1
            },
            automargin: 'true',
            zeroline: false,
            type: 'log',
            range: [-1, 3]
        },
    };

    Plotly.newPlot("pickettPlotly", data, layout);
}

function cutoffPlot(dfLasJson, columnDataJson, vclCutoff, phiCutoff, swCutoff) {
    const dfLas = JSON.parse(dfLasJson);
    const columnData = JSON.parse(columnDataJson);

    console.log(dfLas["SN"])

    const vclCut = vclCutoff;
    const phiCut = phiCutoff;
    const swCut = swCutoff;

    const data = [];
    
    const addcutoffPlot = (columnNameX, columnNameY, xCut, yCut, xaxis, yaxis, titleColor = null) => {
        // Check if the columns exist in dfLas
        if (dfLas[columnNameX] && dfLas[columnNameY] && dfLas["GR"]) {
            // Add the main scatter plot data
            data.push({
                x: dfLas[columnNameX],
                y: dfLas[columnNameY],
                type: "scatter",
                mode: "markers",
                xaxis: xaxis,
                yaxis: yaxis,
                name: `${columnNameX}_${columnNameY}`,
                marker: {
                    color: dfLas["GR"],
                    colorscale: "Viridis",
                    showscale: true,
                    colorbar: {
                        title: `GR (${columnData["GR"]?.unit || ''})`,
                    },
                },
                ...(titleColor && { marker: { color: titleColor } }) // Optional: apply color if provided
            });
    
            // Add the xCut line
            data.push({
                x: [xCut, xCut],
                y: [0, 1],
                type: "scatter",
                mode: "lines",
                line: {
                    color: "black",
                    dash: "dash",
                    width: 2,
                },
                name: `${columnNameX} = ${xCut}`,
                xaxis: xaxis,
                yaxis: yaxis,
            });
    
            // Add the yCut line
            data.push({
                x: [0, 1],
                y: [yCut, yCut],
                type: "scatter",
                mode: "lines",
                line: {
                    color: "black",
                    dash: "dash",
                    width: 2,
                },
                name: `${columnNameY} = ${yCut}`,
                xaxis: xaxis,
                yaxis: yaxis,
            });

            let xLim, yLim;

            if (columnNameX == "SW") {
                xLim = [0, xCut, xCut, 0];
                yLim = [0, 0, yCut, yCut];
            }

            else if (columnNameX == "VCL") {
                xLim = [0, xCut, xCut, 0];
                yLim = [1, 1, yCut, yCut];
            }
    
            // Add the filled area below xCut and yCut
            data.push({
                x: xLim,
                y: yLim,
                type: "scatter",
                fill: "toself",
                fillcolor: "rgba(0, 0, 0, 0.1)", // Light black/gray fill
                line: {
                    color: "rgba(0,0,0,0)", // No border for the filled area
                },
                name: "Shaded Area",
                xaxis: xaxis,
                yaxis: yaxis,
            });
        }
    };

    addcutoffPlot("SW", "VCL", swCut, vclCut, "x", "y");
    addcutoffPlot("VCL", "PHIE", vclCut, phiCut, "x2", "y2");

    var layout = {
        height: 1000,
        showlegend: false,
        yaxis: {
            title: {
                text: `VCL (${columnData["VCL"]?.unit || ''})`,
                standoff: 1
            },
            automargin: 'true',
            zeroline: false,
            range: [0, 1],
            position: 0
        },
        xaxis: {
            title: {
                text: `SW (${columnData["SW"]?.unit || ''})`,
                standoff: 1
            },
            automargin: 'true',
            zeroline: false,
            range: [0, 1],
            domain: [0, 0.475]
        },
        yaxis2: {
            title: {
                text: `PHIE (${columnData["PHIE"]?.unit || ''})`,
                standoff: 1
            },
            automargin: 'true',
            zeroline: false,
            range: [0, 1],
            position: 0.525
        },
        xaxis2: {
            title: {
                text: `VCL (${columnData["VCL"]?.unit || ''})`,
                standoff: 1
            },
            automargin: 'true',
            zeroline: false,
            range: [0, 1],
            domain: [0.525, 1]
        },
    };

    Plotly.newPlot("cutoffPlotly", data, layout);
}