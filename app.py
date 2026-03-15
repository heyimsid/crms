from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random, smtplib, os, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'crms_premium_secret_key'

# ── Database ────────────────────────────────────────────────────────────
app.config['MYSQL_HOST']        = 'localhost'
app.config['MYSQL_USER']        = 'root'
app.config['MYSQL_PASSWORD']    = 'sid510'
app.config['MYSQL_DB']          = 'crms'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# ── Email Configuration ─────────────────────────────────────────────────
#
#  HOW TO SET UP GMAIL OTP:
#  ─────────────────────────
#  1. Go to your Google Account → Security
#  2. Make sure "2-Step Verification" is ON
#  3. Search for "App Passwords" in the search bar
#  4. Create an App Password (select "Mail" + "Windows Computer" or any device)
#  5. Google gives you a 16-character password like:  abcd efgh ijkl mnop
#  6. Paste that below (without spaces) as EMAIL_PASSWORD
#  7. Put your real Gmail address in EMAIL_USER and EMAIL_FROM
#
#  NOTE: Do NOT use your real Gmail login password here — only the App Password works.
#
EMAIL_HOST     = 'smtp.gmail.com'
EMAIL_PORT     = 587
EMAIL_USER     = 'nexuscrms@gmail.com'        
EMAIL_PASSWORD = '...................'   #password needed -google app        
EMAIL_FROM     = 'NEXUS Campus Resource Management System <nexuscrms@gmail.com>'  

# In-memory OTP store: { email: { otp, expires_at } }
# For production, use Redis or a DB table instead.
otp_store = {}

def send_otp_email(to_email: str, otp: str) -> bool:
    """Send OTP email via Gmail SMTP. Returns True on success, False on failure.
    OTP is ALWAYS printed to the Flask console for easy testing/debugging.
    """
    # Always print to console so you can test even without email configured
    print(f"\n{'='*50}")
    print(f"  NEXUS OTP DEBUG")
    print(f"  To:  {to_email}")
    print(f"  OTP: {otp}")
    print(f"{'='*50}\n")

    # Skip sending if credentials are still placeholder
    if 'your_gmail' in EMAIL_USER or 'your_16char' in EMAIL_PASSWORD or len(EMAIL_PASSWORD) < 10:
        print("[EMAIL] Credentials not configured — OTP printed to console above.")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'NEXUS — Your Password Reset OTP'
        msg['From']    = EMAIL_FROM
        msg['To']      = to_email

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="margin:0;padding:0;background:#f0f0f8;font-family:Arial,sans-serif;">
          <div style="max-width:480px;margin:40px auto;background:#ffffff;border:1px solid #e0e0f0;border-radius:18px;overflow:hidden;">
            <div style="padding:28px 32px 20px;border-bottom:1px solid #eeeef8;background:#4f46e5;">
              <div style="font-size:13px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:#c7c2ff;">NEXUS</div>
              <h1 style="font-size:22px;font-weight:700;color:#ffffff;margin:8px 0 0;letter-spacing:-0.02em;">Reset your password</h1>
            </div>
            <div style="padding:28px 32px;">
              <p style="color:#555577;font-size:14px;line-height:1.6;margin-bottom:24px;">
                You requested a password reset for your NEXUS account.<br>
                Use the OTP below — it expires in <strong style="color:#09090f;">10 minutes</strong>.
              </p>
              <div style="text-align:center;background:#f5f4ff;border:2px solid #c7c2ff;border-radius:12px;padding:24px 16px;margin-bottom:24px;">
                <div style="font-size:38px;font-weight:700;letter-spacing:0.22em;color:#4f46e5;font-family:monospace;">{otp}</div>
                <div style="font-size:12px;color:#888;margin-top:8px;">Expires in 10 minutes</div>
              </div>
              <p style="color:#aaaacc;font-size:12px;line-height:1.6;">
                If you didn't request this, you can safely ignore this email.<br>
                Never share this OTP with anyone.
              </p>
            </div>
            <div style="padding:16px 32px;background:#fafafa;border-top:1px solid #eee;font-size:11px;color:#aaa;text-align:center;">
              &copy; 2025 NEXUS — Campus Resource Management System
            </div>
          </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, to_email, msg.as_string())

        print(f"[EMAIL] OTP sent successfully to {to_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("[EMAIL ERROR] Authentication failed!")
        print("  → Make sure you're using a Gmail APP PASSWORD, not your real password.")
        print("  → Google Account → Security → 2-Step Verification → App Passwords")
        return False
    except smtplib.SMTPException as e:
        print(f"[EMAIL ERROR] SMTP error: {e}")
        return False
    except Exception as e:
        print(f"[EMAIL ERROR] Unexpected error: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    email    = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", [email])
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user['password'], password):
        session['user_id']       = user['user_id']
        session['name']          = user['name']
        session['role']          = user['role']
        session['department_id'] = user['department_id']
        return redirect(url_for('dashboard'))

    flash('Login failed — invalid email or password.', 'error')
    return redirect(url_for('index'))


