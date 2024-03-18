from pathlib import Path
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

# Tell streamlit that there is a component called st_scoring_widget,
# and that the code to display that component is in the "frontend" folder
frontend_dir = (Path(__file__).parent / "frontend").absolute()


_component_func = components.declare_component(
    "frc_scoring_tracker",
	path=str(frontend_dir)
)

# Create the python function that will be called
def frc_scoring_tracker(
    key: Optional[str] = None,
):
    """
    Add a descriptive docstring
    """
    component_value = _component_func(
        key=key
    )
    DEFAULT_VALUES=[0,0,0,0,0,0,0,0];
    if component_value is None:
        return DEFAULT_VALUES
    else:
        return component_value
    return component_value


def main():
    st.write("## Scoring Summary")
    value = frc_scoring_tracker(key="auto_scoring")

    st.write(" ## Value:")
    st.write(value)


if __name__ == "__main__":
    main()
