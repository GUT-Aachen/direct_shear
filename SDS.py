import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import numpy as np
import plotly.graph_objs as go

app = dash.Dash(__name__)

# App layout with three normal stress inputs
app.layout = html.Div(style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'flex-start'}, children=[
    # Left-side control panel
    html.Div(style={'flex': '1', 'padding': '20px'}, children=[
        html.H1('Direct Shear Test Simulation'),

        # Dropdown for soil type selection
        html.Div(className='dropdown-container', children=[
            html.Label('Soil Type', className='dropdown-label'),
            dcc.Dropdown(
                id='soil-type-dropdown',
                options=[
                    {'label': 'Dense Sand / OC Clay', 'value': 'dense'},
                    {'label': 'Loose Sand / NC Clay', 'value': 'loose'}
                ],
                value='dense'  # Default to dense sand/OC clay
            ),
        ]),

        # Input for normal stress values (3 inputs)
        html.Div(className='input-container', children=[
            html.Label('Normal Stress 1 [kPa]', className='input-label'),
            dcc.Input(id='normal-stress-1', type='number', value=50, min=20, max=50),
            html.Label('Normal Stress 2 [kPa]', className='input-label'),
            dcc.Input(id='normal-stress-2', type='number', value=100, min=51, max=100),
            html.Label('Normal Stress 3 [kPa]', className='input-label'),
            dcc.Input(id='normal-stress-3', type='number', value=150, min=100, max=300)
        ]),

        # Sliders for cohesion and friction angle
        html.Div(className='slider-container', children=[
            html.Label('Cohesion [kPa]', className='slider-label'),
            dcc.Slider(
                id='cohesion-slider',
                min=0,
                max=100,
                step=1,
                value=25,
                marks={i: f'{i}' for i in range(0, 101, 25)},
                className='slider'
            ),
        ]),

        html.Div(className='slider-container', children=[
            html.Label('Friction Angle [degrees]', className='slider-label'),
            dcc.Slider(
                id='friction-angle-slider',
                min=0,
                max=45,
                step=1,
                value=30,
                marks={i: f'{i}' for i in range(0, 46, 15)},
                className='slider'
            ),
        ]),

        # Control buttons for animation
        html.Div(style={'display': 'flex', 'gap': '10px', 'marginTop': '20px'}, children=[
            html.Button('Start', id='start-button'),
            html.Button('Pause', id='pause-button'),
            html.Button('Reset', id='reset-button')
        ])
    ]),

    # Right-side: Graphs and shear box animation
    html.Div(className='graph-container', style={'flex': '2', 'padding': '20px'}, children=[
        # Graphs stacked vertically
        html.Div(style={'width': '100%', 'height': '50vh', 'marginBottom': '20px'}, children=[
            dcc.Graph(id='stress-strain-graph', style={'height': '100%', 'width': '100%'})
        ]),
        # Shear box animation at the bottom
        html.Div(style={'width': '100%', 'height': '50vh', 'marginTop': '20px'}, children=[
            dcc.Graph(id='shear-box-graph', style={'height': '100%', 'width': '100%'})
        ]),
        html.Div(style={'width': '100%', 'height': '50vh', 'marginBottom': '20px'}, children=[
            dcc.Graph(id='height-change-graph', style={'height': '100%', 'width': '100%'})
        ]),
        html.Div(style={'width': '100%', 'height': '50vh'}, children=[
            dcc.Graph(id='mohr-coulomb-graph', style={'height': '100%', 'width': '100%'})
        ]),
        # Interval component for animation
        dcc.Interval(id='interval-component', interval=100, n_intervals=0, disabled=True)
    ])
])



