from scipy.stats import skew, kurtosis
import pandas as pd
import math
import matplotlib.pyplot as plt
from scipy.stats import probplot
import seaborn as sns
import warnings
from sklearn.preprocessing import QuantileTransformer, PowerTransformer
import numpy as np

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
    
    
def plot_hist_prob(df, columns, kde=True):
    """
    Plots histogram + probability plot + boxplot for each numeric column in df.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with numeric features
    columns : list
        List of column names to visualize
    kde : bool
        Whether to show kernel density in histograms
    """
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        for col_name in columns:
            fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 3))
            fig.suptitle(col_name, fontsize=16, y=1.05)

            # Histogram & Density
            sns.histplot(df[col_name].dropna(), kde=kde, ax=axes[0])
            axes[0].set_title('Histogram')
            axes[0].set_xlabel(col_name)

            # Probability Plot (Q–Q Plot)
            probplot(df[col_name].dropna(), plot=axes[1])
            axes[1].set_title('Probability Plot')

            # Boxplot
            sns.boxplot(x=df[col_name], ax=axes[2], showfliers=True)
            axes[2].set_title('Boxplot')

            plt.tight_layout()
            plt.show()


def compare_transforms(df, col_name, title=None, sample=None, is_discrete=False, random_state=42):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        """
        Compara la distribución original vs log, Quantile y Yeo-Johnson.
        Maneja ceros/negativos de forma segura y muestra si la variable es apta para log.
        """
        s = pd.to_numeric(df[col_name], errors='coerce') \
                .replace([np.inf, -np.inf], np.nan) \
                .dropna()

        if sample and len(s) > sample:
            s = s.sample(sample, random_state=random_state)

        fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(18, 12))
        fig.suptitle(title or col_name, fontsize=18)

        # -------------------------------
        # ORIGINAL
        # -------------------------------
        sns.histplot(x=s, ax=axes[0,0], kde=not is_discrete, discrete=is_discrete)
        axes[0,0].set_title('Histogram (Original)')

        probplot(s, dist="norm", plot=axes[0,1])
        axes[0,1].set_title('Q–Q (Original)')

        sns.boxplot(x=s, ax=axes[0,2], showfliers=True)
        axes[0,2].set_title('Boxplot (Original)')

        # -------------------------------
        # LOG (solo si es apta)
        # -------------------------------
        log_msg = ""
        if (s <= 0).any():
            if (s < 0).any():
                log_msg = "⚠️ Negatives → Log skipped"
                s_log = None
            else:
                log_msg = "Applied log1p() (zeros detected)"
                s_log = np.log1p(s)
        else:
            log_msg = "Applied log()"
            s_log = np.log(s)

        if s_log is not None:
            sns.histplot(x=s_log, ax=axes[1,0], kde=True)
            axes[1,0].set_title('Histogram (Log)')
            probplot(s_log, dist="norm", plot=axes[1,1])
            axes[1,1].set_title('Q–Q (Log)')
            sns.boxplot(x=s_log, ax=axes[1,2], showfliers=True)
            axes[1,2].set_title('Boxplot (Log)')
        else:
            for j in range(3):
                axes[1,j].text(0.5, 0.5, log_msg, ha='center', va='center', fontsize=14)
                axes[1,j].set_axis_off()

        # -------------------------------
        # QUANTILE
        # -------------------------------
        q = QuantileTransformer(
            output_distribution='normal',
            n_quantiles=min(1000, s.shape[0]),
            random_state=random_state
        )
        s_q = q.fit_transform(s.values.reshape(-1,1)).ravel()

        sns.histplot(x=s_q, ax=axes[2,0], kde=True)
        axes[2,0].set_title('Histogram (Quantile→Normal)')

        probplot(s_q, dist="norm", plot=axes[2,1])
        axes[2,1].set_title('Q–Q (Quantile)')

        sns.boxplot(x=s_q, ax=axes[2,2], showfliers=True)
        axes[2,2].set_title('Boxplot (Quantile)')

        # -------------------------------
        # YEO-JOHNSON
        # -------------------------------
        yj = PowerTransformer(method='yeo-johnson')
        if s.nunique() > 1:
            s_yj = yj.fit_transform(s.values.reshape(-1,1)).ravel()
        else:
            s_yj = s.values  # sin cambio

        sns.histplot(x=s_yj, ax=axes[3,0], kde=True)
        axes[3,0].set_title('Histogram (Yeo–Johnson)')

        probplot(s_yj, dist="norm", plot=axes[3,1])
        axes[3,1].set_title('Q–Q (Yeo–Johnson)')

        sns.boxplot(x=s_yj, ax=axes[3,2], showfliers=True)
        axes[3,2].set_title('Boxplot (Yeo–Johnson)')

        fig.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()

        # Info resumida
        print(f"=== {col_name} ===")
        print(f"Count: {len(s)}, Min: {s.min():.3f}, Max: {s.max():.3f}")
        print(f"Log status: {log_msg}")