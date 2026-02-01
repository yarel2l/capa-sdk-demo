"""
Plotly Charts Module
Interactive visualizations for CAPA Demo using Plotly.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import reflex as rx
from typing import Dict, List, Any, Optional


# =============================================================================
# THEME CONFIGURATION
# =============================================================================

# Dark theme colors matching the app's Slate/Orange palette
COLORS = {
    "primary": "#f97316",      # orange-500
    "primary_light": "#fb923c", # orange-400
    "secondary": "#fbbf24",    # amber-400
    "purple": "#a78bfa",       # violet-400
    "green": "#34d399",        # emerald-400
    "blue": "#60a5fa",         # blue-400
    "red": "#ef4444",          # red-500
    "slate_100": "#f1f5f9",
    "slate_200": "#e2e8f0",
    "slate_300": "#cbd5e1",
    "slate_400": "#94a3b8",
    "slate_500": "#64748b",
    "slate_600": "#475569",
    "slate_700": "#334155",
    "slate_800": "#1e293b",
    "slate_900": "#0f172a",
}

# Plotly colorway for consistent chart colors
COLORWAY = [
    COLORS["primary"],
    COLORS["purple"],
    COLORS["green"],
    COLORS["blue"],
    COLORS["secondary"],
    COLORS["red"],
]


def apply_dark_theme(fig: go.Figure, height: int = 300) -> go.Figure:
    """Apply dark theme consistent with app styling."""
    fig.update_layout(
        paper_bgcolor="rgba(30, 41, 59, 0.3)",  # slate-800/30
        plot_bgcolor="rgba(30, 41, 59, 0.1)",   # slate-800/10
        font=dict(
            color=COLORS["slate_300"],
            family="Inter, system-ui, sans-serif",
            size=12,
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        height=height,
        autosize=True,
        colorway=COLORWAY,
    )
    return fig


# =============================================================================
# WD ANALYSIS CHARTS
# =============================================================================

def create_personality_radar(data: List[Dict[str, Any]]) -> go.Figure:
    """
    Create radar chart for 8-dimension personality profile.

    Args:
        data: List of dicts with 'dimension' and 'value' keys
              Example: [{"dimension": "Social Orientation", "value": 0.7}, ...]

    Returns:
        Plotly Figure object
    """
    if not data or len(data) < 3:
        # Return empty figure if no data
        fig = go.Figure()
        fig.add_annotation(
            text="No personality data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=COLORS["slate_400"], size=14)
        )
        return apply_dark_theme(fig, height=350)

    categories = [d.get("dimension", "Unknown") for d in data]
    values = [float(d.get("value", 0)) for d in data]

    # Close the radar by repeating first value
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    # Add the radar trace
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor=f'rgba(249, 115, 22, 0.25)',  # orange-500/25
        line=dict(color=COLORS["primary"], width=2),
        marker=dict(size=8, color=COLORS["primary_light"]),
        name='Personality Profile',
        hovertemplate="<b>%{theta}</b><br>Score: %{r:.2f}<extra></extra>",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(size=10, color=COLORS["slate_500"]),
                gridcolor=f'rgba(100, 116, 139, 0.3)',
                linecolor=COLORS["slate_600"],
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color=COLORS["slate_300"]),
                gridcolor=f'rgba(100, 116, 139, 0.3)',
                linecolor=COLORS["slate_600"],
            ),
            bgcolor="rgba(30, 41, 59, 0.1)",
        ),
        showlegend=False,
        title=dict(
            text="Personality Profile",
            font=dict(size=14, color=COLORS["slate_100"]),
            x=0.5,
        ),
    )

    return apply_dark_theme(fig, height=350)


def create_demographic_gauge(percentile: float) -> go.Figure:
    """
    Create gauge chart for demographic percentile (0-100).

    Args:
        percentile: Value between 0 and 100

    Returns:
        Plotly Figure object
    """
    # Clamp value
    percentile = max(0, min(100, float(percentile)))

    # Determine color based on percentile range
    if percentile >= 75:
        bar_color = COLORS["blue"]
    elif percentile >= 50:
        bar_color = COLORS["green"]
    elif percentile >= 25:
        bar_color = COLORS["secondary"]
    else:
        bar_color = COLORS["red"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentile,
        domain={'x': [0.1, 0.9], 'y': [0.2, 1]},
        number={
            'suffix': "th",
            'font': {'size': 22, 'color': COLORS["slate_100"]},
            'valueformat': '.0f',
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickcolor': COLORS["slate_500"],
                'tickfont': {'color': COLORS["slate_400"], 'size': 9},
                'tickvals': [0, 50, 100],
            },
            'bar': {'color': bar_color, 'thickness': 0.7},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'borderwidth': 1,
            'bordercolor': COLORS["slate_600"],
            'steps': [
                {'range': [0, 25], 'color': 'rgba(239, 68, 68, 0.15)'},
                {'range': [25, 50], 'color': 'rgba(251, 191, 36, 0.15)'},
                {'range': [50, 75], 'color': 'rgba(52, 211, 153, 0.15)'},
                {'range': [75, 100], 'color': 'rgba(96, 165, 250, 0.15)'},
            ],
            'threshold': {
                'line': {'color': COLORS["slate_100"], 'width': 2},
                'thickness': 0.75,
                'value': percentile,
            },
        },
    ))

    fig.update_layout(
        margin=dict(l=30, r=30, t=10, b=0),
    )

    return apply_dark_theme(fig, height=140)


# =============================================================================
# FOREHEAD ANALYSIS CHARTS
# =============================================================================

def create_impulsivity_radar(profile_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Create radar chart for 8-dimension impulsivity profile (BIS-11).

    Args:
        profile_data: List of dicts with 'dimension' and 'value' keys
                      Dimensions: Motor, Attentional, Non-planning, Cognitive, etc.

    Returns:
        Plotly Figure object
    """
    if not profile_data or len(profile_data) < 3:
        fig = go.Figure()
        fig.add_annotation(
            text="No impulsivity data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=COLORS["slate_400"], size=14)
        )
        return apply_dark_theme(fig, height=350)

    categories = [d.get("dimension", "Unknown") for d in profile_data]
    values = [float(d.get("value", 0)) for d in profile_data]

    # Close the radar
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(167, 139, 250, 0.25)',  # purple/25
        line=dict(color=COLORS["purple"], width=2),
        marker=dict(size=8, color=COLORS["purple"]),
        name='Impulsivity Profile',
        hovertemplate="<b>%{theta}</b><br>Score: %{r:.2f}<extra></extra>",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(size=10, color=COLORS["slate_500"]),
                gridcolor='rgba(100, 116, 139, 0.3)',
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color=COLORS["slate_300"]),
                gridcolor='rgba(100, 116, 139, 0.3)',
            ),
            bgcolor="rgba(30, 41, 59, 0.1)",
        ),
        showlegend=False,
        title=dict(
            text="Impulsivity Profile (BIS-11)",
            font=dict(size=14, color=COLORS["slate_100"]),
            x=0.5,
        ),
    )

    return apply_dark_theme(fig, height=350)


