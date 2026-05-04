def generate_insights(df, x_col, y_col, graph_type):
    insights = []

    if df[y_col].dtype in ['int64', 'float64']:
        values = df[y_col]

        insights.append(f"On average, values are around {round(values.mean(), 2)}.")
        insights.append(f"The highest value recorded is {values.max()}, while the lowest is {values.min()}.")

    if graph_type == "bar":
        max_row = df.loc[df[y_col].idxmax()]
        insights.append(f"{max_row[x_col]} clearly stands out with the highest value.")

    elif graph_type == "line":
        if df[y_col].iloc[-1] > df[y_col].iloc[0]:
            insights.append("There is a noticeable upward trend over time.")
        else:
            insights.append("The trend appears to be declining over time.")

    elif graph_type == "pie":
        max_row = df.loc[df[y_col].idxmax()]
        insights.append(f"{max_row[x_col]} contributes the largest share of the total.")

    elif graph_type == "scatter":
        correlation = df[x_col].corr(df[y_col])
        insights.append(f"The relationship between variables has a correlation of {round(correlation, 2)}.")

        if correlation > 0.6:
            insights.append("This suggests a strong positive relationship.")
        elif correlation < -0.6:
            insights.append("This indicates a strong negative relationship.")
        else:
            insights.append("There is no strong linear relationship between variables.")

    elif graph_type == "histogram":
        insights.append("This graph shows how values are distributed across ranges.")
        insights.append(f"Most values fall between {df[y_col].min()} and {df[y_col].max()}.")

    elif graph_type == "heatmap":
        insights.append("The heatmap highlights relationships between numeric variables.")
        insights.append("Darker colors indicate stronger correlations.")

    return insights