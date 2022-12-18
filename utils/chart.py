import altair as alt
import pandas as pd

def get_chart(
    data, chart_title = 'AMM config', 
    symbol = 'function', 
    x = 'input', y = 'output', 
    x_title = 'input', y_title = 'output'
):
    
    hover = alt.selection_single(
        fields=[x],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title=chart_title)
        .mark_line()
        .encode(
            x=x,
            y=y,
            color=symbol,
            strokeDash=symbol,
        )
    )

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x=alt.X(x, axis=alt.Axis(tickMinStep=1)),
            y=y,
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip(x, title=x_title),
                alt.Tooltip(y, title=y_title),
            ],
        )
        .add_selection(hover)
    )

    return (lines + points + tooltips).interactive()

def plot_amm(amm, col):
    source = amm.display()
    all_symbols = source.function.unique()
    symbols = col.multiselect("Choose functions", all_symbols, all_symbols, key='sell')
    source = source[source.function.isin(symbols)]
    return get_chart(source)

def plot_balance_history(filename='amm_state.txt'):
    data = {"Time Step": [], "Amount": [], "Balance Type": []}
    t = 0
    with open(filename, 'r') as f:
        for line in f.readlines():
            amm_balances = list(map(float, line.split()))
            data['Time Step'].extend([t]*4)
            data['Amount'].extend(amm_balances)
            data['Balance Type'].extend(['X virtual', 'Y virtual', 'X real', 'Y real'])
            t += 1
    return get_chart(
        data = pd.DataFrame(data),
        chart_title = 'Balance History', symbol = 'Balance Type',
        x = 'Time Step', y = 'Amount', 
        x_title = 'Time Step', y_title = 'Amount',
        n_ticks = t   
    )