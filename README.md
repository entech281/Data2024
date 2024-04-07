# Data2024

# Documentation

# Status of of 4/7/2024
* gsheet backend is now generic and returns dataframes
* config method sorted
* cache class written
* data file started-- this is where we combine fetching data, caching

# TODO
* get rid of the dot names, need _ instaed to play nice with dfs
* really need to find which tba endpoint returns JUST teams, even before matches start
* refactor team_analysis to be pure DF in DF out, add tests
* refactor tba class
  * pull in tba match predictions (how?)
* new tag manager that manages columns in a df ( because each tag we count how many tags it was applied)
* tests in local cache mode
* ditch pydantic stuff, it was a non-helpful extra layer
* switch to nicegui? streamllit custom compnent and layout was terrible
  * how to deploy then?
  * components are bi-directional, via on(event) and run_method(to component)
* collect tags in match and pit scouting. tally the number of times a tag is applied
  * show in team summary
    
##AGGrid Details
https://streamlit-aggrid.readthedocs.io/en/docs/
https://www.ag-grid.com/javascript-data-grid/getting-started/
https://github.com/PablocFonseca/streamlit-aggrid/blob/main/st_aggrid/__init__.py
https://www.ag-grid.com/javascript-data-grid/grid-options/
https://streamlit-aggrid.readthedocs.io/en/docs/GridOptionsBuilder.html



## Idea: pull-through cache using csv
 * df.to_csv()

## Data sources
gsheet
    pit data
    match data
    applied tags
    valid tags
tba
    rankings: this event
    oprs: this event
    pch team number list
    pch district rankings ( not uesd)
    matches and teams in them
    team stats: this event