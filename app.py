from dateutil.parser import parse
from flask import Flask, render_template

import xlrd
from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField
from wtforms.fields.html5 import DateField


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Changeme'


def open_sheet(filename, sheetname):
    wb = xlrd.open_workbook(filename)
    return wb.sheet_by_name(sheetname)


def read_table(sheet, columnnames, header_row=0):
    name_to_index = {
        c.value: i for i, c
        in enumerate(sheet.row(header_row))
        if c.ctype == xlrd.XL_CELL_TEXT}

    column_indices = [name_to_index[n] for n in columnnames]
    for rowindex in range(header_row + 1, sheet.nrows):
        row = sheet.row(rowindex)
        if len(set([i.value for i in row])) < 2:
            break
        yield dict(zip(columnnames, (row[x].value for x in column_indices)))


def get_records():
    from datetime import datetime

    coloumns = [
        'Date of Submission',
        'BU',
        'Client Feedback'
    ]

    rows = read_table(
        open_sheet("/cygdrive/c/File/Master-Tracker.xlsx", "Master Tracker"),
        coloumns,
        0
    )

    total_records = [row for row in rows]

    for record in total_records:
        try:
            record['Date of Submission'] = datetime(*xlrd.xldate_as_tuple(record['Date of Submission'], datemode=0)).date().isoformat()
        except TypeError:
            continue

    return total_records


@app.route('/beat', methods=['GET'])
def beat():
    from flask import request

    total_records = get_records()

    class Form(FlaskForm):
        business_units = SelectField(
            'Business Units',
            choices=[(i, i) for i in list(set([record['BU'] for record in total_records if record['BU']]))],
            default='All'
        )

    class DateForm(FlaskForm):
        from_date = DateField('From Date', format='%Y-%m-%d')
        to_date = DateField('To Date', format='%Y-%m-%d')
        business_units = HiddenField()

    form = Form()
    date_form = DateForm()

    def get_final_records(total_records):
        fields = [
            'L1 Stage',
            'L2 Stage',
            'L1 Reject',
            'L2 Reject',
            'Screen Reject',
            'Final Select',
            'Offered',
            'Joined',
            'HOLD/Closed',
            'Pending Feedback'
        ]
        result = {
            'Total Submission': len(total_records)
        }
        _tmp = {
            result.update({field: len([i for i in total_records if i['Client Feedback'] == field])})
            for field in fields
        }
        return result

    if request.args.get('business_units'):
        business_units = request.args.get('business_units')
        total_records = [i for i in total_records if i['BU'] == business_units]

    if request.args.get('from_date'):
        from_date = request.args.get('from_date')
        total_records = [i for i in total_records if i['Date of Submission'] and parse(i['Date of Submission']) >= parse(from_date)]

    if request.args.get('to_date'):
        to_date = request.args.get('to_date')
        total_records = [i for i in total_records if i['Date of Submission'] and parse(i['Date of Submission']) <= parse(to_date)]

    return render_template(
        'main.html',
        result=get_final_records(total_records),
        form=form,
        date_form=date_form,
        selected=request.args.get('business_units')
    )
