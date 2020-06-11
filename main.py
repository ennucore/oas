import flask
import json
import pymorphy2


app = flask.Flask(__name__)
morph = pymorphy2.MorphAnalyzer()
num_words = json.loads(open('words.json').read())
measures = json.loads(open('measures.json').read())


def parse(words, last_number=None, current_number=0, accumulated=0):
    if not len(words):
        return current_number
    word = words[0]
    try:
        return parse(words[1:], float(word), current_number + float(word), accumulated + float(word))
    except ValueError:
        variants = morph.parse(word)
        for var in variants:
            if 'NUM' in var.tag.POS or var.tag.POS == 'NOUN':
                variant = var
                nf = variant.normal_form.lower()
                break
        else:
            print('word not found')
            variant = nf = word.lower()
        if nf in measures:
            measure = measures[nf]
            return parse(words[1:], None, current_number * measure)
        if nf not in num_words:
            print('word is not in num_words:', nf)
            return parse(words[1:], last_number, current_number)
        value = num_words[nf]
        if last_number is None or value < last_number:
            return parse(words[1:], value, current_number + value, accumulated + value)
        else:
            return parse(words[1:], None, current_number + accumulated * (value - 1))


@app.route('/', methods=['POST', 'GET'])
def index():
    if flask.request.method == 'GET':
        return flask.render_template('index.html')
    else:
        query = flask.request.form['query']
        what_to_convert = query.split(' в ')[0].strip().split(' ')
        target = query.split(' в ')[1].strip()
        target = next(filter(lambda parsed: parsed.tag.POS == 'NOUN', morph.parse(target)))
        target = measures.get(target.normal_form, 1)
        return flask.render_template('index.html', result=parse(what_to_convert) / target, query=query)


if __name__ == '__main__':
    app.run(port=7080)

