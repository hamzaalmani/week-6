import streamlit as st

from apputil import *
access_code = "m01l5yNjuQeHMI13Kp9j-ZbbpPk6wWCBDgmxtGjlG8eoaB8DxJjXO7XG7Vd1TmFw"

st.write(
'''
# Week x: [Title]

...
''')

# currently set for integer input
amount = st.number_input("Exercise Input: ", 
                         value=None, 
                         step=1, 
                         format="%d")

if amount is not None:
    st.write(f"The exercise input was {amount}.")

