import matplotlib.pyplot as plt
import seaborn as sns


def auto_select_graph(df, x_col, y_col):
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

    is_x_numeric = x_col in numeric_cols
    is_y_numeric = y_col in numeric_cols

    num_unique = df[x_col].nunique()
    data_size = len(df)

    # 1. Same column → distribution
    if x_col == y_col and is_y_numeric:
        return "histogram"

    # 2. Numeric vs Numeric → relationship
    if is_x_numeric and is_y_numeric:
        if data_size > 200:
            return "scatter"  # still fine, but dense
        return "scatter"

    # 3. Categorical + Numeric
    if not is_x_numeric and is_y_numeric:

        # Too many categories → avoid pie
        if num_unique <= 5 and data_size <= 20:
            return "pie"

        # Medium categories → bar
        if num_unique <= 20:
            return "bar"

        # Too many categories → still bar (aggregated)
        return "bar"

    # 4. Numeric X + Categorical Y (rare case)
    if is_x_numeric and not is_y_numeric:
        return "bar"

    # 5. Default fallback
    return "line"


def generate_graph(df, x_col, y_col, graph_type):
    fig, ax = plt.subplots(figsize=(4.5, 3))

    # =========================
    # GRAPH TYPES
    # =========================

    if graph_type == "bar":
        ax.bar(df[x_col], df[y_col])
        ax.set_xlabel(x_col, fontsize=9)
        ax.set_ylabel(y_col, fontsize=9)

    elif graph_type == "line":
        ax.plot(df[x_col], df[y_col], marker='o')
        ax.set_xlabel(x_col, fontsize=9)
        ax.set_ylabel(y_col, fontsize=9)

    elif graph_type == "pie":
        grouped = df.groupby(x_col)[y_col].sum()

        # Limit categories to top 5 for clean UI
        grouped = grouped.sort_values(ascending=False).head(5)

        ax.pie(
            grouped,
            labels=grouped.index,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 8}
            )
        ax.axis('equal')
     

    elif graph_type == "scatter":
        ax.scatter(df[x_col], df[y_col])
        ax.set_xlabel(x_col, fontsize=9)
        ax.set_ylabel(y_col, fontsize=9)

    elif graph_type == "histogram":
        ax.hist(df[y_col], bins=10)
        ax.set_xlabel(y_col, fontsize=9)
        ax.set_ylabel("Frequency", fontsize=9)

    elif graph_type == "heatmap":
        corr = df.select_dtypes(include=['int64', 'float64']).corr()

        # Clear axis before plotting heatmap
        ax.clear()

        sns.heatmap(
            corr,
            annot=True,
            cmap="coolwarm",
            fmt=".2f",
            linewidths=0.5,
            ax=ax
        )

        ax.set_title("Correlation Heatmap", fontsize=10)

    # =========================
    # TITLE (skip for heatmap since already set)
    # =========================

    if graph_type != "heatmap":
        ax.set_title(f"{graph_type.upper()} Graph", fontsize=10)

    plt.tight_layout()

    return fig