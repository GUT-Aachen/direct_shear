import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import numpy as np
import plotly.graph_objs as go
import pandas as pd
import os

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

app.title = 'Direct Shear'
app._favicon = ('assets/favicon.ico')

# Updated layout with sliders on top and layer properties below
app.layout = html.Div([
    # Main container
    html.Div(style={'display': 'flex', 'flexDirection': 'row', 'width': '100%', 'height': '100vh'}, children=[
        # Control container (sliders)
        html.Div(id='control-container', style={'width': '25%', 'padding': '2%', 'flexDirection': 'column'}, children=[
            html.H1('Direct Shear', className='h1'),

        # Animation container
        html.Div(className='dropdown-container', children=[
            html.Label('Animation control', className='slider-label'),
            html.Label('Soil Type:', className='dropdown-label'),
            dcc.Checklist(
                id='soil-type-checklist',
                options=[
                    {'label': 'Dense Sand / OC Clay', 'value': 'dense'},
                    {'label': 'Loose Sand / NC Clay', 'value': 'loose'},
                ],
                value=['dense'],  # Default selected option
                # inline=True,  # Display options inline
            ),
            html.Label('Normal Stresses:', className='dropdown-label'),
            dcc.Checklist(
                id='normal-stress-checklist',
                options=[
                    {'label': html.Span(['σ', html.Sub('n-1')]), 'value': 'sigma_n1'},
                    {'label': html.Span(['σ', html.Sub('n-2')]), 'value': 'sigma_n2'},
                    {'label': html.Span(['σ', html.Sub('n-3')]), 'value': 'sigma_n3'}
                ],
                value=['sigma_n2'],  # Default selected option
                # inline=True,  # Display options inline
            ),
                # Control buttons for animation
            html.Button('Start', id='start-button'),
            html.Button('Pause', id='pause-button'),
            html.Button('Reset', id='reset-button'),  
        ]),

        # Sliders for each layer
        html.Div(className='slider-container', children=[
            # Normal stress1 slider
            html.Label(children=[
                "σ" , html.Sub('n-1'), " (kPa)", 
                        html.Div(className='tooltip', children=[
                            html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                            html.Span('Normal stress 1', className='tooltiptext')
                        ])], className='slider-label'),
            dcc.Slider(
                id='normal-stress-1', min=0, max=300, step=1, value=50,
                marks={i: f'{i}' for i in range(0, 301, 100)},
                className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
            ),
            # Normal stress 2 slider
            html.Label(children=[
                "σ" , html.Sub('n-2'), " (kPa)", 
                        html.Div(className='tooltip', children=[
                            html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                            html.Span('Normal stress 2', className='tooltiptext')
                        ])], className='slider-label'),
            dcc.Slider(
                id='normal-stress-2', min=0, max=300, step=1, value=100,
                marks={i: f'{i}' for i in range(0, 301, 100)},
                className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
            ),
            # Normal stress 3 slider
            html.Label(children=[
                "σ" , html.Sub('n-3'), " (kPa)", 
                        html.Div(className='tooltip', children=[
                            html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                            html.Span('Normal stress 3', className='tooltiptext')
                        ])], className='slider-label'),
            dcc.Slider(
                id='normal-stress-3', min=0, max=300, step=1, value=200,
                marks={i: f'{i}' for i in range(0, 301, 100)},
                className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
            ),
            # Friction angle slider
            html.Label(children=[
                "φ (degrees)", 
                        html.Div(className='tooltip', children=[
                            html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                            html.Span('Friction Angle', className='tooltiptext')
                        ])], className='slider-label'),
            dcc.Slider(
                id='friction-angle', min=0, max=50, step=1, value=30,
                marks={i: f'{i}' for i in range(0, 51, 10)},
                className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
            ),
            # Cohesion slider
            html.Label(children=[
                "c (kPa)", 
                        html.Div(className='tooltip', children=[
                            html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                            html.Span('Cohesion', className='tooltiptext')
                        ])], className='slider-label'),
            dcc.Slider(
                id='cohesion', min=0, max=300, step=1, value=0,
                marks={i: f'{i}' for i in range(0, 301, 100)},
                className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
            ),
            
        ]),

    ]),  # End of control container

    # Right-side: Graphs and shear box animation
    html.Div(
        className='graph-container', 
        style={'display': 'flex', 'flexDirection': 'column', 'height': '100vh', 'width': '75%'}, 
        children=[
            # First row: Shear box and Stress-Strain Graph
            html.Div(
                style={'display': 'flex', 'width': '100%', 'height': '50%'}, 
                children=[
                    html.Div(
                        style={'width': '50%', 'height': '100%'}, 
                        children=[
                            dcc.Graph(id='shear-box-graph', style={'height': '100%', 'width': '100%'})
                        ]
                    ),
                    html.Div(
                        style={'width': '50%', 'height': '100%'}, 
                        children=[
                            dcc.Graph(id='stress-strain-graph', style={'height': '100%', 'width': '100%'})
                        ]
                    ),
                ]
            ),
            # Second row: Height Change and Mohr-Coulomb Graph
            html.Div(
                style={'display': 'flex', 'width': '100%', 'height': '50%'}, 
                children=[
                    html.Div(
                        style={'width': '50%', 'height': '100%'}, 
                        children=[
                            dcc.Graph(id='mohr-coulomb-graph', style={'height': '100%', 'width': '100%'})
                        ]
                    ),
                    html.Div(
                        style={'width': '50%', 'height': '100%'}, 
                        children=[
                            dcc.Graph(id='height-change-graph', style={'height': '100%', 'width': '100%'})
                        ]
                    ),
                ]
            ),
        ]
    ),


    # Interval component for animation
    dcc.Interval(id='interval-component', interval=500, n_intervals=0, disabled=True),

    # Add the logo image to the top left corner
    html.Img(
        src='/assets/logo.png', className='logo',
        style={
            'position': 'absolute',
            'width': '15%',  # Adjust size as needed
            'height': 'auto',
            'z-index': '1000',  # Ensure it's on top of other elements
        }
    ),
    ])  # End of main container
])



