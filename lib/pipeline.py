from lib.feature_engineering import *

class PipelineCorrelation:
    
    
    @staticmethod
    def clean(X, y, options: dict):
        """
        mca_keep_features_min
        min_correlation
        tree_percentage_important
        """
        
        history = dict()
        
        # Multicolinearity
        multicolinear_columns = getMulticolinearColumns(np.abs(X.corr()), keep_features_min = options.get('mca_keep_features_min', 6))
        X = X.drop(multicolinear_columns, axis=1)
        history['multicolinear_columns'] = multicolinear_columns

        # Low correlation
        history['low_correlations'] = dict()
        low_correlations_labels, low_correlations_abs = getLowCorrelationsWithTarget(X, y, min_correlation=options.get('min_correlation', 0.1))
        
        history['low_correlations']['low_correlations_labels'] = low_correlations_labels
        history['low_correlations']['low_correlations_abs'] = low_correlations_abs
        
        
        X = X.drop(low_correlations_labels, axis=1)
        
        
        number_features_to_select = int(len(X.columns) * options.get('tree_percentage_important', 0.8))
        # Important features, the 80% most important
        if number_features_to_select > 0 and number_features_to_select < len(X.columns):
            features_important = getImportantFeatures(X, y, number_features_to_select, max_features = number_features_to_select)
            history['features_important'] = features_important
            X = X.loc[:,features_important]
        else:
            history['features_important'] = X.columns      
        
        return X, history