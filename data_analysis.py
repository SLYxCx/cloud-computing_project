import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings("ignore")

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)


def load_and_clean_data(file_path):
    """Load the dataset and handle missing values"""
    print("Loading dataset...")
    df = pd.read_csv(file_path)

    print(f"\nDataset shape: {df.shape}")
    print(f"\nColumn names: {df.columns.tolist()}")
    print(f"\nFirst few rows:\n{df.head()}")

    # Check for missing values
    print(f"\nMissing values:\n{df.isnull().sum()}")

    # Handle missing values for numeric columns only
    numeric_columns = ["Protein(g)", "Carbs(g)", "Fat(g)"]
    for col in numeric_columns:
        if col in df.columns:
            df[col].fillna(df[col].mean(), inplace=True)

    print("\nData cleaning completed!")
    return df


def calculate_average_macros(df):
    """Calculate average macronutrient content for each diet type"""
    print("\n" + "=" * 50)
    print("AVERAGE MACRONUTRIENT CONTENT BY DIET TYPE")
    print("=" * 50)

    avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean()
    print(avg_macros.round(2))

    return avg_macros


def find_top_protein_recipes(df):
    """Find top 5 protein-rich recipes for each diet type"""
    print("\n" + "=" * 50)
    print("TOP 5 PROTEIN-RICH RECIPES BY DIET TYPE")
    print("=" * 50)

    top_protein = (
        df.sort_values("Protein(g)", ascending=False).groupby("Diet_type").head(5)
    )

    for diet_type in df["Diet_type"].unique():
        print(f"\n{diet_type}:")
        diet_recipes = top_protein[top_protein["Diet_type"] == diet_type][
            ["Recipe_name", "Protein(g)", "Cuisine_type"]
        ].head(5)
        print(diet_recipes.to_string(index=False))

    return top_protein


def find_highest_protein_diet(df):
    """Find the diet type with highest protein content"""
    print("\n" + "=" * 50)
    print("DIET TYPE WITH HIGHEST PROTEIN CONTENT")
    print("=" * 50)

    total_protein = (
        df.groupby("Diet_type")["Protein(g)"].sum().sort_values(ascending=False)
    )
    avg_protein = (
        df.groupby("Diet_type")["Protein(g)"].mean().sort_values(ascending=False)
    )

    print(f"\nBy Total Protein Content:\n{total_protein}")
    print(f"\nBy Average Protein Content:\n{avg_protein.round(2)}")
    print(
        f"\nHighest average protein diet: {avg_protein.index[0]} with {avg_protein.iloc[0]:.2f}g"
    )

    return avg_protein


def find_common_cuisines(df):
    """Find most common cuisines for each diet type"""
    print("\n" + "=" * 50)
    print("MOST COMMON CUISINES BY DIET TYPE")
    print("=" * 50)

    for diet_type in df["Diet_type"].unique():
        print(f"\n{diet_type}:")
        cuisine_counts = (
            df[df["Diet_type"] == diet_type]["Cuisine_type"].value_counts().head(5)
        )
        print(cuisine_counts)


def add_new_metrics(df):
    """Add protein-to-carbs and carbs-to-fat ratios"""
    print("\n" + "=" * 50)
    print("ADDING NEW METRICS")
    print("=" * 50)

    # Handle division by zero
    df["Protein_to_Carbs_ratio"] = np.where(
        df["Carbs(g)"] != 0, df["Protein(g)"] / df["Carbs(g)"], np.nan
    )
    df["Carbs_to_Fat_ratio"] = np.where(
        df["Fat(g)"] != 0, df["Carbs(g)"] / df["Fat(g)"], np.nan
    )

    print("New metrics added:")
    print(f"- Protein_to_Carbs_ratio")
    print(f"- Carbs_to_Fat_ratio")
    print(
        f"\nSample of new metrics:\n{df[['Recipe_name', 'Protein_to_Carbs_ratio', 'Carbs_to_Fat_ratio']].head()}"
    )

    return df