# Store the state of the animation (whether it's running or not)
animation_running = False
shear_displacement = np.linspace(0, 80, 81)
shear_strain = shear_displacement / 100
shear_stress = np.zeros_like(shear_strain)
height_change = np.zeros_like(shear_strain)  # Initialize height_change
max_steps = len(shear_strain)
current_step = 0  # Keep track of the current step

# Callback to handle the animations and input updates
@app.callback(
    [Output('stress-strain-graph', 'figure'),
     Output('height-change-graph', 'figure'),
     Output('mohr-coulomb-graph', 'figure'),
     Output('shear-box-graph', 'figure'),
     Output('interval-component', 'disabled')],
    [Input('interval-component', 'n_intervals'),
     Input('soil-type-checklist', 'value'),  
     Input('normal-stress-checklist', 'value'),
     Input('normal-stress-1', 'value'),
     Input('normal-stress-2', 'value'),
     Input('normal-stress-3', 'value'),
     Input('cohesion', 'value'),
     Input('friction-angle', 'value'),
     Input('start-button', 'n_clicks'),
     Input('pause-button', 'n_clicks'),
     Input('reset-button', 'n_clicks')],
    [State('interval-component', 'disabled'),
     State('stress-strain-graph', 'figure'),
     State('height-change-graph', 'figure')]
)
def update_graphs(n, soil_types, normal_stresses, normal_stress_1, normal_stress_2, normal_stress_3, 
                  cohesion, friction_angle, start_clicks, pause_clicks, reset_clicks, 
                  interval_disabled, stress_strain_fig, height_change_fig):
    global animation_running, current_step, shear_displacement, shear_strain

    # Initialize figures if None
    # Convert figures from dict to go.Figure
    if not isinstance(stress_strain_fig, go.Figure):
        stress_strain_fig = go.Figure(stress_strain_fig)
    if not isinstance(height_change_fig, go.Figure):
        height_change_fig = go.Figure(height_change_fig)
    shear_box_fig = go.Figure()  # Always reset shear box figure
    mohr_fig = go.Figure()

    # Handle button clicks
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    if trigger_id == 'reset-button':
        current_step = 0
        animation_running = False
        return stress_strain_fig, height_change_fig,  mohr_fig, shear_box_fig,True

    if trigger_id == 'pause-button':
        animation_running = False
        # return stress_strain_fig, height_change_fig,  mohr_fig, shear_box_fig,True

    if trigger_id == 'start-button':
        animation_running = True
        interval_disabled = False
    
    # Update animation step
    if animation_running:
        current_step = min(current_step + 1, len(shear_displacement) - 1)
    
    # Map normal stresses to their slider values
    normal_stress_map = {
        'sigma_n1': normal_stress_1,
        'sigma_n2': normal_stress_2,
        'sigma_n3': normal_stress_3
    }


    # Define a color map for normal stresses
    stress_colors = {
        'sigma_n1': 'blue',  # Assign a unique color for sigma_n1
        'sigma_n2': 'green', # Assign a unique color for sigma_n2
        'sigma_n3': 'red'    # Assign a unique color for sigma_n3
    }

    # define legend names map 
    legend_names = {
        'sigma_n1': 'σ<sub>n-1</sub>',
        'sigma_n2': 'σ<sub>n-2</sub>',
        'sigma_n3': 'σ<sub>n-3</sub>'
    }

    # Function to create graphs (unchanged)
    def create_graphs(soil_t, normal_stress):
        shear_stress = np.zeros_like(shear_strain)
        height_change = np.zeros_like(shear_strain)
        if soil_t == 'dense':
            # Shear stress calculation for dense soil
            for i, strain in enumerate(shear_strain):
                if strain < 0.19:
                    s_y0 = (normal_stress / 100) * 1.16
                    s_A = -s_y0
                    s_R0 = -8.8
                    shear_stress[i] = s_y0 + s_A * np.exp(s_R0 * strain)
                else:
                    s_y0 = (normal_stress / 100) * 0.65
                    s_A1 = -s_y0 * 100
                    s_t1 = 0.09
                    s_A2 = -s_A1 * 0.9
                    s_t2 = s_t1 * 1.072
                    shear_stress[i] = s_y0 + s_A1 * np.exp(-strain / s_t1) + s_A2 * np.exp(-strain / s_t2)

            # Height change calculation for dense soil
            for i, strain in enumerate(shear_strain):
                    v_A = -0.6 * (normal_stress / 100) **0.01 # Amplitude
                    v_w = 0.327 * (normal_stress / 100) ** 0.2  # Width
                    if normal_stress > 100:
                        v_xc = 0.084 * (normal_stress / 100) ** 0.6 # Center
                    else:
                        v_xc = 0.084 * (normal_stress / 100) ** 0.8 # Center
                    v_y0 = -v_A / (v_w * np.sqrt(np.pi / (4 * np.log(2)))) * np.exp(-4 * np.log(2) * (0 - v_xc) ** 2 / v_w ** 2)

                    # Add a steepness control term for the upper half
                    height_change[i] = v_y0 + v_A / (v_w * np.sqrt(np.pi / (4 * np.log(2)))) * np.exp(
                        -4 * np.log(2) * (strain - v_xc)**2 / (v_w**2)
                    )

        elif soil_t == 'loose':
            # Shear stress calculation for loose soil
            for i, strain in enumerate(shear_strain):
                s_y0 = (normal_stress / 100) * 0.65
                s_A = -s_y0
                s_R0 = -3.107
                shear_stress[i] = s_y0 + s_A * np.exp(s_R0 * strain)

            # Height change calculation for loose soil
            for i, strain in enumerate(shear_strain):
                v_y0 = -(normal_stress / 100) * 0.81
                v_A = -v_y0
                v_R0 = -3.9
                height_change[i] = v_y0 + v_A * np.exp(v_R0 * strain)

        return shear_stress, height_change

    # Remove deselected traces
    selected_stresses = set(normal_stresses)
    stress_strain_fig.data = [
        trace for trace in stress_strain_fig.data
        if trace.name in selected_stresses
    ]
    height_change_fig.data = [
        trace for trace in height_change_fig.data
        if trace.name in selected_stresses
    ]

    # Generate new data for selected soil types and stresses
    for soil_type in soil_types:
        for stress_label in normal_stresses:
            normal_stress = normal_stress_map[stress_label]

            # Use the `create_graphs` function to calculate data
            shear_stress, height_change = create_graphs(soil_type, normal_stress)

            # Set line style based on soil type
            line_style = 'solid' if soil_type == 'dense' else 'dash'

            # Add traces to the stress-strain graph
            stress_strain_fig.add_trace(go.Scatter(
                x=shear_strain[:current_step],
                y=shear_stress[:current_step],
                mode='lines',
                line=dict(width=3, dash=line_style, color=stress_colors[stress_label]),  # Apply color and line style
                name=f'{legend_names[stress_label]} ({soil_type})',
                hoverinfo='none'
            ))

            # Add traces to the height-change graph
            height_change_fig.add_trace(go.Scatter(
                x=shear_strain[:current_step],
                y=height_change[:current_step],
                mode='lines',
                line=dict(width=3, dash=line_style, color=stress_colors[stress_label]),  # Apply color and line style
                name=f'{legend_names[stress_label]} ({soil_type})',
                hoverinfo='none'
            ))
            # add trace for "P" at the peak stress
            if (shear_stress[:current_step] == shear_stress.max()).any():
                stress_strain_fig.add_trace(go.Scatter(
                    x=[shear_strain[np.argmax(shear_stress)]],
                    y=[np.max(shear_stress)],
                    mode='markers+text',  # Enable both markers and text
                    marker=dict(color='black', size=10),
                    text=['P'],  # Add text
                    textposition="top center",  # Position the text relative to the marker
                    showlegend=False,
                    hoverinfo='none'
                ))
                # Adding a scatter point for corresponding height change in height change figure
                height_change_fig.add_trace(go.Scatter(
                    x=[shear_strain[np.argmax(shear_stress)]], 
                    y=[height_change[np.argmax(shear_stress)]], 
                    mode='markers+text',  # Enable both markers and text
                    marker=dict(color='black', size=10),
                    text=['P'],  # Add text
                    textposition="top center",  # Position the text relative to the marker
                    showlegend=False,
                    hoverinfo='none'
                ))
            # add 'CS' at the critical state at the end of the graph
            if current_step == max_steps - 1:
                stress_strain_fig.add_trace(go.Scatter(
                    x=[shear_strain[-1]],
                    y=[shear_stress[-1]],
                    mode='markers+text',  # Enable both markers and text
                    marker=dict(color='black', size=10),
                    text=['CS'],  # Add text
                    textposition="top center",  # Position the text relative to the marker
                    showlegend=False,
                    hoverinfo='none'
                ))
                # Adding a scatter point for corresponding height change in height change figure
                height_change_fig.add_trace(go.Scatter(
                    x=[shear_strain[-1]], 
                    y=[height_change[-1]], 
                    mode='markers+text',  # Enable both markers and text
                    marker=dict(color='black', size=10),
                    text=['CS'],  # Add text
                    textposition="top center",  # Position the text relative to the marker
                    showlegend=False,
                    hoverinfo='none'
                ))


    # Mohr-Coulomb Failure Envelope
    normal_stresses = [normal_stress_1, normal_stress_2, normal_stress_3]
    peak_stresses= [cohesion + sigma * np.tan(np.radians(friction_angle)) for sigma in normal_stresses] 



    # Add the shear stress points as red markers
    mohr_fig.add_trace(go.Scatter(
        x=normal_stresses,
        y=peak_stresses,
        mode='markers',
        marker=dict(color='red', size=10),
        name='Stress Points',
        showlegend=False
    ))

    # Add the failure envelope line starting from the cohesion value
    mohr_fig.add_trace(go.Scatter(
        x=[0, max(normal_stresses)],
        y=[cohesion, cohesion + max(normal_stresses) * np.tan(np.radians(friction_angle))],
        mode='lines',
        line=dict(color='black', width=3),
        name='Failure Envelope'
    ))

    # adding annotation for the equation of shear stress
    mohr_fig.add_annotation(
        x=min(normal_stresses), y=max(peak_stresses),
        xref='x', yref='y',
        text=f'τ = c + σ tan(φ)',
        showarrow=False,
        font=dict(family="Times New Roman, Arial, sans-serif", size=20, color="black", weight="bold"),
    )

    # Update the layout of the figure
    mohr_fig.update_layout(
        title=dict(
            text='Mohr-Coulomb Failure Envelope',
            font=dict(family="Arial, sans-serif", size=16, color="black", weight="bold", style="italic"),
        ),
        font=dict(family="Times New Roman, Arial, sans-serif", size=16, color="black", weight="bold"),
        xaxis_title='Normal Stress, 	σ<sub>n</sub> (kPa)',
        yaxis_title='Shear Stress, τ (kPa)',
        xaxis=dict(
            range=[0, max(normal_stresses) * 1.2],
            title_standoff=4,
            zeroline=False,
            showticklabels=True,
            ticks='outside',
            ticklen=5,
            minor_ticks="inside",
            showline=True,
            linewidth=2,
            linecolor='black',
            showgrid=False,
            gridwidth=1,
            gridcolor='lightgrey',
            mirror=True,
            hoverformat=".2f"  # Sets hover value format for x-axis to two decimal places
        ),
        yaxis=dict(
            range=[0, max(peak_stresses) * 1.2],
            zeroline=True,
            zerolinecolor= "black",
            title_standoff=4,
            showticklabels=True,
            ticks='outside',
            ticklen=5,
            minor_ticks="inside",
            showline=True,
            linewidth=2,
            linecolor='black',
            showgrid=False,
            gridwidth=1,
            gridcolor='lightgrey',
            mirror=True,
            hoverformat=".3f"  # Sets hover value format for y-axis to two decimal places
        ),
        legend=dict(
            yanchor="top",  # Align the bottom of the legend box
            y=0.1,               # Position the legend at the bottom inside the plot
            xanchor="right",    # Align the right edge of the legend box
            x=1,               # Position the legend at the right inside the plot
            font= dict(size=12),  # Adjust font size
            bgcolor="rgba(255, 255, 255, 0.7)",  # Optional: Semi-transparent white background
            bordercolor="black",                 # Optional: Border color
            borderwidth=1                        # Optional: Border width
        ),
        margin=dict( r=40, t=40),
    )

    # Shear box movement
    displacement = shear_displacement[current_step] * 0.1
    

    # Original position of the lower box (dashed border)
    shear_box_fig.add_trace(go.Scatter(
        x=[0+displacement, 0, 0, displacement],
        y=[0, 0, 10, 10],
        mode='lines',
        line=dict(color='black', width=1, dash='dash'),
        hoverinfo='none'
    ))


    # Lower shear box (moves right with shear displacement)
    shear_box_fig.add_shape(
        type="rect",
        x0=10+displacement, y0=2, x1=90+displacement, y1=10,
        fillcolor="rgb(236,204,162)",
        line=dict(color="rgba(0,0,0,0)"),  # Make the border transparent
        
    )

    # Upper shear box (fixed position)
    shear_box_fig.add_shape(
        type="rect",
        x0=10, y0=10, x1=90, y1=18,
        fillcolor="rgb(236,204,162)",
        line=dict(color="rgba(0,0,0,0)"),  # Make the border transparent
        
    )

    # Add the shear box outline left_upp
    shear_box_fig.add_trace(go.Scatter(
        x=[0, 10, 10, 0, 0],
        y=[10.2, 10.2, 20, 20, 10.2],
        mode='lines',
        line=dict(color='black', width=1),  # Border color and width
        fill='toself',  # Fill the enclosed area
        fillpattern=dict(
            shape="/",  # Pattern shape ('/', '\', '|', '-', '+', 'x', etc.)
            bgcolor='white',  # Background color of the pattern
            fgcolor='black',  # Foreground color of the pattern
            size=5,  # Pattern size
            solidity=0.5  # Pattern transparency
        ),
        hoverinfo='none'
    ))

    # Add the shear box outline left_down
    shear_box_fig.add_trace(go.Scatter(
        x=[0+displacement, 10+displacement, 10+displacement, 0+displacement, 0+displacement],
        y=[0, 0, 9.8, 9.8, 0],
        mode='lines',
        line=dict(color='black', width=1),  # Border color and width
        fill='toself',  # Fill the enclosed area
        fillpattern=dict(
            shape="/",  # Pattern shape ('/', '\', '|', '-', '+', 'x', etc.)
            bgcolor='white',  # Background color of the pattern
            fgcolor='black',  # Foreground color of the pattern
            size=5,  # Pattern size
            solidity=0.5  # Pattern transparency
        ),
        hoverinfo='none'
    ))

    # Add the shear box outline right
    shear_box_fig.add_trace(go.Scatter
    (
        x=[100, 90, 90, 100, 100],
        y=[10.2, 10.2, 20, 20, 10.2],
        mode='lines',
        line=dict(color='black', width=1),
        fill='toself',
        fillpattern=dict(
            shape="/",
            bgcolor='white',
            fgcolor='black',
            size=5,
            solidity=0.5
        ),
        hoverinfo='none'
    ))

    # Add the shear box outline right
    shear_box_fig.add_trace(go.Scatter
    (
        x=[100+displacement, 90+displacement, 90+displacement, 100+displacement, 100+displacement],
        y=[0, 0, 9.8, 9.8, 0],
        mode='lines',
        line=dict(color='black', width=1),
        fill='toself',
        fillpattern=dict(
            shape="/",
            bgcolor='white',
            fgcolor='black',
            size=5,
            solidity=0.5
        ),
        hoverinfo='none'
    ))

    # Add prous stone down
    shear_box_fig.add_trace(go.Scatter
    (
        x=[10+displacement, 90+displacement, 90+displacement, 10+displacement, 10+displacement],
        y=[0, 0, 2, 2, 0],
        mode='lines',
        line=dict(color='black', width=1),
        fill='toself',
        fillpattern=dict(
            shape=".",
            bgcolor='lightgray',
            fgcolor='black',
            size=5,
            solidity=0.5
        ),
        hoverinfo='none'
    ))

    # Add prous stone upp
    shear_box_fig.add_trace(go.Scatter
    (
        x=[10, 90, 90, 10, 10],
        y=[18, 18, 20, 20, 18],
        mode='lines',
        line=dict(color='black', width=1),
        fill='toself',
        fillpattern=dict(
            shape=".",
            bgcolor='lightgray',
            fgcolor='black',
            size=5,
            solidity=0.5
        ),
        hoverinfo='none'
    ))

    # Adding shape top blatten
    shear_box_fig.add_trace(go.Scatter(
        x=[10, 90, 80, 20, 10],
        y=[20, 20, 23, 23, 20],
        mode='lines',
        line=dict(color='black', width=1),  # Border color and width
        fill='toself',  # Fill the enclosed area
        fillcolor='black',  # Solid black fill
        name='Shear Box'
    ))

    # Adding the circle at the top
    shear_box_fig.add_shape(
        type="circle",
        xref="x", yref="y",  # Use the same coordinate system as the Scatter trace
        x0=46, y0=22.5,  # Bottom-left corner of the bounding box
        x1=54, y1=23.5,  # Top-right corner of the bounding box
        line=dict(color="white", width=2),  # Circle border (white)
        fillcolor="black"  # Circle fill (black)
    )



    # Add an arrow showing the horizontal shear force
    shear_box_fig.add_annotation(
        x=0 + displacement,  y=5,
        ax=-40 + displacement, ay=5,
        xref="x", yref="y",
        axref="x", ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.5,
        arrowwidth=3,
        arrowcolor="red",
        text="Shear force",
        font=dict(family="Arial, sans-serif", size=16, color="red", weight="bold"),
    )

    # Add an arrow showing the normal stress (downward arrow)
    shear_box_fig.add_annotation(
        x=50 , y=23.5,
        ax=50 , ay=30,
        xref="x", yref="y",
        axref="x", ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.5,
        arrowwidth=3,
        arrowcolor="blue",
        text="Normal force",
        font=dict(family="Arial, sans-serif", size=16, color="blue", weight="bold"),
        valign="top"
    )

    # Update the layout of the figure
    shear_box_fig.update_layout(
        title='Shear Box Animation:',
        font=dict(family="Arial, sans-serif", size=14, color="black", weight="bold", style="italic"),
        plot_bgcolor='white',
        xaxis=dict(
            range=[-50, 150], 
            showticklabels=False,
            showgrid=False,
            title=None, 
            zeroline=False,
            fixedrange=True
            ),
        yaxis=dict(
            range=[-5, 30],
            showticklabels=False,
            showline = False,
            showgrid=False, 
            title=None,
            zeroline=False,
            fixedrange=True
            ),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    # Update the layout of the stress-strain graph
    stress_strain_fig.update_layout(
        plot_bgcolor='white',
        xaxis_title='Horizantal displacement (Shear strain)',     # Set the title for the x-axis
        yaxis_title='Shear stress',
        font=dict(family="Times New Roman, Arial, sans-serif", size=12, color="black", weight="bold"),
        xaxis=dict(
            range=[0, 1],  # Set the range for the x-axis
            mirror=True,           # Mirror the axes on all sides
            showline=True,         # Show the axes line
            linewidth=2,           # Set the width of the axes line
            linecolor = 'black',
            gridcolor='white',  # Set the gridline color
            showticklabels=False,
            zerolinecolor='black',  # Set zero line color
            fixedrange=True
        ),
        yaxis=dict(
            range=[0, 3.2],  # Set the range for the y-axis
            mirror=True,           # Mirror the axes on all sides
            showline=True,         # Show the axes line
            linewidth=2,           # Set the width of the axes line
            linecolor = 'black',
            showgrid=False,
            showticklabels=False,
            gridcolor='white',
            fixedrange=True
        ),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    # Update the layout of the height-change graph
    height_change_fig.update_layout(
        plot_bgcolor='white',
        xaxis_title='Horizontal displacement (Shear strain)',
        yaxis_title='Change in height (Volumetric strain)',
        font=dict(family="Times New Roman, Arial, sans-serif", size=10, color="black", weight="bold"),
        xaxis=dict(
            range=[0, 1],  # Set the range for the x-axis
            mirror=True,  # Mirror the axes on all sides
            showline=True,  # Show the axes line
            linewidth=2,  # Set the width of the axes line
            linecolor='black',
            gridcolor='white',  # Set the gridline color
            showticklabels=False,
            zeroline=True,
            zerolinecolor='black',  # Set zero line color for the vertical zeroline
            fixedrange=True
        ),
        yaxis=dict(
            range=[-3, 3],  # Set the range for the y-axis
            mirror=True,  # Mirror the axes on all sides
            showline=True,  # Show the axes line
            linewidth=2,  # Set the width of the axes line
            linecolor='black',
            showgrid=False,
            zeroline=True,  # Ensure the horizontal zero line is shown
            zerolinecolor='black',  # Set a visible color for the horizontal zero line
            zerolinewidth=2,  # Adjust the thickness of the horizontal zero line
            showticklabels=False,
            gridcolor='white',
            fixedrange=True
        ),
        margin=dict(l=40, r=40, t=40)
    )


    return stress_strain_fig, height_change_fig, mohr_fig, shear_box_fig, interval_disabled

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
    

# Expose the server
server = app.server

