import json
import pandas as pd

# Saving to JSON file
def create_json(df):
    #df.to_json('test.json', orient='records')
    text = df.to_json(orient='records')
    json_object = json.loads(text)

    json_formatted_str = json.dumps(json_object, indent = 4)

    filename = df.name.split('_')[0]+'.json'

    with open(filename, 'w') as outfile:

        outfile.write(json_formatted_str)

def get_data(str):
    f = open(str, 'r')
    data = json.load(f)
    f.close()
    a= pd.DataFrame(data)
    return a