def create_neuroscience_bar(correlations: List[Dict[str, Any]]) -> go.Figure:
    """
    Create horizontal bar chart for neuroscience correlations.

    Args:
        correlations: List of dicts with 'metric' and 'value' keys
                      Example: [{"metric": "Dopamine Activity", "value": 0.7}, ...]

    Returns:
        Plotly Figure object
    """
    if not correlations:
        fig = go.Figure()
        fig.add_annotation(
            text="No neuroscience data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=COLORS["slate_400"], size=14)
        )
        return apply_dark_theme(fig, height=280)

    metrics = [c.get("metric", "Unknown") for c in correlations]
    values = [float(c.get("value", 0)) for c in correlations]

    # Color coding by metric type
    colors = []
    for m in metrics:
        m_lower = m.lower()
        if "dopamine" in m_lower:
            colors.append(COLORS["purple"])
        elif "serotonin" in m_lower:
            colors.append(COLORS["blue"])
        elif "gaba" in m_lower:
            colors.append(COLORS["green"])
        elif "executive" in m_lower or "memory" in m_lower or "attention" in m_lower:
            colors.append(COLORS["secondary"])
        else:
            colors.append(COLORS["primary"])

    fig = go.Figure(go.Bar(
        x=values,
        y=metrics,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color=COLORS["slate_600"], width=1),
        ),
        text=[f"{v:.2f}" for v in values],
        textposition='outside',
        textfont=dict(color=COLORS["slate_300"], size=11),
        hovertemplate="<b>%{y}</b><br>Value: %{x:.3f}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(
            text="Neuroscience Correlations",
            font=dict(size=14, color=COLORS["slate_100"]),
        ),
        xaxis=dict(
            range=[0, 1.15],
            tickfont=dict(color=COLORS["slate_500"]),
            gridcolor='rgba(100, 116, 139, 0.2)',
            title=dict(text="Activity Level", font=dict(size=11, color=COLORS["slate_400"])),
        ),
        yaxis=dict(
            tickfont=dict(color=COLORS["slate_300"]),
            automargin=True,
        ),
        bargap=0.3,
    )

    return apply_dark_theme(fig, height=max(200, len(correlations) * 40 + 80))