@app.route('/register', methods=['POST'])
def register():
    name      = request.form['name']
    dept_name = request.form['department']
    email     = request.form['email']
    password  = generate_password_hash(request.form['password'])

    cur = mysql.connection.cursor()
    cur.execute("SELECT department_id FROM department WHERE department_name = %s", [dept_name])
    dept = cur.fetchone()

    if not dept:
        flash(f"Department '{dept_name}' not found.", 'error')
        cur.close()
        return redirect(url_for('index'))

    try:
        cur.execute(
            "INSERT INTO users (name, email, password, role, department_id) VALUES (%s,%s,%s,'student',%s)",
            (name, email, password, dept['department_id'])
        )
        mysql.connection.commit()
        flash('Account created! Please sign in.', 'success')
    except Exception:
        flash('Email already registered or invalid data.', 'error')

    cur.close()
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Successfully signed out.', 'success')
    return redirect(url_for('index'))


# ── FORGOT PASSWORD / OTP / RESET ────────────────────────────────────────

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    """Generate OTP, store it, and send via email. Returns JSON."""
    email = request.form.get('email', '').strip().lower()

    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id FROM users WHERE email = %s", [email])
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({'success': False, 'message': 'No account found with that email.'})

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Store with 10-minute expiry
    otp_store[email] = {
        'otp':        otp,
        'expires_at': time.time() + 600   # 10 minutes
    }

    # Send email (OTP also always printed to console for debugging)
    send_otp_email(email, otp)

    return jsonify({'success': True, 'message': 'OTP sent!'})


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    """Verify submitted OTP. Returns JSON."""
    email = request.form.get('email', '').strip().lower()
    otp   = request.form.get('otp', '').strip()

    record = otp_store.get(email)

    if not record:
        return jsonify({'success': False, 'message': 'No OTP found. Please request a new one.'})

    if time.time() > record['expires_at']:
        otp_store.pop(email, None)
        return jsonify({'success': False, 'message': 'OTP has expired. Please request a new one.'})

    if record['otp'] != otp:
        return jsonify({'success': False, 'message': 'Incorrect OTP. Please try again.'})

    # OTP verified — mark as used
    otp_store.pop(email, None)

    # Store verified email in session so reset_password can use it
    session['reset_email'] = email

    return jsonify({'success': True})


@app.route('/reset_password', methods=['POST'])
def reset_password():
    """Set new password after OTP verification."""
    email            = request.form.get('email', '').strip().lower()
    new_password     = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    # Security: must match session-stored verified email
    if session.get('reset_email') != email:
        flash('Session expired. Please start again.', 'error')
        return redirect(url_for('index'))

    if new_password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('index'))

    if len(new_password) < 8:
        flash('Password must be at least 8 characters.', 'error')
        return redirect(url_for('index'))

    hashed = generate_password_hash(new_password)

    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET password = %s WHERE email = %s", (hashed, email))
    mysql.connection.commit()
    cur.close()

    session.pop('reset_email', None)
    flash('Password reset successfully! Please sign in.', 'success')
    return redirect(url_for('index'))


