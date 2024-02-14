#! /home/russell/venv/bin/python3

import psycopg2
from datetime import date
import os
import tkinter as tk
from tkinter import filedialog
import subprocess
from django.utils.text import slugify
import pipes  # Import the pipes module for proper shell escaping

search_directory = "/var/www/media"
media_directory = "/var/www/media"
book_directory = "/var/www/media/Audio_Books"
envfile_directory = "/home/russell/Dropbox/loewetechsoftware_com/loewetechsoftware_com"


def get_mp3_length(file_path):
    try:
        quoted_file_path = pipes.quote(file_path)
        command = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {quoted_file_path}"
        quoted_command = pipes.quote(f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {quoted_file_path}')
    
        HOST = "10.0.0.146"
        ssh_command = f"ssh root@{HOST} {quoted_command}"
        
        
        result = subprocess.run(ssh_command, shell=True, stdout=subprocess.PIPE, text=True)
        output = result.stdout
        #print(f"get_mp3_length('{file_path}'): {output}")
        
        total_seconds = float(output.strip('\n'))
        total_seconds = int(round(total_seconds))

        return total_seconds
    except Exception as e:
        print(f"Error: Couldn't get mp3 length")
        return None

def get_remote_mp3s():
    command = f'find "{search_directory}" -name "*.mp3"'
    HOST = "10.0.0.146"
    ssh_command = f"ssh root@{HOST} {command}"
    result = subprocess.run(ssh_command, shell=True, stdout=subprocess.PIPE, text=True)
    return result.stdout.splitlines()


def get_con():
    # Establish a connection to the PostgreSQL database
    credentials = {}
    with open(f'{envfile_directory}/.env', 'r') as f:
        # Load credentials from  .env file
        for line in f:
            key, var = line.strip('\n').split('=')
            credentials[key] = var
    
    return psycopg2.connect(
        host=credentials['DB_HOST'], 
        database=credentials['DB_NAME'],
        user=credentials['DB_USER'],
        password=credentials['DB_PASS']
    )

def get_series():
    conn = get_con()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, title from media_series")
        rows = cursor.fetchall()
        
        users = []
        for row in rows:
            user = {
                'id': row[0],
                'title': row[1]
            }
            users.append(user)
        
        print("Users retrieved from the database successfully.")
        return users
    except (psycopg2.Error) as e:
        print(f"Error retrieving users from the database: {e}")
    finally:
        cursor.close()
        conn.close()
        
def get_items():
    conn = get_con()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, title, episode, mediatype, local_path, series_id FROM media_mediaitem;")
        rows = cursor.fetchall()
        
        users = []
        for row in rows:
            user = {
                'id': row[0],
                'title': row[1],
                'episode': row[2],
                'mediatype': row[3],
                'local_path': row[4],
                'series': row[5]
            }
            users.append(user)
        
        print("Users retrieved from the database successfully.")
        return users
    except (psycopg2.Error) as e:
        print(f"Error retrieving users from the database: {e}")
    finally:
        cursor.close()
        conn.close()


def clear_playertimes(dry_run=False):
    # Remove dependent references to allow deleting of parent objects 

    conn = get_con()
    cursor = conn.cursor()
    
    # Define the SQL query to retrieve all objects from the media_playertime table
    cursor.execute("UPDATE media_playertime SET mediaitem_id = NULL;")
 
    conn.commit()    
    cursor.close()
    conn.close()

def fix_playertimes(dry_run=False):
    # Reassign orphaned playertime objects via 'local_path' field

    conn = get_con()
    cursor = conn.cursor()
    
    # Define the SQL query to retrieve all objects from the media_playertime table
    cursor.execute("SELECT id, local_path, mediaitem_id FROM media_playertime;")

    # Fetch all rows
    rows = cursor.fetchall()

    # Print or process the retrieved data
    for row in rows:
        try:
            cursor.execute("SELECT id FROM media_mediaitem WHERE local_path = %s;", (row[1],))
            series_id = cursor.fetchone()[0]
            cursor.execute("UPDATE media_playertime SET mediaitem_id = %s WHERE id = %s", (series_id, row[0],))
        except Exception as e:
            print(f"Error processing {row}")
            print(e)
            continue
        print(row)
        
    conn.commit()
    cursor.close()
    conn.close()


def load_books(dry_run=False, mediatype='audio'):
    if not dry_run:
        # remove parent refrences from current playertimes
        clear_playertimes()
    
    conn = get_con()
    cursor = conn.cursor()
    
    base_len = len(book_directory)+1
    media_len = len(media_directory)+1
    
    # Clear database tables
    if not dry_run:
        cursor.execute("DELETE FROM media_mediaitem;")
        cursor.execute("DELETE FROM media_series;")
        conn.commit()
    
    # Find all files with extensions .mp3 on server
    files = sorted(get_remote_mp3s())
    folders_dict = {}
    
    for f in files:
        # Remove the book directory off full path
        folder, file = f[base_len:].split('/')
        if folder in folders_dict:
            continue
        else:
            if not dry_run:
                slug = slugify(folder)
                cursor.execute("INSERT INTO media_series (title, slug) VALUES (%s, %s) RETURNING id;", (folder, slug))
                
                # save the new folder id for later
                series_id = cursor.fetchone()[0]
                folders_dict[folder] = series_id
            else:
                folders_dict[folder] = None
        
    print(folders_dict)
    
            
    for i, result in enumerate(files):
        try:
            folder, file = result[base_len:].split('/')
            
            # get the id for the folder in database
            series_id = folders_dict[folder]
            slug = slugify(f"{folder}_{file}")
            duration = get_mp3_length(result)
            
            querry = f"""
                    INSERT INTO media_mediaitem (title, episode, local_path, mediatype, series_id, slug, duration)
                    VALUES ('{file}', {i+1}, '{result[media_len:]}', '{mediatype}', {series_id}, '{slug}', {duration})
                """
                
            if dry_run:
                print(querry)
            else:
                cursor.execute(querry)
                conn.commit()
                print(f"Item {result[base_len:]} saved to the database successfully.")

        except Exception as e:
            # Rollback changes
            print("Error: rolling back changes")
            print(e)
            conn.rollback()
            break
    
    if not dry_run:
        # Commit the transaction
        conn.commit()
        conn.close()
        fix_playertimes()


if __name__ == '__main__':
    
    load_books(dry_run=False)
    
        
