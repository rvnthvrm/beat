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
        yield dict(zip(columnnames, (row[x].value for x in column_indices)))


def get_records():
    from datetime import datetime

    coloumns = [
        'Day',
        'BU',
        'Skill',
        'Candidate Name',
        'Mobile Number',
        'Drive',
        'L1/L2/Final',
        'Time',
        'Panel',
        'Status',
        'Comments/Reasons',
        'MR Links',
        'Recruiter Name'
    ]

    rows = read_table(
        open_sheet("/cygdrive/c/Users/Master-Tracker.xlsx", "Schedule Tracker"),
        coloumns,
        0
    )
    total_records = [row for row in rows]
    for record in total_records:
        try:
            record['Day'] = datetime(*xlrd.xldate_as_tuple(record['Day'], datemode=0)).date().isoformat()
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
        return {
            'Total Submission': len(total_records),
            'Level 1': len([i for i in total_records if i['L1/L2/Final'] == 'L1']),
            'Level 2': len([i for i in total_records if i['L1/L2/Final'] == 'L2']),
            'Level 3/Final Stage': len([i for i in total_records if i['L1/L2/Final'] == 'L3']),
            'Level 4/Offered': len([i for i in total_records if i['L1/L2/Final'] == 'L4']),
            'Pending Feedback': len([i for i in total_records if i['Status'] == 'Pending Feedback'])
        }

    if request.args.get('business_units'):
        business_units = request.args.get('business_units')
        total_records = [i for i in total_records if i['BU'] == business_units]

    if request.args.get('from_date'):
        from_date = request.args.get('from_date')
        total_records = [i for i in total_records if i['Day'] and parse(i['Day'] >= parse(from_date))]

    if request.args.get('to_date'):
        to_date = request.args.get('to_date_date')
        total_records = [i for i in total_records if i['Day'] and parse(i['Day'] <= parse(to_date))]

    return render_template(
        'main.html',
        result=get_final_records(total_records),
        form=form,
        date_form=date_form,
        selected=request.args.get('business_units')
    )