# =============================================================================
# MORPHOLOGY ANALYSIS CHARTS
# =============================================================================

def create_face_shape_donut(probabilities: List[Dict[str, Any]]) -> go.Figure:
    """
    Create donut chart for face shape probabilities.

    Args:
        probabilities: List of dicts with 'shape' and 'probability' keys
                       Example: [{"shape": "Oval", "probability": 0.45}, ...]

    Returns:
        Plotly Figure object
    """
    if not probabilities:
        fig = go.Figure()
        fig.add_annotation(
            text="No shape data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=COLORS["slate_400"], size=14)
        )
        return apply_dark_theme(fig, height=300)

    # Sort by probability descending
    sorted_probs = sorted(probabilities, key=lambda x: x.get("probability", 0), reverse=True)

    labels = [p.get("shape", "Unknown") for p in sorted_probs]
    values = [float(p.get("probability", 0)) * 100 for p in sorted_probs]  # Convert to percentage

    # Custom colors
    donut_colors = [
        COLORS["primary"],
        COLORS["purple"],
        COLORS["green"],
        COLORS["blue"],
        COLORS["secondary"],
        COLORS["red"],
        COLORS["slate_400"],
        COLORS["slate_500"],
    ]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(
            colors=donut_colors[:len(labels)],
            line=dict(color=COLORS["slate_800"], width=2),
        ),
        textinfo='percent+label',
        textfont=dict(color=COLORS["slate_100"], size=11),
        textposition='outside',
        hovertemplate="<b>%{label}</b><br>Probability: %{percent}<extra></extra>",
        pull=[0.02 if i == 0 else 0 for i in range(len(labels))],  # Pull out top shape
    ))

    # Add center annotation
    if sorted_probs:
        top_shape = sorted_probs[0].get("shape", "N/A")
        fig.add_annotation(
            text=f"<b>{top_shape}</b>",
            x=0.5, y=0.5,
            font=dict(size=16, color=COLORS["slate_100"]),
            showarrow=False,
        )

    fig.update_layout(
        title=dict(
            text="Face Shape Distribution",
            font=dict(size=14, color=COLORS["slate_100"]),
        ),
        showlegend=False,
    )

    return apply_dark_theme(fig, height=320)


def create_proportions_bar(proportions: List[Dict[str, Any]]) -> go.Figure:
    """
    Create bar chart for facial proportions (upper/middle/lower face).

    Args:
        proportions: List of dicts with 'proportion' and 'value' keys
                     Example: [{"proportion": "Upper Face", "value": 0.33}, ...]

    Returns:
        Plotly Figure object
    """
    if not proportions:
        fig = go.Figure()
        fig.add_annotation(
            text="No proportions data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=COLORS["slate_400"], size=14)
        )
        return apply_dark_theme(fig, height=250)

    names = [p.get("proportion", "Unknown") for p in proportions]
    values = [float(p.get("value", 0)) for p in proportions]

    # Golden ratio reference (ideal = 1:1:1 = 0.333 each for thirds)
    ideal_value = 1.0 / 3.0

    # Colors: green if close to ideal, orange if not
    colors = []
    for v in values:
        deviation = abs(v - ideal_value)
        if deviation < 0.05:
            colors.append(COLORS["green"])
        elif deviation < 0.1:
            colors.append(COLORS["secondary"])
        else:
            colors.append(COLORS["primary"])

    fig = go.Figure()

    # Add bars
    fig.add_trace(go.Bar(
        x=names,
        y=values,
        marker=dict(
            color=colors,
            line=dict(color=COLORS["slate_600"], width=1),
        ),
        text=[f"{v:.3f}" for v in values],
        textposition='outside',
        textfont=dict(color=COLORS["slate_300"], size=12),
        hovertemplate="<b>%{x}</b><br>Ratio: %{y:.3f}<extra></extra>",
    ))

    # Add ideal line
    fig.add_hline(
        y=ideal_value,
        line=dict(color=COLORS["slate_400"], width=2, dash="dash"),
        annotation=dict(
            text="Ideal (1/3)",
            font=dict(size=10, color=COLORS["slate_400"]),
        ),
    )

    fig.update_layout(
        title=dict(
            text="Facial Proportions",
            font=dict(size=14, color=COLORS["slate_100"]),
        ),
        xaxis=dict(
            tickfont=dict(color=COLORS["slate_300"]),
        ),
        yaxis=dict(
            range=[0, max(values) * 1.3] if values else [0, 0.5],
            tickfont=dict(color=COLORS["slate_500"]),
            gridcolor='rgba(100, 116, 139, 0.2)',
            title=dict(text="Ratio", font=dict(size=11, color=COLORS["slate_400"])),
        ),
        bargap=0.4,
    )

    return apply_dark_theme(fig, height=280)


