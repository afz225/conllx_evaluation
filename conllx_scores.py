

from pandas import DataFrame
from classes import ConllxScores


def get_attachment_scores(matches_df, counts_df):
        # sum matches
        matches_sums = matches_df[['pos_matches', 'uas_matches', 'label_matches', 'las_matches']].sum()

        # rename columns
        matches_sums.rename({'pos_matches': 'pos', 'uas_matches': 'uas', 'label_matches': 'label', 'las_matches': 'las'}, inplace=True)
        # divide by the total gold token count, round, multiply by 100 to get a percent, convert to dict
        return ((matches_sums / counts_df['ref_token_count'].sum()).round(3)*100).to_dict()
    
def get_f_score_components(matches_df, counts_df):
    # TODO change REC to TOK_REC
    REC = matches_df['tokenization_matches'].sum() / counts_df['ref_token_count'].sum()
    PREC = matches_df['tokenization_matches'].sum() / counts_df['pred_token_count'].sum()
    f_score = (2*PREC*REC / (PREC+REC)).round(3)
    return {
        'tokenization_f_score': f_score*100,
        'tokenization_recall': REC*100,
        'tokenization_precision': PREC*100,
    }

def get_word_accuracy_score(word_matches: int, ref_word_count: int):
    return {'word_accuracy': (word_matches / ref_word_count)*100}

def get_scores_means(tree_matches_list, tree_counts_list) -> ConllxScores:
    """Gets the mean scores for all sentences.
    The scores list is converted to a dataframe to compute mean,
    then the scores are returned as a ConllxStatistics object.
    
    Precision of edits PREC= C / P (what is correct of the prediction)
    Recall of edits REC = C / R (what is correct of the reference)

    The Tokenization F-score = 2*PREC*REC / (PREC+REC)

    Args:
        sentence_scores (List[dict]): scores for each tree pair
        total_token_count (int): total number of tokens

    Returns:
        ConllxStatistics: the mean scores for all sentences
    """
    matches_df = DataFrame(tree_matches_list)
    counts_df = DataFrame(tree_counts_list)
    
    scores_dict = {**get_attachment_scores(matches_df, counts_df), 
                   **get_f_score_components(matches_df, counts_df),
                   **get_word_accuracy_score(matches_df['word_matches'].iloc[0], counts_df['ref_word_count'].iloc[0])}

    return ConllxScores(**scores_dict)