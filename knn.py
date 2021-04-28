from wsba import *
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, KFold


def mean_squared_error(model, X, y):
    return np.mean((model.predict(X) - y) **2)

def evaluate_k(save = None):
    feature_name = 'num_comments'
    target_name = 'score'
    df = fields_to_df(fielda_max=2_000,minimum_val=1)
    X = np.log2(df[[feature_name]])
    y = np.log2(df[target_name])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=4)

    train_score = []
    test_score = []
    maxk = 500
    mink = 5
    number_of_ks = 200
    xrange = np.linspace(mink, maxk, number_of_ks)
    for k_float in xrange:
        k = int(k_float)
        model = KNeighborsRegressor(k)
        model.fit(X_train, y_train)
        train_score.append(mean_squared_error(model, X_train, y_train))
        test_score.append(mean_squared_error(model, X_test, y_test))
        #train_score.append(-model.score(X_train, y_train))
        #test_score.append(-model.score(X_test, y_test))

    fig, ax = plt.subplots(figsize=(6,12))
    ax.plot(xrange, train_score, '.-r', label="train set")
    ax.plot(xrange, test_score, '.-b', label="test set")
    ax.set_xlabel('complexity (value of k)')
    ax.set_ylabel('mean squared error')
    #ax.set_ylim(2.5,3.5)
    #ax.set_xlim(50,200)
    #plt.yscale('log')
    ax.legend()
    #ax.set_xticks(xrange)
    plt.show()
    #print(xrange)
    _=plt.tight_layout()
    if save:
        filename = f'figures/knn.{target_name}-f_of-{feature_name}.png'
        _=plt.savefig(filename)
        print(f'![Figure]({filename})')
        return