# =============================================================================
# NEOCLASSICAL CANONS CHARTS
# =============================================================================

def create_canon_deviation_bar(canons: List[Dict[str, Any]]) -> go.Figure:
    """
    Create horizontal bar chart showing deviation from ideal for each canon.

    Args:
        canons: List of dicts with 'name', 'deviation', and 'in_range' keys
                Example: [{"name": "Facial Thirds", "deviation": 0.02, "in_range": True}, ...]

    Returns:
        Plotly Figure object
    """
    if not canons:
        fig = go.Figure()
        fig.add_annotation(
            text="No canon data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=COLORS["slate_400"], size=14)
        )
        return apply_dark_theme(fig, height=300)

    names = [c.get("name", "Unknown") for c in canons]
    deviations = [float(c.get("deviation", 0)) for c in canons]
    in_range = [c.get("in_range", False) for c in canons]

    # Colors based on in_range status
    colors = [COLORS["green"] if ir else COLORS["red"] for ir in in_range]

    fig = go.Figure(go.Bar(
        x=deviations,
        y=names,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color=COLORS["slate_600"], width=1),
        ),
        text=[f"{d:+.3f}" for d in deviations],
        textposition='outside',
        textfont=dict(color=COLORS["slate_300"], size=10),
        hovertemplate="<b>%{y}</b><br>Deviation: %{x:+.3f}<extra></extra>",
    ))

    # Add vertical line at 0 (ideal)
    fig.add_vline(
        x=0,
        line=dict(color=COLORS["slate_400"], width=2, dash="dash"),
    )

    # Add acceptable range shading (-0.1 to 0.1)
    fig.add_vrect(
        x0=-0.1, x1=0.1,
        fillcolor='rgba(52, 211, 153, 0.1)',
        line_width=0,
    )

    # Calculate x range based on data
    max_dev = max(abs(min(deviations)), abs(max(deviations))) if deviations else 0.2
    x_range = max(0.25, max_dev * 1.3)

    fig.update_layout(
        title=dict(
            text="Canon Deviations from Ideal",
            font=dict(size=14, color=COLORS["slate_100"]),
        ),
        xaxis=dict(
            range=[-x_range, x_range],
            tickfont=dict(color=COLORS["slate_500"]),
            gridcolor='rgba(100, 116, 139, 0.2)',
            title=dict(text="Deviation", font=dict(size=11, color=COLORS["slate_400"])),
            zeroline=True,
            zerolinecolor=COLORS["slate_500"],
        ),
        yaxis=dict(
            tickfont=dict(color=COLORS["slate_300"]),
            automargin=True,
        ),
        bargap=0.25,
    )

    return apply_dark_theme(fig, height=max(250, len(canons) * 35 + 80))


