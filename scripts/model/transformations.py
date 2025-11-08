from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, RobustScaler, QuantileTransformer, PowerTransformer
from category_encoders import TargetEncoder
from sklearn.preprocessing import StandardScaler, FunctionTransformer
import numpy as np
import pandas as pd


class BoundsToNaN(BaseEstimator, TransformerMixin):
    def __init__(self, lower=None, upper=None):
        self.lower = lower; self.upper = upper
    def fit(self, X, y=None): return self
    def transform(self, X):
        X = pd.DataFrame(X).copy()
        return X.mask((X < self.lower) | (X > self.upper))

class TruncateUpper(BaseEstimator, TransformerMixin):
    def __init__(self, upper, value=None):
        self.upper = upper; self.value = value
    def fit(self, X, y=None): return self
    def transform(self, X):
        X = pd.DataFrame(X).copy()
        fill_val = self.upper if self.value is None else self.value
        return X.where(X <= self.upper, fill_val)
    
class ModelTransformations:
    
    def __init__(self):
        pass
    
    def _client_age_pipe(self):

        return Pipeline([
            ("bounds", BoundsToNaN(lower=18, upper=80)),
            ("imp", SimpleImputer(strategy="median")),
            ("log1p", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
        ])

    def _start_using_pipe(self):
        return Pipeline([
            ("bounds", BoundsToNaN(lower=0, upper=94)),
            ("imp", SimpleImputer(strategy="median")),
            ("yj", PowerTransformer(method="yeo-johnson")),
            ("id", FunctionTransformer(lambda x: x, feature_names_out="one-to-one"))
        ])

    def _network_age_pipe(self): 
        return Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("yj", PowerTransformer(method="yeo-johnson")),
            ("id", FunctionTransformer(lambda x: x, feature_names_out="one-to-one"))
        ])

    def _minutes_in_pipe(self):
        return Pipeline([
            ("trunc", TruncateUpper(upper=300, value=300)),
            ("imp", SimpleImputer(strategy="median")),
            ("log1p", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
        ])

    def _avg_perf_pipe(self):
        return Pipeline([
            ("trunc", TruncateUpper(upper=1, value=1)),
            ("imp", SimpleImputer(strategy="median")),
            ("yj", PowerTransformer(method="yeo-johnson")),
            ("id", FunctionTransformer(lambda x: x, feature_names_out="one-to-one"))
        ])


    def _ohe_pipe(self):
        return Pipeline([
            ("imp", SimpleImputer(strategy="most_frequent")),
            ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])


    def _te_pipe(self):
        return Pipeline([
            ("imp", SimpleImputer(strategy="most_frequent")),
            ("te", TargetEncoder()),
            ("id", FunctionTransformer(lambda x: x, feature_names_out="one-to-one"))
        ])


    def _log_pipe(self):
        return Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("log1p", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
        ])

    def _yeojohnson_pipe(self):
        return Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("yj", PowerTransformer(method="yeo-johnson")),
            ("id", FunctionTransformer(lambda x: x, feature_names_out="one-to-one"))
        ])
    
    def transform_pipeline_v1(self):
        cat_ohe_cols = ['previous_classification']
        cat_te_cols = ['state_name']
        start_using_months_col = ['start_using_months']
        passthrough_cols = ['banking', 'plan_postpaid', 'sn_banking', 'digital_index_mean', 'connected_days', 'charged_days', 'music_gb']
        log_transform_features = ['previous_calls', 'validity_average', 'apps_days']
        yj_transform_features = ['arpu_90_days', 'contacts', 'high_frequency_contacts', 'network_age_years' ]
        client_age_col           = ['client_age']
        average_performance_col = ['average_performance']
        network_age_years_col    = ['network_age_years']
        minutes_in_col = ['minutes_in']
        
        return ColumnTransformer(
        transformers=[
            ("client_age",            self._client_age_pipe(),          client_age_col),
            ("start_using_months",    self._start_using_pipe(),         start_using_months_col),
            ("network_age_years",     self._network_age_pipe(),         network_age_years_col),
            ("minutes_in",            self._minutes_in_pipe(),          minutes_in_col),
            ("average_performance",   self._avg_perf_pipe(),            average_performance_col),
            ("ohe",                   self._ohe_pipe(),                 cat_ohe_cols),
            ("te",                    self._te_pipe(),                  cat_te_cols),
            ("log_feats",             self._log_pipe(),                 log_transform_features),
            ("yeojohnson_feats",      self._yeojohnson_pipe(),          yj_transform_features),
            ("not_transform", "passthrough", passthrough_cols)
        ], remainder="drop", verbose_feature_names_out=False)
        
    def get_feature_names_from_ct(self, ct):
        """
        ct: un ColumnTransformer ya .fit(...)
        Devuelve lista de nombres de columnas transformadas en el mismo orden
        que salen de ct.transform(X).
        Maneja pipelines, passthrough y steps que no implementan get_feature_names_out.
        """

        output_names = []

        for name, trans, cols in ct.transformers_:
            # si el transformer fue dropeado explícitamente
            if trans == 'drop':
                continue

            # caso passthrough (columnas que pasan directo)
            if trans == 'passthrough':
                # cols puede ser lista de nombres o índices
                if isinstance(cols, (list, tuple, np.ndarray)):
                    output_names.extend(cols)
                else:
                    output_names.append(cols)
                continue

            # si es un Pipeline
            if hasattr(trans, "steps"):
                # agarramos el último step del pipeline
                last_step_name, last_step = trans.steps[-1]

                # si el último step sabe dar nombres:
                if hasattr(last_step, "get_feature_names_out"):
                    try:
                        names = last_step.get_feature_names_out(cols)
                    except TypeError:
                        # algunos transformers no aceptan 'cols' como arg
                        names = last_step.get_feature_names_out()
                    # prepend el nombre del transformer para evitar colisiones
                    names = [f"{c}" for c in names]
                    output_names.extend(names)
                else:
                    # fallback: usa los nombres originales de las columnas
                    if isinstance(cols, (list, tuple, np.ndarray)):
                        names = [f"{c}" for c in cols]
                        output_names.extend(names)
                    else:
                        output_names.append(f"{cols}")

            # no es Pipeline (ej. directamente OneHotEncoder)
            else:
                if hasattr(trans, "get_feature_names_out"):
                    try:
                        names = trans.get_feature_names_out(cols)
                    except TypeError:
                        names = trans.get_feature_names_out()
                    names = [f"{c}" for c in names]
                    output_names.extend(names)
                else:
                    # último fallback: solo usar cols crudas
                    if isinstance(cols, (list, tuple, np.ndarray)):
                        names = [f"{c}" for c in cols]
                        output_names.extend(names)
                    else:
                        output_names.append(f"{cols}")

        return output_names