# ── DASHBOARD ─────────────────────────────────────────────────────────────

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    cur = mysql.connection.cursor()

    all_users = all_issues = all_depts = []
    if session['role'] == 'admin':
        cur.execute("""
            SELECT u.user_id, u.name, u.email, u.role, d.department_name
            FROM users u
            LEFT JOIN department d ON u.department_id = d.department_id
            ORDER BY u.role, u.name
        """)
        all_users = cur.fetchall()

        cur.execute("""
            SELECT i.issue_id,
                   COALESCE(r.resource_name, 'General/Other Issue') AS resource_name,
                   u.name AS reported_by, i.description, i.status
            FROM issues i
            LEFT JOIN resources r ON i.resource_id = r.resource_id
            JOIN users u ON i.reported_by = u.user_id
            ORDER BY i.status DESC
        """)
        all_issues = cur.fetchall()

        cur.execute("SELECT * FROM department")
        all_depts = cur.fetchall()

    cur.execute("SELECT * FROM resources WHERE status = 'available'")
    resources = cur.fetchall()

    cur.execute("""
        SELECT b.booking_id, r.resource_name, b.booking_date,
               b.time_slot, b.status, b.purpose
        FROM bookings b
        JOIN resources r ON b.resource_id = r.resource_id
        WHERE b.user_id = %s
        ORDER BY b.booking_date DESC
    """, [session['user_id']])
    my_bookings = cur.fetchall()

    cur.execute("""
        SELECT r.resource_name, b.booking_date, b.time_slot, b.status
        FROM bookings b
        JOIN resources r ON b.resource_id = r.resource_id
        WHERE b.status IN ('approved','pending') AND b.booking_date >= CURDATE()
        ORDER BY b.booking_date ASC, b.time_slot ASC
    """)
    campus_schedule = cur.fetchall()

    cur.execute("""
        SELECT i.issue_id, COALESCE(r.resource_name,'General/Other Issue') AS resource_name,
               i.description, i.status
        FROM issues i
        LEFT JOIN resources r ON i.resource_id = r.resource_id
        WHERE i.reported_by = %s
    """, [session['user_id']])
    my_issues = cur.fetchall()

    approvals = []
    if session['role'] == 'hod':
        cur.execute("""
            SELECT b.booking_id, u.name,
                   req_dept.department_name AS requester_dept,
                   r.resource_name, b.booking_date, b.time_slot, b.purpose
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            LEFT JOIN department req_dept ON u.department_id = req_dept.department_id
            JOIN resources r ON b.resource_id = r.resource_id
            WHERE b.department_id = %s AND b.status = 'pending'
        """, [session['department_id']])
        approvals = cur.fetchall()
    elif session['role'] == 'admin':
        cur.execute("""
            SELECT b.booking_id, u.name,
                   req_dept.department_name AS requester_dept,
                   r.resource_name, b.booking_date, b.time_slot, b.purpose
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            LEFT JOIN department req_dept ON u.department_id = req_dept.department_id
            JOIN resources r ON b.resource_id = r.resource_id
            WHERE b.department_id = 99 AND b.status = 'pending'
        """)
        approvals = cur.fetchall()

    cur.close()

    if session['role'] == 'admin':
        return render_template('dashboard.html',
            users=all_users, issues=all_issues, departments=all_depts,
            resources=resources, bookings=my_bookings,
            my_issues=my_issues, approvals=approvals,
            campus_schedule=campus_schedule)
    else:
        return render_template('dashboard.html',
            resources=resources, bookings=my_bookings,
            my_issues=my_issues, approvals=approvals,
            campus_schedule=campus_schedule)