def create_harmony_gauge(score: float) -> go.Figure:
    """
    Create gauge chart for overall harmony score (0-1).

    Args:
        score: Value between 0 and 1

    Returns:
        Plotly Figure object
    """
    # Clamp value to 0-1 range
    score = max(0, min(1, float(score)))

    # Convert to percentage for display (0-100%)
    score_pct = score * 100

    # Determine color based on score
    if score >= 0.8:
        bar_color = COLORS["green"]
    elif score >= 0.6:
        bar_color = COLORS["blue"]
    elif score >= 0.4:
        bar_color = COLORS["secondary"]
    else:
        bar_color = COLORS["red"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score_pct,
        domain={'x': [0, 1], 'y': [0.2, 1]},
        number={
            'font': {'size': 20, 'color': COLORS["slate_100"]},
            'suffix': '%',
            'valueformat': '.1f',
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickcolor': COLORS["slate_500"],
                'tickfont': {'color': COLORS["slate_400"], 'size': 9},
                'tickvals': [0, 25, 50, 75, 100],
            },
            'bar': {'color': bar_color, 'thickness': 0.7},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'borderwidth': 1,
            'bordercolor': COLORS["slate_600"],
            'steps': [
                {'range': [0, 40], 'color': 'rgba(239, 68, 68, 0.15)'},
                {'range': [40, 60], 'color': 'rgba(251, 191, 36, 0.15)'},
                {'range': [60, 80], 'color': 'rgba(96, 165, 250, 0.15)'},
                {'range': [80, 100], 'color': 'rgba(52, 211, 153, 0.15)'},
            ],
            'threshold': {
                'line': {'color': COLORS["slate_100"], 'width': 2},
                'thickness': 0.75,
                'value': score_pct,
            },
        },
    ))

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        autosize=True,
    )

    return apply_dark_theme(fig, height=140)


# =============================================================================
# DASHBOARD AND OVERVIEW CHARTS
# =============================================================================

def create_confidence_dashboard(modules: List[Dict[str, Any]]) -> go.Figure:
    """
    Create multi-indicator dashboard showing confidence for each module.

    Args:
        modules: List of dicts with 'module', 'confidence', and 'status' keys
                 Example: [{"module": "WD", "confidence": 0.85, "status": "active"}, ...]

    Returns:
        Plotly Figure object
    """
    if not modules:
        fig = go.Figure()
        fig.add_annotation(
            text="No module data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=COLORS["slate_400"], size=14)
        )
        return apply_dark_theme(fig, height=120)

    # Filter active modules
    active_modules = [m for m in modules if m.get("status") == "active"]

    if not active_modules:
        active_modules = modules

    n_modules = len(active_modules)

    fig = make_subplots(
        rows=1,
        cols=n_modules,
        specs=[[{"type": "indicator"}] * n_modules],
        horizontal_spacing=0.02,
    )

    for i, mod in enumerate(active_modules):
        confidence = float(mod.get("confidence", 0))

        # Color based on confidence level
        if confidence >= 0.7:
            color = COLORS["green"]
        elif confidence >= 0.5:
            color = COLORS["secondary"]
        else:
            color = COLORS["red"]

        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=confidence * 100,
                number={
                    'suffix': "%",
                    'font': {'size': 14, 'color': COLORS["slate_100"]},
                },
                gauge={
                    'axis': {'range': [0, 100], 'visible': False},
                    'bar': {'color': color, 'thickness': 0.8},
                    'bgcolor': "rgba(30, 41, 59, 0.5)",
                    'borderwidth': 0,
                },
                title={
                    'text': mod.get("module", "Module"),
                    'font': {'size': 10, 'color': COLORS["slate_400"]},
                },
            ),
            row=1, col=i + 1,
        )

    fig.update_layout(
        margin=dict(l=5, r=5, t=25, b=5),
    )

    return apply_dark_theme(fig, height=120)


