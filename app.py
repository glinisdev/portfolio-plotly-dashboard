from dash import Dash, html, dcc
import dash


app = Dash(__name__, use_pages=True)
app._favicon = ("assets/favicon.ico")

app.layout = html.Div([
	html.H1('Avenews Dashboards Application', style={'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "40px", 'margin-top': '2%', 'margin-left': '1%', 'color': '#37C1CE'}),

    html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']}", href=page["relative_path"]
                ), style={'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px", 'margin-left': '1%', 'margin-bottom': '1%', 'display': 'inline-block'}
            )
            for page in dash.page_registry.values()
        ]
    ),

	dash.page_container
])

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8050)
