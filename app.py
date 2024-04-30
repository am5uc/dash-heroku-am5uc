import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])
mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')
gss_gender_mean = gss_clean.groupby('sex').agg({'income': 'mean', 'job_prestige':'mean', 'socioeconomic_index':'mean', 'education':'mean'})
gss_gender_mean = gss_gender_mean.reset_index()
gss_gender_mean[['income', 'job_prestige', 'socioeconomic_index', 'education']] = gss_gender_mean[['income', 'job_prestige', 'socioeconomic_index', 'education']].round(2)
gss_gender_mean.columns = ['Gender', 'Income', 'Occupational Prestige', 'Socioeconomic Index', 'Years of Education']
table = ff.create_table(gss_gender_mean)
breadwinner_bar = gss_clean.groupby('sex').male_breadwinner.value_counts().reset_index()
figBarplot = px.bar(breadwinner_bar, x='male_breadwinner', y='count', color = 'sex',
      labels={'male_breadwinner': 'Better if man is the achiever outside the home and the woman takes care of the home and family?'},
      text = 'count', barmode = 'group')
figScatterplot = px.scatter(gss_clean, x='job_prestige', y='income', color='sex', 
                 trendline='ols',
                 height=600, width=600,
                 labels={'job_prestige':'Occupational Prestige', 
                        'income':'Annual Income'},
                 hover_data=['education', 'socioeconomic_index'])
figScatterplot.update(layout=dict(title=dict(x=0.5)))
box_income = px.box(gss_clean, x='income', y = 'sex',
                   labels={'income':'Annual Income', 'sex':'Gender'})
box_income.update(layout=dict(title=dict(x=0.5)))
box_prestige = px.box(gss_clean, x='job_prestige', y = 'sex',
                   labels={'job_prestige':'Occupational Prestige', 'sex':'Gender'})
box_prestige.update(layout=dict(title=dict(x=0.5)))
newDf = gss_clean[['income', 'sex', 'job_prestige']]
newDf['job_prestige_category'] = pd.cut(newDf['job_prestige'], bins=6, labels=False)
newDf = newDf.dropna()
newDf = newDf.sort_values(by = 'job_prestige_category')
figBoxFacet = px.box(newDf, x='sex', y='income', color='sex', facet_col= 'job_prestige_category', facet_col_wrap = 2, color_discrete_map = {'male':'blue', 'female':'red'})
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div( 
    style={'backgroundColor': 'navy'}, children =
    [
        html.H1('Investigation of Annual Income, Gender, and Occupational Prestige', style={'color': 'white'}), 
        
        dcc.Markdown('''
According to an article by the Pew Research Center, "Gender pay gap in U.S. hasn't changed much in two decades", there has been a wage gap between men and women. Women seem to earn about 82% of what men earned, according to median hourly earnings of both full-time and part-time workers. However, when just looking at workers between the ages of 25 to 34, this gap is smaller. A lot of the gender gap can be addtributed to differences in education, occupational segregation, and years of work experience. Women do work in a lot of lowerpaying occupations. Balancing family and the work may be another reason, as working mothers feel more pressure to focus on home and children. Meanwhile, working fathers feel more pressure to support thier family in financial terms. In addition, there are more men than women who are bossses or top managers where they work. This overall probably contributes to the wage gap disparity. This information was gathered from https://www.pewresearch.org/short-reads/2023/03/01/gender-pay-gap-facts/
The GSS, also known as General Social Survey, is a nationally conducted survey on adults. It collects opionions and attitudes of American adults on a variety of topics such as crime, morality, and social mobility. It gathers and investigates changes in attitudes and social charactersitics in the U.S. This information was gathered from http://www.gss.norc.org/About-The-GSS.
        
        ''', style={'color': 'white'}),
        
        #dcc.Dropdown(id ='features', options =  sorted(vacounties.columns), value = 'Average Annual Pay'), ## Step 1
        html.H2("Average Income, Occupational Prestige, Socioeconomic Index, and Years of Education by Gender", style={'color': 'white'}),
        dcc.Graph(figure=table),
        html.H2("Attitude on Job Satisfaction, Working Mother's relationships with children, Gender and politics, Suffering caused by mothers working, and Men Overworking on Family, by sex, region, and education", style={'color': 'white'}),
        dcc.Dropdown(id ='features', options =  ['satjob', 'relationship', 'male_breadwinner', 'men_bettersuited', 'child_suffer',  'men_overwork'], value = 'satjob'),
        dcc.Dropdown(id ='groupby', options =  ['sex', 'region', 'education'], value = 'sex'),
        dcc.Graph(id='figBarplot'),
        html.H2("Annual Income by Occupational Prestige and Gender", style={'color': 'white'}),
        dcc.Graph(figure=figScatterplot),
        html.H2("Distribution of Incomes by Gender", style={'color': 'white'}),
        dcc.Graph(figure=box_income),
        html.H2("Distribution of Occupational Prestige by Gender", style={'color': 'white'}),
        dcc.Graph(figure=box_prestige),
        html.H2("Distribution of Annual Income by Occupational Prestige Category and Gender", style={'color': 'white'}),
        dcc.Graph(figure=figBoxFacet),
    
    ]
    
)

## Callbacks (how users interact with the dashboard)
@app.callback(Output(component_id='figBarplot', component_property = 'figure'), #Step 4
             [Input(component_id='features', component_property = 'value'), 
             Input(component_id='groupby', component_property = 'value')]) #Step 2


#figBarplot = px.bar(breadwinner_bar, x='male_breadwinner', y='count', color = 'sex',
 #     labels={'male_breadwinner': 'Better if man is the achiever outside the home and the woman takes care of the home and family?'},
  #    text = 'count', barmode = 'group')

def makebar(feature, group):
    breadwinner_bar = gss_clean.groupby(group)[feature].value_counts().reset_index()
    
    figBarplot = px.bar(breadwinner_bar, x= feature, y='count', color = group,
    labels={'male_breadwinner': 'Better if man is the achiever outside the home and the woman takes care of the home and family?',
           'sat_job': 'Job Satisfaction',
           'relationship' : 'Working mother relationship with children just as warm and secure a relationship as mother who does not work.',
           'men_bettersuited': 'Most men are better suited emotionally for politics than are most women',
           'child_suffer': 'A preschool child is likely to suffer if his or her mother works',  
           'men_overwork': 'Family life often suffers because men concentrate too much on their work'},
    text = 'count', barmode = 'group')
    return figBarplot


if __name__ == '__main__':
    app.run_server(debug=True)
