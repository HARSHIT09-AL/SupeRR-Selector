import plotly.express as px

players = ["Player A", "Player B", "Player C"]
runs = [45, 78, 62]

fig = px.bar(
    x=players,
    y=runs,
    title="Sample Player Performance",
    labels={"x": "Players", "y": "Runs Scored"}
)

fig.show()
