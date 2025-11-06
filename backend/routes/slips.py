from flask import Blueprint, request, jsonify, render_template
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection, get_next_bill_no
from datetime import datetime

slips_bp = Blueprint('slips', __name__)

def calculate_fields(data):
    """Calculate all computed fields"""
    bags = float(data.get('bags', 0))
    avg_bag_weight = float(data.get('avg_bag_weight', 0))
    rate = float(data.get('rate', 0))
    bank_commission = float(data.get('bank_commission', 0))
    batav_percent = float(data.get('batav_percent', 1))
    shortage_percent = float(data.get('shortage_percent', 1))
    dalali_rate = float(data.get('dalali_rate', 10))
    hammali_rate = float(data.get('hammali_rate', 10))
    freight = float(data.get('freight', 0))
    rate_diff = float(data.get('rate_diff', 0))
    quality_diff = float(data.get('quality_diff', 0))
    moisture_ded = float(data.get('moisture_ded', 0))
    tds = float(data.get('tds', 0))

    net_weight = round(bags * avg_bag_weight, 2)
    amount = round(net_weight * rate, 2)
    batav = round(amount * (batav_percent / 100), 2)
    shortage = round(amount * (shortage_percent / 100), 2)
    dalali = round(net_weight * dalali_rate, 2)
    hammali = round(net_weight * hammali_rate, 2)
    total_deduction = round(bank_commission + batav + shortage + dalali + hammali + freight + rate_diff + quality_diff + moisture_ded + tds, 2)
    payable_amount = round(amount - total_deduction, 2)

    data.update({
        'net_weight': net_weight,
        'amount': amount,
        'batav': batav,
        'shortage': shortage,
        'dalali': dalali,
        'hammali': hammali,
        'freight': freight,
        'rate_diff': rate_diff,
        'quality_diff': quality_diff,
        'moisture_ded': moisture_ded,
        'tds': tds,
        'total_deduction': total_deduction,
        'payable_amount': payable_amount
    })
    return data

@slips_bp.route('/api/add-slip', methods=['POST'])
def add_slip():
    """Add a new purchase slip"""
    try:
        data = request.json
        data = calculate_fields(data)

        bill_no = get_next_bill_no()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO purchase_slips (
                company_name, company_address, document_type, vehicle_no, date,
                bill_no, party_name, material_name, ticket_no, broker,
                terms_of_delivery, sup_inv_no, gst_no, bags, avg_bag_weight,
                net_weight, rate, amount, bank_commission, batav_percent, batav,
                shortage_percent, shortage, dalali_rate, dalali, hammali_rate,
                hammali, freight, rate_diff, quality_diff, moisture_ded, tds,
                total_deduction, payable_amount, payment_method,
                payment_date, payment_amount, prepared_by, authorised_sign
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data.get('company_name', ''),
            data.get('company_address', ''),
            data.get('document_type', 'Purchase Slip'),
            data.get('vehicle_no', ''),
            data.get('date'),
            bill_no,
            data.get('party_name', ''),
            data.get('material_name', ''),
            data.get('ticket_no', ''),
            data.get('broker', ''),
            data.get('terms_of_delivery', ''),
            data.get('sup_inv_no', ''),
            data.get('gst_no', ''),
            data.get('bags', 0),
            data.get('avg_bag_weight', 0),
            data.get('net_weight', 0),
            data.get('rate', 0),
            data.get('amount', 0),
            data.get('bank_commission', 0),
            data.get('batav_percent', 1),
            data.get('batav', 0),
            data.get('shortage_percent', 1),
            data.get('shortage', 0),
            data.get('dalali_rate', 10),
            data.get('dalali', 0),
            data.get('hammali_rate', 10),
            data.get('hammali', 0),
            data.get('freight', 0),
            data.get('rate_diff', 0),
            data.get('quality_diff', 0),
            data.get('moisture_ded', 0),
            data.get('tds', 0),
            data.get('total_deduction', 0),
            data.get('payable_amount', 0),
            data.get('payment_method', ''),
            data.get('payment_date', ''),
            data.get('payment_amount', 0),
            data.get('prepared_by', ''),
            data.get('authorised_sign', '')
        ))

        slip_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Purchase slip saved successfully',
            'slip_id': slip_id,
            'bill_no': bill_no
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@slips_bp.route('/api/slips', methods=['GET'])
def get_slips():
    """Get all purchase slips"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('''
            SELECT id, date, bill_no, party_name, material_name,
                   net_weight, payable_amount, created_at
            FROM purchase_slips
            ORDER BY id DESC
        ''')

        slips = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'slips': slips
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@slips_bp.route('/api/slip/<int:slip_id>', methods=['GET'])
def get_slip(slip_id):
    """Get a single purchase slip by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM purchase_slips WHERE id = %s', (slip_id,))
        slip = cursor.fetchone()
        cursor.close()
        conn.close()

        if slip is None:
            return jsonify({
                'success': False,
                'message': 'Slip not found'
            }), 404

        return jsonify({
            'success': True,
            'slip': slip
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@slips_bp.route('/api/slip/<int:slip_id>', methods=['DELETE'])
def delete_slip(slip_id):
    """Delete a purchase slip"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM purchase_slips WHERE id = %s', (slip_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Slip deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@slips_bp.route('/print/<int:slip_id>')
def print_slip(slip_id):
    """Render print template for a slip"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM purchase_slips WHERE id = %s', (slip_id,))
        slip = cursor.fetchone()
        cursor.close()
        conn.close()

        if slip is None:
            return "Slip not found", 404

        return render_template('print_template.html', slip=slip)

    except Exception as e:
        return str(e), 400
