# built-in modules
from copy import deepcopy

# third party modules
import streamlit as st
import dill as pickle

# custom modules
from utils.amm import AMM, f_pwl, g_pwl2
from utils.chart import plot_amm, plot_balance_history, plot_exchange_history

# streamlit page config
st.set_page_config(layout="wide", page_icon="💬", page_title="AMM Designer")
st.title("AMM/TBC Explorer")
col1, col2, col3 = st.columns([1,1,3])

BALANCE_HISTORY_PATH = 'amm_state.txt'
EXCHANGE_LOG_PATH = 'exchange_log.txt'
F_PATH = 'f.pkl'
G_PATH = 'g.pkl'

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

def write_function_states(f, g):
    with open(F_PATH, 'wb') as file:
        pickle.dump(f, file)
    with open(G_PATH, 'wb') as file:
        pickle.dump(g, file)
    
def hard_reset():
    global amm 
    amm = AMM(70, 30, 70, 30, f=deepcopy(f_pwl), g=deepcopy(g_pwl2))
    write_amm_state(amm, write_mode='w')
    write_function_states(amm.functions['x'], amm.functions['y'])
    open(EXCHANGE_LOG_PATH, 'w').close()

def main():

    if col1.button('Reset State'):
        hard_reset()

    global amm
    with open(BALANCE_HISTORY_PATH, 'r') as f: 
        amm_states = list(map(float, f.read().split()))
        last_state = [float(state_var) for state_var in amm_states[-4:]]
    
    try:
        with open(F_PATH, 'rb') as f:
            f_latest = pickle.load(f)
        with open(G_PATH, 'rb') as f:
            g_latest = pickle.load(f)
    except FileNotFoundError:
        print('File not found.')
        f_latest = deepcopy(f_pwl)
        g_latest = deepcopy(g_pwl2)
        
    amm = AMM(*last_state, f = f_latest, g = g_latest)

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
            write_amm_state(amm, write_mode='w') # erase state! 

    # AMM Interaction Prompts 
    with col2.form("(Any KYC'd Wallet) Exchange Form"):
        st.markdown("## Exchange")
        st.write("Swap `m` of token `x` or `y` for the amount of the other determined by the AMM.")
        token = st.text_input('Token to sell', 'x')
        n = st.number_input('Number of Token to sell'.format(token), value=5)
        if st.form_submit_button("Submit Sell Order"):
            amount, other_token = amm.sell(n, token)
            write_amm_state(amm)
            write_function_states(amm.functions['x'], amm.functions['y'])
            log_exchange(token, n, other_token, amount)
            # st.experimental_rerun()
    
    with col2.form("(GTGDA) Extend AMM"):
        st.markdown("## Extend AMM")
        st.write('Add a kink to the AMM by extending in the `x` dimension.')
        st.write("Write a function using [Python lambda syntax](https://realpython.com/python-lambda/).")
        f = eval(st.text_input('Function to extend with', 'lambda t: 600 - 2*t'))
        m = st.number_input('m', value=200)
        if st.form_submit_button("Extend AMM"):
            amm.extend_x(f, m)
            write_amm_state(amm)
            write_function_states(amm.functions['x'], amm.functions['y'])

    # make plots
    col3.altair_chart(plot_amm(amm, col3), use_container_width=True)
    col3.altair_chart(plot_balance_history(), use_container_width=True)
    if len(open(EXCHANGE_LOG_PATH, 'r').readlines()) > 0:
        col3.dataframe(plot_exchange_history())

if 'initialized' not in st.session_state:
    hard_reset()
    st.session_state['initialized'] = True
    
main()