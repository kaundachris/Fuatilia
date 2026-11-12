import pandas as pd
import plotly.express as px


def check_password(password):
    """checks that the password:
            - is at least 6 characters long,
            - has a number,
            - has a letter,
            - has a special character
    """

    has_digit = False
    has_letter = False
    has_special = False

    # check that the password is at least 6 character long
    if len(password) < 6:
        return False

    # check that the password has a number, a letter and a special character
    for char in password:
        if char.isnumeric():
            has_digit = True
        elif char.isalpha():
            has_letter = True
        elif not char.isspace():
            has_special = True

        # if all the above are true, exit early (saves time)
        if has_digit and has_letter and has_special:
            return True
    return False


def build_data_dict(profile_data, price_data, income_data, balance_sheet_data, cashflow_data, ratio_data):
    """packages the data for storage in the database"""

    data= {
        "profile_data": profile_data,
        "price_data": price_data,
        "income_data": income_data,
        "balance_sheet_data": balance_sheet_data,
        "cashflow_data": cashflow_data,
        "ratio_data": ratio_data
        }

    return data


def chart(price_data):
    """render the price chart (closing prices)"""

    # set price data to none if API returned nothing
    if not price_data:
        return None

    # load into a dataframe - offers safer handling
    df = pd.DataFrame(price_data)

    # convert date (string) to datetime object - reduces bugs
    df["date"] = pd.to_datetime(df["date"])
    graph = px.line(df, x="date", y ="price")

    # update the graph to match the design of the page
    graph.update_layout(
        # set background to black - like the html
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        # set font color to antiquewhite - like the html
        font_color="#FAEBD7",

        # set font to the page's family
        font_family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif",

        # fill the chart's container fully
        margin=dict(l=0, r=0, t=0, b=0),
        
        #set the height
        height = 300,

        # show one tooltip whatever the position of the cursor
        hovermode="x unified",
        
        # Remove vertical gridlines, axis line, title, and use muted labels
        xaxis=dict(showgrid=False, showline=False, zeroline=False, title=None, automargin=True, tickfont=dict(size=12, color="#888888")),

        # set a few horizontal gridlines
        yaxis=dict(gridcolor="#333333", gridwidth=1, nticks=4, showline=False, zeroline=False, title=None,
                    automargin=True, tickprefix="$", tickfont=dict(size=12, color="#888888")),
    )
    
    # set Line to be thinner, and set a cleaner hover label
    graph.update_traces(line_color="#0A88B3", line_width=1.5, hovertemplate="$%{y:,.2f}<extra></extra>",)

    return graph.to_html(full_html=False, include_plotlyjs="cdn", config={"displayModeBar": False, "responsive": True},)
