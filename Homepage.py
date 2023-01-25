import streamlit as st
from pool import Pool, CurveSegment, SYMBOL_LOOKUP
from sympy import latex

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.markdown('''
Token bonding curves and AMMs,
Two sides of the same coin, it seems.
One a mechanism for price discovery,
The other for liquidity, it beams.

Token bonding curves, a new way to raise,
A method for creating value,
It aligns incentives, and allows for growth,
A path for projects to pursue.

Automated market makers, on the other hand,
Provide liquidity for all to see,
They allow for easy buying and selling,
And make the markets more efficient and free.

Together, they form a powerful pair,
A duality that's hard to ignore,
One for creating value, the other for trading,
A symbiotic relationship, evermore.

Token bonding curves and AMMs,
Two sides of the blockchain coin,
Both vital for the growth and progress,
Of the decentralized economy, we join.

Written by [ChatGPT](https://chat.openai.com/chat) (01/24/2023).
''')

st.set_page_config(layout="wide", page_title="TBC to AMM")
st.title("TBC to AMM Explorer")
st.text('What comes first, AMM balances or TBC segments? A tale as old as DeFi.')
st.text('''
    In this iteration of the project the focus was on going from TBC to AMM
        1. TBC plot of x vs. y is of the form A(x).
        2. Integrated AMM plot is of the form of B(x) = ∫ A(x).
        3. AMM plot is of the form of B(m - x), 
            # where `m` is determined by the domain end point, 
            # which in turn depends on a user-provided value representing the domain width.
''')

def main():

    container1 = st.container()
    left_col, right_col = container1.columns([1, 1])

    x = SYMBOL_LOOKUP['x']

    ### First section - Flat TBC
    right_col.header('Changing parameters on a flat TBC Segment')
    height_section1 = right_col.slider('Height of second TBC segment', min_value=0., max_value=7., value=2., step=0.1)

    f0 = 2
    f1 = height_section1
    initial_tbc_segments = [CurveSegment(f0, 2), CurveSegment(f1, 2)]

    pool1 = Pool(initial_tbc_segments)
    tbc_segments1, integrated_tbc_segments1, amm_segments1 = pool1.amm_curve
    right_col.markdown('TBC Segments')
    right_col.latex(latex(tbc_segments1))
    right_col.markdown('Integrated TBC Segments')
    right_col.latex(latex(integrated_tbc_segments1))
    right_col.markdown('AMM Segments')
    right_col.latex(latex(amm_segments1))
    fig, _ = pool1.plot()
    left_col.pyplot(fig)

    container2 = st.container()
    left_col2, right_col2 = container2.columns([1, 1])

    ### Second section - Linear TBC
    left_col2.header('Changing parameters on a linear TBC Segment')
    slope_slider_section2 = left_col2.slider('Slope on second TBC segment :mountain: :skier:', min_value=-5., max_value=20., value=2.3, step=0.1)
    # y_intercept_slider_section2 = left_col2.slider('Y-intercept on second TBC segment', min_value=-3., max_value=-1., value=-2., step=0.1)
    y_intercept_section2 = 2 - slope_slider_section2*2

    f2 = 2
    f3 = slope_slider_section2*x + y_intercept_section2
    initial_tbc_segments = [CurveSegment(f2, 2), CurveSegment(f3, 1)]

    pool2 = Pool(initial_tbc_segments)
    tbc_segments2, integrated_tbc_segments2, amm_segments2 = pool2.amm_curve
    left_col2.markdown('TBC Segments')
    left_col2.latex(latex(tbc_segments2))
    left_col2.markdown('Integrated TBC Segments')
    left_col2.latex(latex(integrated_tbc_segments2))
    left_col2.markdown('AMM Segments')
    left_col2.latex(latex(amm_segments2))
    fig, _ = pool2.plot()
    right_col2.pyplot(fig)

    ### Third section - Free play mode
    container3 = st.container()
    left_col3, right_col3 = container3.columns([1, 1])
    right_col3.header('Free play mode')

    radio = right_col3.radio('Select a functional form for the second TBC segment', ['Flat', 'Linear'])

    if radio == 'Flat':
        # streamlit widgets to set height and domain width of second segment
        height_section3 = right_col3.slider('Height of second TBC segment', min_value=0., max_value=7., value=2., step=0.1, key = 'flat-height')
        f4 = 2
        f5 = height_section3
        domain_width = right_col3.slider('Domain width', min_value=0.1, max_value=10., value=2., step=0.1,  key = 'flat-domain')
    elif radio == 'Linear':
        # streamlit widgets to set slope and domain width of second segment
        slope_slider_section3 = right_col3.slider('Slope on second TBC segment :mountain: :skier:', min_value=-5., max_value=20., value=2.3, step=0.1, key='linear-slope')
        y_intercept_section3 = 2 - slope_slider_section3*2
        f4 = 2
        f5 = slope_slider_section3*x + y_intercept_section3
        domain_width = right_col3.slider('Domain width', min_value=0.1, max_value=10., value=2., step=0.1, key='linear-domain')
    else:
        raise ValueError('Invalid radio option')
    pool3 = Pool([CurveSegment(f4, 2), CurveSegment(f5, domain_width)])
    tbc_segments3, integrated_tbc_segments3, amm_segments3 = pool3.amm_curve
    right_col3.markdown('TBC Segments')
    right_col3.latex(latex(tbc_segments3))
    right_col3.markdown('Integrated TBC Segments')
    right_col3.latex(latex(integrated_tbc_segments3))
    right_col3.markdown('AMM Segments')
    right_col3.latex(latex(amm_segments3))
    fig, _ = pool3.plot()
    left_col3.pyplot(fig)


main()