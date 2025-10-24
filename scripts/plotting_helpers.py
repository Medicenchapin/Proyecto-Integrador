from scipy.stats import skew, kurtosis
import pandas as pd
import math
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

def plot_histogram(df, numerical_cols, bins=30):
    n = len(numerical_cols)
    cols = 2
    rows = math.ceil(n/cols)

    fig, axes = plt.subplots(rows,cols, figsize=(cols*8,rows*3))
    axes= axes.flatten()
    
    for i, col in enumerate(numerical_cols):
        ax = axes[i]
        s = pd.to_numeric(df[col], errors='coerce').dropna()
        # hist
        ax.hist(s, bins=bins, density=False, alpha=0.7)
        mean = s.mean()
        median = s.median()
        mode = s.mode().iloc[0]
        skewness = skew(s, bias=False, nan_policy='omit')
        kurt = kurtosis(s, fisher=True, bias=False, nan_policy='omit')

        if skewness < -1 and kurt > 3:
            classification = "(-) skewed and leptokurtic"
        elif skewness > 1 and kurt > 3:
            classification = "(+) skewed and leptokurtic"
        elif skewness < -1 and kurt < 0:
            classification = "(-) skewed and platykurtic"
        elif skewness > 1 and kurt < 0:
            classification = "(+) skewed and platykurtic"
        else:
            classification = "aprox. symmetric and mesokurtic"

        ax.axvline(x=mean, linestyle='--', color='red', label=f'Mean {mean:.2f}')
        ax.axvline(x=median, linestyle='-', color='blue', label =f'Median {median:.2f}')
        ax.axvline(x=mode, linestyle='-', color='green', label=f'Mode {mode:.2f}')
        
        annotation_text = (f'Skewness: {skewness:.2f}\n'
                           f'Kurtosis: {kurt:.2f}\n'
                           f'{classification}')
        ax.annotate(annotation_text,
                    xy=(0.57, 0.57), xycoords='axes fraction',
                    fontsize=9, ha='left',
                    bbox=dict(boxstyle='round', fc='w', ec='k', pad=1.0, alpha=1))
        
        ax.legend()
        ax.set_title(f'Histogram of {col}')
        
    plt.tight_layout()
    plt.show()
    
    
def plot_target(sales_counts, sales_perc):
    # Crea la figura
    fig, ax = plt.subplots(figsize=(6,4))
    bars = ax.bar(sales_counts.index.astype(str), sales_counts.values, color=['#66b3ff','#99ff99'])

    # Títulos y etiquetas
    ax.set_title('Sales Distribution', fontsize=14)
    ax.set_xlabel('Sale Outcome')
    ax.set_ylabel('Number of Records')

    # Agrega los porcentajes arriba de cada barra
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2,     # posición horizontal centrada
            height + (height * 0.01),            # un poco arriba de la barra
            f'{sales_perc.iloc[i]:.2f}%',        # texto (porcentaje)
            ha='center', va='bottom', fontsize=12
        )

    plt.tight_layout()
    plt.show()
    
def plot_bar(df, categorical_vars):
    n = len(categorical_vars[:-1])
    cols = 2
    rows = math.ceil(n/cols)


    fig, axes = plt.subplots(rows, cols, figsize=(cols*5,rows*3))

    axes= axes.flatten()

    for i, col in enumerate(categorical_vars[:-1]):
        df[col].value_counts().plot(kind='bar', ax=axes[i])
        axes[i].set_title(f'Counts for {col}')
        axes[i].set_xlabel(col)
        axes[i].set_ylabel('Counts')

    plt.tight_layout()
    plt.show()
    
    
def plot_bivariade_bar(df, categorical_vars, target):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        n = len(categorical_vars[:-1])
        cols = 2
        rows = math.ceil(n/cols)


        fig, axes = plt.subplots(rows, cols, figsize=(18, 24))
        axes = axes.flatten()

        for i, col in enumerate(categorical_vars[:-1]):
            sns.countplot(data=df, x=col, hue=target, ax=axes[i])
            axes[i].set_title(f"{col} vs {target}", fontsize=12)
            axes[i].tick_params(axis='x', rotation=45)

        plt.tight_layout
        plt.show()
    
    
def explain_targetWith_cat(df, categorical_vars, target):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        cols = 2
        rows = math.ceil(len(categorical_vars[:-1]) / cols)
        fig, axes = plt.subplots(rows, cols, figsize=(cols*7, rows*5))
        axes = axes.flatten()

        for i, col in enumerate(categorical_vars[:-1]):
            prop = (
                df.groupby(col)[target]
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )

            sns.barplot(data=prop, x=col, y=target, ax=axes[i], palette="coolwarm")
            axes[i].set_title(f"Proportion of {target}=1 by {col}", fontsize=12)
            axes[i].tick_params(axis='x', rotation=45)
            axes[i].set_ylabel("Proportion of Sale")
            axes[i].set_xlabel(col)

        plt.tight_layout()
        plt.show()
        
        
def plot_correlation(corr, title):
    plt.figure(figsize=(24, 12))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1)
    plt.title(title)
    plt.show()
    
    
def plotBoxplots(df, numerical_cols, target=''):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        n = len(numerical_cols)
        cols = 2
        rows = math.ceil(n/cols)

        fig, axes = plt.subplots(rows,cols, figsize=(cols*8,rows*3))
        axes= axes.flatten()
        
        for i, col in enumerate(numerical_cols):
            ax = axes[i]
            # boxplot
            if target != 'sale':
                sns.boxplot(y=col, data=df, ax=ax)
                ax.set_title(f'Histogram of {col}')
            else:
                sns.boxplot(x=target, y=col, data=df, ax=ax)
                ax.set_title(f'{col} vs Target')
            
            
        plt.tight_layout()
        plt.show()
        
def correlation_barplot(corr):
    plt.figure(figsize=(12,8))
    sns.barplot(x=corr.values, y=corr.index, legend=False)
    plt.title("Correlation of Numerical Features with Target", fontsize=14)
    plt.xlabel("Correlation coefficient")
    plt.ylabel("Feature")
    plt.show()