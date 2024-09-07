from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Read the Excel file
            df = pd.read_excel(file)

            # Calculate metrics
            ready_to_ship = df[df['Current Status'] == 'READY_TO_SHIP']
            out_for_delivery = df[df['Current Status'] == 'OUT_FOR_DELIVERY']
            returned_to_origin = df[df['Current Status'] == 'RETURNED_TO_ORIGIN']
            returning_to_origin = df[df['Current Status'] == 'RETURNING_TO_ORIGIN']

            # Breach count logic
            today = pd.Timestamp(datetime.today().date())
            undelivered_df = df[df['Status Type'] == 'Undelivered']
            breach_count = undelivered_df[undelivered_df['Estimated Delivery Date'] + pd.Timedelta(days=1) < today]
            breach_references = breach_count[['Reference No.', 'Waybill', 'Seller Name', 'Product Description', 
                                              'Pick Up Date', 'Estimated Delivery Date', 'Status Type', 'Current Status']]

            # Prepare data for rendering
            metrics_data = {
                'ready_to_ship': len(ready_to_ship),
                'out_for_delivery': len(out_for_delivery),
                'returned_to_origin': len(returned_to_origin),
                'returning_to_origin': len(returning_to_origin),
                'breach_count': len(breach_count),
                'ready_to_ship_details': ready_to_ship.to_dict(orient='records'),
                'out_for_delivery_details': out_for_delivery.to_dict(orient='records'),
                'returned_to_origin_details': returned_to_origin.to_dict(orient='records'),
                'returning_to_origin_details': returning_to_origin.to_dict(orient='records'),
                'reference_list': breach_references.to_dict(orient='records')
            }

            # Render the dashboard template with the metrics data
            return render_template('dashboard.html', **metrics_data)
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
