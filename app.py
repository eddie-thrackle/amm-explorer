# built-in modules
from copy import deepcopy

# third party modules
import streamlit as st

# custom modules
from utils.amm import AMM, f_pwl, g_pwl2
from utils.chart import plot_amm, plot_balance_history, plot_exchange_history

# streamlit page config
st.set_page_config(layout="wide", page_icon="💬", page_title="AMM Designer")
st.title("AMM/TBC Explorer")
col1, col2, col3 = st.columns([1,1,3])

BALANCE_HISTORY_PATH = 'amm_state.txt'
EXCHANGE_LOG_PATH = 'exchange_log.txt'

def write_amm_state(amm, filename=BALANCE_HISTORY_PATH, write_mode='a'):
    with open(filename, write_mode) as f:
        f.write('{}{} {} {} {}'.format(
            '\n' if write_mode == 'a' else '',
            amm.v_balance['x'], amm.v_balance['y'],
            amm.r_balance['x'], amm.r_balance['y']
        ))

def log_exchange(token, n, other_token, amount, filename=EXCHANGE_LOG_PATH, write_mode='a'):
    with open(filename, write_mode) as f:
        f.write('{}{} {} {} {}'.format(
            '\n' if write_mode == 'a' else '',
            token, n, other_token, amount
        ))

def main():

    if col1.button('Reset State'):
        amm = AMM(70, 30, 70, 30, f=deepcopy(f_pwl), g=deepcopy(g_pwl2))
        write_amm_state(amm, write_mode='w')
        open(EXCHANGE_LOG_PATH, 'w').close() # empty log

    # Kinda hacky. Local filesystem is a bad solution for deployed version.
    # Then, someone else changing the state affects my state on reload. Idk if this is good. 
    with open(BALANCE_HISTORY_PATH, 'r') as f: 
        amm_states = list(map(float, f.read().split()))
        last_state = [float(state_var) for state_var in amm_states[-4:]]
        # amm.extend_x function modifies f and g, so deepcopy to get "fresh" state of functions.
        amm = AMM(*last_state, f = deepcopy(f_pwl), g = deepcopy(g_pwl2))

    # AMM Config Prompts
    with col1.form('AMM Config'):
        st.markdown('## AMM Config')
        st.write('Fill in the balances you want for each. This will reset the state of the AMM accordingly.')
        amm_state = [float(state_var) for state_var in amm.balance_history[-1]]
        x_virt = st.number_input('X virtual', value=amm_state[0])
        y_virt = st.number_input('Y virtual', value=amm_state[1])
        x_real = st.number_input('X real', value=amm_state[2])
        y_real = st.number_input('Y real', value=amm_state[3])
        if st.form_submit_button("Submit AMM State"):
            amm = AMM(x_virt, y_virt, x_real, y_real, f = deepcopy(f_pwl), g = deepcopy(g_pwl2))
            # Erase all AMM history. Does not expect people care about reproducing state ATM. TBD.
            write_amm_state(amm, write_mode='w')

    # AMM Interaction Prompts 
    with col2.form("(Any KYC'd Wallet) Exchange Form"):
        st.markdown("## Exchange")
        st.write("Swap `m` of token `x` or `y` for the amount of the other determined by the AMM.")
        token = st.text_input('Token to sell', 'x')
        n = st.number_input('Number of Token to sell'.format(token), value=5)
        if st.form_submit_button("Submit Sell Order"):
            amount, other_token = amm.sell(n, token)
            write_amm_state(amm)
            log_exchange(token, n, other_token, amount)
            st.experimental_rerun()
    
    with col2.form("(GTGDA) Extend AMM"):
        st.markdown("## Extend AMM")
        st.write('Add a kink to the AMM by extending in the `x` dimension.')
        st.write("Write a function using [Python lambda syntax](https://realpython.com/python-lambda/).")
        f = eval(st.text_input('Function to extend with', 'lambda t: 600 - 2*t'))
        m = st.number_input('m', value=200)
        if st.form_submit_button("Extend AMM"):
            amm.extend_x(f, m)

    # make plots
    col3.altair_chart(plot_amm(amm, col3), use_container_width=True)
    col3.altair_chart(plot_balance_history(), use_container_width=True)
    if len(open(EXCHANGE_LOG_PATH, 'r').readlines()) > 0:
        col3.dataframe(plot_exchange_history())

main()