# Store the state of the animation (whether it's running or not)
animation_running = False
shear_displacement = np.linspace(0, 10, 100)
shear_strain = shear_displacement / 100
shear_stress = np.zeros(300)
height_change = np.zeros(100)  # Initialize height_change
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
     Input('soil-type-dropdown', 'value'),
     Input('normal-stress-1', 'value'),
     Input('normal-stress-2', 'value'),
     Input('normal-stress-3', 'value'),
     Input('cohesion-slider', 'value'),
     Input('friction-angle-slider', 'value'),
     Input('start-button', 'n_clicks'),
     Input('pause-button', 'n_clicks'),
     Input('reset-button', 'n_clicks')],
    [State('interval-component', 'disabled')]
)
def update_graphs(n, soil_type, normal_stress_1, normal_stress_2, normal_stress_3, cohesion, friction_angle, start_clicks, pause_clicks, reset_clicks, interval_disabled):
    global animation_running, current_step, shear_stress, height_change

    ## Ensure step size is valid
    step_size = max(1, n % 100)  # This ensures the graph updates step-by-step

     # Handle control buttons
    ctx = dash.callback_context
    if ctx.triggered:
        if 'start-button' in ctx.triggered[0]['prop_id']:
            animation_running = True
            interval_disabled = False
            if current_step >= max_steps:
                current_step = 0  # Restart from the beginning
        elif 'pause-button' in ctx.triggered[0]['prop_id']:
            animation_running = False
            interval_disabled = True
        elif 'reset-button' in ctx.triggered[0]['prop_id']:
            animation_running = False
            interval_disabled = True
            current_step = 0
            return go.Figure(), go.Figure(), go.Figure(), go.Figure(), True, 0  # Reset figures

    # Update the current step if the animation is running
    if animation_running:
        if current_step < max_steps:
            current_step += 1
        else:
            animation_running = False
            interval_disabled = True

    # Determine figures based on current_step
    if current_step >= max_steps:  # If at the last step, keep using the last computed data
        step_size = max_steps - 1  # Use max_steps - 1 to access the last valid index
    else:
        step_size = current_step
    # Stress-strain and height-change curves based on soil type
    if soil_type == 'dense':
    # Mohr-Coulomb Failure Envelope
        normal_stresses = [normal_stress_1, normal_stress_2, normal_stress_3]
        peak_stresses= [cohesion + sigma * np.tan(np.radians(friction_angle)) for sigma in normal_stresses] 

        shear_stress_1 = -16.1 +(38.78 - (-16.1)) *((-0.42225 / (1 + 10 ** ((0.03646 - shear_strain) * 72.78))) + ((1 - (-0.4225)) / (1 + 10 ** ((0.0075 - shear_strain) * 57.42))))
        shear_stress_2 = -30 +(38.78 - (-30)) *((-0.42225 / (1 + 10 ** ((0.03646 - shear_strain) * 72.78))) + ((1 - (-0.4225)) / (1 + 10 ** ((0.0075 - shear_strain) * 57.42))))
        shear_stress_3 = -16.1 +(38.78 - (-16.1)) *((-0.42225 / (1 + 10 ** ((0.03646 - shear_strain) * 72.78))) + ((1 - (-0.4225)) / (1 + 10 ** ((0.0075 - shear_strain) * 57.42))))


        height_change[:step_size] = np.piecewise(
            shear_strain[:step_size],
            [shear_strain[:step_size] <= 0.01, shear_strain[:step_size] > 0.01],
            [lambda s: -2 * s, lambda s: 2 * (s - 0.01)]
        )
    elif soil_type == 'loose':
        peak_stress = cohesion + normal_stress_1 * np.tan(np.radians(friction_angle))
        residual_stress = peak_stress  # No significant residual stress for loose soil
        # shear_stress[:step_size] = np.piecewise(
        #     shear_strain[:step_size],
        #     [shear_strain[:step_size] <= 0.8, shear_strain[:step_size] > 0.8],
        #     [lambda s: peak_stress * (s / 0.8), lambda s: peak_stress]
        # )

        # y = y0 +A*exp(R0*x)
        shear_stress_1 = 38.8 + (-39.35)*np.exp(-32.49*shear_strain)
        shear_stress_2 = 38.8 + (-39.35)*np.exp(-32.49*shear_strain)
        shear_stress_3 = 38.8 + (-39.35)*np.exp(-32.49*shear_strain)

        height_change[:step_size] = np.piecewise(
            shear_strain[:step_size],
            [shear_strain[:step_size] <= 0.8, shear_strain[:step_size] > 0.8],
            [lambda s: 2 * s, lambda s: 2 * s]
        )



    mohr_fig = go.Figure()

    # Add the shear stress points as red markers
    mohr_fig.add_trace(go.Scatter(
        x=normal_stresses,
        y=peak_stresses,
        mode='markers',
        marker=dict(color='red', size=10),
        name='Shear Stress Points'
    ))

    # Add the failure envelope line starting from the cohesion value
    mohr_fig.add_trace(go.Scatter(
        x=[0, max(normal_stresses)],
        y=[cohesion, cohesion + max(normal_stresses) * np.tan(np.radians(friction_angle))],
        mode='lines',
        line=dict(color='blue', width=2),
        name='Failure Envelope'
    ))

    # Update the layout of the figure
    mohr_fig.update_layout(
        title='Mohr-Coulomb Failure Envelope',
        xaxis_title='Normal Stress [kPa]',
        yaxis_title='Shear Stress [kPa]',
        xaxis=dict(range=[0, max(normal_stresses) * 1.2]),
        yaxis=dict(range=[0, max(peak_stresses) * 1.2]),
        showlegend=True
    )

     # Shear box movement
    shear_displacement = shear_strain[step_size] * 50
    shear_box_fig = go.Figure()

    # Original position of the upper box (dashed border)
    shear_box_fig.add_shape(
        type="rect",
        x0=0, y0=10, x1=100, y1=20,
        line=dict(dash='dash', color="black"),
        fillcolor="rgba(0,0,0,0)",
        layer="below"
    )

    # Lower shear box (fixed)
    shear_box_fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=100, y1=10,
        fillcolor="lightgray",
        line=dict(color="black"),
        layer="below"
    )

    # Upper shear box (moves right with shear displacement)
    shear_box_fig.add_shape(
        type="rect",
        x0=shear_displacement, y0=10, x1=100 + shear_displacement, y1=20,
        fillcolor="blue",
        line=dict(color="black"),
        layer="above"
    )

    # Add an arrow showing the horizontal shear force
    shear_box_fig.add_annotation(
        x=0 + shear_displacement,  y=15,
        ax=-25 + shear_displacement, ay=15,
        xref="x", yref="y",
        axref="x", ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.5,
        arrowwidth=2,
        arrowcolor="red",
        text="Horizantal Force"
    )

    # Add an arrow showing the normal stress (downward arrow)
    shear_box_fig.add_annotation(
        x=50 , y=20,
        ax=50 , ay=25,
        xref="x", yref="y",
        axref="x", ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.5,
        arrowwidth=2,
        arrowcolor="green",
        text="Normal Stress",
        valign="top"
    )

    # Update the layout of the figure
    shear_box_fig.update_layout(
        title='Shear Box Animation',
        plot_bgcolor='white',
        xaxis=dict(
            range=[-50, 150], 
            showticklabels=False,
            showgrid=False,
            title=None, 
            zeroline=False),
        yaxis=dict(
            range=[-5, 30],
            showticklabels=False,
            showline = False,
            showgrid=False, 
            title=None,
            zeroline=False),
        width=800,
        height=400,
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40)
    )


    # Create stress-strain figure for animation
    stress_strain_fig = go.Figure()
    stress_strain_fig.add_trace(go.Scatter(x=shear_strain[:step_size], y=shear_stress_1[:step_size], mode='lines', name=f'Normal Stress 1', hoverinfo='none'))
    stress_strain_fig.add_trace(go.Scatter(x=shear_strain[:step_size], y=shear_stress_2[:step_size], mode='lines', name=f'Normal Stress 2', hoverinfo='none'))
    stress_strain_fig.add_trace(go.Scatter(x=shear_strain[:step_size], y=shear_stress_3[:step_size], mode='lines', name=f'Normal Stress 3', hoverinfo='none'))
    stress_strain_fig.update_layout(
        plot_bgcolor='white',
        title='Stress-Strain Relationship',
        xaxis_title='Shear Strain',      # Set the title for the x-axis
        yaxis_title='Shear Stress',  # Set the title for the y-axis
        xaxis=dict(
            range=[0, shear_strain.max() + 0.05],  # Set the range for the x-axis
            mirror=True,           # Mirror the axes on all sides
            showline=True,         # Show the axes line
            linewidth=2,           # Set the width of the axes line
            linecolor = 'black',
            gridcolor='white',  # Set the gridline color
            showticklabels=False,
            zerolinecolor='black'  # Set zero line color
        ),
        yaxis=dict(
            range=[5, peak_stresses[2] + 20],  # Set the range for the y-axis
            mirror=True,           # Mirror the axes on all sides
            showline=True,         # Show the axes line
            linewidth=2,           # Set the width of the axes line
            linecolor = 'black',
            showgrid=False,
            showticklabels=False,
            gridcolor='white'
        ),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    # Create height-change figure for animation
    height_change_fig = go.Figure()
    height_change_fig.add_trace(go.Scatter(x=shear_strain[:step_size], y=height_change[:step_size], mode='lines', name='Height Change'))
    height_change_fig.update_layout(
        title='Height Change vs Shear Displacement',
        xaxis_title='Shear Displacement / Strain',
        yaxis_title='Change in Height',
        xaxis=dict(range=[0, shear_strain.max() + 0.02]),
        yaxis=dict(range=[- shear_strain.max() - 0.02, shear_strain.max() + 0.02])
    )

    return stress_strain_fig, height_change_fig, mohr_fig, shear_box_fig, interval_disabled

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