# ── BOOKING ───────────────────────────────────────────────────────────────

@app.route('/book', methods=['POST'])
def book():
    if 'user_id' not in session or 'department_id' not in session:
        session.clear()
        flash('Session invalid. Please sign in again.', 'error')
        return redirect(url_for('index'))

    start_str   = request.form['start_time']
    end_str     = request.form['end_time']
    time_slot   = f"{start_str} to {end_str}"
    purpose     = request.form['purpose']
    resource_id = request.form['resource_id']
    booking_date= request.form['date']

    try:
        req_start = datetime.strptime(start_str, '%H:%M').time()
        req_end   = datetime.strptime(end_str,   '%H:%M').time()
        if req_start >= req_end:
            flash('Invalid time: end time must be after start time.', 'error')
            return redirect(url_for('dashboard'))
    except ValueError:
        flash('Invalid time format.', 'error')
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()

    cur.execute("SELECT department_id FROM resources WHERE resource_id = %s", [resource_id])
    res_data = cur.fetchone()
    if not res_data:
        flash('Invalid resource selected.', 'error')
        return redirect(url_for('dashboard'))

    resource_dept_id = res_data['department_id']

    cur.execute(
        "SELECT time_slot FROM bookings WHERE resource_id=%s AND booking_date=%s AND status!='rejected'",
        (resource_id, booking_date)
    )
    conflict = False
    for b in cur.fetchall():
        try:
            b_s, b_e = b['time_slot'].split(' to ')
            bs = datetime.strptime(b_s.strip(), '%H:%M').time()
            be = datetime.strptime(b_e.strip(), '%H:%M').time()
            if req_start < be and req_end > bs:
                conflict = True
                break
        except ValueError:
            continue

    if conflict:
        flash('Resource is already booked during this time. Please choose another slot.', 'error')
    else:
        cur.execute(
            "INSERT INTO bookings (booking_date, time_slot, user_id, resource_id, department_id, purpose) VALUES (%s,%s,%s,%s,%s,%s)",
            (booking_date, time_slot, session['user_id'], resource_id, resource_dept_id, purpose)
        )
        mysql.connection.commit()
        flash('Booking request submitted successfully!', 'success')

    cur.close()
    return redirect(url_for('dashboard'))


# ── APPROVE / REJECT ──────────────────────────────────────────────────────

@app.route('/approve/<int:booking_id>')
def approve(booking_id):
    if session.get('role') not in ['hod', 'admin']:
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT department_id FROM bookings WHERE booking_id = %s", [booking_id])
    b = cur.fetchone()

    if not b:
        flash('Booking not found.', 'error')
        return redirect(url_for('dashboard'))

    authorized = (
        (session['role'] == 'hod'   and b['department_id'] == session['department_id']) or
        (session['role'] == 'admin' and b['department_id'] == 99)
    )

    if not authorized:
        flash('Unauthorized: you cannot approve this booking.', 'error')
        cur.close()
        return redirect(url_for('dashboard'))

    cur.execute("UPDATE bookings SET status='approved', approved_by=%s WHERE booking_id=%s",
                (session['user_id'], booking_id))
    mysql.connection.commit()
    cur.close()
    flash('Booking approved.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/reject/<int:booking_id>')
def reject(booking_id):
    if session.get('role') not in ['hod', 'admin']:
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT department_id FROM bookings WHERE booking_id = %s", [booking_id])
    b = cur.fetchone()

    if not b:
        flash('Booking not found.', 'error')
        return redirect(url_for('dashboard'))

    authorized = (
        (session['role'] == 'hod'   and b['department_id'] == session['department_id']) or
        (session['role'] == 'admin' and b['department_id'] == 99)
    )

    if not authorized:
        flash('Unauthorized: you cannot reject this booking.', 'error')
        cur.close()
        return redirect(url_for('dashboard'))

    cur.execute("UPDATE bookings SET status='rejected', approved_by=%s WHERE booking_id=%s",
                (session['user_id'], booking_id))
    mysql.connection.commit()
    cur.close()
    flash('Booking rejected.', 'success')
    return redirect(url_for('dashboard'))


