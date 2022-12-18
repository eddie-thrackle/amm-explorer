# built-in modules
from copy import deepcopy

# third party modules
import streamlit as st
# import pandas as pd

# custom modules
from utils.amm import AMM, f_pwl, g_pwl2
from utils.chart import plot_amm, plot_balance_history

# streamlit page config
st.set_page_config(layout="wide", page_icon="💬", page_title="AMM Designer")
st.title("AMM/TBC Explorer")
col1, col2, col3 = st.columns([1,1,3])

def write_amm_state(amm, filename='amm_state.txt', write_mode='a'):
    with open(filename, write_mode) as f:
        f.write('{}{} {} {} {}'.format(
            '\n' if write_mode == 'a' else '',
            amm.v_balance['x'], amm.v_balance['y'],
            amm.r_balance['x'], amm.r_balance['y']
        ))

def main():

    # Hacky workaround. Local filesystem seems like a bad solution for deployed version.
    # TODO: read about how Streamlit deployment handles state in multi-user context.
    with open('amm_state.txt', 'r') as f: 
        amm_states = list(map(float, f.read().split()))
        last_state = [float(state_var) for state_var in amm_states[-4:]]
        # amm.extend_x function modifies f and g, so we deepcopy to get "fresh" state of these functions.
        amm = AMM(*last_state, f=deepcopy(f_pwl), g=deepcopy(g_pwl2))

    # AMM Creation Prompts
    with col1.form('AMM Config Form'):
        st.markdown('## Fresh AMM Config')
        amm_state = [float(state_var) for state_var in amm.balance_history[-1]]
        x_virt = st.number_input('X virtual', value=amm_state[0])
        y_virt = st.number_input('Y virtual', value=amm_state[1])
        x_real = st.number_input('X real', value=amm_state[2])
        y_real = st.number_input('Y real', value=amm_state[3])
        if st.form_submit_button("Submit AMM State"):
            amm = AMM(x_virt, y_virt, x_real, y_real, f=deepcopy(f_pwl), g=deepcopy(g_pwl2))
            # Erase all AMM history. Not expecting people care too much about reproducing state ATM.
            write_amm_state(amm, write_mode='w')

    # Post-AMM Creation Prompts 
    with col2.form("(Any KYC'd Wallet) Exchange Form"):
        st.markdown("## Exchange")
        token = st.text_input('Token to sell', 'x')
        n = st.number_input('Number of Token to sell'.format(token), value=5)
        if st.form_submit_button("Submit Sell Order"):
            amm.sell(n, token)
            write_amm_state(amm)
            st.experimental_rerun()
    
    with col2.form("(GTGDA) Extend AMM"):
        st.markdown("## Extend AMM")
        f = eval(st.text_input('Function to extend', 'lambda t: 600 - 2*t'))
        m = st.number_input('m', value=200)
        if st.form_submit_button("Extend AMM"):
            amm.extend_x(f, m)
            write_amm_state(amm)

    # make plots
    col3.altair_chart(plot_amm(amm, col3), use_container_width=True)
    col3.altair_chart(plot_balance_history(), use_container_width=True)

main()

    