def create_cross_validation_chart(validations: List[Dict[str, Any]]) -> go.Figure:
    """
    Create chart showing cross-module validation results.

    Args:
        validations: List of dicts with validation info
                     Example: [{"trait": "Impulsivity", "agreement": 0.85, "modules": "WD + Forehead"}, ...]

    Returns:
        Plotly Figure object
    """
    if not validations:
        fig = go.Figure()
        fig.add_annotation(
            text="No cross-validation data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=COLORS["slate_400"], size=14)
        )
        return apply_dark_theme(fig, height=200)

    traits = [v.get("trait", "Unknown") for v in validations]
    agreements = [float(v.get("agreement", 0)) for v in validations]
    modules = [v.get("modules", "") for v in validations]

    # Colors based on agreement level
    colors = []
    for a in agreements:
        if a >= 0.8:
            colors.append(COLORS["green"])
        elif a >= 0.6:
            colors.append(COLORS["blue"])
        elif a >= 0.4:
            colors.append(COLORS["secondary"])
        else:
            colors.append(COLORS["red"])

    fig = go.Figure(go.Bar(
        x=agreements,
        y=traits,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color=COLORS["slate_600"], width=1),
        ),
        text=[f"{a:.0%}" for a in agreements],
        textposition='outside',
        textfont=dict(color=COLORS["slate_300"], size=11),
        customdata=modules,
        hovertemplate="<b>%{y}</b><br>Agreement: %{x:.0%}<br>Modules: %{customdata}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(
            text="Cross-Module Validation",
            font=dict(size=14, color=COLORS["slate_100"]),
        ),
        xaxis=dict(
            range=[0, 1.15],
            tickformat='.0%',
            tickfont=dict(color=COLORS["slate_500"]),
            gridcolor='rgba(100, 116, 139, 0.2)',
        ),
        yaxis=dict(
            tickfont=dict(color=COLORS["slate_300"]),
            automargin=True,
        ),
        bargap=0.3,
    )

    return apply_dark_theme(fig, height=max(180, len(validations) * 40 + 60))


# =============================================================================
# REFLEX COMPONENT WRAPPERS
# =============================================================================

def evidence_level_badge(level: rx.Var, paper_ref: str) -> rx.Component:
    """
    Create visual badge for evidence level with paper reference.

    Args:
        level: Evidence level Var ('validated', 'partial', 'extrapolated', 'speculative')
        paper_ref: Paper reference string (static)

    Returns:
        Reflex Component
    """
    # Use rx.match for dynamic color based on level
    badge = rx.hstack(
        rx.match(
            level,
            ("validated", rx.badge(
                rx.hstack(
                    rx.icon("circle-check", size=12),
                    rx.text("VALIDATED", size="1"),
                    spacing="1",
                    align="center",
                ),
                color_scheme="green",
                size="1",
            )),
            ("partial", rx.badge(
                rx.hstack(
                    rx.icon("check", size=12),
                    rx.text("PARTIAL", size="1"),
                    spacing="1",
                    align="center",
                ),
                color_scheme="amber",
                size="1",
            )),
            ("extrapolated", rx.badge(
                rx.hstack(
                    rx.icon("arrow-right", size=12),
                    rx.text("EXTRAPOLATED", size="1"),
                    spacing="1",
                    align="center",
                ),
                color_scheme="orange",
                size="1",
            )),
            ("speculative", rx.badge(
                rx.hstack(
                    rx.icon("triangle-alert", size=12),
                    rx.text("SPECULATIVE", size="1"),
                    spacing="1",
                    align="center",
                ),
                color_scheme="red",
                size="1",
            )),
            # Default case
            rx.badge(
                rx.hstack(
                    rx.icon("info", size=12),
                    rx.text("UNKNOWN", size="1"),
                    spacing="1",
                    align="center",
                ),
                color_scheme="gray",
                size="1",
            ),
        ),
        rx.tooltip(
            rx.box(
                rx.icon("file-text", size=12, class_name="text-slate-500 cursor-help"),
            ),
            content=paper_ref,
        ),
        spacing="2",
        align="center",
    )

    return badge


def confidence_interval_display(
    value: float,
    lower: float,
    upper: float,
    label: str = "Value",
) -> rx.Component:
    """
    Display a value with its 95% confidence interval.

    Args:
        value: Central value
        lower: Lower bound of CI
        upper: Upper bound of CI
        label: Label for the metric

    Returns:
        Reflex Component
    """
    return rx.box(
        rx.vstack(
            rx.text(label, size="2", class_name="text-slate-400"),
            rx.hstack(
                rx.text(f"{value:.2f}", size="4", weight="bold", class_name="text-white"),
                rx.text(
                    f"[{lower:.2f} - {upper:.2f}]",
                    size="1",
                    class_name="text-slate-500",
                ),
                spacing="2",
                align="baseline",
            ),
            rx.text("95% CI", size="1", class_name="text-slate-600"),
            spacing="1",
            align="center",
        ),
        class_name="bg-slate-800/30 border border-slate-700/30 rounded-lg p-3",
    )