# ── CANCEL BOOKING ────────────────────────────────────────────────────────

@app.route('/cancel_booking/<int:booking_id>')
def cancel_booking(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bookings WHERE booking_id=%s AND user_id=%s",
                (booking_id, session['user_id']))
    booking = cur.fetchone()

    if not booking:
        flash('Unauthorized: you can only cancel your own bookings.', 'error')
        cur.close()
        return redirect(url_for('dashboard'))

    cur.execute("DELETE FROM bookings WHERE booking_id=%s", [booking_id])
    mysql.connection.commit()
    cur.close()
    flash('Booking cancelled.', 'success')
    return redirect(url_for('dashboard'))


# ── REPORT ISSUE ──────────────────────────────────────────────────────────

@app.route('/report_issue', methods=['POST'])
def report_issue():
    if 'user_id' not in session or 'department_id' not in session:
        session.clear()
        flash('Session invalid. Please sign in again.', 'error')
        return redirect(url_for('index'))

    res_id       = request.form['resource_id']
    final_res_id = None if res_id == '0' else res_id
    owner_dept   = session['department_id']

    cur = mysql.connection.cursor()

    if final_res_id:
        cur.execute("SELECT department_id FROM resources WHERE resource_id=%s", [final_res_id])
        rd = cur.fetchone()
        if rd:
            owner_dept = rd['department_id']

    cur.execute(
        "INSERT INTO issues (resource_id, reported_by, department_id, description, status) VALUES (%s,%s,%s,%s,'open')",
        (final_res_id, session['user_id'], owner_dept, request.form['description'])
    )
    mysql.connection.commit()
    cur.close()
    flash('Issue reported successfully.', 'success')
    return redirect(url_for('dashboard'))


# ── RESOLVE ISSUE ─────────────────────────────────────────────────────────

@app.route('/resolve_issue/<int:issue_id>')
def resolve_issue(issue_id):
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("UPDATE issues SET status='resolved' WHERE issue_id=%s", (issue_id,))
    mysql.connection.commit()
    cur.close()
    flash('Issue marked as resolved.', 'success')
    return redirect(url_for('dashboard'))


# ── ADD RESOURCE ──────────────────────────────────────────────────────────

@app.route('/add_resource', methods=['POST'])
def add_resource():
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))

    resource_type = request.form.get('resource_type')

    if resource_type == 'Centralised Facility':
        dept_id = 99
    else:
        dept_id = request.form.get('department_id')
        if not dept_id:
            flash('Please select a department.', 'error')
            return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "INSERT INTO resources (resource_name, resource_type, status, department_id) VALUES (%s,%s,'available',%s)",
            (request.form['resource_name'], resource_type, dept_id)
        )
        mysql.connection.commit()
        flash(f"Resource '{request.form['resource_name']}' added successfully.", 'success')
    except Exception as e:
        flash('Database error: could not add resource. Check ENUM settings.', 'error')
        print('[DB ERROR]', e)
    finally:
        cur.close()

    return redirect(url_for('dashboard'))


# ── CHANGE ROLE ───────────────────────────────────────────────────────────

@app.route('/admin/change_role/<int:target_user_id>', methods=['POST'])
def change_role(target_user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))

    if target_user_id == session['user_id']:
        flash('You cannot change your own Admin role.', 'error')
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET role=%s WHERE user_id=%s",
                (request.form.get('new_role'), target_user_id))
    mysql.connection.commit()
    cur.close()
    flash('User role updated successfully.', 'success')
    return redirect(url_for('dashboard'))


# ─────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
