from functions.roi_associated import *
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
def masked(df,name,nest = False):
    prob = df[[name + '_likelihood']].values.squeeze()
    from analysis import pcutoff
    mask = prob < pcutoff
    df[name+'_x'] = np.ma.array(
        df[[name + "_x"]].values.squeeze(),
        mask=mask,
    )
    df[name+'_y'] = np.ma.array(
        df[[name + "_y"]].values.squeeze(),
        mask=mask,
    )
    if nest is not False:
        df['nest'] = np.ma.array(
            df[['nest']].values.squeeze(),
            mask=mask,
        )
    return df

def plot_trajectory(df,name,bg=None,lm=None,pixel_per_cm=None):
    ori=df
    fig = plt.figure()
    fig.dpi = 300
    if bg is None:
        plt.gca().invert_yaxis()
    else:
        bg = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)
        plt.imshow(bg)

    df = masked(df,name)
    x = df[name+'_x']
    y = df[name+'_y']

    # print(max(x))
    # print(x.idxmax())

    if pixel_per_cm is not None:
        x = x / pixel_per_cm
        y = y / pixel_per_cm
        x = x - (max(x) + min(x)) / 2
        y = y - (max(y) + min(y)) / 2
        plt.xlabel('(cm)')
        plt.ylabel('(cm)')
    else:
        plt.xlabel('(pixel)')
        plt.ylabel('(pixel)')

    plt.plot(x, y,linewidth = 0.7, color='red')
    # if lm != None:
    #     plt.axis(lm)

    # fancy but slow & blurry one:
    # l = len(df)
    # for i in range(l-2):
    #     plt.plot(x[i:i+2], y[i:i+2], color='red', alpha=0.2)

    plt.show()
    df=ori

def center_of_gravity(df):
    outer_bodyparts=['leftear','nose','rightear','rightbody1','rightbody2','rightbody3','rightbody4','rightbody5',
                    'tailbase','leftbody5','leftbody4','leftbody3','leftbody2','leftbody1']
    df['centroid_x'] = [0] * len(df)
    df['centroid_y'] = [0] * len(df)
    df['centroid_likelihood'] = [0] * len(df)

    for t in range(len(df)):
        li = 1
        points = []
        for i in range(len(outer_bodyparts)):
            bodypart = outer_bodyparts[i]

            x = df[bodypart+'_x'][t]
            y = df[bodypart+'_y'][t]
            pt = (x,y)
            points.append(pt)
            li = min(li,df[bodypart+'_likelihood'][t])
        p = Polygon(points)
        c = p.centroid.coords[0]
        df['centroid_x'][t] = c[0]
        df['centroid_y'][t] = c[1]
        df['centroid_likelihood'][t]=li
    return df

def gen_trajectory(frame,Dataframe,name,show_image=True):
    frame_c = frame.copy()
    M,corrected_coor,pixel_per_cm = corrected(frame_c)
    result = cv2.warpPerspective(frame, M, frame.shape[1::-1])

    Dataframe_t = Dataframe.copy()
    bodyparts = ['nose','leftear','rightear','headstage','leftbody1','leftbody2','leftbody3','leftbody4',
                 'leftbody5','rightbody1','rightbody2','rightbody3','rightbody4','rightbody5','centerbody1',
                 'centerbody2','centerbody3','centerbody4','centerbody5','tailbase','tailtip',
                 'tail1','tail2','tail3']
    for name_bp in bodyparts:
        Dataframe_t = transform(Dataframe_t,name_bp,M)

    if show_image:
        plot_trajectory(Dataframe_t, name,bg=result)
        # plot_trajectory(Dataframe_t, name, pixel_per_cm = pixel_per_cm)
        # plot_trajectory(Dataframe_t,name,lm=[corrected_coor[0][0],corrected_coor[2][0],corrected_coor[0][1],corrected_coor[2][1]])

    return pixel_per_cm,Dataframe_t