def create_visualizations(df, avg_macros, top_protein):
    """Create comprehensive visualizations"""
    print("\n" + "=" * 50)
    print("CREATING VISUALIZATIONS")
    print("=" * 50)

    # 1. Bar chart for average macronutrients
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Protein bar chart
    sns.barplot(
        x=avg_macros.index, y=avg_macros["Protein(g)"], ax=axes[0], palette="viridis"
    )
    axes[0].set_title("Average Protein by Diet Type", fontsize=14, fontweight="bold")
    axes[0].set_xlabel("Diet Type", fontsize=12)
    axes[0].set_ylabel("Average Protein (g)", fontsize=12)
    axes[0].tick_params(axis="x", rotation=45)

    # Carbs bar chart
    sns.barplot(
        x=avg_macros.index, y=avg_macros["Carbs(g)"], ax=axes[1], palette="coolwarm"
    )
    axes[1].set_title("Average Carbs by Diet Type", fontsize=14, fontweight="bold")
    axes[1].set_xlabel("Diet Type", fontsize=12)
    axes[1].set_ylabel("Average Carbs (g)", fontsize=12)
    axes[1].tick_params(axis="x", rotation=45)

    # Fat bar chart
    sns.barplot(x=avg_macros.index, y=avg_macros["Fat(g)"], ax=axes[2], palette="mako")
    axes[2].set_title("Average Fat by Diet Type", fontsize=14, fontweight="bold")
    axes[2].set_xlabel("Diet Type", fontsize=12)
    axes[2].set_ylabel("Average Fat (g)", fontsize=12)
    axes[2].tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.savefig("macronutrients_by_diet.png", dpi=300, bbox_inches="tight")
    print("✓ Saved: macronutrients_by_diet.png")
    plt.show()

    # 2. Heatmap for macronutrient content
    plt.figure(figsize=(10, 6))
    sns.heatmap(
        avg_macros.T, annot=True, fmt=".2f", cmap="YlOrRd", cbar_kws={"label": "Grams"}
    )
    plt.title(
        "Macronutrient Content Heatmap by Diet Type", fontsize=14, fontweight="bold"
    )
    plt.xlabel("Diet Type", fontsize=12)
    plt.ylabel("Macronutrient", fontsize=12)
    plt.tight_layout()
    plt.savefig("macronutrient_heatmap.png", dpi=300, bbox_inches="tight")
    print("✓ Saved: macronutrient_heatmap.png")
    plt.show()

    # 3. Scatter plot for top protein-rich recipes
    plt.figure(figsize=(14, 8))
    diet_types = top_protein["Diet_type"].unique()
    colors = sns.color_palette("husl", len(diet_types))

    for i, diet in enumerate(diet_types):
        diet_data = top_protein[top_protein["Diet_type"] == diet]
        plt.scatter(
            diet_data["Protein(g)"],
            diet_data["Carbs(g)"],
            label=diet,
            alpha=0.7,
            s=100,
            c=[colors[i]],
        )

    plt.title(
        "Top 5 Protein-Rich Recipes: Protein vs Carbs Distribution",
        fontsize=14,
        fontweight="bold",
    )
    plt.xlabel("Protein (g)", fontsize=12)
    plt.ylabel("Carbs (g)", fontsize=12)
    plt.legend(title="Diet Type", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("protein_rich_recipes_scatter.png", dpi=300, bbox_inches="tight")
    print("✓ Saved: protein_rich_recipes_scatter.png")
    plt.show()

    # 4. Box plot for macronutrient distribution
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    sns.boxplot(data=df, x="Diet_type", y="Protein(g)", ax=axes[0], palette="Set2")
    axes[0].set_title(
        "Protein Distribution by Diet Type", fontsize=12, fontweight="bold"
    )
    axes[0].tick_params(axis="x", rotation=45)

    sns.boxplot(data=df, x="Diet_type", y="Carbs(g)", ax=axes[1], palette="Set2")
    axes[1].set_title("Carbs Distribution by Diet Type", fontsize=12, fontweight="bold")
    axes[1].tick_params(axis="x", rotation=45)

    sns.boxplot(data=df, x="Diet_type", y="Fat(g)", ax=axes[2], palette="Set2")
    axes[2].set_title("Fat Distribution by Diet Type", fontsize=12, fontweight="bold")
    axes[2].tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.savefig("macronutrient_distributions.png", dpi=300, bbox_inches="tight")
    print("✓ Saved: macronutrient_distributions.png")
    plt.show()

    # 5. Ratio visualizations
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    df_ratios = df[
        df["Protein_to_Carbs_ratio"].notna() & (df["Protein_to_Carbs_ratio"] < 10)
    ]
    sns.boxplot(
        data=df_ratios,
        x="Diet_type",
        y="Protein_to_Carbs_ratio",
        ax=axes[0],
        palette="Spectral",
    )
    axes[0].set_title(
        "Protein-to-Carbs Ratio by Diet Type", fontsize=12, fontweight="bold"
    )
    axes[0].tick_params(axis="x", rotation=45)

    df_ratios2 = df[df["Carbs_to_Fat_ratio"].notna() & (df["Carbs_to_Fat_ratio"] < 20)]
    sns.boxplot(
        data=df_ratios2,
        x="Diet_type",
        y="Carbs_to_Fat_ratio",
        ax=axes[1],
        palette="Spectral",
    )
    axes[1].set_title("Carbs-to-Fat Ratio by Diet Type", fontsize=12, fontweight="bold")
    axes[1].tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.savefig("ratio_distributions.png", dpi=300, bbox_inches="tight")
    print("✓ Saved: ratio_distributions.png")
    plt.show()


def main():
    """Main execution function"""
    print("\n" + "=" * 50)
    print("NUTRITIONAL DATA ANALYSIS")
    print("=" * 50)

    file_path = "All_Diets.csv"

    try:
        # Load and clean data
        df = load_and_clean_data(file_path)

        # Perform analysis
        avg_macros = calculate_average_macros(df)
        top_protein = find_top_protein_recipes(df)
        highest_protein = find_highest_protein_diet(df)
        find_common_cuisines(df)
        df = add_new_metrics(df)

        # Create visualizations
        create_visualizations(df, avg_macros, top_protein)

        # Save processed data
        df.to_csv("processed_nutrition_data.csv", index=False)
        print("\n✓ Saved: processed_nutrition_data.csv")

        # Save summary statistics
        with open("analysis_summary.txt", "w") as f:
            f.write("NUTRITIONAL DATA ANALYSIS SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write("Average Macronutrients by Diet Type:\n")
            f.write(avg_macros.to_string())
            f.write("\n\nHighest Protein Diet Type:\n")
            f.write(highest_protein.to_string())

        print("✓ Saved: analysis_summary.txt")

        print("\n" + "=" * 50)
        print("ANALYSIS COMPLETE!")
        print("=" * 50)
        print("\nGenerated files:")
        print("1. macronutrients_by_diet.png")
        print("2. macronutrient_heatmap.png")
        print("3. protein_rich_recipes_scatter.png")
        print("4. macronutrient_distributions.png")
        print("5. ratio_distributions.png")
        print("6. processed_nutrition_data.csv")
        print("7. analysis_summary.txt")

    except FileNotFoundError:
        print(f"\nError: Could not find file '{file_path}'")
        print(
            "Please update the file_path variable with the correct path to your CSV file."
        )
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback

        traceback.print_exc()


main()
