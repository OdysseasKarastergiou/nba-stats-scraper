from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from .scraper import scrape_nba_stats
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from app import db
import pandas as pd
import numpy as np
import json

main = Blueprint('main', __name__)

@main.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    login_error = None
    register_error = None
    
    # Handle login form submission
    if request.method == 'POST' and 'login_submit' in request.form:
        username = request.form.get('login_username')
        password = request.form.get('login_password')
        
        user = User.authenticate(username, password)
        if user:
            login_user(user)
            user.update_last_login()
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        else:
            login_error = 'Invalid username or password'
    
    # Handle registration form submission
    if request.method == 'POST' and 'register_submit' in request.form:
        username = request.form.get('register_username')
        email = request.form.get('register_email')
        password = request.form.get('register_password')
        confirm_password = request.form.get('register_confirm_password')
        
        # Validate form data
        if User.query.filter_by(username=username).first():
            register_error = 'Username already exists'
        elif User.query.filter_by(email=email).first():
            register_error = 'Email already exists'
        elif password != confirm_password:
            register_error = 'Passwords do not match'
        else:
            # Create new user
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            
            # Log in the new user
            login_user(new_user)
            flash('Registration successful! Welcome to NBA Stats!', 'success')
            return redirect(url_for('main.index'))
    
    return render_template('dashboard.html', 
                           login_error=login_error, 
                           register_error=register_error)

@main.route('/')
def index():
    data = scrape_nba_stats()
    
    # Convert to DataFrame for sorting
    df = pd.DataFrame(data)
    
    # Columns to exclude from the tables
    columns_to_exclude = ['Rk', 'Age', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'Awards']
    
    # Filter columns for display (keep only columns not in the exclude list)
    display_columns = [col for col in df.columns if col not in columns_to_exclude]
    filtered_df = df[display_columns]
    
    # Sort by points (PTS) and get top 20 for Points Leaders
    points_leaders = filtered_df.sort_values(by='PTS', ascending=False).head(10).to_dict(orient='records')
    
    # Sort by 3P% and get top 20 for 3PT Leaders
    # Only include players with at least 5 three-point attempts
    three_pt_df = filtered_df[filtered_df['3PA'] >= 5]  # Filter players with 5+ 3-point attempts
    three_pt_leaders = three_pt_df.sort_values(by='3P%', ascending=False).head(10).to_dict(orient='records')
    
    # Prepare data for the scatter plot
    # For each player, we need their name, points, and field goal percentage
    chart_data = []
    for _, row in df.iterrows():
        try:
            # Convert PTS and FG% to numeric values
            pts = float(row['PTS']) if pd.notna(row['PTS']) else 0
            fg_pct = float(row['FG%']) if pd.notna(row['FG%']) else 0
            
            # Skip rows where either value is NaN or invalid
            if np.isnan(pts) or np.isnan(fg_pct):
                continue
                
            chart_data.append({
                'name': row['Player'],
                'pts': pts,
                'fg_pct': fg_pct
            })
        except (ValueError, TypeError):
            # Skip rows with invalid data
            continue
    
    # Convert to JSON-safe format
    chart_data_json = json.dumps(chart_data)
    
    return render_template('index.html', 
                          points_leaders=points_leaders, 
                          three_pt_leaders=three_pt_leaders,
                          chart_data=chart_data_json)

@main.route('/api/stats')
def api_stats():
    return jsonify(scrape_nba_stats())

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')